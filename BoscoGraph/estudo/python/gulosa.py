# Busca gulosa pela melhor escolha (greedy best-first): sai da fronteira sempre o vértice de
# menor h, a ESTIMATIVA de quanto falta até o destino. Não olha quanto já gastou: costuma chegar
# rápido, mas não garante o caminho de menor custo.
#   h[v]    -> a heurística (estimativa até o destino)
#   cor[v]  -> BRANCO (não visto), CINZA (na fronteira) ou PRETO (já expandido)
#   pai[v]  -> de onde a busca chegou em v
# Devolve True se chegou ao destino.

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"


class BuscaGulosa:
    def __init__(self, adj, h):
        self.adj = adj                  # adj[u] = [(v, peso), ...] (a gulosa não precisa do peso)
        self.h = h
        self.cor = {}
        self.pai = {}
        self.fila = []

    def buscar(self, s, destino):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.pai[v] = None                          # @inicializar
        self.cor[s] = CINZA                             # @origem_cinza
        self.fila.append(s)                             # @origem
        while self.fila:                                # @enquanto_fila
            u = self.extrair_minimo()                   # @chama_extrair
            self.cor[u] = PRETO                         # @extrair
            if u == destino:                            # @se_destino
                return True                             # @chegou
            for v, peso in self.adj[u]:                 # @cada_vizinho
                if self.cor[v] == BRANCO:               # @ignorar_vizinho
                    self.cor[v] = CINZA                 # @pinta_cinza
                    self.pai[v] = u                     # @pai_v
                    self.fila.append(v)                 # @descobrir_vizinho
        return False                                    # @nao_chegou

    # O vértice da fronteira com o menor h (no empate, o que entrou primeiro)
    def extrair_minimo(self):
        menor = self.fila[0]                            # @menor_primeiro
        for v in self.fila:                             # @cada_da_fila
            if self.h[v] < self.h[menor]:               # @compara_h
                menor = v                               # @novo_menor
        self.fila.remove(menor)                         # @tira_da_fila
        return menor                                    # @devolve_menor
