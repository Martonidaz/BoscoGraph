# Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do livro do Cormen (CLRS).
#   conjunto[v] -> o representante do conjunto de v: os vértices já ligados pelas arestas escolhidas têm
#                  o mesmo representante (é o MAKE-SET, o FIND-SET e o UNION do livro)
#   arvore      -> as arestas aceitas (u, v, peso), na ordem em que entraram
# As arestas são examinadas da mais leve para a mais pesada: (u, v) entra se u e v estão em conjuntos
# diferentes (ela liga duas partes); se estão no mesmo, ela fecharia um ciclo e fica de fora.
# itemgetter(2) pega o item 2 de cada tupla (u, v, peso), que é o peso. O sorted é estável: as arestas de
# mesmo peso ficam na ordem em que foram criadas. unir percorre todos os vértices: O(V) por união. Com a
# floresta de conjuntos disjuntos do livro (união por posto e compressão de caminho), seria quase O(1).

from operator import itemgetter


class Kruskal:
    def __init__(self, vertices, arestas):
        self.vertices = vertices        # os nomes dos vértices
        self.arestas = arestas          # (u, v, peso), uma vez cada, na ordem em que foram criadas
        self.conjunto = {}
        self.arvore = []

    def kruskal(self):
        for v in self.vertices:                                 # @cada_vertice
            self.conjunto[v] = v                                # @criar_conjunto
        ordenadas = sorted(self.arestas, key=itemgetter(2))     # @ordenar_arestas
        for u, v, peso in ordenadas:                            # @cada_aresta
            if self.conjunto[u] == self.conjunto[v]:            # @rejeitar
                continue                                        # @pula_aresta
            self.arvore.append((u, v, peso))                    # @aceitar
            self.unir(self.conjunto[u], self.conjunto[v])       # @unir

    # UNION: todos os vértices do conjunto b passam para o conjunto a
    def unir(self, a, b):
        for x in self.vertices:                                 # @cada_do_conjunto
            if self.conjunto[x] == b:                           # @mesmo_conjunto
                self.conjunto[x] = a                            # @muda_conjunto
