# A tela inicial: a primeira que aparece.
#   - em cima: o logo e o nome; à direita, o "Sobre" e a chave do tema (sol e lua);
#   - à esquerda: os TIPOS de busca (sem pesos, menor custo, com heurística, árvore geradora mínima), em
#     sanfona: clicar num tipo abre a lista dos algoritmos dele (e fecha o tipo que estava aberto);
#   - à direita: um cartão que muda com a escolha:
#       nada escolhido -> as boas-vindas e como começar;
#       um tipo aberto -> o que as buscas desse tipo têm em comum e os algoritmos dele;
#       um algoritmo   -> o que ele faz, um desenho pequeno dele no meio do caminho e os dois caminhos, em
#                         cartões grandes na cor do tipo:
#                         "Ver um exemplo pronto" (cheio) -> abre a visualização num grafo pronto que combina
#                                                            com a busca (o da prova, os do livro, a Romênia);
#                         "Montar meu grafo" (só a borda) -> abre o editor na etapa dos vértices, com essa busca;
#   - embaixo: os outros jeitos de começar, cada um com a sua cor e o seu ícone:
#       Começar do zero (verde), Importar desenho (verde-azulado), Abrir arquivo .bosco (roxo)
#       e Continuar no editor (cinza).
# Teclado: ↑ e ↓ andam pelos algoritmos do tipo aberto; Enter abre o exemplo; Ctrl+O vai para a importação.
# O tamanho das letras muda com Ctrl + roda do mouse (ou Ctrl + e Ctrl −).

import tkinter as tk
from tkinter import ttk

import algoritmos
import entrada
import modelos
from visual.botoes import Botao, CartaoDeAcao, desenhar_icone, redesenhar_componentes
from visual.cabecalho import Cabecalho
from visual.dica import Dica
from visual.editor import configuracao_da_visualizacao, valores_para_abrir
from visual.rolagem import QuadroRolavel
from visual.sobre import mostrar_sobre
from visual.tema import misturar

# Os tipos de busca (os grupos da sanfona): ficam em algoritmos.py, porque o editor também usa
GRUPOS = algoritmos.TIPOS_DE_BUSCA

ROMENIA = "Exemplo - A estrela (Romênia)"
ARVORE_MINIMA = "Exemplo - Árvore geradora mínima (CLRS 23.1)"

# O exemplo de cada busca: (modelo que vem com o programa, o que muda nele para esta busca)
EXEMPLOS = {
    algoritmos.PROFUNDIDADE: ("Prova 01", {}),
    algoritmos.LIMITADA: (ROMENIA, {"inicio": "Arad", "destino": "Bucharest", "limite": 3}),
    algoritmos.ITERATIVA: (ROMENIA, {"inicio": "Arad", "destino": "Bucharest"}),
    algoritmos.LARGURA: ("Prova 01", {}),
    algoritmos.BIDIRECIONAL: (ROMENIA, {"inicio": "Arad", "destino": "Bucharest"}),
    algoritmos.DIJKSTRA: ("Exemplo - Dijkstra (CLRS 24.6)", {}),
    algoritmos.BELLMAN_FORD: ("Exemplo - Bellman-Ford (CLRS 24.4)", {}),
    algoritmos.FLOYD_WARSHALL: ("Exemplo - Floyd-Warshall (CLRS 25.1)", {}),
    algoritmos.GULOSA: (ROMENIA, {}),
    algoritmos.A_ESTRELA: (ROMENIA, {}),
    algoritmos.PRIM: (ARVORE_MINIMA, {"inicio": "a"}),
    algoritmos.KRUSKAL: (ARVORE_MINIMA, {}),
}

# O que cada exemplo abre, em poucas palavras (aparece no cartão "Ver um exemplo pronto")
TEXTOS_DOS_EXEMPLOS = {
    "Prova 01": "O grafo da Prova 01 (16 roteadores)",
    ROMENIA: "O mapa da Romênia, de Arad até Bucharest",
    "Exemplo - Dijkstra (CLRS 24.6)": "O grafo do livro do Cormen (figura 24.6)",
    "Exemplo - Bellman-Ford (CLRS 24.4)": "O grafo do livro do Cormen (figura 24.4), com pesos negativos",
    "Exemplo - Floyd-Warshall (CLRS 25.1)": "O grafo do livro do Cormen (figura 25.1)",
    ARVORE_MINIMA: "O grafo do livro do Cormen (figura 23.1), peso mínimo 37",
}

# A miniatura de cada busca: o mesmo grafo pequeno, no meio da busca, com as cores dela.
# As posições vão de 0 a 1 (a fração da largura e da altura do desenho).
POSICOES_DA_MINIATURA = {"A": (0.10, 0.50), "B": (0.37, 0.17), "C": (0.37, 0.83), "D": (0.64, 0.32),
                         "E": (0.90, 0.66)}
ARESTAS_DA_MINIATURA = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D"), ("D", "E")]
CENAS = {
    algoritmos.PROFUNDIDADE: {"cores": {"A": "Cinza", "B": "Cinza", "C": "Preto", "D": "Cinza", "E": "Branco"},
                              "arvore": [("A", "B"), ("B", "C"), ("B", "D")],
                              "rotulos": {"A": "1/", "B": "2/", "C": "3/4", "D": "5/"}},
    algoritmos.LIMITADA: {"cores": {"A": "Cinza", "B": "Cinza", "C": "Preto", "D": "Cinza", "E": "Branco"},
                          "arvore": [("A", "B"), ("B", "D")], "cortados": ["C"],
                          "rotulos": {"A": "p=0", "B": "p=1", "C": "p=2", "D": "p=2"}, "destino": "E"},
    algoritmos.ITERATIVA: {"cores": {"A": "Cinza", "B": "Preto", "C": "Cinza", "D": "Branco", "E": "Branco"},
                           "arvore": [("A", "C")], "cortados": ["B"],
                           "rotulos": {"A": "p=0", "B": "p=1", "C": "p=1"}, "destino": "E"},
    algoritmos.LARGURA: {"cores": {"A": "Preto", "B": "Cinza", "C": "Cinza", "D": "Branco", "E": "Branco"},
                         "arvore": [("A", "B"), ("A", "C")],
                         "rotulos": {"A": "0", "B": "1", "C": "1"}},
    algoritmos.BIDIRECIONAL: {"cores": {"A": "Preto", "B": "Cinza", "C": "Cinza", "D": "Cinza", "E": "Preto"},
                              "lados": {"A": "frente", "B": "frente", "C": "frente", "D": "tras", "E": "tras"},
                              "arvore": [("A", "B"), ("A", "C")], "arvore_tras": [("D", "E")],
                              "rotulos": {"A": "0", "B": "1", "C": "1", "D": "1", "E": "0"}, "destino": "E"},
    algoritmos.DIJKSTRA: {"cores": {"A": "Preto", "B": "Preto", "C": "Cinza", "D": "Cinza", "E": "Branco"},
                          "arvore": [("A", "B"), ("B", "C"), ("B", "D")],
                          "pesos": {("A", "B"): "2", ("A", "C"): "5", ("B", "C"): "1", ("B", "D"): "4",
                                    ("C", "D"): "3", ("D", "E"): "2"},
                          "rotulos": {"A": "0", "B": "2", "C": "3", "D": "6", "E": "∞"}},
    algoritmos.BELLMAN_FORD: {"cores": {"A": "Preto", "B": "Cinza", "C": "Cinza", "D": "Cinza", "E": "Branco"},
                              "arvore": [("A", "B"), ("B", "C"), ("B", "D")],
                              "pesos": {("A", "B"): "4", ("A", "C"): "2", ("B", "C"): "-3", ("B", "D"): "1",
                                        ("C", "D"): "5", ("D", "E"): "2"},
                              "rotulos": {"A": "0", "B": "4", "C": "1", "D": "5", "E": "∞"}},
    algoritmos.FLOYD_WARSHALL: {"cores": {"A": "Preto", "B": "Cinza", "C": "Branco", "D": "Branco", "E": "Branco"},
                                "arvore": [("A", "B"), ("B", "D")], "destacadas": [("A", "B"), ("B", "D")],
                                "pesos": {("A", "B"): "2", ("A", "C"): "5", ("B", "C"): "1", ("B", "D"): "4",
                                          ("C", "D"): "3", ("D", "E"): "2"},
                                "rotulos": {"B": "k"}},
    algoritmos.GULOSA: {"cores": {"A": "Preto", "B": "Preto", "C": "Cinza", "D": "Cinza", "E": "Branco"},
                        "arvore": [("A", "B"), ("B", "D")],
                        "rotulos": {"A": "h=7", "B": "h=4", "C": "h=6", "D": "h=2", "E": "h=0"},
                        "destino": "E"},
    algoritmos.A_ESTRELA: {"cores": {"A": "Preto", "B": "Preto", "C": "Cinza", "D": "Cinza", "E": "Branco"},
                           "arvore": [("A", "B"), ("B", "D")],
                           "pesos": {("A", "B"): "2", ("A", "C"): "5", ("B", "C"): "4", ("B", "D"): "4",
                                     ("C", "D"): "3", ("D", "E"): "2"},
                           "rotulos": {"A": "0+7", "B": "2+4", "C": "5+6", "D": "6+2"},
                           "destino": "E"},
    # Prim: a árvore (A, B, C) já tem duas arestas; D está na fila, ligado por C — D (tracejada)
    algoritmos.PRIM: {"cores": {"A": "Preto", "B": "Preto", "C": "Preto", "D": "Cinza", "E": "Branco"},
                      "arvore": [("A", "B"), ("B", "C")], "candidatas": [("C", "D")],
                      "examinadas": [("A", "C"), ("B", "D")],
                      "pesos": {("A", "B"): "2", ("A", "C"): "5", ("B", "C"): "1", ("B", "D"): "4",
                                ("C", "D"): "3", ("D", "E"): "2"},
                      "rotulos": {"A": "0", "B": "2", "C": "1", "D": "3", "E": "∞"}},
    # Kruskal: três arestas aceitas, dois conjuntos (cada um com a sua cor); a próxima é C — D
    algoritmos.KRUSKAL: {"cores": {"A": "Branco", "B": "Branco", "C": "Branco", "D": "Branco", "E": "Branco"},
                         "conjuntos": {"A": 0, "B": 0, "C": 0, "D": 1, "E": 1},
                         "arvore": [("A", "B"), ("B", "C"), ("D", "E")], "destacadas": [("C", "D")],
                         "pesos": {("A", "B"): "2", ("A", "C"): "5", ("B", "C"): "1", ("B", "D"): "4",
                                   ("C", "D"): "3", ("D", "E"): "2"},
                         "rotulos": {}},
}

# "Como começar", nas boas-vindas
COMO_COMECAR = ["Escolha um tipo de busca na lista ao lado",
                "Clique num algoritmo para ver o que ele faz",
                "Veja um exemplo pronto ou monte o seu grafo"]

# A sanfona: quantos quadros a animação de abrir e fechar tem, e o tempo entre eles
QUADROS_DA_SANFONA = 8
MILISSEGUNDOS_DA_SANFONA = 15


# Desenha a miniatura de uma busca num Canvas de largura x altura
def desenhar_miniatura(canvas, chave, tema, largura, altura):
    cena = CENAS[chave]
    margem = 18
    raio = max(8, min(16, altura * 0.085))
    pontos = {}
    for vertice in POSICOES_DA_MINIATURA:
        fracao_x, fracao_y = POSICOES_DA_MINIATURA[vertice]
        pontos[vertice] = (margem + fracao_x * (largura - 2 * margem), margem + fracao_y * (altura - 2 * margem))
    fonte = ("Segoe UI", -max(9, round(raio * 0.85)))
    for origem, destino in ARESTAS_DA_MINIATURA:
        cor = tema["aresta_grafo"]
        espessura = 1.2
        if (origem, destino) in cena["arvore"]:
            cor, espessura = tema["aresta_arvore"], 2.6
        if (origem, destino) in cena.get("arvore_tras", []):
            cor, espessura = tema["aresta_arvore_tras"], 2.6
        if (origem, destino) in cena.get("examinadas", []):
            cor = tema["aresta_examinada"]
        tracejado = None
        if (origem, destino) in cena.get("candidatas", []):
            cor, espessura, tracejado = tema["aresta_candidata"], 2.2, (6, 3)
        if (origem, destino) in cena.get("destacadas", []):
            cor, espessura = tema["destaque"], 3
        canvas.create_line(*pontos[origem], *pontos[destino], width=espessura, fill=cor, dash=tracejado)
        peso = cena.get("pesos", {}).get((origem, destino))
        if peso is not None:
            x = (pontos[origem][0] + pontos[destino][0]) / 2
            y = (pontos[origem][1] + pontos[destino][1]) / 2
            item = canvas.create_text(x, y, text=peso, font=fonte, fill=tema["texto_suave"])
            esquerda, cima, direita, baixo = canvas.bbox(item)
            fundo = canvas.create_rectangle(esquerda - 1, cima, direita + 1, baixo, fill=tema["superficie"],
                                            outline="")
            canvas.tag_lower(fundo, item)
    for vertice, (x, y) in pontos.items():
        cor = cena["cores"][vertice]
        preenchimento = tema["vertice_" + cor.lower()]
        lado = cena.get("lados", {}).get(vertice)
        if lado is not None:
            preenchimento = tema["lado_" + lado + ("_preto" if cor == "Preto" else "")]
        conjunto = cena.get("conjuntos", {}).get(vertice)
        if conjunto is not None:
            preenchimento = tema[f"conjunto_{conjunto}"]
        if vertice == cena.get("destino"):
            canvas.create_oval(x - raio - 4, y - raio - 4, x + raio + 4, y + raio + 4, outline=tema["acento"],
                               width=2, dash=(3, 2))
        if vertice in cena.get("cortados", []):
            canvas.create_oval(x - raio - 6, y - raio - 6, x + raio + 6, y + raio + 6, outline=tema["cortado"],
                               width=2, dash=(2, 2))
        canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=preenchimento, outline=tema["contorno_vertice"],
                           width=1.5)
        rotulo = cena["rotulos"].get(vertice)
        if rotulo:
            # O rótulo vai para fora do grafo: em cima dos vértices de cima, embaixo dos de baixo
            embaixo = POSICOES_DA_MINIATURA[vertice][1] >= 0.5
            canvas.create_text(x, y + raio + 3 if embaixo else y - raio - 3, text=rotulo,
                               anchor="n" if embaixo else "s", font=fonte, fill=tema["rotulo"])


# A miniatura desenhada no meio do Canvas, numa área de "usada" pixels de largura
def desenhar_miniatura_centralizada(canvas, chave, tema, largura, altura, usada):
    deslocamento = (largura - usada) / 2
    desenhar_miniatura(canvas, chave, tema, usada, altura)
    if deslocamento > 0:
        canvas.move("all", deslocamento, 0)


# Os fatos de uma busca, um por etiqueta: ["pilha", "não usa pesos", "precisa de destino"]
# (ficam em algoritmos.py, porque o editor também mostra)
def fatos(informacoes):
    return algoritmos.fatos(informacoes)


# O que o cartão "Ver um exemplo pronto" diz que vai abrir: "O mapa da Romênia, de Arad até Bucharest"
def explicacao_do_exemplo(chave):
    nome, extras = EXEMPLOS[chave]
    texto = TEXTOS_DOS_EXEMPLOS.get(nome, nome.replace("Exemplo - ", ""))
    if "limite" in extras:
        texto += f", limite {extras['limite']}"
    return texto


# Em qual grupo (tipo) uma busca está
def grupo_da_busca(chave):
    return algoritmos.tipo_da_busca(chave)


class TelaInicial:
    def __init__(self, app):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        # O que estava escolhido da última vez (volta igual da visualização e da troca de tema)
        self.escolhida = app.preferencias.get("busca_da_tela_inicial")
        self.grupo_aberto = app.preferencias.get("grupo_da_tela_inicial")
        if self.grupo_aberto is None and self.escolhida is not None:
            self.grupo_aberto = grupo_da_busca(self.escolhida)
        self.itens = {}                 # chave da busca -> (linha, marca, rótulo) na sanfona
        self.grupos = []                # o que cada grupo da sanfona tem na tela (veja montar_sanfona)
        self.animacao = None            # o "after" da animação da sanfona
        self.miniatura = None           # o Canvas da miniatura do cartão (quando o cartão tem uma)
        self.chave_da_miniatura = None
        self.montar()
        for indice in range(len(self.grupos)):
            self.mostrar_grupo_na_sanfona(indice, indice == self.grupo_aberto)
        self.pintar_itens()
        self.atualizar_cartao()
        teclas = {"<Control-o>": self.importar, "<Control-O>": self.importar, "<Up>": lambda evento: self.andar(-1),
                  "<Down>": lambda evento: self.andar(1), "<Return>": self.enter}
        for tecla in teclas:
            self.app.raiz.bind(tecla, teclas[tecla])

    def montar(self):
        self.quadro = ttk.Frame(self.app.raiz, padding=(24, 16, 24, 14))
        self.quadro.pack(fill="both", expand=True)
        self.quadro.columnconfigure(1, weight=1)
        self.quadro.rowconfigure(2, weight=1)
        self.cabecalho = Cabecalho(self.quadro, self.app, "BoscoGraph",
                                   "Buscas em grafos: por partes, passo a passo e linha a linha")
        self.cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew")
        Botao(self.cabecalho.botoes, self.app, "Sobre", icone="info", papel="icone", comando=lambda: mostrar_sobre(self.app),
              dica="O que é o BoscoGraph, a versão e quem fez").pack(side="left")
        titulo = ttk.Frame(self.quadro)
        titulo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(18, 10))
        ttk.Label(titulo, text="Escolha o tipo de busca que você quer estudar", font=self.fontes["mensagem"]).pack(
            side="left")
        ttk.Label(titulo, text="clique num tipo para ver os algoritmos dele", style="Suave.TLabel").pack(
            side="left", padx=(12, 0), pady=(4, 0))
        self.montar_sanfona()
        self.cartao = ttk.Frame(self.quadro, style="Painel.TFrame", padding=(22, 18, 22, 18))
        self.cartao.grid(row=2, column=1, sticky="nsew", padx=(16, 0))
        self.cartao.columnconfigure(0, weight=1)
        self.cartao.bind("<Configure>", self.ajustar_quebras_de_linha)
        self.montar_outros_jeitos()

    # ------------------------------------------------------------------
    # A sanfona dos tipos de busca
    # ------------------------------------------------------------------

    def montar_sanfona(self):
        tema = self.tema
        # A sanfona rola quando não cabe (janela baixa ou letras grandes)
        self.rolagem_da_sanfona = QuadroRolavel(self.quadro, self.app, tema["superficie"], highlightthickness=1,
                                                highlightbackground=tema["borda"])
        self.rolagem_da_sanfona.grid(row=2, column=0, sticky="nsw")
        self.sanfona = self.rolagem_da_sanfona.conteudo
        # Uma "régua" invisível deixa a sanfona com uma largura mínima (os nomes curtos não a encolhem)
        tk.Frame(self.sanfona, bg=tema["superficie"], width=round(290 * self.app.zoom), height=1).pack(fill="x")
        for indice in range(len(GRUPOS)):
            grupo = GRUPOS[indice]
            cor = tema[grupo["cor"]]
            if indice > 0:
                tk.Frame(self.sanfona, bg=tema["borda"], height=1).pack(fill="x")
            # O cabeçalho do grupo: a faixa colorida, a setinha, o título, o subtítulo e quantas buscas tem
            cabecalho = tk.Frame(self.sanfona, bg=tema["superficie"], cursor="hand2")
            cabecalho.pack(fill="x")
            faixa = tk.Frame(cabecalho, bg=cor, width=4)
            faixa.pack(side="left", fill="y")
            lado = round(self.fontes["negrito"].metrics("linespace") * 1.1)
            seta = tk.Canvas(cabecalho, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0,
                             cursor="hand2")
            seta.pack(side="left", padx=(10, 6), pady=(10, 0), anchor="n")
            textos = tk.Frame(cabecalho, bg=tema["superficie"], cursor="hand2")
            textos.pack(side="left", fill="x", expand=True, pady=(9, 9))
            rotulo_titulo = tk.Label(textos, text=grupo["titulo"], font=self.fontes["negrito"], bg=tema["superficie"],
                                     fg=tema["texto"], anchor="w", cursor="hand2")
            rotulo_titulo.pack(anchor="w")
            rotulo_subtitulo = tk.Label(textos, text=grupo["subtitulo"], font=self.fontes["pequena"],
                                        bg=tema["superficie"], fg=tema["texto_suave"], anchor="w", cursor="hand2")
            rotulo_subtitulo.pack(anchor="w")
            contador = tk.Label(cabecalho, text=str(len(grupo["buscas"])), font=self.fontes["pequena"],
                                bg=misturar(tema["superficie"], cor, 0.15), fg=cor, padx=7, cursor="hand2")
            contador.pack(side="right", padx=(6, 12))
            Dica(contador, entrada.contar(len(grupo["buscas"]), "busca", "buscas") + " deste tipo")
            componentes = (cabecalho, seta, textos, rotulo_titulo, rotulo_subtitulo, contador)
            for componente in componentes:
                componente.bind("<Button-1>", lambda evento, indice=indice: self.clicar_no_grupo(indice))
                componente.bind("<Enter>", lambda evento, indice=indice: self.pintar_cabecalho(indice, True))
                componente.bind("<Leave>", lambda evento, indice=indice: self.pintar_cabecalho(indice, False))
            # A "janela" da lista: a animação muda a altura dela, mostrando a lista aos poucos
            janela = tk.Frame(self.sanfona, bg=tema["superficie"], height=1)
            conteudo = tk.Frame(janela, bg=tema["superficie"])
            conteudo.pack(fill="x", anchor="n", pady=(0, 8))
            for chave in grupo["buscas"]:
                self.montar_item(conteudo, chave, cor)
            self.grupos.append({"cabecalho": cabecalho, "seta": seta, "fundos": (cabecalho, seta, textos, rotulo_titulo,
                                                                                 rotulo_subtitulo),
                                "titulo": rotulo_titulo, "janela": janela, "conteudo": conteudo, "aberto": False,
                                "altura": 0, "alvo": 0, "em_cima": False})
        self.rolagem_da_sanfona.ligar_roda()

    # Um algoritmo dentro do grupo: a marca (bolinha da cor do tipo) e o nome
    def montar_item(self, pai, chave, cor):
        tema = self.tema
        informacoes = algoritmos.algoritmo(chave)
        linha = tk.Frame(pai, bg=tema["superficie"], cursor="hand2")
        linha.pack(fill="x", padx=(14, 10), pady=1)
        marca = tk.Canvas(linha, width=14, height=14, bg=tema["superficie"], highlightthickness=0, cursor="hand2")
        marca.pack(side="left", padx=(14, 8))
        marca.create_oval(4, 4, 11, 11, fill=cor, outline=cor)
        rotulo = tk.Label(linha, text=informacoes["nome"], bg=tema["superficie"], fg=tema["texto"], anchor="w",
                          font=self.fontes["texto"], padx=2, pady=5, cursor="hand2")
        rotulo.pack(side="left", fill="x", expand=True)
        for componente in (linha, marca, rotulo):
            componente.bind("<Button-1>", lambda evento, chave=chave: self.escolher(chave))
            componente.bind("<Double-1>", lambda evento, chave=chave: self.ver_exemplo(chave))
            componente.bind("<Enter>", lambda evento, chave=chave: self.pintar_item(chave, True))
            componente.bind("<Leave>", lambda evento, chave=chave: self.pintar_item(chave, False))
        self.itens[chave] = (linha, marca, rotulo)

    def pintar_cabecalho(self, indice, em_cima=None):
        tema = self.tema
        grupo = self.grupos[indice]
        if em_cima is not None:
            grupo["em_cima"] = em_cima
        cor = tema[GRUPOS[indice]["cor"]]
        fundo = tema["superficie"]
        if grupo["aberto"]:
            fundo = misturar(tema["superficie"], cor, 0.10)
        elif grupo["em_cima"]:
            fundo = misturar(tema["superficie"], cor, 0.06)
        for componente in grupo["fundos"]:
            componente.configure(bg=fundo)
        grupo["titulo"].configure(fg=cor if grupo["aberto"] else tema["texto"])
        seta = grupo["seta"]
        lado = round(self.fontes["negrito"].metrics("linespace") * 1.1)      # acompanha o zoom
        seta.configure(width=lado, height=lado)
        seta.delete("all")
        desenhar_icone(seta, "chevron_baixo" if grupo["aberto"] else "chevron_direita", lado / 2, lado / 2, lado * 0.8,
                       cor if grupo["aberto"] else tema["texto_suave"], fundo)

    def pintar_item(self, chave, em_cima=False):
        tema = self.tema
        linha, marca, rotulo = self.itens[chave]
        cor = tema[GRUPOS[grupo_da_busca(chave)]["cor"]]
        escolhida = chave == self.escolhida
        fundo = tema["superficie"]
        if escolhida:
            fundo = misturar(tema["superficie"], cor, 0.16)
        elif em_cima:
            fundo = misturar(tema["superficie"], cor, 0.07)
        for componente in (linha, marca, rotulo):
            componente.configure(bg=fundo)
        rotulo.configure(font=self.fontes["negrito"] if escolhida else self.fontes["texto"],
                         fg=cor if escolhida else tema["texto"])

    def pintar_itens(self):
        for chave in self.itens:
            self.pintar_item(chave)

    # Abre ou fecha a lista de um grupo, na hora (sem animação)
    def mostrar_grupo_na_sanfona(self, indice, aberto):
        grupo = self.grupos[indice]
        grupo["aberto"] = aberto
        janela = grupo["janela"]
        if aberto:
            janela.pack_propagate(True)
            janela.pack(fill="x", after=grupo["cabecalho"])
            grupo["altura"] = grupo["alvo"] = -1        # "-1" = do tamanho natural
        else:
            janela.pack_forget()
            grupo["altura"] = grupo["alvo"] = 0
        self.pintar_cabecalho(indice)

    # O clique no cabeçalho de um grupo: abre (fechando o que estava aberto) ou fecha
    def clicar_no_grupo(self, indice):
        if self.grupo_aberto == indice:
            self.abrir_grupo(None)
        else:
            self.abrir_grupo(indice)
        self.atualizar_cartao()

    # Abre o grupo "indice" (None = fecha todos). animar=False: muda na hora (os testes e a tecla usam)
    def abrir_grupo(self, indice, animar=True):
        self.grupo_aberto = indice
        self.app.preferencias["grupo_da_tela_inicial"] = indice
        if not animar or not self.quadro.winfo_ismapped():
            self.parar_animacao()
            for outro in range(len(self.grupos)):
                self.mostrar_grupo_na_sanfona(outro, outro == indice)
            self.mostrar_grupo_aberto()
            return
        self.app.raiz.update_idletasks()
        for outro in range(len(self.grupos)):
            grupo = self.grupos[outro]
            janela = grupo["janela"]
            if outro == indice and not grupo["aberto"]:
                grupo["aberto"] = True
                janela.pack_propagate(False)        # a altura passa a ser a que a animação mandar
                janela.configure(height=1)
                janela.pack(fill="x", after=grupo["cabecalho"])
                grupo["altura"] = 1
                grupo["alvo"] = grupo["conteudo"].winfo_reqheight() + 8
            elif outro != indice and grupo["aberto"]:
                grupo["aberto"] = False
                altura = janela.winfo_height()
                janela.pack_propagate(False)
                janela.configure(height=max(1, altura))
                grupo["altura"] = max(1, altura)
                grupo["alvo"] = 0
            self.pintar_cabecalho(outro)
        if self.animacao is None:
            self.animar_sanfona(0)

    # Um quadro da animação: cada grupo que está abrindo ou fechando chega mais perto da altura final
    # (anda uma fração do que falta: começa rápido e termina devagar)
    def animar_sanfona(self, quadro):
        self.animacao = None
        ultimo = quadro >= QUADROS_DA_SANFONA - 1
        for grupo in self.grupos:
            if grupo["alvo"] < 0 or grupo["altura"] == grupo["alvo"]:
                continue
            if ultimo:
                grupo["altura"] = grupo["alvo"]
            else:
                grupo["altura"] += (grupo["alvo"] - grupo["altura"]) * 0.45
            grupo["janela"].configure(height=max(1, round(grupo["altura"])))
        if not ultimo:
            self.animacao = self.app.raiz.after(MILISSEGUNDOS_DA_SANFONA, lambda: self.animar_sanfona(quadro + 1))
            return
        # Terminou: os abertos voltam ao tamanho natural (acompanham o zoom); os fechados saem da tela
        for indice in range(len(self.grupos)):
            self.mostrar_grupo_na_sanfona(indice, self.grupos[indice]["aberto"])
        self.mostrar_grupo_aberto()

    # Se a sanfona estiver rolando, rola até o grupo aberto aparecer inteiro
    def mostrar_grupo_aberto(self):
        if self.grupo_aberto is None or not self.quadro.winfo_ismapped():
            return
        grupo = self.grupos[self.grupo_aberto]
        self.rolagem_da_sanfona.mostrar(grupo["janela"])
        self.rolagem_da_sanfona.mostrar(grupo["cabecalho"])

    def parar_animacao(self):
        if self.animacao is not None:
            self.app.raiz.after_cancel(self.animacao)
            self.animacao = None

    # ------------------------------------------------------------------
    # O cartão da direita
    # ------------------------------------------------------------------

    # O que o cartão mostra depende do que está aberto e escolhido
    def atualizar_cartao(self):
        if self.grupo_aberto is None:
            self.mostrar_boas_vindas()
        elif self.escolhida is not None and grupo_da_busca(self.escolhida) == self.grupo_aberto:
            self.mostrar_busca(self.escolhida)
        else:
            self.mostrar_tipo(self.grupo_aberto)

    def novo_cartao(self):
        for filho in self.cartao.winfo_children():
            filho.destroy()
        for linha in range(10):
            self.cartao.rowconfigure(linha, weight=0)
        self.miniatura = None
        self.quebras = []               # os rótulos que quebram a linha na largura do cartão
        self.estado_do_cartao = None
        return self.cartao

    def rotulo_que_quebra(self, pai, texto, estilo="Cartao.TLabel", fonte=None):
        rotulo = ttk.Label(pai, text=texto, style=estilo, justify="left")
        if fonte is not None:
            rotulo.configure(font=fonte)
        self.quebras.append(rotulo)
        rotulo.configure(wraplength=max(260, self.cartao.winfo_width() - 60))
        return rotulo

    def ajustar_quebras_de_linha(self, evento):
        for rotulo in self.quebras:
            if rotulo.winfo_exists():
                rotulo.configure(wraplength=max(260, evento.width - 60))

    # Uma etiqueta (pílula) colorida: o tipo da busca, os fatos
    def etiqueta(self, pai, texto, cor, forte=False):
        tema = self.tema
        return tk.Label(pai, text=texto, bg=misturar(tema["superficie"], cor, 0.14 if forte else 0.08), fg=cor,
                        font=self.fontes["negrito"] if forte else self.fontes["pequena"], padx=8, pady=2)

    def mostrar_boas_vindas(self):
        tema = self.tema
        cartao = self.novo_cartao()
        self.estado_do_cartao = "boas_vindas"
        ttk.Label(cartao, text="Bem-vindo ao BoscoGraph!", style="Titulo.TLabel").grid(row=0, column=0, sticky="w")
        self.rotulo_que_quebra(cartao, "Aqui você vê as buscas em grafos funcionando, por partes: o grafo, a lista e "
                                       "as matrizes, o passo a passo e o código rodando linha a linha.",
                               "CartaoSuave.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 8))
        cartao.rowconfigure(2, weight=1)
        self.criar_miniatura(cartao, 2, algoritmos.PROFUNDIDADE)
        self.rotulo_que_quebra(cartao, "Uma busca em profundidade no meio do caminho: branco = ainda não visitado, "
                                       "cinza = em andamento, preto = terminado. As arestas azuis formam a árvore da "
                                       "busca.", "CartaoSuave.TLabel", self.fontes["pequena"]).grid(
            row=3, column=0, sticky="w", pady=(4, 12))
        ttk.Label(cartao, text="Como começar", style="TituloDoPainel.TLabel").grid(row=4, column=0, sticky="w",
                                                                                 pady=(0, 6))
        passos = ttk.Frame(cartao, style="Cartao.TFrame")
        passos.grid(row=5, column=0, sticky="w")
        lado = round(self.fontes["negrito"].metrics("linespace") * 1.35)
        for numero in range(len(COMO_COMECAR)):
            circulo = tk.Canvas(passos, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0)
            circulo.grid(row=numero, column=0, pady=2)
            circulo.create_oval(1, 1, lado - 1, lado - 1, fill=tema["acento"], outline=tema["acento"])
            circulo.create_text(lado / 2, lado / 2, text=str(numero + 1), fill=tema["texto_acento"],
                                font=self.fontes["negrito"])
            ttk.Label(passos, text=COMO_COMECAR[numero], style="Cartao.TLabel").grid(row=numero, column=1, sticky="w",
                                                                                     padx=(10, 0))

    # Um tipo aberto: o que as buscas dele têm em comum e um atalho para cada algoritmo
    def mostrar_tipo(self, indice):
        tema = self.tema
        grupo = GRUPOS[indice]
        cor = tema[grupo["cor"]]
        cartao = self.novo_cartao()
        self.estado_do_cartao = ("tipo", indice)
        self.etiqueta(cartao, "TIPO DE BUSCA", cor, forte=True).grid(row=0, column=0, sticky="w")
        ttk.Label(cartao, text=grupo["titulo"], style="Titulo.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(cartao, text=grupo["subtitulo"], style="CartaoSuave.TLabel").grid(row=2, column=0, sticky="w")
        self.rotulo_que_quebra(cartao, grupo["explicacao"]).grid(row=3, column=0, sticky="w", pady=(10, 14))
        ttk.Label(cartao, text="Escolha um algoritmo:", style="TituloDoPainel.TLabel").grid(row=4, column=0, sticky="w",
                                                                                          pady=(0, 6))
        lista = ttk.Frame(cartao, style="Cartao.TFrame")
        lista.grid(row=5, column=0, sticky="ew")
        lista.columnconfigure(0, weight=1)
        for numero in range(len(grupo["buscas"])):
            self.montar_atalho(lista, numero, grupo["buscas"][numero], cor)

    # Um algoritmo no cartão do tipo: o nome, os fatos e a setinha (clicar escolhe)
    def montar_atalho(self, pai, linha, chave, cor):
        tema = self.tema
        informacoes = algoritmos.algoritmo(chave)
        caixa = tk.Frame(pai, bg=tema["superficie"], highlightthickness=1, highlightbackground=tema["borda"],
                         padx=12, pady=7, cursor="hand2")
        caixa.grid(row=linha, column=0, sticky="ew", pady=(0, 6))
        caixa.columnconfigure(0, weight=1)
        nome = tk.Label(caixa, text=informacoes["nome"], font=self.fontes["negrito"], bg=tema["superficie"],
                        fg=tema["texto"], anchor="w", cursor="hand2")
        nome.grid(row=0, column=0, sticky="w")
        detalhes = tk.Label(caixa, text=" · ".join(fatos(informacoes)), font=self.fontes["pequena"],
                            bg=tema["superficie"], fg=tema["texto_suave"], anchor="w", cursor="hand2")
        detalhes.grid(row=1, column=0, sticky="w")
        lado = round(self.fontes["negrito"].metrics("linespace"))
        seta = tk.Canvas(caixa, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0, cursor="hand2")
        seta.grid(row=0, column=1, rowspan=2)

        def pintar(em_cima):
            fundo = misturar(tema["superficie"], cor, 0.07) if em_cima else tema["superficie"]
            for componente in (caixa, nome, detalhes, seta):
                componente.configure(bg=fundo)
            caixa.configure(highlightbackground=cor if em_cima else tema["borda"])
            seta.delete("all")
            desenhar_icone(seta, "chevron_direita", lado / 2 + (2 if em_cima else 0), lado / 2, lado * 0.8,
                           cor if em_cima else tema["texto_suave"], fundo)

        pintar(False)
        for componente in (caixa, nome, detalhes, seta):
            componente.bind("<Button-1>", lambda evento: self.escolher(chave))
            componente.bind("<Double-1>", lambda evento: self.ver_exemplo(chave))
            componente.bind("<Enter>", lambda evento: pintar(True))
            componente.bind("<Leave>", lambda evento: pintar(False))

    # Um algoritmo escolhido: o que ele faz, a miniatura e os dois caminhos
    def mostrar_busca(self, chave):
        tema = self.tema
        informacoes = algoritmos.algoritmo(chave)
        grupo = GRUPOS[grupo_da_busca(chave)]
        cor = tema[grupo["cor"]]
        cartao = self.novo_cartao()
        self.estado_do_cartao = ("busca", chave)
        self.etiqueta(cartao, grupo["titulo"].upper(), cor, forte=True).grid(row=0, column=0, sticky="w")
        ttk.Label(cartao, text=informacoes["nome"], style="Titulo.TLabel").grid(row=1, column=0, sticky="w",
                                                                               pady=(6, 4))
        etiquetas = ttk.Frame(cartao, style="Cartao.TFrame")
        etiquetas.grid(row=2, column=0, sticky="w", pady=(0, 8))
        for texto in fatos(informacoes):
            self.etiqueta(etiquetas, texto, tema["texto_suave"]).pack(side="left", padx=(0, 6))
        self.rotulo_que_quebra(cartao, informacoes["descricao"]).grid(row=3, column=0, sticky="w")
        cartao.rowconfigure(4, weight=1)
        self.criar_miniatura(cartao, 4, chave)
        # Os dois caminhos, em cartões grandes na cor do tipo: o exemplo pronto (cheio, a ação principal)
        # e o editor (só com a borda). Cada cartão diz o que vai abrir.
        caminhos = ttk.Frame(cartao, style="Cartao.TFrame")
        caminhos.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        caminhos.columnconfigure(0, weight=1, uniform="caminhos")
        caminhos.columnconfigure(1, weight=1, uniform="caminhos")
        self.botao_exemplo = CartaoDeAcao(caminhos, self.app, "Ver um exemplo pronto", explicacao_do_exemplo(chave),
                                          "play", "principal", comando=lambda: self.ver_exemplo(chave),
                                          fundo=tema["superficie"], largura_minima=230, cor=cor, cheio=True,
                                          grande=True,
                                          dica="Abre a visualização com um grafo pronto para esta busca "
                                               "(Enter ou duplo clique na lista)")
        self.botao_exemplo.grid(row=0, column=0, sticky="nsew")
        self.botao_editor = CartaoDeAcao(caminhos, self.app, "Montar meu grafo",
                                         "No editor, em 3 etapas: vértices, arestas e busca", "lapis", "principal",
                                         comando=lambda: self.montar_grafo(chave), fundo=tema["superficie"],
                                         largura_minima=230, cor=cor, cheio=False, grande=True,
                                         dica="Abre o editor com esta busca escolhida, na etapa dos vértices")
        self.botao_editor.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    def criar_miniatura(self, pai, linha, chave):
        self.miniatura = tk.Canvas(pai, bg=self.tema["superficie"], highlightthickness=0, height=170)
        self.miniatura.grid(row=linha, column=0, sticky="nsew", pady=(8, 4))
        self.chave_da_miniatura = chave
        self.miniatura.bind("<Configure>", lambda evento: self.desenhar_miniatura())

    def desenhar_miniatura(self):
        if self.miniatura is None or not self.miniatura.winfo_exists():
            return
        largura = self.miniatura.winfo_width()
        altura = self.miniatura.winfo_height()
        self.miniatura.delete("all")
        if largura < 60 or altura < 60:
            return
        # A miniatura fica com proporção de 16 por 9, centralizada
        usada = min(largura, int(altura * 1.8))
        desenhar_miniatura_centralizada(self.miniatura, self.chave_da_miniatura, self.tema, largura, altura, usada)

    # ------------------------------------------------------------------
    # Os outros jeitos de começar
    # ------------------------------------------------------------------

    def montar_outros_jeitos(self):
        ttk.Label(self.quadro, text="Outros jeitos de começar", style="Negrito.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(16, 8))
        linha = ttk.Frame(self.quadro)
        linha.grid(row=4, column=0, columnspan=2, sticky="ew")
        if self.app.ultimo_editor is not None:
            anterior = self.app.ultimo_editor
            nome = anterior["modelo"].strip() or "Grafo sem nome"
            grafo = anterior["grafo"]
            titulo_do_editor = "Continuar no editor"
            texto_do_editor = (f"{nome}: " + entrada.contar(len(grafo["vertices"]), "vértice", "vértices") + ", "
                               + entrada.contar(len(grafo["arestas"]), "aresta", "arestas"))
        else:
            titulo_do_editor = "Abrir o editor"
            try:
                texto_do_editor = f"Com o modelo padrão ({modelos.nome_do_padrao()})"
            except OSError:
                texto_do_editor = "Com o modelo padrão"
        cartoes = [
            ("Começar do zero", "Um grafo vazio: você cria os vértices e as arestas", "mais", "sucesso",
             self.comecar_do_zero, "Abre o editor com um grafo vazio (o grafo de antes fica no Ctrl+Z do editor)"),
            ("Importar desenho", "draw.io, GraphML, DOT, CSV, PDF ou imagem", "importar", "info", self.importar,
             "Traz um grafo desenhado em outro programa, em etapas: escolher, conferir e abrir (Ctrl+O)"),
            ("Abrir arquivo .bosco", "Volta exatamente para onde você parou", "bosco", "roxo", self.abrir_bosco,
             "Um arquivo salvo pelo BoscoGraph: abre a visualização exatamente como ela estava"),
            (titulo_do_editor, texto_do_editor, "lapis", "neutro", self.continuar_no_editor,
             "O editor do grafo, como você deixou"),
        ]
        self.cartoes_de_acao = []
        for coluna in range(len(cartoes)):
            titulo, texto, icone, papel, comando, dica = cartoes[coluna]
            linha.columnconfigure(coluna, weight=1, uniform="jeitos")
            cartao = CartaoDeAcao(linha, self.app, titulo, texto, icone, papel, comando=comando, dica=dica,
                                  largura_minima=200)
            cartao.grid(row=0, column=coluna, sticky="nsew", padx=(0 if coluna == 0 else 10, 0))
            self.cartoes_de_acao.append(cartao)

    # ------------------------------------------------------------------
    # As escolhas e os botões
    # ------------------------------------------------------------------

    # Escolhe uma busca: o tipo dela abre na sanfona e o cartão da direita passa a mostrar ela
    def escolher(self, chave):
        self.escolhida = chave
        self.app.preferencias["busca_da_tela_inicial"] = chave
        indice = grupo_da_busca(chave)
        if self.grupo_aberto != indice:
            self.abrir_grupo(indice, animar=False)
        self.pintar_itens()
        self.mostrar_busca(chave)

    # ↑ e ↓: a busca de cima ou de baixo, dentro do tipo aberto (sem tipo aberto, abre o primeiro)
    def andar(self, sentido):
        if self.grupo_aberto is None:
            self.abrir_grupo(0, animar=False)
        buscas = GRUPOS[self.grupo_aberto]["buscas"]
        if self.escolhida in buscas:
            posicao = buscas.index(self.escolhida) + sentido
            posicao = max(0, min(posicao, len(buscas) - 1))
        elif sentido > 0:
            posicao = 0
        else:
            posicao = len(buscas) - 1
        self.escolher(buscas[posicao])
        return "break"

    def enter(self, evento=None):
        if self.estado_do_cartao == ("busca", self.escolhida):
            self.ver_exemplo(self.escolhida)
        return "break"

    # Abre a visualização direto no exemplo da busca. O exemplo também vai para o editor ("Editar grafo"),
    # com o grafo que estava lá no Desfazer.
    def ver_exemplo(self, chave):
        nome, extras = EXEMPLOS[chave]
        try:
            grafo = modelos.carregar_exemplo(nome)
        except ValueError as problema:
            self.app.mostrar_editor(busca=chave)
            self.app.tela.avisar(str(problema), erro=True)
            return
        grafo["algoritmo"] = chave
        for campo in extras:
            grafo[campo] = extras[campo]
        if algoritmos.algoritmo(chave)["destino"] == "nao":
            grafo["destino"] = None
        resumo = entrada.resumo(grafo["vertices"], grafo["arestas"], grafo["direcionado"])
        valores = valores_para_abrir(self.app, grafo, nome, f"Exemplo \"{nome}\": {resumo}. Edite à vontade: Ctrl+Z desfaz.")
        self.app.visualizar(configuracao_da_visualizacao(grafo, nome, valores))

    def montar_grafo(self, chave):
        self.app.mostrar_editor(busca=chave)

    # Um grafo vazio no editor, com a busca escolhida aqui (ou a busca em profundidade)
    def comecar_do_zero(self):
        chave = self.escolhida or algoritmos.PROFUNDIDADE
        grafo = modelos.novo_grafo([], [], True, None, True, chave)
        aviso = "Grafo novo, vazio: comece pelos vértices (o Nome e o Adicionar, ou a Quantidade)."
        if self.app.ultimo_editor is not None:
            aviso += " Ctrl+Z volta para o grafo de antes."
        self.app.mostrar_editor(valores_para_abrir(self.app, grafo, "Meu grafo", aviso, igual_ao_arquivo=False))

    def importar(self, evento=None):
        self.app.mostrar_importacao()
        return "break"

    def abrir_bosco(self):
        self.app.mostrar_bosco()

    def continuar_no_editor(self):
        self.app.mostrar_editor()

    # ------------------------------------------------------------------
    # O que toda tela tem (o aplicativo chama ao trocar o tema, mudar o zoom e trocar de tela)
    # ------------------------------------------------------------------

    def reconstruir(self):
        self.app.mostrar_inicio()

    def redesenhar(self):
        redesenhar_componentes(self.quadro)
        for indice in range(len(self.grupos)):
            self.pintar_cabecalho(indice)
        self.desenhar_miniatura()

    def destruir(self):
        self.parar_animacao()
        for tecla in ("<Control-o>", "<Control-O>", "<Up>", "<Down>", "<Return>"):
            self.app.raiz.unbind(tecla)
        self.quadro.destroy()
