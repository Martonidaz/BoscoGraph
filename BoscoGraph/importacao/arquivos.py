'''
    Fase 1 da importação: arquivos de programas de desenho de grafos. Só Python (nada para instalar)
    e o resultado é exato, porque o arquivo diz quem é vértice e quem é aresta.

      ler_drawio  -> draw.io / diagrams.net (.drawio): XML, às vezes compactado
      ler_graphml -> GraphML (.graphml): o formato do yEd, do Gephi e do NetworkX
      ler_dot     -> DOT (.dot, .gv): a linguagem do Graphviz ("digraph { A -> B }")
      ler_csv     -> CSV: uma aresta por linha (origem, destino, nome, peso) ou matriz de adjacência

    Cada função recebe o texto do arquivo e devolve o "grafo bruto" (veja importacao/__init__.py).
'''

import base64
import csv
import html
import io
import re
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

from entrada import contar
from importacao import ProblemaNaImportacao


# ----------------------------------------------------------------------
# XML (draw.io e GraphML)
# ----------------------------------------------------------------------

# Lê um XML com um cuidado de segurança: arquivos com <!ENTITY> são recusados. Entidades podem
# se expandir umas nas outras ("billion laughs") e ocupar toda a memória com um arquivo pequeno.
# Nenhum desenho de grafo precisa delas.
def ler_xml(texto, formato):
    if "<!ENTITY" in texto:
        raise ProblemaNaImportacao(f"O arquivo {formato} declara entidades XML (<!ENTITY>), que não são aceitas "
                                   f"por segurança.")
    try:
        return ET.fromstring(texto)
    except ET.ParseError as erro:
        raise ProblemaNaImportacao(f"O arquivo não é um {formato} válido (XML com erro: {erro}).")


# O nome de uma tag sem o "namespace": "{http://graphml.graphdrawing.org/xmlns}node" -> "node"
def nome_local(tag):
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


# ----------------------------------------------------------------------
# draw.io
# ----------------------------------------------------------------------
# Estrutura do arquivo:
#   <mxfile> <diagram name="Página-1"> ... </diagram> </mxfile>
# Dentro de cada <diagram> (uma página) vem um <mxGraphModel>, ou o mesmo XML compactado:
# em base64, comprimido com "deflate" e com os caracteres especiais escapados como numa URL.
# No <mxGraphModel>, cada forma é um <mxCell>:
#   vertex="1" -> uma forma (o vértice); value = o texto; <mxGeometry x y width height>
#   edge="1"   -> uma ligação; source e target = os ids das formas ligadas; style diz as setas
# O texto de uma ligação às vezes é uma célula separada, "filha" da ligação (parent = id da ligação).

# Desfaz a compactação de uma página do draw.io: base64 -> deflate -> texto escapado de URL
def descompactar_drawio(texto):
    try:
        dados = base64.b64decode(texto)
        # -15 = "deflate puro", sem o cabeçalho que o zlib normalmente espera
        return urllib.parse.unquote(zlib.decompress(dados, -15).decode("utf-8"))
    except (ValueError, zlib.error, UnicodeDecodeError):
        raise ProblemaNaImportacao("Não consegui descompactar a página do draw.io.")


# O style do draw.io é uma lista "chave=valor;chave=valor;palavra;" -> dicionário
# (as palavras soltas, como "ellipse" ou "text", viram chave com valor "")
def ler_estilo(estilo):
    resultado = {}
    for parte in (estilo or "").split(";"):
        parte = parte.strip()
        if parte == "":
            continue
        if "=" in parte:
            chave, valor = parte.split("=", 1)
            resultado[chave.strip()] = valor.strip()
        else:
            resultado[parte] = ""
    return resultado


# O texto de uma forma pode ter HTML ("<b>A</b>", "A<br>B"): fica só o texto
def texto_sem_html(valor):
    texto = re.sub(r"<br\s*/?>", " ", valor or "", flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", "", texto)          # tira todas as tags
    texto = html.unescape(texto)                   # "&amp;" -> "&", "&nbsp;" -> espaço
    return re.sub(r"\s+", " ", texto).strip()


def ler_drawio(texto):
    raiz = ler_xml(texto, "draw.io")
    paginas = []
    if nome_local(raiz.tag) == "mxGraphModel":
        paginas.append(("Página 1", raiz))
    elif nome_local(raiz.tag) == "mxfile":
        numero = 0
        for diagrama in raiz.iter("diagram"):
            numero += 1
            nome = diagrama.get("name") or f"Página {numero}"
            modelo = diagrama.find("mxGraphModel")
            if modelo is None:
                conteudo = (diagrama.text or "").strip()
                if conteudo == "":
                    continue
                modelo = ler_xml(descompactar_drawio(conteudo), "draw.io")
            paginas.append((nome, modelo))
    else:
        raise ProblemaNaImportacao("Esse XML não é um desenho do draw.io (não começa com <mxfile> nem "
                                   "<mxGraphModel>).")
    if not paginas:
        raise ProblemaNaImportacao("O arquivo do draw.io não tem nenhuma página.")

    # A primeira página que tem pelo menos um vértice
    for i in range(len(paginas)):
        nome, modelo = paginas[i]
        bruto = ler_pagina_do_drawio(modelo)
        if bruto["vertices"]:
            if len(paginas) > 1:
                bruto["avisos"].insert(0, f"O arquivo tem {len(paginas)} páginas; importei \"{nome}\".")
            return bruto
    raise ProblemaNaImportacao("Nenhuma página do draw.io tem formas (vértices).")


def ler_pagina_do_drawio(modelo):
    avisos = []
    # 1. Todas as células, com o id, o texto, o estilo e a geometria
    celulas = {}
    ordem = []
    for elemento in modelo.iter():
        tag = nome_local(elemento.tag)
        if tag in ("object", "UserObject"):
            # Forma com propriedades extras: o id e o texto ficam no <object>, o resto no <mxCell> de dentro
            celula = elemento.find("mxCell")
            if celula is None:
                continue
            identificador = elemento.get("id")
            valor = elemento.get("label", "")
        elif tag == "mxCell":
            identificador = elemento.get("id")
            if identificador is None:
                continue                   # é o <mxCell> de dentro de um <object> (já foi lido)
            celula = elemento
            valor = elemento.get("value", "")
        else:
            continue
        geometria = celula.find("mxGeometry")
        dados = {"id": identificador, "valor": texto_sem_html(valor), "pai": celula.get("parent"),
                 "estilo": ler_estilo(celula.get("style")), "vertice": celula.get("vertex") == "1",
                 "aresta": celula.get("edge") == "1", "origem": celula.get("source"),
                 "destino": celula.get("target"), "geometria": geometria}
        celulas[identificador] = dados
        ordem.append(identificador)

    # 2. Quem é texto de uma ligação (filho de uma aresta) e quem é grupo (pai de outras formas)
    texto_da_aresta = {}
    pais_de_formas = []
    for identificador in ordem:
        celula = celulas[identificador]
        pai = celulas.get(celula["pai"])
        if celula["vertice"] and pai is not None and pai["aresta"]:
            if celula["valor"]:
                texto_da_aresta[pai["id"]] = celula["valor"]
        elif celula["vertice"] and pai is not None and pai["vertice"]:
            pais_de_formas.append(pai["id"])

    # 3. As formas que são vértices, com a posição do centro (somando o deslocamento dos grupos)
    formas = []
    for identificador in ordem:
        celula = celulas[identificador]
        pai = celulas.get(celula["pai"])
        if not celula["vertice"] or (pai is not None and pai["aresta"]) or identificador in pais_de_formas:
            continue
        formas.append(identificador)
    centro = {}
    caixa = {}
    for identificador in formas:
        x, y, largura, altura = geometria_absoluta(celulas, identificador)
        centro[identificador] = (x + largura / 2, y + altura / 2)
        caixa[identificador] = (x, y, largura, altura)

    # 4. As ligações. Ponta solta (desenhada perto de uma forma, mas sem estar presa a ela):
    # liga na forma que contém o ponto (com uma folga de 10 pixels)
    arestas = []
    soltas = 0
    usadas_por_aresta = []
    for identificador in ordem:
        celula = celulas[identificador]
        if not celula["aresta"]:
            continue
        origem = celula["origem"]
        destino = celula["destino"]
        if origem not in centro:
            origem = forma_no_ponto(ponto_da_geometria(celula["geometria"], "sourcePoint"), caixa)
        if destino not in centro:
            destino = forma_no_ponto(ponto_da_geometria(celula["geometria"], "targetPoint"), caixa)
        if origem is None or destino is None:
            soltas += 1
            continue
        estilo = celula["estilo"]
        # No draw.io, uma ligação nova tem seta no fim (endArrow=classic) e nenhuma no começo
        seta_no_fim = estilo.get("endArrow", "classic") != "none"
        seta_no_inicio = estilo.get("startArrow", "none") != "none"
        if seta_no_fim and seta_no_inicio:
            seta = "ambas"
        elif seta_no_fim:
            seta = "fim"
        elif seta_no_inicio:
            seta = "inicio"
        else:
            seta = "nenhuma"
        rotulo = celula["valor"] or texto_da_aresta.get(identificador, "")
        arestas.append({"origem": origem, "destino": destino, "rotulo": rotulo, "peso": None, "seta": seta})
        usadas_por_aresta.append(origem)
        usadas_por_aresta.append(destino)
    if soltas:
        avisos.append(contar(soltas, "ligação com ponta solta (não presa a nenhuma forma) foi ignorada",
                             "ligações com ponta solta (não presas a nenhuma forma) foram ignoradas") + ".")

    # 5. Texto solto (estilo "text", sem nenhuma ligação) é anotação do desenho, não vértice
    vertices = []
    anotacoes = []
    for identificador in formas:
        celula = celulas[identificador]
        if "text" in celula["estilo"] and identificador not in usadas_por_aresta:
            if celula["valor"]:
                anotacoes.append(celula["valor"])
            continue
        vertices.append({"id": identificador, "rotulo": celula["valor"], "posicao": centro[identificador]})
    if anotacoes:
        avisos.append("Textos soltos ignorados (não são vértices): " + ", ".join(anotacoes[:4]) + ".")
    return {"vertices": vertices, "arestas": arestas, "direcionado": None, "avisos": avisos, "conferir": False}


# Um número de um atributo do XML; se o arquivo estiver com defeito ("1a"), vale 0
def numero_seguro(texto):
    try:
        return float(texto)
    except (TypeError, ValueError):
        return 0.0


# A posição e o tamanho de uma forma na página: as coordenadas dentro de um grupo são relativas
# ao grupo, então é preciso somar as posições de todos os "pais" que são formas
def geometria_absoluta(celulas, identificador):
    x, y, largura, altura = 0.0, 0.0, 0.0, 0.0
    geometria = celulas[identificador]["geometria"]
    if geometria is not None:
        x = numero_seguro(geometria.get("x", 0))
        y = numero_seguro(geometria.get("y", 0))
        largura = numero_seguro(geometria.get("width", 0))
        altura = numero_seguro(geometria.get("height", 0))
    pai = celulas.get(celulas[identificador]["pai"])
    while pai is not None and pai["vertice"]:
        if pai["geometria"] is not None:
            x += numero_seguro(pai["geometria"].get("x", 0))
            y += numero_seguro(pai["geometria"].get("y", 0))
        pai = celulas.get(pai["pai"])
    return x, y, largura, altura


# O ponto <mxPoint as="sourcePoint" x=".." y=".."> de uma ligação (ou None)
def ponto_da_geometria(geometria, nome):
    if geometria is None:
        return None
    for ponto in geometria.findall("mxPoint"):
        if ponto.get("as") == nome:
            return (numero_seguro(ponto.get("x", 0)), numero_seguro(ponto.get("y", 0)))
    return None


# A forma que contém o ponto (com folga); se várias, a de centro mais próximo
def forma_no_ponto(ponto, caixa):
    if ponto is None:
        return None
    escolhida = None
    menor = None
    folga = 10
    for identificador in caixa:
        x, y, largura, altura = caixa[identificador]
        if x - folga <= ponto[0] <= x + largura + folga and y - folga <= ponto[1] <= y + altura + folga:
            distancia = abs(ponto[0] - (x + largura / 2)) + abs(ponto[1] - (y + altura / 2))
            if menor is None or distancia < menor:
                escolhida = identificador
                menor = distancia
    return escolhida


# ----------------------------------------------------------------------
# GraphML
# ----------------------------------------------------------------------
# Estrutura:
#   <key id="d0" for="edge" attr.name="weight" attr.type="double"><default>1</default></key>
#   <graph edgedefault="directed">   (ou "undirected")
#     <node id="n0"><data key="d1">A</data></node>
#     <edge source="n0" target="n1"><data key="d0">5</data></edge>
# O yEd guarda o texto em <y:NodeLabel> e a posição em <y:Geometry x y width height>;
# o Gephi e o NetworkX guardam a posição em atributos "x" e "y".

NOMES_DE_ROTULO = ("label", "name", "nome", "rotulo", "rótulo", "id_label")
NOMES_DE_PESO = ("weight", "peso", "custo", "cost", "valor", "value", "distance", "distancia", "distância",
                 "w", "length", "comprimento", "tempo", "time", "rtt")


def ler_graphml(texto):
    raiz = ler_xml(texto, "GraphML")
    if nome_local(raiz.tag) != "graphml":
        raise ProblemaNaImportacao("Esse arquivo não é GraphML (não começa com <graphml>).")
    avisos = []

    # As "chaves": o que cada <data key="..."> significa (e o valor padrão, se houver)
    chaves = {}
    for elemento in raiz:
        if nome_local(elemento.tag) == "key":
            padrao = None
            for filho in elemento:
                if nome_local(filho.tag) == "default":
                    padrao = (filho.text or "").strip()
            chaves[elemento.get("id")] = {"nome": (elemento.get("attr.name") or "").strip().lower(),
                                          "para": elemento.get("for", "all"), "padrao": padrao}

    grafo = None
    for elemento in raiz:
        if nome_local(elemento.tag) == "graph":
            grafo = elemento
            break
    if grafo is None:
        raise ProblemaNaImportacao("O GraphML não tem nenhum <graph>.")
    direcionado = grafo.get("edgedefault", "directed") == "directed"

    vertices = []
    arestas = []
    hiperarestas = 0
    for elemento in grafo:
        tag = nome_local(elemento.tag)
        if tag == "node":
            dados = dados_do_graphml(elemento, chaves, "node")
            rotulo = rotulo_do_yed(elemento, "NodeLabel")
            if rotulo is None:
                rotulo = primeiro_valor(dados, NOMES_DE_ROTULO)
            vertices.append({"id": elemento.get("id"), "rotulo": rotulo or "",
                             "posicao": posicao_do_graphml(elemento, dados)})
        elif tag == "edge":
            dados = dados_do_graphml(elemento, chaves, "edge")
            rotulo = rotulo_do_yed(elemento, "EdgeLabel")
            if rotulo is None:
                rotulo = primeiro_valor(dados, NOMES_DE_ROTULO) or ""
            seta = None
            if elemento.get("directed") == "true":
                seta = "fim"
            elif elemento.get("directed") == "false":
                seta = "nenhuma"
            setas_do_yed = setas_do_yed_na_aresta(elemento)
            if setas_do_yed is not None:
                seta = setas_do_yed
            arestas.append({"origem": elemento.get("source"), "destino": elemento.get("target"),
                            "rotulo": rotulo, "peso": primeiro_valor(dados, NOMES_DE_PESO), "seta": seta})
        elif tag == "hyperedge":
            hiperarestas += 1
    if hiperarestas:
        avisos.append(contar(hiperarestas, "hiperaresta (liga mais de 2 vértices) foi ignorada",
                             "hiperarestas (ligam mais de 2 vértices) foram ignoradas") + ".")
    return {"vertices": vertices, "arestas": arestas, "direcionado": direcionado, "avisos": avisos,
            "conferir": False}


# Os <data> de um nó ou aresta: {nome do atributo: valor}, com os padrões das chaves
def dados_do_graphml(elemento, chaves, tipo):
    dados = {}
    for chave in chaves.values():
        if chave["padrao"] is not None and chave["para"] in (tipo, "all"):
            dados[chave["nome"]] = chave["padrao"]
    for filho in elemento:
        if nome_local(filho.tag) == "data" and filho.get("key") in chaves:
            texto = "".join(filho.itertext()).strip()
            if texto != "" or len(filho) == 0:
                dados[chaves[filho.get("key")]["nome"]] = texto
    return dados


def primeiro_valor(dados, nomes):
    for nome in nomes:
        if nome in dados and dados[nome] not in (None, ""):
            return dados[nome]
    return None


# O texto de um rótulo do yEd (<y:NodeLabel> ou <y:EdgeLabel>), ou None se não houver
def rotulo_do_yed(elemento, nome):
    for filho in elemento.iter():
        if nome_local(filho.tag) == nome:
            texto = "".join(filho.itertext()).strip()
            if texto:
                return texto
    return None


# As setas do yEd: <y:Arrows source="none" target="standard"/>
def setas_do_yed_na_aresta(elemento):
    for filho in elemento.iter():
        if nome_local(filho.tag) == "Arrows":
            no_inicio = filho.get("source", "none") != "none"
            no_fim = filho.get("target", "none") != "none"
            if no_inicio and no_fim:
                return "ambas"
            if no_fim:
                return "fim"
            if no_inicio:
                return "inicio"
            return "nenhuma"
    return None


# Posição do vértice: <y:Geometry> do yEd (y para baixo, como na tela) ou os atributos "x" e "y"
# do Gephi e do NetworkX (y para cima, como na matemática: por isso o sinal de y é trocado)
def posicao_do_graphml(elemento, dados):
    for filho in elemento.iter():
        if nome_local(filho.tag) == "Geometry":
            try:
                x = float(filho.get("x", 0)) + float(filho.get("width", 0)) / 2
                y = float(filho.get("y", 0)) + float(filho.get("height", 0)) / 2
                return (x, y)
            except ValueError:
                return None
    if "x" in dados and "y" in dados:
        try:
            return (float(dados["x"]), -float(dados["y"]))
        except ValueError:
            return None
    return None


# ----------------------------------------------------------------------
# DOT (Graphviz)
# ----------------------------------------------------------------------
# Exemplo:
#   digraph rede {                 // "graph" = não orientado (arestas com --)
#     node [shape=circle];         // padrão para os próximos vértices
#     A [label="São Paulo"];
#     A -> B [label="e1", weight=5];
#     B -> C -> D;                 // uma "corrente": B -> C e C -> D
#     A -> {C D};                  // um subgrafo: A -> C e A -> D
#   }
# A leitura tem duas partes: o "tokenizador" quebra o texto em pedaços (nomes, textos entre aspas,
# símbolos como -> e {), e o "parser" segue a gramática da linguagem DOT pedaço por pedaço.

PALAVRAS_DO_DOT = ("strict", "graph", "digraph", "node", "edge", "subgraph")


# Quebra o texto em pedaços: ("id", texto), ("simbolo", "->"), ...
def pedacos_do_dot(texto):
    pedacos = []
    i = 0
    tamanho = len(texto)
    while i < tamanho:
        caractere = texto[i]
        if caractere.isspace():
            i += 1
        elif texto.startswith("//", i):                 # comentário até o fim da linha
            fim = texto.find("\n", i)
            i = tamanho if fim < 0 else fim
        elif texto.startswith("/*", i):                 # comentário em bloco
            fim = texto.find("*/", i + 2)
            if fim < 0:
                raise ProblemaNaImportacao("DOT: um comentário /* não foi fechado com */.")
            i = fim + 2
        elif caractere == "#":                          # comentário até o fim da linha (como no Graphviz)
            fim = texto.find("\n", i)
            i = tamanho if fim < 0 else fim
        elif texto.startswith("->", i) or texto.startswith("--", i):
            pedacos.append(("simbolo", texto[i:i + 2]))
            i += 2
        elif caractere in "{}[]=;,:":
            pedacos.append(("simbolo", caractere))
            i += 1
        elif caractere == "+":                          # "a" + "b": junta os dois textos (veja o fim)
            pedacos.append(("id", "+"))
            i += 1
        elif caractere == '"':                          # texto entre aspas, com \" escapado
            j = i + 1
            valor = ""
            while j < tamanho and texto[j] != '"':
                if texto[j] == "\\" and j + 1 < tamanho:
                    if texto[j + 1] == '"':
                        valor += '"'
                        j += 2
                        continue
                    if texto[j + 1] == "\n":           # barra no fim da linha: continua na próxima
                        j += 2
                        continue
                valor += texto[j]
                j += 1
            if j >= tamanho:
                raise ProblemaNaImportacao("DOT: um texto entre aspas não foi fechado.")
            pedacos.append(("texto", valor))
            i = j + 1
        elif caractere == "<":                          # texto HTML: <...> com < > equilibrados
            profundidade = 0
            j = i
            while j < tamanho:
                if texto[j] == "<":
                    profundidade += 1
                elif texto[j] == ">":
                    profundidade -= 1
                    if profundidade == 0:
                        break
                j += 1
            pedacos.append(("texto", texto_sem_html(texto[i + 1:j])))
            i = j + 1
        else:
            achado = re.match(r"-?(\.\d+|\d+(\.\d*)?)|[A-Za-z_\u0080-￿][A-Za-z_0-9\u0080-￿]*",
                              texto[i:])
            if achado is None or achado.group(0) == "":
                raise ProblemaNaImportacao(f"DOT: não entendi o caractere '{caractere}'.")
            pedacos.append(("id", achado.group(0)))
            i += len(achado.group(0))
    # "a" + "b" no DOT junta os dois textos
    juntos = []
    for pedaco in pedacos:
        if len(juntos) >= 2 and juntos[-1] == ("id", "+") and juntos[-2][0] == "texto" and pedaco[0] == "texto":
            juntos.pop()
            juntos[-1] = ("texto", juntos[-1][1] + pedaco[1])
        else:
            juntos.append(pedaco)
    return juntos


class LeitorDeDot:
    def __init__(self, texto):
        self.pedacos = pedacos_do_dot(texto)
        self.posicao = 0
        self.vertices = []              # ids na ordem em que aparecem
        self.atributos_do_vertice = {}  # id -> atributos
        self.arestas = []               # (origem, destino, atributos com os padrões, atributos da própria aresta)
        self.direcionado = True
        self.estrito = False
        self.operador_errado = False

    # O pedaço atual (sem avançar) e o próximo (avançando)
    def olhar(self):
        if self.posicao < len(self.pedacos):
            return self.pedacos[self.posicao]
        return (None, None)

    def avancar(self):
        pedaco = self.olhar()
        self.posicao += 1
        return pedaco

    def eh_simbolo(self, simbolo):
        return self.olhar() == ("simbolo", simbolo)

    def eh_palavra(self, palavra):
        tipo, valor = self.olhar()
        return tipo == "id" and valor.lower() == palavra

    def esperar(self, simbolo):
        if not self.eh_simbolo(simbolo):
            tipo, valor = self.olhar()
            raise ProblemaNaImportacao(f"DOT: esperava '{simbolo}' e encontrei '{valor or 'o fim do arquivo'}'.")
        self.avancar()

    def ler_id(self):
        tipo, valor = self.avancar()
        if tipo not in ("id", "texto"):
            raise ProblemaNaImportacao(f"DOT: esperava um nome e encontrei '{valor or 'o fim do arquivo'}'.")
        return valor

    # graph : [strict] (graph | digraph) [ID] '{' stmt_list '}'
    def ler(self):
        if self.eh_palavra("strict"):
            self.avancar()
            self.estrito = True
        if self.eh_palavra("digraph"):
            self.direcionado = True
        elif self.eh_palavra("graph"):
            self.direcionado = False
        else:
            raise ProblemaNaImportacao("DOT: o arquivo precisa começar com \"graph\" ou \"digraph\".")
        self.avancar()
        if not self.eh_simbolo("{"):
            self.ler_id()                               # o nome do grafo (não é usado)
        self.esperar("{")
        self.ler_comandos({"node": {}, "edge": {}})
        self.esperar("}")

    # stmt_list: comandos até o "}" do bloco. "padroes" são os atributos de node/edge valendo agora.
    # Devolve os vértices que apareceram no bloco (para as arestas que ligam subgrafos).
    def ler_comandos(self, padroes):
        padroes = {"node": dict(padroes["node"]), "edge": dict(padroes["edge"])}   # cópia: vale só no bloco
        do_bloco = []
        while not self.eh_simbolo("}") and self.olhar()[0] is not None:
            for vertice in self.ler_comando(padroes):
                if vertice not in do_bloco:
                    do_bloco.append(vertice)
            if self.eh_simbolo(";"):
                self.avancar()
        return do_bloco

    def ler_comando(self, padroes):
        # node [...] / edge [...] / graph [...]: muda os padrões
        if self.eh_palavra("node") or self.eh_palavra("edge") or self.eh_palavra("graph"):
            tipo = self.avancar()[1].lower()
            atributos = self.ler_atributos()
            if tipo in padroes:
                for chave in atributos:
                    padroes[tipo][chave] = atributos[chave]
            return []
        # ID = ID: atributo do grafo, como rankdir=LR (não é usado). É preciso olhar o pedaço
        # SEGUINTE antes de ler o nome; senão "rankdir" viraria um vértice.
        if self.olhar()[0] in ("id", "texto") and self.posicao + 1 < len(self.pedacos) \
                and self.pedacos[self.posicao + 1] == ("simbolo", "="):
            self.avancar()
            self.avancar()
            self.ler_id()
            return []
        # Lado esquerdo: um vértice ou um subgrafo
        esquerda = self.ler_vertice_ou_subgrafo(padroes)
        envolvidos = list(esquerda["vertices"])
        lados = [esquerda]
        while self.eh_simbolo("->") or self.eh_simbolo("--"):
            operador = self.avancar()[1]
            if (operador == "->") != self.direcionado:
                self.operador_errado = True
            lado = self.ler_vertice_ou_subgrafo(padroes)
            lados.append(lado)
            for vertice in lado["vertices"]:
                if vertice not in envolvidos:
                    envolvidos.append(vertice)
        atributos = self.ler_atributos()
        if len(lados) == 1:
            # Um vértice sozinho: os atributos são dele
            if esquerda["eh_vertice"]:
                vertice = esquerda["vertices"][0]
                for chave in atributos:
                    self.atributos_do_vertice[vertice][chave] = atributos[chave]
            return envolvidos
        # Uma corrente de arestas: cada lado liga com o próximo (subgrafo = todos os vértices dele)
        atributos_da_aresta = dict(padroes["edge"])
        for chave in atributos:
            atributos_da_aresta[chave] = atributos[chave]
        for i in range(len(lados) - 1):
            for origem in lados[i]["vertices"]:
                for destino in lados[i + 1]["vertices"]:
                    self.arestas.append((origem, destino, atributos_da_aresta, atributos))
        return envolvidos

    def ler_vertice_ou_subgrafo(self, padroes):
        if self.eh_palavra("subgraph") or self.eh_simbolo("{"):
            if self.eh_palavra("subgraph"):
                self.avancar()
                if not self.eh_simbolo("{"):
                    self.ler_id()                       # o nome do subgrafo
            self.esperar("{")
            vertices = self.ler_comandos(padroes)
            self.esperar("}")
            return {"vertices": vertices, "eh_vertice": False}
        identificador = self.ler_id()
        if self.eh_simbolo(":"):                        # porta (A:norte): a porta não importa
            self.avancar()
            self.ler_id()
            if self.eh_simbolo(":"):
                self.avancar()
                self.ler_id()
        if identificador not in self.atributos_do_vertice:
            self.vertices.append(identificador)
            self.atributos_do_vertice[identificador] = dict(padroes["node"])
        return {"vertices": [identificador], "eh_vertice": True}

    # attr_list : '[' [ID '=' ID [',' | ';']]* ']' (pode repetir: [a=1][b=2])
    def ler_atributos(self):
        atributos = {}
        while self.eh_simbolo("["):
            self.avancar()
            while not self.eh_simbolo("]"):
                chave = self.ler_id().lower()
                valor = "true"
                if self.eh_simbolo("="):
                    self.avancar()
                    valor = self.ler_id()
                atributos[chave] = valor
                if self.eh_simbolo(",") or self.eh_simbolo(";"):
                    self.avancar()
            self.esperar("]")
        return atributos


def ler_dot(texto):
    leitor = LeitorDeDot(texto)
    leitor.ler()
    avisos = []
    if leitor.operador_errado:
        avisos.append("O arquivo mistura \"->\" e \"--\": valeu o tipo do grafo (graph ou digraph).")
    vertices = []
    for identificador in leitor.vertices:
        atributos = leitor.atributos_do_vertice[identificador]
        rotulo = atributos.get("label", identificador)
        if rotulo in ("\\N", ""):
            rotulo = identificador                     # \N no Graphviz = "o nome do vértice"
        vertices.append({"id": identificador, "rotulo": rotulo, "posicao": posicao_do_dot(atributos.get("pos"))})
    arestas = []
    vistas = []
    repetidas = 0
    for origem, destino, atributos, proprios in leitor.arestas:
        if leitor.estrito:
            # "strict": no máximo uma aresta por par (no não orientado, A -- B e B -- A são o mesmo par)
            chave = (origem, destino)
            if not leitor.direcionado and destino < origem:
                chave = (destino, origem)
            if chave in vistas:
                repetidas += 1
                continue
            vistas.append(chave)
        # O peso: o escrito na própria aresta; senão o rótulo, se for um número (a normalização cuida
        # disso); senão o padrão "edge [weight=...]". (No Graphviz, "weight" só ajusta o desenho;
        # quem desenha um grafo valorado em DOT costuma escrever o peso no label.)
        rotulo = atributos.get("label", "")
        peso = peso_dos_atributos(proprios)
        if peso is None and not re.fullmatch(r"\s*[+-]?\d+([.,]\d+)?\s*", rotulo):
            peso = peso_dos_atributos(atributos)
        arestas.append({"origem": origem, "destino": destino, "rotulo": rotulo, "peso": peso, "seta": None})
    if repetidas:
        avisos.append("Grafo \"strict\": " + contar(repetidas, "aresta repetida foi juntada",
                                                     "arestas repetidas foram juntadas") + ".")
    return {"vertices": vertices, "arestas": arestas, "direcionado": leitor.direcionado, "avisos": avisos,
            "conferir": False}


def peso_dos_atributos(atributos):
    for nome in NOMES_DE_PESO:
        if nome in atributos:
            return atributos[nome]
    return None


# pos="x,y" (ou "x,y!") do Graphviz: em pontos, com y para cima (por isso o sinal de y é trocado)
def posicao_do_dot(texto):
    if not texto:
        return None
    partes = texto.rstrip("!").split(",")
    if len(partes) < 2:
        return None
    try:
        return (float(partes[0]), -float(partes[1]))
    except ValueError:
        return None


# ----------------------------------------------------------------------
# CSV
# ----------------------------------------------------------------------
# Dois formatos:
# 1. Lista de arestas, uma por linha, com ou sem cabeçalho:
#      origem;destino;nome;peso        (o Excel em português usa ";" e vírgula nos decimais)
#      A;B;e1;2,5
#    Sem cabeçalho: origem, destino e, na 3ª coluna, o peso (se for número) ou o nome.
#    Uma linha só com a origem cria um vértice sem arestas.
# 2. Matriz de adjacência (como na Lista 03): a 1ª linha e a 1ª coluna têm os nomes dos vértices.
#      ;A;B;C
#      A;0;1;0
#    0 ou vazio = sem aresta; só 0 e 1 = arestas sem peso; outros números = o peso da aresta.
#    Matriz simétrica = grafo não orientado (cada par vira uma aresta só).

# Só nomes que não costumam ser nome de vértice ("u" e "v", por exemplo, ficam de fora: um CSV sem
# cabeçalho começando com "u,v" perderia a primeira aresta)
NOMES_DE_ORIGEM = ("origem", "source", "from", "de", "src", "no1", "node1", "vertice1")
NOMES_DE_DESTINO = ("destino", "target", "to", "para", "dst", "dest", "no2", "node2", "vertice2")
NOMES_DE_NOME = ("nome", "label", "rotulo", "name", "aresta", "id")


# Para comparar nomes de coluna: minúsculas e sem acento ("Rótulo" -> "rotulo")
def sem_acento(texto):
    decomposto = unicodedata.normalize("NFD", texto.strip().lower())
    resultado = ""
    for caractere in decomposto:
        if unicodedata.category(caractere) != "Mn":     # Mn = marca de acento separada da letra
            resultado += caractere
    return resultado


def separador_do_csv(texto):
    amostra = texto[:4096]
    try:
        return csv.Sniffer().sniff(amostra, delimiters=";,\t|").delimiter
    except csv.Error:
        primeira = amostra.split("\n")[0]
        melhor = ","
        for separador in (";", "\t", "|"):
            if primeira.count(separador) > primeira.count(melhor):
                melhor = separador
        return melhor


def ler_csv(texto):
    separador = separador_do_csv(texto)
    linhas = []
    for linha in csv.reader(io.StringIO(texto), delimiter=separador):
        celulas = []
        for celula in linha:
            celulas.append(celula.strip())
        if any(celulas):
            linhas.append(celulas)
    if not linhas:
        raise ProblemaNaImportacao("O CSV está vazio.")
    if parece_matriz(linhas):
        return ler_matriz(linhas)
    return ler_lista_de_arestas(linhas)


# Matriz: os nomes da 1ª linha iguais aos da 1ª coluna, a 1ª célula sem ser um desses nomes
# (normalmente vazia) e o miolo todo de números (ou vazio)
def parece_matriz(linhas):
    cabecalho = linhas[0][1:]
    if len(cabecalho) < 1 or len(linhas) != len(cabecalho) + 1 or linhas[0][0] in cabecalho:
        return False
    for i in range(1, len(linhas)):
        if len(linhas[i]) < 1 or linhas[i][0] != cabecalho[i - 1]:
            return False
        for celula in linhas[i][1:]:
            if celula != "" and re.fullmatch(r"[+-]?\d+([.,]\d+)?", celula) is None:
                return False
    return True


def ler_matriz(linhas):
    from entrada import ler_numero
    nomes = linhas[0][1:]
    valores = []
    for i in range(1, len(linhas)):
        linha = []
        for j in range(len(nomes)):
            texto = linhas[i][j + 1] if j + 1 < len(linhas[i]) else ""
            numero, problema = ler_numero(texto or "0")
            if problema:
                raise ProblemaNaImportacao(f"Matriz de adjacência: '{texto}' (linha {nomes[i - 1]}, coluna "
                                           f"{nomes[j]}) não é um número.")
            linha.append(numero)
        valores.append(linha)
    n = len(nomes)
    simetrica = True
    so_zero_e_um = True
    for i in range(n):
        for j in range(n):
            if valores[i][j] != valores[j][i]:
                simetrica = False
            if valores[i][j] not in (0, 1):
                so_zero_e_um = False
    vertices = []
    for nome in nomes:
        vertices.append({"id": nome, "rotulo": nome, "posicao": None})
    arestas = []
    for i in range(n):
        for j in range(n):
            if valores[i][j] == 0 or (simetrica and j < i):
                continue                                # no simétrico, cada par conta uma vez
            peso = None if so_zero_e_um else str(valores[i][j])
            arestas.append({"origem": nomes[i], "destino": nomes[j], "rotulo": "", "peso": peso, "seta": None})
    avisos = ["Lido como matriz de adjacência (" + ("simétrica: não orientado" if simetrica else "orientado")
              + ("" if so_zero_e_um else "; os números viraram pesos") + ")."]
    return {"vertices": vertices, "arestas": arestas, "direcionado": not simetrica, "avisos": avisos,
            "conferir": False}


def ler_lista_de_arestas(linhas):
    # Cabeçalho: alguma célula da 1ª linha é um nome de coluna conhecido
    colunas = {"origem": 0, "destino": 1, "nome": None, "peso": None}
    primeira = []
    for celula in linhas[0]:
        primeira.append(sem_acento(celula))
    tem_cabecalho = False
    achou_ponta = False
    for indice in range(len(primeira)):
        nome = primeira[indice]
        if nome in NOMES_DE_ORIGEM:
            colunas["origem"] = indice
            tem_cabecalho = True
            achou_ponta = True
        elif nome in NOMES_DE_DESTINO:
            colunas["destino"] = indice
            tem_cabecalho = True
            achou_ponta = True
        elif nome in NOMES_DE_NOME:
            colunas["nome"] = indice
            tem_cabecalho = True
        elif nome in NOMES_DE_PESO:
            colunas["peso"] = indice
            tem_cabecalho = True
    if not achou_ponta:
        tem_cabecalho = False                           # só achou "nome" ou "peso": não é um cabeçalho confiável
        colunas = {"origem": 0, "destino": 1, "nome": None, "peso": None}
    if tem_cabecalho:
        linhas = linhas[1:]
    vertices = []
    ids = []
    arestas = []
    for celulas in linhas:
        origem = valor_da_coluna(celulas, colunas["origem"])
        destino = valor_da_coluna(celulas, colunas["destino"])
        for vertice in (origem, destino):
            if vertice and vertice not in ids:
                ids.append(vertice)
                vertices.append({"id": vertice, "rotulo": vertice, "posicao": None})
        if not origem or not destino:
            continue                                    # só um vértice na linha: vértice isolado
        nome = valor_da_coluna(celulas, colunas["nome"])
        peso = valor_da_coluna(celulas, colunas["peso"])
        if not tem_cabecalho:
            # Sem cabeçalho: 3ª coluna é o peso se for número, senão o nome; a 4ª é a outra
            extras = celulas[2:4]
            nome = ""
            peso = None
            for extra in extras:
                if peso is None and re.fullmatch(r"[+-]?\d+([.,]\d+)?", extra or ""):
                    peso = extra
                elif extra and not nome:
                    nome = extra
        arestas.append({"origem": origem, "destino": destino, "rotulo": nome or "", "peso": peso or None,
                        "seta": None})
    return {"vertices": vertices, "arestas": arestas, "direcionado": None, "avisos": [], "conferir": False}


def valor_da_coluna(celulas, indice):
    if indice is None or indice >= len(celulas):
        return ""
    return celulas[indice]
