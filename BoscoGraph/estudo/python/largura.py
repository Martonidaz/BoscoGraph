# Busca em largura (BFS), como BFS(G, s) do livro do Cormen (CLRS).
#   cor[v]  -> BRANCO (não descoberto), CINZA (descoberto, na fila) ou PRETO (terminado)
#   d[v]    -> o menor número de arestas de s até v (INFINITO = não alcançado)
#   pai[v]  -> de qual vértice a busca chegou em v (o π do livro)
#   fila    -> os descobertos que ainda vão ter os vizinhos examinados: entra no fim, sai do começo
# A fila é um deque (fila de duas pontas): tirar do começo custa O(1). Numa lista comum,
# lista.pop(0) arrasta todos os outros elementos uma posição: O(n).

from collections import deque
from decimal import Decimal

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
INFINITO = Decimal("Infinity")


class BuscaEmLargura:
    def __init__(self, adj):
        self.adj = adj                  # adj[u] = [(v, peso), ...] (a BFS não usa o peso)
        self.cor = {}
        self.d = {}
        self.pai = {}
        self.fila = deque()

    def bfs(self, s):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.d[v] = INFINITO                        # @d_infinito
            self.pai[v] = None                          # @inicializar
        self.cor[s] = CINZA                             # @origem_cinza
        self.d[s] = 0                                   # @origem_d
        self.fila.append(s)                             # @origem
        while self.fila:                                # @enquanto_fila
            u = self.fila.popleft()                     # @desenfileirar
            for v, peso in self.adj[u]:                 # @cada_vizinho
                if self.cor[v] == BRANCO:               # @ignorar_vizinho
                    self.cor[v] = CINZA                 # @pinta_cinza
                    self.d[v] = self.d[u] + 1           # @d_mais_um
                    self.pai[v] = u                     # @pai_v
                    self.fila.append(v)                 # @descobrir_vizinho
            self.cor[u] = PRETO                         # @terminar_vertice
