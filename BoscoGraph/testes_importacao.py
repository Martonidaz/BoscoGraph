'''
    Conferências da importação, sem abrir janela.
    Rode com: python testes_importacao.py   (o testes.py também chama este arquivo)

    1. Os arquivos de exemplo (pasta exemplos_importacao) dão exatamente o grafo esperado.
    2. Ida e volta: centenas de grafos sorteados são escritos em DOT, GraphML, draw.io e CSV
       (com variações: aspas, comentários, compactação...) e lidos de volta: tem que dar o mesmo grafo.
    3. Arquivos com defeito (cortados, embaralhados, vazios) só podem dar ProblemaNaImportacao,
       com uma mensagem para o usuário, e nunca outro erro (que travaria o programa).
    4. PDF e imagem (fases 2 e 3), se as bibliotecas estiverem instaladas. Na imagem, além dos
       exemplos, o teste mede as taxas de acerto em grafos sorteados (limpos e com efeito de foto).
'''

import base64
import random
import tempfile
import urllib.parse
import zlib
from decimal import Decimal
from pathlib import Path

import entrada
import importacao
from importacao import arquivos

PASTA_DOS_EXEMPLOS = Path(__file__).resolve().parent / "exemplos_importacao"


def importar(nome):
    return importacao.importar_arquivo(PASTA_DOS_EXEMPLOS / nome)


def D(texto):
    return Decimal(texto)


# ----------------------------------------------------------------------
# 1. Os arquivos de exemplo
# ----------------------------------------------------------------------

def conferir_exemplos():
    # draw.io: setas viram orientação; "429,5" num rótulo vira peso; ponta solta perto de uma forma
    # é ligada a ela; ligação sem seta vira ida e volta; texto solto e ligação solta são ignorados
    for arquivo in ("rede.drawio", "rede_compactada.drawio"):
        r = importar(arquivo)
        assert r["vertices"] == ["São_Paulo", "RJ", "BH", "Vitória"], r["vertices"]
        assert r["arestas"] == [("São_Paulo", "RJ", "", D("429.5")), ("RJ", "BH", "BR-040", None),
                                ("BH", "RJ", "BR-040", None), ("São_Paulo", "BH", "", D(586)),
                                ("RJ", "Vitória", "", None)], r["arestas"]
        assert r["direcionado"] is True and r["orientacao_veio_de"] == "setas"
        assert r["posicoes"]["Vitória"] == (450.0, 370.0), "posição dentro do grupo soma a do grupo"
        texto = " ".join(r["avisos"])
        assert "Rotas do Sudeste" in texto and "ponta solta" in texto and "São Paulo" in texto
    assert "2 páginas" in " ".join(importar("rede.drawio")["avisos"])
    # Conferência: escolhendo "não orientado", ida e volta viram uma aresta só
    grafo = importacao.grafo_para_o_editor(importar("rede.drawio"), False)
    assert len(grafo["arestas"]) == 4 and grafo["direcionado"] is False and grafo["arrumacao"] == "arquivo"

    # yEd: rótulos e posições do yEd, peso pela chave "weight" (com valor padrão), setas do yEd
    r = importar("yed.graphml")
    assert r["vertices"] == ["Origem", "Meio", "Destino_f"]
    assert r["arestas"] == [("Origem", "Meio", "rota 1", D("2.5")), ("Meio", "Destino_f", "", D(1)),
                            ("Origem", "Destino_f", "", D(7)), ("Destino_f", "Origem", "", D(7))]
    assert r["posicoes"]["Meio"] == (265.0, 55.0)

    # Gephi: não orientado, nomes repetidos ganham número, y para cima vira y para baixo
    r = importar("gephi.graphml")
    assert r["vertices"] == ["Ana", "Bruno", "Carla", "Ana2"] and r["direcionado"] is False
    assert r["arestas"] == [("Ana", "Bruno", "", D(1)), ("Bruno", "Carla", "", D(3)), ("Carla", "Ana2", "", D(2))]
    assert r["posicoes"]["Bruno"][1] < r["posicoes"]["Ana"][1], "no Gephi, y maior é mais para cima"
    assert "hiperaresta" in " ".join(r["avisos"])

    # DOT: o mesmo resultado que o próprio Graphviz dá (conferido com dot -Tjson)
    r = importar("rede.dot")
    assert r["vertices"] == ["Roteador_1", "R2", "R3", "Servidor_w", "B1", "B2"], r["vertices"]
    assert r["arestas"] == [("Roteador_1", "R2", "", D(10)), ("R2", "R3", "fibra", D(4)),
                            ("R3", "Servidor_w", "fibra", D(4)), ("Roteador_1", "R3", "", D(1)),
                            ("R3", "Roteador_1", "", D("2.5")), ("R3", "R2", "", D("2.5")),
                            ("B1", "B2", "", D(1)), ("R2", "B1", "", D(1))], r["arestas"]

    # CSV do Excel em português: ";" e vírgula decimal; linha só com a origem = vértice isolado
    r = importar("estradas.csv")
    assert r["vertices"] == ["São_Paulo", "Rio", "BH", "Vitória"]
    assert r["arestas"] == [("São_Paulo", "Rio", "Via Dutra", D("429.5")), ("Rio", "BH", "", D(434)),
                            ("BH", "São_Paulo", "Fernão Dias", D(586))]
    assert r["orientacao_detectada"] is None, "o CSV não diz a orientação: a conferência pergunta"

    # Matriz de adjacência simétrica (como na Lista 03): não orientado, cada par uma vez
    r = importar("matriz.csv")
    assert r["vertices"] == list("ABCD") and r["direcionado"] is False
    assert r["arestas"] == [("A", "B", "", None), ("A", "C", "", None), ("B", "C", "", None), ("C", "D", "", None)]
    print("9a. Exemplos de importação (draw.io, yEd, Gephi, DOT, CSV, matriz): resultado exato")


def conferir_casos_pequenos():
    # Nomes: espaços viram _, símbolos saem, longos ficam com as iniciais, repetidos ganham número
    usados = []
    for texto, esperado in (("São Paulo", "São_Paulo"), ("nó #1", "nó_1"), ("Destino final", "Destino_f"),
                            ("Rimnicu Vilcea", "Rimnicu_V"), ("A", "A"), ("A", "A2"),
                            ("", "A3"),                         # vazio: segue o padrão do último nome
                            ("Supercalifragilístico", "Supercalif"), ("x" * 9 + " y", "xxxxxxxxx")):
        nome = importacao.nome_de_vertice_valido(texto, usados)
        assert nome == esperado, (texto, nome)
        assert entrada.validar_nome_de_vertice(nome, usados) == "", (texto, nome)
        usados.append(nome)
    assert importacao.nome_de_aresta_valido("a, b; c: d = e") == "a b c d e"
    assert importacao.nome_do_modelo('rede: v2 "final".') == "rede v2 final"

    # DOT: atributos do grafo não viram vértices; corrente, subgrafo, strict, comentários, + e HTML
    texto = '''strict graph {
        graph [bgcolor=white] rankdir = LR
        "a b" -- c -- d [label=<<b>5</b>>]  # comentário
        c -- "a b"                          // repetida (strict): some
        e -- {f g} [weight = 2]
        h [label="x" + "y"]
    }'''
    bruto = arquivos.ler_dot(texto)
    r = importacao.normalizar(bruto)
    assert r["vertices"] == ["a_b", "c", "d", "e", "f", "g", "xy"], r["vertices"]
    assert r["arestas"] == [("a_b", "c", "", D(5)), ("c", "d", "", D(5)), ("e", "f", "", D(2)),
                            ("e", "g", "", D(2))], r["arestas"]
    assert r["direcionado"] is False and "strict" in " ".join(r["avisos"])

    # CSV sem cabeçalho, separado por vírgula e com aspas: 3ª coluna número = peso, senão nome
    r = importacao.normalizar(arquivos.ler_csv('u,v,7\nv,w,"rota, norte"\nw,u\n'))
    assert r["vertices"] == ["u", "v", "w"], "u e v são vértices, não um cabeçalho"
    assert r["arestas"] == [("u", "v", "", D(7)), ("v", "w", "rota norte", None), ("w", "u", "", None)]
    # Matriz com pesos e não simétrica: orientado, os números viram pesos
    r = importacao.normalizar(arquivos.ler_csv(";X;Y\nX;0;2,5\nY;0;1\n"))
    assert r["direcionado"] is True and r["arestas"] == [("X", "Y", "", D("2.5")), ("Y", "Y", "", D(1))]

    # GraphML com directed por aresta num grafo orientado, peso em texto e chave sem attr.name
    texto = '''<graphml><key id="k" for="edge" attr.name="Peso"/><graph edgedefault="directed">
        <node id="1"/><node id="2"/>
        <edge source="1" target="2" directed="false"><data key="k">3,5</data></edge></graph></graphml>'''
    r = importacao.normalizar(arquivos.ler_graphml(texto))
    assert r["arestas"] == [("1", "2", "", D("3.5")), ("2", "1", "", D("3.5"))], "sem seta num orientado: ida e volta"

    # Limites do editor viram mensagem clara
    texto = "digraph {" + " ".join(f"v{i};" for i in range(30)) + "}"
    try:
        importacao.normalizar(arquivos.ler_dot(texto))
        assert False, "30 vértices passam do limite"
    except importacao.ProblemaNaImportacao as problema:
        assert "26" in str(problema)
    # XML com entidades é recusado (segurança: "billion laughs")
    perigoso = '<?xml version="1.0"?><!DOCTYPE g [<!ENTITY a "aaaa">]><graphml><graph/></graphml>'
    try:
        arquivos.ler_graphml(perigoso)
        assert False, "entidades XML deveriam ser recusadas"
    except importacao.ProblemaNaImportacao:
        pass
    print("9b. Casos difíceis: nomes, DOT (strict, subgrafo, HTML, +), CSV sem cabeçalho, matriz, limites, XML")


# ----------------------------------------------------------------------
# 2. Ida e volta com grafos sorteados
# ----------------------------------------------------------------------

def texto_dot(vertices, arestas, direcionado, sorteio):
    linhas = ["/* gerado pelo teste */", ("digraph" if direcionado else "graph") + " teste {"]
    if sorteio.random() < 0.5:
        linhas.append('  node [shape=circle]; rankdir=LR  # comentário')
    # Cada vértice tem um id no DOT: o próprio nome entre aspas, ou um id "v_3" com o nome no label
    # (aí as arestas precisam usar o id, como no Graphviz)
    id_no_dot = {}
    for vertice in vertices:
        if sorteio.random() < 0.5:
            id_no_dot[vertice] = f'"{vertice}"'
            linhas.append(f'  "{vertice}";')
        else:
            id_no_dot[vertice] = f"v_{vertices.index(vertice)}"
            linhas.append(f'  v_{vertices.index(vertice)} [label="{vertice}"]')
    operador = "->" if direcionado else "--"
    for origem, destino, nome, peso in arestas:
        atributos = []
        if nome:
            atributos.append(f'label="{nome}"')
        if peso is not None:
            atributos.append(f'weight="{entrada.formatar_numero(peso).replace(",", ".")}"')
        texto_atributos = f" [{', '.join(atributos)}]" if atributos else ""
        linhas.append(f'  {id_no_dot[origem]} {operador} {id_no_dot[destino]}{texto_atributos} // aresta')
    linhas.append("}")
    return "\n".join(linhas)


def texto_graphml(vertices, arestas, direcionado):
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
              '<key id="r" for="all" attr.name="label" attr.type="string"/>',
              '<key id="p" for="edge" attr.name="weight" attr.type="double"/>',
              f'<graph edgedefault="{"directed" if direcionado else "undirected"}">']
    for i in range(len(vertices)):
        linhas.append(f'<node id="n{i}"><data key="r">{vertices[i]}</data></node>')
    for origem, destino, nome, peso in arestas:
        dados = ""
        if nome:
            dados += f'<data key="r">{nome}</data>'
        if peso is not None:
            dados += f'<data key="p">{entrada.formatar_numero(peso).replace(",", ".")}</data>'
        linhas.append(f'<edge source="n{vertices.index(origem)}" target="n{vertices.index(destino)}">{dados}</edge>')
    linhas.append("</graph></graphml>")
    return "\n".join(linhas)


def texto_drawio(vertices, arestas, direcionado, compactar):
    celulas = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    for i in range(len(vertices)):
        celulas.append(f'<mxCell id="v{i}" value="{vertices[i]}" style="ellipse;" vertex="1" parent="1">'
                       f'<mxGeometry x="{100 * i}" y="{(i % 3) * 80}" width="40" height="40" as="geometry"/></mxCell>')
    for j in range(len(arestas)):
        origem, destino, nome, peso = arestas[j]
        estilo = "edgeStyle=none;" + ("" if direcionado else "endArrow=none;")
        rotulo = nome
        if peso is not None:
            rotulo = entrada.formatar_numero(peso)       # o draw.io só tem o texto: o peso vai no rótulo
        celulas.append(f'<mxCell id="a{j}" value="{rotulo}" style="{estilo}" edge="1" parent="1" '
                       f'source="v{vertices.index(origem)}" target="v{vertices.index(destino)}">'
                       f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    modelo = "<mxGraphModel><root>" + "".join(celulas) + "</root></mxGraphModel>"
    if compactar:
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        dados = compressor.compress(urllib.parse.quote(modelo).encode()) + compressor.flush()
        return f'<mxfile><diagram name="P">{base64.b64encode(dados).decode()}</diagram></mxfile>'
    return f'<mxfile><diagram name="P">{modelo}</diagram></mxfile>'


def texto_csv(vertices, arestas, sorteio):
    separador = sorteio.choice([";", ",", "\t"])
    linhas = [separador.join(["origem", "destino", "nome", "peso"])]
    com_aresta = []
    for origem, destino, nome, peso in arestas:
        texto_peso = entrada.formatar_numero(peso)
        if separador == ",":
            texto_peso = texto_peso.replace(",", ".")
        linhas.append(separador.join([origem, destino, nome, texto_peso]))
        com_aresta.extend([origem, destino])
    for vertice in vertices:
        if vertice not in com_aresta:
            linhas.append(vertice)                       # vértice isolado: só a origem
    return "\n".join(linhas)


def conferir_ida_e_volta(quantidade):
    sorteio = random.Random(99)
    for rodada in range(quantidade):
        direcionado = sorteio.random() < 0.5
        n = sorteio.randint(1, 15)
        vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "numeros", "prefixo"]), "R")
        m = sorteio.randint(0, entrada.maximo_de_arestas(n, True, False, direcionado) // 2)
        arestas = entrada.arestas_aleatorias(vertices, m, True, False, sorteio.randint(0, 10 ** 6), direcionado)
        if sorteio.random() < 0.5:
            arestas = entrada.numerar_arestas(arestas)
        pesos = []
        for i in range(len(arestas)):
            pesos.append(None if sorteio.random() < 0.3 else Decimal(sorteio.randint(-50, 500)) / 10)
        arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
        descricao = f"ida e volta {rodada}: {n} vértices, {len(arestas)} arestas, orientado={direcionado}"

        r = importacao.normalizar(arquivos.ler_dot(texto_dot(vertices, arestas, direcionado, sorteio)))
        assert (r["vertices"], r["arestas"], r["direcionado"]) == (vertices, arestas, direcionado), descricao
        r = importacao.normalizar(arquivos.ler_graphml(texto_graphml(vertices, arestas, direcionado)))
        assert (r["vertices"], r["arestas"], r["direcionado"]) == (vertices, arestas, direcionado), descricao
        # No draw.io o peso e o nome dividem o mesmo texto: com peso, o nome não volta
        esperadas = []
        for origem, destino, nome, peso in arestas:
            esperadas.append((origem, destino, "" if peso is not None else nome, peso))
        r = importacao.normalizar(arquivos.ler_drawio(texto_drawio(vertices, arestas, direcionado,
                                                                  sorteio.random() < 0.5)))
        assert r["vertices"] == vertices and r["arestas"] == esperadas, descricao
        assert r["direcionado"] == direcionado or not arestas, descricao
        # CSV: a ordem dos vértices é a ordem em que aparecem
        r = importacao.normalizar(arquivos.ler_csv(texto_csv(vertices, arestas, sorteio)))
        assert sorted(r["vertices"]) == sorted(vertices) and r["arestas"] == arestas, descricao
    print(f"9c. Ida e volta em {quantidade} grafos sorteados: DOT, GraphML, draw.io (com e sem compactar) e CSV")


# ----------------------------------------------------------------------
# 3. Arquivos com defeito: sempre uma mensagem, nunca um travamento
# ----------------------------------------------------------------------

def conferir_arquivos_com_defeito(quantidade):
    sorteio = random.Random(5)
    exemplos = {}
    for nome in ("rede.drawio", "yed.graphml", "rede.dot", "estradas.csv"):
        exemplos[nome] = (PASTA_DOS_EXEMPLOS / nome).read_text(encoding="utf-8")
    leitores = {".drawio": arquivos.ler_drawio, ".graphml": arquivos.ler_graphml, ".dot": arquivos.ler_dot,
                ".csv": arquivos.ler_csv}
    for rodada in range(quantidade):
        nome = sorteio.choice(list(exemplos))
        texto = exemplos[nome]
        mutacao = sorteio.choice(["cortar", "trocar", "apagar", "lixo"])
        if mutacao == "cortar":
            texto = texto[:sorteio.randint(0, len(texto))]
        elif mutacao == "trocar":
            lista = list(texto)
            for vez in range(sorteio.randint(1, 20)):
                lista[sorteio.randrange(len(lista))] = sorteio.choice('<>"{}[];,=:-#/\\ \nab1é')
            texto = "".join(lista)
        elif mutacao == "apagar":
            inicio = sorteio.randrange(len(texto))
            texto = texto[:inicio] + texto[inicio + sorteio.randint(1, 60):]
        else:
            texto = "".join(sorteio.choice("abc<>{}\"';,\n\t01") for vez in range(sorteio.randint(0, 200)))
        leitor = leitores[Path(nome).suffix]
        try:
            importacao.normalizar(leitor(texto))
        except importacao.ProblemaNaImportacao:
            pass                    # o esperado num arquivo com defeito: uma mensagem para o usuário
    # Arquivos que não existem, vazios ou de tipo desconhecido
    with tempfile.TemporaryDirectory() as pasta:
        for nome, conteudo in (("vazio.csv", ""), ("x.docx", "abc"), ("quebrado.graphml", "<graphml>")):
            caminho = Path(pasta) / nome
            caminho.write_text(conteudo, encoding="utf-8")
            try:
                importacao.importar_arquivo(caminho)
                assert False, nome
            except importacao.ProblemaNaImportacao:
                pass
        try:
            importacao.importar_arquivo(Path(pasta) / "nao_existe.dot")
            assert False
        except importacao.ProblemaNaImportacao:
            pass
    print(f"9d. {quantidade} arquivos com defeito: todos viram mensagem para o usuário (nenhum travamento)")


# ----------------------------------------------------------------------
# 4. PDF (fase 2): só roda se a PyMuPDF estiver instalada
# ----------------------------------------------------------------------

def tem_biblioteca(nome):
    try:
        __import__(nome)
        return True
    except ImportError:
        return False


def conferir_pdf():
    if not tem_biblioteca("pymupdf") and not tem_biblioteca("fitz"):
        print("9e. PDF: pulado (instale a PyMuPDF para conferir: pip install pymupdf)")
        return
    # Graphviz orientado: pesos nos rótulos ("8,5" com vírgula), laço e vértice isolado
    r = importar("graphviz_orientado.pdf")
    assert r["vertices"] == ["S", "A", "B", "T", "X"] and r["direcionado"] is True, r["vertices"]
    assert sorted(r["arestas"]) == sorted([("S", "A", "", D(4)), ("S", "B", "", D(2)), ("B", "A", "", D(1)),
                                           ("A", "T", "", D(5)), ("B", "T", "", D("8.5")), ("T", "T", "", None)])
    assert r["conferir"] and r["imagem"].startswith(b"\x89PNG") and len(r["marcas"]["vertices"]) == 5
    # Graphviz não orientado: nenhuma seta = não orientado
    r = importar("graphviz_nao_orientado.pdf")
    assert r["vertices"] == ["Ana", "Bia", "Caio", "Davi", "Eva"] and r["direcionado"] is False
    assert sorted(r["arestas"]) == sorted([("Ana", "Bia", "", None), ("Bia", "Caio", "", None),
                                           ("Caio", "Ana", "", None), ("Caio", "Davi", "", None),
                                           ("Davi", "Davi", "", None)])
    # Estilo draw.io: caixas com texto, linha quebrada, rótulo com fundo, título e moldura ignorados
    r = importar("drawio_exportado.pdf")
    assert r["vertices"] == ["Pedido", "Estoque", "NF", "Entrega"], r["vertices"]
    assert r["arestas"] == [("Pedido", "Estoque", "", D(3)), ("Estoque", "Entrega", "", D("1.5")),
                            ("Pedido", "NF", "", None), ("NF", "Entrega", "", None), ("Entrega", "NF", "", None),
                            ("NF", "Entrega", "", None)], r["arestas"]
    assert "Fluxo de pedidos" in " ".join(r["avisos"])
    print("9e. PDF (Graphviz orientado e não orientado, estilo draw.io): grafo reconhecido por inteiro")
    conferir_pdf_do_graphviz_sorteado(150)


# Grafos sorteados desenhados pelo próprio Graphviz (dot -Tpdf) e lidos de volta.
# Só roda se o Graphviz estiver instalado (o programa "dot").
# A estrutura (vértices, ligações e sentidos) precisa sair 100% certa. Os rótulos não: às vezes o
# Graphviz põe o rótulo de uma aresta colado em OUTRA aresta, e nem uma pessoa saberia de quem ele é
# (é por isso que o PDF passa pela conferência). Para os rótulos, o teste mede a taxa de acerto.
def conferir_pdf_do_graphviz_sorteado(quantidade):
    import shutil
    import subprocess
    if shutil.which("dot") is None:
        print("9f. PDF do Graphviz sorteado: pulado (o Graphviz não está instalado)")
        return
    sorteio = random.Random(8)
    rotulos_certos = 0
    rotulos_no_total = 0
    grafos_perfeitos = 0
    with tempfile.TemporaryDirectory() as pasta:
        for rodada in range(quantidade):
            direcionado = sorteio.random() < 0.6
            n = sorteio.randint(2, 9)
            vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "prefixo"]), "R")
            m = sorteio.randint(1, min(12, entrada.maximo_de_arestas(n, True, False, direcionado)))
            arestas = entrada.arestas_aleatorias(vertices, m, sorteio.random() < 0.3, False,
                                                 sorteio.randint(0, 10 ** 6), direcionado)
            pesos = []
            for i in range(len(arestas)):
                pesos.append(None if sorteio.random() < 0.4 else Decimal(sorteio.randint(1, 99)))
            arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
            linhas = [("digraph" if direcionado else "graph") + " { node [shape=circle];"]
            for vertice in vertices:
                linhas.append(f'"{vertice}";')
            for origem, destino, nome, peso in arestas:
                rotulo = f' [label="{peso}"]' if peso is not None else ""
                linhas.append(f'"{origem}" {"->" if direcionado else "--"} "{destino}"{rotulo};')
            arquivo_dot = Path(pasta) / "g.dot"
            arquivo_pdf = Path(pasta) / f"g{rodada}.pdf"
            arquivo_dot.write_text("\n".join(linhas) + "}", encoding="utf-8")
            subprocess.run(["dot", "-Tpdf", str(arquivo_dot), "-o", str(arquivo_pdf)], check=True,
                           stderr=subprocess.DEVNULL)
            r = importacao.importar_arquivo(arquivo_pdf)
            descricao = f"PDF sorteado {rodada}: {linhas}"

            # No não orientado, a ordem das pontas de cada aresta não importa
            def chave(aresta):
                origem, destino, nome, peso = aresta
                if not direcionado:
                    origem, destino = min(origem, destino), max(origem, destino)
                return (origem, destino, peso)
            esperadas = sorted(chave(aresta) for aresta in arestas)
            obtidas = sorted(chave(aresta) for aresta in r["arestas"])
            assert sorted(r["vertices"]) == sorted(vertices) and r["direcionado"] == direcionado, descricao
            assert [a[:2] for a in obtidas] == [a[:2] for a in esperadas], (descricao, "estrutura", obtidas)
            # Rótulos: quantos pares (ligação, peso) bateram
            sobrando = list(obtidas)
            for aresta in esperadas:
                if aresta[2] is not None:
                    rotulos_no_total += 1
                    if aresta in sobrando:
                        rotulos_certos += 1
                if aresta in sobrando:
                    sobrando.remove(aresta)
            if obtidas == esperadas:
                grafos_perfeitos += 1
    taxa = rotulos_certos / max(1, rotulos_no_total)
    assert taxa >= 0.95, f"só {taxa:.1%} dos rótulos certos"
    print(f"9f. {quantidade} grafos sorteados desenhados pelo Graphviz (PDF): estrutura 100% certa; "
          f"rótulos {rotulos_certos}/{rotulos_no_total} ({taxa:.1%}); {grafos_perfeitos} grafos perfeitos")


# ----------------------------------------------------------------------
# 5. Imagem e foto (fase 3): só roda se o OpenCV estiver instalado
# ----------------------------------------------------------------------

def conferir_imagem():
    if not tem_biblioteca("cv2"):
        print("9g. Imagem: pulado (instale o OpenCV para conferir: pip install opencv-python-headless)")
        return
    from importacao import imagem
    tem_ocr = imagem.carregar_ocr() is not None

    # Arquivo que não é imagem e imagem cortada pela metade: mensagem para o usuário, nunca outro erro
    with tempfile.TemporaryDirectory() as pasta:
        falsa = Path(pasta) / "falsa.png"
        falsa.write_bytes(b"isto nao e uma imagem")
        cortada = Path(pasta) / "cortada.png"
        cortada.write_bytes((PASTA_DOS_EXEMPLOS / "graphviz_orientado.png").read_bytes()[:900])
        for arquivo in (falsa, cortada):
            try:
                importacao.importar_arquivo(arquivo)
                assert False, f"{arquivo.name} deveria dar ProblemaNaImportacao"
            except importacao.ProblemaNaImportacao:
                pass
        # Ruído puro e uma imagem toda branca: sem vértices (ou um grafo qualquer), mas sem travar
        import cv2
        import numpy
        sorteio = numpy.random.default_rng(3)
        for nome, figura in (("ruido.png", sorteio.integers(0, 256, (300, 400, 3), dtype=numpy.uint8)),
                             ("branca.png", numpy.full((300, 400, 3), 255, dtype=numpy.uint8))):
            caminho = Path(pasta) / nome
            cv2.imwrite(str(caminho), figura)
            try:
                importacao.importar_arquivo(caminho)
            except importacao.ProblemaNaImportacao:
                pass

    # Sem o leitor de texto: a estrutura sai igual, os nomes viram A, B, C... e há um aviso
    original = imagem.carregar_ocr
    imagem.carregar_ocr = lambda: None
    try:
        r = importar("graphviz_orientado.png")
    finally:
        imagem.carregar_ocr = original
    assert len(r["vertices"]) == 5 and len(r["arestas"]) == 6 and r["direcionado"] is True
    assert "Tesseract" in " ".join(r["avisos"])

    if not tem_ocr:
        print("9g. Imagem: estrutura conferida sem o leitor de texto (instale o Tesseract para conferir os nomes)")
        return
    # Os três exemplos: o grafo inteiro, com nomes e pesos (o "8,5" com vírgula)
    esperado = sorted([("S", "A", "", D(4)), ("S", "B", "", D(2)), ("B", "A", "", D(1)), ("A", "T", "", D(5)),
                       ("B", "T", "", D("8.5")), ("T", "T", "", None)], key=chave_de_ordem)
    for nome in ("graphviz_orientado.png", "foto_graphviz.jpg"):
        r = importar(nome)
        assert sorted(r["vertices"]) == ["A", "B", "S", "T", "X"] and r["direcionado"] is True, (nome, r["vertices"])
        assert sorted(r["arestas"], key=chave_de_ordem) == esperado, (nome, r["arestas"])
        assert r["conferir"] and r["imagem"].startswith(b"\x89PNG") and len(r["marcas"]["vertices"]) == 5
    r = importar("drawio_exportado.png")
    assert r["vertices"] == ["Pedido", "Estoque", "NF", "Entrega"], r["vertices"]
    assert sorted(r["arestas"], key=chave_de_ordem) == sorted(
        [("Pedido", "Estoque", "", D(3)), ("Estoque", "Entrega", "", D("1.5")), ("Pedido", "NF", "", None),
         ("NF", "Entrega", "", None), ("Entrega", "NF", "", None), ("NF", "Entrega", "", None)], key=chave_de_ordem)
    # Tema escuro do draw.io (a imagem que um usuário mandou e não abria): fundo escuro com grade,
    # vértices pintados de verde (um de roxo), nomes em branco, ligações ortogonais sem seta e duas
    # junções em T (D4 e D2 chegam juntas em F3; H4 e H2 também). São os movimentos do cavalo a partir de F3.
    r = importar("drawio_tema_escuro.png")
    casas = ["E5", "G5", "D4", "H4", "D2", "H2", "E1", "G1"]
    assert sorted(r["vertices"]) == sorted(casas + ["F3"]) and r["direcionado"] is False, r["vertices"]
    ligacoes = []
    for origem, destino, nome, peso in r["arestas"]:
        ligacoes.append(tuple(sorted((origem, destino))))
    assert sorted(ligacoes) == sorted(tuple(sorted((casa, "F3"))) for casa in casas), r["arestas"]
    print("9g. Imagem (Graphviz, draw.io claro e escuro e uma foto sintética): grafo reconhecido por inteiro; "
          "arquivos com defeito viram mensagem")
    conferir_imagens_sorteadas(40, "limpa")
    conferir_imagens_sorteadas(40, "foto")
    conferir_imagens_sorteadas(40, "escura")


def chave_de_ordem(aresta):
    origem, destino, nome, peso = aresta
    return (origem, destino, nome, peso is not None, peso or 0)


# Efeito de "foto de celular" numa imagem limpa: inclinação (perspectiva), luz desigual, ruído,
# um pouco de desfoque e a compressão do JPEG
def foto_sintetica(caminho_png, caminho_jpg, sorteio):
    import cv2
    import numpy
    figura = cv2.imread(str(caminho_png))
    altura, largura = figura.shape[:2]
    m = 0.04
    cantos = numpy.float32([[0, 0], [largura, 0], [largura, altura], [0, altura]])
    tortos = numpy.float32([[sorteio.uniform(0, m) * largura, sorteio.uniform(0, m) * altura],
                            [largura - sorteio.uniform(0, m) * largura, sorteio.uniform(0, m) * altura],
                            [largura - sorteio.uniform(0, m) * largura, altura - sorteio.uniform(0, m) * altura],
                            [sorteio.uniform(0, m) * largura, altura - sorteio.uniform(0, m) * altura]])
    figura = cv2.warpPerspective(figura, cv2.getPerspectiveTransform(cantos, tortos), (largura, altura),
                                 borderValue=(235, 235, 235))
    ys, xs = numpy.mgrid[0:altura, 0:largura]
    luz = 0.72 + 0.28 * (xs / largura * sorteio.uniform(0.3, 1) + ys / altura * sorteio.uniform(0, 0.7)) / 1.7
    figura = figura.astype(numpy.float32) * luz[:, :, None] * 0.95
    figura += numpy.random.default_rng(sorteio.randint(0, 10 ** 6)).normal(0, 6, figura.shape)
    figura = cv2.GaussianBlur(numpy.clip(figura, 0, 255).astype(numpy.uint8), (3, 3), 0.9)
    cv2.imwrite(str(caminho_jpg), figura, [cv2.IMWRITE_JPEG_QUALITY, 70])


# A grade de fundo de um programa de desenho: linhas a cada 30, 40 ou 50 pixels, um pouco mais claras
# que o fundo, desenhadas só onde a imagem é fundo (os vértices e as linhas ficam por cima)
def com_grade(caminho, fundo, sorteio):
    import cv2
    import numpy
    figura = cv2.imread(str(caminho))
    alvo = numpy.array(fundo, dtype=numpy.int16)
    e_fundo = numpy.abs(figura.astype(numpy.int16) - alvo).max(axis=2) <= 6
    passo = sorteio.choice([30, 40, 50])
    grade = numpy.zeros(figura.shape[:2], dtype=bool)
    for desvio in (0, 1):
        grade[desvio::passo, :] = True
        grade[:, desvio::passo] = True
    figura[e_fundo & grade] = numpy.clip(alvo + 24, 0, 255).astype(numpy.uint8)
    cv2.imwrite(str(caminho), figura)


# Grafos sorteados desenhados pelo Graphviz (dot -Tpng, em 72, 96, 110 ou 150 pontos por polegada) e
# lidos de volta: "limpa", "foto" (com efeito de foto) ou "escura" (tema escuro: fundo quase preto com
# grade, vértices pintados de uma cor, nomes e linhas claros). Uma imagem não tem "objetos", só pixels: aqui não dá
# para exigir 100%. O teste MEDE as taxas de acerto e exige um mínimo, para nenhuma mudança piorar a
# leitura sem ninguém ver. Os mínimos ficam um pouco abaixo do que foi medido nesta mesma sequência
# sorteada (semente 2718), que NÃO foi usada para ajustar o reconhecimento (foi separada para isso).
#   - vértices: a quantidade certa;   - nomes: todos os nomes certos (OCR);
#   - estrutura: com os nomes certos, as mesmas ligações e sentidos;   - rótulos: os pesos certos.
def conferir_imagens_sorteadas(quantidade, modo):
    import shutil
    import subprocess
    tipo = {"limpa": "imagens limpas", "foto": "fotos sintéticas", "escura": "tema escuro com grade"}[modo]
    if shutil.which("dot") is None:
        print(f"9h. Imagens sorteadas ({tipo}): pulado (o Graphviz não está instalado)")
        return
    sorteio = random.Random(2718)
    contagem = {"vertices": 0, "nomes": 0, "estrutura": 0, "rotulos_certos": 0, "rotulos": 0}
    with tempfile.TemporaryDirectory() as pasta:
        for rodada in range(quantidade):
            direcionado = sorteio.random() < 0.6
            n = sorteio.randint(2, 9)
            vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "prefixo"]), "R")
            m = sorteio.randint(1, min(12, entrada.maximo_de_arestas(n, True, False, direcionado)))
            arestas = entrada.arestas_aleatorias(vertices, m, sorteio.random() < 0.3, False,
                                                 sorteio.randint(0, 10 ** 6), direcionado)
            pesos = []
            for i in range(len(arestas)):
                if sorteio.random() < 0.4:
                    pesos.append(None)
                elif sorteio.random() < 0.2:
                    pesos.append(Decimal(sorteio.randint(10, 99)) / 10)          # decimal: "4,7"
                else:
                    pesos.append(Decimal(sorteio.randint(1, 99)))
            arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
            cabecalho = " { node [shape=circle];"
            if modo == "escura":
                cor = sorteio.choice(["#43ba43", "#9933ff", "#1e88e5", "#f57c00", "#e53935", "#00897b"])
                cabecalho = (' { bgcolor="#121212"; node [shape=circle, style=filled, fillcolor="' + cor +
                             '", color="' + cor + '", fontcolor="white"]; edge [color="#dddddd", fontcolor="#dddddd"];')
            linhas = [("digraph" if direcionado else "graph") + cabecalho]
            for vertice in vertices:
                linhas.append(f'"{vertice}";')
            for origem, destino, nome, peso in arestas:
                rotulo = f' [label="{entrada.formatar_numero(peso)}"]' if peso is not None else ""
                linhas.append(f'"{origem}" {"->" if direcionado else "--"} "{destino}"{rotulo};')
            dpi = sorteio.choice([72, 96, 110, 150])
            arquivo_dot = Path(pasta) / "g.dot"
            arquivo = Path(pasta) / f"g{rodada}.png"
            arquivo_dot.write_text("\n".join(linhas) + "}", encoding="utf-8")
            subprocess.run(["dot", "-Tpng", f"-Gdpi={dpi}", str(arquivo_dot), "-o", str(arquivo)], check=True,
                           stderr=subprocess.DEVNULL)
            if modo == "escura":
                com_grade(arquivo, (18, 18, 18), sorteio)
            if modo == "foto":
                foto_png = arquivo
                arquivo = Path(pasta) / f"g{rodada}.jpg"
                foto_sintetica(foto_png, arquivo, sorteio)
            try:
                r = importacao.importar_arquivo(arquivo)
            except importacao.ProblemaNaImportacao:
                continue                                    # conta como erro em tudo

            def chave(aresta):
                origem, destino, nome, peso = aresta
                if not direcionado:
                    origem, destino = min(origem, destino), max(origem, destino)
                return (origem, destino, peso is not None, peso or 0)
            esperadas = sorted(chave(aresta) for aresta in arestas)
            obtidas = sorted(chave(aresta) for aresta in r["arestas"])
            if len(r["vertices"]) == len(vertices):
                contagem["vertices"] += 1
            if sorted(r["vertices"]) != sorted(vertices):
                continue
            contagem["nomes"] += 1
            if r["direcionado"] != direcionado or [a[:2] for a in obtidas] != [a[:2] for a in esperadas]:
                continue
            contagem["estrutura"] += 1
            sobrando = list(obtidas)
            for aresta in esperadas:
                if aresta[2]:
                    contagem["rotulos"] += 1
                    if aresta in sobrando:
                        contagem["rotulos_certos"] += 1
                if aresta in sobrando:
                    sobrando.remove(aresta)
    taxas = {"vertices": contagem["vertices"] / quantidade, "nomes": contagem["nomes"] / quantidade,
             "estrutura": contagem["estrutura"] / max(1, contagem["nomes"]),
             "rotulos": contagem["rotulos_certos"] / max(1, contagem["rotulos"])}
    minimos = {"limpa": MINIMOS_DA_IMAGEM_LIMPA, "foto": MINIMOS_DA_FOTO, "escura": MINIMOS_DO_TEMA_ESCURO}[modo]
    for nome in minimos:
        assert taxas[nome] >= minimos[nome], f"{tipo}: {nome} {taxas[nome]:.0%} (mínimo {minimos[nome]:.0%})"
    print(f"9h. {quantidade} grafos sorteados do Graphviz, {tipo}: vértices {taxas['vertices']:.0%}, "
          f"nomes {taxas['nomes']:.0%}, estrutura {taxas['estrutura']:.0%} (dos com nomes certos), "
          f"rótulos {contagem['rotulos_certos']}/{contagem['rotulos']} ({taxas['rotulos']:.0%})")


# Medido (semente 2718, 40 grafos de cada): limpas -> vértices 100%, nomes 100%, estrutura 90%,
# rótulos 92%; fotos -> vértices 98%, nomes 72%, estrutura 90%, rótulos 86%; tema escuro com grade ->
# vértices 92%, nomes 85%, estrutura 85%, rótulos 76%. Outra versão do Tesseract pode ler um pouco
# diferente; por isso a folga.
MINIMOS_DA_IMAGEM_LIMPA = {"vertices": 0.95, "nomes": 0.9, "estrutura": 0.85, "rotulos": 0.85}
MINIMOS_DA_FOTO = {"vertices": 0.9, "nomes": 0.6, "estrutura": 0.8, "rotulos": 0.75}
MINIMOS_DO_TEMA_ESCURO = {"vertices": 0.85, "nomes": 0.75, "estrutura": 0.75, "rotulos": 0.65}


def rodar():
    conferir_exemplos()
    conferir_casos_pequenos()
    conferir_ida_e_volta(200)
    conferir_arquivos_com_defeito(600)
    conferir_pdf()
    conferir_imagem()


if __name__ == "__main__":
    rodar()
    print("Todos os testes da importação passaram.")
