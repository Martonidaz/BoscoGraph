'''
    Rastreador: roda o Python de estudo LINHA POR LINHA e guarda o que aconteceu em cada uma.

    Como funciona: o Python deixa registrar uma função "de rastro" com sys.settrace. Daí em diante, a
    cada linha que vai rodar (e a cada função que começa ou termina), o próprio Python chama essa
    função, passando o "quadro" (frame) da execução: em que arquivo e linha está, e as variáveis locais.
    É assim que os depuradores (debuggers) funcionam. Aqui, a função de rastro só olha os quadros do
    arquivo de estudo e, em cada linha, tira uma "foto": a pilha de chamadas (quem chamou quem, com as
    variáveis de cada um) e os campos do objeto da busca.

    Cada linha executada vira um PASSO DE LINHA. Na tela, o passo j mostra:
      - a linha j em destaque (a que acabou de rodar) e a próxima a rodar;
      - as variáveis DEPOIS da linha j (a foto tirada no evento seguinte);
      - o desenho com os passos da busca que já aconteceram (veja sincronizar).

    Dois jeitos de rodar:
      - rastrear(): só a busca (o objeto já criado, a função da busca chamada direto);
      - rastrear_programa(): o PROGRAMA INTEIRO, desde a linha 1 (o cabeçalho, a classe, o grafo, a
        chamada e os print do fim). É o que a tela usa no linha a linha (veja a explicação lá embaixo).

    Este arquivo não usa Tkinter.
'''

import ast
import sys
import types
from decimal import Decimal

import algoritmos
import estudo
from estudo import explicacoes
from classes.aresta import Aresta
from classes.grafo import Grafo
from classes.vertice import Vertice
from entrada import formatar_numero

# Para não travar a tela num grafo grande: o rastro para nesse número de linhas
LIMITE_DE_LINHAS = 20000
TAMANHO_MAXIMO_DO_VALOR = 400       # caracteres de cada valor mostrado


class RastroGrandeDemais(Exception):
    pass


# Um valor do Python como aparece no painel de variáveis: nomes entre aspas simples (como o Python
# escreve), números no formato da tela (2,5 e ∞), listas, tuplas e dicionários por dentro
def formatar(valor):
    if valor is None or isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, (int, Decimal)):
        return formatar_numero(valor)
    if isinstance(valor, str):
        return f"'{valor}'"
    if isinstance(valor, tuple):
        partes = []
        for item in valor:
            partes.append(formatar(item))
        return "(" + ", ".join(partes) + ")"
    if isinstance(valor, dict):
        partes = []
        for chave in valor:
            partes.append(f"{formatar(chave)}: {formatar(valor[chave])}")
        return "{" + ", ".join(partes) + "}"
    if hasattr(valor, "__iter__"):                  # lista, deque...
        partes = []
        for item in valor:
            partes.append(formatar(item))
        return "[" + ", ".join(partes) + "]"
    return str(valor)


def curto(texto):
    if len(texto) > TAMANHO_MAXIMO_DO_VALOR:
        return texto[:TAMANHO_MAXIMO_DO_VALOR - 1] + "…"
    return texto


# Um valor para o painel de variáveis: (texto, itens). Os dicionários (cor, d, pai...) também vêm
# item por item, para o painel poder abrir cada um: itens = [(chave, valor), ...]; nos outros, None.
def descrever(valor):
    if not isinstance(valor, dict):
        return curto(formatar(valor)), None
    # O texto do dicionário inteiro é feito com os textos dos itens (cada item é formatado uma vez só:
    # isto roda a cada linha do rastro, e uma matriz d do Floyd-Warshall tem n x n números)
    itens = []
    partes = []
    for chave in valor:
        texto_da_chave = formatar(chave)
        texto_do_valor = formatar(valor[chave])
        itens.append((texto_da_chave, curto(texto_do_valor)))
        partes.append(f"{texto_da_chave}: {texto_do_valor}")
    return curto("{" + ", ".join(partes) + "}"), itens


# Os campos que são a entrada da busca: não mudam, não precisam aparecer
CAMPOS_DA_ENTRADA = ("adj", "adj_tras", "arcos", "arestas", "vertices", "h", "direcionado")


# A foto de um momento: a pilha de chamadas do arquivo de estudo (da chamada mais recente para a
# mais antiga), com as variáveis de cada uma, e os campos do objeto da busca (self.tempo, self.fila...).
# Cada variável e cada campo: (nome, texto, itens), como em descrever.
def tirar_foto(quadro, nome_do_arquivo):
    pilha = []
    objeto = None
    atual = quadro
    while atual is not None and atual.f_code.co_filename == nome_do_arquivo:
        variaveis = []
        for nome, valor in atual.f_locals.items():
            if nome == "self":
                objeto = valor
            else:
                texto, itens = descrever(valor)
                variaveis.append((nome, texto, itens))
        pilha.append({"funcao": atual.f_code.co_name, "linha": atual.f_lineno, "variaveis": variaveis})
        atual = atual.f_back
    campos = []
    if objeto is not None:
        campos = tirar_foto_do_objeto(objeto)
    return {"pilha": pilha, "campos": campos}


# A entrada da busca, montada do mesmo jeito que o BoscoGraph monta (a mesma ordem das listas)
def montar_entrada(vertices, arestas, ordenar, inicio, direcionado):
    dicionario = {}
    for nome in vertices:
        dicionario[nome] = Vertice(nome)
    lista = []
    for origem, destino, nome, peso in arestas:
        lista.append(Aresta(dicionario[origem], dicionario[destino], nome, peso))
    grafo = Grafo(list(dicionario.values()), lista, [], direcionado)
    if ordenar:
        grafo.ordenar_listas_adjacencia()
    if inicio not in vertices:
        inicio = sorted(vertices)[0] if vertices else None
    return grafo, inicio


# A entrada do código de estudo, montada como o BoscoGraph monta (com a mesma ordem das listas):
#   "origem"    -> o vértice de partida
#   "vizinhos"  -> {u: [v1, v2, ...]}             (a DFS de estudo não usa os pesos)
#   "com_pesos" -> {u: [(v, peso), ...]}
#   "com_pesos_tras" -> {v: [(u, peso), ...]}: quem CHEGA em v (o lado de trás da busca bidirecional);
#                       no não orientado é igual a "com_pesos"
#   "ordem"     -> as raízes da DFS: a origem primeiro, depois os outros em ordem alfabética
#   "arcos"     -> [(u, v, peso), ...] na ordem de criação; no não orientado, nos dois sentidos
#   "arestas"   -> [(u, v, peso), ...] na ordem de criação, UMA vez cada (o Kruskal; versão 7.3)
# Os testes usam esta mesma entrada para rodar as traduções (Java, C...) e comparar.
def preparar_entrada(vertices, arestas, ordenar, inicio, direcionado):
    grafo, origem = montar_entrada(vertices, arestas, ordenar, inicio, direcionado)
    vizinhos = {}
    com_pesos = {}
    com_pesos_tras = {}
    reversa = grafo.lista_reversa()
    for vertice in grafo.grafo:
        vizinhos[vertice] = list(grafo.grafo[vertice])
        com_pesos[vertice] = []
        for vizinho, peso, numero in grafo.lista_com_pesos[vertice]:
            com_pesos[vertice].append((vizinho, peso))
        com_pesos_tras[vertice] = []
        for vizinho, peso, numero in reversa[vertice]:
            com_pesos_tras[vertice].append((vizinho, peso))
    ordem = sorted(grafo.grafo)
    if origem in ordem:
        ordem.remove(origem)
        ordem.insert(0, origem)
    arcos = []
    arestas_uma_vez = []
    for aresta in grafo.arestas:
        u = aresta.vertice_origem.nome
        v = aresta.vertice_destino.nome
        arcos.append((u, v, aresta.peso))
        if not direcionado and u != v:
            arcos.append((v, u, aresta.peso))
        arestas_uma_vez.append((u, v, aresta.peso))
    return {"origem": origem, "vizinhos": vizinhos, "com_pesos": com_pesos, "com_pesos_tras": com_pesos_tras,
            "ordem": ordem, "arcos": arcos, "arestas": arestas_uma_vez}


# Carrega o Python de estudo da busca e cria o objeto dela, pronto para rodar.
# Devolve (o arquivo carregado, o objeto da busca, uma função que executa a busca).
def criar_busca(algoritmo, entrada, direcionado, destino=None, heuristica=None, limite=None):
    arquivo = estudo.carregar(algoritmo, "python")
    codigo = compile(arquivo["texto_original"], str(arquivo["caminho"]), "exec")
    ambiente = {"__name__": "estudo_" + algoritmo}
    exec(codigo, ambiente)                          # define as classes (sem rastro: ainda não é a busca)
    origem = entrada["origem"]
    if algoritmo == algoritmos.PROFUNDIDADE:
        busca = ambiente["BuscaEmProfundidade"](entrada["vizinhos"], direcionado)
        executar = lambda: busca.dfs(entrada["ordem"])
    elif algoritmo == algoritmos.LARGURA:
        busca = ambiente["BuscaEmLargura"](entrada["com_pesos"])
        executar = lambda: busca.bfs(origem)
    elif algoritmo == algoritmos.DIJKSTRA:
        busca = ambiente["Dijkstra"](entrada["com_pesos"])
        executar = lambda: busca.dijkstra(origem)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        busca = ambiente["BellmanFord"](list(entrada["vizinhos"]), entrada["arcos"])
        executar = lambda: busca.bellman_ford(origem)
    elif algoritmo == algoritmos.LIMITADA:
        busca = ambiente["ProfundidadeLimitada"](entrada["vizinhos"])
        executar = lambda: busca.buscar(origem, destino, limite)
    elif algoritmo == algoritmos.ITERATIVA:
        busca = ambiente["AprofundamentoIterativo"](entrada["vizinhos"])
        executar = lambda: busca.buscar(origem, destino)
    elif algoritmo == algoritmos.BIDIRECIONAL:
        busca = ambiente["BuscaBidirecional"](entrada["com_pesos"], entrada["com_pesos_tras"])
        executar = lambda: busca.buscar(origem, destino)
    elif algoritmo == algoritmos.FLOYD_WARSHALL:
        busca = ambiente["FloydWarshall"](list(entrada["vizinhos"]), entrada["arcos"])
        executar = lambda: busca.floyd_warshall()
    elif algoritmo == algoritmos.GULOSA:
        busca = ambiente["BuscaGulosa"](entrada["com_pesos"], dict(heuristica or {}))
        executar = lambda: busca.buscar(origem, destino)
    elif algoritmo == algoritmos.PRIM:
        busca = ambiente["Prim"](entrada["com_pesos"])
        executar = lambda: busca.prim(entrada["ordem"])
    elif algoritmo == algoritmos.KRUSKAL:
        busca = ambiente["Kruskal"](list(entrada["vizinhos"]), entrada["arestas"])
        executar = lambda: busca.kruskal()
    else:
        busca = ambiente["AEstrela"](entrada["com_pesos"], dict(heuristica or {}))
        executar = lambda: busca.buscar(origem, destino)
    return arquivo, busca, executar


# Executa o Python de estudo da busca com o rastro ligado. Devolve:
#   "passos_de_linha" -> um por linha executada, na ordem: {"linha", "rotulo", "proxima", "antes", "foto",
#                        "explicacao", "profundidade"}
#                        "antes" = a foto antes de a linha rodar; "foto" = a foto depois
#                        "explicacao" = o que a linha vai fazer, com os valores (estudo/explicacoes.py)
#                        "profundidade" = quantas chamadas há na pilha (1 = a função da busca)
#   "arquivo"         -> o código de estudo carregado (estudo.carregar)
#   "resposta"        -> o que a função da busca devolveu (True/False em algumas)
#   "busca"           -> o objeto da busca, com o estado final (cor, d, pai...)
# estrito=True (nos testes): uma explicação que dê erro interrompe tudo, em vez de ficar vazia.
def rastrear(algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino=None, heuristica=None,
             estrito=False, limite=None):
    entrada = preparar_entrada(vertices, arestas, ordenar, inicio, direcionado)
    arquivo, busca, executar = criar_busca(algoritmo, entrada, direcionado, destino, heuristica, limite)
    nome_do_arquivo = str(arquivo["caminho"])
    rotulo_da_linha = arquivo["rotulo_da_linha"]

    eventos = []                                    # (tipo, linha, foto, explicação)

    def rastro(quadro, evento, argumento):
        if quadro.f_code.co_filename != nome_do_arquivo:
            return None                             # outro arquivo: não rastreia lá dentro
        if evento in ("line", "return"):
            explicacao = ""
            if evento == "line" and quadro.f_lineno in rotulo_da_linha:
                locais = quadro.f_locals
                explicacao = explicacoes.explicar_linha(algoritmo, rotulo_da_linha[quadro.f_lineno], locais,
                                                        locais.get("self"), estrito)
            eventos.append((evento, quadro.f_lineno, tirar_foto(quadro, nome_do_arquivo), explicacao))
            if len(eventos) > LIMITE_DE_LINHAS:
                raise RastroGrandeDemais(f"A busca passou de {LIMITE_DE_LINHAS} linhas: grande demais para "
                                         f"seguir linha a linha.")
        return rastro

    antigo = sys.gettrace()
    sys.settrace(rastro)
    try:
        resposta = executar()
    finally:
        sys.settrace(antigo)
    foto_final = {"pilha": [], "campos": tirar_foto_do_objeto(busca)}

    # Cada evento de linha vira um passo de linha: a foto "depois" é a do evento seguinte
    passos_de_linha = []
    for indice in range(len(eventos)):
        tipo, linha, foto, explicacao = eventos[indice]
        if tipo != "line":
            continue
        depois = foto_final
        if indice + 1 < len(eventos):
            depois = eventos[indice + 1][2]
        proxima = None
        for seguinte in range(indice + 1, len(eventos)):
            if eventos[seguinte][0] == "line":
                proxima = eventos[seguinte][1]
                break
        passos_de_linha.append({"linha": linha, "rotulo": rotulo_da_linha.get(linha), "proxima": proxima,
                                "antes": foto, "foto": depois, "explicacao": explicacao,
                                "profundidade": len(foto["pilha"])})
    return {"passos_de_linha": passos_de_linha, "arquivo": arquivo, "resposta": resposta, "busca": busca,
            "foto_final": foto_final}


def tirar_foto_do_objeto(busca):
    campos = []
    for nome, valor in vars(busca).items():
        if nome in CAMPOS_DA_ENTRADA:
            continue
        texto, itens = descrever(valor)
        campos.append((nome, texto, itens))
    return campos


# ----------------------------------------------------------------------
# O programa INTEIRO, da primeira à última linha (o modo linha a linha da tela)
# ----------------------------------------------------------------------
#
# rastrear() acima roda só a busca. Aqui roda o arquivo todo, o mesmo que a exportação do código-fonte
# grava (exportacao/codigo_fonte.py): o cabeçalho, os import, a classe, as funções de ajuda, o grafo, a
# chamada da busca e os print do resultado. Como num depurador, desde a primeira linha:
#   - cada comando executado é um passo (um comando de várias linhas, como o dicionário adj, é UM passo);
#   - ao entrar numa função, a linha do def é um passo (com os parâmetros que ela recebeu);
#   - os comentários e as linhas em branco do caminho também são passos (o Python não os executa, mas
#     quem lê passa por eles): os que ficam logo antes do próximo comando, no mesmo trecho do código.
# O que o programa escreve (o print) é guardado: a tela mostra no painel Saída.

NOME_DO_PROGRAMA = "<programa do BoscoGraph>"   # o "arquivo" do programa (o rastro só olha o que é dele)
LIMITE_DE_EVENTOS = 40000


# Os comandos do programa: para cada linha, (primeira, última) linha do comando a que ela pertence.
# Num comando composto (for, if, while, def, class), só o cabeçalho, até os dois-pontos.
def comandos_do_programa(texto):
    comando_da_linha = {}

    def visitar(corpo):
        for no in corpo:
            if not isinstance(no, ast.stmt):
                continue
            inicio = no.lineno
            if hasattr(no, "body"):
                fim = fim_do_cabecalho(no)
            else:
                fim = no.end_lineno
            for linha in range(inicio, fim + 1):
                comando_da_linha[linha] = (inicio, fim)
            for campo in ("body", "orelse", "finalbody"):
                visitar(getattr(no, campo, []) or [])
            for tratador in getattr(no, "handlers", []) or []:
                visitar(tratador.body)

    visitar(ast.parse(texto).body)
    return comando_da_linha


# A última linha do cabeçalho de um comando composto (onde ficam os dois-pontos)
def fim_do_cabecalho(no):
    fim = no.lineno
    partes = []
    if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
        partes = list(ast.walk(no.args)) + ([no.returns] if no.returns is not None else [])
    elif isinstance(no, ast.ClassDef):
        partes = list(no.bases) + list(no.keywords)
    elif isinstance(no, (ast.For, ast.AsyncFor)):
        partes = [no.target, no.iter]
    elif isinstance(no, (ast.If, ast.While)):
        partes = [no.test]
    elif isinstance(no, (ast.With, ast.AsyncWith)):
        partes = [item.context_expr for item in no.items]
    for parte in partes:
        fim = max(fim, getattr(parte, "end_lineno", None) or fim)
    return fim


def comentario_ou_branco(linha):
    texto = linha.strip()
    return texto == "" or texto.startswith("#")


# As variáveis do programa (as globais), sem o que não é dado: os módulos importados, as classes, as
# funções e os nomes internos do Python (__name__...). O objeto da busca aparece como "objeto Dijkstra":
# os campos dele aparecem no painel dos campos.
def variaveis_do_programa(globais, guardados):
    variaveis = []
    for nome, valor in list(globais.items()):
        if nome.startswith("__") or nome == "print":
            continue
        if isinstance(valor, (types.ModuleType, types.FunctionType, types.BuiltinFunctionType, type)):
            continue
        if objeto_do_programa(valor, globais):
            variaveis.append((nome, f"objeto {type(valor).__name__}", None))
            continue
        # As listas e os dicionários do programa (nomes, adj...) não mudam depois de criados: o texto
        # deles é feito uma vez só (descrever a lista de adjacência a cada linha deixaria tudo lento)
        if isinstance(valor, (list, dict, tuple)):
            chave = (nome, id(valor), len(valor))
            if chave not in guardados:
                guardados[chave] = descrever(valor)
            texto, itens = guardados[chave]
        else:
            texto, itens = descrever(valor)
        variaveis.append((nome, texto, itens))
    return variaveis


# Um objeto de uma classe criada pelo próprio programa (a busca)
def objeto_do_programa(valor, globais):
    return type(valor).__module__ == globais.get("__name__") and not isinstance(valor, type)


# A foto de um momento do programa: a pilha de chamadas (a de cima é a que está rodando; a de baixo é o
# "programa", o nível de fora das funções) e os campos do objeto da busca (o self de quem estiver
# rodando ou, fora dos métodos, a variável do programa que guarda o objeto).
def tirar_foto_do_programa(quadro, globais, guardados):
    pilha = []
    objeto = None
    atual = quadro
    while atual is not None and atual.f_code.co_filename == NOME_DO_PROGRAMA:
        nome = atual.f_code.co_name
        if nome == "<module>":
            pilha.append({"funcao": "programa", "tipo": "programa", "linha": atual.f_lineno,
                          "variaveis": variaveis_do_programa(globais, guardados)})
        elif tipo_do_quadro(atual) == "classe":
            pilha.append({"funcao": nome, "tipo": "classe", "linha": atual.f_lineno, "variaveis": []})
        else:
            variaveis = []
            for nome_da_variavel, valor in atual.f_locals.items():
                if nome_da_variavel == "self":
                    if objeto is None:
                        objeto = valor
                else:
                    texto, itens = descrever(valor)
                    variaveis.append((nome_da_variavel, texto, itens))
            pilha.append({"funcao": nome, "tipo": "funcao", "linha": atual.f_lineno, "variaveis": variaveis})
        atual = atual.f_back
    if objeto is None:
        objeto = objeto_das_globais(globais)
    campos = []
    if objeto is not None:
        campos = tirar_foto_do_objeto(objeto)
    return {"pilha": pilha, "campos": campos}


# O objeto da busca nas variáveis do programa ("busca"), ou None se ele ainda não foi criado
def objeto_das_globais(globais):
    valor = globais.get("busca")
    if valor is not None and objeto_do_programa(valor, globais):
        return valor
    for valor in list(globais.values()):
        if objeto_do_programa(valor, globais):
            return valor
    return None


# "programa" (o nível de fora), "classe" (o corpo de uma classe sendo criada) ou "funcao"
def tipo_do_quadro(quadro):
    if quadro.f_code.co_name == "<module>":
        return "programa"
    if "__qualname__" in quadro.f_code.co_names and "__module__" in quadro.f_code.co_names:
        return "classe"
    return "funcao"


# Os parâmetros de uma função que acabou de ser chamada, em texto (sem o self)
def parametros_da_chamada(quadro):
    codigo = quadro.f_code
    quantos = codigo.co_argcount + codigo.co_kwonlyargcount
    parametros = []
    for nome in codigo.co_varnames[:quantos]:
        if nome == "self":
            continue
        valor = quadro.f_locals.get(nome)
        texto = formatar(valor)
        if len(texto) > 60:
            texto = texto[:59] + "…"
        parametros.append((nome, texto))
    return parametros


# Roda o programa inteiro com o rastro ligado. programa: o Python de exportacao/codigo_fonte, completado por
# estudo/estrutura.completar (o texto, as linhas e os rótulos). Devolve:
#   "passos_de_linha" -> um por passo, na ordem: {"linha" (a primeira linha do comando), "linhas" (todas as
#                        linhas do comando), "tipo" ("linha", "chamada", "volta", "comentario" ou "branco"),
#                        "rotulo", "proxima", "antes", "foto", "explicacao", "profundidade", "saida"}
#                        "saida" = quantos caracteres o programa já tinha escrito antes deste passo
#   "arquivo"         -> o programa (o mesmo dicionário que entrou)
#   "saida"           -> tudo o que o programa escreveu (o print)
#   "resposta", "busca", "foto_final" -> como em rastrear()
# estrito=True (nos testes): uma explicação que dê erro interrompe tudo, em vez de ficar vazia.
def rastrear_programa(programa, algoritmo, estrito=False):
    texto = programa["texto"]
    linhas = programa["linhas"]
    rotulos_da_linha = programa["rotulos_da_linha"]
    comando_da_linha = comandos_do_programa(texto)
    codigo = compile(texto, NOME_DO_PROGRAMA, "exec")
    escrito = []                                    # os pedaços de texto do print, na ordem
    tamanho = [0]                                   # quantos caracteres já foram escritos

    def imprimir(*valores, sep=" ", end="\n", file=None, flush=False):
        pedaco = sep.join(str(valor) for valor in valores) + end
        escrito.append(pedaco)
        tamanho[0] += len(pedaco)

    globais = {"__name__": "programa_do_boscograph", "print": imprimir}
    guardados = {}
    numero_do_quadro = {}                           # id do quadro -> um número (para juntar as linhas do mesmo)
    contador = [0]
    eventos = []                                    # (tipo, quadro, tipo do quadro, linha, profundidade, foto, explicação, saída)

    def rotulo_do_comando(inicio, fim):
        for linha in range(inicio, fim + 1):
            if rotulos_da_linha.get(linha):
                return rotulos_da_linha[linha][0]
        return None

    def explicar(evento, quadro, tipo, linha):
        try:
            if evento == "call":
                return explicacoes.explicar_chamada(quadro.f_code.co_name, parametros_da_chamada(quadro))
            inicio, fim = comando_da_linha.get(linha, (linha, linha))
            rotulo = rotulo_do_comando(inicio, fim)
            locais = quadro.f_locals
            if rotulo is not None and not explicacoes.rotulo_do_programa(rotulo):
                return explicacoes.explicar_linha(algoritmo, rotulo, locais, locais.get("self"), estrito)
            if rotulo is None:
                return "Roda esta linha."
            return explicacoes.explicar_linha_do_programa(rotulo, linhas[inicio - 1].strip(), locais,
                                                          em_classe=(tipo == "classe"))
        except Exception:
            if estrito:
                raise
            return ""

    def rastro(quadro, evento, argumento):
        if quadro.f_code.co_filename != NOME_DO_PROGRAMA:
            return None
        if evento == "call":
            numero_do_quadro[id(quadro)] = contador[0]
            contador[0] += 1
        if evento in ("call", "line", "return"):
            tipo = tipo_do_quadro(quadro)
            profundidade = 0
            atual = quadro
            while atual is not None and atual.f_code.co_filename == NOME_DO_PROGRAMA:
                profundidade += 1
                atual = atual.f_back
            explicacao = ""
            if evento == "line" or (evento == "call" and tipo == "funcao"):
                explicacao = explicar(evento, quadro, tipo, quadro.f_lineno)
            eventos.append((evento, numero_do_quadro.get(id(quadro)), tipo, quadro.f_lineno, profundidade,
                            tirar_foto_do_programa(quadro, globais, guardados), explicacao, tamanho[0]))
            if len(eventos) > LIMITE_DE_EVENTOS:
                raise RastroGrandeDemais(f"O programa passou de {LIMITE_DE_EVENTOS} passos: grande demais para "
                                         f"seguir linha a linha.")
        if evento == "return":
            numero_do_quadro.pop(id(quadro), None)
        return rastro

    antigo = sys.gettrace()
    sys.settrace(rastro)
    try:
        exec(codigo, globais)
    finally:
        sys.settrace(antigo)
    busca = objeto_das_globais(globais)
    saida = "".join(escrito)
    foto_final = {"pilha": [{"funcao": "programa", "tipo": "programa", "linha": len(linhas),
                             "variaveis": variaveis_do_programa(globais, guardados)}],
                  "campos": tirar_foto_do_objeto(busca) if busca is not None else []}
    corpo = ast.parse(texto).body
    fim_do_codigo = corpo[-1].end_lineno if corpo else 0         # a última linha do último comando do arquivo
    passos = montar_passos_do_programa(eventos, linhas, comando_da_linha, rotulos_da_linha, foto_final, len(saida),
                                       fim_do_codigo)
    explicar_os_print(passos, saida)
    return {"passos_de_linha": passos, "arquivo": programa, "saida": saida, "resposta": globais.get("resposta"),
            "busca": busca, "foto_final": foto_final}


# Os eventos do rastro viram os passos (veja rastrear_programa)
def montar_passos_do_programa(eventos, linhas, comando_da_linha, rotulos_da_linha, foto_final, tamanho_final,
                              fim_do_codigo):
    passos = []
    ultimo_fim = {}                 # quadro -> a última linha do último comando dele (de onde procurar comentários)
    ultimo_comando = {}             # quadro -> a primeira linha do último comando dele
    final_do_passo = []             # para cada passo: o índice do último evento que ele juntou

    def rotulo_de(inicio, fim):
        for linha in range(inicio, fim + 1):
            if rotulos_da_linha.get(linha):
                return rotulos_da_linha[linha][0]
        return None

    def acrescentar(tipo, inicio, fim, quadro, profundidade, foto, explicacao, saida, indice):
        passos.append({"linha": inicio, "linhas": list(range(inicio, fim + 1)), "tipo": tipo,
                       "rotulo": rotulo_de(inicio, fim), "antes": foto, "explicacao": explicacao,
                       "profundidade": profundidade, "saida": saida, "quadro": quadro})
        final_do_passo.append(indice)

    # Os comentários e as linhas em branco que ficam logo antes do comando que começa em "inicio" (e
    # depois da linha "comeco"), em ordem
    def lacuna(comeco, inicio):
        encontradas = []
        linha = inicio - 1
        while linha > comeco and comentario_ou_branco(linhas[linha - 1]):
            encontradas.append(linha)
            linha -= 1
        encontradas.reverse()
        return encontradas

    def acrescentar_lacuna(comeco, inicio, quadro, profundidade, foto, saida, indice):
        for linha in lacuna(comeco, inicio):
            tipo = "branco" if linhas[linha - 1].strip() == "" else "comentario"
            rotulo = rotulo_de(linha, linha)
            acrescentar(tipo, linha, linha, quadro, profundidade, foto_na_linha(foto, linha),
                        explicacoes.explicar_comentario(rotulo, linhas[linha - 1]), saida, indice - 1)

    for indice in range(len(eventos)):
        evento, quadro, tipo_do_quadro, linha, profundidade, foto, explicacao, saida = eventos[indice]
        if evento == "return":
            continue
        if evento == "call":
            if tipo_do_quadro == "programa":
                ultimo_fim[quadro] = 0              # o programa começa na linha 1 (comentários do topo incluídos)
            else:
                inicio, fim = comando_da_linha.get(linha, (linha, linha))
                ultimo_fim[quadro] = fim
                ultimo_comando[quadro] = inicio
                if tipo_do_quadro == "funcao":
                    acrescentar("chamada", inicio, fim, quadro, profundidade, foto, explicacao, saida, indice)
            continue
        inicio, fim = comando_da_linha.get(linha, (linha, linha))
        if tipo_do_quadro == "classe" and ultimo_comando.get(quadro) == inicio and ultimo_fim.get(quadro) == fim \
                and passos and passos[-1]["quadro"] != quadro:
            continue                                # a linha "class X:" de novo, já dentro do corpo da classe
        anterior = passos[-1] if passos else None
        if anterior is not None and anterior["quadro"] == quadro and anterior["linha"] == inicio and \
                anterior["tipo"] in ("linha", "volta"):
            final_do_passo[-1] = indice             # outra linha do mesmo comando: o mesmo passo
            continue
        if ultimo_comando.get(quadro) == inicio and anterior is not None and anterior["quadro"] != quadro:
            acrescentar("volta", inicio, fim, quadro, profundidade, foto,
                        explicacoes.explicar_volta(linhas[inicio - 1]), saida, indice)
        else:
            acrescentar_lacuna(ultimo_fim.get(quadro, 0), inicio, quadro, profundidade, foto, saida, indice)
            acrescentar("linha", inicio, fim, quadro, profundidade, foto, explicacao, saida, indice)
        ultimo_fim[quadro] = fim
        ultimo_comando[quadro] = inicio

    # O fim do arquivo: os comentários depois do último comando do programa (a saída esperada)
    for linha in range(fim_do_codigo + 1, len(linhas) + 1):
        if not comentario_ou_branco(linhas[linha - 1]):
            break
        tipo = "branco" if linhas[linha - 1].strip() == "" else "comentario"
        passos.append({"linha": linha, "linhas": [linha], "tipo": tipo, "rotulo": rotulo_de(linha, linha),
                       "antes": foto_na_linha(foto_final, linha),
                       "explicacao": explicacoes.explicar_comentario(rotulo_de(linha, linha),
                                                                                         linhas[linha - 1]),
                       "profundidade": 1, "saida": tamanho_final, "quadro": None})
        final_do_passo.append(len(eventos))
    # O passo seguinte e a foto "depois" de cada passo (a do evento seguinte ao último que ele juntou)
    for posicao in range(len(passos)):
        passo = passos[posicao]
        seguinte = final_do_passo[posicao] + 1
        passo["foto"] = eventos[seguinte][5] if seguinte < len(eventos) else foto_final
        passo["proxima"] = passos[posicao + 1]["linha"] if posicao + 1 < len(passos) else None
        del passo["quadro"]
    return passos


# A mesma foto, com a chamada de cima parada na linha dada (num comentário, a pilha mostra a linha dele)
def foto_na_linha(foto, linha):
    if not foto["pilha"]:
        return foto
    pilha = list(foto["pilha"])
    pilha[0] = dict(pilha[0])
    pilha[0]["linha"] = linha
    return {"pilha": pilha, "campos": foto["campos"]}


# Os print: a explicação diz o que a linha vai escrever (o texto que saiu entre este passo e o próximo
# passo do mesmo nível)
def explicar_os_print(passos, saida):
    for posicao in range(len(passos)):
        passo = passos[posicao]
        rotulo = passo["rotulo"] or ""
        if passo["tipo"] != "linha" or not rotulo.startswith("principal_escreve"):
            continue
        fim = len(saida)
        for seguinte in range(posicao + 1, len(passos)):
            outro = passos[seguinte]
            # (a volta para o mesmo print, depois de uma chamada no meio dele, ainda é o mesmo print)
            if outro["profundidade"] <= passo["profundidade"] and \
                    not (outro["tipo"] == "volta" and outro["linha"] == passo["linha"]):
                fim = outro["saida"]
                break
        escrito = saida[passo["saida"]:fim].rstrip("\n")
        if escrito:
            passo["explicacao"] = "Escreve na saída: " + escrito.replace("\n", " | ")


# Liga os passos da busca (os do BoscoGraph, que desenham a tela) aos passos de linha.
# Cada passo da busca tem a chave do trecho (perfis.chave_do_trecho: "descobrir", "relaxar_nao"...);
# no código de estudo, a linha com esse rótulo é a que faz aquele passo. Indo em ordem, cada passo
# casa com a PRÓXIMA execução dessa linha. Os passos que não são da busca (montar o grafo, a etapa 6)
# não têm rótulo e ficam de fora.
# Devolve {índice do passo: índice do passo de linha}. Se algum passo não achar a linha, ValueError:
# seria um erro no código de estudo (os testes conferem isso em centenas de grafos).
def sincronizar(passos, passos_de_linha, rotulo_da_linha, chave_do_trecho):
    rotulos = set(rotulo_da_linha.values())
    casamento = {}
    proximo = 0
    for indice in range(len(passos)):
        chave = chave_do_trecho(passos[indice])
        if chave not in rotulos:
            continue
        achou = None
        for j in range(proximo, len(passos_de_linha)):
            if passos_de_linha[j]["rotulo"] == chave and passos_de_linha[j].get("tipo", "linha") == "linha":
                achou = j
                break
        if achou is None:
            raise ValueError(f"O passo '{chave}' (nº {indice + 1}) não aparece no código de estudo.")
        casamento[indice] = achou
        proximo = achou + 1
    return casamento
