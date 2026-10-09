'''
    Conferências das exportações (pasta exportacao/), sem abrir janela.
    Rode com: python testes_exportacao.py   (o testes.py também chama este arquivo)

      14a. O arquivo .bosco: grafos sorteados salvos e lidos de volta ficam iguais (pesos decimais
           exatos, posições, heurística, limite) e a tela também; arquivos estragados viram uma mensagem
           clara (e nunca um erro do Python).
      14b. O código-fonte: para cada busca, programas nas cinco linguagens com grafos sorteados; cada
           programa roda (os que precisam são compilados, sem nenhum aviso) e escreve EXATAMENTE a saída
           esperada que vai no fim do arquivo. As linguagens sem compilador nesta máquina são puladas.
      14c. As figuras: a geometria igual à do Tkinter (curva suave, ponta de seta, tracejado), o SVG é um
           XML válido, o PNG (com a Pillow) tem as cores nos lugares certos e o PDF tem os textos.
      14d. O relatório: tabelas compridas continuam na página seguinte repetindo o cabeçalho, matrizes
           largas saem em pedaços, o código mantém a indentação e todas as páginas têm o rodapé.
      14e. A prévia e os recentes do .bosco: a data e o programa que salvou voltam na leitura; a lista dos
           abertos por último põe o mais novo em cima, não repete, guarda no máximo 6 e nunca dá erro
           (arquivo faltando, estragado ou pasta sem permissão).
'''

import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as arvore_xml
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

import algoritmos
import modelos
from exportacao import bosco, codigo_fonte, geometria, relatorio
from exportacao import figura as figuras
from exportacao import pdf
from testes_estudo import grafo_sorteado

CHAVES = [informacoes["chave"] for informacoes in algoritmos.ALGORITMOS]


# ----------------------------------------------------------------------
# 14a. O arquivo .bosco
# ----------------------------------------------------------------------

def grafo_para_o_bosco(sorteio):
    algoritmo = sorteio.choice(CHAVES)
    vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo_sorteado(sorteio, algoritmo)
    posicoes = {}
    if sorteio.random() < 0.5:
        for vertice in vertices:
            posicoes[vertice] = (round(sorteio.uniform(-500, 500), 2), round(sorteio.uniform(-500, 500), 2))
    return modelos.novo_grafo(vertices, arestas, ordenar, inicio, direcionado, algoritmo, destino, heuristica,
                              posicoes, None, sorteio.choice([None, 0, 3, 7]))


def conferir_bosco(quantidade):
    sorteio = random.Random(14)
    with tempfile.TemporaryDirectory() as pasta:
        caminho = os.path.join(pasta, "teste.bosco")
        for vez in range(quantidade):
            grafo = grafo_para_o_bosco(sorteio)
            tela = {"parte": sorteio.choice(list(bosco.ESCOLHAS_DAS_PARTES)),
                    "partes": {"passo": {"posicao": sorteio.randint(-1, 40), "mostrar": {"codigo": True}},
                               "adjacencia": {"celula": (0, None), "modo": "pesos"},
                               "linha": {"linha": 3, "escolhida": ("java", 12)},
                               "pesos": {"arestas": list(range(len(grafo["arestas"])))[:2]}},
                    "exibir": {"pesos": False, "nomes": True, "tema": "escuro", "zoom": 1.3, "velocidade": 3}}
            nome = sorteio.choice(["Prova 01", "Grafo com acentos: ação ∞ π", "x"])
            bosco.salvar(caminho, grafo, nome, tela)
            lido, nome_lido, tela_lida = bosco.ler(caminho)
            assert nome_lido == nome
            for campo in ("vertices", "arestas", "ordenar", "direcionado", "algoritmo", "heuristica", "limite"):
                assert lido[campo] == grafo[campo], (campo, lido[campo], grafo[campo])
            assert lido["inicio"] == (grafo["inicio"] if grafo["inicio"] in grafo["vertices"] else None)
            assert lido["destino"] == grafo["destino"]
            assert lido["posicoes"] == grafo["posicoes"] and lido["arrumacao"] == grafo["arrumacao"]
            # Os pesos voltam como Decimal exato (2,5 e não 2.4999999)
            for origem, destino, nome_da_aresta, peso in lido["arestas"]:
                assert peso is None or isinstance(peso, Decimal)
            assert tela_lida["parte"] == tela["parte"]
            assert tela_lida["partes"]["adjacencia"]["celula"] == (0, None)        # a tupla volta como tupla
            assert tela_lida["partes"]["linha"]["escolhida"] == ("java", 12)
            assert tela_lida["exibir"] == tela["exibir"]
            assert tela_lida["partes"]["passo"] == tela["partes"]["passo"]

        # Arquivos estragados: sempre um ValueError com uma explicação (nunca outro erro)
        bom = json.loads(Path(caminho).read_text(encoding="utf-8"))
        estragados = [
            ("não é json {", "não é um JSON válido"),
            ("[1, 2, 3]", "não é um arquivo do BoscoGraph"),
            (json.dumps({"formato": "outro"}), "não é um arquivo do BoscoGraph"),
            (json.dumps(dict(bom, versao=99)), "BoscoGraph mais novo"),
            (json.dumps(dict(bom, versao="1")), "versão do arquivo"),
            (json.dumps(dict(bom, grafo=[])), "precisa ter as listas"),
            (json.dumps(dict(bom, grafo=dict(bom["grafo"], arestas=[{"origem": "?", "destino": "?"}]))),
             "vértice que não existe"),
            (json.dumps(dict(bom, grafo=dict(bom["grafo"], vertices=["A", "A"], arestas=[]))), "Já existe"),
        ]
        for texto, pedaco in estragados:
            Path(caminho).write_text(texto, encoding="utf-8")
            try:
                bosco.ler(caminho)
            except ValueError as problema:
                assert pedaco in str(problema), (pedaco, str(problema))
            else:
                raise AssertionError("aceitou um arquivo estragado: " + texto[:60])
        # Com BOM (o Bloco de Notas do Windows grava assim) e com a tela toda errada: abre igual
        dados = dict(bom, tela={"parte": 5, "partes": {"passo": {"posicao": "dez"}, "x": 1}, "exibir": []})
        Path(caminho).write_bytes(b"\xef\xbb\xbf" + json.dumps(dados).encode("utf-8"))
        grafo, nome, tela = bosco.ler(caminho)
        assert tela == {"parte": None, "partes": {"passo": {}}, "exibir": {}}, tela
        try:
            bosco.ler(os.path.join(pasta, "nao_existe.bosco"))
        except ValueError as problema:
            assert "não consegui ler" in str(problema)
    print(f"14a. Arquivo .bosco: {quantidade} grafos sorteados salvos e lidos iguais (com a tela); "
          f"{len(estragados) + 2} arquivos estragados viram uma mensagem clara")


# ----------------------------------------------------------------------
# 14b. O código-fonte
# ----------------------------------------------------------------------

# A saída esperada que vai no fim do arquivo (o comentário "Saída esperada")
def saida_do_comentario(texto, comentario):
    linhas = texto.split("\n")
    inicio = None
    for posicao in range(len(linhas)):
        if "Saída esperada" in linhas[posicao]:
            inicio = posicao + 1
    saida = []
    for linha in linhas[inicio:]:
        if linha.startswith(comentario + "     "):
            saida.append(linha[len(comentario) + 5:])
    return saida


def tem_programa(nome):
    return shutil.which(nome) is not None


# Cada linguagem: (extensão, comentário, programas necessários, função que roda o arquivo e devolve a saída)
def rodar_python(caminho, pasta):
    # PYTHONIOENCODING: o programa escreve a saída em UTF-8. Sem isso, no Windows, quando a saída vai para
    # um "cano" (pipe) e não para a tela, o Python usa a página de código do sistema (cp1252): o "á" de
    # "árvore" vira o byte 0xE1, que não é UTF-8, e a leitura abaixo quebra
    return subprocess.run([sys.executable, caminho], capture_output=True, text=True, encoding="utf-8",
                          timeout=120, cwd=pasta, env=dict(os.environ, PYTHONIOENCODING="utf-8"))


def rodar_java(caminho, pasta):
    return subprocess.run(["java", "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", caminho], capture_output=True,
                          text=True, encoding="utf-8", timeout=180, cwd=pasta)


def compilar_e_rodar(compilador, opcoes, caminho, pasta):
    executavel = caminho + (".exe" if sys.platform.startswith("win") else ".bin")
    resultado = subprocess.run([compilador] + opcoes[0] + [caminho, "-o", executavel] + opcoes[1], capture_output=True,
                               text=True, timeout=180, cwd=pasta)
    if resultado.returncode != 0 or resultado.stderr.strip():
        raise AssertionError(f"{caminho} não compilou sem avisos:\n{resultado.stderr[:3000]}")
    return subprocess.run([executavel], capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=pasta)


def rodar_c(caminho, pasta):
    return compilar_e_rodar("gcc", (["-std=c11", "-Wall", "-Wextra", "-pedantic", "-Werror", "-O2"], ["-lm"]),
                            caminho, pasta)


def rodar_cpp(caminho, pasta):
    return compilar_e_rodar("g++", (["-std=c++17", "-Wall", "-Wextra", "-pedantic", "-Werror", "-O2"], []),
                            caminho, pasta)


def rodar_javascript(caminho, pasta):
    return subprocess.run(["node", caminho], capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=pasta)


# O Java pede o javac (um JDK), como no testes_estudo.py: rodar "java Arquivo.java" direto precisa do Java 11
# ou mais novo (e o "record" dos programas, do 16). No Windows é comum ter só o java de um Java 8 antigo (sem
# javac), que não sabe rodar um .java e dava "não foi possível localizar nem carregar a classe principal"
LINGUAGENS = [("python", [], rodar_python), ("java", ["javac", "java"], rodar_java), ("c", ["gcc"], rodar_c),
              ("cpp", ["g++"], rodar_cpp), ("javascript", ["node"], rodar_javascript)]


def dados_sorteados(sorteio, algoritmo, so_inteiros, sem_arestas=False):
    vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo_sorteado(
        sorteio, algoritmo, so_inteiros=so_inteiros)
    if sem_arestas:
        arestas = []
    if inicio is None:
        inicio = sorted(vertices)[0]
    return {"nome": "Teste " + algoritmo, "vertices": vertices, "arestas": arestas, "ordenar": ordenar,
            "inicio": inicio, "direcionado": direcionado, "algoritmo": algoritmo, "destino": destino,
            "heuristica": heuristica, "limite": limite}


# Pesos com quartos (0,25, 2,75...): no double eles são exatos, então o Java, o C, o C++ e o JavaScript
# têm que escrever exatamente os mesmos decimais que o Python (que usa Decimal)
def com_quartos(dados, sorteio):
    arestas = []
    for origem, destino, nome, peso in dados["arestas"]:
        if peso is not None:
            peso = peso + Decimal(sorteio.randint(0, 3)) / 4
        arestas.append((origem, destino, nome, peso))
    novos = dict(dados)
    novos["arestas"] = arestas
    return novos


# Um caminho de 12 vértices com o maior peso que o BoscoGraph aceita (quase 1 milhão, com quartos): as
# distâncias passam de 10 milhões, onde o Java escreveria 1.0999991E7 sem cuidado (e não 10999991,75)
def caminho_comprido(algoritmo):
    vertices = [f"V{numero:02d}" for numero in range(1, 13)]
    arestas = []
    for posicao in range(len(vertices) - 1):
        arestas.append((vertices[posicao], vertices[posicao + 1], "", Decimal("999999.25")))
    return {"nome": "Caminho comprido", "vertices": vertices, "arestas": arestas, "ordenar": True,
            "inicio": vertices[0], "direcionado": not algoritmos.algoritmo(algoritmo).get("so_nao_orientado"),
            "algoritmo": algoritmo, "destino": vertices[-1],
            "heuristica": {vertice: Decimal(0) for vertice in vertices}, "limite": None}


def conferir_codigo_fonte(por_busca):
    sorteio = random.Random(1414)
    disponiveis = []
    puladas = []
    for chave, programas, funcao in LINGUAGENS:
        if all(tem_programa(programa) for programa in programas):
            disponiveis.append((chave, funcao))
        else:
            puladas.append(chave)
    tarefas = []
    with tempfile.TemporaryDirectory() as pasta:
        for algoritmo in CHAVES:
            casos = []
            for vez in range(por_busca):
                casos.append(dados_sorteados(sorteio, algoritmo, so_inteiros=True))
            casos.append(dados_sorteados(sorteio, algoritmo, so_inteiros=True, sem_arestas=True))
            casos.append(com_quartos(dados_sorteados(sorteio, algoritmo, so_inteiros=True), sorteio))
            if algoritmos.algoritmo(algoritmo)["usa_pesos"] == "sim":
                casos.append(caminho_comprido(algoritmo))
            for numero in range(len(casos)):
                dados = casos[numero]
                for chave, funcao in disponiveis:
                    extensao = codigo_fonte.LINGUAGENS[chave]["extensao"]
                    caminho = os.path.join(pasta, f"{algoritmo}_{numero}_{chave}{extensao}")
                    texto = codigo_fonte.programa(chave, dados, os.path.basename(caminho))
                    Path(caminho).write_text(texto, encoding="utf-8")
                    tarefas.append((caminho, chave, funcao, texto))
                # O pseudocódigo é texto: tem o pseudocódigo, o grafo e o resultado
                texto = codigo_fonte.programa("pseudocodigo", dados, "busca.txt")
                assert "PSEUDOCÓDIGO" in texto and "O GRAFO" in texto and "O RESULTADO" in texto
            # Pesos decimais: o Python de estudo usa Decimal (exato, como o BoscoGraph)
            dados = dados_sorteados(sorteio, algoritmo, so_inteiros=False)
            caminho = os.path.join(pasta, f"{algoritmo}_decimal_python.py")
            texto = codigo_fonte.programa("python", dados, os.path.basename(caminho))
            Path(caminho).write_text(texto, encoding="utf-8")
            tarefas.append((caminho, "python", rodar_python, texto))

        def executar(tarefa):
            caminho, chave, funcao, texto = tarefa
            resultado = funcao(caminho, pasta)
            assert resultado.returncode == 0, (caminho, resultado.stderr[-2000:])
            obtida = resultado.stdout.replace("\r\n", "\n").rstrip("\n").split("\n")
            comentario = codigo_fonte.LINGUAGENS[chave]["comentario"]
            esperada = saida_do_comentario(texto, comentario)
            assert esperada and obtida == esperada, (caminho, obtida[:5], esperada[:5])
            return chave

        # Vários de uma vez (compilar demora): cada um num processo separado
        with ThreadPoolExecutor(max_workers=max(2, min(8, os.cpu_count() or 2))) as executor:
            feitos = list(executor.map(executar, tarefas))
    quantos = {}
    for chave in feitos:
        quantos[chave] = quantos.get(chave, 0) + 1
    resumo = ", ".join(f"{chave} {quantos[chave]}" for chave in quantos)
    texto = f"14b. Código-fonte: {len(feitos)} programas rodaram e escreveram a saída esperada ({resumo})"
    if puladas:
        texto += f"; puladas (sem o compilador aqui): {', '.join(puladas)}"
    print(texto)


# ----------------------------------------------------------------------
# 14c. Figuras: geometria, SVG, PNG e PDF
# ----------------------------------------------------------------------

def figura_de_exemplo():
    formas = [
        {"tipo": "retangulo", "caixa": (10, 10, 110, 60), "preenchimento": (255, 0, 0), "contorno": None,
         "espessura": 1, "tracejado": None},
        {"tipo": "elipse", "caixa": (150, 20, 250, 120), "preenchimento": (0, 0, 255), "contorno": (0, 0, 0),
         "espessura": 2, "tracejado": (4, 3)},
        {"tipo": "linha", "pontos": [(20, 200), (150, 140), (280, 200)], "cor": (0, 128, 0), "espessura": 3,
         "tracejado": None, "suave": True, "ponta": "fim", "forma_da_ponta": (8, 10, 3)},
        {"tipo": "poligono", "pontos": [(300, 20), (380, 20), (340, 90)], "preenchimento": (255, 200, 0),
         "contorno": (0, 0, 0), "espessura": 1, "tracejado": None},
        {"tipo": "texto", "x": 200, "base": 240, "texto": "A <&> ação π ∞", "tamanho": 14, "negrito": True,
         "italico": False, "mono": False, "cor": (20, 20, 20), "alinhamento": "centro"},
    ]
    return {"largura": 400, "altura": 260, "fundo": (255, 255, 255), "formas": formas}


def conferir_geometria():
    # A ponta de seta como o Tk (ConfigureArrows), numa linha horizontal de espessura 2 e forma (8, 10, 3):
    #   d3 = 3 + 1 + 0,001; fração = 1/d3; recuo = fração·d2 + d1·(1 − fração)/2
    pontos, poligonos = geometria.aplicar_pontas([(0, 0), (100, 0)], "fim", (8, 10, 3), 2)
    d1, d2, d3 = 8.001, 10.001, 4.001
    fracao = 1 / d3
    recuo = fracao * d2 + d1 * (1 - fracao) / 2
    assert abs(pontos[-1][0] - (100 - recuo)) < 1e-9 and pontos[-1][1] == 0
    ponta, asa_1, pescoco_1, pescoco_2, asa_2 = poligonos[0]
    assert ponta == (100, 0)
    assert abs(asa_1[0] - (100 - d2)) < 1e-9 and abs(asa_1[1] + d3) < 1e-9          # a asa de cima (y para cima)
    assert abs(asa_2[0] - (100 - d2)) < 1e-9 and abs(asa_2[1] - d3) < 1e-9
    # A curva suave de 3 pontos é a quadrática; no meio (t = 0,5) passa por P0/4 + P1/2 + P2/4
    inicio, cubicas = geometria.cubicas_da_curva([(0, 0), (50, 100), (100, 0)])
    c1, c2, fim = cubicas[0]
    meio = geometria.ponto_da_cubica(inicio, c1, c2, fim, 0.5)
    assert abs(meio[0] - 50) < 1e-9 and abs(meio[1] - 50) < 1e-9
    amostra = geometria.pontos_da_linha([(0, 0), (50, 100), (100, 0)], True)
    assert amostra[0] == (0, 0) and abs(amostra[-1][0] - 100) < 1e-9
    # O tracejado (5, 4) numa reta de 100: traços de 5, espaços de 4 -> 12 traços (o último cortado)
    tracos = geometria.tracejar([(0, 0), (100, 0)], (5, 4))
    comprimentos = [math.hypot(traco[-1][0] - traco[0][0], traco[-1][1] - traco[0][1]) for traco in tracos]
    assert len(tracos) == 12 and all(abs(c - 5) < 1e-9 for c in comprimentos[:-1]) and abs(comprimentos[-1] - 1) < 1e-9
    assert abs(tracos[1][0][0] - 9) < 1e-9                  # o segundo traço começa depois de 5 + 4
    # Num caminho com curvas, o tracejado continua de um segmento para o outro
    tracos = geometria.tracejar([(0, 0), (3, 0), (3, 3), (6, 3)], (2, 1))
    total = sum(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(traco, traco[1:])) for traco in tracos)
    assert abs(total - 6) < 1e-9                             # 9 de caminho: 3 períodos de 2 traço + 1 espaço
    # A elipse amostrada fica sobre a elipse
    for x, y in geometria.pontos_da_elipse(0, 0, 200, 100, 36):
        assert abs(((x - 100) / 100) ** 2 + ((y - 50) / 50) ** 2 - 1) < 1e-9


def conferir_figuras():
    conferir_geometria()
    figura = figura_de_exemplo()
    texto = figuras.para_svg(figura)
    raiz = arvore_xml.fromstring(texto.encode("utf-8"))
    nomes = [elemento.tag.split("}")[1] for elemento in raiz.iter()]
    assert nomes.count("rect") == 2 and "ellipse" in nomes and "path" in nomes and "text" in nomes
    assert nomes.count("polygon") == 2                      # o triângulo e a ponta da seta
    textos = [elemento.text for elemento in raiz.iter() if elemento.tag.endswith("text")]
    assert textos == ["A <&> ação π ∞"]                     # o XML devolve o texto original
    assert 'stroke-dasharray="4 3"' in texto
    pillow = figuras.tem_pillow()
    with tempfile.TemporaryDirectory() as pasta:
        if pillow:
            from PIL import Image
            caminho = os.path.join(pasta, "figura.png")
            figuras.salvar_png(figura, caminho, escala=1, amostragem=3)
            with Image.open(caminho) as imagem:
                assert imagem.size == (400, 260)
                rgb = imagem.convert("RGB")
                assert rgb.getpixel((60, 35)) == (255, 0, 0)           # dentro do retângulo vermelho
                assert rgb.getpixel((200, 70))[2] > 200                # dentro da elipse azul
                assert rgb.getpixel((390, 250)) == (255, 255, 255)     # o fundo
        documento = pdf.DocumentoPdf()
        pagina = documento.nova_pagina()
        altura = figuras.desenhar_no_pdf(pagina, figura, 50, 50, 400, 260)
        assert abs(altura - 260) < 1e-9
        dados = documento.para_bytes()
        try:
            import pymupdf
        except ImportError:
            pymupdf = None
        if pymupdf is not None:
            lido = pymupdf.open(stream=dados, filetype="pdf")[0]
            assert "A <&> ação π ∞" in lido.get_text()
    # Recortar: a figura encolhe para a caixa das formas (com a margem)
    recortada = figuras.recortar(figura, margem=5)
    assert recortada["largura"] < figura["largura"] or recortada["altura"] < figura["altura"]
    print("14c. Figuras: ponta de seta, curva suave e tracejado iguais ao Tkinter; SVG válido; "
          + ("PNG com as cores certas; " if pillow else "PNG pulado (sem a Pillow); ")
          + "PDF com o texto")


# ----------------------------------------------------------------------
# 14d. O relatório
# ----------------------------------------------------------------------

def conferir_relatorio():
    linhas_da_tabela = [[str(numero), f"Vértice {numero}", "texto comprido " * (numero % 7)] for numero in range(260)]
    colunas = [f"c{numero}" for numero in range(40)]
    celulas = {}
    for i in range(5):
        for j in range(40):
            celulas[(i, j)] = str((i * j) % 3 - 1)
    codigo = ["def busca(adj):", "    for u in adj:", "        if u:", "            return u", "x" * 300]
    conteudo = {"titulo": "Relatório de teste", "blocos": [
        {"tipo": "capa", "titulo": "Relatório de teste", "subtitulo": "gerado nos testes",
         "fatos": [("Grafo", "orientado"), ("Busca", "Dijkstra")], "figura": figura_de_exemplo(),
         "legenda": "O grafo"},
        {"tipo": "secao", "titulo": "Tabela comprida", "cor": (40, 110, 220), "descricao": "Muitas linhas."},
        {"tipo": "tabela", "colunas": ["Número", "Nome", "Observação"], "linhas": linhas_da_tabela},
        {"tipo": "secao", "titulo": "Matriz larga"},
        {"tipo": "grade", "matriz": {"linhas": ["A", "B", "C", "D", "E"], "colunas": colunas, "celulas": celulas}},
        {"tipo": "numerada", "itens": [f"passo {numero}" for numero in range(1, 30)]},
        {"tipo": "paragrafo", "texto": "Um aviso.", "estilo": "aviso"},
        {"tipo": "quebra"},
        {"tipo": "codigo", "titulo": "Código", "linhas": codigo},
    ]}
    documento = relatorio.gerar(conteudo)
    total = len(documento.paginas)
    assert total >= 6, total
    dados = documento.para_bytes()
    try:
        import pymupdf
    except ImportError:
        print(f"14d. Relatório: {total} páginas geradas (conferência do texto pulada: sem o PyMuPDF)")
        return
    lido = pymupdf.open(stream=dados, filetype="pdf")
    paginas_com_a_tabela = 0
    linhas_vistas = set()
    for numero in range(total):
        texto = lido[numero].get_text()
        assert f"página {numero + 1} de {total}" in texto, numero          # o rodapé em todas
        if "Vértice 1" in texto or "Vértice 2" in texto:
            paginas_com_a_tabela += 1
            assert "Número" in texto and "Observação" in texto, numero      # o cabeçalho repetido
        for linha in range(260):
            if f"Vértice {linha}\n" in texto:
                linhas_vistas.add(linha)
    assert paginas_com_a_tabela >= 3 and len(linhas_vistas) == 260, (paginas_com_a_tabela, len(linhas_vistas))
    tudo = "".join(pagina.get_text() for pagina in lido)
    assert "colunas 1 a" in tudo and "de 40" in tudo                       # a matriz larga em pedaços
    # O código mantém a indentação: o "return" começa mais à direita que o "if", que começa mais à
    # direita que o "for" (o search_for acha onde o texto começa de fato, depois dos espaços)
    ultima = lido[total - 1]
    posicoes = {}
    for palavra in ("def busca", "for u in adj", "if u:", "return u"):
        achados = ultima.search_for(palavra)
        assert achados, palavra
        posicoes[palavra] = achados[0].x0
    assert posicoes["def busca"] < posicoes["for u in adj"] < posicoes["if u:"] < posicoes["return u"], posicoes
    passo = posicoes["if u:"] - posicoes["for u in adj"]
    assert abs((posicoes["return u"] - posicoes["if u:"]) - passo) < 0.5       # 4 espaços cada nível
    print(f"14d. Relatório: {total} páginas; a tabela de 260 linhas continua em {paginas_com_a_tabela} páginas com o "
          f"cabeçalho, a matriz de 40 colunas sai em pedaços, o código mantém a indentação e todas têm o rodapé")


# ----------------------------------------------------------------------
# 14e. A prévia e os recentes do .bosco
# ----------------------------------------------------------------------

def conferir_detalhes_e_recentes():
    import caminhos
    pasta_dos_modelos = modelos.PASTA_DOS_MODELOS
    with tempfile.TemporaryDirectory() as pasta:
        # A data e o programa que salvou (a prévia da tela do .bosco mostra os dois)
        caminho = os.path.join(pasta, "prova.bosco")
        grafo = modelos.novo_grafo(["A", "B"], [("A", "B", "e1", None)])
        bosco.salvar(caminho, grafo, "Prova", {"parte": "passo", "partes": {}, "exibir": {}})
        detalhes = bosco.ler_com_detalhes(caminho)
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", detalhes["salvo_em"]), detalhes["salvo_em"]
        assert detalhes["programa"] == f"BoscoGraph {caminhos.VERSAO}" and detalhes["nome"] == "Prova"
        assert detalhes["tela"]["parte"] == "passo" and detalhes["grafo"]["vertices"] == ["A", "B"]
        # Editados à mão: o que não é texto vira "" (nunca um erro)
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        dados["salvo_em"] = 123
        del dados["programa"]
        Path(caminho).write_text(json.dumps(dados), encoding="utf-8")
        detalhes = bosco.ler_com_detalhes(caminho)
        assert detalhes["salvo_em"] == "" and detalhes["programa"] == ""

        # Os recentes, numa pasta de dados de mentira
        modelos.PASTA_DOS_MODELOS = Path(pasta) / "dados" / "modelos"
        try:
            assert bosco.listar_recentes() == []                 # o arquivo ainda não existe
            arquivos = [os.path.join(pasta, f"grafo{numero}.bosco") for numero in range(8)]
            bosco.lembrar_recente(arquivos[0])
            bosco.lembrar_recente(arquivos[1])
            bosco.lembrar_recente(arquivos[0])                  # de novo: volta para cima, sem repetir
            assert bosco.listar_recentes() == [arquivos[0], arquivos[1]]
            for arquivo in arquivos:
                bosco.lembrar_recente(arquivo)
            recentes = bosco.listar_recentes()
            assert recentes == list(reversed(arquivos))[:bosco.MAXIMO_DE_RECENTES], recentes
            bosco.esquecer_recente(arquivos[7])
            assert arquivos[7] not in bosco.listar_recentes() and len(bosco.listar_recentes()) == 5
            # Linhas em branco e repetidas (o arquivo editado à mão) não aparecem
            texto = "\n\n" + arquivos[3] + "\n" + arquivos[3] + "\n   \n" + arquivos[2] + "\n"
            bosco.arquivo_dos_recentes().write_text(texto, encoding="utf-8")
            assert bosco.listar_recentes() == [arquivos[3], arquivos[2]]
            # O "arquivo" dos recentes é uma pasta (não dá para ler): a lista fica vazia, sem erro
            bosco.arquivo_dos_recentes().unlink()
            bosco.arquivo_dos_recentes().mkdir()
            assert bosco.listar_recentes() == []
            bosco.lembrar_recente(arquivos[0])                  # gravar também falha em silêncio
            # A pasta de dados não pode ser criada (no lugar dela há um arquivo): também sem erro
            bloqueio = Path(pasta) / "bloqueio"
            bloqueio.write_text("x", encoding="utf-8")
            modelos.PASTA_DOS_MODELOS = bloqueio / "modelos"
            bosco.lembrar_recente(arquivos[0])
            assert bosco.listar_recentes() == []
        finally:
            modelos.PASTA_DOS_MODELOS = pasta_dos_modelos
    print("14e. Prévia do .bosco (data e programa que salvou) e os abertos recentemente: o mais novo em cima, "
          f"sem repetir, no máximo {bosco.MAXIMO_DE_RECENTES}, sem erro com arquivo faltando ou sem permissão")


def rodar():
    conferir_bosco(150)
    conferir_detalhes_e_recentes()
    conferir_codigo_fonte(2)
    conferir_figuras()
    conferir_relatorio()


if __name__ == "__main__":
    rodar()
    print("Todos os testes das exportações passaram.")
