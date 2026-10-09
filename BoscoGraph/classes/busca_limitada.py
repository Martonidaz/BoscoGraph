# Busca em profundidade limitada (DLS, "depth-limited search"), como no livro do Russell e Norvig
# (Inteligência Artificial, a busca sem informação).
#
# É a busca em profundidade com um LIMITE: ela desce no máximo "limite" arestas a partir da origem.
# Num vértice que já está na profundidade do limite, a busca não olha os vizinhos: é o CORTE
# ("pode ter mais coisa depois daqui, mas o limite não deixa ver").
#
# Diferente da DFS do Cormen, aqui a busca é em "árvore": ela NÃO lembra quem já visitou fora do
# caminho atual. Um mesmo vértice pode entrar no caminho mais de uma vez, por caminhos diferentes
# (com profundidades diferentes). O que ela evita é andar em círculo: um vizinho que JÁ ESTÁ no
# caminho atual é ignorado (senão A -> B -> A -> B... nunca acabaria).
#
# Cores, para a tela:
#   Branco -> ainda não entrou no caminho;  Cinza -> está no caminho agora (na pilha da recursão);
#   Preto  -> já entrou e já saiu do caminho.
#
# Três respostas possíveis, como no livro:
#   "achou" -> chegou ao destino (o caminho até ele está em self.caminho)
#   "corte" -> não achou, mas o limite cortou algum ramo (com um limite maior, talvez ache)
#   "falha" -> não achou e nada foi cortado: o destino não é alcançável (ou não há destino)

ACHOU = "achou"
CORTE = "corte"
FALHA = "falha"


class BuscaEmProfundidadeLimitada:

    def __init__(self, grafo, passos):
        # A lista com pesos traz o número de cada aresta (para o desenho pintar a aresta certa)
        self.lista_adjacencia = grafo.lista_com_pesos
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.cor = {}
        self.profundidade = {}      # a profundidade com que o vértice entrou no caminho (a última vez)
        self.pai = {}               # π: de qual vértice ele entrou no caminho (a última vez)
        self.aresta_do_pai = {}     # o número da aresta pai -> vértice
        self.caminho = []           # o caminho atual, da origem até o vértice de agora (a pilha da recursão)
        self.arestas_do_caminho = []   # os números das arestas desse caminho
        self.cortados = []          # onde o limite cortou (um vértice pode aparecer mais de uma vez)
        self.nos = 0                # quantas vezes um vértice entrou no caminho (os "nós" da árvore de busca)
        self.origem = None
        self.destino = None
        self.limite = None
        self.resultado = None

    # Começo: todo vértice Branco e sem pai
    def inicializar(self):
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice} pintado de Branco: ainda fora do caminho",
                        {"vertice": vertice})

    # DEPTH-LIMITED-SEARCH(problema, limite)
    def buscar(self, origem, destino, limite):
        self.origem = origem
        self.destino = destino
        self.limite = limite
        self.inicializar()
        self.resultado = self.dls(origem, None, None, limite, 0)
        return self.resultado

    # RECURSIVE-DLS: o vértice entra no caminho; se for o destino, achou; se o limite acabou,
    # corta; senão, desce em cada vizinho que não está no caminho
    #   pai, numero -> de onde veio e por qual aresta (None na origem)
    #   restante    -> quantas arestas ainda pode descer
    def dls(self, vertice, pai, numero, restante, profundidade):
        self.entrar(vertice, pai, numero, profundidade)

        if vertice == self.destino:
            self.anotar("chegou", f"{vertice} é o destino: achou, com profundidade {profundidade}",
                        {"vertice": vertice})
            return ACHOU

        if restante == 0:
            # O limite acabou: os vizinhos não são examinados e o vértice sai do caminho
            self.cortados.append(vertice)
            self.sair(vertice)
            self.anotar("corte", f"Corte em {vertice}: profundidade {profundidade} = limite {self.limite}, "
                                 f"os vizinhos dele ficam de fora",
                        {"vertice": vertice, "profundidade": profundidade, "origem": pai, "aresta": numero})
            return CORTE

        houve_corte = False
        for vizinho, peso, numero_do_vizinho in self.lista_adjacencia[vertice]:
            if vizinho in self.caminho:
                # Já está no caminho: descer nele fecharia um ciclo (e a busca andaria em círculo)
                self.anotar("ignorar_vizinho",
                            f"Aresta {self.ligacao(vertice, vizinho)}: {vizinho} já está no caminho "
                            f"(seria um ciclo), não desce",
                            {"origem": vertice, "destino": vizinho, "aresta": numero_do_vizinho})
                continue
            resultado = self.dls(vizinho, vertice, numero_do_vizinho, restante - 1, profundidade + 1)
            if resultado == ACHOU:
                return ACHOU            # o caminho até o destino continua guardado em self.caminho
            if resultado == CORTE:
                houve_corte = True

        self.sair(vertice)
        if houve_corte:
            resposta = CORTE
            texto = "algum ramo abaixo dele foi cortado pelo limite"
        else:
            resposta = FALHA
            texto = "nada abaixo dele chegou ao destino" if self.destino is not None else "todos os ramos acabaram"
        self.anotar("subir", f"{vertice} sai do caminho (Preto): {texto}",
                    {"vertice": vertice, "origem": pai, "aresta": numero, "resultado": resposta})
        return resposta

    # O vértice entra no caminho (Cinza), com a profundidade e o pai desta vez
    def entrar(self, vertice, pai, numero, profundidade):
        self.cor[vertice] = "Cinza"
        self.profundidade[vertice] = profundidade
        self.pai[vertice] = pai
        if numero is not None:
            self.aresta_do_pai[vertice] = numero
            self.arestas_do_caminho.append(numero)
        self.caminho.append(vertice)
        self.nos += 1
        if pai is None:
            mensagem = f"{vertice} é a origem: entra no caminho com profundidade 0 (limite {self.limite})"
        else:
            mensagem = (f"Aresta {self.ligacao(pai, vertice)}: {vertice} entra no caminho (Cinza) "
                        f"com profundidade {profundidade}")
        self.anotar("entrar", mensagem, {"vertice": vertice, "origem": pai, "aresta": numero,
                                         "profundidade": profundidade, "limite": self.limite})

    # O vértice sai do caminho (Preto): a recursão volta para o pai.
    # Só a origem entra sem aresta (pai None); os outros levam junto a aresta por onde entraram.
    def sair(self, vertice):
        self.cor[vertice] = "Preto"
        self.caminho.pop()
        if self.pai[vertice] is not None:
            self.arestas_do_caminho.pop()

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
