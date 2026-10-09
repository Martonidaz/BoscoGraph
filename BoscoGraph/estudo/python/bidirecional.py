# Busca bidirecional: duas buscas em largura, uma a partir da origem s (a "frente") e outra a partir
# do destino t ("trás"). Elas se revezam, cada vez expandindo UMA CAMADA INTEIRA (todos os que estão
# na fila daquele lado), até um lado achar um vértice que o outro já descobriu: o encontro.
#   cor[v]      -> BRANCO (ninguém descobriu), CINZA (na fila de um dos lados) ou PRETO (expandido)
#   lado[v]     -> FRENTE ou TRAS: qual das buscas descobriu v (None = nenhuma)
#   d[v]        -> arestas de s até v (frente);  d_tras[v] -> arestas de v até t (trás)
#   pai[v]      -> de onde a frente chegou em v;  pai_tras[v] -> o próximo vértice de v até t
#   encontro    -> (u, v): u estava sendo expandido e v já era do outro lado
# O lado de trás anda pelas arestas AO CONTRÁRIO: adj_tras[v] = quem chega em v.
# Devolve True (as buscas se encontraram: existe caminho) ou False.

from collections import deque
from decimal import Decimal

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
FRENTE = "frente"
TRAS = "tras"
INFINITO = Decimal("Infinity")


class BuscaBidirecional:
    def __init__(self, adj, adj_tras):
        self.adj = adj                  # adj[u] = [(v, peso), ...]: quem sai de u (a busca não usa o peso)
        self.adj_tras = adj_tras        # adj_tras[v] = [(u, peso), ...]: quem chega em v
        self.cor = {}
        self.lado = {}
        self.d = {}
        self.d_tras = {}
        self.pai = {}
        self.pai_tras = {}
        self.fila = deque()
        self.fila_tras = deque()
        self.encontro = None

    def buscar(self, s, t):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.lado[v] = None                         # @sem_lado
            self.d[v] = INFINITO                        # @d_infinito
            self.d_tras[v] = INFINITO                   # @d_tras_infinito
            self.pai[v] = None                          # @pai_nulo
            self.pai_tras[v] = None                     # @inicializar
        self.cor[s] = CINZA                             # @origem_cinza
        self.lado[s] = FRENTE                           # @origem_lado
        self.d[s] = 0                                   # @origem_d
        self.fila.append(s)                             # @origem
        if s == t:                                      # @mesmo_vertice
            self.encontro = (s, s)                      # @encontro_na_origem
            return True                                 # @devolve_na_origem
        self.cor[t] = CINZA                             # @destino_cinza
        self.lado[t] = TRAS                             # @destino_lado
        self.d_tras[t] = 0                              # @destino_d
        self.fila_tras.append(t)                        # @origem_tras
        while self.fila and self.fila_tras:             # @enquanto_filas
            if self.expandir(FRENTE):                   # @expande_frente
                return True                             # @achou_pela_frente
            if self.expandir(TRAS):                     # @expande_tras
                return True                             # @achou_por_tras
        return False                                    # @sem_encontro

    # Expande uma camada inteira de um lado; devolve True se encontrou o outro lado
    def expandir(self, lado):
        if lado == FRENTE:                              # @qual_lado
            fila, adj, d, pai, outro = self.fila, self.adj, self.d, self.pai, TRAS              # @usa_frente
        else:
            fila, adj, d, pai, outro = self.fila_tras, self.adj_tras, self.d_tras, self.pai_tras, FRENTE    # @usa_tras
        tamanho = len(fila)                             # @nova_camada
        for vez in range(tamanho):                      # @cada_da_camada
            u = fila.popleft()                          # @desenfileirar
            for v, peso in adj[u]:                      # @cada_vizinho
                if self.lado[v] == outro:               # @se_do_outro_lado
                    self.encontro = (u, v)              # @encontro
                    return True                         # @devolve_encontro
                if self.cor[v] == BRANCO:               # @ignorar_vizinho
                    self.cor[v] = CINZA                 # @pinta_cinza
                    self.lado[v] = lado                 # @anota_lado
                    d[v] = d[u] + 1                     # @d_mais_um
                    pai[v] = u                          # @pai_v
                    fila.append(v)                      # @descobrir_vizinho
            self.cor[u] = PRETO                         # @terminar_vertice
        return False                                    # @camada_sem_encontro
