'''
    Gera o executável e o instalador do BoscoGraph, conferindo cada etapa.

        python construir.py              tudo: testes, ícone, executável, autoteste e instalador
        python construir.py --sem-testes pula os testes (mais rápido, para experimentar)

    As etapas, e por que cada uma existe:
      1. Testes (testes.py): não adianta empacotar um programa com defeito.
      2. Ícone (instalador/boscograph.ico): o Windows quer o desenho em vários tamanhos. E as imagens
         das telas do instalador (instalador/assistente_*.bmp), nas cores da paleta.
      3. Executável (PyInstaller, pela receita BoscoGraph.spec): gera a pasta dist/BoscoGraph.
      4. Autoteste: roda "BoscoGraph --verificar" no executável recém-gerado, com a pasta de dados
         apontando para uma pasta temporária (para não mexer nos modelos de quem está gerando).
         Se faltou algum arquivo no pacote (um .py que o painel de código mostra, o ícone, os
         exemplos), o erro aparece aqui, e não na mão do usuário.
      5. Instalador (Inno Setup, pela receita instalador/BoscoGraph.iss): só no Windows, e só se o
         Inno Setup estiver instalado. O resultado vai para instalador/saida.

    Precisa (além do que o programa usa): pip install pyinstaller pillow
'''

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import caminhos

PASTA = Path(__file__).resolve().parent
PASTA_DO_EXECUTAVEL = PASTA / "dist" / caminhos.NOME_DO_PROGRAMA
RECEITA_DO_INSTALADOR = PASTA / "instalador" / "BoscoGraph.iss"


def etapa(numero, texto):
    print(f"\n=== {numero}. {texto}", flush=True)


def falhar(texto):
    print(f"\nERRO: {texto}")
    sys.exit(1)


def rodar_testes():
    etapa(1, "Testes")
    resultado = subprocess.run([sys.executable, "testes.py"], cwd=PASTA)
    if resultado.returncode != 0:
        falhar("os testes falharam; o executável não foi gerado.")


def gerar_icone():
    etapa(2, "Ícone e imagens do instalador")
    try:
        from instalador import gerar_icone
    except ImportError as erro:
        falhar(f"não consegui gerar o ícone ({erro}). Instale a Pillow: pip install pillow")
    print(f"Ícone gerado: {gerar_icone.gerar()}")
    # As imagens das telas do instalador (com as cores da paleta), que o BoscoGraph.iss usa
    print(f"Imagens do instalador: {len(gerar_icone.gerar_imagens_do_assistente())} arquivos .bmp")


def gerar_executavel():
    etapa(3, "Executável (PyInstaller)")
    # find_spec procura o módulo sem importar: só para avisar antes, com uma mensagem clara
    if importlib.util.find_spec("PyInstaller") is None:
        falhar("o PyInstaller não está instalado: pip install pyinstaller")
    resultado = subprocess.run([sys.executable, "-m", "PyInstaller", "BoscoGraph.spec", "--noconfirm", "--clean"],
                               cwd=PASTA)
    if resultado.returncode != 0:
        falhar("o PyInstaller falhou (veja as mensagens acima).")


# O executável que o PyInstaller gerou (BoscoGraph.exe no Windows, BoscoGraph nos outros)
def caminho_do_executavel():
    nome = caminhos.NOME_DO_PROGRAMA + (".exe" if sys.platform.startswith("win") else "")
    return PASTA_DO_EXECUTAVEL / nome


def autotestar():
    etapa(4, "Autoteste do executável (--verificar)")
    executavel = caminho_do_executavel()
    if not executavel.is_file():
        falhar(f"executável não encontrado: {executavel}")
    with tempfile.TemporaryDirectory() as pasta:
        relatorio = Path(pasta) / "relatorio.txt"
        ambiente = dict(os.environ)
        ambiente[caminhos.VARIAVEL_DA_PASTA_DE_DADOS] = str(Path(pasta) / "dados")
        try:
            # A saída do próprio programa é guardada (capture_output): o relatório vem do arquivo
            resultado = subprocess.run([str(executavel), "--verificar", str(relatorio)], env=ambiente,
                                       timeout=300, capture_output=True)
        except subprocess.TimeoutExpired:
            falhar("o executável não terminou a verificação em 5 minutos.")
        except OSError as erro:
            # WinError 4551: o Controle Inteligente de Aplicativos do Windows 11 não deixa rodar um .exe sem
            # assinatura digital, e o BoscoGraph.exe acabou de ser criado aqui, sem assinatura
            if getattr(erro, "winerror", None) != 4551:
                raise
            falhar("o Windows bloqueou o BoscoGraph.exe (Controle Inteligente de Aplicativos: o programa não tem "
                   "assinatura digital). Para gerar e testar aqui, desligue em Segurança do Windows → Controle de "
                   "aplicativos e navegador → Configurações do Controle Inteligente de Aplicativos (dá para religar "
                   "depois) e rode de novo: python construir.py")
        if relatorio.is_file():
            print(relatorio.read_text(encoding="utf-8"))
        if resultado.returncode != 0:
            falhar("o executável não passou na própria verificação (veja o relatório acima).")


# O compilador do Inno Setup (ISCC.exe): no PATH ou na pasta onde o instalador dele costuma ficar
def achar_inno_setup():
    candidatos = [shutil.which("ISCC") or "", shutil.which("iscc") or ""]
    for variavel in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        base = os.environ.get(variavel)
        if base:
            candidatos.append(str(Path(base) / "Inno Setup 6" / "ISCC.exe"))
            candidatos.append(str(Path(base) / "Programs" / "Inno Setup 6" / "ISCC.exe"))
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            return candidato
    return None


def gerar_instalador():
    etapa(5, "Instalador (Inno Setup)")
    if not sys.platform.startswith("win"):
        print("O Inno Setup só roda no Windows: o executável está pronto em", PASTA_DO_EXECUTAVEL)
        return
    iscc = achar_inno_setup()
    if iscc is None:
        print("Inno Setup não encontrado. Instale (https://jrsoftware.org/isdl.php) e rode de novo,")
        print("ou abra instalador\\BoscoGraph.iss no Inno Setup e aperte F9.")
        return
    resultado = subprocess.run([iscc, f"/DVersao={caminhos.VERSAO}", str(RECEITA_DO_INSTALADOR)], cwd=PASTA)
    if resultado.returncode != 0:
        falhar("o Inno Setup falhou (veja as mensagens acima).")
    print("Instalador pronto em", PASTA / "instalador" / "saida")


if __name__ == "__main__":
    if "--sem-testes" not in sys.argv:
        rodar_testes()
    gerar_icone()
    gerar_executavel()
    autotestar()
    gerar_instalador()
    print("\nPronto.")
