# Busca em profundidade (DFS), como DFS(G) e DFS-VISIT(G, u) do livro do Cormen (CLRS).
#   cor[u]  -> BRANCO (não descoberto), CINZA (em exploração) ou PRETO (terminado)
#   d[u]    -> o tempo em que u foi descoberto;  f[u] -> o tempo em que u terminou
#   pai[u]  -> de qual vértice a busca chegou em u (o π do livro)
#   tempo   -> o relógio da busca: anda 1 a cada descoberta e a cada término
#   tipo    -> o tipo de cada aresta examinada (u, v): árvore, retorno, avanço ou cruzamento
#              (com duas arestas paralelas de u para v, fica o tipo da última)
# No grafo NÃO orientado, a aresta u — v está na lista de u e na de v. Quando a busca a examina
# por um lado, "voltas" anota que a outra metade é a mesma aresta (para não contá-la de novo).

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"


class BuscaEmProfundidade:
    def __init__(self, adj, direcionado):
        self.adj = adj                  # lista de adjacência: adj[u] = [v1, v2, ...]
        self.direcionado = direcionado
        self.cor = {}
        self.d = {}
        self.f = {}
        self.pai = {}
        self.tempo = 0
        self.voltas = {}
        self.tipo = {}

    def dfs(self, ordem):
        for u in self.adj:                              # @pinta_cada
            self.cor[u] = BRANCO                        # @pintar_branco
            self.pai[u] = None                          # @pai_nulo
        self.tempo = 0                                  # @zerar_tempo
        for u in ordem:                                 # @cada_raiz
            if self.cor[u] == BRANCO:                   # @raiz_branca
                self.dfs_visit(u)                       # @nova_arvore

    def dfs_visit(self, u):
        self.tempo = self.tempo + 1                     # @tempo_d
        self.d[u] = self.tempo                          # @anota_d
        self.cor[u] = CINZA                             # @descobrir
        for v in self.adj[u]:                           # @cada_vizinho
            if self.voltas.get((u, v), 0) > 0:          # @e_volta
                self.voltas[(u, v)] -= 1                # @revisitar
            elif self.cor[v] == BRANCO:                 # @vizinho_branco
                self.tipo[(u, v)] = "árvore"            # @examinar_arvore
                self.anotar_volta(u, v)                 # @volta_arvore
                self.pai[v] = u                         # @pai_v
                self.dfs_visit(v)                       # @desce
            else:
                self.tipo[(u, v)] = self.classificar(u, v)      # @examinar_outra
                self.anotar_volta(u, v)                         # @volta_outra
        self.cor[u] = PRETO                             # @pintar_preto
        self.tempo = self.tempo + 1                     # @tempo_f
        self.f[u] = self.tempo                          # @finalizar

    # A aresta u -> v leva a um vértice já descoberto: retorno, avanço ou cruzamento
    def classificar(self, u, v):
        if self.cor[v] == CINZA:                        # @se_cinza
            return "retorno"                            # @retorno
        if self.d[u] < self.d[v]:                       # @se_descendente
            return "avanço"                             # @avanco
        return "cruzamento"                             # @cruzamento

    # Só no não orientado (e fora do laço): a outra metade da aresta, v — u, fica anotada
    def anotar_volta(self, u, v):
        if not self.direcionado and u != v:                         # @se_nao_orientado
            self.voltas[(v, u)] = self.voltas.get((v, u), 0) + 1    # @anota_volta
