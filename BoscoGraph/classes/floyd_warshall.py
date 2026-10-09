# Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25).
#
# As outras buscas partem de UMA origem. O Floyd-Warshall calcula o menor custo entre TODOS os pares
# de vértices de uma vez, numa matriz d: d[i][j] = o menor custo de i até j.
#
# A ideia, em rodadas: na rodada do vértice k, cada par (i, j) pergunta "passar por k fica mais
# barato?", isto é, d[i][k] + d[k][j] < d[i][j]? Depois da rodada de k, os caminhos podem usar k no
# meio. Depois da última rodada, podem usar qualquer vértice no meio: são os menores custos.
# São n rodadas de n × n perguntas: n³ comparações (por isso o BoscoGraph limita o tamanho do grafo).
#
#   d[i][j]  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
#   pi[i][j] -> o vértice que vem ANTES de j no melhor caminho de i até j (o π do livro)
# Aceita pesos negativos. Se no fim algum d[i][i] < 0, dá para sair de i e voltar com custo
# negativo: existe um CICLO NEGATIVO, e os "menores custos" não existem (cada volta diminui mais).
#
# Diferenças pequenas do livro, para o grafo do BoscoGraph:
#   - arestas paralelas: a matriz guarda a mais barata (a outra nunca seria usada);
#   - laço com peso negativo: d[i][i] começa com o peso dele (já é um ciclo negativo);
#   - um par em que d[i][k] ou d[k][j] é infinito é pulado: passar por k é impossível.

from entrada import INFINITO, formatar_numero


class FloydWarshall:

    def __init__(self, grafo, passos):
        self.vertices = list(grafo.grafo)       # os vértices, na ordem de criação
        self.arestas = grafo.arestas
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.d = {}                 # d[i][j]: um dicionário de dicionários (uma "matriz" com nomes)
        self.pi = {}
        self.aresta = {}            # aresta[(i, j)]: o número da aresta usada de i para j (para o desenho)
        self.ciclo_negativo = []    # os vértices i com d[i][i] < 0 no fim
        self.comparacoes = 0
        self.melhoras = 0

    def floyd_warshall(self):
        self.inicializar()
        for k in self.vertices:
            self.anotar("rodada_k", f"Rodada do vértice {k}: cada par (i, j) pergunta se passar por {k} "
                                    f"fica mais barato", {"k": k})
            for i in self.vertices:
                for j in self.vertices:
                    if self.d[i][k] == INFINITO or self.d[k][j] == INFINITO:
                        continue            # não há caminho de i até k ou de k até j: k não ajuda
                    self.comparar(i, j, k)
        self.conferir_ciclo_negativo()

    # D(0): 0 na diagonal, o peso das arestas, e infinito onde não há aresta
    def inicializar(self):
        for i in self.vertices:
            self.d[i] = {}
            self.pi[i] = {}
            for j in self.vertices:
                self.d[i][j] = INFINITO
                self.pi[i][j] = None
            self.d[i][i] = 0
            self.anotar("inicializar_linha", f"Linha de {i}: d[{i}][{i}] = 0 (sem sair do lugar) e ∞ no resto",
                        {"vertice": i})
        # Cada aresta, nos dois sentidos se o grafo não for orientado
        for numero in range(len(self.arestas)):
            aresta = self.arestas[numero]
            origem = aresta.vertice_origem.nome
            destino = aresta.vertice_destino.nome
            self.arco_inicial(origem, destino, aresta.peso, numero)
            if not self.direcionado and origem != destino:
                self.arco_inicial(destino, origem, aresta.peso, numero)

    # Uma aresta u -> v entra na matriz se for mais barata que o que já está lá
    # (uma paralela mais cara, ou um laço que não é negativo, não muda nada)
    def arco_inicial(self, origem, destino, peso, numero):
        antes = self.d[origem][destino]
        melhorou = peso < antes
        if melhorou:
            self.d[origem][destino] = peso
            self.pi[origem][destino] = origem
            self.aresta[(origem, destino)] = numero
            mensagem = f"Aresta {self.ligacao(origem, destino)} (peso {formatar_numero(peso)}): " \
                       f"d[{origem}][{destino}] = {formatar_numero(peso)}"
        else:
            mensagem = f"Aresta {self.ligacao(origem, destino)} (peso {formatar_numero(peso)}): não é menor " \
                       f"que d[{origem}][{destino}] = {formatar_numero(antes)}, fica como está"
        self.anotar("arco_inicial", mensagem, {"origem": origem, "destino": destino, "aresta": numero, "peso": peso,
                                               "antes": antes, "melhorou": melhorou})

    # A pergunta da rodada: d[i][k] + d[k][j] < d[i][j]?
    def comparar(self, i, j, k):
        self.comparacoes += 1
        antes = self.d[i][j]
        por_k = self.d[i][k] + self.d[k][j]
        melhorou = por_k < antes
        if melhorou:
            self.d[i][j] = por_k
            self.pi[i][j] = self.pi[k][j]
            self.melhoras += 1
            mensagem = (f"d[{i}][{k}] + d[{k}][{j}] = {formatar_numero(self.d[i][k])} + "
                        f"{formatar_numero(self.d[k][j])} = {formatar_numero(por_k)} < {formatar_numero(antes)}: "
                        f"passar por {k} é melhor, d[{i}][{j}] = {formatar_numero(por_k)}")
        else:
            mensagem = (f"d[{i}][{k}] + d[{k}][{j}] = {formatar_numero(por_k)} não é menor que "
                        f"d[{i}][{j}] = {formatar_numero(antes)}: fica como está")
        self.anotar("comparar_par", mensagem, {"i": i, "j": j, "k": k, "antes": antes, "por_k": por_k,
                                               "melhorou": melhorou})

    # No fim: algum d[i][i] < 0? Então existe ciclo negativo (e os menores custos não existem)
    def conferir_ciclo_negativo(self):
        for i in self.vertices:
            if self.d[i][i] < 0:
                self.ciclo_negativo.append(i)
        if self.ciclo_negativo:
            primeiro = self.ciclo_negativo[0]
            self.anotar("diagonal_negativa", f"d[{primeiro}][{primeiro}] = {formatar_numero(self.d[primeiro][primeiro])} "
                                          f"< 0: dá para sair de {primeiro} e voltar com custo negativo, existe "
                                          f"ciclo negativo", {"vertice": primeiro})
        else:
            self.anotar("sem_ciclo_negativo", "Nenhum d[i][i] ficou negativo: não há ciclo negativo, os valores "
                                              "da matriz são os menores custos", {})

    # O caminho de i até j, seguindo pi de trás para frente: j, pi[i][j], pi[i][pi[i][j]], ..., i.
    # Devolve (vértices, arestas) ou (None, None) se não houver caminho.
    def caminho(self, i, j):
        if self.d[i][j] == INFINITO:
            return None, None
        vertices = [j]
        atual = j
        while atual != i:
            anterior = self.pi[i][atual]
            if anterior is None or len(vertices) > len(self.vertices):
                return None, None           # só acontece com ciclo negativo no meio
            vertices.append(anterior)
            atual = anterior
        vertices.reverse()
        arestas = []
        for posicao in range(len(vertices) - 1):
            arestas.append(self.aresta[(vertices[posicao], vertices[posicao + 1])])
        return vertices, arestas

    def ligacao(self, origem, destino):
        if self.direcionado:
            return f"{origem} -> {destino}"
        return f"{origem} — {destino}"

    # Acrescenta um passo com as informações dadas (tipo, mensagem e o que mais vier)
    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
