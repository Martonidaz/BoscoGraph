# Tudo o que a tela mostra num determinado passo.
#
# A janela cria um EstadoVisual novo e aplica os passos 0, 1, 2, ... até o passo atual.
# Voltar um passo é só criar de novo e aplicar um passo a menos.
# Este arquivo não usa Tkinter: dá para testar sem abrir janela nenhuma.

import algoritmos
from entrada import INFINITO


class EstadoVisual:
    def __init__(self, arestas, direcionado=True, algoritmo=algoritmos.PROFUNDIDADE):
        # arestas: lista de (origem, destino, nome, peso) na ordem em que foram criadas
        self.arestas = arestas
        self.direcionado = direcionado
        self.algoritmo = algoritmo

        # Situação de cada aresta na tela, na mesma ordem da lista acima:
        # "invisivel" -> ainda não foi criada
        # "objeto"    -> o objeto Aresta existe, mas ainda não entrou no grafo
        # "grafo"     -> já está na lista de adjacência
        # DFS: "arvore", "retorno", "avanco" ou "cruzamento" -> já foi examinada pela busca
        # Outras buscas: "arvore" (é a aresta do pai: o melhor caminho conhecido) ou
        #                "examinada" (a busca olhou para ela, mas ela não está no caminho)
        # Prim: "candidata" (a ligação mais leve conhecida de um vértice da fila: ainda pode mudar),
        #       "arvore" (já está na árvore) ou "examinada" (ficou de fora)
        # Kruskal: "arvore" (aceita) ou "examinada" (recusada: fecharia um ciclo)
        self.situacao_aresta = []
        self.revisitada = []            # não orientado: a busca já passou pela "volta" desta aresta?
        for aresta in arestas:
            self.situacao_aresta.append("invisivel")
            self.revisitada.append(False)

        self.vertices_criados = []      # vértices já desenhados, na ordem de criação
        self.lista = {}                 # lista de adjacência como está neste passo
        self.pesos_da_lista = {}        # os pesos dos vizinhos, na mesma ordem da lista
        self.ordenou = None             # True/False depois da etapa de ordenação
        self.cor = {}                   # cor de cada vértice (None = ainda sem cor: a busca não começou)
        self.d = {}                     # DFS: tempos de descoberta já conhecidos
        self.f = {}                     # DFS: tempos de finalização já conhecidos
        self.tempo = None               # DFS: o relógio (None = a busca ainda não zerou o relógio)
        self.pilha = []                 # DFS: vértices Cinza, do primeiro ao último descoberto
        self.raizes = []                # DFS: raízes das árvores da busca; nas outras, a origem
        self.log = []                   # mensagens de todos os passos até aqui
        self.mensagem = ""              # a mensagem do último passo aplicado
        self.vertice_em_destaque = None
        self.aresta_em_destaque = None  # índice da aresta em destaque
        self.ultima_aresta_na_lista = None   # índice da última aresta que entrou numa lista (para a "volta")

        # As outras buscas
        self.distancia = {}             # d (BFS, Dijkstra, Bellman-Ford), g (gulosa, A*) ou a chave (Prim); infinito = ∞
        self.prioridade = {}            # a chave da fila de prioridade (d no Dijkstra, h na gulosa, f no A*)
        self.h = {}                     # a heurística (gulosa e A*)
        self.pai = {}                   # π
        self.fila = []                  # a fila (BFS) ou a fronteira (fila de prioridade), na ordem de entrada
        self.rodada = None              # Bellman-Ford: a rodada atual e o total
        self.total_de_rodadas = None
        self.melhoras_na_rodada = []    # Bellman-Ford: números das arestas que melhoraram alguém nesta rodada
                                        # (no Floyd-Warshall: os pares (i, j) que melhoraram nesta rodada)
        self.arco_atual = None          # Bellman-Ford: (número da aresta, de, até) sendo relaxada agora

        # Busca limitada e aprofundamento iterativo (a pilha é o caminho atual: self.pilha)
        self.profundidade = {}          # a profundidade de cada vértice no caminho (a última vez que entrou)
        self.cortados = []              # onde o limite cortou (nesta rodada)
        self.limite_atual = None        # o limite de profundidade (no iterativo, o da rodada)
        self.iteracao = 0               # aprofundamento iterativo: quantas rodadas já começaram

        # Busca bidirecional
        self.lado = {}                  # "frente" ou "tras" (quem descobriu o vértice)
        self.distancia_tras = {}        # arestas até o destino (lado de trás)
        self.pai_tras = {}              # π de trás: o próximo vértice no caminho até o destino
        self.fila_tras = []             # a fila de trás (a da frente é self.fila)
        self.lado_atual = None          # o lado que está expandindo agora

        # Floyd-Warshall: as matrizes, com chave (i, j)
        self.matriz_d = {}
        self.matriz_pi = {}
        self.aresta_da_matriz = {}      # (i, j) -> o número da aresta usada de i para j
        self.k_atual = None             # o vértice k da rodada
        self.par_atual = None           # o par (i, j) que está sendo comparado

        # Árvore geradora mínima (versão 7.3)
        self.conjunto = {}              # Kruskal: o representante do conjunto de cada vértice
        self.cor_do_conjunto = {}       # Kruskal: representante -> número da cor (só os conjuntos com 2 ou mais)
        self.proxima_cor = 0
        self.ordem_das_arestas = []     # Kruskal: os números das arestas, da mais leve para a mais pesada
        self.decisao = {}               # Kruskal: número da aresta -> "aceita" ou "rejeitada"
        self.aresta_atual = None        # Kruskal: a aresta examinada agora
        self.arvore_minima = []         # as arestas que já estão na árvore, na ordem em que entraram
        self.peso_da_arvore = 0         # a soma dos pesos delas

        # Etapa 6: o que fica marcado no desenho e como os vértices são arrumados
        self.arestas_marcadas = []      # índices das arestas destacadas (um ciclo, os laços, um caminho...)
        self.vertices_marcados = []
        self.caminho_final = None       # (vértices, arestas) do caminho do resultado: continua marcado até o fim
        self.layout = "circulo"         # "circulo" ou "linha" (a linha mostra a ordem topológica)
        self.ordem_topologica = []
        self.resumo_do_tipo = ""

    # Atualiza a tela de acordo com um passo anotado
    def aplicar(self, passo):
        tipo = passo["tipo"]
        mensagem = passo["mensagem"]
        self.vertice_em_destaque = None
        self.aresta_em_destaque = None
        self.arestas_marcadas = []
        self.vertices_marcados = []
        self.arco_atual = None

        if tipo == "criar_vertice":
            vertice = passo["vertice"]
            self.vertices_criados.append(vertice)
            self.cor[vertice] = None
            self.vertice_em_destaque = vertice

        elif tipo == "criar_aresta":
            indice = self.achar_aresta(passo["origem"], passo["destino"], ["invisivel"])
            self.situacao_aresta[indice] = "objeto"
            self.aresta_em_destaque = indice

        elif tipo == "criar_lista":
            self.lista[passo["vertice"]] = []
            self.pesos_da_lista[passo["vertice"]] = []
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "adicionar_vizinho":
            if passo.get("volta"):
                # Não orientado: a mesma aresta do passo anterior, agora na lista do outro vértice
                indice = self.ultima_aresta_na_lista
            else:
                indice = self.achar_aresta(passo["origem"], passo["destino"], ["objeto"])
                self.situacao_aresta[indice] = "grafo"
                self.ultima_aresta_na_lista = indice
            self.lista[passo["origem"]].append(passo["destino"])
            self.pesos_da_lista[passo["origem"]].append(passo.get("peso"))
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = passo["origem"]
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "ordenar":
            self.lista[passo["vertice"]] = list(passo["lista"])
            if "pesos" in passo:
                self.pesos_da_lista[passo["vertice"]] = list(passo["pesos"])
            self.ordenou = True
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "sem_ordenar":
            self.ordenou = False

        elif tipo in ("pintar_branco", "zerar_tempo", "nova_arvore", "descobrir", "examinar", "revisitar",
                      "finalizar") or tipo.startswith("tipo_") or tipo == "ordem_topologica":
            mensagem = self.aplicar_profundidade(passo, mensagem)

        elif self.algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA) and not tipo.startswith("resultado_"):
            mensagem = self.aplicar_limitada(passo, mensagem)

        elif self.algoritmo == algoritmos.FLOYD_WARSHALL and not tipo.startswith("resultado_"):
            mensagem = self.aplicar_floyd_warshall(passo, mensagem)

        elif self.algoritmo == algoritmos.PRIM and not tipo.startswith("resultado_"):
            mensagem = self.aplicar_prim(passo, mensagem)

        elif self.algoritmo == algoritmos.KRUSKAL and not tipo.startswith("resultado_"):
            mensagem = self.aplicar_kruskal(passo, mensagem)

        elif self.algoritmo == algoritmos.BIDIRECIONAL and passo.get("lado") == "tras":
            mensagem = self.aplicar_lado_de_tras(passo, mensagem)

        else:
            mensagem = self.aplicar_outras_buscas(passo, mensagem)

        self.mensagem = mensagem
        self.log.append(mensagem)

    # ------------------------------------------------------------------
    # Busca em profundidade e o tipo do grafo
    # ------------------------------------------------------------------

    def aplicar_profundidade(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "pintar_branco":
            self.cor[passo["vertice"]] = "Branco"
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "zerar_tempo":
            self.tempo = 0

        elif tipo == "nova_arvore":
            self.raizes.append(passo["vertice"])
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "descobrir":
            vertice = passo["vertice"]
            self.cor[vertice] = "Cinza"
            self.d[vertice] = passo["tempo"]
            self.tempo = passo["tempo"]
            self.pilha.append(vertice)          # entra no topo da pilha
            self.vertice_em_destaque = vertice

        elif tipo == "examinar":
            indice = self.achar_aresta(passo["origem"], passo["destino"], ["grafo"])
            self.situacao_aresta[indice] = passo["classe"]
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = passo["origem"]
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "revisitar":
            # Não orientado: a volta de uma aresta que já foi examinada (não muda a situação dela)
            indice = self.achar_aresta(passo["origem"], passo["destino"], ["arvore", "retorno"], True)
            self.revisitada[indice] = True
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = passo["origem"]
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "finalizar":
            vertice = passo["vertice"]
            self.cor[vertice] = "Preto"
            self.f[vertice] = passo["tempo"]
            self.tempo = passo["tempo"]
            self.pilha.pop()                    # sai do topo da pilha: é sempre o último Cinza
            self.vertice_em_destaque = vertice

        elif tipo == "tipo_simples":
            self.marcar_lacos_e_paralelas()

        elif tipo == "tipo_valorado":
            for indice in range(len(self.arestas)):
                if self.arestas[indice][3] is not None:
                    self.arestas_marcadas.append(indice)

        elif tipo == "tipo_ciclo":
            if passo["ciclico"]:
                self.marcar_ciclo(passo["ciclo"])

        elif tipo == "tipo_componentes":
            self.vertices_marcados = list(passo["raizes"])

        elif tipo == "ordem_topologica":
            self.layout = "linha"
            self.ordem_topologica = list(passo["ordem"])

        elif tipo == "tipo_resumo":
            self.resumo_do_tipo = passo["resumo"]
        return mensagem

    # ------------------------------------------------------------------
    # Largura, Dijkstra, Bellman-Ford, gulosa e A*
    # (os passos trazem o número da aresta: não é preciso procurar qual é)
    # ------------------------------------------------------------------

    def aplicar_outras_buscas(self, passo, mensagem):
        tipo = passo["tipo"]
        usa_fila = self.algoritmo != algoritmos.BELLMAN_FORD

        if tipo == "inicializar":
            vertice = passo["vertice"]
            self.cor[vertice] = "Branco"
            self.distancia[vertice] = INFINITO
            self.pai[vertice] = None
            if "h" in passo:
                self.h[vertice] = passo["h"]
            self.vertice_em_destaque = vertice

        elif tipo == "origem":
            vertice = passo["vertice"]
            self.cor[vertice] = "Cinza"
            self.distancia[vertice] = passo["distancia"]
            if "prioridade" in passo:
                self.prioridade[vertice] = passo["prioridade"]
            self.raizes = [vertice]
            if usa_fila:
                self.fila.append(vertice)
            if "lado" in passo:
                self.lado[vertice] = passo["lado"]
            self.vertice_em_destaque = vertice

        elif tipo == "desenfileirar":
            # BFS: sai da frente da fila, mas continua Cinza até todos os vizinhos serem vistos
            self.fila.pop(0)
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "extrair":
            # Fila de prioridade: sai da fronteira e fica Preto (definitivo / expandido)
            vertice = passo["vertice"]
            self.fila.remove(vertice)
            self.cor[vertice] = "Preto"
            self.vertice_em_destaque = vertice

        elif tipo == "descobrir_vizinho":
            # BFS e gulosa: o vizinho é visto pela primeira vez, ganha pai e entra na fila
            vizinho = passo["destino"]
            indice = passo["aresta"]
            self.cor[vizinho] = "Cinza"
            self.distancia[vizinho] = passo["distancia"]
            self.pai[vizinho] = passo["origem"]
            if "prioridade" in passo:
                self.prioridade[vizinho] = passo["prioridade"]
            self.fila.append(vizinho)
            if "lado" in passo:
                self.lado[vizinho] = passo["lado"]
            self.situacao_aresta[indice] = "arvore"
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = vizinho
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "ignorar_vizinho":
            indice = passo["aresta"]
            if self.situacao_aresta[indice] not in ("arvore", "arvore_tras"):
                self.situacao_aresta[indice] = "examinada"
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = passo["origem"]
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "terminar_vertice":
            self.cor[passo["vertice"]] = "Preto"
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "relaxar":
            mensagem = self.aplicar_relaxamento(passo, mensagem, usa_fila)

        elif tipo == "rodada":
            self.rodada = passo["numero"]
            self.total_de_rodadas = passo["total"]
            self.melhoras_na_rodada = []

        elif tipo == "ciclo_negativo":
            self.arestas_marcadas = list(passo["arestas_do_ciclo"])
            self.vertices_marcados = list(passo["ciclo"][:-1])
            self.aresta_em_destaque = passo["aresta"]

        elif tipo == "chegou":
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "nova_camada":
            self.lado_atual = passo["lado"]

        elif tipo == "encontro":
            # Bidirecional: as duas buscas se encontraram (pela aresta do passo, ou na própria origem)
            if passo.get("na_origem"):
                self.vertice_em_destaque = passo["vertice"]
            else:
                self.arestas_marcadas = [passo["aresta"]]
                self.vertices_marcados = [passo["origem"], passo["destino"]]
                self.aresta_em_destaque = passo["aresta"]
                mensagem = self.com_nome_da_aresta(mensagem, passo["aresta"])

        elif tipo == "resultado_distancias":
            # Bellman-Ford: só no fim as distâncias ficam definitivas (Preto)
            for vertice in self.cor:
                if self.cor[vertice] == "Cinza" and self.algoritmo == algoritmos.BELLMAN_FORD:
                    self.cor[vertice] = "Preto"
            self.vertices_marcados = list(passo["nao_alcancados"])

        elif tipo in ("resultado_arvore", "resultado_caminho", "resultado_ciclo_negativo"):
            self.arestas_marcadas = list(passo["arestas"])
            if tipo == "resultado_caminho":
                self.vertices_marcados = list(passo["caminho"])
                self.caminho_final = (list(passo["caminho"]), list(passo["arestas"]))
            elif tipo == "resultado_ciclo_negativo":
                self.vertices_marcados = list(passo["ciclo"][:-1])

        elif tipo == "resultado_limitada":
            self.vertices_marcados = list(passo["cortados"])

        elif tipo == "resultado_diagonal_negativa":
            self.vertices_marcados = list(passo["vertices"])

        elif tipo == "resultado_arvore_minima":
            self.arestas_marcadas = list(passo["arestas"])

        elif tipo == "resultado_mesmo_peso":
            # As mesmas arestas: a árvore continua marcada. Arestas diferentes: as que mudam ficam marcadas.
            if passo["mesmas"]:
                self.arestas_marcadas = list(passo["arestas"])
            else:
                self.arestas_marcadas = list(passo["diferentes"])

        elif tipo in ("resultado_comparacao", "resultado_heuristica", "resultado_iteracoes"):
            # O caminho encontrado é a resposta da busca: continua marcado nos passos seguintes
            if self.caminho_final is not None:
                self.vertices_marcados = list(self.caminho_final[0])
                self.arestas_marcadas = list(self.caminho_final[1])
            if tipo == "resultado_heuristica":
                for vertice in passo["vertices"]:
                    if vertice not in self.vertices_marcados:
                        self.vertices_marcados.append(vertice)
        return mensagem

    # ------------------------------------------------------------------
    # Busca limitada e aprofundamento iterativo
    # ------------------------------------------------------------------

    def aplicar_limitada(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "inicializar":
            self.cor[passo["vertice"]] = "Branco"
            self.pai[passo["vertice"]] = None
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "nova_iteracao":
            # Uma rodada nova: tudo volta ao começo (Branco, caminho vazio, arestas só "no grafo")
            self.limite_atual = passo["limite"]
            self.iteracao += 1
            for vertice in self.vertices_criados:
                self.cor[vertice] = "Branco"
                self.pai[vertice] = None
            self.profundidade = {}
            self.pilha = []
            self.cortados = []
            self.raizes = []
            for indice in range(len(self.arestas)):
                if self.situacao_aresta[indice] not in ("invisivel", "objeto"):
                    self.situacao_aresta[indice] = "grafo"

        elif tipo == "entrar":
            vertice = passo["vertice"]
            self.cor[vertice] = "Cinza"
            self.profundidade[vertice] = passo["profundidade"]
            self.pai[vertice] = passo["origem"]
            self.pilha.append(vertice)
            self.limite_atual = passo["limite"]
            if passo["origem"] is None:
                self.raizes = [vertice]
            else:
                self.situacao_aresta[passo["aresta"]] = "arvore"
                self.aresta_em_destaque = passo["aresta"]
                mensagem = self.com_nome_da_aresta(mensagem, passo["aresta"])
            self.vertice_em_destaque = vertice

        elif tipo == "chegou":
            self.vertice_em_destaque = passo["vertice"]

        elif tipo in ("corte", "subir"):
            # O vértice sai do caminho (o topo da pilha); a aresta por onde ele entrou fica "examinada"
            vertice = passo["vertice"]
            self.cor[vertice] = "Preto"
            self.pilha.pop()
            if tipo == "corte":
                self.cortados.append(vertice)
            if passo["aresta"] is not None:
                self.situacao_aresta[passo["aresta"]] = "examinada"
            self.vertice_em_destaque = vertice

        elif tipo == "ignorar_vizinho":
            indice = passo["aresta"]
            if self.situacao_aresta[indice] != "arvore":
                self.situacao_aresta[indice] = "examinada"
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = passo["origem"]
            mensagem = self.com_nome_da_aresta(mensagem, indice)
        return mensagem

    # ------------------------------------------------------------------
    # Busca bidirecional: o lado de trás (o lado da frente usa os passos da busca em largura)
    # ------------------------------------------------------------------

    def aplicar_lado_de_tras(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "origem_tras":
            vertice = passo["vertice"]
            self.cor[vertice] = "Cinza"
            self.lado[vertice] = "tras"
            self.distancia_tras[vertice] = passo["distancia"]
            self.fila_tras.append(vertice)
            self.vertice_em_destaque = vertice

        elif tipo == "nova_camada":
            self.lado_atual = "tras"

        elif tipo == "desenfileirar":
            self.fila_tras.pop(0)
            self.vertice_em_destaque = passo["vertice"]

        elif tipo == "descobrir_vizinho":
            vizinho = passo["destino"]
            indice = passo["aresta"]
            self.cor[vizinho] = "Cinza"
            self.lado[vizinho] = "tras"
            self.distancia_tras[vizinho] = passo["distancia"]
            self.pai_tras[vizinho] = passo["origem"]
            self.fila_tras.append(vizinho)
            self.situacao_aresta[indice] = "arvore_tras"
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = vizinho
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        else:
            # ignorar_vizinho, terminar_vertice e encontro são iguais nos dois lados
            mensagem = self.aplicar_outras_buscas(passo, mensagem)
        return mensagem

    # ------------------------------------------------------------------
    # Floyd-Warshall
    # ------------------------------------------------------------------

    def aplicar_floyd_warshall(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "inicializar_linha":
            i = passo["vertice"]
            for j in self.vertices_criados:
                self.matriz_d[(i, j)] = INFINITO
                self.matriz_pi[(i, j)] = None
            self.matriz_d[(i, i)] = 0
            self.cor[i] = "Branco"
            self.vertice_em_destaque = i
            self.par_atual = (i, i)

        elif tipo == "arco_inicial":
            origem = passo["origem"]
            destino = passo["destino"]
            indice = passo["aresta"]
            if passo["melhorou"]:
                antiga = self.aresta_da_matriz.get((origem, destino))
                if antiga is not None and antiga != indice:
                    self.situacao_aresta[antiga] = "examinada"      # uma paralela mais barata tomou o lugar
                self.matriz_d[(origem, destino)] = passo["peso"]
                self.matriz_pi[(origem, destino)] = origem
                self.aresta_da_matriz[(origem, destino)] = indice
                self.situacao_aresta[indice] = "arvore"
            elif self.situacao_aresta[indice] != "arvore":
                self.situacao_aresta[indice] = "examinada"
            self.par_atual = (origem, destino)
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = origem
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "rodada_k":
            # O k anterior já foi usado (Preto); o novo k é o desta rodada (Cinza)
            if self.k_atual is not None:
                self.cor[self.k_atual] = "Preto"
            self.k_atual = passo["k"]
            self.cor[self.k_atual] = "Cinza"
            self.melhoras_na_rodada = []
            self.par_atual = None
            self.vertice_em_destaque = self.k_atual

        elif tipo == "comparar_par":
            i = passo["i"]
            j = passo["j"]
            k = passo["k"]
            # Os caminhos de agora de i até k e de k até j: é por eles que a pergunta passa
            self.arestas_marcadas = self.caminho_na_matriz(i, k) + self.caminho_na_matriz(k, j)
            if passo["melhorou"]:
                self.matriz_d[(i, j)] = passo["por_k"]
                self.matriz_pi[(i, j)] = self.matriz_pi[(k, j)]
                self.melhoras_na_rodada.append((i, j))
            self.par_atual = (i, j)
            self.vertices_marcados = [i, j]
            self.vertice_em_destaque = k

        elif tipo == "diagonal_negativa":
            self.vertices_marcados = [passo["vertice"]]
            self.par_atual = (passo["vertice"], passo["vertice"])

        elif tipo == "sem_ciclo_negativo":
            if self.k_atual is not None:
                self.cor[self.k_atual] = "Preto"
            self.par_atual = None
        return mensagem

    # ------------------------------------------------------------------
    # Prim: a árvore cresce a partir da raiz; a fila de prioridade é pela chave
    # ------------------------------------------------------------------

    def aplicar_prim(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "raiz":
            # Uma árvore nova começa (mais de uma só quando o grafo é desligado)
            vertice = passo["vertice"]
            self.cor[vertice] = "Cinza"
            self.distancia[vertice] = passo["chave"]
            self.prioridade[vertice] = passo["chave"]
            self.raizes.append(vertice)
            self.fila.append(vertice)
            self.vertice_em_destaque = vertice

        elif tipo == "extrair":
            # Sai da fila e entra na árvore: a ligação dele (tracejada) vira aresta da árvore
            vertice = passo["vertice"]
            self.fila.remove(vertice)
            self.cor[vertice] = "Preto"
            indice = passo["aresta"]
            if indice is not None:
                self.situacao_aresta[indice] = "arvore"
                self.arvore_minima.append(indice)
                self.peso_da_arvore += self.arestas[indice][3]
                self.aresta_em_destaque = indice
                mensagem = self.com_nome_da_aresta(mensagem, indice)
            self.vertice_em_destaque = vertice

        elif tipo == "atualizar":
            vizinho = passo["destino"]
            indice = passo["aresta"]
            if passo["melhorou"]:
                self.distancia[vizinho] = passo["depois"]
                self.prioridade[vizinho] = passo["depois"]
                self.pai[vizinho] = passo["origem"]
                antiga = passo.get("aresta_antiga")
                if antiga is not None and antiga != indice:
                    self.situacao_aresta[antiga] = "examinada"     # a ligação antiga era mais cara
                self.situacao_aresta[indice] = "candidata"         # a melhor ligação de agora (provisória)
                if passo["entrou"]:
                    self.cor[vizinho] = "Cinza"
                    self.fila.append(vizinho)
            elif self.situacao_aresta[indice] not in ("arvore", "candidata"):
                self.situacao_aresta[indice] = "examinada"
            self.aresta_em_destaque = indice
            self.vertice_em_destaque = vizinho
            mensagem = self.com_nome_da_aresta(mensagem, indice)
        else:
            # inicializar e ignorar_vizinho: iguais aos das outras buscas
            mensagem = self.aplicar_outras_buscas(passo, mensagem)
        return mensagem

    # ------------------------------------------------------------------
    # Kruskal: as arestas em ordem de peso e os conjuntos disjuntos
    # ------------------------------------------------------------------

    def aplicar_kruskal(self, passo, mensagem):
        tipo = passo["tipo"]
        if tipo == "criar_conjunto":
            vertice = passo["vertice"]
            self.cor[vertice] = "Branco"
            self.conjunto[vertice] = vertice
            self.vertice_em_destaque = vertice

        elif tipo == "ordenar_arestas":
            self.ordem_das_arestas = list(passo["ordem"])

        elif tipo in ("aceitar", "rejeitar"):
            indice = passo["aresta"]
            self.aresta_atual = indice
            if tipo == "aceitar":
                self.decisao[indice] = "aceita"
                self.situacao_aresta[indice] = "arvore"
                self.arvore_minima.append(indice)
                self.peso_da_arvore += passo["peso"]
            else:
                self.decisao[indice] = "rejeitada"
                self.situacao_aresta[indice] = "examinada"
                self.vertices_marcados = list(passo["membros"])     # o conjunto que já liga as duas pontas
            self.aresta_em_destaque = indice
            mensagem = self.com_nome_da_aresta(mensagem, indice)

        elif tipo == "unir":
            fica = passo["fica"]
            sai = passo["sai"]
            # A cor do conjunto novo: a de quem fica; senão, a do outro; senão (dois sozinhos), uma cor nova
            cor = self.cor_do_conjunto.get(fica, self.cor_do_conjunto.get(sai))
            if cor is None:
                cor = self.proxima_cor
                self.proxima_cor += 1
            self.cor_do_conjunto.pop(sai, None)
            self.cor_do_conjunto[fica] = cor
            for vertice in passo["mudaram"]:
                self.conjunto[vertice] = fica
            self.vertices_marcados = list(passo["membros"])
            self.aresta_atual = passo["aresta"]
            self.aresta_em_destaque = passo["aresta"]
            mensagem = self.com_nome_da_aresta(mensagem, passo["aresta"])
        return mensagem

    # Kruskal: o número da cor do conjunto de um vértice (None = sozinho, sem cor)
    def numero_da_cor_do_conjunto(self, vertice):
        representante = self.conjunto.get(vertice)
        if representante is None:
            return None
        return self.cor_do_conjunto.get(representante)

    # Kruskal: os conjuntos de agora, cada um como (representante, [membros]), na ordem dos vértices
    def conjuntos(self):
        lista = []
        posicao = {}
        for vertice in self.vertices_criados:
            if vertice not in self.conjunto:
                continue
            representante = self.conjunto[vertice]
            if representante not in posicao:
                posicao[representante] = len(lista)
                lista.append((representante, []))
            lista[posicao[representante]][1].append(vertice)
        return lista

    # As arestas do melhor caminho conhecido de i até j, seguindo π de trás para frente.
    # Devolve [] se não houver caminho (ou se π der voltas, o que só acontece com ciclo negativo).
    def caminho_na_matriz(self, i, j):
        arestas = []
        atual = j
        passos_dados = 0
        while atual != i:
            anterior = self.matriz_pi.get((i, atual))
            if anterior is None or passos_dados > len(self.vertices_criados):
                return []
            arestas.append(self.aresta_da_matriz[(anterior, atual)])
            atual = anterior
            passos_dados += 1
        arestas.reverse()
        return arestas

    # RELAX: a distância do vizinho pode diminuir; aí a aresta usada vira a "aresta do pai" (azul)
    # e a aresta do pai antigo volta a ser só "examinada"
    def aplicar_relaxamento(self, passo, mensagem, usa_fila):
        vizinho = passo["destino"]
        indice = passo["aresta"]
        if passo["melhorou"]:
            self.distancia[vizinho] = passo["depois"]
            self.pai[vizinho] = passo["origem"]
            if "prioridade" in passo:
                self.prioridade[vizinho] = passo["prioridade"]
            antiga = passo.get("aresta_antiga")
            if antiga is not None and antiga != indice:
                self.situacao_aresta[antiga] = "examinada"
            self.situacao_aresta[indice] = "arvore"
            if passo.get("entrou") or passo.get("reabriu"):
                self.cor[vizinho] = "Cinza"
                if usa_fila:
                    self.fila.append(vizinho)
            if self.rodada is not None:
                self.melhoras_na_rodada.append(indice)
        elif self.situacao_aresta[indice] != "arvore":
            self.situacao_aresta[indice] = "examinada"
        self.aresta_em_destaque = indice
        self.vertice_em_destaque = vizinho
        self.arco_atual = (indice, passo["origem"], vizinho)
        return self.com_nome_da_aresta(mensagem, indice)

    # ------------------------------------------------------------------
    # Ajudantes
    # ------------------------------------------------------------------

    # A aresta liga origem e destino? No não orientado, vale nos dois sentidos.
    def liga(self, indice, origem, destino):
        origem_da_aresta, destino_da_aresta, nome, peso = self.arestas[indice]
        if origem_da_aresta == origem and destino_da_aresta == destino:
            return True
        return not self.direcionado and origem_da_aresta == destino and destino_da_aresta == origem

    # Acha o índice da primeira aresta origem -> destino que está numa das situações pedidas.
    # É o que resolve as arestas paralelas: B -> C aparece duas vezes, e cada passo
    # pega a primeira que ainda não passou por aquela etapa.
    # so_nao_revisitadas=True: pula as arestas cuja volta já apareceu (não orientado)
    def achar_aresta(self, origem, destino, situacoes, so_nao_revisitadas=False):
        for indice in range(len(self.arestas)):
            if self.liga(indice, origem, destino) and self.situacao_aresta[indice] in situacoes:
                if not so_nao_revisitadas or not self.revisitada[indice]:
                    return indice
        raise ValueError(f"Não achei a aresta {origem} -> {destino} na situação {situacoes}")

    # A busca e o Grafo só guardam os nomes dos vértices nas listas; o nome da aresta
    # (quando existe) é acrescentado aqui, no fim da mensagem: "... (aresta de árvore) [e2]"
    def com_nome_da_aresta(self, mensagem, indice):
        nome = self.arestas[indice][2]
        if nome == "":
            return mensagem
        return f"{mensagem} [{nome}]"

    # Etapa 6: marca os laços e as arestas paralelas (o que impede o grafo de ser simples)
    def marcar_lacos_e_paralelas(self):
        for indice in range(len(self.arestas)):
            origem, destino, nome, peso = self.arestas[indice]
            repeticoes = 0
            for outro in range(len(self.arestas)):
                if self.liga(outro, origem, destino):
                    repeticoes += 1
            if origem == destino or repeticoes > 1:
                self.arestas_marcadas.append(indice)
                for vertice in (origem, destino):
                    if vertice not in self.vertices_marcados:
                        self.vertices_marcados.append(vertice)

    # Etapa 6: marca o ciclo de exemplo. O ciclo vem como a lista de vértices [v0, v1, ..., v0]:
    # cada par seguido é uma aresta de árvore, menos o último, que é a aresta de retorno.
    def marcar_ciclo(self, ciclo):
        for posicao in range(len(ciclo) - 1):
            origem = ciclo[posicao]
            destino = ciclo[posicao + 1]
            situacao = "arvore"
            if posicao == len(ciclo) - 2:
                situacao = "retorno"
            indice = self.achar_aresta(origem, destino, [situacao])
            self.arestas_marcadas.append(indice)
            if origem not in self.vertices_marcados:
                self.vertices_marcados.append(origem)

    # A fila de prioridade como aparece na tela: ordenada pela prioridade (a menor em cima),
    # e nos empates quem entrou primeiro (o sort do Python é estável).
    def fila_por_prioridade(self):
        ordenada = list(self.fila)
        ordenada.sort(key=self.prioridade_de)
        return ordenada

    def prioridade_de(self, vertice):
        return self.prioridade[vertice]
