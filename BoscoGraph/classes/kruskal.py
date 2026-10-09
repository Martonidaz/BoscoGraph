# Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do CLRS.
#
# Ideia: começa com cada vértice sozinho (uma floresta de árvores de um vértice só) e examina as arestas
# da mais leve para a mais pesada. A aresta que liga dois PEDAÇOS diferentes entra na árvore (e os dois
# pedaços viram um só); a aresta cujas pontas já estão no mesmo pedaço fecharia um ciclo e fica de fora.
#
# Os pedaços são CONJUNTOS DISJUNTOS (nenhum vértice está em dois): conjunto[v] é o "representante" do
# conjunto de v, um vértice que dá nome ao conjunto. As três operações do livro:
#   MAKE-SET(v)  -> conjunto[v] = v (v sozinho)
#   FIND-SET(v)  -> conjunto[v]
#   UNION(a, b)  -> todos os vértices do conjunto b passam a ter o representante a
# (Aqui a UNION percorre todos os vértices: O(V). O livro usa uma floresta de conjuntos, com união por
# posto e compressão de caminho, em que cada operação fica quase O(1).)
#
# Empates (arestas de mesmo peso): ficam na ordem em que foram criadas (a ordenação do Python é estável).

from entrada import formatar_numero


class Kruskal:

    def __init__(self, grafo, passos):
        self.vertices = list(grafo.grafo)           # os nomes, na ordem em que foram criados
        self.arestas = grafo.arestas                # os objetos Aresta, na ordem em que foram criados
        self.passos = passos
        self.conjunto = {}                          # o representante do conjunto de cada vértice
        self.arvore = []                            # os números das arestas aceitas, na ordem em que entraram

    # MST-KRUSKAL(G, w)
    def kruskal(self):
        # MAKE-SET: cada vértice começa sozinho, no seu próprio conjunto
        for vertice in self.vertices:
            self.conjunto[vertice] = vertice
            self.anotar("criar_conjunto", f"MAKE-SET({vertice}): {vertice} começa sozinho, no conjunto {{{vertice}}}",
                        {"vertice": vertice})

        # As arestas em ordem de peso (os números delas: o número diz qual aresta pintar no desenho)
        numeros = list(range(len(self.arestas)))
        numeros.sort(key=self.peso_da_aresta)
        textos = []
        for numero in numeros:
            textos.append(f"{self.texto_da_aresta(numero)} ({formatar_numero(self.arestas[numero].peso)})")
        mensagem = "Arestas da mais leve para a mais pesada: " + ", ".join(textos)
        if not numeros:
            mensagem = "O grafo não tem arestas: cada vértice fica sozinho"
        self.anotar("ordenar_arestas", mensagem, {"ordem": list(numeros)})

        for numero in numeros:
            aresta = self.arestas[numero]
            u = aresta.vertice_origem.nome
            v = aresta.vertice_destino.nome
            peso = aresta.peso
            if self.conjunto[u] == self.conjunto[v]:
                # FIND-SET(u) = FIND-SET(v): u e v já estão ligados pelas arestas escolhidas
                if u == v:
                    mensagem = f"{self.texto_da_aresta(numero)} (peso {formatar_numero(peso)}) é um laço: fica de fora"
                else:
                    mensagem = (f"{self.texto_da_aresta(numero)} (peso {formatar_numero(peso)}): {u} e {v} já estão no "
                                f"mesmo conjunto {self.texto_do_conjunto(self.conjunto[u])}, fecharia um ciclo")
                self.anotar("rejeitar", mensagem, {"aresta": numero, "origem": u, "destino": v, "peso": peso,
                                                   "membros": self.membros(self.conjunto[u])})
                continue
            self.arvore.append(numero)
            mensagem = (f"{self.texto_da_aresta(numero)} (peso {formatar_numero(peso)}): {u} está em "
                        f"{self.texto_do_conjunto(self.conjunto[u])} e {v} em {self.texto_do_conjunto(self.conjunto[v])}, "
                        f"conjuntos diferentes: a aresta entra na árvore")
            self.anotar("aceitar", mensagem, {"aresta": numero, "origem": u, "destino": v, "peso": peso,
                                              "membros_u": self.membros(self.conjunto[u]),
                                              "membros_v": self.membros(self.conjunto[v])})
            self.unir(self.conjunto[u], self.conjunto[v], u, v, numero)

    # UNION: todos os vértices do conjunto b passam para o conjunto a
    def unir(self, a, b, u, v, numero):
        mudaram = []
        for x in self.vertices:
            if self.conjunto[x] == b:
                self.conjunto[x] = a
                mudaram.append(x)
        mensagem = (f"UNION: os conjuntos de {u} e de {v} viram um só, {self.texto_do_conjunto(a)} "
                    f"(representante {a})")
        self.anotar("unir", mensagem, {"aresta": numero, "origem": u, "destino": v, "fica": a, "sai": b,
                                       "mudaram": mudaram, "membros": self.membros(a)})

    # O critério da ordenação: o peso da aresta de número "numero"
    def peso_da_aresta(self, numero):
        return self.arestas[numero].peso

    # Os vértices de um conjunto (pelo representante), na ordem em que foram criados
    def membros(self, representante):
        lista = []
        for vertice in self.vertices:
            if self.conjunto[vertice] == representante:
                lista.append(vertice)
        return lista

    # "{a, b, h}"
    def texto_do_conjunto(self, representante):
        return "{" + ", ".join(self.membros(representante)) + "}"

    def texto_da_aresta(self, numero):
        aresta = self.arestas[numero]
        return f"{aresta.vertice_origem.nome} — {aresta.vertice_destino.nome}"

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
