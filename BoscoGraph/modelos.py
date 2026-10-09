'''
    Modelos: grafos salvos em arquivos .json dentro da pasta "modelos".

    Cada modelo guarda os vértices, as arestas (com nome e peso), a heurística dos vértices e as
    opções da busca. O modelo padrão (o que abre quando o BoscoGraph começa) fica anotado em
    "padrao.txt". Se a pasta ou o modelo da prova sumirem, eles são recriados.

    Exemplo de arquivo:
    {
      "nome": "Exemplo",
      "vertices": ["A", "B", "C"],
      "arestas": [
        {"origem": "A", "destino": "B", "nome": "e1", "peso": 4},
        {"origem": "B", "destino": "C", "nome": "", "peso": 2.5},
        {"origem": "A", "destino": "C", "nome": ""}
      ],
      "ordenar": true,
      "inicio": "A",
      "direcionado": true,
      "algoritmo": "dijkstra",
      "destino": "C",
      "heuristica": {"A": 5, "B": 2, "C": 0},
      "posicoes": {"A": [0, 0], "B": [120, 40], "C": [240, 0]},
      "arrumacao": "arquivo",
      "limite": 3
    }
    Só "vertices" e "arestas" são obrigatórios: o que faltar recebe o valor padrão
    (os modelos das versões anteriores continuam abrindo). Sem "peso" = aresta sem peso;
    "direcionado" falso = grafo não orientado; "posicoes" vem da importação de um desenho, e
    "arrumacao" diz como desenhar: "circulo" ou "arquivo" (nas posições do desenho original).
    "limite" é o limite de profundidade da busca limitada (só aparece quando existe).

    Dentro do programa, um grafo com as opções é um dicionário com as mesmas chaves do arquivo
    (veja novo_grafo); os pesos ficam como Decimal (veja entrada.py).
'''

import json
import math
import os
import shutil
from decimal import Decimal

import algoritmos
import caminhos
import entrada

# Onde os modelos do usuário são gravados: a pasta modelos/ do projeto (rodando pelo código)
# ou %APPDATA%\BoscoGraph\modelos (instalado). As regras estão em caminhos.py.
PASTA_DOS_MODELOS = caminhos.pasta_dos_modelos()
# Os modelos de exemplo que vêm com o programa (só leitura)
PASTA_DOS_EXEMPLOS = caminhos.pasta_dos_exemplos()
NOME_DO_MODELO_DA_PROVA = "Prova 01"
TAMANHO_MAXIMO_DO_NOME = 40


# Um grafo com as opções da busca, no formato que o editor, os modelos e a importação usam.
#   heuristica -> {vértice: h} (só a gulosa e o A* usam)
#   posicoes   -> {vértice: (x, y)} (vem da importação de um desenho; vazio = arrumar em círculo)
#   arrumacao  -> "circulo" ou "arquivo" (None = "arquivo" se houver posições, senão "circulo")
#   limite     -> o limite de profundidade da busca limitada (None = nenhum escolhido)
def novo_grafo(vertices, arestas, ordenar=True, inicio=None, direcionado=True,
               algoritmo=algoritmos.PROFUNDIDADE, destino=None, heuristica=None, posicoes=None, arrumacao=None,
               limite=None):
    if heuristica is None:
        heuristica = {}
    if posicoes is None:
        posicoes = {}
    if arrumacao not in ("circulo", "arquivo"):
        arrumacao = "circulo"
        if posicoes:
            arrumacao = "arquivo"
    return {
        "vertices": list(vertices),
        "arestas": list(arestas),
        "ordenar": ordenar,
        "inicio": inicio,
        "direcionado": direcionado,
        "algoritmo": algoritmo,
        "destino": destino,
        "heuristica": dict(heuristica),
        "posicoes": dict(posicoes),
        "arrumacao": arrumacao,
        "limite": limite,
    }


def arquivo_do_padrao():
    return PASTA_DOS_MODELOS / "padrao.txt"


def caminho_do_modelo(nome):
    return PASTA_DOS_MODELOS / f"{nome}.json"


def existe_modelo(nome):
    return caminho_do_modelo(nome).exists()


# No Windows, "prova 01" e "Prova 01" são o MESMO arquivo (maiúsculas e minúsculas não importam
# no nome de arquivo). Por isso os nomes de modelo são comparados assim, e não com ==.
def mesmo_nome(nome_1, nome_2):
    return nome_1.casefold() == nome_2.casefold()


# Garante que existam a pasta, o modelo da prova e a anotação de qual é o padrão.
# Na primeira vez (a pasta ainda não existe), os modelos de exemplo são copiados para ela.
def garantir_modelo_da_prova():
    if not PASTA_DOS_MODELOS.exists():
        # parents=True cria também as pastas de cima que faltarem (por exemplo %APPDATA%\BoscoGraph)
        PASTA_DOS_MODELOS.mkdir(parents=True, exist_ok=True)
        copiar_exemplos()
    if not existe_modelo(NOME_DO_MODELO_DA_PROVA):
        vertices, arestas = entrada.grafo_da_prova()
        salvar_modelo(NOME_DO_MODELO_DA_PROVA, novo_grafo(vertices, arestas, True, "A", True))
    if not arquivo_do_padrao().exists():
        gravar_texto(arquivo_do_padrao(), NOME_DO_MODELO_DA_PROVA)


# Copia os modelos de exemplo que vêm com o programa para a pasta do usuário.
# Rodando pelo código-fonte as duas pastas são a mesma, e não há nada para copiar.
# Um exemplo que o usuário já tem (com o mesmo nome) nunca é substituído.
def copiar_exemplos():
    if not PASTA_DOS_EXEMPLOS.is_dir():
        return
    if PASTA_DOS_EXEMPLOS.resolve() == PASTA_DOS_MODELOS.resolve():
        return
    for arquivo in sorted(PASTA_DOS_EXEMPLOS.glob("*.json")):
        destino = PASTA_DOS_MODELOS / arquivo.name
        if not destino.exists():
            shutil.copyfile(arquivo, destino)


# Grava um texto num arquivo sem correr o risco de deixá-lo pela metade:
# primeiro grava num arquivo temporário e só depois troca um pelo outro (os.replace).
# Se a energia cair no meio da gravação, o arquivo antigo continua inteiro.
def gravar_texto(caminho, texto):
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(texto, encoding="utf-8")
    os.replace(temporario, caminho)


# Devolve "" se o nome serve para nome de arquivo, ou a explicação do problema
def validar_nome_de_modelo(nome):
    if nome.strip() == "":
        return "Digite um nome para o modelo."
    if nome != nome.strip():
        return "O nome do modelo não pode começar nem terminar com espaço."
    if len(nome) > TAMANHO_MAXIMO_DO_NOME:
        return f"O nome do modelo pode ter no máximo {TAMANHO_MAXIMO_DO_NOME} caracteres."
    for caractere in '\\/:*?"<>|':              # caracteres que o Windows não aceita em nome de arquivo
        if caractere in nome:
            return f"O nome do modelo não pode ter '{caractere}'."
    if nome.endswith("."):
        return "O nome do modelo não pode terminar com ponto."
    return ""


def listar_modelos():
    garantir_modelo_da_prova()
    nomes = []
    for caminho in PASTA_DOS_MODELOS.glob("*.json"):
        nomes.append(caminho.stem)      # stem = nome do arquivo sem o ".json"
    return sorted(nomes)


# O JSON não conhece o Decimal: um peso inteiro vai como int (5) e um decimal como float (2.5).
# Como os pesos têm no máximo 3 casas, o float escrito no arquivo é exatamente o número digitado.
def numero_para_json(numero):
    if numero == numero.to_integral_value():
        return int(numero)
    return float(numero)


# Grava o modelo. "grafo" é o dicionário de novo_grafo.
def salvar_modelo(nome, grafo):
    problema = validar_nome_de_modelo(nome)
    if problema:
        raise ValueError(problema)
    PASTA_DOS_MODELOS.mkdir(parents=True, exist_ok=True)
    dados = dados_do_grafo(nome, grafo)
    # ensure_ascii=False mantém os acentos legíveis no arquivo; indent=2 deixa o arquivo organizado
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    gravar_texto(caminho_do_modelo(nome), texto)


# O dicionário que vai para o arquivo (JSON) de um grafo: o modelo salvo e o arquivo .bosco usam o
# mesmo formato (e o mesmo grafo_dos_dados para ler de volta). Os pesos (Decimal) viram números do JSON.
def dados_do_grafo(nome, grafo):
    lista_de_arestas = []
    for origem, destino, nome_da_aresta, peso in grafo["arestas"]:
        aresta = {"origem": origem, "destino": destino, "nome": nome_da_aresta}
        if peso is not None:
            aresta["peso"] = numero_para_json(peso)
        lista_de_arestas.append(aresta)
    dados = {
        "nome": nome,
        "vertices": list(grafo["vertices"]),
        "arestas": lista_de_arestas,
        "ordenar": grafo["ordenar"],
        "inicio": grafo["inicio"],
        "direcionado": grafo["direcionado"],
        "algoritmo": grafo["algoritmo"],
        "destino": grafo["destino"],
    }
    # Heurística e posições só entram no arquivo quando existem (o arquivo fica mais limpo)
    if grafo["heuristica"]:
        heuristica = {}
        for vertice in grafo["vertices"]:
            if vertice in grafo["heuristica"]:
                heuristica[vertice] = numero_para_json(grafo["heuristica"][vertice])
        dados["heuristica"] = heuristica
    if grafo["posicoes"]:
        posicoes = {}
        for vertice in grafo["vertices"]:
            if vertice in grafo["posicoes"]:
                x, y = grafo["posicoes"][vertice]
                posicoes[vertice] = [round(x, 2), round(y, 2)]
        dados["posicoes"] = posicoes
        dados["arrumacao"] = grafo["arrumacao"]
    if grafo.get("limite") is not None:
        dados["limite"] = grafo["limite"]
    return dados


# Lê um modelo e confere se ele faz sentido, porque o arquivo pode ter sido editado à mão.
# Qualquer problema vira um ValueError com a explicação (o editor mostra a mensagem na tela).
# Devolve o dicionário de novo_grafo.
def carregar_modelo(nome):
    if not existe_modelo(nome):
        raise ValueError(f"O modelo '{nome}' não existe.")
    try:
        # parse_float=Decimal: "2.5" no arquivo vira Decimal("2.5") direto, sem passar pelo float
        dados = json.loads(caminho_do_modelo(nome).read_text(encoding="utf-8"), parse_float=Decimal)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError(f"O arquivo do modelo '{nome}' não é um JSON válido.")
    return grafo_dos_dados(dados, f"Modelo '{nome}'")


# Lê um dos modelos de exemplo direto da pasta que vem com o programa: a versão original, mesmo que
# a pessoa tenha mudado a cópia dela. É o "Ver exemplo" da tela inicial.
def carregar_exemplo(nome):
    caminho = PASTA_DOS_EXEMPLOS / (nome + ".json")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"), parse_float=Decimal)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError(f"Não consegui abrir o exemplo '{nome}'.")
    return grafo_dos_dados(dados, f"Exemplo '{nome}'")


# Um número que veio do arquivo (int, Decimal ou texto como "2,5") vira Decimal.
# "onde" entra na mensagem de erro (por exemplo "o peso da aresta A -> B").
def numero_do_arquivo(valor, onde, rotulo):
    # bool é um tipo de int no Python (True == 1): por isso é recusado antes
    if isinstance(valor, bool) or not isinstance(valor, (int, Decimal, str)):
        raise ValueError(f"{rotulo}: {onde} não é um número.")
    numero, problema = entrada.ler_numero(str(valor))
    if problema or numero is None:
        raise ValueError(f"{rotulo}: {onde}: {problema or 'está vazio'}")
    return numero


# Confere os dados lidos do arquivo (vértices válidos e sem repetição, arestas com vértices
# que existem, pesos e heurísticas que são números, limites respeitados) e monta o grafo.
# "rotulo" começa as mensagens de erro (por exemplo "Modelo 'Aula 3'").
def grafo_dos_dados(dados, rotulo):
    if not isinstance(dados, dict) or not isinstance(dados.get("vertices"), list) \
            or not isinstance(dados.get("arestas"), list):
        raise ValueError(f"{rotulo}: o arquivo precisa ter as listas \"vertices\" e \"arestas\".")

    vertices = []
    for vertice in dados["vertices"]:
        if not isinstance(vertice, str):
            raise ValueError(f"{rotulo}: o vértice {vertice!r} não é um texto.")
        problema = entrada.validar_nome_de_vertice(vertice, vertices)
        if problema:
            raise ValueError(f"{rotulo}: {problema}")
        vertices.append(vertice)
    if len(vertices) > entrada.MAXIMO_DE_VERTICES:
        raise ValueError(f"{rotulo}: tem mais de {entrada.MAXIMO_DE_VERTICES} vértices.")

    arestas = []
    for aresta in dados["arestas"]:
        if not isinstance(aresta, dict):
            raise ValueError(f"{rotulo}: cada aresta precisa ter \"origem\" e \"destino\".")
        origem = aresta.get("origem")
        destino = aresta.get("destino")
        nome_da_aresta = aresta.get("nome", "")
        if origem not in vertices or destino not in vertices:
            raise ValueError(f"{rotulo}: a aresta {origem} -> {destino} usa um vértice que não existe.")
        if not isinstance(nome_da_aresta, str):
            raise ValueError(f"{rotulo}: o nome da aresta {origem} -> {destino} não é um texto.")
        problema = entrada.validar_nome_de_aresta(nome_da_aresta)
        if problema:
            raise ValueError(f"{rotulo}: {problema}")
        peso = None
        if aresta.get("peso") is not None:
            peso = numero_do_arquivo(aresta["peso"], f"o peso da aresta {origem} -> {destino}", rotulo)
        arestas.append((origem, destino, nome_da_aresta, peso))
    if len(arestas) > entrada.LIMITE_DE_ARESTAS:
        raise ValueError(f"{rotulo}: tem mais de {entrada.LIMITE_DE_ARESTAS} arestas.")

    heuristica = {}
    dados_da_heuristica = dados.get("heuristica", {})
    if not isinstance(dados_da_heuristica, dict):
        raise ValueError(f"{rotulo}: \"heuristica\" precisa ser um dicionário {{\"vértice\": número}}.")
    for vertice in dados_da_heuristica:
        if vertice not in vertices:
            raise ValueError(f"{rotulo}: a heurística fala do vértice {vertice}, que não existe.")
        h = numero_do_arquivo(dados_da_heuristica[vertice], f"a heurística de {vertice}", rotulo)
        if h < 0:
            raise ValueError(f"{rotulo}: a heurística de {vertice} é negativa.")
        heuristica[vertice] = h

    posicoes = {}
    dados_das_posicoes = dados.get("posicoes", {})
    if not isinstance(dados_das_posicoes, dict):
        raise ValueError(f"{rotulo}: \"posicoes\" precisa ser um dicionário {{\"vértice\": [x, y]}}.")
    for vertice in dados_das_posicoes:
        par = dados_das_posicoes[vertice]
        if vertice not in vertices or not isinstance(par, list) or len(par) != 2:
            raise ValueError(f"{rotulo}: a posição de {vertice} precisa ser [x, y] de um vértice que existe.")
        for valor in par:
            if isinstance(valor, bool) or not isinstance(valor, (int, Decimal)) or not math.isfinite(valor):
                raise ValueError(f"{rotulo}: a posição de {vertice} precisa ter dois números.")
        posicoes[vertice] = (float(par[0]), float(par[1]))

    ordenar = dados.get("ordenar", True)
    if not isinstance(ordenar, bool):
        ordenar = True
    inicio = dados.get("inicio")
    if inicio not in vertices:
        inicio = None                   # None = a busca começa pelo primeiro em ordem alfabética
    direcionado = dados.get("direcionado", True)       # modelos antigos não têm essa chave: orientado
    if not isinstance(direcionado, bool):
        direcionado = True
    algoritmo = dados.get("algoritmo", algoritmos.PROFUNDIDADE)
    if not algoritmos.existe(algoritmo):
        algoritmo = algoritmos.PROFUNDIDADE
    destino = dados.get("destino")
    if destino not in vertices:
        destino = None
    arrumacao = dados.get("arrumacao")          # None ou inválida: novo_grafo escolhe pelo que existe
    limite = dados.get("limite")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 0 <= limite <= algoritmos.MAIOR_LIMITE:
        limite = None                   # sem limite (ou um limite estranho): o editor sugere um
    return novo_grafo(vertices, arestas, ordenar, inicio, direcionado, algoritmo, destino, heuristica, posicoes,
                      arrumacao, limite)


def nome_do_padrao():
    garantir_modelo_da_prova()
    nome = arquivo_do_padrao().read_text(encoding="utf-8").strip()
    if not existe_modelo(nome):
        return NOME_DO_MODELO_DA_PROVA
    return nome


def definir_padrao(nome):
    if not existe_modelo(nome):
        raise ValueError(f"Salve o modelo '{nome}' antes de torná-lo padrão.")
    gravar_texto(arquivo_do_padrao(), nome)
