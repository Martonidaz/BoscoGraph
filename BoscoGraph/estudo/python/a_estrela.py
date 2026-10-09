# Busca A* (A estrela): sai da fronteira o vértice de menor f = g + h.
#   g[v]    -> o custo do melhor caminho conhecido de s até v (como o d do Dijkstra)
#   h[v]    -> a estimativa de quanto falta de v até o destino
#   f[v]    -> g[v] + h[v]: a estimativa do custo total de um caminho que passa por v
# Com h admissível (nunca maior que o custo real), o A* acha o caminho de menor custo.
# Se h não for consistente, um vértice já expandido pode ganhar um caminho mais barato:
# aí ele é REABERTO (volta para a fronteira). Devolve True se chegou ao destino.

from decimal import Decimal

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
INFINITO = Decimal("Infinity")


class AEstrela:
    def __init__(self, adj, h):
        self.adj = adj                  # adj[u] = [(v, peso), ...]
        self.h = h
        self.cor = {}
        self.g = {}
        self.f = {}
        self.pai = {}
        self.fila = []

    def buscar(self, s, destino):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.g[v] = INFINITO                        # @g_infinito
            self.f[v] = INFINITO                        # @f_infinito
            self.pai[v] = None                          # @inicializar
        self.g[s] = 0                                   # @origem_g
        self.f[s] = self.h[s]                           # @origem_f
        self.cor[s] = CINZA                             # @origem_cinza
        self.fila.append(s)                             # @origem
        while self.fila:                                # @enquanto_fila
            u = self.extrair_minimo()                   # @chama_extrair
            self.cor[u] = PRETO                         # @extrair
            if u == destino:                            # @se_destino
                return True                             # @chegou
            for v, peso in self.adj[u]:                 # @cada_vizinho
                self.relaxar(u, v, peso)                # @chama_relaxar
        return False                                    # @nao_chegou

    # O vértice da fronteira com o menor f (no empate, o que entrou primeiro)
    def extrair_minimo(self):
        menor = self.fila[0]                            # @menor_primeiro
        for v in self.fila:                             # @cada_da_fila
            if self.f[v] < self.f[menor]:               # @compara_f
                menor = v                               # @novo_menor
        self.fila.remove(menor)                         # @tira_da_fila
        return menor                                    # @devolve_menor

    # Como o RELAX do Dijkstra, mas a prioridade do vizinho passa a ser f = g + h
    def relaxar(self, u, v, peso):
        novo = self.g[u] + peso                         # @soma
        if novo < self.g[v]:                            # @relaxar_nao
            self.g[v] = novo                            # @novo_g
            self.f[v] = novo + self.h[v]                # @relaxar_melhorou
            self.pai[v] = u                             # @pai_v
            if self.cor[v] == BRANCO:                   # @se_branco
                self.cor[v] = CINZA                     # @pinta_cinza
                self.fila.append(v)                     # @entra_na_fila
            elif self.cor[v] == PRETO:                  # @se_preto
                self.cor[v] = CINZA                     # @relaxar_reabriu
                self.fila.append(v)                     # @reentra_na_fila
