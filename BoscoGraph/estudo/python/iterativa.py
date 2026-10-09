# Busca de aprofundamento iterativo (IDDFS), como ITERATIVE-DEEPENING-SEARCH do livro do Russell e
# Norvig: a busca em profundidade limitada com limite 0, depois 1, depois 2... até não haver corte.
# Acha o destino com o menor número de arestas (como a busca em largura), guardando só o caminho atual.
#   cor[v]   -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
#   prof[v]  -> a profundidade com que v entrou no caminho (a última vez, nesta rodada)
#   pai[v]   -> de onde v entrou no caminho (a última vez, nesta rodada)
#   caminho  -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão
#   cortados -> onde o limite cortou, nesta rodada
# Devolve ACHOU (o caminho fica em "caminho") ou FALHA (o destino não é alcançável).

BRANCO = "Branco"
CINZA = "Cinza"
PRETO = "Preto"
ACHOU = "achou"
CORTE = "corte"
FALHA = "falha"


class AprofundamentoIterativo:
    def __init__(self, adj):
        self.adj = adj                  # lista de adjacência: adj[u] = [v1, v2, ...]
        self.cor = {}
        self.prof = {}
        self.pai = {}
        self.caminho = []
        self.cortados = []

    def buscar(self, s, destino):
        limite = 0                                      # @limite_zero
        while True:                                     # @cada_rodada
            for v in self.adj:                          # @cada_vertice
                self.cor[v] = BRANCO                    # @pinta_branco
                self.pai[v] = None                      # @pai_nulo
            self.prof = {}                              # @zera_prof
            self.caminho = []                           # @esvazia_caminho
            self.cortados = []                          # @nova_iteracao
            resultado = self.dls(s, destino, limite, 0)     # @chama_dls
            if resultado != CORTE:                      # @se_nao_cortou
                return resultado                        # @devolve
            limite = limite + 1                         # @aumenta_limite

    # A mesma busca limitada: desce no máximo "limite" arestas a partir de u
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
