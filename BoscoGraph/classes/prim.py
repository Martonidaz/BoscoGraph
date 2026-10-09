# Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do CLRS, na mesma forma do Dijkstra
# daqui: a fila de prioridade só guarda os vértices já alcançados.
#
# Ideia: a árvore cresce a partir da raiz, um vértice por vez. chave[v] é o peso da aresta MAIS LEVE
# conhecida que liga v a algum vértice que já está na árvore (∞ = nenhuma ainda). A cada rodada sai da
# fila o vértice de MENOR chave: ele entra na árvore pela aresta do pai (π). Depois, cada aresta que sai
# dele pode deixar mais barata a ligação de um vizinho que ainda está fora da árvore.
#
# A diferença para o Dijkstra: lá a prioridade é a distância desde a origem (d[u] + peso); aqui é só o
# peso da aresta. E aqui um vizinho que JÁ ESTÁ na árvore (Preto) é pulado: a aresta até ele pode até
# ser mais leve que a chave dele, mas ligaria dois vértices da árvore (fecharia um ciclo).
#
# Grafo desligado: quando a fila esvazia e ainda sobra vértice Branco, ele vira a raiz de uma árvore
# nova (como no laço de fora do DFS(G)). O resultado é a floresta geradora mínima: uma árvore por parte.
#
# Cores: Branco = fora da árvore, sem ligação conhecida (chave = ∞); Cinza = na fila, com a chave
# provisória; Preto = já está na árvore.

from entrada import INFINITO, formatar_numero


class Prim:

    def __init__(self, grafo, passos):
        self.lista_adjacencia = grafo.lista_com_pesos       # (vizinho, peso, número da aresta)
        self.passos = passos
        self.cor = {}
        self.chave = {}             # o peso da aresta mais leve que liga o vértice à árvore (INFINITO = nenhuma)
        self.pai = {}               # π: a outra ponta dessa aresta, que já está na árvore
        self.aresta_do_pai = {}     # o número da aresta pai — vértice
        self.fila = []              # a fila de prioridade: os vértices Cinza, na ordem em que entraram
        self.ordem_de_extracao = [] # em que ordem os vértices entraram na árvore
        self.raizes = []            # a raiz de cada árvore (mais de uma se o grafo for desligado)

    # MST-PRIM(G, w, r), com o laço de fora dos grafos desligados.
    # A raiz escolhida vem primeiro; depois, os outros vértices em ordem alfabética: cada um que ainda
    # estiver Branco começa uma árvore nova (como o DFS(G) faz com as raízes).
    def prim(self, inicio):
        ordem = sorted(self.lista_adjacencia)
        if inicio in ordem:
            ordem.remove(inicio)
            ordem.insert(0, inicio)

        # Todo vértice começa fora da árvore: chave = ∞ e sem pai
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.chave[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice}: chave = ∞ e sem pai (Branco: fora da árvore)",
                        {"vertice": vertice})

        for raiz in ordem:
            if self.cor[raiz] == "Branco":
                self.crescer(raiz)

    # A árvore que começa na raiz cresce até a fila esvaziar (até todos da parte dela entrarem)
    def crescer(self, raiz):
        self.raizes.append(raiz)
        self.chave[raiz] = 0
        self.cor[raiz] = "Cinza"
        self.fila.append(raiz)
        if len(self.raizes) == 1:
            mensagem = f"Raiz {raiz}: chave = 0, entra na fila de prioridade (a árvore começa nela)"
        else:
            mensagem = (f"{raiz} ainda está fora: o grafo tem outra parte, desligada das anteriores. {raiz} é a raiz "
                        f"de uma árvore nova (chave = 0)")
        self.anotar("raiz", mensagem, {"vertice": raiz, "chave": 0, "prioridade": 0, "arvore": len(self.raizes)})

        while self.fila:
            vertice = self.extrair_minimo()
            self.cor[vertice] = "Preto"            # entrou na árvore: não muda mais
            self.ordem_de_extracao.append(vertice)
            pai = self.pai[vertice]
            if pai is None:
                mensagem = f"{vertice} sai da fila e é o primeiro vértice da árvore (a raiz)"
            else:
                mensagem = (f"{vertice} sai da fila com a menor chave ({formatar_numero(self.chave[vertice])}) e entra "
                            f"na árvore pela aresta {pai} — {vertice}")
            self.anotar("extrair", mensagem, {"vertice": vertice, "pai": pai, "chave": self.chave[vertice],
                                               "aresta": self.aresta_do_pai.get(vertice)})
            for vizinho, peso, numero in self.lista_adjacencia[vertice]:
                if self.cor[vizinho] == "Preto":
                    self.ignorar(vertice, vizinho, peso, numero)
                else:
                    self.atualizar(vertice, vizinho, peso, numero)

    # EXTRACT-MIN: o vértice da fila com a menor chave. Em caso de empate, sai o que entrou primeiro.
    # (Percorrer a lista toda custa O(V) por extração. Com um heap, como o heapq do Python, custaria
    # O(log V), mas a lista deixa a fila visível do jeito que aparece na tela.)
    def extrair_minimo(self):
        menor = self.fila[0]
        for vertice in self.fila:
            if self.chave[vertice] < self.chave[menor]:
                menor = vertice
        self.fila.remove(menor)
        return menor

    # O vizinho já está na árvore: a aresta ligaria dois vértices da árvore (fecharia um ciclo)
    def ignorar(self, vertice, vizinho, peso, numero):
        if vizinho == vertice:
            mensagem = f"{vertice} — {vertice} é um laço: ligaria {vertice} a ele mesmo, fica de fora"
        elif self.aresta_do_pai.get(vertice) == numero:
            mensagem = f"{vizinho} já está na árvore: {vertice} — {vizinho} é a aresta por onde {vertice} acabou de entrar"
        else:
            mensagem = (f"{vizinho} já está na árvore: a aresta {vertice} — {vizinho} ligaria dois vértices da árvore "
                        f"(fecharia um ciclo), fica de fora")
        self.anotar("ignorar_vizinho", mensagem, {"origem": vertice, "destino": vizinho, "aresta": numero,
                                                   "peso": peso})

    # A aresta vertice — vizinho deixa mais barata a ligação do vizinho com a árvore?
    def atualizar(self, vertice, vizinho, peso, numero):
        antes = self.chave[vizinho]
        dados = {"origem": vertice, "destino": vizinho, "aresta": numero, "peso": peso, "antes": antes,
                 "depois": peso, "melhorou": False, "entrou": False}
        if peso < self.chave[vizinho]:
            self.chave[vizinho] = peso
            self.pai[vizinho] = vertice
            dados["aresta_antiga"] = self.aresta_do_pai.get(vizinho)    # a ligação que deixa de ser a melhor
            self.aresta_do_pai[vizinho] = numero
            dados["melhorou"] = True
            dados["prioridade"] = peso
            mensagem = (f"Aresta {vertice} — {vizinho}: peso {formatar_numero(peso)} < chave[{vizinho}] = "
                        f"{formatar_numero(antes)}, então chave[{vizinho}] = {formatar_numero(peso)} e o pai de "
                        f"{vizinho} é {vertice}")
            if self.cor[vizinho] == "Branco":
                self.cor[vizinho] = "Cinza"
                self.fila.append(vizinho)
                dados["entrou"] = True
                mensagem += f" ({vizinho} entra na fila)"
        else:
            mensagem = (f"Aresta {vertice} — {vizinho}: peso {formatar_numero(peso)} não é menor que "
                        f"chave[{vizinho}] = {formatar_numero(antes)}, nada muda")
        self.anotar("atualizar", mensagem, dados)

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
