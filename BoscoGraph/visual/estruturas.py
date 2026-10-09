# O painel da estrutura que guia a busca, desenhado num Canvas:
#   pilha       -> DFS (os vértices Cinza) e busca limitada/iterativa (o caminho atual, com o limite)
#   fila        -> BFS: a frente da fila em cima
#   prioridade  -> Dijkstra, gulosa e A*: a menor prioridade em cima
#   rodadas     -> Bellman-Ford: a rodada e a lista de arestas, com a aresta de agora em destaque
#   duas_filas  -> bidirecional: a fila da frente e a de trás, lado a lado
#   conjuntos   -> Kruskal: as arestas da mais leve para a mais pesada (✓ aceita, ✗ recusada, a de agora em
#                  destaque) e, embaixo, os conjuntos disjuntos, cada um com a cor dele no desenho
# (o Floyd-Warshall usa uma matriz: visual/matrizes.py)

import algoritmos
from entrada import contar, formatar_numero
from visual.tema import CORES_DOS_CONJUNTOS


class DesenhoDaEstrutura:
    def __init__(self, canvas, app, algoritmo, perfil, arestas, direcionado):
        self.canvas = canvas
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.algoritmo = algoritmo
        self.perfil = perfil
        self.arestas = arestas
        self.direcionado = direcionado

    def desenhar(self, estado):
        c = self.canvas
        c.delete("all")
        largura = c.winfo_width()
        altura = c.winfo_height()
        if largura < 30 or altura < 30 or estado is None:
            return
        tipo = self.perfil["estrutura"]
        if tipo == "pilha":
            self.desenhar_pilha(estado, largura, altura)
        elif tipo == "rodadas":
            self.desenhar_rodadas(estado, largura, altura)
        elif tipo == "conjuntos":
            self.desenhar_conjuntos(estado, largura, altura)
        elif tipo == "duas_filas":
            meio = largura / 2
            self.desenhar_fila(estado, estado.fila, 0, meio - 3, altura, "frente",
                               estado.distancia, "lado_frente_preto")
            self.desenhar_fila(estado, estado.fila_tras, meio + 3, largura, altura, "trás",
                               estado.distancia_tras, "lado_tras_preto")
            c.create_line(meio, 4, meio, altura - 4, fill=self.tema["borda"])
        else:
            if self.perfil["estrutura"] == "prioridade":
                itens = estado.fila_por_prioridade()
            else:
                itens = list(estado.fila)
            self.desenhar_fila(estado, itens, 0, largura, altura, None, estado.distancia, None)

    # Texto centralizado quando a estrutura está vazia
    def vazia(self, x0, x1, altura, comecou):
        texto = "(vazia)" if comecou else "(começa na\nbusca)"
        self.canvas.create_text((x0 + x1) / 2, altura / 2, text=texto, fill=self.tema["texto_suave"],
                                font=self.fontes["pequena"], justify="center")

    # A pilha como caixas empilhadas: a base embaixo e o topo em cima
    def desenhar_pilha(self, estado, largura, altura):
        tema = self.tema
        c = self.canvas
        fonte = self.fontes["pequena"]
        pilha = estado.pilha
        limitada = self.algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA)
        topo_livre = 18
        if limitada and estado.limite_atual is not None:
            texto = f"limite {estado.limite_atual}"
            if self.algoritmo == algoritmos.ITERATIVA:
                texto = f"rodada {estado.iteracao} · limite {estado.limite_atual}"
            c.create_text(largura / 2, 4, anchor="n", text=texto, fill=tema["texto"], font=self.fontes["negrito"])
            topo_livre = fonte.metrics("linespace") + 24
        if not pilha:
            comecou = estado.tempo is not None or (limitada and estado.limite_atual is not None)
            self.vazia(0, largura, altura, comecou)
            return
        altura_da_caixa = min(30, (altura - topo_livre - 6) / len(pilha))
        mostrar_texto = altura_da_caixa >= 12

        # O texto de cada caixa: "B   d=2" na DFS, "B   p=2" na limitada (sai o número se não couber)
        def texto_da_caixa(vertice):
            if limitada:
                return f"{vertice}   p={estado.profundidade.get(vertice, '?')}"
            return f"{vertice}   d={estado.d.get(vertice, '?')}"

        mostrar_numero = True
        for vertice in pilha:
            if fonte.measure(texto_da_caixa(vertice)) > largura - 14:
                mostrar_numero = False
        for i in range(len(pilha)):
            vertice = pilha[i]
            baixo = altura - 4 - i * altura_da_caixa
            cima = baixo - altura_da_caixa + 2
            c.create_rectangle(6, cima, largura - 6, baixo, fill=tema["pilha_caixa"], outline=tema["contorno_vertice"],
                               width=1)
            if mostrar_texto:
                texto = texto_da_caixa(vertice) if mostrar_numero else vertice
                c.create_text(largura / 2, (cima + baixo) / 2, text=texto, fill=tema["pilha_texto"], font=fonte)
        topo = altura - 4 - (len(pilha) - 1) * altura_da_caixa - altura_da_caixa + 2
        c.create_rectangle(6, topo, largura - 6, topo + altura_da_caixa - 2, outline=tema["destaque"], width=2)
        c.create_text(largura / 2, topo - 8, text="topo", fill=tema["destaque"], font=fonte)

    # Uma fila de cima para baixo (em cima, quem sai primeiro), entre x0 e x1.
    #   titulo_do_lado -> na bidirecional, "frente" ou "trás" (None nas outras buscas)
    #   distancias     -> o dicionário de onde vem o número de cada caixa
    def desenhar_fila(self, estado, itens, x0, x1, altura, titulo_do_lado, distancias, cor_do_lado):
        tema = self.tema
        c = self.canvas
        fonte = self.fontes["pequena"]
        largura = x1 - x0
        por_prioridade = self.perfil["estrutura"] == "prioridade"
        chave = "d"
        if self.algoritmo == algoritmos.GULOSA:
            chave = "h"
        elif self.algoritmo == algoritmos.A_ESTRELA:
            chave = "f"
        elif self.algoritmo == algoritmos.PRIM:
            chave = "chave"
        espaco_do_titulo = fonte.metrics("linespace") + 6
        titulo = "frente: sai primeiro"
        if por_prioridade:
            titulo = f"menor {chave}: sai primeiro"
        if titulo_do_lado is not None:
            titulo = f"fila {'da frente' if titulo_do_lado == 'frente' else 'de trás'}"
        if fonte.measure(titulo) > largura - 8:
            titulo = "sai primeiro" if titulo_do_lado is None else titulo_do_lado
        cor_do_titulo = tema[cor_do_lado] if cor_do_lado else tema["destaque"]
        c.create_text(x0 + largura / 2, 4, text=titulo, anchor="n", fill=cor_do_titulo, font=fonte)
        if not itens:
            comecou = bool(estado.distancia) or bool(estado.distancia_tras)
            self.vazia(x0, x1, altura, comecou)
            return
        altura_da_caixa = min(30, max(14, (altura - espaco_do_titulo - 6) / len(itens)))
        cabem = max(1, int((altura - espaco_do_titulo - 6) // altura_da_caixa))
        sobrando = 0
        if len(itens) > cabem:
            sobrando = len(itens) - (cabem - 1)       # a última caixa vira "+N"
            itens = itens[:cabem - 1]
        textos = []
        cabe_valor = True
        for vertice in itens:
            if por_prioridade:
                valor = formatar_numero(estado.prioridade.get(vertice))
            else:
                valor = formatar_numero(distancias.get(vertice))
            texto = f"{vertice}   {chave}={valor}"
            if fonte.measure(texto) > largura - 14:
                texto = f"{vertice}  {valor}"
            textos.append(texto)
            if fonte.measure(texto) > largura - 14:
                cabe_valor = False
        for i in range(len(itens)):
            cima = espaco_do_titulo + i * altura_da_caixa
            baixo = cima + altura_da_caixa - 2
            preenchimento = tema["pilha_caixa"]
            if titulo_do_lado is not None:
                preenchimento = tema["lado_frente"] if titulo_do_lado == "frente" else tema["lado_tras"]
            c.create_rectangle(x0 + 6, cima, x1 - 6, baixo, fill=preenchimento, outline=tema["contorno_vertice"],
                               width=1)
            texto = textos[i] if cabe_valor else itens[i]
            c.create_text(x0 + largura / 2, (cima + baixo) / 2, text=texto, fill=tema["pilha_texto"], font=fonte)
            if i == 0:
                c.create_rectangle(x0 + 6, cima, x1 - 6, baixo, outline=tema["destaque"], width=2)
        if sobrando:
            cima = espaco_do_titulo + len(itens) * altura_da_caixa
            c.create_text(x0 + largura / 2, cima + altura_da_caixa / 2, text=f"+{sobrando}", fill=tema["texto_suave"],
                          font=fonte)

    # Bellman-Ford: a rodada atual e a lista de arestas na ordem em que cada rodada as relaxa
    def desenhar_rodadas(self, estado, largura, altura):
        tema = self.tema
        c = self.canvas
        fonte = self.fontes["pequena"]
        if estado.rodada is None:
            self.vazia(0, largura, altura, False)
            return
        linha = fonte.metrics("linespace") + 4
        c.create_text(largura / 2, 4, anchor="n", font=self.fontes["negrito"], fill=tema["texto"],
                      text=f"Rodada {estado.rodada} de {estado.total_de_rodadas}")
        c.create_text(largura / 2, 4 + linha + 2, anchor="n", font=fonte, fill=tema["texto_suave"],
                      text=contar(len(estado.melhoras_na_rodada), "melhora", "melhoras") + " nesta rodada")
        arcos = []
        for numero in range(len(self.arestas)):
            origem, destino, nome, peso = self.arestas[numero]
            arcos.append((numero, origem, destino, peso))
            if not self.direcionado and origem != destino:
                arcos.append((numero, destino, origem, peso))
        topo = 4 + 2 * linha + 8
        cabem = max(1, int((altura - topo) // linha))
        posicao_atual = 0
        for i in range(len(arcos)):
            numero, origem, destino, peso = arcos[i]
            if estado.arco_atual == (numero, origem, destino):
                posicao_atual = i
        comeco = max(0, min(posicao_atual - cabem // 2, len(arcos) - cabem))
        seta = "→" if self.direcionado else "—"
        for i in range(comeco, min(len(arcos), comeco + cabem)):
            numero, origem, destino, peso = arcos[i]
            y = topo + (i - comeco) * linha
            if estado.arco_atual == (numero, origem, destino):
                c.create_rectangle(4, y - 1, largura - 4, y + linha - 3, fill=tema["fundo_destaque"], outline="")
            cor = tema["texto"]
            if numero in estado.melhoras_na_rodada:
                cor = tema["aresta_arvore"]
            c.create_text(10, y, anchor="nw", font=fonte, fill=cor,
                          text=f"{origem} {seta} {destino}   ({formatar_numero(peso)})")

    # Kruskal: em cima, as arestas em ordem de peso; embaixo, os conjuntos (cada um com a cor do desenho)
    def desenhar_conjuntos(self, estado, largura, altura):
        tema = self.tema
        c = self.canvas
        fonte = self.fontes["pequena"]
        linha = fonte.metrics("linespace") + 4
        if not estado.conjunto:
            self.vazia(0, largura, altura, False)
            return

        # Os conjuntos primeiro (de baixo para cima): quantas fileiras de "pílulas" eles ocupam
        pilulas = []
        for representante, membros in estado.conjuntos():
            texto = " ".join(membros)
            numero = estado.cor_do_conjunto.get(representante) if len(membros) > 1 else None
            pilulas.append((texto, numero, fonte.measure(texto) + 14))
        altura_da_pilula = linha + 2
        fileiras = [[]]
        ocupado = 6
        for pilula in pilulas:
            if fileiras[-1] and ocupado + pilula[2] > largura - 6:
                fileiras.append([])
                ocupado = 6
            fileiras[-1].append(pilula)
            ocupado += pilula[2] + 6
        cabem = max(1, int((altura * 0.45 - linha - 8) // (altura_da_pilula + 4)))
        if len(fileiras) > cabem:
            fileiras = fileiras[:cabem]
        topo_dos_conjuntos = altura - 4 - len(fileiras) * (altura_da_pilula + 4) - linha - 2
        c.create_line(4, topo_dos_conjuntos - 4, largura - 4, topo_dos_conjuntos - 4, fill=tema["borda"])
        quantos = len(pilulas)
        c.create_text(largura / 2, topo_dos_conjuntos, anchor="n", font=fonte, fill=tema["texto_suave"],
                      text=contar(quantos, "conjunto", "conjuntos"))
        y = topo_dos_conjuntos + linha + 2
        for fileira in fileiras:
            x = 6
            for texto, numero, largura_da_pilula in fileira:
                fundo = tema["superficie"] if numero is None else tema[f"conjunto_{numero % CORES_DOS_CONJUNTOS}"]
                cor_do_texto = tema["texto"] if numero is None else tema["texto_conjunto"]
                c.create_rectangle(x, y, x + largura_da_pilula, y + altura_da_pilula, fill=fundo,
                                   outline=tema["contorno_vertice"], width=1)
                c.create_text(x + largura_da_pilula / 2, y + altura_da_pilula / 2, text=texto, font=fonte,
                              fill=cor_do_texto)
                x += largura_da_pilula + 6
            y += altura_da_pilula + 4

        # As arestas em ordem de peso, com a de agora no meio da janela
        titulo = "Arestas, da mais leve para a mais pesada"
        if fonte.measure(titulo) > largura - 10:
            titulo = "Arestas por peso"
        c.create_text(largura / 2, 4, anchor="n", font=self.fontes["negrito"], fill=tema["texto"], text=titulo)
        resumo = (contar(len(estado.arvore_minima), "aresta", "arestas") + " na árvore · peso "
                  + formatar_numero(estado.peso_da_arvore))
        c.create_text(largura / 2, 4 + linha + 2, anchor="n", font=fonte, fill=tema["texto_suave"], text=resumo)
        topo = 4 + 2 * linha + 8
        espaco = topo_dos_conjuntos - 10 - topo
        if not estado.ordem_das_arestas:
            c.create_text(largura / 2, topo + max(0, espaco) / 2, text="(a lista ordenada vem depois\ndos conjuntos)",
                          fill=tema["texto_suave"], font=fonte, justify="center")
            return
        cabem = max(1, int(espaco // linha))
        ordem = estado.ordem_das_arestas
        posicao_atual = 0
        if estado.aresta_atual in ordem:
            posicao_atual = ordem.index(estado.aresta_atual)
        comeco = max(0, min(posicao_atual - cabem // 2, len(ordem) - cabem))
        for i in range(comeco, min(len(ordem), comeco + cabem)):
            numero = ordem[i]
            origem, destino, nome, peso = self.arestas[numero]
            y = topo + (i - comeco) * linha
            if numero == estado.aresta_atual:
                c.create_rectangle(4, y - 1, largura - 4, y + linha - 3, fill=tema["fundo_destaque"], outline="")
            decisao = estado.decisao.get(numero)
            marca = ""
            cor = tema["texto"]
            if decisao == "aceita":
                marca = "✓"
                cor = tema["aresta_arvore"]
                c.create_text(10, y, anchor="nw", font=fonte, fill=tema["sucesso"], text=marca)
            elif decisao == "rejeitada":
                marca = "✗"
                cor = tema["texto_suave"]
                c.create_text(10, y, anchor="nw", font=fonte, fill=tema["erro"], text=marca)
            texto = f"{origem} — {destino}"
            if nome:
                texto += f"  [{nome}]"
            c.create_text(26, y, anchor="nw", font=fonte, fill=cor, text=texto)
            c.create_text(largura - 10, y, anchor="ne", font=fonte, fill=cor, text=formatar_numero(peso))
