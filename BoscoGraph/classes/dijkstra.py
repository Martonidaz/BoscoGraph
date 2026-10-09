# Algoritmo de Dijkstra (caminhos mínimos a partir de uma origem), como no CLRS,
# na versão "busca de custo uniforme": a fila de prioridade só guarda os vértices já alcançados.
#
# Ideia: d[v] é o menor custo CONHECIDO até agora para ir da origem até v.
# A cada rodada sai da fila o vértice de MENOR d. Como nenhum peso é negativo, nenhum caminho
# que passe por outro vértice da fila pode ficar mais barato que isso: o d dele é definitivo.
# Depois, cada aresta que sai dele é "relaxada": se passar por ele deixa o vizinho mais barato,
# o d do vizinho diminui e o pai do vizinho passa a ser ele.
#
# Cores: Branco = ainda não alcançado (d = ∞); Cinza = na fila, com d provisório;
# Preto = saiu da fila, com d definitivo.

from entrada import INFINITO, formatar_numero


class Dijkstra:

    def __init__(self, grafo, passos):
        self.lista_adjacencia = grafo.lista_com_pesos       # (vizinho, peso, número da aresta)
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.cor = {}
        self.d = {}                 # menor custo conhecido desde a origem; INFINITO = não alcançado
        self.pai = {}               # π: o vértice anterior no melhor caminho conhecido
        self.aresta_do_pai = {}     # o número da aresta pai -> vértice
        self.fila = []              # a fila de prioridade: os vértices Cinza, na ordem em que entraram
        self.ordem_de_extracao = [] # em que ordem os vértices ficaram definitivos
        self.origem = None

    # DIJKSTRA(G, w, s)
    def dijkstra(self, origem):
        self.origem = origem

        # INITIALIZE-SINGLE-SOURCE: todo vértice começa com d = ∞ e sem pai
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.d[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice}: d = ∞ e sem pai (Branco: ainda não alcançado)",
                        {"vertice": vertice})

        # A origem custa 0 para ela mesma e é a primeira a entrar na fila
        self.d[origem] = 0
        self.cor[origem] = "Cinza"
        self.fila.append(origem)
        self.anotar("origem", f"Origem {origem}: d = 0, entra na fila de prioridade",
                    {"vertice": origem, "distancia": 0, "prioridade": 0})

        while self.fila:
            vertice = self.extrair_minimo()
            self.cor[vertice] = "Preto"            # o d dele não muda mais
            self.ordem_de_extracao.append(vertice)
            self.anotar("extrair", f"{vertice} sai da fila com o menor d ({formatar_numero(self.d[vertice])}): "
                                   f"essa distância é definitiva", {"vertice": vertice})
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                self.relaxar(vertice, vizinho, peso, numero)

    # EXTRACT-MIN: o vértice da fila com o menor d. Em caso de empate, sai o que entrou primeiro.
    # (Percorrer a lista toda custa O(V) por extração. Com um heap, como o heapq do Python,
    # custaria O(log V), mas a lista deixa a fila visível do jeito que aparece na tela.)
    def extrair_minimo(self):
        menor = self.fila[0]
        for vertice in self.fila:
            if self.d[vertice] < self.d[menor]:
                menor = vertice
        self.fila.remove(menor)
        return menor

    # RELAX(u, v, w): passar por "vertice" deixa o caminho até "vizinho" mais barato?
    def relaxar(self, vertice, vizinho, peso, numero):
        antes = self.d[vizinho]
        novo = self.d[vertice] + peso
        conta = f"d[{vertice}] + {formatar_numero(peso)} = {formatar_numero(novo)}"
        dados = {"origem": vertice, "destino": vizinho, "aresta": numero, "peso": peso,
                 "antes": antes, "depois": novo, "melhorou": False, "entrou": False,
                 "finalizado": self.cor[vizinho] == "Preto"}
        if novo < self.d[vizinho]:
            self.d[vizinho] = novo
            self.pai[vizinho] = vertice
            dados["aresta_antiga"] = self.aresta_do_pai.get(vizinho)    # a aresta que deixa de ser a do pai
            self.aresta_do_pai[vizinho] = numero
            dados["melhorou"] = True
            dados["prioridade"] = novo
            mensagem = (f"Relaxar {self.ligacao(vertice, vizinho)}: {conta} < {formatar_numero(antes)}, "
                        f"então d[{vizinho}] = {formatar_numero(novo)} e o pai de {vizinho} é {vertice}")
            if self.cor[vizinho] == "Branco":
                self.cor[vizinho] = "Cinza"
                self.fila.append(vizinho)
                dados["entrou"] = True
                mensagem += f" ({vizinho} entra na fila)"
        else:
            mensagem = (f"Relaxar {self.ligacao(vertice, vizinho)}: {conta} não é menor que "
                        f"d[{vizinho}] = {formatar_numero(antes)}, nada muda")
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
