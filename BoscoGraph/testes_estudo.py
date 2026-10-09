'''
    Conferências do código de estudo (pasta estudo/), sem abrir janela.
    Rode com: python testes_estudo.py   (o testes.py também chama este arquivo)

    1. O Python de estudo faz EXATAMENTE a mesma busca que o BoscoGraph: em centenas de grafos sorteados,
       cada passo da busca casa com a linha certa do código de estudo, na mesma ordem e com os mesmos
       vértices, e o estado final (cores, distâncias, pais) é igual.
    2. Os rótulos de linha batem entre as linguagens (veja conferir_rotulos).
    3. As traduções (Java, C, C++, JavaScript) compilam e dão o mesmo resultado que o Python
       (só roda com os compiladores instalados; veja conferir_traducoes).
    4. O programa INTEIRO (o modo linha a linha da tela roda o arquivo todo, desde a linha 1): os passos
       começam no cabeçalho, toda linha do nível de fora passa, comentários e linhas em branco do caminho
       também viram passos, toda linha executada tem rótulo e explicação, a busca casa com os passos do
       BoscoGraph, o print escreve a saída esperada, e as outras linguagens têm os mesmos rótulos.
'''

import random
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

import algoritmos
import entrada
import estudo
from boscograph import montar_passos
from classes.a_estrela import AEstrela
from classes.aprofundamento_iterativo import AprofundamentoIterativo
from classes.bellman_ford import BellmanFord
from classes.busca_bidirecional import BuscaBidirecional
from classes.busca_em_largura import BuscaEmLargura
from classes.busca_em_profundidade import BuscaEmProfundidade
from classes.busca_gulosa import BuscaGulosa
from classes.busca_limitada import BuscaEmProfundidadeLimitada
from classes.dijkstra import Dijkstra
from classes.floyd_warshall import FloydWarshall
from classes.kruskal import Kruskal
from classes.prim import Prim
from estudo import estrutura, rastreador
from exportacao import codigo_fonte
from visual import perfis

CHAVES = [informacoes["chave"] for informacoes in algoritmos.ALGORITMOS]
TIPOS_DA_MONTAGEM = {"criar_vertice", "criar_aresta", "criar_lista", "adicionar_vizinho", "ordenar", "sem_ordenar"}

# Que variável do código de estudo (na linha do passo, antes de ela rodar) tem que bater com que
# campo do passo do BoscoGraph. Ex.: na linha "@descobrir", a variável u é o vértice descoberto.
ARGUMENTOS = {
    "pintar_branco": {"u": "vertice"}, "nova_arvore": {"u": "vertice"}, "descobrir": {"u": "vertice"},
    "finalizar": {"u": "vertice"}, "examinar_arvore": {"u": "origem", "v": "destino"},
    "examinar_outra": {"u": "origem", "v": "destino"}, "revisitar": {"u": "origem", "v": "destino"},
    "inicializar": {"v": "vertice"}, "terminar_vertice": {"u": "vertice"}, "extrair": {"u": "vertice"},
    "descobrir_vizinho": {"u": "origem", "v": "destino"}, "ignorar_vizinho": {"u": "origem", "v": "destino"},
    "relaxar_melhorou": {"u": "origem", "v": "destino"}, "relaxar_nao": {"u": "origem", "v": "destino"},
    "relaxar_reabriu": {"u": "origem", "v": "destino"}, "chegou": {"u": "vertice"},
    # Versão 6: busca limitada, aprofundamento iterativo, bidirecional e Floyd-Warshall
    "entrar": {"u": "vertice"}, "corte": {"u": "vertice"}, "subir": {"u": "vertice"},
    "encontro": {"u": "origem", "v": "destino"}, "origem_tras": {"t": "vertice"},
    "inicializar_linha": {"i": "vertice"}, "arco_melhorou": {"u": "origem", "v": "destino"},
    "arco_nao": {"u": "origem", "v": "destino"}, "par_melhorou": {"i": "i", "j": "j", "k": "k"},
    "par_nao": {"i": "i", "j": "j", "k": "k"},
    # Versão 7.3: Prim e Kruskal
    "raiz": {"r": "vertice"}, "atualizar_melhorou": {"u": "origem", "v": "destino"},
    "atualizar_nao": {"u": "origem", "v": "destino"}, "criar_conjunto": {"v": "vertice"},
    "aceitar": {"u": "origem", "v": "destino"}, "rejeitar": {"u": "origem", "v": "destino"},
    "unir": {"u": "origem", "v": "destino"},
}

# As buscas que podem ter peso negativo nos grafos sorteados (a árvore mínima aceita peso negativo)
COM_NEGATIVOS = (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL, algoritmos.PRIM, algoritmos.KRUSKAL)

# O tipo da aresta no BoscoGraph ("avanco") e no código de estudo ("avanço")
COM_ACENTO = {"arvore": "árvore", "retorno": "retorno", "avanco": "avanço", "cruzamento": "cruzamento"}


# Um grafo sorteado que a busca aceita (pesos quando precisa, destino e heurística quando precisa).
#   so_inteiros -> sem pesos decimais (as traduções usam double, que não soma 0,1 + 0,2 exatamente)
#   empates     -> grafo mais cheio, com pesos e h de 0 a 2: muitos empates na fila de prioridade e
#                  muitos caminhos de mesmo custo. Assim, uma tradução que desempatasse diferente (ou
#                  tirasse da fila em outra ordem) daria outro pai no fim, e o teste perceberia.
# Devolve (vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite); o limite só vale na
# busca limitada. Na limitada e na iterativa, um grafo com árvore de busca grande demais é sorteado de novo.
def grafo_sorteado(sorteio, algoritmo, so_inteiros=False, empates=False):
    while True:
        grafo = sortear_um_grafo(sorteio, algoritmo, so_inteiros, empates)
        vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo
        problemas, avisos = algoritmos.conferir(algoritmo, vertices, arestas, direcionado, inicio, destino,
                                                heuristica, limite, ordenar)
        if not problemas:
            return grafo


def sortear_um_grafo(sorteio, algoritmo, so_inteiros, empates):
    direcionado = sorteio.random() < 0.6
    if algoritmos.algoritmo(algoritmo).get("so_nao_orientado"):
        direcionado = False             # a árvore geradora mínima só existe no não orientado
    n = sorteio.randint(4, 8) if empates else sorteio.randint(1, 8)
    vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "prefixo"]), "V")
    maximo = min(20 if empates else 14, entrada.maximo_de_arestas(n, True, True, direcionado))
    m = sorteio.randint(n if empates else 0, maximo)
    arestas = entrada.arestas_aleatorias(vertices, m, sorteio.random() < 0.4, sorteio.random() < 0.3,
                                         sorteio.randint(0, 10 ** 6), direcionado)
    pesos = []
    for i in range(len(arestas)):
        if empates:
            pesos.append(Decimal(sorteio.randint(-1 if algoritmo in COM_NEGATIVOS else 0, 2)))
        elif algoritmo in COM_NEGATIVOS:
            pesos.append(Decimal(sorteio.randint(-3, 9)))
        elif sorteio.random() < 0.2 and not so_inteiros:
            pesos.append(Decimal(sorteio.randint(1, 30)) / 10)         # 0,1 a 3: decimais exatos
        else:
            pesos.append(Decimal(sorteio.randint(0, 9)))
    arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
    heuristica = {}
    for vertice in vertices:
        heuristica[vertice] = Decimal(sorteio.randint(0, 2 if empates else 9))
    inicio = sorteio.choice(vertices)
    destino = sorteio.choice(vertices)
    ordenar = sorteio.random() < 0.7
    limite = None
    if algoritmo == algoritmos.LIMITADA:
        limite = sorteio.randint(0, 4)
        if sorteio.random() < 0.25:
            destino = None                              # sem destino: explora até o limite
    return vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite


# Um grafo em que o A* REABRE um vértice (a heurística não é consistente). Nos grafos sorteados
# isso quase nunca acontece (medido: 0 em 300), e esse caminho do código ficaria sem teste.
# O molde, com os papéis s, a, b, c, t sorteados entre os nomes:
#     s -> b (peso 1),  s -> a (1),  b -> c (3 a 5),  a -> c (1),  c -> t (8 a 12)
#     h(b) = h(c) = h(t) = 0  e  h(a) de 6 a 9 (bem maior que o custo real de a até t)
# O c sai da fronteira pelo caminho caro (via b, f = 4 a 6) antes do a (f = 7 a 10); depois o a acha
# um caminho mais barato até o c (g = 2), e o c volta para a fronteira. Por cima, alguns vértices e
# arestas sorteados, que às vezes desmancham o molde (os testes contam quantos reabriram de fato).
def grafo_que_reabre(sorteio):
    vertices = entrada.nomes_dos_vertices(sorteio.randint(5, 8), "letras", "V")
    s, a, b, c, t = sorteio.sample(vertices, 5)
    direcionado = sorteio.random() < 0.7
    arestas = [(s, b, "", Decimal(1)), (s, a, "", Decimal(1)), (b, c, "", Decimal(sorteio.randint(3, 5))),
               (a, c, "", Decimal(1)), (c, t, "", Decimal(sorteio.randint(8, 12)))]
    for i in range(sorteio.randint(0, 4)):
        u, v = sorteio.sample(vertices, 2)
        arestas.append((u, v, "", Decimal(sorteio.randint(2, 9))))
    sorteio.shuffle(arestas)
    heuristica = {}
    for vertice in vertices:
        heuristica[vertice] = Decimal(sorteio.randint(0, 9))
    heuristica[b] = heuristica[c] = heuristica[t] = Decimal(0)
    heuristica[a] = Decimal(sorteio.randint(6, 9))
    ordenar = sorteio.random() < 0.7
    return vertices, arestas, ordenar, s, direcionado, t, heuristica, None


# O estado final da busca do BoscoGraph (rodando as classes de verdade) para comparar com o de estudo
def busca_do_boscograph(algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino, heuristica,
                        limite=None):
    grafo, origem = rastreador.montar_entrada(vertices, arestas, ordenar, inicio, direcionado)
    if algoritmo == algoritmos.LIMITADA:
        busca = BuscaEmProfundidadeLimitada(grafo, [])
        busca.buscar(origem, destino, limite)
    elif algoritmo == algoritmos.ITERATIVA:
        busca = AprofundamentoIterativo(grafo, [])
        busca.buscar(origem, destino)
    elif algoritmo == algoritmos.BIDIRECIONAL:
        busca = BuscaBidirecional(grafo, [])
        busca.buscar(origem, destino)
    elif algoritmo == algoritmos.FLOYD_WARSHALL:
        busca = FloydWarshall(grafo, [])
        busca.floyd_warshall()
    elif algoritmo == algoritmos.PROFUNDIDADE:
        busca = BuscaEmProfundidade(grafo, [])
        busca.dfs(inicio if inicio in vertices else None)
    elif algoritmo == algoritmos.LARGURA:
        busca = BuscaEmLargura(grafo, [])
        busca.bfs(origem)
    elif algoritmo == algoritmos.DIJKSTRA:
        busca = Dijkstra(grafo, [])
        busca.dijkstra(origem)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        busca = BellmanFord(grafo, [])
        busca.bellman_ford(origem)
    elif algoritmo == algoritmos.GULOSA:
        busca = BuscaGulosa(grafo, [], heuristica)
        busca.buscar(origem, destino)
    elif algoritmo == algoritmos.PRIM:
        busca = Prim(grafo, [])
        busca.prim(origem)
    elif algoritmo == algoritmos.KRUSKAL:
        busca = Kruskal(grafo, [])
        busca.kruskal()
        # As arestas aceitas como o código de estudo guarda: (u, v, peso)
        busca.arvore = [(grafo.arestas[i].vertice_origem.nome, grafo.arestas[i].vertice_destino.nome,
                         grafo.arestas[i].peso) for i in busca.arvore]
    else:
        busca = AEstrela(grafo, [], heuristica)
        busca.buscar(origem, destino)
    return busca


# Confere um grafo: o Python de estudo faz a mesma busca que o BoscoGraph.
# Devolve o rastro (as linhas executadas) e os passos do BoscoGraph.
def conferir_um_grafo(algoritmo, grafo):
    vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo
    descricao = (algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite)
    passos = montar_passos(vertices, arestas, ordenar, inicio, direcionado, algoritmo, destino, heuristica, limite)
    # estrito: a explicação de cada linha (estudo/explicacoes.py) tem que funcionar em todas as linhas
    rastro = rastreador.rastrear(algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino, heuristica,
                                 estrito=True, limite=limite)
    rotulo_da_linha = rastro["arquivo"]["rotulo_da_linha"]
    for passo_de_linha in rastro["passos_de_linha"]:
        assert passo_de_linha["explicacao"], (algoritmo, passo_de_linha["rotulo"])
    casamento = rastreador.sincronizar(passos, rastro["passos_de_linha"], rotulo_da_linha, perfis.chave_do_trecho)
    # Todo passo da busca (etapa 5) casou com uma linha
    for indice in range(len(passos)):
        tipo = passos[indice]["tipo"]
        da_busca = tipo not in TIPOS_DA_MONTAGEM and not tipo.startswith("tipo_") and \
            not tipo.startswith("resultado_") and tipo != "ordem_topologica"
        assert (indice in casamento) == da_busca, (descricao, indice, tipo)
    # Toda linha executada tem rótulo (para achar a mesma linha nas outras linguagens)
    for passo_de_linha in rastro["passos_de_linha"]:
        assert passo_de_linha["linha"] in rotulo_da_linha, (algoritmo, passo_de_linha["linha"])
    # Os vértices de cada passo são os das variáveis na linha casada
    for indice in casamento:
        passo = passos[indice]
        chave = perfis.chave_do_trecho(passo)
        variaveis = {}
        for nome, texto, itens in rastro["passos_de_linha"][casamento[indice]]["antes"]["pilha"][0]["variaveis"]:
            variaveis[nome] = texto
        for variavel, campo in ARGUMENTOS.get(chave, {}).items():
            assert variaveis[variavel] == f"'{passo[campo]}'", (descricao, chave, variavel, variaveis)
    # O estado final é o mesmo
    nosso = busca_do_boscograph(algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino, heuristica,
                                limite)
    deles = rastro["busca"]
    campos = ("cor", "d", "f", "g", "pai", "chave", "conjunto", "arvore")
    if algoritmo == algoritmos.BELLMAN_FORD and nosso.ciclo_negativo is not None:
        # Achado o ciclo negativo, o BoscoGraph continua relaxando "escondido" para mostrar o
        # ciclo; o de estudo para na hora, como o livro (devolve False). As distâncias não valem.
        campos = ()
    for campo in campos:
        if hasattr(deles, campo) and hasattr(nosso, campo):
            esperado = getattr(nosso, campo)
            obtido = getattr(deles, campo)
            if isinstance(esperado, dict):
                esperado = dict(esperado)
                obtido = dict(obtido)
            if campo == "pai":
                # O BoscoGraph só cria pai para quem foi alcançado; o estudo começa todos com None
                for vertice in obtido:
                    esperado.setdefault(vertice, None)
            if campo == "cor" and algoritmo == algoritmos.BELLMAN_FORD:
                continue                    # o Bellman-Ford de estudo não usa cores (o livro também não)
            assert obtido == esperado, (descricao, campo, obtido, esperado)
    if algoritmo == algoritmos.BELLMAN_FORD:
        assert rastro["resposta"] == (nosso.ciclo_negativo is None), descricao
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        assert rastro["resposta"] == nosso.chegou, descricao
    if algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        assert rastro["resposta"] == nosso.resultado, descricao
        assert deles.cortados == nosso.cortados, descricao
        if nosso.resultado == "achou":
            assert deles.caminho == nosso.caminho, descricao
    if algoritmo == algoritmos.BIDIRECIONAL:
        assert rastro["resposta"] == (nosso.caminho is not None), descricao
    if algoritmo == algoritmos.FLOYD_WARSHALL:
        assert rastro["resposta"] == (not nosso.ciclo_negativo), descricao
        assert deles.pi == nosso.pi, descricao
    if algoritmo == algoritmos.PROFUNDIDADE:
        # O tipo de cada aresta: o mesmo que o BoscoGraph mostra (na mesma ordem: fica o último)
        tipos = {}
        for passo in passos:
            if passo["tipo"] == "examinar":
                tipos[(passo["origem"], passo["destino"])] = COM_ACENTO[passo["classe"]]
        assert deles.tipo == tipos, (descricao, deles.tipo, tipos)
    return rastro, passos


def conferir_mesma_busca(quantidade_por_busca):
    sorteio = random.Random(31)
    linhas = 0
    executados = {}                         # os rótulos que rodaram ao menos uma vez, por busca
    for algoritmo in CHAVES:
        executados[algoritmo] = set()
        grafos = []
        for rodada in range(quantidade_por_busca):
            grafos.append(grafo_sorteado(sorteio, algoritmo))
        reabriram = 0
        if algoritmo == algoritmos.A_ESTRELA:
            # Mais uns grafos em que o A* reabre vértices (nos sorteados isso quase nunca acontece)
            for rodada in range(quantidade_por_busca // 2):
                grafos.append(grafo_que_reabre(sorteio))
        for grafo in grafos:
            rastro, passos = conferir_um_grafo(algoritmo, grafo)
            linhas += len(rastro["passos_de_linha"])
            rotulo_da_linha = rastro["arquivo"]["rotulo_da_linha"]
            for passo_de_linha in rastro["passos_de_linha"]:
                executados[algoritmo].add(rotulo_da_linha[passo_de_linha["linha"]])
            for passo in passos:
                if passo.get("reabriu"):
                    reabriram += 1
                    break
        if algoritmo == algoritmos.A_ESTRELA:
            assert reabriram >= quantidade_por_busca // 4, reabriram
        # Cobertura: TODA linha do código de estudo rodou em algum grafo (nenhum caminho ficou sem teste)
        todos = set(estudo.carregar(algoritmo, "python")["linhas_do_rotulo"])
        assert executados[algoritmo] == todos, (algoritmo, "nunca rodaram:", sorted(todos - executados[algoritmo]))
    print(f"11a. Código de estudo em Python: mesma busca que o BoscoGraph em {quantidade_por_busca} grafos de "
          f"cada busca (+{quantidade_por_busca // 2} do A* reabrindo vértices); {linhas} linhas executadas, todas "
          f"com rótulo, e todas as linhas do código de estudo rodaram")


# ----------------------------------------------------------------------
# 2. Os rótulos de linha batem entre as linguagens
# ----------------------------------------------------------------------

def conferir_rotulos():
    for algoritmo in CHAVES:
        python = estudo.carregar(algoritmo, "python")
        esperados = set(python["linhas_do_rotulo"])
        # No Python, cada rótulo marca UMA linha: é ela que roda e para no modo linha a linha
        for rotulo in python["linhas_do_rotulo"]:
            assert len(python["linhas_do_rotulo"][rotulo]) == 1, (algoritmo, rotulo)
        for informacoes in estudo.LINGUAGENS:
            arquivo = estudo.carregar(algoritmo, informacoes["chave"])
            obtidos = set(arquivo["linhas_do_rotulo"])
            assert obtidos == esperados, (algoritmo, informacoes["chave"], "faltam", sorted(esperados - obtidos),
                                          "sobram", sorted(obtidos - esperados))
            # Nenhum rótulo mal escrito ficou aparecendo na tela (como "// @Descobrir" ou "//@ x")
            comentario = informacoes["comentario"]
            for numero, linha in enumerate(arquivo["linhas"], start=1):
                assert re.search(re.escape(comentario) + r"\s*@", linha) is None, \
                    (algoritmo, informacoes["chave"], numero, linha)
    print(f"11b. Rótulos de linha: as {len(estudo.LINGUAGENS)} linguagens marcam as mesmas linhas nas "
          f"{len(CHAVES)} buscas")


# ----------------------------------------------------------------------
# 3. As traduções compilam (sem nenhum aviso) e dão o mesmo resultado que o Python
# ----------------------------------------------------------------------

PASTA_DA_CONFERENCIA = estudo.PASTA_DO_ESTUDO / "conferencia"


# Um número como as traduções escrevem: "inf" para o infinito, inteiros sem casas decimais
def texto_do_numero(valor):
    if valor is None:
        return "NIL"
    valor = Decimal(valor)
    if valor.is_infinite():
        return "inf" if valor > 0 else "-inf"
    if valor == valor.to_integral_value():
        return str(int(valor))
    return repr(float(valor))


# A entrada das traduções: palavras separadas por espaço, um grafo atrás do outro:
#   busca  n  nome_1 ... nome_n  orientado (0/1)  origem  destino (-1 = nenhum)  h_1 ... h_n
#   para cada vértice u, na ordem: k  v_1 peso_1 ... v_k peso_k     (a lista de adjacência de u)
#   a  u_1 v_1 peso_1 ... u_a v_a peso_a                            (os arcos do Bellman-Ford e do Floyd-Warshall)
#   ordem_1 ... ordem_n                                             (as raízes da DFS)
#   limite (-1 = nenhum)                                            (a busca limitada; versão 6)
#   para cada vértice v, na ordem: k  u_1 peso_1 ... u_k peso_k     (quem CHEGA em v: a lista ao contrário
#                                                                    da busca bidirecional; versão 6)
#   m  u_1 v_1 peso_1 ... u_m v_m peso_m                            (as arestas uma vez cada: o Kruskal; 7.3)
# Os vértices vão pelo número (a posição na lista de nomes); um peso que falta vai como 0.
def entrada_das_traducoes(algoritmo, entrada, direcionado, destino, heuristica, limite=None):
    nomes = list(entrada["vizinhos"])
    numero = {}
    for indice in range(len(nomes)):
        numero[nomes[indice]] = indice
    palavras = [algoritmo, str(len(nomes))] + nomes
    palavras += ["1" if direcionado else "0", str(numero[entrada["origem"]]),
                 str(numero[destino]) if destino in numero else "-1"]
    for nome in nomes:
        palavras.append(texto_do_numero(heuristica.get(nome, 0)))
    for nome in nomes:
        lista = entrada["com_pesos"][nome]
        palavras.append(str(len(lista)))
        for vizinho, peso in lista:
            palavras += [str(numero[vizinho]), texto_do_numero(peso if peso is not None else 0)]
    palavras.append(str(len(entrada["arcos"])))
    for u, v, peso in entrada["arcos"]:
        palavras += [str(numero[u]), str(numero[v]), texto_do_numero(peso if peso is not None else 0)]
    for nome in entrada["ordem"]:
        palavras.append(str(numero[nome]))
    palavras.append(str(limite) if limite is not None else "-1")
    for nome in nomes:
        lista = entrada["com_pesos_tras"][nome]
        palavras.append(str(len(lista)))
        for vizinho, peso in lista:
            palavras += [str(numero[vizinho]), texto_do_numero(peso if peso is not None else 0)]
    palavras.append(str(len(entrada["arestas"])))
    for u, v, peso in entrada["arestas"]:
        palavras += [str(numero[u]), str(numero[v]), texto_do_numero(peso if peso is not None else 0)]
    return " ".join(palavras)


# O estado final da busca de estudo em Python, no formato que as traduções escrevem.
# Uma linha por informação, em qualquer ordem (as duas listas são comparadas em ordem alfabética):
#   todas menos as da versão 6 -> "cor v X", "d v X" / "g v X" / "f v X", "pai v X", "tipo u v X", "resposta X"
#   limitada e iterativa -> "cor v X", "pai v X", "prof v X" (só quem entrou no caminho), "caminho v1 v2 ...",
#                           "cortados v1 v2 ...", "resposta achou|corte|falha"
#   bidirecional         -> "cor v X", "lado v frente|tras|NIL", "d v X", "d_tras v X", "pai v X", "pai_tras v X",
#                           "encontro u v" (se houver), "resposta true|false"
#   floyd_warshall       -> "d i j X" e "pi i j X" para todo par, "resposta true|false"
#   prim                 -> "cor v X", "chave v X", "pai v X"
#   kruskal              -> "conjunto v X" e "arvore i u v peso" (i = a ordem em que a aresta entrou)
# Números como em texto_do_numero (inf, inteiros sem casas); vértices pelo nome; nenhum = NIL.
def saida_do_python(algoritmo, nomes, busca, resposta):
    if algoritmo == algoritmos.PRIM:
        linhas = []
        for v in nomes:
            linhas += [f"cor {v} {busca.cor[v]}", f"chave {v} {texto_do_numero(busca.chave[v])}",
                       f"pai {v} {nome_ou_nil(busca.pai[v])}"]
        return sorted(linhas)
    if algoritmo == algoritmos.KRUSKAL:
        linhas = [f"conjunto {v} {busca.conjunto[v]}" for v in nomes]
        for i, (u, v, peso) in enumerate(busca.arvore):
            linhas.append(f"arvore {i} {u} {v} {texto_do_numero(peso)}")
        return sorted(linhas)
    if algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA, algoritmos.BIDIRECIONAL, algoritmos.FLOYD_WARSHALL):
        return saida_das_buscas_novas(algoritmo, nomes, busca, resposta)
    linhas = []
    for v in nomes:
        if algoritmo != algoritmos.BELLMAN_FORD:
            linhas.append(f"cor {v} {busca.cor[v]}")
        if algoritmo == algoritmos.A_ESTRELA:
            linhas.append(f"g {v} {texto_do_numero(busca.g[v])}")
            linhas.append(f"f {v} {texto_do_numero(busca.f[v])}")
        elif algoritmo != algoritmos.GULOSA:
            linhas.append(f"d {v} {texto_do_numero(busca.d[v])}")
        if algoritmo == algoritmos.PROFUNDIDADE:
            linhas.append(f"f {v} {texto_do_numero(busca.f[v])}")
        linhas.append(f"pai {v} {texto_do_numero(busca.pai[v]) if busca.pai[v] is None else busca.pai[v]}")
    if algoritmo == algoritmos.PROFUNDIDADE:
        for (u, v), tipo in busca.tipo.items():
            linhas.append(f"tipo {u} {v} {tipo}")
    if algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.GULOSA, algoritmos.A_ESTRELA):
        linhas.append(f"resposta {'true' if resposta else 'false'}")
    return sorted(linhas)


def nome_ou_nil(valor):
    if valor is None:
        return "NIL"
    return valor


def saida_das_buscas_novas(algoritmo, nomes, busca, resposta):
    linhas = []
    if algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        for v in nomes:
            linhas.append(f"cor {v} {busca.cor[v]}")
            linhas.append(f"pai {v} {nome_ou_nil(busca.pai[v])}")
            if v in busca.prof:
                linhas.append(f"prof {v} {busca.prof[v]}")
        linhas.append("caminho " + " ".join(busca.caminho) if busca.caminho else "caminho")
        linhas.append("cortados " + " ".join(busca.cortados) if busca.cortados else "cortados")
        linhas.append(f"resposta {resposta}")
    elif algoritmo == algoritmos.BIDIRECIONAL:
        for v in nomes:
            linhas.append(f"cor {v} {busca.cor[v]}")
            linhas.append(f"lado {v} {nome_ou_nil(busca.lado[v])}")
            linhas.append(f"d {v} {texto_do_numero(busca.d[v])}")
            linhas.append(f"d_tras {v} {texto_do_numero(busca.d_tras[v])}")
            linhas.append(f"pai {v} {nome_ou_nil(busca.pai[v])}")
            linhas.append(f"pai_tras {v} {nome_ou_nil(busca.pai_tras[v])}")
        if busca.encontro is not None:
            linhas.append(f"encontro {busca.encontro[0]} {busca.encontro[1]}")
        linhas.append(f"resposta {'true' if resposta else 'false'}")
    else:
        for i in nomes:
            for j in nomes:
                linhas.append(f"d {i} {j} {texto_do_numero(busca.d[i][j])}")
                linhas.append(f"pi {i} {j} {nome_ou_nil(busca.pi[i][j])}")
        linhas.append(f"resposta {'true' if resposta else 'false'}")
    return sorted(linhas)


# Roda um programa com a entrada dada; devolve a saída, um grafo por item (cada um termina em "fim")
def rodar_programa(comando, entrada, pasta):
    resultado = subprocess.run(comando, input=entrada.encode("utf-8"), capture_output=True, cwd=pasta,
                               timeout=300)
    assert resultado.returncode == 0, (comando, resultado.stderr.decode("utf-8", "replace")[-2000:])
    grafos = []
    atual = []
    for linha in resultado.stdout.decode("utf-8").splitlines():
        if linha.strip() == "fim":
            grafos.append(sorted(atual))
            atual = []
        elif linha.strip():
            atual.append(linha.strip())
    return grafos


def compilar(comando, pasta):
    resultado = subprocess.run(comando, capture_output=True, cwd=pasta, timeout=300)
    saida = (resultado.stdout + resultado.stderr).decode("utf-8", "replace")
    # O Java avisa no erro padrão quando há JAVA_TOOL_OPTIONS: isso não é um aviso da compilação
    avisos = [linha for linha in saida.splitlines() if linha.strip() and "JAVA_TOOL_OPTIONS" not in linha]
    assert resultado.returncode == 0 and not avisos, (comando, saida[-3000:])


def copiar(origens, destino):
    destino.mkdir(parents=True, exist_ok=True)
    for origem in origens:
        shutil.copy(origem, destino / origem.name)


# Cada linguagem: (nome, programas que precisa, função que compila e roda, devolvendo as saídas)
def rodar_java(pasta, entrada, algoritmos_dos_casos):
    copiar(list((estudo.PASTA_DO_ESTUDO / "java").glob("*.java")) + [PASTA_DA_CONFERENCIA / "Principal.java"],
           pasta)
    arquivos = sorted(caminho.name for caminho in pasta.glob("*.java"))
    compilar(["javac", "-encoding", "UTF-8", "-Xlint:all", "-Werror", "-d", "classes"] + arquivos, pasta)
    return rodar_programa(["java", "-cp", "classes", "Principal"], entrada, pasta)


def rodar_c(pasta, entrada, algoritmos_dos_casos):
    copiar(list((estudo.PASTA_DO_ESTUDO / "c").glob("*.c")) + [PASTA_DA_CONFERENCIA / "principal.c"], pasta)
    # Cada busca num programa (as globais têm o mesmo nome): roda os grafos de cada uma separado
    saidas = {}
    casos = entrada.split("\n")
    for algoritmo in CHAVES:
        programa = "busca_" + algoritmo + (".exe" if sys.platform.startswith("win") else "")
        compilar(["gcc", "-std=c11", "-Wall", "-Wextra", "-pedantic", "-Werror", "-O2",
                  "-D" + algoritmo.upper(), "-o", programa, "principal.c", "-lm"], pasta)
        meus = [casos[i] for i in range(len(casos)) if algoritmos_dos_casos[i] == algoritmo]
        saidas[algoritmo] = rodar_programa([str(pasta / programa)], "\n".join(meus), pasta)
    grafos = []
    proximo = dict.fromkeys(CHAVES, 0)
    for algoritmo in algoritmos_dos_casos:
        grafos.append(saidas[algoritmo][proximo[algoritmo]])
        proximo[algoritmo] += 1
    return grafos


def rodar_cpp(pasta, entrada, algoritmos_dos_casos):
    copiar(list((estudo.PASTA_DO_ESTUDO / "cpp").glob("*.cpp")) + [PASTA_DA_CONFERENCIA / "principal.cpp"],
           pasta)
    programa = "buscas" + (".exe" if sys.platform.startswith("win") else "")
    compilar(["g++", "-std=c++17", "-Wall", "-Wextra", "-pedantic", "-Werror", "-O2", "-o", programa,
              "principal.cpp"], pasta)
    return rodar_programa([str(pasta / programa)], entrada, pasta)


def rodar_javascript(pasta, entrada, algoritmos_dos_casos):
    copiar(list((estudo.PASTA_DO_ESTUDO / "javascript").glob("*.js")) + [PASTA_DA_CONFERENCIA / "principal.js"],
           pasta)
    return rodar_programa(["node", "principal.js"], entrada, pasta)


TRADUCOES = [
    ("Java", ["javac", "java"], rodar_java),
    ("C", ["gcc"], rodar_c),
    ("C++", ["g++"], rodar_cpp),
    ("JavaScript", ["node"], rodar_javascript),
]


def conferir_traducoes(quantidade_por_busca):
    sorteio = random.Random(57)
    entradas = []
    esperadas = []
    algoritmos_dos_casos = []
    for algoritmo in CHAVES:
        for rodada in range(quantidade_por_busca):
            if algoritmo == algoritmos.A_ESTRELA and rodada % 3 == 2:
                grafo = grafo_que_reabre(sorteio)
            else:
                grafo = grafo_sorteado(sorteio, algoritmo, so_inteiros=True, empates=rodada % 2 == 1)
            vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo
            entrada = rastreador.preparar_entrada(vertices, arestas, ordenar, inicio, direcionado)
            arquivo, busca, executar = rastreador.criar_busca(algoritmo, entrada, direcionado, destino, heuristica,
                                                              limite)
            resposta = executar()
            entradas.append(entrada_das_traducoes(algoritmo, entrada, direcionado, destino, heuristica, limite))
            esperadas.append(saida_do_python(algoritmo, list(entrada["vizinhos"]), busca, resposta))
            algoritmos_dos_casos.append(algoritmo)
    conferidas = []
    puladas = []
    for nome, programas, rodar_traducao in TRADUCOES:
        faltando = [programa for programa in programas if shutil.which(programa) is None]
        if faltando:
            puladas.append(f"{nome} (sem {', '.join(faltando)})")
            continue
        with tempfile.TemporaryDirectory() as pasta:
            obtidas = rodar_traducao(Path(pasta), "\n".join(entradas), algoritmos_dos_casos)
        assert len(obtidas) == len(esperadas), (nome, len(obtidas), len(esperadas))
        for indice in range(len(esperadas)):
            assert obtidas[indice] == esperadas[indice], (nome, algoritmos_dos_casos[indice], entradas[indice],
                                                          "obtido", obtidas[indice], "esperado", esperadas[indice])
        conferidas.append(nome)
    texto = f"11c. Traduções: {', '.join(conferidas) or 'nenhuma'} compilam sem avisos e dão o mesmo resultado " \
            f"que o Python em {quantidade_por_busca} grafos de cada busca"
    if puladas:
        texto += f" (não conferidas: {'; '.join(puladas)})"
    print(texto)


# ----------------------------------------------------------------------
# 4. O programa inteiro (o modo linha a linha da tela)
# ----------------------------------------------------------------------

# Os rótulos do Python que cada linguagem pode não ter (o resto ela tem que ter: é por eles que a tela
# acha, na outra linguagem, a linha que faz o mesmo que a do Python)
PODEM_FALTAR = {
    "java": set(),
    "cpp": {"aux_numero", "aux_verdadeiro"},                    # só entram se a busca escreve números/respostas
    "javascript": {"estrutura_importar"},                       # o JavaScript não importa nada
    "c": {"aux_numero", "aux_verdadeiro", "estrutura_classe", "estrutura_construtor", "principal_criar",
          "estrutura_campo_vertices"},                          # o C não tem classe nem objeto
}


def conferir_um_programa(algoritmo, grafo):
    vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite = grafo
    descricao = (algoritmo, vertices, arestas, ordenar, inicio, direcionado, destino, heuristica, limite)
    dados = {"nome": "Teste", "vertices": vertices, "arestas": arestas, "ordenar": ordenar, "inicio": inicio,
             "direcionado": direcionado, "algoritmo": algoritmo, "destino": destino, "heuristica": heuristica or {},
             "limite": limite}
    programas = codigo_fonte.programas_com_rotulos(dados, "busca", "02/10/2026 12:00")
    for programa in programas.values():
        estrutura.completar(programa)
    python = programas["python"]
    # O texto é o mesmo que a exportação grava (sem os rótulos); só a data e a hora do cabeçalho mudam
    data = re.compile(r"\d\d/\d\d/\d{4} \d\d:\d\d")
    for linguagem in programas:
        exportado = codigo_fonte.programa(linguagem, dados, "busca")
        assert data.sub("", programas[linguagem]["texto"]) == data.sub("", exportado), (descricao, linguagem)
    rastro = rastreador.rastrear_programa(python, algoritmo, estrito=True)
    passos_de_linha = rastro["passos_de_linha"]
    linhas = python["linhas"]
    # O print escreveu exatamente a saída esperada (a que fica comentada no fim do arquivo)
    assert rastro["saida"].splitlines() == python["saida"], (descricao, rastro["saida"])
    # Começa na linha 1: o cabeçalho, uma linha de comentário por passo
    quantas_do_cabecalho = sum(1 for rotulo in python["linhas_do_rotulo"] if rotulo.startswith("cabecalho_"))
    assert quantas_do_cabecalho >= 6, descricao
    for posicao in range(quantas_do_cabecalho):
        assert passos_de_linha[posicao]["linha"] == posicao + 1, (descricao, posicao)
        assert passos_de_linha[posicao]["tipo"] in ("comentario", "branco"), (descricao, posicao)
    # Termina na última linha do arquivo (a saída esperada, comentada)
    assert passos_de_linha[-1]["linha"] == len(linhas) and passos_de_linha[-1]["rotulo"] == "saida_esperada", descricao
    # Toda linha do nível de fora (começa na coluna 0) passa por um passo do programa (o nível 1)
    cobertas = set()
    for passo in passos_de_linha:
        if passo["profundidade"] == 1:
            cobertas.update(passo["linhas"])
    for numero in range(1, len(linhas) + 1):
        if linhas[numero - 1] and not linhas[numero - 1][0].isspace():
            assert numero in cobertas, (descricao, numero, linhas[numero - 1])
    for passo in passos_de_linha:
        # Comentário e linha em branco são mesmo isso; o resto é código e tem rótulo
        texto_da_linha = linhas[passo["linha"] - 1].strip()
        if passo["tipo"] == "branco":
            assert texto_da_linha == "", (descricao, passo["linha"])
        elif passo["tipo"] == "comentario":
            assert texto_da_linha.startswith("#"), (descricao, passo["linha"])
        else:
            assert passo["rotulo"], (descricao, passo["linha"], texto_da_linha)
        assert passo["explicacao"], (descricao, passo["linha"], texto_da_linha)
        # A entrada numa função é na linha do def dela
        if passo["tipo"] == "chamada":
            assert texto_da_linha.startswith("def "), (descricao, passo["linha"])
        # Num comentário, a pilha mostra a linha do próprio comentário
        if passo["tipo"] in ("comentario", "branco") and passo["antes"]["pilha"]:
            assert passo["antes"]["pilha"][0]["linha"] == passo["linha"], (descricao, passo["linha"])
        # O print diz o que vai escrever
        if passo["tipo"] == "linha" and texto_da_linha.startswith("print("):
            assert passo["explicacao"].startswith("Escreve na saída: "), (descricao, passo["explicacao"])
    # Entrar numa função é sempre um passo de "chamada" (na linha do def): toda vez que a pilha cresce,
    # o primeiro passo lá dentro é esse (menos no corpo de uma classe, que é criado sem chamada)
    for posicao in range(1, len(passos_de_linha)):
        anterior, atual = passos_de_linha[posicao - 1], passos_de_linha[posicao]
        if atual["profundidade"] > anterior["profundidade"] and atual["antes"]["pilha"][0]["tipo"] == "funcao":
            assert atual["tipo"] == "chamada", (descricao, posicao, atual["linha"])
    chamadas = [linhas[passo["linha"] - 1].strip() for passo in passos_de_linha if passo["tipo"] == "chamada"]
    assert any(chamada.startswith("def __init__") for chamada in chamadas), descricao
    # Um comando de várias linhas é UM passo, com todas as linhas dele: o grafo (adj ou arcos) aparece uma
    # vez só, do "adj = {" até o "}"
    do_grafo = [passo for passo in passos_de_linha if passo["rotulo"] == "principal_grafo" and passo["tipo"] == "linha"]
    assert len(do_grafo) == 1, (descricao, len(do_grafo))
    ultima_do_grafo = do_grafo[0]["linhas"][-1]
    assert linhas[ultima_do_grafo - 1].strip() in ("}", "]"), (descricao, linhas[ultima_do_grafo - 1])
    # A busca casa com os passos do BoscoGraph (como no 11a, agora no programa inteiro)
    passos = montar_passos(vertices, arestas, ordenar, inicio, direcionado, algoritmo, destino, heuristica, limite)
    casamento = rastreador.sincronizar(passos, passos_de_linha, python["rotulo_da_linha"], perfis.chave_do_trecho)
    for indice in range(len(passos)):
        tipo = passos[indice]["tipo"]
        da_busca = tipo not in TIPOS_DA_MONTAGEM and not tipo.startswith("tipo_") and \
            not tipo.startswith("resultado_") and tipo != "ordem_topologica"
        assert (indice in casamento) == da_busca, (descricao, indice, tipo)
    # As outras linguagens têm os rótulos do Python (menos os que a linguagem não precisa) e o cabeçalho
    # na mesma linha
    for linguagem in PODEM_FALTAR:
        outros = set(programas[linguagem]["linhas_do_rotulo"])
        faltam = set(python["linhas_do_rotulo"]) - outros - PODEM_FALTAR[linguagem]
        assert not faltam, (algoritmo, linguagem, sorted(faltam))
    for linguagem in programas:
        for numero in range(1, quantas_do_cabecalho + 1):
            assert programas[linguagem]["linhas_do_rotulo"][f"cabecalho_{numero}"] == [numero], (algoritmo, linguagem)
        # Nenhum rótulo sobrou na tela (a MARCA invisível sai antes de mostrar)
        for linha in programas[linguagem]["linhas"]:
            assert codigo_fonte.MARCA not in linha, (algoritmo, linguagem, linha)
    return rastro


def conferir_programa_inteiro(quantidade_por_busca):
    sorteio = random.Random(47)
    passos = 0
    for algoritmo in CHAVES:
        for rodada in range(quantidade_por_busca):
            rastro = conferir_um_programa(algoritmo, grafo_sorteado(sorteio, algoritmo))
            passos += len(rastro["passos_de_linha"])
    print(f"11d. Programa inteiro: em {quantidade_por_busca} grafos de cada busca, o linha a linha começa na linha 1 "
          f"(o cabeçalho), passa por todas as linhas do nível de fora até a última, cada linha executada tem rótulo e "
          f"explicação, a busca casa com o BoscoGraph, o print escreve a saída esperada e as outras linguagens têm os "
          f"mesmos rótulos ({passos} passos)")


def rodar():
    conferir_mesma_busca(150)
    conferir_rotulos()
    conferir_traducoes(60)
    conferir_programa_inteiro(40)


if __name__ == "__main__":
    rodar()
    print("Todos os testes do código de estudo passaram.")
