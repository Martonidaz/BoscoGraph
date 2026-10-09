# Depois da busca (todas menos a DFS, que tem o TipoDoGrafo): o resultado, na etapa 6.
# É o "TipoDoGrafo" dessas buscas: cada conclusão vira um passo, e a tela mostra esses passos.
#
#   distâncias -> o d de cada vértice (em arestas na BFS; em custo nas outras)
#   árvore     -> as arestas pai -> filho (π): juntas formam a árvore de caminhos mínimos
#   caminho    -> se um destino foi escolhido: o caminho da origem até ele, subindo pelos pais
#   ciclo      -> no Bellman-Ford, o ciclo negativo (quando existe, não há caminho mínimo)
#   comparação -> na gulosa e no A*: o custo encontrado comparado com o menor custo possível;
#                 na bidirecional e no aprofundamento iterativo: comparado com a busca em largura
#   heurística -> na gulosa e no A*: h é admissível? é consistente?
#   limitada   -> na busca limitada: achou, cortou (o limite não deixou ver) ou falhou
#   iterações  -> no aprofundamento iterativo: quantos nós cada limite gerou
#   matriz     -> no Floyd-Warshall: a matriz final de menores custos (ou o ciclo negativo)
#   árvore mínima -> no Prim e no Kruskal: as arestas da árvore (ou da floresta) e o peso total, e a
#                 comparação com o outro algoritmo (rodando escondido): o peso total é sempre o mesmo

import algoritmos
from entrada import INFINITO, formatar_numero
from classes.dijkstra import Dijkstra
from classes.busca_em_largura import BuscaEmLargura
from classes.busca_limitada import ACHOU, CORTE
from classes.kruskal import Kruskal
from classes.prim import Prim


class ResultadoDaBusca:

    # inicio: a origem escolhida (o Floyd-Warshall não tem origem; com ela e um destino, mostra o caminho)
    def __init__(self, chave, grafo, busca, passos, heuristica, inicio=None):
        self.chave = chave              # qual busca rodou ("dijkstra", "a_estrela"...)
        self.inicio = inicio
        self.grafo = grafo
        self.busca = busca
        self.passos = passos
        self.heuristica = heuristica
        self.direcionado = grafo.direcionado
        self.nomes = list(grafo.grafo)  # os vértices, na ordem de criação
        self.resultado = {}

    # A distância de cada vértice, com o nome que cada busca usa (d ou g)
    def distancia(self, vertice):
        if self.chave in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
            return self.busca.g[vertice]
        return self.busca.d[vertice]

    def concluir(self, destino):
        if self.chave in (algoritmos.PRIM, algoritmos.KRUSKAL):
            self.concluir_arvore_minima()
            return
        if self.chave in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
            self.concluir_limitada(destino)
            return
        if self.chave == algoritmos.BIDIRECIONAL:
            self.concluir_bidirecional(destino)
            return
        if self.chave == algoritmos.FLOYD_WARSHALL:
            self.concluir_floyd_warshall(destino)
            return
        if self.chave == algoritmos.BELLMAN_FORD and self.busca.ciclo_negativo:
            self.anotar_ciclo_negativo()
            return
        if self.chave in (algoritmos.LARGURA, algoritmos.DIJKSTRA, algoritmos.BELLMAN_FORD):
            self.anotar_distancias()
            self.anotar_arvore()
        if destino is not None:
            self.anotar_caminho(destino)
        if self.chave in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
            self.anotar_comparacao(destino)
            self.anotar_heuristica(destino)

    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)

    # ------------------------------------------------------------------

    def anotar_distancias(self):
        partes = []
        nao_alcancados = []
        for vertice in self.nomes:
            partes.append(f"{vertice} = {formatar_numero(self.distancia(vertice))}")
            if self.distancia(vertice) == INFINITO:
                nao_alcancados.append(vertice)
        unidade = "custo"
        if self.chave == algoritmos.LARGURA:
            unidade = "arestas"
        mensagem = f"Distâncias a partir de {self.busca.origem} ({unidade}): " + ", ".join(partes)
        if nao_alcancados:
            mensagem += ". Não alcançados (d = ∞): " + ", ".join(nao_alcancados)
        self.resultado["distancias"] = mensagem
        self.anotar("resultado_distancias", mensagem, {"nao_alcancados": nao_alcancados})

    def anotar_arvore(self):
        arestas = []
        for vertice in self.nomes:
            if vertice in self.busca.aresta_do_pai:
                arestas.append(self.busca.aresta_do_pai[vertice])
        nome = "Árvore de caminhos mínimos"
        if self.chave == algoritmos.LARGURA:
            nome = "Árvore da busca em largura"
        mensagem = (f"{nome}: cada vértice alcançado aponta para o pai (π); são "
                    f"{len(arestas)} arestas, uma para cada vértice alcançado menos a origem")
        self.anotar("resultado_arvore", mensagem, {"arestas": arestas})

    # O caminho até o destino: sobe pelos pais a partir do destino e depois inverte
    def caminho_ate(self, destino):
        if self.distancia(destino) == INFINITO:
            return None, None
        vertices = [destino]
        arestas = []
        atual = destino
        while self.busca.pai[atual] is not None:
            arestas.append(self.busca.aresta_do_pai[atual])
            atual = self.busca.pai[atual]
            vertices.append(atual)
        vertices.reverse()
        arestas.reverse()
        return vertices, arestas

    def anotar_caminho(self, destino):
        alcancou = self.distancia(destino) != INFINITO
        if self.chave in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
            alcancou = self.busca.chegou
        if not alcancou:
            mensagem = f"Não existe caminho de {self.busca.origem} até {destino} (d = ∞)"
            self.resultado["caminho"] = None
            self.anotar("resultado_caminho", mensagem, {"caminho": [], "arestas": [], "custo": None})
            return
        vertices, arestas = self.caminho_ate(destino)
        separador = " -> "
        if not self.direcionado:
            separador = " — "
        custo = self.distancia(destino)
        unidade = f"custo {formatar_numero(custo)}"
        if self.chave == algoritmos.LARGURA or (self.chave == algoritmos.GULOSA and not self.busca.usa_pesos):
            unidade = f"{len(arestas)} arestas"
        mensagem = f"Caminho de {self.busca.origem} até {destino}: {separador.join(vertices)} ({unidade})"
        self.resultado["caminho"] = vertices
        self.resultado["custo"] = custo
        self.anotar("resultado_caminho", mensagem, {"caminho": vertices, "arestas": arestas, "custo": custo})

    def anotar_ciclo_negativo(self):
        ciclo = self.busca.ciclo_negativo
        soma = 0
        for numero in self.busca.arestas_do_ciclo:
            soma += self.grafo.arestas[numero].peso
        separador = " -> "
        if not self.direcionado:
            separador = " — "
        mensagem = (f"Ciclo negativo {separador.join(ciclo)} (soma dos pesos = {formatar_numero(soma)}): "
                    f"cada volta nele diminui o custo, então os caminhos mínimos não existem")
        self.resultado["ciclo_negativo"] = ciclo
        self.anotar("resultado_ciclo_negativo", mensagem,
                    {"ciclo": list(ciclo), "arestas": list(self.busca.arestas_do_ciclo), "soma": soma})

    # Gulosa e A*: o custo encontrado comparado com o melhor possível, e quantos vértices
    # foram expandidos comparado com o Dijkstra (que não tem estimativa nenhuma).
    # O Dijkstra e a BFS rodam aqui "escondidos", com uma lista de passos que é jogada fora.
    def anotar_comparacao(self, destino):
        if not self.busca.chegou:
            return
        usa_pesos = self.chave == algoritmos.A_ESTRELA or self.busca.usa_pesos
        if usa_pesos:
            referencia = Dijkstra(self.grafo, [])
            referencia.dijkstra(self.busca.origem)
            melhor = referencia.d[destino]
            expandidos_pela_referencia = referencia.ordem_de_extracao.index(destino) + 1
            nome_da_referencia = "pelo Dijkstra"
        else:
            referencia = BuscaEmLargura(self.grafo, [])
            referencia.bfs(self.busca.origem)
            melhor = referencia.d[destino]
            expandidos_pela_referencia = None
            nome_da_referencia = "pela busca em largura"
        encontrado = self.distancia(destino)
        expandidos = len(self.busca.ordem_de_expansao)
        if encontrado == melhor:
            mensagem = f"O caminho encontrado é o de menor custo possível ({formatar_numero(melhor)})"
        else:
            mensagem = (f"O caminho encontrado custa {formatar_numero(encontrado)}, mas o menor custo possível "
                        f"é {formatar_numero(melhor)} ({nome_da_referencia})")
            if self.chave == algoritmos.GULOSA:
                mensagem += ": a gulosa não garante o melhor caminho"
        mensagem += f". Vértices expandidos: {expandidos}"
        if expandidos_pela_referencia is not None:
            mensagem += f" (o Dijkstra expandiria {expandidos_pela_referencia} até chegar em {destino})"
        self.resultado["otimo"] = encontrado == melhor
        self.anotar("resultado_comparacao", mensagem,
                    {"encontrado": encontrado, "melhor": melhor, "otimo": encontrado == melhor, "expandidos": expandidos,
                     "expandidos_pela_referencia": expandidos_pela_referencia})

    def anotar_heuristica(self, destino):
        vertices = self.nomes
        arestas = []
        for aresta in self.grafo.arestas:
            arestas.append((aresta.vertice_origem.nome, aresta.vertice_destino.nome, aresta.nome, aresta.peso))
        custo = algoritmos.custos_ate_o_destino(vertices, arestas, destino, self.direcionado)
        if custo is None:
            mensagem = "Sem pesos em todas as arestas não dá para conferir se h é admissível"
            self.anotar("resultado_heuristica", mensagem, {"admissivel": None, "consistente": None,
                                                           "vertices": []})
            return
        exageros = algoritmos.violacoes_de_admissibilidade(vertices, self.heuristica, custo)
        quebras = algoritmos.violacoes_de_consistencia(arestas, self.direcionado, self.heuristica)
        marcados = []
        if exageros:
            textos = []
            for vertice, h, real in exageros[:3]:
                textos.append(f"h({vertice}) = {formatar_numero(h)} > {formatar_numero(real)}")
                marcados.append(vertice)
            mensagem = "h NÃO é admissível (passa do custo real até o destino): " + ", ".join(textos)
        else:
            mensagem = "h é admissível: em nenhum vértice ela passa do custo real até o destino"
        if quebras:
            u, v = quebras[0]
            mensagem += f"; não é consistente (h({u}) > peso({u}, {v}) + h({v}))"
        else:
            mensagem += "; e é consistente (em toda aresta, h cai no máximo o peso da aresta)"
        if self.chave == algoritmos.A_ESTRELA and self.busca.reaberturas:
            mensagem += f". Reaberturas: {self.busca.reaberturas}"
        self.anotar("resultado_heuristica", mensagem,
                    {"admissivel": not exageros, "consistente": not quebras, "vertices": marcados})

    # ------------------------------------------------------------------
    # Busca limitada e aprofundamento iterativo
    # ------------------------------------------------------------------

    def concluir_limitada(self, destino):
        busca = self.busca
        if busca.resultado == ACHOU:
            self.anotar_caminho_pronto(busca.caminho, busca.arestas_do_caminho)
        else:
            self.anotar_limitada(destino)
        if self.chave == algoritmos.ITERATIVA:
            self.anotar_iteracoes(destino)

    # Não achou (ou não havia destino): o que a busca alcançou e onde o limite cortou
    def anotar_limitada(self, destino):
        busca = self.busca
        alcancados = []
        for vertice in self.nomes:
            if busca.cor[vertice] != "Branco":
                alcancados.append(vertice)
        cortados = []
        for vertice in busca.cortados:
            if vertice not in cortados:
                cortados.append(vertice)
        if busca.resultado == CORTE:
            if destino is None:
                mensagem = (f"Com limite {busca.limite}, a busca alcançou {len(alcancados)} vértices e o limite "
                            f"cortou em {', '.join(cortados)}: além deles pode haver mais")
            else:
                mensagem = (f"Corte: {destino} não apareceu até a profundidade {busca.limite}, mas o limite cortou "
                            f"em {', '.join(cortados)}. Com um limite maior a busca pode achar")
        else:
            if destino is None:
                mensagem = (f"Com limite {busca.limite}, a busca alcançou {len(alcancados)} vértices e nada foi "
                            f"cortado: ela viu tudo o que dá para alcançar a partir de {busca.origem}")
            else:
                mensagem = (f"Falha: {destino} não é alcançável a partir de {busca.origem} (nada foi cortado: "
                            f"nenhum limite maior ajudaria)")
        self.resultado["limitada"] = busca.resultado
        self.anotar("resultado_limitada", mensagem, {"resultado": busca.resultado, "alcancados": alcancados,
                                                     "cortados": cortados})

    # Quantos nós cada rodada gerou, e a comparação com a busca em largura (que acha a mesma
    # profundidade, mas guarda a fila inteira na memória)
    def anotar_iteracoes(self, destino):
        partes = []
        total = 0
        for limite, nos, resultado in self.busca.iteracoes:
            partes.append(f"limite {limite}: {nos}")
            total += nos
        mensagem = f"Nós gerados em cada rodada ({', '.join(partes)}); total {total}"
        if self.busca.resultado == ACHOU:
            referencia = BuscaEmLargura(self.grafo, [])
            referencia.bfs(self.busca.origem)
            mensagem += (f". Achou com limite {self.busca.limite}: é a mesma distância da busca em largura "
                         f"({formatar_numero(referencia.d[destino])} arestas)")
        self.anotar("resultado_iteracoes", mensagem, {"iteracoes": list(self.busca.iteracoes), "total": total})

    # ------------------------------------------------------------------
    # Busca bidirecional
    # ------------------------------------------------------------------

    def concluir_bidirecional(self, destino):
        busca = self.busca
        if busca.caminho is None:
            mensagem = f"Não existe caminho de {busca.origem} até {destino}: as buscas não se encontraram"
            self.resultado["caminho"] = None
            self.anotar("resultado_caminho", mensagem, {"caminho": [], "arestas": [], "custo": None})
            return
        self.anotar_caminho_pronto(busca.caminho, busca.arestas_do_caminho)
        # Comparação: quantos vértices a busca em largura sozinha tiraria da fila até chegar no destino
        referencia = BuscaEmLargura(self.grafo, [])
        referencia.bfs(busca.origem)
        expandidos = len(busca.ordem_de_expansao)
        mensagem = (f"Vértices expandidos: {expandidos} ({self.contar_lado('frente')} pela frente e "
                    f"{self.contar_lado('tras')} por trás). O caminho tem {len(busca.caminho) - 1} arestas, a "
                    f"mesma distância da busca em largura ({formatar_numero(referencia.d[destino])})")
        self.anotar("resultado_comparacao", mensagem, {"expandidos": expandidos,
                                                       "melhor": referencia.d[destino],
                                                       "encontrado": len(busca.caminho) - 1, "otimo": True})

    def contar_lado(self, lado):
        quantos = 0
        for lado_da_expansao, vertice in self.busca.ordem_de_expansao:
            if lado_da_expansao == lado:
                quantos += 1
        return quantos

    # O caminho que a própria busca já montou (busca limitada, iterativa e bidirecional):
    # o tamanho é em arestas; se todas as arestas do caminho têm peso, a soma vai junto
    def anotar_caminho_pronto(self, vertices, arestas):
        separador = " -> "
        if not self.direcionado:
            separador = " — "
        mensagem = f"Caminho de {vertices[0]} até {vertices[-1]}: {separador.join(vertices)} ({len(arestas)} arestas"
        pesos = []
        for numero in arestas:
            pesos.append(self.grafo.arestas[numero].peso)
        if arestas and None not in pesos:
            soma = 0
            for peso in pesos:
                soma += peso
            mensagem += f", custo {formatar_numero(soma)}"
        mensagem += ")"
        self.resultado["caminho"] = list(vertices)
        self.anotar("resultado_caminho", mensagem, {"caminho": list(vertices), "arestas": list(arestas),
                                                    "custo": len(arestas)})

    # ------------------------------------------------------------------
    # Floyd-Warshall
    # ------------------------------------------------------------------

    def concluir_floyd_warshall(self, destino):
        busca = self.busca
        if busca.ciclo_negativo:
            textos = []
            for vertice in busca.ciclo_negativo:
                textos.append(f"d[{vertice}][{vertice}] = {formatar_numero(busca.d[vertice][vertice])}")
            mensagem = ("Ciclo negativo: " + ", ".join(textos) + ". Esses vértices conseguem sair e voltar com "
                        "custo negativo, então os menores custos não existem (cada volta diminui mais)")
            self.anotar("resultado_diagonal_negativa", mensagem, {"vertices": list(busca.ciclo_negativo)})
            return
        alcancaveis = 0
        for i in busca.vertices:
            for j in busca.vertices:
                if i != j and busca.d[i][j] != INFINITO:
                    alcancaveis += 1
        mensagem = (f"Matriz final: o menor custo entre todos os pares ({alcancaveis} pares com caminho, de "
                    f"{len(busca.vertices) * (len(busca.vertices) - 1)} pares de vértices diferentes). "
                    f"{busca.comparacoes} comparações, {busca.melhoras} melhoras")
        self.anotar("resultado_matriz", mensagem, {"pares": alcancaveis})
        origem = self.inicio
        if destino is not None and origem is not None:
            vertices, arestas = busca.caminho(origem, destino)
            separador = " -> " if self.direcionado else " — "
            if vertices is None:
                mensagem = f"Não existe caminho de {origem} até {destino} (d[{origem}][{destino}] = ∞)"
                self.anotar("resultado_caminho", mensagem, {"caminho": [], "arestas": [], "custo": None})
            else:
                custo = busca.d[origem][destino]
                mensagem = (f"Caminho de {origem} até {destino} (seguindo π de trás para frente): "
                            f"{separador.join(vertices)} (custo {formatar_numero(custo)})")
                self.anotar("resultado_caminho", mensagem, {"caminho": vertices, "arestas": arestas,
                                                            "custo": custo})

    # ------------------------------------------------------------------
    # Árvore geradora mínima (Prim e Kruskal)
    # ------------------------------------------------------------------

    def concluir_arvore_minima(self):
        if self.chave == algoritmos.PRIM:
            arestas = arestas_do_prim(self.busca)
        else:
            arestas = list(self.busca.arvore)
        total = self.peso_total(arestas)
        self.anotar_arvore_minima(arestas, total)
        self.anotar_mesmo_peso(arestas, total)

    def peso_total(self, arestas):
        total = 0
        for numero in arestas:
            total += self.grafo.arestas[numero].peso
        return total

    # "a — b (4)": uma aresta com o peso
    def texto_da_aresta(self, numero):
        aresta = self.grafo.arestas[numero]
        return f"{aresta.vertice_origem.nome} — {aresta.vertice_destino.nome} ({formatar_numero(aresta.peso)})"

    # As arestas da árvore (ou da floresta) e o peso total, com a conta: "1 + 2 + 2 + 4 = 9"
    def anotar_arvore_minima(self, arestas, total):
        n = len(self.nomes)
        partes = n - len(arestas)           # cada aresta aceita junta duas partes em uma
        pesos = []
        for numero in arestas:
            peso = self.grafo.arestas[numero].peso
            pesos.append(f"({formatar_numero(peso)})" if peso < 0 else formatar_numero(peso))
        conta = formatar_numero(total)
        if 1 < len(pesos) <= 12:
            conta = " + ".join(pesos) + " = " + formatar_numero(total)
        if n == 1:
            mensagem = f"Árvore geradora mínima: só o vértice {self.nomes[0]}, sem arestas (peso total 0)"
        elif not arestas:
            mensagem = (f"Floresta geradora mínima: nenhuma aresta liga vértices diferentes, então cada um dos {n} "
                        f"vértices é uma árvore sozinho (peso total 0)")
        elif partes == 1:
            mensagem = (f"Árvore geradora mínima: {len(arestas)} arestas (n − 1 = {n} − 1) ligam os {n} vértices, "
                        f"peso total {conta}")
        else:
            mensagem = (f"Floresta geradora mínima: {partes} árvores (uma por parte desligada), {len(arestas)} arestas "
                        f"(n − partes = {n} − {partes}), peso total {conta}")
        self.anotar("resultado_arvore_minima", mensagem, {"arestas": list(arestas), "total": total, "partes": partes})

    # O outro algoritmo (Kruskal para o Prim, Prim para o Kruskal) roda escondido, com uma lista de passos
    # que é jogada fora: o peso total tem que ser o mesmo (as arestas podem mudar, se houver pesos iguais)
    def anotar_mesmo_peso(self, arestas, total):
        if self.chave == algoritmos.PRIM:
            outro = Kruskal(self.grafo, [])
            outro.kruskal()
            outras = list(outro.arvore)
            nome = "O Kruskal"
        else:
            outro = Prim(self.grafo, [])
            outro.prim(self.inicio)
            outras = arestas_do_prim(outro)
            nome = "O Prim"
        outro_total = self.peso_total(outras)
        so_aqui = []
        for numero in arestas:
            if numero not in outras:
                so_aqui.append(numero)
        so_no_outro = []
        for numero in outras:
            if numero not in arestas:
                so_no_outro.append(numero)
        # O peso total da árvore mínima é sempre o mesmo (os testes conferem outro_total == total)
        mesmas = not so_aqui and not so_no_outro
        if mesmas:
            mensagem = (f"{nome} (rodando escondido, só para comparar) escolheu as mesmas {len(arestas)} arestas, "
                        f"com o mesmo peso total ({formatar_numero(outro_total)})")
        else:
            mensagem = (f"{nome} (rodando escondido, só para comparar) chegou ao mesmo peso total "
                        f"({formatar_numero(outro_total)}) com outras arestas: aqui "
                        f"{', '.join(self.texto_da_aresta(numero) for numero in so_aqui)}; no "
                        f"{nome.split()[1]}, {', '.join(self.texto_da_aresta(numero) for numero in so_no_outro)}. "
                        f"Com pesos repetidos pode haver mais de uma árvore mínima, todas com o mesmo peso")
        if mesmas and pesos_todos_diferentes(self.grafo.arestas):
            mensagem += ". Como os pesos são todos diferentes, a árvore mínima é única"
        self.anotar("resultado_mesmo_peso", mensagem,
                    {"arestas": list(arestas), "outras": list(outras), "mesmas": mesmas, "total": total,
                     "outro_total": outro_total, "diferentes": so_aqui + so_no_outro})


# As arestas que o Prim escolheu, na ordem em que entraram na árvore: a aresta do pai de cada vértice que
# saiu da fila (as raízes não têm)
def arestas_do_prim(busca):
    arestas = []
    for vertice in busca.ordem_de_extracao:
        if vertice in busca.aresta_do_pai:
            arestas.append(busca.aresta_do_pai[vertice])
    return arestas


# Nenhum peso se repete (sem contar os laços, que nunca entram na árvore)? Então a árvore mínima é única.
def pesos_todos_diferentes(arestas):
    pesos = [aresta.peso for aresta in arestas if aresta.vertice_origem.nome != aresta.vertice_destino.nome]
    return len(set(pesos)) == len(pesos)          # o set joga fora os pesos repetidos
