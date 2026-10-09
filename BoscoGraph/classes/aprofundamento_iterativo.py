# Busca de aprofundamento iterativo (IDDFS, "iterative deepening"), como no livro do Russell e Norvig.
#
# A ideia: rodar a busca em profundidade LIMITADA com limite 0, depois 1, depois 2... até achar o
# destino (ou até nenhuma rodada ser cortada pelo limite, quando o destino não é alcançável).
#
# Parece desperdício (a cada rodada tudo recomeça da origem), mas junta o melhor de duas buscas:
#   - como a busca em largura, acha o destino com o MENOR NÚMERO DE ARESTAS (o primeiro limite em que
#     ele aparece é a distância até ele);
#   - como a busca em profundidade, só guarda na memória o caminho atual (e não uma fila enorme).
# O trabalho repetido é pequeno: numa árvore, a última camada tem mais nós que todas as de cima juntas.
#
# Cada rodada é exatamente a busca limitada (classes/busca_limitada.py): esta classe herda dela e só
# acrescenta o laço dos limites.

from classes.busca_limitada import BuscaEmProfundidadeLimitada, CORTE


class AprofundamentoIterativo(BuscaEmProfundidadeLimitada):

    def __init__(self, grafo, passos):
        # super().__init__ prepara tudo o que a busca limitada usa (cores, caminho, cortados...)
        super().__init__(grafo, passos)
        self.iteracoes = []         # (limite, quantos nós entraram no caminho, resultado) de cada rodada

    # ITERATIVE-DEEPENING-SEARCH(problema)
    def buscar(self, origem, destino):
        self.origem = origem
        self.destino = destino
        limite = 0
        while True:
            self.nova_iteracao(limite)
            nos_antes = self.nos
            resultado = self.dls(origem, None, None, limite, 0)
            self.iteracoes.append((limite, self.nos - nos_antes, resultado))
            # Sem corte, um limite maior não mudaria nada: ou achou, ou o destino não é alcançável.
            # (Um caminho sem repetir vértices tem no máximo n - 1 arestas, então isso sempre acontece.)
            if resultado != CORTE:
                break
            limite = limite + 1
        self.resultado = resultado
        return resultado

    # Uma rodada nova: tudo volta a ser Branco e o caminho recomeça vazio
    def nova_iteracao(self, limite):
        self.limite = limite
        for vertice in self.lista_adjacencia:
            self.cor[vertice] = "Branco"
            self.pai[vertice] = None
        self.profundidade = {}
        self.aresta_do_pai = {}
        self.caminho = []
        self.arestas_do_caminho = []
        self.cortados = []
        self.anotar("nova_iteracao", f"Rodada com limite {limite}: todos voltam a Branco e a busca recomeça "
                                     f"da origem", {"limite": limite})
