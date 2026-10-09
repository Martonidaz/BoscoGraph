# Nome de cada tipo de aresta para as mensagens
# (as chaves ficam sem acento para não haver erro de digitação no resto do código)
NOME_DA_ARESTA = {
    "arvore": "árvore",
    "retorno": "retorno",
    "avanco": "avanço",
    "cruzamento": "cruzamento",
}


class BuscaEmProfundidade:

    # Recebe o grafo e a lista de passos, e prepara o estado da busca
    def __init__(self, grafo, passos):
        # Estado da busca:
        # cor   -> "Branco" (não descoberto), "Cinza" (em exploração) ou "Preto" (finalizado)
        # d     -> tempo de descoberta de cada vértice
        # f     -> tempo de finalização de cada vértice
        # pai   -> de qual vértice a busca chegou em cada um (π no pseudocódigo); a raiz não tem pai
        # tempo -> relógio da busca: avança 1 a cada descoberta e a cada finalização
        self.lista_adjacencia = grafo.grafo
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.cor = {}
        self.d = {}
        self.f = {}
        self.pai = {}
        self.tempo = 0

        # Anotações que a análise do tipo do grafo usa depois da busca
        self.raizes = []                # a raiz de cada árvore da busca
        self.arestas_de_retorno = []    # (vértice, vizinho) de cada aresta de retorno: cada uma fecha um ciclo

        # Só no não orientado: a aresta A — B está na lista de A e na lista de B.
        # ja_examinada[(B, A)] diz quantas vezes "A na lista de B" é uma aresta
        # que já foi examinada pelo outro lado (de A para B) e não deve contar de novo.
        self.ja_examinada = {}

    # Início do DFS(G) no pseudocódigo: pinta todos os vértices de Branco e zera o relógio.
    # Cada vértice pintado vira um passo, para a pintura aparecer um por um na tela.
    def inicializar(self):
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.passos.append({
                "tipo": "pintar_branco",
                "vertice": vertice,
                "mensagem": f"Vértice {vertice} pintado de Branco (ainda não descoberto)",
            })
        self.tempo = 0
        self.passos.append({
            "tipo": "zerar_tempo",
            "mensagem": "Relógio zerado: tempo = 0",
        })

    # DFS(G): percorre os vértices em ordem alfabética; quem ainda estiver Branco
    # vira a raiz de uma nova árvore. Se um vértice inicial for escolhido, ele vem primeiro.
    def dfs(self, inicio=None):
        self.inicializar()

        ordem = sorted(self.lista_adjacencia)
        if inicio in ordem:
            ordem.remove(inicio)
            ordem.insert(0, inicio)

        for vertice in ordem:
            if self.cor[vertice] == "Branco":
                self.raizes.append(vertice)
                self.pai[vertice] = None
                self.passos.append({
                    "tipo": "nova_arvore",
                    "vertice": vertice,
                    "mensagem": f"Nova árvore de DFS a partir de {vertice}",
                })
                self.dfs_visit(vertice)

    # DFS-VISIT(u): descobre o vértice, examina cada vizinho e depois finaliza o vértice
    def dfs_visit(self, vertice):
        self.descobrir(vertice)
        for vizinho in self.lista_adjacencia[vertice]:
            if self.aresta_ja_examinada(vertice, vizinho):
                # Não orientado: é a mesma aresta que já foi examinada pelo outro lado
                self.anotar_volta(vertice, vizinho)
            elif self.cor[vizinho] == "Branco":
                # Vizinho ainda não descoberto: a aresta entra na árvore e a busca desce para ele.
                # Este vértice fica esperando aqui até o vizinho terminar.
                self.anotar_aresta(vertice, vizinho, "arvore")
                self.pai[vizinho] = vertice
                self.dfs_visit(vizinho)
            else:
                # Vizinho Cinza ou Preto: já foi descoberto, não entra de novo
                tipo_aresta = self.classificar(vertice, vizinho)
                self.anotar_aresta(vertice, vizinho, tipo_aresta)
        self.finalizar(vertice)

    # Classifica uma aresta cujo destino já foi descoberto (Cinza ou Preto)
    def classificar(self, vertice, vizinho):
        if self.cor[vizinho] == "Cinza":
            return "retorno"        # o vizinho ainda está em exploração: a aresta fecha um ciclo
        if self.d[vertice] < self.d[vizinho]:
            return "avanco"         # o vizinho é descendente deste vértice e já terminou
        return "cruzamento"         # o vizinho está em outro ramo e já terminou

    # Só no não orientado: "vizinho" na lista de "vertice" é uma aresta já examinada pelo outro lado?
    # (no orientado o dicionário fica vazio e a resposta é sempre não)
    def aresta_ja_examinada(self, vertice, vizinho):
        return self.ja_examinada.get((vertice, vizinho), 0) > 0

    # Como a aresta aparece na mensagem: A -> B no orientado e A — B no não orientado
    def ligacao(self, vertice, vizinho):
        if self.direcionado:
            return f"{vertice} -> {vizinho}"
        return f"{vertice} — {vizinho}"

    # Anota o exame de uma aresta, com o tipo dela
    def anotar_aresta(self, vertice, vizinho, tipo_aresta):
        nome = NOME_DA_ARESTA[tipo_aresta]
        aresta = self.ligacao(vertice, vizinho)
        if tipo_aresta == "arvore":
            mensagem = f"Aresta {aresta}: {vizinho} está Branco, avançando (aresta de {nome})"
        else:
            # Duas strings seguidas dentro de parênteses viram uma só (linha longa quebrada em duas)
            mensagem = (f"Aresta {aresta}: {vizinho} está {self.cor[vizinho]}, "
                        f"não revisitado (aresta de {nome})")
        self.passos.append({
            "tipo": "examinar",
            "origem": vertice,
            "destino": vizinho,
            "classe": tipo_aresta,
            "mensagem": mensagem,
        })
        if tipo_aresta == "retorno":
            self.arestas_de_retorno.append((vertice, vizinho))

        # Não orientado: quando a busca chegar na lista do vizinho, este vértice vai aparecer lá.
        # É a mesma aresta, então fica anotado que ela já foi examinada.
        # (o laço aparece uma vez só na lista, por isso não tem essa "volta")
        if not self.direcionado and vertice != vizinho:
            chave = (vizinho, vertice)
            self.ja_examinada[chave] = self.ja_examinada.get(chave, 0) + 1

    # A volta de uma aresta já examinada: não muda nada na busca, só é anotada
    def anotar_volta(self, vertice, vizinho):
        self.ja_examinada[(vertice, vizinho)] -= 1
        self.passos.append({
            "tipo": "revisitar",
            "origem": vertice,
            "destino": vizinho,
            "mensagem": f"Aresta {vertice} — {vizinho}: é a mesma aresta {vizinho} — {vertice}, já examinada (não conta de novo)",
        })

    # Descoberta: o relógio avança, o vértice fica Cinza e o tempo é anotado em d
    def descobrir(self, vertice):
        self.tempo += 1
        self.cor[vertice] = "Cinza"
        self.d[vertice] = self.tempo
        self.passos.append({
            "tipo": "descobrir",
            "vertice": vertice,
            "tempo": self.tempo,
            "mensagem": f"Vértice {vertice} descoberto (Cinza) no tempo {self.tempo}",
        })

    # Finalização: só acontece depois que todos os vizinhos foram examinados;
    # o vértice fica Preto, o relógio avança e o tempo é anotado em f
    def finalizar(self, vertice):
        self.cor[vertice] = "Preto"
        self.tempo += 1
        self.f[vertice] = self.tempo
        self.passos.append({
            "tipo": "finalizar",
            "vertice": vertice,
            "tempo": self.tempo,
            "mensagem": f"Vértice {vertice} finalizado (Preto) no tempo {self.tempo}",
        })
