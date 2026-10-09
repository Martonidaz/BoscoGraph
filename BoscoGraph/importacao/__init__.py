'''
    Importação de grafos desenhados em outros programas, em três fases:

    1. Arquivos de programas (só Python, resultado exato): draw.io (.drawio), GraphML (.graphml,
       do yEd e do Gephi), DOT do Graphviz (.dot, .gv) e CSV (lista de arestas ou matriz de adjacência).
       Ficam em importacao/arquivos.py.
    2. PDF exportado (draw.io, PowerPoint, Graphviz...): a biblioteca PyMuPDF lê os desenhos
       (círculos, linhas, pontas de seta) e os textos com as posições. Em importacao/pdf.py.
    3. Foto ou imagem: OpenCV acha os círculos e as linhas, e o OCR (Tesseract) lê os nomes.
       É o que mais erra. Em importacao/imagem.py.

    Todas as fontes devolvem o mesmo formato intermediário, o "grafo bruto":
      {"vertices": [{"id": "n0", "rotulo": "São Paulo", "posicao": (x, y) ou None}, ...],
       "arestas":  [{"origem": "n0", "destino": "n1", "rotulo": "e1" ou "5", "peso": "5" ou None,
                     "seta": "fim", "inicio", "ambas", "nenhuma" ou None}, ...],
       "direcionado": True, False ou None (o arquivo não diz),
       "avisos": ["..."], "conferir": True/False, "imagem": bytes de um PNG ou None}
    ("seta" None = segue o "direcionado" do arquivo, como nas arestas do DOT e do GraphML)

    E uma função só, normalizar(), transforma o grafo bruto no que o editor aceita:
      - nomes de vértice válidos (até 10 letras, números e _), sem repetir;
      - rótulo de aresta que é um número vira peso ("5" -> peso 5);
      - orientação pelas setas: se alguma aresta tem seta, o grafo é orientado;
      - os limites de 26 vértices e 60 arestas.
    Cada ajuste feito vira um aviso, que a janela de conferência mostra antes de abrir no editor.
'''

import re
from pathlib import Path

import entrada
import modelos

# Os tipos de arquivo que aparecem na janela "Abrir" (o primeiro é o filtro inicial)
TIPOS_DE_ARQUIVO = [
    ("Todos os grafos", "*.bosco *.drawio *.xml *.graphml *.dot *.gv *.csv *.tsv *.txt *.pdf "
                        "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp"),
    ("BoscoGraph (abre como foi salvo)", "*.bosco"),
    ("draw.io", "*.drawio *.xml"),
    ("GraphML (yEd, Gephi)", "*.graphml"),
    ("DOT (Graphviz)", "*.dot *.gv"),
    ("CSV (arestas ou matriz)", "*.csv *.tsv *.txt"),
    ("PDF", "*.pdf"),
    ("Imagem ou foto", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp"),
    ("Todos os arquivos", "*.*"),
]
EXTENSOES_DE_IMAGEM = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp")
TAMANHO_MAXIMO_DO_ARQUIVO = 30 * 1024 * 1024        # 30 MB: um grafo de 26 vértices nunca precisa de mais


class ProblemaNaImportacao(Exception):
    # Um problema que o usuário precisa ler (o arquivo não é do formato esperado, falta uma
    # biblioteca, o grafo passa dos limites...). O editor mostra a mensagem na linha de avisos.
    pass


# Lê o arquivo e devolve o "importado": o grafo já normalizado, mais o que a conferência mostra.
# Rede de segurança: um erro que ninguém previu (um arquivo estranho de um jeito novo) vira uma
# mensagem para o usuário em vez de travar a janela. Os testes chamam os leitores direto, sem
# esta rede, para que um erro de programação apareça lá.
def importar_arquivo(caminho):
    try:
        return importar_sem_rede(caminho)
    except ProblemaNaImportacao:
        raise
    except Exception as erro:
        raise ProblemaNaImportacao(f"Não consegui ler {Path(caminho).name}: o arquivo parece estar com defeito "
                                   f"({type(erro).__name__}: {erro}).")


def importar_sem_rede(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        raise ProblemaNaImportacao(f"O arquivo {caminho} não existe.")
    if caminho.stat().st_size > TAMANHO_MAXIMO_DO_ARQUIVO:
        raise ProblemaNaImportacao(f"O arquivo {caminho.name} tem mais de 30 MB: grande demais para um grafo.")
    extensao = caminho.suffix.lower()
    # Os módulos são importados só quando precisa: o PDF e a imagem usam bibliotecas que podem
    # não estar instaladas, e o resto do programa funciona sem elas
    if extensao in (".drawio", ".xml"):
        from importacao import arquivos
        bruto = arquivos.ler_drawio(ler_texto(caminho))
        fonte = "draw.io"
    elif extensao == ".graphml":
        from importacao import arquivos
        bruto = arquivos.ler_graphml(ler_texto(caminho))
        fonte = "GraphML"
    elif extensao in (".dot", ".gv"):
        from importacao import arquivos
        bruto = arquivos.ler_dot(ler_texto(caminho))
        fonte = "DOT (Graphviz)"
    elif extensao in (".csv", ".tsv", ".txt"):
        from importacao import arquivos
        bruto = arquivos.ler_csv(ler_texto(caminho))
        fonte = "CSV"
    elif extensao == ".pdf":
        from importacao import pdf
        bruto = pdf.ler_pdf(caminho)
        fonte = "PDF"
    elif extensao in EXTENSOES_DE_IMAGEM:
        from importacao import imagem
        bruto = imagem.ler_imagem(caminho)
        fonte = "imagem"
    else:
        raise ProblemaNaImportacao(f"Não sei importar arquivos {extensao or 'sem extensão'}. Formatos aceitos: "
                                   f"draw.io, GraphML, DOT, CSV, PDF e imagens (PNG, JPG...).")
    importado = normalizar(bruto)
    importado["fonte"] = f"{caminho.name} ({fonte})"
    importado["nome"] = nome_do_modelo(caminho.stem)
    return importado


# Lê um arquivo de texto tentando as codificações mais comuns: UTF-8 (com ou sem a marca BOM,
# que o Excel coloca), Windows-1252 (o padrão do Excel em português) e, por fim, Latin-1
# (que aceita qualquer byte, então nunca falha).
def ler_texto(caminho):
    dados = caminho.read_bytes()
    for codificacao in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return dados.decode(codificacao)
        except UnicodeDecodeError:
            continue
    return dados.decode("latin-1", errors="replace")


# O nome do arquivo vira o nome sugerido para o modelo (sem os caracteres que o Windows não aceita)
def nome_do_modelo(texto):
    nome = ""
    for caractere in texto:
        if caractere not in '\\/:*?"<>|':
            nome += caractere
    nome = nome.strip().rstrip(".")[:modelos.TAMANHO_MAXIMO_DO_NOME].strip()
    if nome == "":
        nome = "Importado"
    return nome


# ----------------------------------------------------------------------
# Normalização: do grafo bruto para as regras do editor
# ----------------------------------------------------------------------

# Transforma um texto qualquer num nome de vértice válido e que ainda não foi usado:
# "São Paulo" -> "São_Paulo"; "nó #1" -> "nó_1"; "" -> a próxima letra livre;
# longo demais -> a primeira palavra e as iniciais das outras ("Destino final" -> "Destino_f",
# "Rimnicu Vilcea" -> "Rimnicu_V"), que fica mais legível que cortar no meio de uma palavra;
# repetido -> ganha um número no fim ("A" -> "A2").
def nome_de_vertice_valido(texto, usados):
    texto = re.sub(r"\s+", "_", texto.strip())      # espaços (um ou mais) viram um "_"
    limpo = ""
    for caractere in texto:
        if caractere.isalnum() or caractere == "_":
            limpo += caractere
    limpo = re.sub(r"_+", "_", limpo).strip("_")
    limite = entrada.TAMANHO_MAXIMO_DO_VERTICE
    if len(limpo) > limite:
        palavras = limpo.split("_")
        curto = palavras[0][:limite]
        for palavra in palavras[1:]:
            if len(curto) + 2 <= limite:
                curto += "_" + palavra[0]
        limpo = curto
    if limpo == "":
        limpo = entrada.proximo_nome_livre(usados) or "V"
    candidato = limpo
    numero = 2
    while candidato in usados:
        sufixo = str(numero)
        candidato = limpo[:entrada.TAMANHO_MAXIMO_DO_VERTICE - len(sufixo)] + sufixo
        numero += 1
    return candidato


# Um rótulo de aresta que pode ir para o editor: sem os separadores do texto das arestas
# (, ; : =), sem quebras de linha e com no máximo 16 caracteres
def nome_de_aresta_valido(texto):
    limpo = ""
    for caractere in texto:
        if caractere in ",;:=" or not caractere.isprintable():
            limpo += " "                    # vira espaço, para não grudar as palavras ("a,b" -> "a b")
        else:
            limpo += caractere
    limpo = re.sub(r"\s+", " ", limpo).strip()       # depois, os espaços repetidos viram um só
    return limpo[:entrada.TAMANHO_MAXIMO_DA_ARESTA].strip()


# Um rótulo que é só um número (com ou sem decimais) vira peso
def rotulo_numerico(texto):
    numero, problema = entrada.ler_numero(texto.strip())
    if problema or numero is None:
        return None
    return numero


def normalizar(bruto):
    avisos = list(bruto.get("avisos", []))

    # 1. Vértices: um nome válido para cada um, na ordem do arquivo
    vertices = []
    nome_do_id = {}
    posicoes = {}
    mudados = []
    for vertice in bruto["vertices"]:
        rotulo = vertice.get("rotulo") or ""
        if rotulo.strip() == "" and not vertice.get("sem_nome"):
            rotulo = str(vertice["id"])         # sem rótulo, o id do arquivo é o nome ("n0", "R1"...)
        # (num desenho reconhecido, vértice sem texto fica "sem_nome" e ganha a próxima letra livre)
        nome = nome_de_vertice_valido(rotulo, vertices)
        if nome != rotulo.strip() and rotulo.strip() != "":
            mudados.append(f"'{rotulo.strip()}' → {nome}")
        vertices.append(nome)
        nome_do_id[vertice["id"]] = nome
        if vertice.get("posicao") is not None:
            posicoes[nome] = (float(vertice["posicao"][0]), float(vertice["posicao"][1]))
    if mudados:
        exemplos = ", ".join(mudados[:5])
        if len(mudados) > 5:
            exemplos += f" e mais {len(mudados) - 5}"
        avisos.append(f"Nomes ajustados às regras do editor (até {entrada.TAMANHO_MAXIMO_DO_VERTICE} letras, "
                      f"números e _): {exemplos}.")
    if len(posicoes) != len(vertices):
        posicoes = {}               # posições pela metade não servem para desenhar

    # 2. Orientação: o que o arquivo diz (DOT, GraphML); se não diz, as setas desenhadas decidem
    # (draw.io, PDF, imagem); se nem isso (CSV), fica orientado e a conferência avisa que foi suposto.
    # Os laços não votam: a seta de um laço não diz nada (A -> A e A <- A são a mesma coisa) e é a que
    # mais se confunde num desenho (a curva fechada parece seta). Só votam se o grafo só tiver laços.
    direcionado = bruto.get("direcionado")
    setas = []
    for aresta in bruto["arestas"]:
        seta = aresta.get("seta")
        if seta is None:
            if direcionado is False:
                seta = "nenhuma"
            else:
                seta = "fim"
        setas.append(seta)
    votam = []
    for i in range(len(bruto["arestas"])):
        if bruto["arestas"][i]["origem"] != bruto["arestas"][i]["destino"]:
            votam.append(i)
    if not votam:
        votam = list(range(len(bruto["arestas"])))
    setas_desenhadas = False
    tem_seta = False
    tem_sem_seta = False
    com_seta = 0
    for i in votam:
        if bruto["arestas"][i].get("seta") is not None:
            setas_desenhadas = True
        if setas[i] == "nenhuma":
            tem_sem_seta = True
        else:
            tem_seta = True
            com_seta += 1
    # Num desenho RECONHECIDO (PDF, imagem), uma seta solta no meio de muitas ligações sem seta é mais
    # provável que seja engano da leitura (um canto de linha que pareceu seta) do que um grafo orientado
    # com quase todas as setas esquecidas. Por isso, aí, o grafo só é orientado se pelo menos 1/3 das
    # ligações tiverem seta (os laços não contam). A conferência mostra e deixa trocar.
    setas_ignoradas = 0
    if bruto.get("conferir") and tem_seta and tem_sem_seta and com_seta * 3 < len(votam):
        setas_ignoradas = com_seta
        tem_seta = False
    detectado = direcionado
    de_onde = "arquivo"                 # de onde veio a orientação: "arquivo", "setas" ou None (suposta)
    if direcionado is None:
        if setas_desenhadas:
            direcionado = tem_seta
            detectado = tem_seta
            de_onde = "setas"
            if setas_ignoradas:
                avisos.append(f"Só {entrada.contar(setas_ignoradas, 'ligação parece ter seta', 'ligações parecem ter seta')}"
                              f" (de {len(votam)}): deve ser engano da leitura, e o grafo ficou não orientado. "
                              f"Se ele for orientado, troque na conferência.")
        else:
            direcionado = True          # nada diz a orientação: "origem, destino" sugere um sentido
            detectado = None
            de_onde = None
    if tem_seta and tem_sem_seta and direcionado:
        avisos.append("Algumas arestas não têm seta: num grafo orientado, cada uma delas virou duas "
                      "(ida e volta), porque sem seta a ligação vale nos dois sentidos.")

    # 3. Arestas: rótulo numérico vira peso; sem seta (no orientado) e com duas setas viram ida e volta
    arestas = []
    ignoradas = 0
    pesos_ruins = []
    for i in range(len(bruto["arestas"])):
        aresta = bruto["arestas"][i]
        if aresta["origem"] not in nome_do_id or aresta["destino"] not in nome_do_id:
            ignoradas += 1
            continue
        origem = nome_do_id[aresta["origem"]]
        destino = nome_do_id[aresta["destino"]]
        rotulo = aresta.get("rotulo") or ""
        peso = None
        nome = nome_de_aresta_valido(rotulo)
        if aresta.get("peso") not in (None, ""):
            peso, problema = entrada.ler_numero(str(aresta["peso"]).strip())
            if problema:
                pesos_ruins.append(f"{origem} - {destino}: {aresta['peso']}")
                peso = None
        elif rotulo_numerico(rotulo) is not None:
            peso = rotulo_numerico(rotulo)
            nome = ""
        seta = setas[i]
        if not direcionado or seta == "fim":
            arestas.append((origem, destino, nome, peso))
        elif seta == "inicio":
            arestas.append((destino, origem, nome, peso))
        else:                                   # "ambas" ou "nenhuma" num grafo orientado: ida e volta
            arestas.append((origem, destino, nome, peso))
            if origem != destino:
                arestas.append((destino, origem, nome, peso))
    if ignoradas:
        avisos.append(entrada.contar(ignoradas, "aresta ignorada porque não liga", "arestas ignoradas porque não ligam")
                      + " dois vértices.")
    if pesos_ruins:
        avisos.append("Pesos que não são números foram ignorados: " + ", ".join(pesos_ruins[:4]) + ".")

    # 4. Limites do editor
    if not vertices:
        raise ProblemaNaImportacao("Não encontrei nenhum vértice nesse arquivo.")
    if len(vertices) > entrada.MAXIMO_DE_VERTICES:
        raise ProblemaNaImportacao(f"O grafo tem {len(vertices)} vértices; o BoscoGraph desenha no máximo "
                                   f"{entrada.MAXIMO_DE_VERTICES} (acima disso o desenho fica ilegível).")
    if len(arestas) > entrada.LIMITE_DE_ARESTAS:
        raise ProblemaNaImportacao(f"O grafo tem {len(arestas)} arestas; o BoscoGraph desenha no máximo "
                                   f"{entrada.LIMITE_DE_ARESTAS} (acima disso o desenho fica ilegível).")

    # As marcas da conferência (PDF e imagem) usam os ids das formas: aqui viram os nomes finais
    marcas = bruto.get("marcas")
    if marcas is not None:
        com_nomes = []
        for identificador, x, y, raio in marcas["vertices"]:
            com_nomes.append((nome_do_id.get(identificador, "?"), x, y, raio))
        marcas = {"vertices": com_nomes, "arestas": marcas["arestas"]}

    return {
        "vertices": vertices,
        "arestas": arestas,
        "direcionado": bool(direcionado),
        "orientacao_detectada": detectado,          # None = nada no arquivo diz a orientação
        "orientacao_veio_de": de_onde,
        "posicoes": posicoes,
        "avisos": avisos,
        "conferir": bruto.get("conferir", False),
        "imagem": bruto.get("imagem"),
        "marcas": marcas,                           # o que foi reconhecido, desenhado por cima da imagem
    }


# O grafo que o editor abre (o formato de modelos.novo_grafo). A orientação é a escolhida na
# conferência: num grafo não orientado, ida e volta da mesma ligação viram uma aresta só.
def grafo_para_o_editor(importado, direcionado):
    arestas = list(importado["arestas"])
    if importado["direcionado"] and not direcionado:
        arestas = juntar_ida_e_volta(arestas)
    elif not importado["direcionado"] and direcionado:
        # Não orientado lido como orientado: cada aresta vira ida e volta (ela valia nos dois sentidos)
        duplicadas = []
        for origem, destino, nome, peso in arestas:
            duplicadas.append((origem, destino, nome, peso))
            if origem != destino:
                duplicadas.append((destino, origem, nome, peso))
        arestas = duplicadas[:entrada.LIMITE_DE_ARESTAS]
    vertices = importado["vertices"]
    return modelos.novo_grafo(vertices, arestas, True, None, direcionado, posicoes=importado["posicoes"])


# A -> B e B -> A com o mesmo nome e peso viram uma aresta só A — B (no não orientado, são a mesma)
def juntar_ida_e_volta(arestas):
    juntas = []
    usadas = []
    for i in range(len(arestas)):
        if i in usadas:
            continue
        origem, destino, nome, peso = arestas[i]
        for j in range(i + 1, len(arestas)):
            if j not in usadas and arestas[j] == (destino, origem, nome, peso) and origem != destino:
                usadas.append(j)
                break
        juntas.append((origem, destino, nome, peso))
    return juntas
