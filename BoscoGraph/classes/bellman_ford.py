# Algoritmo de Bellman-Ford (caminhos mínimos a partir de uma origem), como no CLRS.
#
# Diferente do Dijkstra, ele aceita pesos NEGATIVOS. A ideia é mais "bruta":
# em cada rodada, relaxa TODAS as arestas. Um caminho mínimo sem ciclo tem no máximo |V| − 1
# arestas, e depois da rodada i já estão certos todos os caminhos mínimos com até i arestas.
# Então |V| − 1 rodadas bastam.
#
# Depois disso, se alguma aresta ainda consegue diminuir uma distância, é porque existe um
# CICLO NEGATIVO alcançável (dar mais uma volta nele sempre fica mais barato): aí não existe
# caminho mínimo, e o algoritmo avisa.
#
# Melhoria usada aqui (e explicada na tela): se uma rodada inteira não muda nada, as próximas
# também não mudariam, e a busca para antes.
#
# Cores: Branco = d = ∞ (ainda não alcançado); Cinza = já tem um d (que ainda pode diminuir).

from entrada import INFINITO, formatar_numero


class BellmanFord:

    def __init__(self, grafo, passos):
        self.vertices = list(grafo.grafo)               # os nomes, na ordem de criação
        self.direcionado = grafo.direcionado
        self.passos = passos
        self.cor = {}
        self.d = {}
        self.pai = {}
        self.aresta_do_pai = {}
        self.ciclo_negativo = None      # o ciclo encontrado (lista de vértices), se houver
        self.arestas_do_ciclo = []
        self.origem = None

        # A lista de arestas na ordem em que cada rodada as relaxa: a ordem de criação.
        # No não orientado, a aresta A — B pode ser usada nos dois sentidos: A -> B e B -> A.
        # Cada item: (de onde sai, aonde chega, peso, número da aresta)
        self.arcos = []
        for numero in range(len(grafo.arestas)):
            aresta = grafo.arestas[numero]
            origem = aresta.vertice_origem.nome
            destino = aresta.vertice_destino.nome
            self.arcos.append((origem, destino, aresta.peso, numero))
            if not self.direcionado and origem != destino:
                self.arcos.append((destino, origem, aresta.peso, numero))

    # BELLMAN-FORD(G, w, s)
    def bellman_ford(self, origem):
        self.origem = origem

        # INITIALIZE-SINGLE-SOURCE
        for vertice in self.vertices:
            self.cor[vertice] = "Branco"
            self.d[vertice] = INFINITO
            self.pai[vertice] = None
            self.anotar("inicializar", f"Vértice {vertice}: d = ∞ e sem pai", {"vertice": vertice})
        self.d[origem] = 0
        self.cor[origem] = "Cinza"
        self.anotar("origem", f"Origem {origem}: d = 0", {"vertice": origem, "distancia": 0})

        total = len(self.vertices) - 1          # |V| − 1 rodadas
        parou_antes = False
        for rodada in range(1, total + 1):
            self.anotar("rodada", f"Rodada {rodada} de {total}: relaxar todas as arestas, na ordem de criação",
                        {"numero": rodada, "total": total})
            mudou = False
            for de, ate, peso, numero in self.arcos:
                if self.relaxar(de, ate, peso, numero, rodada):
                    mudou = True
            if not mudou:
                mensagem = (f"A rodada {rodada} não mudou nenhuma distância: as próximas também não mudariam, "
                            f"então a busca para aqui")
                if rodada == total:
                    mensagem = f"A rodada {rodada} (a última) não mudou nenhuma distância: elas já estão certas"
                self.anotar("rodada_sem_mudanca", mensagem, {"numero": rodada, "total": total})
                parou_antes = True
                break

        # Conferência do ciclo negativo. Se uma rodada já não mudou nada, a conferência também não mudaria.
        # (Com 1 vértice não há rodada nenhuma, mas a conferência continua valendo: um laço de peso
        # negativo A -> A já é um ciclo negativo.)
        if parou_antes:
            self.anotar("sem_ciclo_negativo", "Sem ciclo negativo: nenhuma aresta consegue diminuir mais "
                                              "uma distância", {})
            return
        self.anotar("verificar_ciclo", f"Conferência: depois de {total} rodadas, alguma aresta ainda diminui "
                                       f"uma distância?", {})
        for de, ate, peso, numero in self.arcos:
            if self.d[de] + peso < self.d[ate]:
                self.achar_ciclo(de, ate, numero)
                texto = " -> ".join(self.ciclo_negativo)
                if not self.direcionado:
                    texto = " — ".join(self.ciclo_negativo)
                self.anotar("ciclo_negativo",
                            f"Ciclo negativo: {self.ligacao(de, ate)} ainda diminui d[{ate}]. "
                            f"Ciclo: {texto}",
                            {"origem": de, "destino": ate, "aresta": numero, "ciclo": list(self.ciclo_negativo),
                             "arestas_do_ciclo": list(self.arestas_do_ciclo)})
                return
        self.anotar("sem_ciclo_negativo", "Sem ciclo negativo: nenhuma aresta consegue diminuir mais uma distância",
                    {})

    # RELAX(u, v, w). Devolve True se a distância diminuiu.
    def relaxar(self, de, ate, peso, numero, rodada):
        antes = self.d[ate]
        novo = self.d[de] + peso                        # ∞ + peso continua ∞
        texto_do_peso = formatar_numero(peso)
        if peso < 0:
            texto_do_peso = f"({texto_do_peso})"        # d[A] + (-2): o parêntese evita ler "+ -2" como erro
        conta = f"d[{de}] + {texto_do_peso} = {formatar_numero(novo)}"
        dados = {"origem": de, "destino": ate, "aresta": numero, "peso": peso, "antes": antes, "depois": novo,
                 "melhorou": False, "entrou": False, "rodada": rodada}
        if novo < antes:
            self.d[ate] = novo
            self.pai[ate] = de
            dados["aresta_antiga"] = self.aresta_do_pai.get(ate)
            self.aresta_do_pai[ate] = numero
            dados["melhorou"] = True
            if self.cor[ate] == "Branco":
                self.cor[ate] = "Cinza"
                dados["entrou"] = True
            mensagem = (f"Relaxar {self.ligacao(de, ate)}: {conta} < {formatar_numero(antes)}, "
                        f"então d[{ate}] = {formatar_numero(novo)} e o pai de {ate} é {de}")
            self.anotar("relaxar", mensagem, dados)
            return True
        if self.d[de] == INFINITO:
            mensagem = f"Relaxar {self.ligacao(de, ate)}: d[{de}] = ∞ (ainda não se chega em {de}), nada muda"
        else:
            mensagem = (f"Relaxar {self.ligacao(de, ate)}: {conta} não é menor que "
                        f"d[{ate}] = {formatar_numero(antes)}, nada muda")
        self.anotar("relaxar", mensagem, dados)
        return False

    # Acha o ciclo negativo, sabendo que a aresta de -> ate ainda melhora.
    # Enquanto os pais não formarem um ciclo, continua relaxando "escondido" (sem anotar passos,
    # só para mexer nos pais). Todo ciclo formado pelos pais tem peso negativo (CLRS, lema 24.16),
    # e dar voltas num ciclo negativo sempre melhora alguém: por isso os pais acabam fechando o ciclo.
    def achar_ciclo(self, de, ate, numero):
        for vez in range(len(self.vertices) + 1):
            for comeco in self.vertices:
                ciclo, arestas = self.ciclo_seguindo_os_pais(comeco)
                if ciclo:
                    self.ciclo_negativo = ciclo
                    self.arestas_do_ciclo = arestas
                    return
            for de_2, ate_2, peso_2, numero_2 in self.arcos:
                if self.d[de_2] + peso_2 < self.d[ate_2]:
                    self.d[ate_2] = self.d[de_2] + peso_2
                    self.pai[ate_2] = de_2
                    self.aresta_do_pai[ate_2] = numero_2

    # Sobe pelos pais a partir de "comeco" até repetir um vértice (ciclo) ou chegar em quem não tem pai.
    # Devolve o ciclo [v0, v1, ..., v0] no sentido das arestas e os números das arestas dele,
    # ou (None, None) se não houver ciclo por esse caminho.
    def ciclo_seguindo_os_pais(self, comeco):
        visitados = []
        atual = comeco
        while atual is not None and atual not in visitados:
            visitados.append(atual)
            atual = self.pai[atual]
        if atual is None:
            return None, None
        # "atual" é o primeiro vértice repetido: o ciclo começa (e termina) nele
        ciclo = [atual]
        arestas = []
        vertice = atual
        while True:
            arestas.append(self.aresta_do_pai[vertice])
            vertice = self.pai[vertice]
            ciclo.append(vertice)
            if vertice == atual:
                break
        # Os pais apontam "para trás"; invertendo, o ciclo segue o sentido das arestas
        ciclo.reverse()
        arestas.reverse()
        return ciclo, arestas

    def ligacao(self, vertice, vizinho):
        if self.direcionado:
            return f"{vertice} -> {vizinho}"
        return f"{vertice} — {vizinho}"

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)
