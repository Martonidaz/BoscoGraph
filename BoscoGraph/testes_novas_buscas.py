'''
    Conferências das buscas novas (versão 6), sem abrir janela:
    profundidade limitada, aprofundamento iterativo, bidirecional e Floyd-Warshall.
    Rode com: python testes_novas_buscas.py   (o testes.py também chama este arquivo)

    A ideia é a mesma dos outros testes: sortear centenas de grafos e conferir cada resposta com um
    jeito INDEPENDENTE de chegar nela:
      - todos os caminhos sem repetir vértice, listados um por um (força bruta), para a busca limitada;
      - a busca em largura, para o aprofundamento iterativo e a bidirecional (as duas acham o caminho
        com menos arestas);
      - o Bellman-Ford rodado a partir de cada vértice, para o Floyd-Warshall.
'''

import random
from decimal import Decimal

import algoritmos
import entrada
from boscograph import montar_passos
from testes_buscas import custo_do_caminho, floyd_warshall, passo_do_tipo, passos_do_tipo, nenhuma_mensagem_quebrada

INFINITO = entrada.INFINITO


# ----------------------------------------------------------------------
# Funções de apoio (independentes das classes do BoscoGraph)
# ----------------------------------------------------------------------

# Os "arcos" de cada vértice: (vizinho, número da aresta), cada aresta paralela separada.
# No não orientado, a aresta vale nos dois sentidos (o laço, uma vez só).
def arcos_de_cada_vertice(vertices, arestas, direcionado):
    arcos = {}
    for vertice in vertices:
        arcos[vertice] = []
    for numero in range(len(arestas)):
        origem, destino, nome, peso = arestas[numero]
        arcos[origem].append((destino, numero))
        if not direcionado and origem != destino:
            arcos[destino].append((origem, numero))
    return arcos


# Todos os caminhos que saem da origem sem repetir vértice, com até "maximo" arestas.
# Cada aresta paralela conta como um caminho diferente (como na árvore da busca limitada).
# Devolve a lista de caminhos, cada um como a lista de vértices.
def caminhos_simples(arcos, origem, maximo):
    todos = []

    def andar(caminho):
        todos.append(list(caminho))
        if len(caminho) - 1 == maximo:
            return
        for vizinho, numero in arcos[caminho[-1]]:
            if vizinho not in caminho:
                caminho.append(vizinho)
                andar(caminho)
                caminho.pop()

    andar([origem])
    return todos


# A distância em arestas de origem até cada vértice (busca em largura simples, com uma lista)
def distancias_em_arestas(arcos, origem):
    distancia = {origem: 0}
    fila = [origem]
    while fila:
        u = fila.pop(0)
        for v, numero in arcos[u]:
            if v not in distancia:
                distancia[v] = distancia[u] + 1
                fila.append(v)
    return distancia


# Bellman-Ford de uma origem (para conferir o Floyd-Warshall): devolve (d, tem_ciclo_negativo)
def bellman_ford(vertices, arestas, direcionado, origem):
    d = {}
    for v in vertices:
        d[v] = INFINITO
    d[origem] = Decimal(0)
    arcos = []
    for o, de, nome, peso in arestas:
        arcos.append((o, de, peso))
        if not direcionado and o != de:
            arcos.append((de, o, peso))
    for rodada in range(len(vertices) - 1):
        for u, v, w in arcos:
            if d[u] != INFINITO and d[u] + w < d[v]:
                d[v] = d[u] + w
    for u, v, w in arcos:
        if d[u] != INFINITO and d[u] + w < d[v]:
            return d, True
    return d, False


def grafo_sorteado(sorteio, maximo_de_vertices, maximo_de_arestas, com_pesos=False, negativos=False):
    direcionado = sorteio.random() < 0.6
    n = sorteio.randint(1, maximo_de_vertices)
    vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "numeros", "prefixo"]), "V")
    lacos = sorteio.random() < 0.3
    paralelas = sorteio.random() < 0.3
    m = sorteio.randint(0, min(maximo_de_arestas, entrada.maximo_de_arestas(n, lacos, paralelas, direcionado)))
    arestas = entrada.arestas_aleatorias(vertices, m, lacos, paralelas, sorteio.randint(0, 10 ** 6), direcionado)
    if com_pesos:
        pesos = []
        for i in range(len(arestas)):
            if negativos and sorteio.random() < 0.25:
                pesos.append(Decimal(sorteio.randint(-4, -1)))
            else:
                pesos.append(Decimal(sorteio.randint(0, 9)) + Decimal(sorteio.choice([0, 0, 0, 5])) / 10)
        arestas = entrada.trocar_pesos(arestas, list(range(len(arestas))), pesos)
    return vertices, arestas, direcionado


# ----------------------------------------------------------------------
# 8i. Busca em profundidade limitada
# ----------------------------------------------------------------------

def conferir_limitada(quantidade):
    sorteio = random.Random(101)
    cortes = 0
    achados = 0
    for rodada in range(quantidade):
        vertices, arestas, direcionado = grafo_sorteado(sorteio, 7, 11)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices + [None])
        limite = sorteio.randint(0, 4)
        ordenar = sorteio.random() < 0.6
        descricao = (vertices, arestas, direcionado, origem, destino, limite, ordenar)
        problemas, avisos = algoritmos.conferir(algoritmos.LIMITADA, vertices, arestas, direcionado, origem, destino,
                                                {}, limite, ordenar)
        assert problemas == [], (descricao, problemas)
        passos = montar_passos(vertices, arestas, ordenar, origem, direcionado, algoritmos.LIMITADA, destino,
                               None, limite)
        nenhuma_mensagem_quebrada(passos, descricao)
        arcos = arcos_de_cada_vertice(vertices, arestas, direcionado)
        caminhos = caminhos_simples(arcos, origem, limite)
        distancia = distancias_em_arestas(arcos, origem)
        entradas = passos_do_tipo(passos, "entrar")

        # A árvore da busca: cada entrada no caminho é um caminho simples a partir da origem
        for passo in entradas:
            assert passo["profundidade"] <= limite, descricao
        # A conta antecipada do algoritmos.py (usada para recusar árvores grandes demais) bate
        assert algoritmos.contar_nos(algoritmos.LIMITADA, vertices, arestas, direcionado, ordenar, origem, destino,
                                     limite) == len(entradas), descricao

        caminho = passo_do_tipo(passos, "resultado_caminho")
        if destino is not None and destino in distancia and distancia[destino] <= limite:
            # Existe caminho com até "limite" arestas: a busca TEM que achar um (válido e dentro do limite)
            achados += 1
            assert caminho is not None, descricao
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado, origem,
                                    destino) is not None, descricao
            assert len(caminho["arestas"]) <= limite and len(set(caminho["caminho"])) == len(caminho["caminho"])
        else:
            assert caminho is None, descricao
            fim = passo_do_tipo(passos, "resultado_limitada")
            # Sem achar, a busca gerou a árvore inteira: um nó por caminho simples até o limite
            assert len(entradas) == len(caminhos), (descricao, len(entradas), len(caminhos))
            # Corte <=> algum caminho simples tem exatamente "limite" arestas (alguém ficou na profundidade do limite)
            tem_no_limite = False
            for lista in caminhos:
                if len(lista) - 1 == limite:
                    tem_no_limite = True
            assert (fim["resultado"] == "corte") == tem_no_limite, descricao
            if fim["resultado"] == "corte":
                cortes += 1
            # Quem foi cortado: exatamente o fim dos caminhos com "limite" arestas
            esperados = set()
            for lista in caminhos:
                if len(lista) - 1 == limite:
                    esperados.add(lista[-1])
            assert set(fim["cortados"]) == esperados, descricao
            # Alcançados: todo vértice com distância até o limite
            alcancaveis = set()
            for vertice in distancia:
                if distancia[vertice] <= limite:
                    alcancaveis.add(vertice)
            assert set(fim["alcancados"]) == alcancaveis, descricao
    print(f"8i. Profundidade limitada conferida com a força bruta em {quantidade} grafos ({achados} acharam, "
          f"{cortes} com corte): achou <=> existe caminho até o limite; nós = caminhos simples; cortes certos")


# ----------------------------------------------------------------------
# 8j. Aprofundamento iterativo
# ----------------------------------------------------------------------

def conferir_iterativa(quantidade):
    sorteio = random.Random(202)
    achados = 0
    for rodada in range(quantidade):
        vertices, arestas, direcionado = grafo_sorteado(sorteio, 7, 10)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        ordenar = sorteio.random() < 0.6
        descricao = (vertices, arestas, direcionado, origem, destino, ordenar)
        problemas, avisos = algoritmos.conferir(algoritmos.ITERATIVA, vertices, arestas, direcionado, origem, destino,
                                                {}, None, ordenar)
        if problemas:
            assert "nós" in problemas[0], (descricao, problemas)        # só pode ser árvore grande demais
            continue
        passos = montar_passos(vertices, arestas, ordenar, origem, direcionado, algoritmos.ITERATIVA, destino)
        nenhuma_mensagem_quebrada(passos, descricao)
        arcos = arcos_de_cada_vertice(vertices, arestas, direcionado)
        distancia = distancias_em_arestas(arcos, origem)
        rodadas = passos_do_tipo(passos, "nova_iteracao")
        # As rodadas são 0, 1, 2, ... sem pular nenhuma
        for posicao in range(len(rodadas)):
            assert rodadas[posicao]["limite"] == posicao, descricao
        caminho = passo_do_tipo(passos, "resultado_caminho")
        assert algoritmos.contar_nos(algoritmos.ITERATIVA, vertices, arestas, direcionado, ordenar, origem, destino,
                                     None) == len(passos_do_tipo(passos, "entrar")), descricao
        if destino in distancia:
            # Acha na rodada da distância, com o MENOR número de arestas (o mesmo da busca em largura)
            achados += 1
            assert caminho is not None and len(caminho["arestas"]) == distancia[destino], descricao
            assert len(rodadas) == distancia[destino] + 1, descricao
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado, origem,
                                    destino) is not None, descricao
        else:
            assert caminho is None and passo_do_tipo(passos, "resultado_limitada")["resultado"] == "falha", descricao
            # Para quando uma rodada não tem corte: o limite passou do maior caminho simples
            maior = 0
            for lista in caminhos_simples(arcos, origem, len(vertices)):
                maior = max(maior, len(lista) - 1)
            assert len(rodadas) == maior + 2, (descricao, len(rodadas), maior)
        assert passo_do_tipo(passos, "resultado_iteracoes") is not None, descricao
    print(f"8j. Aprofundamento iterativo conferido com a busca em largura em {quantidade} grafos ({achados} acharam): "
          f"acha na rodada da distância, com o menor número de arestas")


# ----------------------------------------------------------------------
# 8k. Busca bidirecional
# ----------------------------------------------------------------------

def conferir_bidirecional(quantidade):
    sorteio = random.Random(303)
    achados = 0
    expandidos = 0                  # somando os grafos em que achou
    expandidos_pela_largura = 0
    for rodada in range(quantidade):
        vertices, arestas, direcionado = grafo_sorteado(sorteio, 12, 24)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        ordenar = sorteio.random() < 0.6
        descricao = (vertices, arestas, direcionado, origem, destino, ordenar)
        passos = montar_passos(vertices, arestas, ordenar, origem, direcionado, algoritmos.BIDIRECIONAL, destino)
        nenhuma_mensagem_quebrada(passos, descricao)
        arcos = arcos_de_cada_vertice(vertices, arestas, direcionado)
        distancia = distancias_em_arestas(arcos, origem)
        caminho = passo_do_tipo(passos, "resultado_caminho")
        if destino in distancia:
            achados += 1
            assert caminho["caminho"], descricao
            # O caminho existe de verdade (no sentido das arestas) e tem o menor número de arestas
            assert custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado, origem,
                                    destino) is not None, descricao
            assert len(caminho["arestas"]) == distancia[destino], (descricao, caminho, distancia[destino])
            comparacao = passo_do_tipo(passos, "resultado_comparacao")
            expandidos += comparacao["expandidos"]
            # A busca em largura, antes de tirar o destino da fila, tira pelo menos todos os que estão mais
            # perto da origem que ele (e o próprio destino)
            for vertice in distancia:
                if distancia[vertice] < distancia[destino]:
                    expandidos_pela_largura += 1
            expandidos_pela_largura += 1
        else:
            assert caminho["caminho"] == [] and passo_do_tipo(passos, "sem_encontro") is not None, descricao
        # Os lados se revezam: frente, trás, frente, trás...
        camadas = passos_do_tipo(passos, "nova_camada")
        for posicao in range(len(camadas)):
            assert camadas[posicao]["lado"] == ("frente" if posicao % 2 == 0 else "tras"), descricao
        # Nenhum vértice é descoberto pelos dois lados (o segundo lado a chegar vira o encontro)
        lados = {}
        for passo in passos:
            if passo["tipo"] in ("origem", "origem_tras"):
                lados[passo["vertice"]] = passo["lado"]
            elif passo["tipo"] == "descobrir_vizinho":
                assert passo["destino"] not in lados, descricao
                lados[passo["destino"]] = passo["lado"]
    print(f"8k. Busca bidirecional conferida com a busca em largura em {quantidade} grafos ({achados} acharam, "
          f"expandindo {expandidos} vértices no total, contra pelo menos {expandidos_pela_largura} da largura): "
          f"caminho válido e com o menor número de arestas")


# ----------------------------------------------------------------------
# 8l. Floyd-Warshall
# ----------------------------------------------------------------------

def conferir_floyd_warshall(quantidade):
    sorteio = random.Random(404)
    ciclos = 0
    for rodada in range(quantidade):
        negativos = sorteio.random() < 0.4
        vertices, arestas, direcionado = grafo_sorteado(sorteio, algoritmos.MAXIMO_FLOYD, 20, True, negativos)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices + [None])
        descricao = (vertices, arestas, direcionado, origem, destino)
        passos = montar_passos(vertices, arestas, sorteio.random() < 0.5, origem, direcionado,
                               algoritmos.FLOYD_WARSHALL, destino)
        nenhuma_mensagem_quebrada(passos, descricao)
        # A matriz final, montada só pelos passos (como a tela faz)
        d = {}
        for passo in passos:
            if passo["tipo"] == "inicializar_linha":
                for j in vertices:
                    d[(passo["vertice"], j)] = INFINITO
                d[(passo["vertice"], passo["vertice"])] = Decimal(0)
            elif passo["tipo"] == "arco_inicial" and passo["melhorou"]:
                d[(passo["origem"], passo["destino"])] = passo["peso"]
            elif passo["tipo"] == "comparar_par" and passo["melhorou"]:
                d[(passo["i"], passo["j"])] = passo["por_k"]
        # Ciclo negativo: o Floyd-Warshall acha <=> algum Bellman-Ford acha
        algum_ciclo = False
        for vertice in vertices:
            if bellman_ford(vertices, arestas, direcionado, vertice)[1]:
                algum_ciclo = True
        tem = passo_do_tipo(passos, "resultado_diagonal_negativa") is not None
        assert tem == algum_ciclo, descricao
        if tem:
            ciclos += 1
            continue
        # Sem ciclo negativo: cada linha da matriz é o Bellman-Ford daquela origem
        for i in vertices:
            esperado = bellman_ford(vertices, arestas, direcionado, i)[0]
            for j in vertices:
                assert d[(i, j)] == esperado[j], (descricao, i, j, d[(i, j)], esperado[j])
        # E é o Floyd-Warshall dos testes antigos também
        referencia = floyd_warshall(vertices, arestas, direcionado)
        for i in vertices:
            for j in vertices:
                assert d[(i, j)] == referencia[i][j], descricao
        caminho = passo_do_tipo(passos, "resultado_caminho")
        if destino is not None:
            if d[(origem, destino)] == INFINITO:
                assert caminho["caminho"] == [], descricao
            else:
                # O caminho que sai de π existe e custa exatamente d[origem][destino]
                custo = custo_do_caminho(caminho["caminho"], caminho["arestas"], arestas, direcionado, origem, destino)
                assert custo == d[(origem, destino)], (descricao, caminho, custo)
        else:
            assert caminho is None, descricao
    print(f"8l. Floyd-Warshall conferido com o Bellman-Ford de cada vértice em {quantidade} grafos ({ciclos} com "
          f"ciclo negativo): matriz, caminhos pela matriz π e ciclo negativo")


# ----------------------------------------------------------------------
# 8m. Exemplos e requisitos
# ----------------------------------------------------------------------

def conferir_exemplos_e_requisitos():
    D = Decimal
    # CLRS, figura 25.4: a matriz D(5) do grafo da figura 25.1
    vertices = ["1", "2", "3", "4", "5"]
    dados = [("1", "2", 3), ("1", "3", 8), ("1", "5", -4), ("2", "4", 1), ("2", "5", 7), ("3", "2", 4), ("4", "1", 2),
             ("4", "3", -5), ("5", "4", 6)]
    arestas = []
    for o, de, w in dados:
        arestas.append((o, de, "", D(w)))
    esperada = [[0, 1, -3, 2, -4], [3, 0, -4, 1, -1], [7, 4, 0, 5, 3], [2, -1, -5, 0, -2], [8, 5, 1, 6, 0]]
    passos = montar_passos(vertices, arestas, True, "1", True, algoritmos.FLOYD_WARSHALL, "3")
    d = {}
    for passo in passos:
        if passo["tipo"] == "inicializar_linha":
            for j in vertices:
                d[(passo["vertice"], j)] = INFINITO
            d[(passo["vertice"], passo["vertice"])] = 0
        elif passo["tipo"] in ("arco_inicial",) and passo["melhorou"]:
            d[(passo["origem"], passo["destino"])] = passo["peso"]
        elif passo["tipo"] == "comparar_par" and passo["melhorou"]:
            d[(passo["i"], passo["j"])] = passo["por_k"]
    for i in range(5):
        for j in range(5):
            assert d[(vertices[i], vertices[j])] == esperada[i][j], (i, j)
    assert passo_do_tipo(passos, "resultado_caminho")["caminho"] == ["1", "5", "4", "3"]

    # Requisitos
    sem_peso = [("A", "B", "", None)]
    problemas, avisos = algoritmos.conferir(algoritmos.LIMITADA, ["A", "B"], sem_peso, True, "A", None, {})
    assert problemas and "limite" in problemas[0]
    problemas, avisos = algoritmos.conferir(algoritmos.LIMITADA, ["A", "B"], sem_peso, True, "A", None, {}, 2)
    assert problemas == []
    problemas, avisos = algoritmos.conferir(algoritmos.ITERATIVA, ["A", "B"], sem_peso, True, "A", None, {})
    assert problemas and "destino" in problemas[0]
    problemas, avisos = algoritmos.conferir(algoritmos.BIDIRECIONAL, ["A", "B"], sem_peso, True, "A", None, {})
    assert problemas and "destino" in problemas[0]
    problemas, avisos = algoritmos.conferir(algoritmos.FLOYD_WARSHALL, ["A", "B"], sem_peso, True, "A", None, {})
    assert problemas and "sem peso" in problemas[0]
    muitos = entrada.nomes_dos_vertices(algoritmos.MAXIMO_FLOYD + 1, "letras")
    problemas, avisos = algoritmos.conferir(algoritmos.FLOYD_WARSHALL, muitos, [], True, None, None, {})
    assert problemas and "no máximo" in problemas[0]
    # Árvore de busca grande demais: K8 completo, limite 7 (milhares de caminhos simples)
    k8 = entrada.nomes_dos_vertices(8, "letras")
    completo = []
    for u in k8:
        for v in k8:
            if u < v:
                completo.append((u, v, "", None))
    problemas, avisos = algoritmos.conferir(algoritmos.LIMITADA, k8, completo, False, "A", None, {}, 7)
    assert problemas and "nós" in problemas[0], problemas
    # Origem igual ao destino
    passos = montar_passos(["A", "B"], [("A", "B", "", None)], True, "A", True, algoritmos.BIDIRECIONAL, "A")
    assert passo_do_tipo(passos, "resultado_caminho")["caminho"] == ["A"]
    passos = montar_passos(["A", "B"], [("A", "B", "", None)], True, "A", True, algoritmos.ITERATIVA, "A")
    assert len(passos_do_tipo(passos, "nova_iteracao")) == 1
    print("8m. Exemplo do livro (CLRS 25.1: a matriz D(5) inteira), requisitos e casos de borda das buscas novas: ok")


# ----------------------------------------------------------------------
# 8n. A tela, passo a passo, nas buscas novas
# ----------------------------------------------------------------------

def conferir_estado_visual(quantidade):
    from visual.estado import EstadoVisual
    from visual import explicacoes, perfis
    sorteio = random.Random(505)
    chaves = [algoritmos.LIMITADA, algoritmos.ITERATIVA, algoritmos.BIDIRECIONAL, algoritmos.FLOYD_WARSHALL]
    for rodada in range(quantidade):
        chave = chaves[rodada % len(chaves)]
        com_pesos = chave == algoritmos.FLOYD_WARSHALL
        vertices, arestas, direcionado = grafo_sorteado(sorteio, 8, 14, com_pesos, com_pesos)
        if sorteio.random() < 0.4:
            arestas = entrada.numerar_arestas(arestas)
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        limite = sorteio.randint(0, 4)
        ordenar = sorteio.random() < 0.5
        problemas, avisos = algoritmos.conferir(chave, vertices, arestas, direcionado, origem, destino, {}, limite,
                                                ordenar)
        if problemas:
            continue
        descricao = (chave, vertices, arestas, direcionado, origem, destino, limite)
        passos = montar_passos(vertices, arestas, ordenar, origem, direcionado, chave, destino, None, limite)
        estado = EstadoVisual(arestas, direcionado, chave)
        for passo in passos:
            if passo["tipo"] in ("corte", "subir"):
                assert estado.pilha[-1] == passo["vertice"], descricao       # sai quem está no topo
            if passo["tipo"] == "desenfileirar":
                fila = estado.fila_tras if passo.get("lado") == "tras" else estado.fila
                assert fila[0] == passo["vertice"], descricao
            estado.aplicar(passo)
            assert perfis.chave_do_trecho(passo) in perfis.perfil(chave)["trechos"], (descricao, passo["tipo"])
            assert explicacoes.explicar(chave, passo) != "", (descricao, passo["tipo"])
            for vertice in vertices:
                perfis.valores_da_tabela(chave, estado, vertice)
                perfis.rotulo_do_vertice(chave, estado, vertice)
            if passo["tipo"] == "entrar":
                # A pilha da tela é um caminho de verdade: cada um entrou pelo anterior
                assert estado.pilha[-1] == passo["vertice"] and len(estado.pilha) == passo["profundidade"] + 1
        if chave in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
            caminho = passo_do_tipo(passos, "resultado_caminho")
            if caminho is not None:
                assert estado.pilha == caminho["caminho"], descricao
            else:
                assert estado.pilha == [], descricao
        if chave == algoritmos.FLOYD_WARSHALL:
            # As setas azuis no fim: exatamente as arestas que estão na matriz inicial
            usadas = set(estado.aresta_da_matriz.values())
            for indice in range(len(arestas)):
                assert (estado.situacao_aresta[indice] == "arvore") == (indice in usadas), descricao
    print(f"8n. Tela conferida passo a passo em {quantidade} buscas novas (pilha do caminho, duas filas, matriz, "
          f"código e explicações)")


def rodar():
    conferir_limitada(400)
    conferir_iterativa(300)
    conferir_bidirecional(400)
    conferir_floyd_warshall(250)
    conferir_exemplos_e_requisitos()
    conferir_estado_visual(300)


if __name__ == "__main__":
    rodar()
    print("Todos os testes das buscas novas passaram.")
