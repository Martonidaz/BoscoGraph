'''
    O arquivo .bosco: o grafo + a busca escolhida + COMO A TELA ESTAVA, num arquivo só.
    Quem tem o BoscoGraph instalado abre o arquivo (duplo clique, "Abrir arquivo .bosco" na tela inicial
    ou "BoscoGraph.exe arquivo.bosco") e cai direto na visualização, do jeito que foi salvo: a mesma parte
    aberta, o mesmo passo, a mesma linha escolhida, os mesmos painéis minimizados, os pesos e nomes
    ligados ou não, a arrumação do desenho, o tema e o tamanho das letras.

    Por dentro é um JSON (texto) como este:
        {
          "formato": "BoscoGraph",
          "versao": 1,
          "programa": "BoscoGraph 6.0",
          "salvo_em": "2026-10-01 14:30",
          "grafo": { ...o mesmo formato dos modelos salvos (modelos.dados_do_grafo)... },
          "tela": {
            "parte": "passo",                         <- a parte aberta
            "partes": {"passo": {"posicao": 12}, ...},   <- as escolhas de cada parte
            "exibir": {"pesos": true, "nomes": true, "arrumacao": "circulo", "tema": "claro", ...}
          }
        }
    O arquivo pode ter sido editado à mão (ou estragado): tudo é conferido ao abrir. O grafo passa pela
    mesma conferência dos modelos (modelos.grafo_dos_dados); as escolhas da tela que não fazem sentido
    são simplesmente esquecidas (a parte abre do começo).

    Este arquivo não usa Tkinter.
'''

import datetime
import json
import math
import os
from decimal import Decimal
from pathlib import Path

import caminhos
import modelos

FORMATO = "BoscoGraph"
VERSAO = 1
EXTENSAO = ".bosco"
TAMANHO_MAXIMO = 20 * 1024 * 1024           # 20 MB: um .bosco de verdade tem poucos KB

# As partes da tela e o tipo de cada escolha que elas guardam (o resto do que vier é ignorado):
#   "texto"   -> um texto (nome de vértice, número da aresta como texto, um modo...)
#   "inteiro" -> um número inteiro (uma posição)
#   "logico"  -> verdadeiro ou falso
#   "marcas"  -> um dicionário {nome: verdadeiro/falso} (os painéis ligados ou minimizados)
#   "par"     -> dois valores (linha e coluna de uma célula; linguagem e número de uma linha de código)
#   "inteiros" -> uma lista de números inteiros (as arestas escolhidas)
ESCOLHAS_DAS_PARTES = {
    "vertices": {"vertice": "texto", "montagem": "logico"},
    "arestas": {"aresta": "texto", "montagem": "logico"},
    "pesos": {"aresta": "texto", "arestas": "inteiros"},
    "lista": {"vertice": "texto", "sentido": "texto", "montagem": "logico"},
    "adjacencia": {"celula": "par", "modo": "texto", "preenchendo": "logico", "preenchidas": "inteiro"},
    "incidencia": {"celula": "par", "modo": "texto", "preenchendo": "logico", "preenchidas": "inteiro"},
    "tipo": {"passo": "texto"},
    "passo": {"posicao": "inteiro", "mostrar": "marcas"},
    "linha": {"linha": "inteiro", "mostrar": "marcas", "escolhida": "par"},
    "comparar": {"modo": "texto", "posicao_passo": "inteiro", "posicao_linha": "inteiro"},
    "resultado": {"passo": "texto"},
}
# Toda parte pode guardar os painéis minimizados
for _escolhas in ESCOLHAS_DAS_PARTES.values():
    _escolhas["recolhidos"] = "marcas"

# O que o menu Exibir (e o resto da aparência) guarda
EXIBIR = {"pesos": "logico", "nomes": "logico", "arrumacao": "texto", "tema": "texto", "zoom": "numero",
          "linguagem": "texto", "comparar": "texto", "comparar_1": "texto", "comparar_2": "texto",
          "velocidade": "inteiro"}


# ----------------------------------------------------------------------
# Gravar
# ----------------------------------------------------------------------

# grafo: o dicionário de modelos.novo_grafo; nome: o nome do grafo; tela: o estado_da_tela da visualização
def dados_do_arquivo(grafo, nome, tela):
    return {
        "formato": FORMATO,
        "versao": VERSAO,
        "programa": f"{caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO}",
        "salvo_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "grafo": modelos.dados_do_grafo(nome, grafo),
        "tela": para_json(tela or {}),
    }


# O estado da tela tem tuplas (a célula escolhida é (linha, coluna)): o JSON só conhece listas
def para_json(valor):
    if isinstance(valor, dict):
        resultado = {}
        for chave in valor:
            resultado[str(chave)] = para_json(valor[chave])
        return resultado
    if isinstance(valor, (list, tuple)):
        return [para_json(item) for item in valor]
    if isinstance(valor, Decimal):
        return modelos.numero_para_json(valor)
    return valor


def salvar(caminho, grafo, nome, tela):
    texto = json.dumps(dados_do_arquivo(grafo, nome, tela), ensure_ascii=False, indent=2)
    caminho = str(caminho)
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto + "\n")
    os.replace(temporario, caminho)


# ----------------------------------------------------------------------
# Ler
# ----------------------------------------------------------------------

# Lê e confere o arquivo. Devolve (grafo, nome, tela); qualquer problema vira ValueError com a explicação.
def ler(caminho):
    detalhes = ler_com_detalhes(caminho)
    return detalhes["grafo"], detalhes["nome"], detalhes["tela"]


# O mesmo que ler(), num dicionário e com o que a prévia da tela do .bosco mostra a mais:
#   {"grafo": ..., "nome": ..., "tela": ..., "salvo_em": "2026-10-01 14:30" ou "", "programa": "BoscoGraph 7.0" ou ""}
def ler_com_detalhes(caminho):
    caminho = Path(caminho)
    rotulo = f"Arquivo \"{caminho.name}\""
    try:
        if caminho.stat().st_size > TAMANHO_MAXIMO:
            raise ValueError(f"{rotulo}: grande demais para ser um arquivo do BoscoGraph.")
        texto = caminho.read_text(encoding="utf-8-sig")         # -sig: aceita o arquivo com BOM do Bloco de Notas
    except OSError as erro:
        raise ValueError(f"{rotulo}: não consegui ler ({erro.strerror or erro}).")
    except UnicodeDecodeError:
        raise ValueError(f"{rotulo}: não é um arquivo de texto do BoscoGraph.")
    detalhes = {}
    grafo, nome, tela = ler_texto(texto, rotulo, detalhes)
    detalhes["grafo"] = grafo
    detalhes["nome"] = nome
    detalhes["tela"] = tela
    return detalhes


# detalhes: um dicionário que recebe a data e o programa que salvou (textos curtos; "" se não forem texto)
def ler_texto(texto, rotulo="Arquivo .bosco", detalhes=None):
    try:
        # parse_float=Decimal: os pesos "2.5" voltam como Decimal("2.5"), sem passar pelo float
        dados = json.loads(texto, parse_float=Decimal)
    except json.JSONDecodeError as erro:
        raise ValueError(f"{rotulo}: não é um JSON válido (linha {erro.lineno}, coluna {erro.colno}).")
    if not isinstance(dados, dict) or dados.get("formato") != FORMATO:
        raise ValueError(f"{rotulo}: não é um arquivo do BoscoGraph (falta \"formato\": \"{FORMATO}\").")
    versao = dados.get("versao")
    if isinstance(versao, bool) or not isinstance(versao, int) or versao < 1:
        raise ValueError(f"{rotulo}: a versão do arquivo não é um número válido.")
    if versao > VERSAO:
        raise ValueError(f"{rotulo}: foi salvo por um BoscoGraph mais novo ({dados.get('programa', '?')}). "
                         f"Atualize o programa para abrir.")
    grafo = modelos.grafo_dos_dados(dados.get("grafo"), rotulo)
    nome = dados["grafo"].get("nome")
    if not isinstance(nome, str) or nome.strip() == "":
        nome = "Grafo"
    nome = nome.strip()[:120]
    tela = limpar_tela(dados.get("tela"), grafo)
    if detalhes is not None:
        for chave in ("salvo_em", "programa"):
            valor = dados.get(chave)
            detalhes[chave] = valor.strip()[:40] if isinstance(valor, str) else ""
    return grafo, nome, tela


# Fica só o que tem o tipo certo; o resto é esquecido (a parte abre do começo)
def limpar_tela(tela, grafo):
    limpa = {"parte": None, "partes": {}, "exibir": {}}
    if not isinstance(tela, dict):
        return limpa
    if tela.get("parte") in ESCOLHAS_DAS_PARTES:
        limpa["parte"] = tela["parte"]
    partes = tela.get("partes")
    if isinstance(partes, dict):
        for chave in partes:
            if chave not in ESCOLHAS_DAS_PARTES or not isinstance(partes[chave], dict):
                continue
            escolhas = {}
            for nome, tipo in ESCOLHAS_DAS_PARTES[chave].items():
                if nome in partes[chave]:
                    certo, valor = conferir_valor(partes[chave][nome], tipo)
                    if certo and faz_sentido(chave, nome, valor, grafo):
                        escolhas[nome] = valor
            limpa["partes"][chave] = escolhas
    exibir = tela.get("exibir")
    if isinstance(exibir, dict):
        for nome, tipo in EXIBIR.items():
            if nome in exibir:
                certo, valor = conferir_valor(exibir[nome], tipo)
                if certo:
                    limpa["exibir"][nome] = valor
    if limpa["exibir"].get("tema") not in (None, "claro", "escuro"):
        limpa["exibir"].pop("tema")
    for chave in ("linguagem", "comparar", "comparar_1", "comparar_2"):
        if limpa["exibir"].get(chave) not in (None,) + LINGUAGENS_DO_CODIGO:
            limpa["exibir"].pop(chave)
    if not 0 <= limpa["exibir"].get("velocidade", 0) <= 4:
        limpa["exibir"].pop("velocidade")
    # A arrumação "como no arquivo" só existe se o grafo tiver as posições
    if limpa["exibir"].get("arrumacao") not in ("circulo", "arquivo"):
        limpa["exibir"].pop("arrumacao", None)
    if limpa["exibir"].get("arrumacao") == "arquivo" and not grafo["posicoes"]:
        limpa["exibir"]["arrumacao"] = "circulo"
    return limpa


# Além do tipo, o valor tem que fazer sentido NESTE grafo: o vértice escolhido existe, a aresta escolhida
# existe, a célula está dentro da matriz, a linguagem é uma das seis... (None sempre vale: "nada escolhido")
def faz_sentido(parte, nome, valor, grafo):
    if valor is None:
        return True
    quantidade_de_vertices = len(grafo["vertices"])
    quantidade_de_arestas = len(grafo["arestas"])
    if nome == "vertice":
        return valor in grafo["vertices"]
    if nome == "aresta":
        return valor.isdigit() and int(valor) < quantidade_de_arestas
    if nome == "arestas":
        for numero in valor:
            if numero >= quantidade_de_arestas:
                return False
        return True
    if nome == "passo":
        return valor.isdigit()
    if nome == "sentido":
        return valor in ("saem", "chegam")
    if nome == "modo":
        if parte == "comparar":
            return valor in ("passo", "linha")
        if parte == "adjacencia":
            return valor in ("contagem", "sinais", "pesos")
        return valor in ("sinais", "pesos")
    if nome == "celula":
        linha, coluna = valor
        colunas = quantidade_de_vertices if parte == "adjacencia" else quantidade_de_arestas
        if linha is not None and not (isinstance(linha, int) and 0 <= linha < quantidade_de_vertices):
            return False
        if coluna is not None and not (isinstance(coluna, int) and 0 <= coluna < colunas):
            return False
        return True
    if nome == "escolhida":
        chave, numero = valor
        return chave in LINGUAGENS_DO_CODIGO and isinstance(numero, int) and numero >= 1
    if nome in ("posicao", "linha", "posicao_passo", "posicao_linha", "preenchidas"):
        return valor >= -1
    return True


# As chaves das linguagens do painel de código ("boscograph" = o código do próprio programa)
LINGUAGENS_DO_CODIGO = ("boscograph", "pseudocodigo", "python", "java", "c", "cpp", "javascript")


# Devolve (o valor tem o tipo pedido?, o valor arrumado). None vale em todo tipo (= "nada escolhido").
def conferir_valor(valor, tipo):
    if valor is None:
        return True, None
    if tipo == "texto":
        return isinstance(valor, str) and len(valor) <= 500, valor
    if tipo == "logico":
        return isinstance(valor, bool), valor
    if tipo == "inteiro":
        certo = isinstance(valor, int) and not isinstance(valor, bool) and -1 <= valor <= 10 ** 7
        return certo, valor
    if tipo == "numero":
        if isinstance(valor, bool) or not isinstance(valor, (int, Decimal)):
            return False, None
        if not math.isfinite(valor):
            return False, None
        return True, float(valor)
    if tipo == "marcas":
        if not isinstance(valor, dict):
            return False, None
        marcas = {}
        for chave in valor:
            if isinstance(valor[chave], bool):
                marcas[chave] = valor[chave]
        return True, marcas
    if tipo == "par":
        if not isinstance(valor, list) or len(valor) != 2:
            return False, None
        for item in valor:
            if item is not None and not (isinstance(item, (int, str)) and not isinstance(item, bool)):
                return False, None
        return True, (valor[0], valor[1])
    if tipo == "inteiros":
        if not isinstance(valor, list) or len(valor) > 10000:
            return False, None
        for item in valor:
            if isinstance(item, bool) or not isinstance(item, int) or item < 0:
                return False, None
        return True, list(valor)
    return False, None


# ----------------------------------------------------------------------
# Os abertos por último (a lista "Abertos recentemente" da tela do .bosco)
# ----------------------------------------------------------------------
# Um arquivo de texto na pasta dos dados (a mesma dos modelos), com um caminho por linha,
# do mais novo para o mais antigo. Se não der para ler ou gravar, a lista só fica vazia.

MAXIMO_DE_RECENTES = 6


def arquivo_dos_recentes():
    return modelos.PASTA_DOS_MODELOS / "recentes.txt"


# O mesmo arquivo escrito de jeitos diferentes ("C:\Aulas\a.bosco" e "c:/aulas/A.bosco" no Windows)
def mesmo_arquivo(caminho_1, caminho_2):
    return os.path.normcase(os.path.abspath(caminho_1)) == os.path.normcase(os.path.abspath(caminho_2))


def listar_recentes():
    try:
        texto = arquivo_dos_recentes().read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    recentes = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if linha == "":
            continue
        repetido = False
        for outro in recentes:
            if mesmo_arquivo(outro, linha):
                repetido = True
        if not repetido:
            recentes.append(linha)
    return recentes[:MAXIMO_DE_RECENTES]


def gravar_recentes(recentes):
    try:
        modelos.PASTA_DOS_MODELOS.mkdir(parents=True, exist_ok=True)
        modelos.gravar_texto(arquivo_dos_recentes(), "\n".join(recentes[:MAXIMO_DE_RECENTES]) + "\n")
    except OSError:
        pass                # sem permissão de gravar: a lista de recentes não é importante


# O arquivo vai para o começo da lista (se já estava, sai do lugar antigo)
def lembrar_recente(caminho):
    caminho = os.path.abspath(str(caminho))
    recentes = [caminho]
    for outro in listar_recentes():
        if not mesmo_arquivo(outro, caminho):
            recentes.append(outro)
    gravar_recentes(recentes)


def esquecer_recente(caminho):
    recentes = []
    for outro in listar_recentes():
        if not mesmo_arquivo(outro, str(caminho)):
            recentes.append(outro)
    gravar_recentes(recentes)
