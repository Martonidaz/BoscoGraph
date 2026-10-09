# Algoritmo de Bellman-Ford, como BELLMAN-FORD(G, w, s) do livro do Cormen (CLRS).
# Aceita pesos negativos: em cada rodada relaxa TODAS as arestas; |V| − 1 rodadas bastam.
# Se depois disso alguma aresta ainda diminui uma distância, há um CICLO NEGATIVO alcançável.
# Devolve True (sem ciclo negativo) ou False (com ciclo negativo), como no livro.
# Melhoria: se uma rodada não muda nada, as próximas também não mudariam, e a busca para antes.
#   arcos   -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos

from decimal import Decimal

INFINITO = Decimal("Infinity")


class BellmanFord:
    def __init__(self, vertices, arcos):
        self.vertices = vertices        # os nomes dos vértices
        self.arcos = arcos              # [(u, v, peso), ...]
        self.d = {}
        self.pai = {}

    def bellman_ford(self, s):
        for v in self.vertices:                         # @cada_vertice
            self.d[v] = INFINITO                        # @d_infinito
            self.pai[v] = None                          # @inicializar
        self.d[s] = 0                                   # @origem
        parou_antes = False                             # @parou_falso
        for rodada in range(1, len(self.vertices)):     # @rodada
            mudou = False                               # @mudou_falso
            for u, v, peso in self.arcos:               # @cada_arco
                if self.d[u] + peso < self.d[v]:        # @relaxar_nao
                    self.d[v] = self.d[u] + peso        # @relaxar_melhorou
                    self.pai[v] = u                     # @pai_v
                    mudou = True                        # @mudou
            if not mudou:                               # @se_nao_mudou
                parou_antes = True                      # @rodada_sem_mudanca
                break                                   # @para
        if not parou_antes:                             # @se_nao_parou
            for u, v, peso in self.arcos:               # @verificar_ciclo
                if self.d[u] + peso < self.d[v]:        # @ainda_diminui
                    return False                        # @ciclo_negativo
        return True                                     # @sem_ciclo_negativo
