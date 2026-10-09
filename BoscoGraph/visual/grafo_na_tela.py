# O desenho do grafo num Canvas: vértices, arestas, nomes, pesos e o que cada passo destaca.
#
# Todas as partes da tela usam este mesmo desenho (Vértices, Arestas, Pesos, Matrizes, Passo a passo...).
# O que muda de uma parte para outra são as "opções" de cada desenho:
#   algoritmo  -> qual busca (para o rótulo ao lado de cada vértice: d/f, d, h, g+h, p=...)
#   destino    -> o vértice de chegada (ganha um anel tracejado)
#   arrumacao  -> "circulo" (o normal) ou "arquivo" (as posições do desenho importado)
#   nomes, pesos -> se o nome e o peso das arestas aparecem
#   neutro     -> True nas partes do grafo: os vértices ficam brancos, sem as cores da busca
#   selecao    -> o que a pessoa escolheu na parte: {"vertices": [...], "arestas": [...], "cor": "#..."};
#                 o escolhido fica na cor da parte e o resto fica mais apagado, para chamar a atenção
#   informacao -> o texto do canto de cima (qual grafo é, a origem...)
#   informacao_final -> o texto mais comprido que o canto vai ter (reserva o espaço uma vez só,
#                       para o desenho não pular quando o texto cresce)
#   vazio      -> se não houver estado: o texto que aparece no meio
#   tamanho    -> (largura, altura) do desenho; sem ele, o tamanho do Canvas na tela. A exportação usa
#                 para desenhar num Canvas que nem aparece (a imagem e o PDF têm tamanho fixo).
# A geometria (onde fica cada vértice) só é recalculada quando o tamanho, o zoom ou a arrumação mudam.
#
# Cada vértice e cada aresta desenhados levam uma "etiqueta" (tag) do Tkinter com o número dele
# ("v3", "a12"): assim, um clique no desenho diz qual vértice ou aresta foi clicado (item_em).
# O texto escrito na aresta (nome e peso) leva também a etiqueta "rotulo": o duplo clique em cima do
# peso muda o peso, e no resto renomeia (item_para_editar).

from tkinter import font as tkfont

import algoritmos
from entrada import formatar_numero
from visual import desenho
from visual import perfis
from visual.tema import CORES_DOS_CONJUNTOS

# Espessura de cada situação de aresta (multiplica a espessura base, que depende do tamanho do desenho)
ESPESSURA_DA_ARESTA = {
    "objeto": 1,
    "grafo": 1.2,
    "arvore": 2.4,
    "arvore_tras": 2.4,
    "retorno": 1.8,
    "avanco": 1.8,
    "cruzamento": 1.8,
    "examinada": 1.5,
    "candidata": 2.2,
}

# O tracejado de cada situação (as outras são linhas cheias): a aresta criada que ainda não entrou no grafo
# e a ligação provisória do Prim (a melhor conhecida, que ainda pode mudar)
TRACEJADO_DA_ARESTA = {"objeto": (5, 4), "candidata": (8, 4)}


class DesenhoDoGrafo:
    def __init__(self, canvas, app):
        self.canvas = canvas
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.fonte_do_vertice = tkfont.Font(root=app.raiz, family="Segoe UI", size=-12, weight="bold")
        self.fonte_do_nome_da_aresta = tkfont.Font(root=app.raiz, family="Segoe UI", size=-11)
        self.vertices = []
        self.arestas = []
        self.pares = []
        self.direcionado = True
        self.posicoes_originais = None
        self.medidas_para = None
        self.nomes_por_fora = False
        self.ultimo = None              # o último (estado, opções) desenhado: a exportação redesenha igual
        self.inicio_do_peso = {}        # {número da aresta: x onde o peso começa no texto dela}

    # O grafo que vai ser desenhado (chamado de novo quando o grafo muda)
    def configurar(self, vertices, arestas, direcionado, posicoes=None):
        self.vertices = list(vertices)
        self.arestas = list(arestas)
        self.direcionado = direcionado
        self.pares = []
        for origem, destino, nome, peso in self.arestas:
            self.pares.append((origem, destino))
        # "Como no arquivo" só existe se todos os vértices tiverem posição
        self.posicoes_originais = None
        if posicoes and self.vertices:
            completas = True
            for vertice in self.vertices:
                if vertice not in posicoes:
                    completas = False
            if completas:
                self.posicoes_originais = dict(posicoes)
        self.medidas_para = None

    def tem_posicoes_do_arquivo(self):
        return self.posicoes_originais is not None

    # ------------------------------------------------------------------
    # Geometria
    # ------------------------------------------------------------------

    # A arrumação deste momento: a linha da ordem topológica tem prioridade; senão, a escolhida
    def arrumacao_do_momento(self, estado, opcoes):
        if estado is not None and estado.layout == "linha":
            return "linha"
        if self.posicoes_originais is not None and opcoes.get("arrumacao") == "arquivo":
            return "arquivo"
        return "circulo"

    # Recalcula posições e tamanhos para o tamanho atual do desenho
    def calcular_geometria(self, largura, altura, arrumacao, estado, faixa_de_cima):
        # Nomes compridos pedem vértices maiores: o raio que o nome mais largo precisa para caber
        # no círculo com uma fonte confortável (14 pixels, vezes o zoom)
        self.fonte_do_vertice.configure(size=-round(14 * self.app.zoom))
        maior_largura = 0
        for nome in self.vertices:
            maior_largura = max(maior_largura, self.fonte_do_vertice.measure(nome))
        raio_para_os_nomes = maior_largura / (2 * 0.84) + 2

        if arrumacao == "linha":
            ordem = estado.ordem_topologica
            self.medidas = desenho.medidas_da_linha(len(ordem), largura, altura - faixa_de_cima, self.app.zoom,
                                                    raio_para_os_nomes)
            self.posicoes = desenho.posicoes_em_linha(ordem, largura, self.medidas, faixa_de_cima)
            self.pontos_das_arestas = desenho.pontos_em_arco(self.pares, self.posicoes, self.medidas["raio_vertice"],
                                                             self.medidas["espaco_acima"])
        elif arrumacao == "arquivo":
            self.medidas = desenho.medidas_livres(self.vertices, self.posicoes_originais, largura,
                                                  altura - faixa_de_cima, self.app.zoom, raio_para_os_nomes)
            self.posicoes = desenho.posicoes_livres(self.vertices, self.posicoes_originais, self.medidas,
                                                    faixa_de_cima)
            self.medidas["centro"] = desenho.centro_das_posicoes(self.posicoes)
            self.pontos_das_arestas = desenho.pontos_de_todas_as_arestas(
                self.pares, self.posicoes, self.vertices, self.medidas["centro"], self.medidas["raio_vertice"],
                curvar_cordas=False)
        else:
            self.medidas = desenho.calcular_medidas(len(self.vertices), largura, altura - faixa_de_cima,
                                                    self.app.zoom, raio_para_os_nomes)
            centro_x, centro_y = self.medidas["centro"]
            self.medidas["centro"] = (centro_x, centro_y + faixa_de_cima)
            self.posicoes = desenho.posicoes_em_circulo(self.vertices, self.medidas["centro"],
                                                        self.medidas["raio_circulo"])
            self.pontos_das_arestas = desenho.pontos_de_todas_as_arestas(
                self.pares, self.posicoes, self.vertices, self.medidas["centro"], self.medidas["raio_vertice"])
        self.pontos_dos_nomes = []
        for pontos in self.pontos_das_arestas:
            self.pontos_dos_nomes.append(desenho.ponto_do_nome_da_aresta(pontos, self.medidas["raio_vertice"] * 0.45))
        self.ajustar_fontes(arrumacao)

    # O nome do vértice precisa caber dentro do círculo: se não couber, a fonte diminui; se nem com
    # letra pequena couber (nomes longos em vértices pequenos, como num mapa), o nome vai para fora,
    # embaixo do vértice (menos na linha da ordem topológica, em que embaixo ficam os tempos d/f)
    def ajustar_fontes(self, arrumacao):
        raio = self.medidas["raio_vertice"]
        tamanho = -self.medidas["fonte_vertice"]
        self.fonte_do_vertice.configure(size=-tamanho)
        largura_disponivel = 2 * raio * 0.84
        maior_largura = 1
        for nome in self.vertices:
            maior_largura = max(maior_largura, self.fonte_do_vertice.measure(nome))
        self.nomes_por_fora = False
        if maior_largura > largura_disponivel:
            necessario = int(tamanho * largura_disponivel / maior_largura)
            if necessario < 9 and arrumacao != "linha":
                self.nomes_por_fora = True
                self.fonte_do_vertice.configure(size=-round(desenho.limitar(raio * 0.9, 10, 13)))
            else:
                self.fonte_do_vertice.configure(size=-max(8, necessario))
        self.fonte_do_nome_da_aresta.configure(size=-round(desenho.limitar(raio * 0.55, 9, 15)))

    # A altura da faixa de cima, onde vai o texto de informação (quantas linhas ele ocupa)
    def altura_da_faixa(self, texto, largura):
        if not texto:
            return 6
        linhas = 1 + int(self.fontes["pequena"].measure(texto) // max(1, largura - 20))
        return linhas * self.fontes["pequena"].metrics("linespace") + 12

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------

    def desenhar(self, estado, opcoes):
        tema = self.tema
        c = self.canvas
        c.delete("all")
        self.ultimo = (estado, dict(opcoes))
        if opcoes.get("tamanho"):
            largura, altura = opcoes["tamanho"]
        else:
            largura = c.winfo_width()
            altura = c.winfo_height()
        if largura < 60 or altura < 60:
            return              # o Canvas ainda não apareceu na tela
        if estado is None or not self.vertices:
            texto = opcoes.get("vazio") or "O grafo vai aparecer aqui"
            if not self.vertices:
                texto = "O grafo não tem vértices"
            c.create_text(largura / 2, altura / 2, justify="center", fill=tema["texto_suave"],
                          font=self.fontes["mensagem"], text=texto, width=largura - 40)
            return
        arrumacao = self.arrumacao_do_momento(estado, opcoes)
        faixa = self.altura_da_faixa(opcoes.get("informacao_final") or opcoes.get("informacao"), largura)
        chave = (largura, altura, self.app.zoom, arrumacao, faixa, tuple(estado.ordem_topologica))
        if self.medidas_para != chave:
            self.calcular_geometria(largura, altura, arrumacao, estado, faixa)
            self.medidas_para = chave

        if opcoes.get("informacao"):
            c.create_text(10, 8, anchor="nw", text=opcoes["informacao"], width=largura - 20,
                          fill=tema["texto_suave"], font=self.fontes["pequena"])

        selecao = opcoes.get("selecao") or {}
        vertices_escolhidos = set(selecao.get("vertices", []))
        arestas_escolhidas = set(selecao.get("arestas", []))
        cor_da_selecao = selecao.get("cor", tema["destaque"])
        tem_selecao = bool(vertices_escolhidos or arestas_escolhidas)

        self.desenhar_arestas(estado, opcoes, arestas_escolhidas, cor_da_selecao, tem_selecao)
        self.desenhar_rotulos_das_arestas(estado, opcoes, arestas_escolhidas, cor_da_selecao, tem_selecao)
        self.desenhar_vertices(estado, opcoes, vertices_escolhidos, cor_da_selecao)

    def ponta(self):
        if self.direcionado:
            return "last"
        return "none"

    def desenhar_arestas(self, estado, opcoes, escolhidas, cor_da_selecao, tem_selecao):
        tema = self.tema
        c = self.canvas
        medidas = self.medidas
        neutro = opcoes.get("neutro", False)
        for indice in range(len(self.arestas)):
            situacao = estado.situacao_aresta[indice]
            if situacao == "invisivel":
                continue
            if neutro and situacao not in ("objeto",):
                situacao = "grafo"
            cor = tema["aresta_" + situacao]
            espessura = medidas["espessura"] * ESPESSURA_DA_ARESTA[situacao]
            tracejado = TRACEJADO_DA_ARESTA.get(situacao)
            if not neutro:
                if indice == estado.aresta_em_destaque:
                    cor = tema["destaque"]
                    espessura = espessura + 2
                if indice in estado.arestas_marcadas:
                    cor = tema["destaque"]
                    espessura = espessura + 2.5
            if indice in escolhidas:
                cor = cor_da_selecao
                espessura = medidas["espessura"] * 2.6 + 1.5
            elif tem_selecao and neutro:
                cor = tema["aresta_objeto"]          # o que não foi escolhido fica mais apagado
            c.create_line(self.pontos_das_arestas[indice], smooth=True, arrow=self.ponta(),
                          arrowshape=medidas["ponta_da_seta"], fill=cor, width=espessura, dash=tracejado,
                          tags=("aresta", f"a{indice}"))

    # O texto de uma aresta no desenho: o nome, o peso ou os dois ("e1 = 5")
    def rotulo_da_aresta(self, indice, opcoes):
        origem, destino, nome, peso = self.arestas[indice]
        partes = []
        if nome != "" and opcoes.get("nomes", True):
            partes.append(nome)
        if peso is not None and opcoes.get("pesos", True):
            partes.append(formatar_numero(peso))
        return " = ".join(partes)

    # O rótulo de cada aresta no meio da curva, na cor da aresta, com um fundo da cor do desenho por
    # trás (para o texto não se misturar com as linhas)
    def desenhar_rotulos_das_arestas(self, estado, opcoes, escolhidas, cor_da_selecao, tem_selecao):
        tema = self.tema
        c = self.canvas
        neutro = opcoes.get("neutro", False)
        fonte = self.fonte_do_nome_da_aresta
        if opcoes.get("pesos_em_destaque"):
            fonte = (self.fonte_do_nome_da_aresta.cget("family"), self.fonte_do_nome_da_aresta.cget("size"), "bold")
        self.inicio_do_peso = {}
        for indice in range(len(self.arestas)):
            texto = self.rotulo_da_aresta(indice, opcoes)
            situacao = estado.situacao_aresta[indice]
            if texto == "" or situacao == "invisivel":
                continue
            if neutro and situacao != "objeto":
                situacao = "grafo"
            cor = tema["aresta_" + situacao]
            if not neutro and (indice == estado.aresta_em_destaque or indice in estado.arestas_marcadas):
                cor = tema["destaque"]
            if indice in escolhidas:
                cor = cor_da_selecao
            elif tem_selecao and neutro:
                cor = tema["texto_suave"]
            x, y = self.pontos_dos_nomes[indice]
            item = c.create_text(x, y, text=texto, fill=cor, font=fonte, tags=("aresta", f"a{indice}", "rotulo"))
            esquerda, cima, direita, baixo = c.bbox(item)
            fundo = c.create_rectangle(esquerda - 2, cima, direita + 2, baixo, fill=tema["canvas"], outline="",
                                       tags=("aresta", f"a{indice}", "rotulo"))
            c.tag_lower(fundo, item)
            # Onde o peso começa no texto ("e1 = 5": depois do "e1 = "), para o duplo clique saber se
            # foi em cima do nome ou do peso
            peso = self.arestas[indice][3]
            if peso is not None and opcoes.get("pesos", True):
                antes_do_peso = texto[:len(texto) - len(formatar_numero(peso))]
                largura_antes = int(c.tk.call("font", "measure", fonte, antes_do_peso)) if antes_do_peso else 0
                self.inicio_do_peso[indice] = esquerda + largura_antes

    # As cores de preenchimento e do texto de um vértice (na bidirecional, o lado muda o tom; no Kruskal,
    # cada conjunto com 2 ou mais vértices tem a sua cor)
    def cores_do_vertice(self, estado, nome, opcoes):
        tema = self.tema
        cor = estado.cor.get(nome)
        if opcoes.get("neutro"):
            return tema["vertice_branco"], tema["texto_vertice_branco"]
        if cor is None:
            return None, None
        numero = estado.numero_da_cor_do_conjunto(nome)
        if numero is not None:
            return tema[f"conjunto_{numero % CORES_DOS_CONJUNTOS}"], tema["texto_conjunto"]
        lado = estado.lado.get(nome)
        if lado in ("frente", "tras") and cor != "Branco":
            chave = "lado_" + lado + ("_preto" if cor == "Preto" else "")
            texto = tema["texto_lado_preto"] if cor == "Preto" else tema["texto_vertice_branco"]
            return tema[chave], texto
        return tema["vertice_" + cor.lower()], tema["texto_vertice_" + cor.lower()]

    def desenhar_vertices(self, estado, opcoes, escolhidos, cor_da_selecao):
        tema = self.tema
        c = self.canvas
        medidas = self.medidas
        neutro = opcoes.get("neutro", False)
        algoritmo = opcoes.get("algoritmo", algoritmos.PROFUNDIDADE)
        destino = opcoes.get("destino")
        raio = medidas["raio_vertice"]
        fonte_rotulo = ("Segoe UI", medidas["fonte_rotulo"], "bold")
        for indice in range(len(self.vertices)):
            nome = self.vertices[indice]
            if nome not in estado.vertices_criados:
                continue
            x, y = self.posicoes[nome]
            etiquetas = ("vertice", f"v{indice}")
            if not neutro:
                # Raiz da busca (ou a origem): um anel fino a mais em volta
                if nome in estado.raizes:
                    c.create_oval(x - raio - 4, y - raio - 4, x + raio + 4, y + raio + 4,
                                  outline=tema["contorno_vertice"], width=1.5, tags=etiquetas)
                # Destino: um anel tracejado na cor de acento
                if nome == destino:
                    c.create_oval(x - raio - 5, y - raio - 5, x + raio + 5, y + raio + 5,
                                  outline=tema["acento"], width=2.5, dash=(5, 3), tags=etiquetas)
                # Cortado pelo limite (busca limitada): um anel pontilhado vermelho
                if nome in estado.cortados:
                    c.create_oval(x - raio - 9, y - raio - 9, x + raio + 9, y + raio + 9,
                                  outline=tema["cortado"], width=2, dash=(2, 3), tags=etiquetas)
            preenchimento, cor_do_texto = self.cores_do_vertice(estado, nome, opcoes)
            if preenchimento is None:
                # Ainda sem cor (a busca não começou): só o contorno tracejado
                c.create_oval(x - raio, y - raio, x + raio, y + raio, fill=tema["canvas"],
                              outline=tema["contorno_sem_cor"], width=2, dash=(4, 3), tags=etiquetas)
                cor_do_texto = tema["texto_sem_cor"]
            else:
                c.create_oval(x - raio, y - raio, x + raio, y + raio, fill=preenchimento,
                              outline=tema["contorno_vertice"], width=2, tags=etiquetas)
            # O que acabou de mudar (ou o que o resultado aponta) ganha um anel laranja por fora
            if not neutro and (nome == estado.vertice_em_destaque or nome in estado.vertices_marcados):
                folga = 7
                c.create_oval(x - raio - folga, y - raio - folga, x + raio + folga, y + raio + folga,
                              outline=tema["destaque"], width=3, tags=etiquetas)
            # O escolhido na parte: um anel grosso na cor da parte
            if nome in escolhidos:
                folga = 6
                c.create_oval(x - raio - folga, y - raio - folga, x + raio + folga, y + raio + folga,
                              outline=cor_da_selecao, width=4, tags=etiquetas)
            if self.nomes_por_fora:
                c.create_text(x, y + raio + 3, text=nome, anchor="n", fill=tema["texto"], font=self.fonte_do_vertice,
                              tags=etiquetas)
            else:
                c.create_text(x, y, text=nome, fill=cor_do_texto, font=self.fonte_do_vertice, tags=etiquetas)
            if neutro:
                texto = opcoes.get("rotulos", {}).get(nome, "")
            else:
                texto = perfis.rotulo_do_vertice(algoritmo, estado, nome)
            if texto and raio >= 10:
                if estado.layout == "linha":
                    x_rotulo, y_rotulo, ancora = x, y + raio + 6, "n"
                else:
                    giro = 0
                    if (nome, nome) in self.pares:
                        giro = desenho.GIRO_DO_ROTULO_COM_LACO
                    x_rotulo, y_rotulo, ancora = desenho.rotulo_do_vertice((x, y), medidas["centro"], raio + 9, giro)
                cor_do_rotulo = tema["rotulo"]
                lado = estado.lado.get(nome)
                if not neutro and lado in ("frente", "tras"):
                    cor_do_rotulo = tema["lado_" + lado + "_preto"]
                c.create_text(x_rotulo, y_rotulo, text=texto, anchor=ancora, font=fonte_rotulo, fill=cor_do_rotulo,
                              tags=etiquetas)

    # Qual vértice ou aresta está no ponto (x, y) do Canvas: ("vertice", nome), ("aresta", número) ou None.
    # O vértice ganha da aresta (ele fica por cima).
    def item_em(self, x, y):
        itens = self.canvas.find_overlapping(x - 3, y - 3, x + 3, y + 3)
        aresta = None
        for item in reversed(itens):
            for etiqueta in self.canvas.gettags(item):
                if etiqueta.startswith("v") and etiqueta[1:].isdigit():
                    return ("vertice", self.vertices[int(etiqueta[1:])])
                if etiqueta.startswith("a") and etiqueta[1:].isdigit() and aresta is None:
                    aresta = ("aresta", int(etiqueta[1:]))
        return aresta

    # O mesmo, para o duplo clique (editar): separa o PESO do resto da aresta. Em cima do peso escrito
    # na aresta devolve ("peso", número); no nome da aresta ou na linha, ("aresta", número).
    # No rótulo "e1 = 5", o "e1 = " é o nome e o "5" é o peso.
    def item_para_editar(self, x, y):
        item = self.item_em(x, y)
        if item is None or item[0] != "aresta":
            return item
        numero = item[1]
        inicio = self.inicio_do_peso.get(numero)
        if inicio is None or x < inicio - 1:
            return item
        for encontrado in self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1):
            etiquetas = self.canvas.gettags(encontrado)
            if "rotulo" in etiquetas and f"a{numero}" in etiquetas:
                return ("peso", numero)
        return item
