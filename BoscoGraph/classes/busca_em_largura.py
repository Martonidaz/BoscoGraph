# Busca em largura (BFS), como o BFS(G, s) do CLRS.
#
# A partir da origem s, a busca descobre primeiro todos os vizinhos de s, depois os vizinhos
# dos vizinhos, e assim por diante, em "camadas". Quem garante essa ordem é uma FILA:
# o primeiro que entra é o primeiro que sai (como a fila de um caixa).
#
# Cores, como na DFS: Branco = ainda não descoberto; Cinza = descoberto, esperando na fila;
# Preto = já saiu da fila e teve todos os vizinhos examinados.
#
# Resultado: d[v] = o MENOR NÚMERO DE ARESTAS de s até v (a BFS não olha os pesos)
# e pai[v] (π no pseudocódigo), que forma a árvore da BFS.

from entrada import INFINITO


class BuscaEmLargura:

    def __init__(self, grafo, passos):
        # A lista com pesos traz o número de cada aresta, para o desenho pintar a aresta certa.
        # A BFS não usa o peso (por isso ele aparece como "peso" e fica sem uso no laço).
        self.lista_adjacencia = grafo.lista_com_pesos
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.cor = {}
        self.d = {}                 # distância (em arestas) desde a origem; INFINITO = não alcançado
        self.pai = {}               # π: de qual vértice a busca chegou; a origem não tem pai
        self.aresta_do_pai = {}     # o número da aresta pai -> vértice (usado no desenho e no resultado)
        self.fila = []              # a fila da BFS: entra no fim, sai do começo
        self.origem = None

    # BFS(G, s)
    def bfs(self, origem):
        self.origem = origem

        # Começo: todo vértice Branco, com distância infinita e sem pai
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.d[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice} pintado de Branco: d = ∞ e sem pai",
                        {"vertice": vertice})

        # A origem é descoberta com distância 0 e entra na fila
        self.cor[origem] = "Cinza"
        self.d[origem] = 0
        self.fila.append(origem)
        self.anotar("origem", f"Origem {origem} descoberta (Cinza) com d = 0: entra na fila",
                    {"vertice": origem, "distancia": 0})

        while self.fila:                            # enquanto a fila não estiver vazia
            vertice = self.fila.pop(0)              # pop(0) tira o PRIMEIRO da fila (o mais antigo)
            self.anotar("desenfileirar", f"{vertice} sai da frente da fila (d = {self.d[vertice]}): "
                                         f"agora os vizinhos dele", {"vertice": vertice})
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                if self.cor[vizinho] == "Branco":
                    # Primeira vez que a busca vê esse vizinho: ele fica uma camada depois deste vértice
                    self.cor[vizinho] = "Cinza"
                    self.d[vizinho] = self.d[vertice] + 1
                    self.pai[vizinho] = vertice
                    self.aresta_do_pai[vizinho] = numero
                    self.fila.append(vizinho)       # entra no FIM da fila
                    self.anotar("descobrir_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho)}: {vizinho} está Branco, descoberto "
                                f"com d = {self.d[vizinho]} (pai {vertice}) e entra no fim da fila",
                                {"origem": vertice, "destino": vizinho, "aresta": numero,
                                 "distancia": self.d[vizinho]})
                else:
                    # Já descoberto: a BFS não descobre ninguém duas vezes
                    self.anotar("ignorar_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho)}: {vizinho} já foi descoberto "
                                f"({self.cor[vizinho]}), nada muda",
                                {"origem": vertice, "destino": vizinho, "aresta": numero})
            self.cor[vertice] = "Preto"
            self.anotar("terminar_vertice", f"Vértice {vertice} finalizado (Preto): todos os vizinhos foram vistos",
                        {"vertice": vertice})

    # Como a aresta aparece na mensagem: A -> B no orientado e A — B no não orientado
    def ligacao(self, vertice, vizinho):
        if self.direcionado:
            return f"{vertice} -> {vizinho}"
        return f"{vertice} — {vizinho}"

    # Acrescenta um passo com as informações dadas (tipo, mensagem e o que mais vier)
    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
