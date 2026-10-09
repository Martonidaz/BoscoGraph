class Grafo:
    # Recebe os vértices, as arestas, a lista de passos e se o grafo é orientado.
    # A lista de passos é o "caderno de anotações" do programa: cada etapa
    # anota nela o que fez, para a janela reproduzir depois, um passo por vez.
    #
    # Orientado (dígrafo): a aresta A -> B é um par ordenado e só entra na lista de A.
    # Não orientado: a aresta A — B é um par não ordenado e entra nas duas listas
    # (B na lista de A e A na lista de B). Um laço A — A entra uma vez só na lista de A,
    # como no slide de lista de adjacência com laço.
    #
    # São montadas duas listas de adjacência, sempre na mesma ordem:
    #   grafo[A]           -> só os nomes dos vizinhos: ["B", "C"] (é a que a DFS usa)
    #   lista_com_pesos[A] -> cada vizinho com o peso e o número da aresta: [("B", 4, 0), ("C", 2, 1)]
    # O número da aresta (a posição dela na ordem de criação) diz ao desenho QUAL aresta pintar
    # quando há arestas paralelas com pesos diferentes.
    def __init__(self, vertices, arestas, passos, direcionado=True):
        self.vertices = vertices
        self.arestas = arestas
        self.passos = passos
        self.direcionado = direcionado
        self.grafo = {}
        self.lista_com_pesos = {}
        self.ordenado = False           # vira True quando as listas são ordenadas

        # Cria uma chave para cada vértice com uma lista vazia, que vai receber os vizinhos.
        # Assim, até um vértice sem nenhuma aresta saindo aparece no grafo.
        for vertice in vertices:
            self.grafo[vertice.nome] = []
            self.lista_com_pesos[vertice.nome] = []
            self.passos.append({
                "tipo": "criar_lista",
                "vertice": vertice.nome,
                "mensagem": f"Grafo: lista de {vertice.nome} criada (vazia)",
            })

        # Para cada aresta, coloca o nome do destino na lista da origem (A -> B: "B" entra na lista de "A")
        for numero in range(len(arestas)):
            aresta = arestas[numero]
            origem = aresta.vertice_origem.nome
            destino = aresta.vertice_destino.nome
            self.grafo[origem].append(destino)
            self.lista_com_pesos[origem].append((destino, aresta.peso, numero))
            self.passos.append({
                "tipo": "adicionar_vizinho",
                "origem": origem,
                "destino": destino,
                "peso": aresta.peso,
                "volta": False,
                "mensagem": f"Grafo: {destino} entra na lista de {origem}",
            })

            # Não orientado: a mesma aresta vale no outro sentido, então a origem
            # também entra na lista do destino (menos no laço, que já está na lista certa)
            if not self.direcionado and origem != destino:
                self.grafo[destino].append(origem)
                self.lista_com_pesos[destino].append((origem, aresta.peso, numero))
                self.passos.append({
                    "tipo": "adicionar_vizinho",
                    "origem": destino,
                    "destino": origem,
                    "peso": aresta.peso,
                    "volta": True,
                    "mensagem": f"Grafo: {origem} entra na lista de {destino} (a aresta vale nos dois sentidos)",
                })

    # Ordena a lista de vizinhos de cada vértice em ordem alfabética:
    # é o critério de desempate que o enunciado pede antes da busca
    def ordenar_listas_adjacencia(self):
        self.ordenado = True
        for nome in self.grafo:
            antes = list(self.grafo[nome])      # list(...) faz uma cópia: guarda como a lista estava
            self.grafo[nome].sort()
            # A lista com pesos é ordenada pelo nome do vizinho também. O sort do Python é "estável":
            # vizinhos com o mesmo nome (arestas paralelas) continuam na ordem de criação,
            # e as duas listas continuam com os vizinhos na mesma ordem.
            self.lista_com_pesos[nome].sort(key=self.nome_do_vizinho)
            depois = list(self.grafo[nome])
            pesos = []                          # os pesos na nova ordem (para a tela mostrar "B (4), C (2)")
            for vizinho, peso, numero in self.lista_com_pesos[nome]:
                pesos.append(peso)

            if antes == depois:
                mensagem = f"Lista de {nome} já estava em ordem: {depois}"
            else:
                mensagem = f"Lista de {nome} ordenada: {antes} -> {depois}"

            self.passos.append({
                "tipo": "ordenar",
                "vertice": nome,
                "lista": depois,
                "pesos": pesos,
                "mensagem": mensagem,
            })

    # O critério da ordenação da lista com pesos: o nome do vizinho (o 1º item do trio)
    def nome_do_vizinho(self, item):
        return item[0]

    # A lista "ao contrário": para cada vértice, quem CHEGA nele (com o peso e o número da aresta).
    # É a que a busca bidirecional usa no lado do destino: andar de trás para frente numa aresta
    # A -> B é ir de B para A. No não orientado, cada aresta já vale nos dois sentidos: a lista é a
    # mesma. Se as listas foram ordenadas, esta também é (pelo nome, como as outras).
    def lista_reversa(self):
        if not self.direcionado:
            return self.lista_com_pesos
        reversa = {}
        for nome in self.grafo:
            reversa[nome] = []
        for numero in range(len(self.arestas)):
            aresta = self.arestas[numero]
            origem = aresta.vertice_origem.nome
            destino = aresta.vertice_destino.nome
            reversa[destino].append((origem, aresta.peso, numero))
        if self.ordenado:
            for nome in reversa:
                reversa[nome].sort(key=self.nome_do_vizinho)
        return reversa
