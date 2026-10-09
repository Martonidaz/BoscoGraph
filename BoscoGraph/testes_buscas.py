'''
    Conferências das buscas com pesos e da busca em largura, sem abrir janela.
    Rode com: python testes_buscas.py   (o testes.py também chama este arquivo)

    A ideia é a mesma do testes.py: sortear centenas de grafos e conferir o resultado de cada
    busca com um algoritmo INDEPENDENTE, que chega na resposta por outro caminho:
      - Floyd-Warshall: calcula a menor distância entre todos os pares com três laços,
        sem fila nenhuma. Também detecta ciclo negativo (a distância de v até v fica < 0).
    Se a busca e o Floyd-Warshall concordam em centenas de grafos sorteados, é muito difícil
    que os dois estejam errados do mesmo jeito.
'''

import random
from decimal import Decimal

import algoritmos
import entrada
import modelos
from boscograph import montar_passos

INFINITO = entrada.INFINITO


# ----------------------------------------------------------------------
# Funções de apoio
# ----------------------------------------------------------------------

# Floyd-Warshall: dist[u][v] = menor custo de u até v. "unitario" = cada aresta custa 1 (para a BFS).
# Ideia: para cada vértice k, ver se passar por k encurta o caminho de i até j.
def floyd_warshall(vertices, arestas, direcionado, unitario=False):
    dist = {}
    for i in vertices:
        dist[i] = {}
        for j in vertices:
            dist[i][j] = INFINITO
        dist[i][i] = Decimal(0)
    for origem, destino, nome, peso in arestas:
        custo = Decimal(1) if unitario else peso
        sentidos = [(origem, destino)]
        if not direcionado:
            sentidos.append((destino, origem))
        for u, v in sentidos:
            if custo < dist[u][v]:
                dist[u][v] = custo
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


# O passo da busca com esse tipo (o primeiro), ou None
def passo_do_tipo(passos, tipo):
    for passo in passos:
        if passo["tipo"] == tipo:
            return passo
    return None


def passos_do_tipo(passos, tipo):
    lista = []
    for passo in passos:
        if passo["tipo"] == tipo:
            lista.append(passo)
    return lista


# As distâncias finais, montadas só a partir dos passos (como a janela faz)
def distancias_dos_passos(vertices, passos):
    d = {}
    for vertice in vertices:
        d[vertice] = INFINITO
    for passo in passos:
        if passo["tipo"] == "origem":
            d[passo["vertice"]] = Decimal(passo["distancia"])
        elif passo["tipo"] == "descobrir_vizinho":
            d[passo["destino"]] = Decimal(passo["distancia"])
        elif passo["tipo"] == "relaxar" and passo["melhorou"]:
            d[passo["destino"]] = passo["depois"]
    return d


# O caminho do resultado é um caminho de verdade no grafo? (cada aresta liga o vértice atual ao seguinte)
# Devolve o custo do caminho (soma dos pesos) ou None se for inválido.
def custo_do_caminho(caminho, numeros, arestas, direcionado, origem, destino):
    if not caminho or caminho[0] != origem or caminho[-1] != destino or len(numeros) != len(caminho) - 1:
        return None
    soma = Decimal(0)
    for posicao in range(len(numeros)):
        a, b = caminho[posicao], caminho[posicao + 1]
        o, d, nome, peso = arestas[numeros[posicao]]
        if not ((o, d) == (a, b) or (not direcionado and (o, d) == (b, a))):
            return None
        if peso is not None:
            soma += peso
    return soma


# Um grafo sorteado (vértices, arestas com pesos) com as opções dadas
def grafo_sorteado(sorteio, menor_peso, maior_peso, direcionado, maximo_de_vertices=12):
    n = sorteio.randint(1, maximo_de_vertices)
    vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "numeros", "prefixo"]), "R")
    lacos = sorteio.random() < 0.3
    paralelas = sorteio.random() < 0.4
    m = sorteio.randint(0, entrada.maximo_de_arestas(n, lacos, paralelas, direcionado))
    arestas = entrada.arestas_aleatorias(vertices, m, lacos, paralelas, sorteio.randint(0, 10 ** 6), direcionado)
    pesos = entrada.sortear_numeros(len(arestas), menor_peso, maior_peso, sorteio.randint(0, 10 ** 6))
    # Alguns pesos com casas decimais, para exercitar o Decimal
    for i in range(len(pesos)):
        if sorteio.random() < 0.2:
            pesos[i] = pesos[i] + Decimal(sorteio.randint(0, 999)) / 1000
    arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
    return vertices, arestas


def nenhuma_mensagem_quebrada(passos, descricao):
    for passo in passos:
        assert "None" not in passo["mensagem"] and "Infinity" not in passo["mensagem"], (descricao, passo)


# ----------------------------------------------------------------------
# As conferências
# ----------------------------------------------------------------------

def conferir_exemplos_do_livro():
    D = Decimal
    # CLRS, figura 24.6 (Dijkstra): d = s 0, t 8, x 9, y 5, z 7
    vertices = list("stxyz")
    dados = [("s", "t", 10), ("s", "y", 5), ("t", "x", 1), ("t", "y", 2), ("y", "t", 3), ("y", "x", 9),
             ("y", "z", 2), ("x", "z", 4), ("z", "x", 6), ("z", "s", 7)]
    arestas = []
    for o, d, w in dados:
        arestas.append((o, d, "", D(w)))
    passos = montar_passos(vertices, arestas, True, "s", True, "dijkstra", "x")
    assert distancias_dos_passos(vertices, passos) == {"s": 0, "t": 8, "x": 9, "y": 5, "z": 7}
    extraidos = []
    for passo in passos_do_tipo(passos, "extrair"):
        extraidos.append(passo["vertice"])
    assert extraidos == ["s", "y", "z", "t", "x"], "a mesma ordem do livro"
    assert passo_do_tipo(passos, "resultado_caminho")["caminho"] == ["s", "y", "t", "x"]

    # CLRS, figura 24.4 (Bellman-Ford, com pesos negativos): d = t 2, x 4, y 7, z -2
    dados = [("s", "t", 6), ("s", "y", 7), ("t", "x", 5), ("t", "y", 8), ("t", "z", -4), ("x", "t", -2),
             ("y", "x", -3), ("y", "z", 9), ("z", "s", 2), ("z", "x", 7)]
    arestas = []
    for o, d, w in dados:
        arestas.append((o, d, "", D(w)))
    passos = montar_passos(vertices, arestas, True, "s", True, "bellman_ford", "z")
    assert distancias_dos_passos(vertices, passos) == {"s": 0, "t": 2, "x": 4, "y": 7, "z": -2}
    assert passo_do_tipo(passos, "resultado_caminho")["caminho"] == ["s", "y", "x", "t", "z"]
    assert passo_do_tipo(passos, "ciclo_negativo") is None

    # Dijkstra recusa peso negativo (com a explicação do que fazer)
    problemas, avisos = algoritmos.conferir("dijkstra", vertices, arestas, True, "s", None, {})
    assert problemas and "Bellman-Ford" in problemas[0], problemas
    try:
        montar_passos(vertices, arestas, True, "s", True, "dijkstra")
        assert False, "Dijkstra com peso negativo deveria ser recusado"
    except ValueError:
        pass

    # Não orientado: uma aresta negativa já é um ciclo negativo (A — B — A)
    passos = montar_passos(["A", "B"], [("A", "B", "", D(-1))], True, "A", False, "bellman_ford")
    assert passo_do_tipo(passos, "resultado_ciclo_negativo")["ciclo"] in (["A", "B", "A"], ["B", "A", "B"])
    problemas, avisos = algoritmos.conferir("bellman_ford", ["A", "B"], [("A", "B", "", D(-1))], False, "A", None, {})
    assert not problemas and "ciclo negativo" in avisos[0]

    # A precisão do Decimal: 0,1 + 0,2 = 0,3 não pode "melhorar" um caminho de custo 0,3
    arestas = [("A", "B", "", D("0.1")), ("B", "C", "", D("0.2")), ("A", "C", "", D("0.3"))]
    passos = montar_passos(["A", "B", "C"], arestas, True, "A", True, "dijkstra", "C")
    assert passo_do_tipo(passos, "resultado_caminho")["caminho"] == ["A", "C"], "empate exato: fica o 1º caminho"
    print("8a. Exemplos do livro (CLRS 24.4 e 24.6), pesos negativos e precisão do Decimal: ok")


def conferir_largura(quantidade):
    sorteio = random.Random(11)
    for rodada in range(quantidade):
        direcionado = sorteio.random() < 0.5
        vertices, arestas = grafo_sorteado(sorteio, 1, 9, direcionado, 16)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        descricao = f"BFS {rodada}: {len(vertices)} vértices, {len(arestas)} arestas, orientado={direcionado}"
        passos = montar_passos(vertices, arestas, sorteio.random() < 0.5, origem, direcionado, "largura", destino)
        nenhuma_mensagem_quebrada(passos, descricao)
        oraculo = floyd_warshall(vertices, arestas, direcionado, unitario=True)
        d = distancias_dos_passos(vertices, passos)
        for v in vertices:
            assert d[v] == oraculo[origem][v], (descricao, v, d[v], oraculo[origem][v])

        # A fila: sai na mesma ordem em que entrou (FIFO), e as distâncias de quem sai nunca diminuem
        entrou = []
        saiu = []
        for passo in passos:
            if passo["tipo"] == "origem":
                entrou.append(passo["vertice"])
            elif passo["tipo"] == "descobrir_vizinho":
                entrou.append(passo["destino"])
            elif passo["tipo"] == "desenfileirar":
                saiu.append(passo["vertice"])
        assert saiu == entrou, descricao
        for i in range(1, len(saiu)):
            assert d[saiu[i - 1]] <= d[saiu[i]], descricao
        # Cada aresta da árvore desce exatamente uma camada; árvore = alcançados - 1
        alcancados = 0
        for v in vertices:
            if d[v] != INFINITO:
                alcancados += 1
        arvore = passos_do_tipo(passos, "descobrir_vizinho")
        assert len(arvore) == alcancados - 1, descricao
        for passo in arvore:
            assert d[passo["destino"]] == d[passo["origem"]] + 1, descricao
        # Cada aresta é examinada uma vez de cada ponta (no não orientado) ou uma vez (no orientado),
        # e só a partir de vértices alcançados
        examinadas = len(arvore) + len(passos_do_tipo(passos, "ignorar_vizinho"))
        esperado = 0
        for o, dd, nome, peso in arestas:
            if d[o] != INFINITO:
                esperado += 1
            if not direcionado and o != dd and d[dd] != INFINITO:
                esperado += 1
        assert examinadas == esperado, descricao
        # O caminho até o destino tem d[destino] arestas e é um caminho de verdade
        caminho = passo_do_tipo(passos, "resultado_caminho")
        if d[destino] == INFINITO:
            assert caminho["caminho"] == [], descricao
        else:
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado,
                                    origem, destino) is not None, descricao
            assert len(caminho["arestas"]) == d[destino], descricao
    print(f"8b. Busca em largura conferida com Floyd-Warshall em {quantidade} grafos (fila, camadas, caminho)")


def conferir_dijkstra(quantidade):
    sorteio = random.Random(24)
    for rodada in range(quantidade):
        direcionado = sorteio.random() < 0.5
        vertices, arestas = grafo_sorteado(sorteio, 0, 20, direcionado)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        descricao = f"Dijkstra {rodada}: {len(vertices)} vértices, {len(arestas)} arestas, orientado={direcionado}"
        passos = montar_passos(vertices, arestas, sorteio.random() < 0.5, origem, direcionado, "dijkstra", destino)
        nenhuma_mensagem_quebrada(passos, descricao)
        oraculo = floyd_warshall(vertices, arestas, direcionado)
        d = distancias_dos_passos(vertices, passos)
        for v in vertices:
            assert d[v] == oraculo[origem][v], (descricao, v, d[v], oraculo[origem][v])
        # Quem sai da fila nunca é mais barato que quem saiu antes, e cada um sai uma vez só
        extraidos = []
        for passo in passos_do_tipo(passos, "extrair"):
            extraidos.append(passo["vertice"])
        assert len(extraidos) == len(set(extraidos)), descricao
        for i in range(1, len(extraidos)):
            assert d[extraidos[i - 1]] <= d[extraidos[i]], descricao
        alcancados = []
        for v in vertices:
            if d[v] != INFINITO:
                alcancados.append(v)
        assert sorted(extraidos) == sorted(alcancados), descricao
        # Um vértice já extraído (Preto) nunca melhora
        pretos = []
        for passo in passos:
            if passo["tipo"] == "extrair":
                pretos.append(passo["vertice"])
            if passo["tipo"] == "relaxar" and passo["melhorou"]:
                assert passo["destino"] not in pretos, descricao
        caminho = passo_do_tipo(passos, "resultado_caminho")
        if d[destino] != INFINITO:
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado,
                                    origem, destino) == d[destino], descricao
    print(f"8c. Dijkstra conferido com Floyd-Warshall em {quantidade} grafos (ordem de saída e caminhos)")


def conferir_bellman_ford(quantidade):
    sorteio = random.Random(37)
    ciclos = 0
    for rodada in range(quantidade):
        direcionado = sorteio.random() < 0.7
        vertices, arestas = grafo_sorteado(sorteio, -4, 15, direcionado, 10)
        origem = sorteio.choice(vertices)
        descricao = f"Bellman-Ford {rodada}: {len(vertices)} vértices, {len(arestas)} arestas"
        passos = montar_passos(vertices, arestas, True, origem, direcionado, "bellman_ford")
        nenhuma_mensagem_quebrada(passos, descricao)
        oraculo = floyd_warshall(vertices, arestas, direcionado)
        # Existe ciclo negativo alcançável a partir da origem? (no Floyd-Warshall: dist[v][v] < 0)
        tem_ciclo = False
        for v in vertices:
            if oraculo[origem][v] != INFINITO and oraculo[v][v] < 0:
                tem_ciclo = True
        achado = passo_do_tipo(passos, "resultado_ciclo_negativo")
        assert (achado is not None) == tem_ciclo, descricao
        if achado:
            ciclos += 1
            ciclo = achado["ciclo"]
            soma = custo_do_caminho(ciclo, achado["arestas"], arestas, direcionado, ciclo[0], ciclo[0])
            assert soma is not None and soma < 0 and soma == achado["soma"], (descricao, ciclo)
        else:
            d = distancias_dos_passos(vertices, passos)
            for v in vertices:
                assert d[v] == oraculo[origem][v], (descricao, v)
        # Nunca passa de |V| - 1 rodadas
        assert len(passos_do_tipo(passos, "rodada")) <= max(0, len(vertices) - 1), descricao
    assert ciclos > 20, "o sorteio precisa exercitar ciclos negativos"
    print(f"8d. Bellman-Ford conferido em {quantidade} grafos ({ciclos} com ciclo negativo, sempre de soma < 0)")


def conferir_a_estrela_e_gulosa(quantidade):
    sorteio = random.Random(50)
    for rodada in range(quantidade):
        direcionado = sorteio.random() < 0.5
        vertices, arestas = grafo_sorteado(sorteio, 0, 20, direcionado)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        descricao = f"A* {rodada}: {len(vertices)} vértices, {len(arestas)} arestas"
        custo = algoritmos.custos_ate_o_destino(vertices, arestas, destino, direcionado)
        oraculo = floyd_warshall(vertices, arestas, direcionado)
        otimo = oraculo[origem][destino]

        # Três heurísticas: zero (A* = Dijkstra), exata (perfeita e consistente) e admissível sorteada
        zero = {}
        exata = {}
        admissivel = {}
        for v in vertices:
            zero[v] = Decimal(0)
            exata[v] = custo[v] if custo[v] != INFINITO else Decimal(1000)
            fracao = Decimal(sorteio.randint(0, 100)) / 100
            admissivel[v] = (custo[v] * fracao).quantize(Decimal("0.001")) if custo[v] != INFINITO else Decimal(500)
        for nome, h in (("zero", zero), ("exata", exata), ("admissivel", admissivel)):
            passos = montar_passos(vertices, arestas, True, origem, direcionado, "a_estrela", destino, h)
            nenhuma_mensagem_quebrada(passos, descricao)
            caminho = passo_do_tipo(passos, "resultado_caminho")
            if otimo == INFINITO:
                assert passo_do_tipo(passos, "nao_chegou") is not None and caminho["caminho"] == [], descricao
                continue
            assert passo_do_tipo(passos, "chegou") is not None, (descricao, nome)
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado,
                                    origem, destino) == otimo, (descricao, nome, "com h admissível, A* é ótimo")
            comparacao = passo_do_tipo(passos, "resultado_comparacao")
            assert comparacao["melhor"] == otimo and comparacao["encontrado"] == otimo, descricao
            reaberturas = 0
            for passo in passos_do_tipo(passos, "relaxar"):
                if passo["reabriu"]:
                    reaberturas += 1
            if nome != "admissivel":
                assert reaberturas == 0, (descricao, nome, "h consistente nunca reabre")
            if nome == "exata":
                assert passo_do_tipo(passos, "resultado_heuristica")["admissivel"] is True, descricao
            if nome == "zero":
                # Com h = 0, o A* expande exatamente o que o Dijkstra expande até chegar no destino
                referencia = montar_passos(vertices, arestas, True, origem, direcionado, "dijkstra")
                ordem_dijkstra = []
                for passo in passos_do_tipo(referencia, "extrair"):
                    ordem_dijkstra.append(passo["vertice"])
                ordem_a_estrela = []
                for passo in passos_do_tipo(passos, "extrair"):
                    ordem_a_estrela.append(passo["vertice"])
                assert ordem_a_estrela == ordem_dijkstra[:ordem_dijkstra.index(destino) + 1], descricao

        # Gulosa com h qualquer: chega se e somente se existe caminho; o caminho é válido e nunca
        # é mais barato que o ótimo
        h = {}
        for v in vertices:
            h[v] = Decimal(sorteio.randint(0, 30))
        passos = montar_passos(vertices, arestas, True, origem, direcionado, "gulosa", destino, h)
        nenhuma_mensagem_quebrada(passos, descricao)
        caminho = passo_do_tipo(passos, "resultado_caminho")
        if otimo == INFINITO:
            assert caminho["caminho"] == [], descricao
        else:
            custo_da_gulosa = custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado,
                                               origem, destino)
            assert custo_da_gulosa is not None and custo_da_gulosa >= otimo, descricao
            assert passo_do_tipo(passos, "resultado_comparacao")["otimo"] == (custo_da_gulosa == otimo)
    print(f"8e. A* (h zero, exata e admissível) e gulosa conferidos em {quantidade} grafos")


def conferir_requisitos():
    D = Decimal
    vertices = ["A", "B", "C"]
    sem_peso = [("A", "B", "", None), ("B", "C", "", D(2))]
    problemas, avisos = algoritmos.conferir("dijkstra", vertices, sem_peso, True, "A", None, {})
    assert problemas and "1 aresta está sem peso" in problemas[0], problemas
    problemas, avisos = algoritmos.conferir("largura", vertices, sem_peso, True, "A", None, {})
    assert not problemas and "ignora os pesos" in avisos[0]
    problemas, avisos = algoritmos.conferir("a_estrela", vertices, [("A", "B", "", D(1))], True, "A", None, {})
    assert len(problemas) == 2, "falta o destino e falta h"
    h = {"A": D(9), "B": D(0), "C": D(0)}
    problemas, avisos = algoritmos.conferir("a_estrela", vertices, [("A", "B", "", D(1))], True, "A", "B", h)
    assert not problemas and "não é admissível" in avisos[0], avisos
    problemas, avisos = algoritmos.conferir("gulosa", vertices, sem_peso, True, "A", "C", {"A": D(1), "B": D(1),
                                                                                          "C": D(0)})
    assert not problemas and "conta o caminho em arestas" in avisos[0]
    # Gulosa sem pesos: o resultado conta arestas
    passos = montar_passos(vertices, sem_peso, True, "A", True, "gulosa", "C", {"A": D(1), "B": D(1), "C": D(0)})
    assert passo_do_tipo(passos, "resultado_caminho")["mensagem"].endswith("(2 arestas)")
    # A* com h que superestima pode errar: o resultado mostra que não foi o melhor caminho
    arestas = [("S", "A", "", D(1)), ("A", "T", "", D(1)), ("S", "T", "", D(5))]
    h = {"S": D(0), "A": D(10), "T": D(0)}
    passos = montar_passos(["S", "A", "T"], arestas, True, "S", True, "a_estrela", "T", h)
    assert passo_do_tipo(passos, "resultado_comparacao")["encontrado"] == 5
    assert passo_do_tipo(passos, "resultado_heuristica")["admissivel"] is False
    print("8f. Requisitos de cada busca (pesos, negativos, destino, heurística) e avisos: ok")


def conferir_modelos_de_exemplo():
    for nome in modelos.listar_modelos():
        grafo = modelos.carregar_modelo(nome)
        problemas, avisos = algoritmos.conferir(grafo["algoritmo"], grafo["vertices"], grafo["arestas"],
                                                grafo["direcionado"], grafo["inicio"], grafo["destino"],
                                                grafo["heuristica"])
        assert problemas == [], (nome, problemas)
        passos = montar_passos(grafo["vertices"], grafo["arestas"], grafo["ordenar"], grafo["inicio"],
                               grafo["direcionado"], grafo["algoritmo"], grafo["destino"], grafo["heuristica"])
        nenhuma_mensagem_quebrada(passos, nome)
    print("8g. Modelos de exemplo: todos abrem e rodam a busca escolhida")


def conferir_estado_visual(quantidade):
    from visual.estado import EstadoVisual
    from visual import explicacoes, perfis
    sorteio = random.Random(77)
    chaves = [algoritmos.LARGURA, algoritmos.DIJKSTRA, algoritmos.BELLMAN_FORD, algoritmos.GULOSA,
              algoritmos.A_ESTRELA]
    for rodada in range(quantidade):
        chave = chaves[rodada % len(chaves)]
        direcionado = sorteio.random() < 0.5
        menor = -3 if chave == algoritmos.BELLMAN_FORD else 0
        vertices, arestas = grafo_sorteado(sorteio, menor, 12, direcionado)
        if sorteio.random() < 0.4:
            arestas = entrada.numerar_arestas(arestas)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        h = {}
        for v in vertices:
            h[v] = Decimal(sorteio.randint(0, 15))
        descricao = f"tela {rodada} ({chave}): {len(vertices)} vértices, {len(arestas)} arestas"
        passos = montar_passos(vertices, arestas, sorteio.random() < 0.5, origem, direcionado, chave, destino, h)
        estado = EstadoVisual(arestas, direcionado, chave)
        for passo in passos:
            # Quem sai da fila na tela é quem o algoritmo tirou
            if passo["tipo"] == "desenfileirar":
                assert estado.fila[0] == passo["vertice"], descricao
            if passo["tipo"] == "extrair":
                assert estado.fila_por_prioridade()[0] == passo["vertice"], (descricao, estado.fila)
            estado.aplicar(passo)
            # Toda linha destacada existe no perfil e todo passo tem explicação
            assert perfis.chave_do_trecho(passo) in perfis.perfil(chave)["trechos"], (descricao, passo["tipo"])
            assert explicacoes.explicar(chave, passo) != "", (descricao, passo["tipo"])
            for vertice in vertices:
                perfis.valores_da_tabela(chave, estado, vertice)
                perfis.rotulo_do_vertice(chave, estado, vertice)
        # No fim, as arestas azuis da tela são exatamente as arestas do pai (π)
        arvore = passo_do_tipo(passos, "resultado_arvore")
        if arvore is not None:
            azuis = []
            for indice in range(len(arestas)):
                if estado.situacao_aresta[indice] == "arvore":
                    azuis.append(indice)
            assert sorted(azuis) == sorted(arvore["arestas"]), descricao
        if chave in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
            assert estado.fila == [], descricao
        # Toda aresta examinada pela busca terminou como "arvore" ou "examinada"
        for situacao in estado.situacao_aresta:
            assert situacao in ("grafo", "arvore", "examinada"), descricao
    print(f"8h. Tela conferida passo a passo em {quantidade} buscas (fila, árvore azul, código e explicações)")


def rodar():
    conferir_exemplos_do_livro()
    conferir_largura(300)
    conferir_dijkstra(300)
    conferir_bellman_ford(400)
    conferir_a_estrela_e_gulosa(250)
    conferir_requisitos()
    conferir_modelos_de_exemplo()
    conferir_estado_visual(300)


if __name__ == "__main__":
    rodar()
    print("Todos os testes das buscas passaram.")
