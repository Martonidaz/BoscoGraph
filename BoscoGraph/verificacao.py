'''
    Autoteste do programa: confere, sem abrir janela, se tudo o que o BoscoGraph precisa está no lugar.

        python boscograph.py --verificar                  (pelo código-fonte)
        BoscoGraph.exe --verificar relatorio.txt          (no programa instalado)

    Serve principalmente para o executável: o PyInstaller junta só o que foi pedido no BoscoGraph.spec,
    e um arquivo esquecido (um .py que o painel de código mostra, o ícone, os exemplos) só daria erro
    com o programa já aberto, na frente do usuário. O construir.py roda esta verificação no executável
    recém-gerado, antes de montar o instalador.

    O executável não tem terminal (é um programa de janela), então o resultado também pode ir para um
    arquivo. A saída do programa diz se passou: 0 = tudo certo, 1 = alguma coisa falhou.
'''

import sys
import tempfile
from pathlib import Path

import caminhos
from entrada import contar


def verificar():
    resultados = []                     # (deu certo?, texto)

    def anotar(certo, texto):
        resultados.append((certo, texto))

    # 1. Os arquivos de código que o painel "Código" mostra, com todos os trechos destacados
    try:
        from visual.codigo import localizar_trechos
        from visual import perfis
        arquivos = set()
        for chave in perfis.PERFIS:
            linhas_do_arquivo, linha_do_trecho = localizar_trechos(perfis.PERFIS[chave]["trechos"])
            arquivos.update(linhas_do_arquivo)
        anotar(True, f"Painel de código: {len(arquivos)} arquivos .py e todos os trechos encontrados")
    except Exception as erro:
        anotar(False, f"Painel de código: {erro}")

    # 1b. O código de estudo (seis linguagens, com os mesmos rótulos) e o linha a linha: o Python de
    #     estudo de cada busca roda com o rastro, e cada passo da busca acha a linha dele
    try:
        import algoritmos
        import estudo
        from decimal import Decimal
        from boscograph import montar_passos
        from estudo import rastreador
        from visual import perfis
        vertices = ["A", "B", "C", "D"]
        arestas = [("A", "B", "", Decimal(2)), ("A", "C", "", Decimal(5)), ("B", "C", "", Decimal(1)),
                   ("C", "D", "", Decimal(3))]
        heuristica = {"A": Decimal(4), "B": Decimal(3), "C": Decimal(2), "D": Decimal(0)}
        arquivos = 0
        linhas = 0
        for algoritmo in estudo.ARQUIVOS:
            rotulos = set(estudo.carregar(algoritmo, "python")["linhas_do_rotulo"])
            for informacoes in estudo.LINGUAGENS:
                carregado = estudo.carregar(algoritmo, informacoes["chave"])
                assert set(carregado["linhas_do_rotulo"]) == rotulos, f"rótulos de {carregado['caminho'].name}"
                arquivos += 1
            orientado = not algoritmos.algoritmo(algoritmo).get("so_nao_orientado")     # Prim e Kruskal: não orientado
            passos = montar_passos(vertices, arestas, True, "A", orientado, algoritmo, "D", heuristica, limite=3)
            rastro = rastreador.rastrear(algoritmo, vertices, arestas, True, "A", orientado, "D", heuristica, limite=3)
            rastreador.sincronizar(passos, rastro["passos_de_linha"], rastro["arquivo"]["rotulo_da_linha"],
                                   perfis.chave_do_trecho)
            linhas += len(rastro["passos_de_linha"])
        anotar(True, f"Código de estudo: {arquivos} arquivos ({len(estudo.ARQUIVOS)} buscas em "
                     f"{len(estudo.LINGUAGENS)} linguagens); linha a linha: {linhas} linhas executadas")
    except Exception as erro:
        anotar(False, f"Código de estudo: {erro}")

    # 2. O ícone da janela
    icone = caminhos.pasta_dos_recursos() / "visual" / "icone.png"
    anotar(icone.is_file(), f"Ícone da janela: {icone}")

    # 3. Os modelos de exemplo que vêm com o programa (cada um precisa abrir sem erro)
    try:
        import json
        from decimal import Decimal
        import modelos
        exemplos = sorted(caminhos.pasta_dos_exemplos().glob("*.json"))
        for arquivo in exemplos:
            dados = json.loads(arquivo.read_text(encoding="utf-8"), parse_float=Decimal)
            modelos.grafo_dos_dados(dados, arquivo.stem)
        anotar(len(exemplos) > 0, f"Modelos de exemplo: {len(exemplos)} encontrados e abertos")
    except Exception as erro:
        anotar(False, f"Modelos de exemplo: {erro}")

    # 4. A pasta dos modelos do usuário: precisa existir e aceitar gravação
    #    (instalado em "Arquivos de Programas", é a pasta no %APPDATA%, nunca a do programa)
    try:
        import modelos
        pasta = caminhos.pasta_dos_modelos()
        pasta.mkdir(parents=True, exist_ok=True)
        teste = pasta / "verificacao.tmp"
        modelos.gravar_texto(teste, "teste")
        certo = teste.read_text(encoding="utf-8") == "teste"
        teste.unlink()
        anotar(certo, f"Pasta dos modelos (gravação): {pasta}")
    except Exception as erro:
        anotar(False, f"Pasta dos modelos (gravação): {erro}")

    # 5. Todas as buscas, do começo ao fim, num grafo com pesos
    try:
        from decimal import Decimal
        import algoritmos
        from boscograph import montar_passos
        vertices = ["A", "B", "C", "D"]
        arestas = [("A", "B", "", Decimal(2)), ("A", "C", "", Decimal(5)), ("B", "C", "", Decimal(1)),
                   ("C", "D", "", Decimal(3))]
        heuristica = {"A": Decimal(4), "B": Decimal(3), "C": Decimal(2), "D": Decimal(0)}
        for algoritmo in algoritmos.ALGORITMOS:
            passos = montar_passos(vertices, arestas, True, "A", not algoritmo.get("so_nao_orientado"), algoritmo["chave"],
                                   "D", heuristica, limite=3)
            assert passos[-1]["tipo"].startswith("resultado") or passos[-1]["tipo"].startswith("tipo"), \
                algoritmo["chave"]
        anotar(True, f"Buscas: as {len(algoritmos.ALGORITMOS)} rodaram do começo ao fim")
    except Exception as erro:
        anotar(False, f"Buscas: {erro}")

    # 5b. As exportações que não precisam da janela: um relatório em PDF, um arquivo .bosco (gravado e lido
    #     de volta) e o código-fonte nas seis linguagens (o Python gerado roda aqui mesmo e tem que escrever
    #     a saída esperada que vai no fim do arquivo)
    try:
        anotar(True, conferir_exportacoes())
    except Exception as erro:
        anotar(False, f"Exportações: {erro}")

    # 6. Importação de PDF e de imagem: opcionais (o programa funciona sem elas). Se a biblioteca está
    #    no pacote, um grafo pequeno (A -> B) é desenhado na hora e importado de volta: assim a
    #    verificação pega também uma biblioteca que entrou no pacote faltando algum pedaço.
    extras = []
    for modulo, nome, conferir in (("pymupdf", "PDF (PyMuPDF)", conferir_pdf),
                                   ("cv2", "imagem (OpenCV)", conferir_imagem)):
        try:
            __import__(modulo)
        except ImportError:
            extras.append(f"{nome}: não está no pacote")
            continue
        try:
            conferir()
            extras.append(f"{nome}: importou um grafo de teste")
        except Exception as erro:
            anotar(False, f"Importação de {nome}: {erro}")
    try:
        from importacao.imagem import carregar_ocr
        extras.append("leitor de texto (Tesseract): " + ("sim" if carregar_ocr() else "não"))
    except Exception:
        extras.append("leitor de texto (Tesseract): não")
    anotar(True, "Importação opcional: " + "; ".join(extras))
    return resultados


def conferir_exportacoes():
    import contextlib
    import io
    from decimal import Decimal
    import modelos
    from exportacao import bosco, codigo_fonte, relatorio
    from exportacao import figura as figuras
    vertices = ["A", "B", "C", "D"]
    arestas = [("A", "B", "", Decimal(2)), ("A", "C", "", Decimal("2.5")), ("B", "C", "", Decimal(1)),
               ("C", "D", "", Decimal(3))]
    # O relatório (sem o desenho, que precisa da janela)
    blocos = [{"tipo": "capa", "titulo": "Verificação", "fatos": [("Grafo", "A, B, C, D")]},
              {"tipo": "secao", "titulo": "Tabela"},
              {"tipo": "tabela", "colunas": ["u", "v"], "linhas": [[u, v] for u, v, nome, peso in arestas]},
              {"tipo": "codigo", "linhas": ["for u in adj:", "    print(u)"]}]
    documento = relatorio.gerar({"titulo": "Verificação", "blocos": blocos})
    dados_do_pdf = documento.para_bytes()
    assert dados_do_pdf.startswith(b"%PDF") and len(documento.paginas) == 1
    # O .bosco, gravado e lido de volta
    grafo = modelos.novo_grafo(vertices, arestas, True, "A", True, "dijkstra", "D")
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "teste.bosco"
        bosco.salvar(caminho, grafo, "Verificação", {"parte": "passo", "partes": {"passo": {"posicao": 3}}})
        lido, nome, tela = bosco.ler(caminho)
    assert lido["arestas"] == arestas and tela["partes"]["passo"]["posicao"] == 3
    # O código-fonte: as seis linguagens são geradas; o Python roda aqui dentro
    dados = {"nome": "Verificação", "vertices": vertices, "arestas": arestas, "ordenar": True, "inicio": "A",
             "direcionado": True, "algoritmo": "dijkstra", "destino": "D", "heuristica": {}, "limite": None}
    for chave in codigo_fonte.LINGUAGENS:
        texto = codigo_fonte.programa(chave, dados, "busca" + codigo_fonte.LINGUAGENS[chave]["extensao"])
        assert "Saída esperada" in texto or chave == "pseudocodigo", chave
        if chave == "python":
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                exec(compile(texto, "busca.py", "exec"), {"__name__": "__main__"})
            esperada = [linha[6:] for linha in texto.split("\n") if linha.startswith("#     ")]
            assert saida.getvalue().rstrip("\n").split("\n") == esperada[-len(vertices):], saida.getvalue()
    pillow = "PNG com a Pillow" if figuras.tem_pillow() else "PNG: a Pillow não está no pacote (SVG e PDF funcionam)"
    return (f"Exportações: relatório em PDF ({len(dados_do_pdf) // 1024 + 1} KB), .bosco lido de volta igual, "
            f"código-fonte em {len(codigo_fonte.LINGUAGENS)} linguagens (o Python gerado rodou certo); {pillow}")


# Um grafo A -> B desenhado num PDF (dois círculos, uma linha e a ponta da seta) e importado de volta
def conferir_pdf():
    import pymupdf
    import importacao
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "teste.pdf"
        documento = pymupdf.open()
        pagina = documento.new_page(width=300, height=150)
        pagina.draw_circle((60, 75), 25)
        pagina.draw_circle((240, 75), 25)
        pagina.draw_line((85, 75), (203, 75))
        pagina.draw_polyline([(203, 69), (215, 75), (203, 81), (203, 69)], fill=(0, 0, 0), closePath=True)
        pagina.insert_text((55, 80), "A", fontsize=14)
        pagina.insert_text((235, 80), "B", fontsize=14)
        documento.save(str(caminho))
        documento.close()
        importado = importacao.importar_arquivo(caminho)
    assert len(importado["vertices"]) == 2 and len(importado["arestas"]) == 1, importado["arestas"]


# O mesmo grafo A -> B desenhado numa imagem (sem conferir os nomes: o Tesseract é opcional)
def conferir_imagem():
    import cv2
    import numpy
    import importacao
    figura = numpy.full((200, 420, 3), 255, dtype=numpy.uint8)
    cv2.circle(figura, (80, 100), 40, (0, 0, 0), 2)
    cv2.circle(figura, (340, 100), 40, (0, 0, 0), 2)
    cv2.line(figura, (122, 100), (280, 100), (0, 0, 0), 2)
    cv2.fillPoly(figura, [numpy.array([[298, 100], [276, 89], [276, 111]], dtype=numpy.int32)], (0, 0, 0))
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "teste.png"
        cv2.imwrite(str(caminho), figura)
        importado = importacao.importar_arquivo(caminho)
    assert len(importado["vertices"]) == 2 and len(importado["arestas"]) == 1, importado["arestas"]
    assert importado["direcionado"] is True, "a seta não foi reconhecida"


# Roda a verificação, mostra no terminal (se houver um) e grava no arquivo pedido.
# Devolve o código de saída do programa: 0 = tudo certo, 1 = falhou alguma coisa.
def rodar(arquivo_do_relatorio=None):
    resultados = verificar()
    linhas = [f"{caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO} - verificação"
              f" ({'executável' if caminhos.esta_empacotado() else 'código-fonte'})"]
    falhas = 0
    for certo, texto in resultados:
        linhas.append(("[ok]      " if certo else "[FALHOU]  ") + texto)
        if not certo:
            falhas += 1
    if falhas == 0:
        linhas.append("Tudo certo.")
    else:
        linhas.append(contar(falhas, "verificação falhou.", "verificações falharam."))
    relatorio = "\n".join(linhas)
    if sys.stdout is not None:          # o executável de janela não tem terminal: sys.stdout é None
        print(relatorio)
    if arquivo_do_relatorio:
        with open(arquivo_do_relatorio, "w", encoding="utf-8") as arquivo:
            arquivo.write(relatorio + "\n")
    return 0 if falhas == 0 else 1
