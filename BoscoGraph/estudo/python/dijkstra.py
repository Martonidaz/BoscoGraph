# Algoritmo de Dijkstra, como DIJKSTRA(G, w, s) do livro do Cormen (CLRS), na versão em que a fila
# de prioridade só guarda os vértices já alcançados ("busca de custo uniforme").
#   d[v]    -> o menor custo conhecido de s até v (INFINITO = ainda não alcançado)
#   pai[v]  -> o vértice anterior no melhor caminho conhecido (o π do livro)
#   cor[v]  -> BRANCO (não alcançado), CINZA (na fila) ou PRETO (d definitivo)
# A fila é uma lista: EXTRACT-MIN percorre todos, O(V). Com um heap seria O(log V).
# Os pesos são Decimal (números decimais exatos): 0,1 + 0,2 dá exatamente 0,3.

from decimal import Decimal

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
INFINITO = Decimal("Infinity")


class Dijkstra:
    def __init__(self, adj):
        self.adj = adj                  # adj[u] = [(v, peso), ...]
        self.cor = {}
        self.d = {}
        self.pai = {}
        self.fila = []

    def dijkstra(self, s):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.d[v] = INFINITO                        # @d_infinito
            self.pai[v] = None                          # @inicializar
        self.d[s] = 0                                   # @origem_d
        self.cor[s] = CINZA                             # @origem_cinza
        self.fila.append(s)                             # @origem
        while self.fila:                                # @enquanto_fila
            u = self.extrair_minimo()                   # @chama_extrair
            self.cor[u] = PRETO                         # @extrair
            for v, peso in self.adj[u]:                 # @cada_vizinho
                self.relaxar(u, v, peso)                # @chama_relaxar

    # EXTRACT-MIN: o vértice da fila com o menor d (no empate, o que entrou primeiro)
    def extrair_minimo(self):
        menor = self.fila[0]                            # @menor_primeiro
        for v in self.fila:                             # @cada_da_fila
            if self.d[v] < self.d[menor]:               # @compara_d
                menor = v                               # @novo_menor
        self.fila.remove(menor)                         # @tira_da_fila
        return menor                                    # @devolve_menor

    # RELAX(u, v, w): passar por u deixa o caminho até v mais barato?
    def relaxar(self, u, v, peso):
        novo = self.d[u] + peso                         # @soma
        if novo < self.d[v]:                            # @relaxar_nao
            self.d[v] = novo                            # @relaxar_melhorou
            self.pai[v] = u                             # @pai_v
            if self.cor[v] == BRANCO:                   # @se_branco
                self.cor[v] = CINZA                     # @pinta_cinza
                self.fila.append(v)                     # @entra_na_fila
