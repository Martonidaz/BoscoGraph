# Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do livro do Cormen (CLRS), na mesma
# forma do Dijkstra daqui: a fila de prioridade só guarda os vértices já alcançados.
#   chave[v] -> o peso da aresta mais leve conhecida que liga v à árvore (INFINITO = nenhuma ainda)
#   pai[v]   -> a outra ponta dessa aresta, que já está na árvore (o π do livro)
#   cor[v]   -> BRANCO (fora, sem ligação), CINZA (na fila) ou PRETO (já está na árvore)
# No livro, o grafo é conexo e a árvore cresce a partir de uma raiz r. Aqui, como no DFS(G), uma árvore
# nova começa em cada parte desligada: as raízes vêm em ordem (a escolhida primeiro) e o resultado é a
# floresta geradora mínima. A fila é uma lista: EXTRACT-MIN percorre todos, O(V). Com um heap seria
# O(log V). Os pesos são Decimal (números decimais exatos): 0,1 + 0,2 dá exatamente 0,3.

from decimal import Decimal

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
INFINITO = Decimal("Infinity")


class Prim:
    def __init__(self, adj):
        self.adj = adj                  # adj[u] = [(v, peso), ...]
        self.cor = {}
        self.chave = {}
        self.pai = {}
        self.fila = []

    def prim(self, raizes):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.chave[v] = INFINITO                    # @chave_infinito
            self.pai[v] = None                          # @inicializar
        for r in raizes:                                # @cada_raiz
            if self.cor[r] == BRANCO:                   # @raiz_branca
                self.crescer(r)                         # @chama_crescer

    # A árvore que começa em r cresce até a fila esvaziar (até todos da parte de r entrarem)
    def crescer(self, r):
        self.chave[r] = 0                               # @raiz_chave
        self.cor[r] = CINZA                             # @raiz_cinza
        self.fila.append(r)                             # @raiz
        while self.fila:                                # @enquanto_fila
            u = self.extrair_minimo()                   # @chama_extrair
            self.cor[u] = PRETO                         # @extrair
            for v, peso in self.adj[u]:                 # @cada_vizinho
                if self.cor[v] == PRETO:                # @ignorar_vizinho
                    continue                            # @pula_vizinho
                if peso < self.chave[v]:                # @atualizar_nao
                    self.chave[v] = peso                # @atualizar_melhorou
                    self.pai[v] = u                     # @pai_v
                    if self.cor[v] == BRANCO:           # @se_branco
                        self.cor[v] = CINZA             # @pinta_cinza
                        self.fila.append(v)             # @entra_na_fila

    # EXTRACT-MIN: o vértice da fila com a menor chave (no empate, o que entrou primeiro)
    def extrair_minimo(self):
        menor = self.fila[0]                            # @menor_primeiro
        for v in self.fila:                             # @cada_da_fila
            if self.chave[v] < self.chave[menor]:       # @compara_chave
                menor = v                               # @novo_menor
        self.fila.remove(menor)                         # @tira_da_fila
        return menor                                    # @devolve_menor
