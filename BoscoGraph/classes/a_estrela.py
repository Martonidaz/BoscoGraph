# Busca A* (A estrela).
#
# Junta as duas ideias:
#   g(v) = o custo do melhor caminho conhecido da origem até v (o que o Dijkstra usa);
#   h(v) = a estimativa de quanto falta de v até o destino (o que a busca gulosa usa);
#   f(v) = g(v) + h(v) = a estimativa do custo TOTAL de um caminho que passa por v.
# Sai da fronteira sempre o vértice de menor f.
#
# Se h nunca passa do custo real até o destino (h ADMISSÍVEL), o A* acha o caminho de menor custo.
# Com h = 0 em todo vértice, f = g e o A* vira o Dijkstra. Quanto melhor a estimativa
# (mais perto do custo real, sem passar dele), menos vértices o A* precisa expandir.
#
# Se h não for "consistente" (h(u) <= peso(u, v) + h(v) em toda aresta), um vértice já expandido
# pode ganhar um caminho mais barato depois: aí ele é REABERTO (volta para a fronteira).
#
# Cores: Branco = ainda não visto; Cinza = na fronteira; Preto = já expandido.

from entrada import INFINITO, formatar_numero


class AEstrela:

    def __init__(self, grafo, passos, heuristica):
        self.lista_adjacencia = grafo.lista_com_pesos       # (vizinho, peso, número da aresta)
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.h = heuristica
        self.cor = {}
        self.g = {}
        self.f = {}
        self.pai = {}
        self.aresta_do_pai = {}
        self.fila = []              # a fronteira (lista aberta): vértices Cinza, na ordem em que entraram
        self.ordem_de_expansao = []
        self.reaberturas = 0
        self.chegou = False
        self.origem = None
        self.destino = None

    def buscar(self, origem, destino):
        self.origem = origem
        self.destino = destino
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.g[vertice] = INFINITO
            self.f[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice}: g = ∞, h = {formatar_numero(self.h[vertice])}, "
                                       f"sem pai", {"vertice": vertice, "h": self.h[vertice]})

        self.g[origem] = 0
        self.f[origem] = self.h[origem]
        self.cor[origem] = "Cinza"
        self.fila.append(origem)
        self.anotar("origem", f"Origem {origem}: g = 0 e f = 0 + {formatar_numero(self.h[origem])} = "
                              f"{formatar_numero(self.f[origem])}, entra na fronteira",
                    {"vertice": origem, "distancia": 0, "prioridade": self.f[origem]})

        while self.fila:
            vertice = self.extrair_minimo()
            self.cor[vertice] = "Preto"
            self.ordem_de_expansao.append(vertice)
            self.anotar("extrair", f"{vertice} sai da fronteira: é o de menor f "
                                   f"({formatar_numero(self.g[vertice])} + {formatar_numero(self.h[vertice])} = "
                                   f"{formatar_numero(self.f[vertice])})", {"vertice": vertice})
            if vertice == destino:
                self.chegou = True
                self.anotar("chegou", f"Chegou ao destino {destino} com custo {formatar_numero(self.g[destino])}: "
                                      f"a busca termina", {"vertice": vertice})
                return
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                self.relaxar(vertice, vizinho, peso, numero)
        self.anotar("nao_chegou", f"A fronteira esvaziou sem chegar em {destino}: não há caminho", {})

    # O menor f da fronteira. Em caso de empate, sai o que entrou primeiro.
    def extrair_minimo(self):
        menor = self.fila[0]
        for vertice in self.fila:
            if self.f[vertice] < self.f[menor]:
                menor = vertice
        self.fila.remove(menor)
        return menor

    # Como o RELAX do Dijkstra, mas a prioridade do vizinho na fila passa a ser f = g + h
    def relaxar(self, vertice, vizinho, peso, numero):
        antes = self.g[vizinho]
        novo = self.g[vertice] + peso
        conta = f"g[{vertice}] + {formatar_numero(peso)} = {formatar_numero(novo)}"
        dados = {"origem": vertice, "destino": vizinho, "aresta": numero, "peso": peso,
                 "antes": antes, "depois": novo, "melhorou": False, "entrou": False, "reabriu": False}
        if novo < self.g[vizinho]:
            self.g[vizinho] = novo
            self.f[vizinho] = novo + self.h[vizinho]
            self.pai[vizinho] = vertice
            dados["aresta_antiga"] = self.aresta_do_pai.get(vizinho)
            self.aresta_do_pai[vizinho] = numero
            dados["melhorou"] = True
            dados["prioridade"] = self.f[vizinho]
            mensagem = (f"Relaxar {self.ligacao(vertice, vizinho)}: {conta} < {formatar_numero(antes)}, "
                        f"então g[{vizinho}] = {formatar_numero(novo)} e f = {formatar_numero(novo)} + "
                        f"{formatar_numero(self.h[vizinho])} = {formatar_numero(self.f[vizinho])}")
            if self.cor[vizinho] == "Branco":
                self.cor[vizinho] = "Cinza"
                self.fila.append(vizinho)
                dados["entrou"] = True
                mensagem += f" ({vizinho} entra na fronteira)"
            elif self.cor[vizinho] == "Preto":
                # Só acontece se h não for consistente: o vértice já expandido volta para a fronteira
                self.cor[vizinho] = "Cinza"
                self.fila.append(vizinho)
                self.reaberturas += 1
                dados["reabriu"] = True
                mensagem += f" ({vizinho} já tinha saído e é reaberto)"
        else:
            mensagem = (f"Relaxar {self.ligacao(vertice, vizinho)}: {conta} não é menor que "
                        f"g[{vizinho}] = {formatar_numero(antes)}, nada muda")
        self.anotar("relaxar", mensagem, dados)

    def ligacao(self, vertice, vizinho):
        if self.direcionado:
            return f"{vertice} -> {vizinho}"
        return f"{vertice} — {vizinho}"

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
