'''
    BoscoGraph - buscas em grafos passo a passo

    O programa funciona em duas fases:
    1. Calcula tudo, como na prova. Só que, em vez de imprimir no terminal,
       cada etapa anota o que fez numa lista de passos.
    2. A janela reproduz os passos anotados, um de cada vez, desenhando o grafo.
       No modo "linha a linha", o código de estudo da busca (pasta estudo/) roda de verdade, uma
       linha por clique, e a janela mostra as variáveis dele (veja estudo/rastreador.py).

    A primeira tela é a escolha da busca: profundidade (DFS), profundidade limitada, aprofundamento
    iterativo, largura (BFS), bidirecional, Dijkstra, Bellman-Ford, Floyd-Warshall, gulosa, A* e a
    árvore geradora mínima (Prim e Kruskal), com um exemplo pronto ou com o grafo do editor. No editor,
    vértices, arestas, pesos e a heurística podem ser adicionados, renomeados, removidos, sorteados ou
    importados de outros programas, e o grafo pode ser salvo como modelo. O modelo padrão é o grafo da
    Prova 01.
    Depois da DFS, o programa classifica o grafo (simples, completo, valorado, cíclico, DAG...);
    depois das outras, mostra o resultado (distâncias, árvore, caminho, a árvore mínima e o peso dela).
'''

import algoritmos
from classes.vertice import Vertice
from classes.aresta import Aresta
from classes.grafo import Grafo
from classes.busca_em_profundidade import BuscaEmProfundidade
from classes.busca_limitada import BuscaEmProfundidadeLimitada
from classes.aprofundamento_iterativo import AprofundamentoIterativo
from classes.busca_em_largura import BuscaEmLargura
from classes.busca_bidirecional import BuscaBidirecional
from classes.dijkstra import Dijkstra
from classes.bellman_ford import BellmanFord
from classes.floyd_warshall import FloydWarshall
from classes.busca_gulosa import BuscaGulosa
from classes.a_estrela import AEstrela
from classes.prim import Prim
from classes.kruskal import Kruskal
from classes.tipo_do_grafo import TipoDoGrafo
from classes.resultado_da_busca import ResultadoDaBusca
from entrada import formatar_numero


# Fase 1: monta o grafo, roda a busca e devolve a lista com todos os passos anotados
#   vertices    -> nomes dos vértices, por exemplo ["A", "B", "C"]
#   arestas     -> (origem, destino, nome, peso), por exemplo [("A", "B", "e1", 5), ("B", "C", "", None)]
#   ordenar     -> True para ordenar as listas de adjacência antes da busca
#   inicio      -> vértice por onde a busca começa (None = o primeiro em ordem alfabética)
#   direcionado -> True para grafo orientado (A -> B); False para não orientado (A — B)
#   algoritmo   -> qual busca: "profundidade", "limitada", "iterativa", "largura", "bidirecional", "dijkstra",
#                  "bellman_ford", "floyd_warshall", "gulosa", "a_estrela", "prim" ou "kruskal" (as constantes
#                  de algoritmos.py)
#   destino     -> o vértice de chegada (obrigatório na gulosa, no A*, na iterativa e na bidirecional;
#                  nas outras, marca o caminho no resultado)
#   heuristica  -> {vértice: h} para a gulosa e o A*
#   limite      -> o limite de profundidade da busca limitada
def montar_passos(vertices, arestas, ordenar, inicio, direcionado=True, algoritmo=algoritmos.PROFUNDIDADE,
                  destino=None, heuristica=None, limite=None):
    # Confere antes de começar (o editor já confere, mas assim o erro nunca passa em silêncio)
    problemas, avisos = algoritmos.conferir(algoritmo, vertices, arestas, direcionado, inicio, destino,
                                            heuristica or {}, limite, ordenar)
    if problemas:
        raise ValueError(problemas[0])

    # O "caderno de anotações": cada etapa acrescenta aqui um passo.
    # A mesma lista é passada para o Grafo e para a busca, que anotam nela também.
    passos = []

    dicionario_vertice = {}

    # Cada nome vira uma chave e o valor é o objeto Vertice com esse nome ("A" -> Vertice("A"))
    for nome in vertices:
        dicionario_vertice[nome] = Vertice(nome)
        passos.append({
            "tipo": "criar_vertice",
            "vertice": nome,
            "mensagem": f"Vértice {nome} criado",
        })

    lista_arestas = []

    # No orientado a aresta aparece como A -> B; no não orientado, como A — B
    ligacao = "->"
    if not direcionado:
        ligacao = "—"

    # Para cada aresta, busca os dois objetos Vertice no dicionário e cria a Aresta que liga a origem ao destino
    for origem, destino_da_aresta, nome, peso in arestas:
        lista_arestas.append(Aresta(dicionario_vertice[origem], dicionario_vertice[destino_da_aresta], nome, peso))
        mensagem = f"Aresta {origem} {ligacao} {destino_da_aresta} criada"
        if nome:
            mensagem = f"Aresta {nome} ({origem} {ligacao} {destino_da_aresta}) criada"
        if peso is not None:
            mensagem += f", com peso {formatar_numero(peso)}"
        passos.append({
            "tipo": "criar_aresta",
            "origem": origem,
            "destino": destino_da_aresta,
            "nome": nome,
            "peso": peso,
            "mensagem": mensagem,
        })

    # Todos os objetos Vertice (os valores do dicionário) em uma lista: é o V de G = (V, A)
    lista_vertice = list(dicionario_vertice.values())

    # G = (V, A): o Grafo monta a lista de adjacência e anota cada passo
    grafo = Grafo(lista_vertice, lista_arestas, passos, direcionado)

    if ordenar:
        grafo.ordenar_listas_adjacencia()
    else:
        passos.append({
            "tipo": "sem_ordenar",
            "mensagem": "Ordenação desligada: cada lista fica na ordem em que as arestas foram criadas",
        })

    # A busca em profundidade percorre o grafo inteiro (DFS(G)) e depois classifica o grafo
    if algoritmo == algoritmos.PROFUNDIDADE:
        busca = BuscaEmProfundidade(grafo, passos)
        busca.dfs(inicio)
        # Com a busca pronta, a classificação do grafo (simples, completo, valorado, cíclico, DAG...)
        tipo = TipoDoGrafo(grafo, busca, passos)
        tipo.concluir()
        return passos

    # As outras buscas partem de uma origem (sem escolha, a primeira em ordem alfabética)
    if inicio not in vertices:
        inicio = sorted(vertices)[0]
    if algoritmo == algoritmos.LIMITADA:
        busca = BuscaEmProfundidadeLimitada(grafo, passos)
        busca.buscar(inicio, destino, limite)
    elif algoritmo == algoritmos.ITERATIVA:
        busca = AprofundamentoIterativo(grafo, passos)
        busca.buscar(inicio, destino)
    elif algoritmo == algoritmos.LARGURA:
        busca = BuscaEmLargura(grafo, passos)
        busca.bfs(inicio)
    elif algoritmo == algoritmos.BIDIRECIONAL:
        busca = BuscaBidirecional(grafo, passos)
        busca.buscar(inicio, destino)
    elif algoritmo == algoritmos.DIJKSTRA:
        busca = Dijkstra(grafo, passos)
        busca.dijkstra(inicio)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        busca = BellmanFord(grafo, passos)
        busca.bellman_ford(inicio)
    elif algoritmo == algoritmos.FLOYD_WARSHALL:
        # Todos os pares: não parte de uma origem (a origem só serve para mostrar um caminho no resultado)
        busca = FloydWarshall(grafo, passos)
        busca.floyd_warshall()
    elif algoritmo == algoritmos.GULOSA:
        busca = BuscaGulosa(grafo, passos, heuristica)
        busca.buscar(inicio, destino)
    elif algoritmo == algoritmos.PRIM:
        # A árvore geradora mínima a partir da raiz (e uma árvore nova em cada parte desligada)
        busca = Prim(grafo, passos)
        busca.prim(inicio)
    elif algoritmo == algoritmos.KRUSKAL:
        # O Kruskal não parte de um vértice: ele olha as arestas, da mais leve para a mais pesada
        busca = Kruskal(grafo, passos)
        busca.kruskal()
    else:
        busca = AEstrela(grafo, passos, heuristica)
        busca.buscar(inicio, destino)

    # Com a busca pronta, o resultado: distâncias, árvore, caminho até o destino...
    resultado = ResultadoDaBusca(algoritmo, grafo, busca, passos, heuristica or {}, inicio)
    resultado.concluir(destino)
    return passos


# Fase 2: a tela inicial, o editor do grafo e a janela que reproduz os passos.
# "--verificar" faz o autoteste sem abrir janela (veja verificacao.py); o construir.py usa no executável.
# Um arquivo .bosco na linha de comando abre direto na visualização (é o que o Windows faz no duplo
# clique, depois que o instalador associa a extensão .bosco ao BoscoGraph).
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--verificar":
        import verificacao

        relatorio = sys.argv[2] if len(sys.argv) > 2 else None
        sys.exit(verificacao.rodar(relatorio))

    from visual.aplicativo import Aplicativo

    aplicativo = Aplicativo(montar_passos)
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".bosco"):
        from visual import exportar

        arquivo = sys.argv[1]
        # Depois que a janela aparecer (o aviso de arquivo com problema precisa da janela na tela)
        aplicativo.raiz.after(150, lambda: exportar.abrir_bosco(aplicativo, arquivo))
    aplicativo.abrir()
