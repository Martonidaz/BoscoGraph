# Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25):
# o menor custo entre TODOS os pares de vértices, numa matriz.
#   d[i][j]  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
#   pi[i][j] -> o vértice que vem antes de j no melhor caminho de i até j (o π do livro)
# Na rodada de cada vértice k, cada par (i, j) pergunta: passar por k fica mais barato?
# Os pares em que d[i][k] ou d[k][j] é infinito são pulados: passar por k é impossível.
# Aceita pesos negativos. Devolve True, ou False se algum d[i][i] ficar negativo (ciclo negativo).
#   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos.
#            Entre arestas paralelas, a matriz fica com a mais barata.

from decimal import Decimal

INFINITO = Decimal("Infinity")


class FloydWarshall:
    def __init__(self, vertices, arcos):
        self.vertices = vertices        # os nomes dos vértices
        self.arcos = arcos              # [(u, v, peso), ...]
        self.d = {}
        self.pi = {}

    def floyd_warshall(self):
        for i in self.vertices:                         # @cada_linha
            self.d[i] = {}                              # @nova_linha_d
            self.pi[i] = {}                             # @nova_linha_pi
            for j in self.vertices:                     # @cada_coluna
                self.d[i][j] = INFINITO                 # @d_infinito
                self.pi[i][j] = None                    # @pi_nulo
            self.d[i][i] = 0                            # @inicializar_linha
        for u, v, peso in self.arcos:                   # @cada_arco
            if peso < self.d[u][v]:                     # @arco_nao
                self.d[u][v] = peso                     # @arco_melhorou
                self.pi[u][v] = u                       # @pi_do_arco
        for k in self.vertices:                         # @rodada_k
            for i in self.vertices:                     # @cada_i
                for j in self.vertices:                 # @cada_j
                    if self.d[i][k] == INFINITO or self.d[k][j] == INFINITO:    # @passa_por_k
                        continue                        # @pula_par
                    if self.d[i][k] + self.d[k][j] < self.d[i][j]:              # @par_nao
                        self.d[i][j] = self.d[i][k] + self.d[k][j]              # @par_melhorou
                        self.pi[i][j] = self.pi[k][j]                           # @pi_par
        for i in self.vertices:                         # @verifica_diagonal
            if self.d[i][i] < 0:                        # @testa_diagonal
                return False                            # @diagonal_negativa
        return True                                     # @sem_ciclo_negativo
