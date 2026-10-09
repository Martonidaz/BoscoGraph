'''
    Caminhos: onde o BoscoGraph acha os próprios arquivos e onde ele grava os do usuário.

    São duas pastas diferentes, porque seguem regras diferentes:

    1. Recursos (só leitura): os arquivos .py que o painel "Código" mostra, o ícone e os
       modelos de exemplo que vêm com o programa.
       - Rodando pelo código-fonte (python boscograph.py): é a própria pasta do projeto.
       - No executável do PyInstaller: é a pasta interna que ele monta (sys._MEIPASS),
         para onde vão os arquivos listados como "datas" no BoscoGraph.spec.

    2. Dados (leitura e escrita): os modelos que o usuário salva.
       - Rodando pelo código-fonte: a pasta modelos/ do projeto, como sempre foi.
       - Instalado (executável): %APPDATA%\\BoscoGraph\\modelos no Windows. Instalado em
         "Arquivos de Programas", um programa comum NÃO tem permissão de gravar na própria
         pasta (só o administrador tem), por isso os dados do usuário vão para o perfil dele.
       - A variável de ambiente BOSCOGRAPH_DADOS escolhe outra pasta (útil nos testes e
         para usar o programa "portátil", num pen drive).

    Este arquivo não usa Tkinter: os testes conferem tudo sem abrir janela.
'''

import os
import re
import sys
from pathlib import Path

NOME_DO_PROGRAMA = "BoscoGraph"
VERSAO = "7.3"                      # a mesma do instalador (o construir.py passa para o Inno Setup)
VARIAVEL_DA_PASTA_DE_DADOS = "BOSCOGRAPH_DADOS"


# O PyInstaller cria o atributo sys.frozen ("congelado") no executável.
# Rodando pelo python, ele não existe e o getattr devolve o valor padrão (False).
def esta_empacotado():
    return getattr(sys, "frozen", False)


# Pasta dos recursos (só leitura). No executável, o PyInstaller guarda o caminho em sys._MEIPASS.
def pasta_dos_recursos():
    if esta_empacotado():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent      # a pasta onde está este arquivo (a do projeto)


# A pasta que cada sistema reserva para os dados dos programas, dentro do perfil do usuário:
#   Windows -> %APPDATA%                 (por exemplo C:\Users\Ana\AppData\Roaming)
#   macOS   -> ~/Library/Application Support
#   Linux   -> $XDG_DATA_HOME, ou ~/.local/share se a variável não existir
def pasta_de_dados_do_sistema():
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata)
        return Path.home() / "AppData" / "Roaming"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".local" / "share"


# Onde os modelos do usuário são gravados (as regras estão no começo do arquivo)
def pasta_dos_modelos():
    escolhida = os.environ.get(VARIAVEL_DA_PASTA_DE_DADOS, "").strip()
    if escolhida:
        return Path(escolhida) / "modelos"
    if esta_empacotado():
        return pasta_de_dados_do_sistema() / NOME_DO_PROGRAMA / "modelos"
    return pasta_dos_recursos() / "modelos"


# Os modelos de exemplo que vêm junto com o programa (só leitura).
# Na primeira vez, eles são copiados para a pasta dos modelos do usuário (veja modelos.py).
def pasta_dos_exemplos():
    return pasta_dos_recursos() / "modelos"


# Um nome de arquivo que o Windows aceita: sem \ / : * ? " < > | (viram espaço), sem espaços repetidos
# e sem ponto no fim. As exportações sugerem nomes assim ("Dijkstra - Prova 01.py").
def nome_de_arquivo(texto):
    texto = re.sub(r'[\\/:*?"<>|\n\r\t]+', " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip().rstrip(".").strip()
    return texto[:80].strip() or "grafo"
