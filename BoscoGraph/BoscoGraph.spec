# -*- mode: python ; coding: utf-8 -*-
#
# Receita do PyInstaller para gerar o executável do BoscoGraph.
# Uso (o construir.py faz isto e mais): python -m PyInstaller BoscoGraph.spec --noconfirm --clean
#
# O PyInstaller lê o boscograph.py, segue todos os "import" e junta numa pasta (dist/BoscoGraph):
# o Python, as bibliotecas e o código já compilado (.pyc). Só que ele junta o CÓDIGO COMPILADO, e o
# painel "Código" do BoscoGraph mostra o TEXTO dos arquivos .py. Por isso os .py que o painel lê vão
# como "datas" (arquivos de dados, copiados como estão), junto com o ícone e os modelos de exemplo.
# O código de estudo (estudo/, em seis linguagens) também vai como dado: o painel mostra o texto, e o
# modo linha a linha lê o Python de estudo e o executa (veja estudo/rastreador.py). Os programas de
# estudo/conferencia/ são só dos testes e ficam de fora.
# No executável, essa pasta interna é a sys._MEIPASS (veja caminhos.pasta_dos_recursos).
#
# "onedir" (uma pasta) e não "onefile" (um .exe só): o onefile se descompacta numa pasta temporária a
# cada vez que abre (fica lento para abrir) e é o formato que mais leva alarme falso de antivírus.
# Quem distribui é o instalador do Inno Setup, então a pasta não incomoda ninguém.

from pathlib import Path

PASTA = Path(SPECPATH)          # SPECPATH: a pasta deste arquivo (o PyInstaller define)

datas = [
    (str(PASTA / "boscograph.py"), "."),
    (str(PASTA / "classes" / "*.py"), "classes"),
    (str(PASTA / "visual" / "icone.png"), "visual"),
    (str(PASTA / "modelos" / "*.json"), "modelos"),
]
for linguagem in ("pseudocodigo", "python", "java", "c", "cpp", "javascript"):
    datas.append((str(PASTA / "estudo" / linguagem / "*"), "estudo/" + linguagem))

analise = Analysis(
    [str(PASTA / "boscograph.py")],
    pathex=[str(PASTA)],
    datas=datas,
    # Importados só dentro de funções e com try/except (são opcionais). O PyInstaller costuma achar
    # sozinho; listar aqui garante que entram quando estiverem instalados na máquina que gera o .exe.
    hiddenimports=["pymupdf", "cv2", "numpy", "pytesseract", "PIL"],
    # Bibliotecas grandes que o BoscoGraph não usa, mas que alguma dependência pode puxar
    excludes=["matplotlib", "scipy", "pandas", "IPython", "pytest", "setuptools"],
    noarchive=False,
)

pacote = PYZ(analise.pure)

executavel = EXE(
    pacote,
    analise.scripts,
    [],
    exclude_binaries=True,
    name="BoscoGraph",
    console=False,                                      # programa de janela: sem a tela preta do terminal
    icon=str(PASTA / "instalador" / "boscograph.ico"),
    upx=False,                                          # UPX compacta, mas também atrai antivírus
)

pasta_final = COLLECT(
    executavel,
    analise.binaries,
    analise.datas,
    name="BoscoGraph",
    upx=False,
)
