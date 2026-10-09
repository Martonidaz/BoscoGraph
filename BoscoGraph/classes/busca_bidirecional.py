# Busca bidirecional: duas buscas em largura ao mesmo tempo, uma saindo da ORIGEM (a "frente") e
# outra saindo do DESTINO (a de "trás"), até as duas se encontrarem no meio.
#
# Por que vale a pena: se cada vértice tem uns b vizinhos e o caminho tem L arestas, uma busca em
# largura sozinha examina perto de b^L vértices; duas buscas que andam metade cada uma examinam perto
# de 2 · b^(L/2), que é MUITO menos (com b = 3 e L = 6: 729 contra 54).
#
# Como funciona aqui (a versão "por camadas"):
#   - cada lado tem a sua fila; as duas buscas se revezam, e cada vez um lado expande UMA CAMADA
#     INTEIRA (todos os vértices que estavam na fila dele naquele momento);
#   - o lado de trás anda pelas arestas AO CONTRÁRIO (no orientado, A -> B vira B -> A: quem chega
#     em B), porque ele procura de onde dá para chegar no destino;
#   - quando um lado encontra um vértice que o OUTRO lado já descobriu, as buscas se encontraram:
#     o caminho é origem ... encontro ... destino.
# Expandindo camadas inteiras e conferindo o encontro na hora em que cada vizinho é descoberto, o
# primeiro encontro já dá o caminho com o MENOR NÚMERO DE ARESTAS (como a busca em largura).
#
# Cores, como na busca em largura (Branco, Cinza na fila, Preto expandido), e cada vértice descoberto
# tem um LADO: "frente" (descoberto a partir da origem) ou "tras" (a partir do destino).

from entrada import INFINITO

FRENTE = "frente"
TRAS = "tras"


class BuscaBidirecional:

    def __init__(self, grafo, passos):
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.lista_frente = grafo.lista_com_pesos       # quem sai de cada vértice
        self.lista_tras = grafo.lista_reversa()         # quem chega em cada vértice (igual no não orientado)
        self.cor = {}
        self.lado = {}              # FRENTE, TRAS ou None (ainda não descoberto)
        self.d = {}                 # arestas desde a origem (lado da frente)
        self.d_tras = {}            # arestas até o destino (lado de trás)
        self.pai = {}               # π da frente: de onde a busca da frente chegou
        self.pai_tras = {}          # π de trás: o próximo vértice no caminho até o destino
        self.aresta_do_pai = {}
        self.aresta_do_pai_tras = {}
        self.fila = []              # a fila da frente
        self.fila_tras = []         # a fila de trás
        self.encontro = None        # (vértice do lado da frente, vértice do lado de trás, número da aresta)
        self.caminho = None         # o caminho encontrado (vértices) e as arestas dele
        self.arestas_do_caminho = None
        self.ordem_de_expansao = [] # (lado, vértice), na ordem em que saíram das filas
        self.origem = None
        self.destino = None

    def buscar(self, origem, destino):
        self.origem = origem
        self.destino = destino

        # Começo: todo vértice Branco, sem lado, com distância infinita e sem pai
        for vertice in self.lista_frente:
            self.cor[vertice] = "Branco"
            self.lado[vertice] = None
            self.d[vertice] = INFINITO
            self.d_tras[vertice] = INFINITO
            self.pai[vertice] = None
            self.pai_tras[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice} pintado de Branco: nenhum lado o descobriu ainda",
                        {"vertice": vertice})

        # A frente começa na origem
        self.cor[origem] = "Cinza"
        self.lado[origem] = FRENTE
        self.d[origem] = 0
        self.fila.append(origem)
        self.anotar("origem", f"A frente começa na origem {origem} (d = 0): entra na fila da frente",
                    {"vertice": origem, "lado": FRENTE, "distancia": 0})
        if origem == destino:
            self.encontro = (origem, origem, None)
            self.anotar("encontro", f"A origem já é o destino: o caminho é só {origem}",
                        {"vertice": origem, "na_origem": True})
            self.montar_caminho()
            return True

        # Trás começa no destino
        self.cor[destino] = "Cinza"
        self.lado[destino] = TRAS
        self.d_tras[destino] = 0
        self.fila_tras.append(destino)
        self.anotar("origem_tras", f"Trás começa no destino {destino} (d = 0): entra na fila de trás",
                    {"vertice": destino, "lado": TRAS, "distancia": 0})

        # As duas se revezam, uma camada inteira de cada vez, enquanto as duas filas tiverem alguém
        while self.fila and self.fila_tras:
            if self.expandir(FRENTE):
                return True
            if self.expandir(TRAS):
                return True
        self.anotar("sem_encontro", "Uma das filas acabou sem as buscas se encontrarem: não existe caminho "
                                    f"de {origem} até {destino}", {})
        return False

    # Expande uma camada inteira de um lado. Devolve True se encontrou o outro lado.
    def expandir(self, lado):
        if lado == FRENTE:
            fila, lista, d, pai, aresta_do_pai, outro = (self.fila, self.lista_frente, self.d, self.pai,
                                                         self.aresta_do_pai, TRAS)
        else:
            fila, lista, d, pai, aresta_do_pai, outro = (self.fila_tras, self.lista_tras, self.d_tras, self.pai_tras,
                                                         self.aresta_do_pai_tras, FRENTE)
        tamanho = len(fila)         # quantos estão na fila AGORA: essa é a camada (quem entrar depois espera)
        self.anotar("nova_camada", f"{self.nome_do_lado(lado).capitalize()}: expande uma camada inteira, "
                                   f"{tamanho} na fila ({', '.join(fila)})",
                    {"lado": lado, "tamanho": tamanho, "vertices": list(fila)})
        for vez in range(tamanho):
            vertice = fila.pop(0)
            self.ordem_de_expansao.append((lado, vertice))
            self.anotar("desenfileirar", f"{vertice} sai da fila {self.nome_do_lado(lado, 'da')} "
                                         f"(d = {d[vertice]}): agora os vizinhos dele",
                        {"vertice": vertice, "lado": lado})
            for vizinho, peso, numero in lista[vertice]:
                if self.lado[vizinho] == outro:
                    # O outro lado já descobriu esse vizinho: as duas buscas se encontraram
                    if lado == FRENTE:
                        self.encontro = (vertice, vizinho, numero)
                    else:
                        self.encontro = (vizinho, vertice, numero)
                    self.anotar("encontro", f"Aresta {self.ligacao(vertice, vizinho, lado)}: {vizinho} já foi "
                                            f"descoberto {self.nome_do_lado(outro, 'pela')}: as buscas se "
                                            f"encontraram!",
                                {"origem": vertice, "destino": vizinho, "aresta": numero, "lado": lado})
                    self.montar_caminho()
                    return True
                if self.cor[vizinho] == "Branco":
                    self.cor[vizinho] = "Cinza"
                    self.lado[vizinho] = lado
                    d[vizinho] = d[vertice] + 1
                    pai[vizinho] = vertice
                    aresta_do_pai[vizinho] = numero
                    fila.append(vizinho)
                    self.anotar("descobrir_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho, lado)}: {vizinho} descoberto "
                                f"{self.nome_do_lado(lado, 'pela')} com d = {d[vizinho]}: entra no fim da fila",
                                {"origem": vertice, "destino": vizinho, "aresta": numero, "lado": lado,
                                 "distancia": d[vizinho]})
                else:
                    self.anotar("ignorar_vizinho",
                                f"Aresta {self.ligacao(vertice, vizinho, lado)}: {vizinho} já foi descoberto "
                                f"{self.nome_do_lado(lado, 'pela')}, nada muda",
                                {"origem": vertice, "destino": vizinho, "aresta": numero, "lado": lado})
            self.cor[vertice] = "Preto"
            self.anotar("terminar_vertice", f"Vértice {vertice} expandido (Preto)",
                        {"vertice": vertice, "lado": lado})
        return False

    # Junta as duas metades: da origem até o vértice da frente (subindo pelos pais da frente),
    # a aresta do encontro, e do vértice de trás até o destino (seguindo os pais de trás)
    def montar_caminho(self):
        da_frente, de_tras, numero = self.encontro
        vertices = [da_frente]
        arestas = []
        atual = da_frente
        while self.pai[atual] is not None:
            arestas.append(self.aresta_do_pai[atual])
            atual = self.pai[atual]
            vertices.append(atual)
        vertices.reverse()
        arestas.reverse()
        if numero is not None:              # None: a origem já era o destino
            arestas.append(numero)
            atual = de_tras
            vertices.append(atual)
            while self.pai_tras[atual] is not None:
                arestas.append(self.aresta_do_pai_tras[atual])
                atual = self.pai_tras[atual]
                vertices.append(atual)
        self.caminho = vertices
        self.arestas_do_caminho = arestas

    # "pela frente" / "por trás", "da frente" / "de trás" (para as mensagens)
    def nome_do_lado(self, lado, preposicao=""):
        if lado == FRENTE:
            nomes = {"": "a frente", "da": "da frente", "pela": "pela frente"}
        else:
            nomes = {"": "trás", "da": "de trás", "pela": "por trás"}
        return nomes[preposicao]

    # A aresta na mensagem, no sentido de verdade dela: o lado de trás anda ao contrário,
    # então de B ele chega em A pela aresta A -> B
    def ligacao(self, vertice, vizinho, lado):
        if not self.direcionado:
            return f"{vertice} — {vizinho}"
        if lado == FRENTE:
            return f"{vertice} -> {vizinho}"
        return f"{vizinho} -> {vertice}"

    # Acrescenta um passo com as informações dadas (tipo, mensagem e o que mais vier)
    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
