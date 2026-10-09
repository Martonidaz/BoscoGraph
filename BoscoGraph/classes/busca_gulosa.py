# Busca gulosa pela melhor escolha (greedy best-first search).
#
# Cada vértice tem uma heurística h(v): uma ESTIMATIVA de quanto falta para chegar ao destino
# (por exemplo, a distância em linha reta num mapa). A busca sempre continua pelo vértice da
# fronteira que PARECE estar mais perto do destino (o menor h), sem olhar quanto já gastou.
#
# É a mesma estrutura do Dijkstra (uma fila de prioridade), só muda a prioridade:
#   Dijkstra -> o custo desde a origem (g)
#   Gulosa   -> a estimativa até o destino (h)
#   A*       -> as duas somadas (f = g + h)
# Por olhar só para a frente, a gulosa costuma chegar rápido, mas NÃO garante o caminho de
# menor custo: o resultado (etapa 6) compara com o melhor caminho possível.
#
# Cores: Branco = ainda não visto; Cinza = na fronteira; Preto = já expandido.

from entrada import INFINITO, formatar_numero


class BuscaGulosa:

    def __init__(self, grafo, passos, heuristica):
        self.lista_adjacencia = grafo.lista_com_pesos       # (vizinho, peso, número da aresta)
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.h = heuristica                                 # {vértice: estimativa até o destino}
        self.cor = {}
        self.g = {}                 # o custo do caminho encontrado até cada vértice (só para informar)
        self.pai = {}
        self.aresta_do_pai = {}
        self.fila = []              # a fronteira: vértices Cinza, na ordem em que entraram
        self.ordem_de_expansao = []
        self.chegou = False
        self.origem = None
        self.destino = None
        # A gulosa não precisa dos pesos para decidir. Se todas as arestas tiverem peso,
        # g soma os pesos; se não, g conta as arestas do caminho.
        self.usa_pesos = True
        for vertice in self.lista_adjacencia:
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                if peso is None:
                    self.usa_pesos = False

    def buscar(self, origem, destino):
        self.origem = origem
        self.destino = destino
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.g[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice}: h = {formatar_numero(self.h[vertice])} "
                                       f"(estimativa até {destino}), ainda não visto",
                        {"vertice": vertice, "h": self.h[vertice]})

        self.g[origem] = 0
        self.cor[origem] = "Cinza"
        self.fila.append(origem)
        self.anotar("origem", f"Origem {origem} entra na fronteira com h = {formatar_numero(self.h[origem])}",
                    {"vertice": origem, "distancia": 0, "prioridade": self.h[origem]})

        while self.fila:
            vertice = self.extrair_minimo()
            self.cor[vertice] = "Preto"
            self.ordem_de_expansao.append(vertice)
            self.anotar("extrair", f"{vertice} sai da fronteira: é o de menor h ({formatar_numero(self.h[vertice])})",
                        {"vertice": vertice})
            if vertice == destino:
                self.chegou = True
                self.anotar("chegou", f"Chegou ao destino {destino}: a busca termina", {"vertice": vertice})
                return
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                if self.cor[vizinho] == "Branco":
                    self.cor[vizinho] = "Cinza"
                    self.g[vizinho] = self.g[vertice] + self.custo_da_aresta(peso)
                    self.pai[vizinho] = vertice
                    self.aresta_do_pai[vizinho] = numero
                    self.fila.append(vizinho)
                    self.anotar("descobrir_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho)}: {vizinho} entra na fronteira "
                                f"com h = {formatar_numero(self.h[vizinho])} (pai {vertice})",
                                {"origem": vertice, "destino": vizinho, "aresta": numero,
                                 "distancia": self.g[vizinho], "prioridade": self.h[vizinho]})
                else:
                    # A gulosa não volta atrás: um vértice já visto não muda mais
                    self.anotar("ignorar_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho)}: {vizinho} já foi visto "
                                f"({self.cor[vizinho]}), nada muda",
                                {"origem": vertice, "destino": vizinho, "aresta": numero})
        self.anotar("nao_chegou", f"A fronteira esvaziou sem chegar em {destino}: não há caminho", {})

    # O menor h da fronteira. Em caso de empate, sai o que entrou primeiro.
    def extrair_minimo(self):
        menor = self.fila[0]
        for vertice in self.fila:
            if self.h[vertice] < self.h[menor]:
                menor = vertice
        self.fila.remove(menor)
        return menor

    def custo_da_aresta(self, peso):
        if self.usa_pesos:
            return peso
        return 1

    def ligacao(self, vertice, vizinho):
        if self.direcionado:
            return f"{vertice} -> {vizinho}"
        return f"{vertice} — {vizinho}"

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
