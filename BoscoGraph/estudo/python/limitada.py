# Busca em profundidade limitada (DLS), como RECURSIVE-DLS do livro do Russell e Norvig, sem repetir
# vértices do caminho atual (senão a busca andaria em círculo).
#   cor[v]   -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
#   prof[v]  -> a profundidade com que v entrou no caminho (a última vez)
#   pai[v]   -> de onde v entrou no caminho (a última vez)
#   caminho  -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão
#   cortados -> onde o limite cortou (um vértice pode ser cortado mais de uma vez)
# Devolve ACHOU (o caminho até o destino fica em "caminho"), CORTE (o limite cortou algum ramo)
# ou FALHA (não achou, e nenhum limite maior ajudaria).

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
ACHOU = "achou"
CORTE = "corte"
FALHA = "falha"


class ProfundidadeLimitada:
    def __init__(self, adj):
        self.adj = adj                  # lista de adjacência: adj[u] = [v1, v2, ...]
        self.cor = {}
        self.prof = {}
        self.pai = {}
        self.caminho = []
        self.cortados = []

    def buscar(self, s, destino, limite):
        for v in self.adj:                              # @cada_vertice
            self.cor[v] = BRANCO                        # @pinta_branco
            self.pai[v] = None                          # @inicializar
        return self.dls(s, destino, limite, 0)          # @chama_dls

    # Desce no máximo "limite" arestas a partir de u (prof = a profundidade de u)
    def dls(self, u, destino, limite, prof):
        self.cor[u] = CINZA                             # @entrar
        self.prof[u] = prof                             # @anota_prof
        self.caminho.append(u)                          # @empilha
        if u == destino:                                # @testa_destino
            return ACHOU                                # @chegou
        if limite == 0:                                 # @testa_limite
            self.caminho.pop()                          # @desempilha_cortado
            self.cor[u] = PRETO                         # @pinta_cortado
            self.cortados.append(u)                     # @corte
            return CORTE                                # @devolve_corte
        houve_corte = False                             # @sem_corte
        for v in self.adj[u]:                           # @cada_vizinho
            if v in self.caminho:                       # @ignorar_vizinho
                continue                                # @pula_vizinho
            self.pai[v] = u                             # @pai_v
            resultado = self.dls(v, destino, limite - 1, prof + 1)      # @desce
            if resultado == ACHOU:                      # @se_achou
                return ACHOU                            # @repassa_achou
            if resultado == CORTE:                      # @se_cortou
                houve_corte = True                      # @houve_corte
        self.caminho.pop()                              # @desempilha
        self.cor[u] = PRETO                             # @subir
        if houve_corte:                                 # @se_houve_corte
            return CORTE                                # @devolve_corte_de_baixo
        return FALHA                                    # @devolve_falha
