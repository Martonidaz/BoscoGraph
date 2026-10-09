# O que toda parte da tela por partes tem em comum (a classe Parte) e alguns ajudantes.
#
# Uma "parte" é um pedaço da visualização que mostra UMA coisa de cada vez: os vértices, as arestas, a
# matriz de adjacência, o passo a passo da busca... A tela (visual/visualizacao.py) mostra uma parte
# por vez; cada uma tem a sua cor (o título, a trilha da esquerda e o destaque do que foi escolhido).
#
# Cada parte guarda as próprias escolhas (o que está selecionado, os painéis abertos, a posição do
# passo a passo) em self.escolhas: a tela guarda esse dicionário quando a parte sai e devolve quando
# ela volta, e o arquivo .bosco grava todos eles.

import tkinter as tk
from tkinter import ttk

from visual.componentes import PainelRecolhivel
from visual.grafo_na_tela import DesenhoDoGrafo
from visual.tema import misturar


class Parte:
    chave = ""
    titulo = ""
    grupo = "grafo"                 # "grafo" ou "busca"
    descricao = ""                  # uma frase sobre a parte (aparece embaixo do título)
    escolhas_iniciais = {}          # o que a parte lembra (veja a explicação no começo do arquivo)

    def __init__(self, tela, escolhas):
        self.tela = tela
        self.app = tela.app
        self.tema = tela.app.tema
        self.fontes = tela.app.fontes
        self.sessao = tela.sessao
        self.cor = self.tema["parte_" + self.chave]
        # O tom clarinho da cor da parte (fundo da linha escolhida nas tabelas e no código)
        self.tinta = misturar(self.tema["superficie"], self.cor, 0.22)
        self.escolhas = dict(self.escolhas_iniciais)
        self.escolhas.update(escolhas or {})
        self.agendamentos = []
        self.desenho = None

    # As partes de baixo implementam:
    def montar(self, pai):
        pass

    def mostrar(self):
        pass

    # A janela mudou de tamanho (ou o zoom): só redesenha
    def redesenhar(self):
        self.mostrar()

    # As setas do teclado (← →), o espaço e Home/End: as partes com tocador respondem
    def tecla(self, nome):
        return False

    def destruir(self):
        for agendamento in self.agendamentos:
            try:
                self.app.raiz.after_cancel(agendamento)
            except tk.TclError:
                pass
        self.agendamentos = []

    # ------------------------------------------------------------------
    # Ajudantes que várias partes usam
    # ------------------------------------------------------------------

    # O painel do grafo (recolhível) dentro de uma divisão, com o desenho e os cliques ligados.
    #   ao_clicar(item): um clique no desenho (item = ("vertice", nome), ("aresta", número) ou None)
    #   ao_clicar_duas_vezes(item): o duplo clique; aqui o item também pode ser ("peso", número), quando
    #                               o clique foi em cima do peso escrito na aresta
    def criar_painel_do_grafo(self, divisao, titulo="Grafo", peso=3, ao_clicar=None, ao_clicar_duas_vezes=None):
        painel = PainelRecolhivel(divisao, self.app, titulo, peso, ao_mudar=self.ao_recolher)
        canvas = tk.Canvas(painel.corpo, bg=self.tema["canvas"], highlightthickness=1,
                           highlightbackground=self.tema["borda"], width=420, height=300)
        canvas.pack(fill="both", expand=True)
        self.desenho = DesenhoDoGrafo(canvas, self.app)
        self.desenho.configurar(self.sessao.vertices, self.sessao.arestas, self.sessao.direcionado,
                                self.sessao.posicoes)
        canvas.bind("<Configure>", self.ao_redimensionar_o_desenho)
        if ao_clicar is not None:
            canvas.bind("<Button-1>", lambda evento: ao_clicar(self.desenho.item_em(evento.x, evento.y)))
        if ao_clicar_duas_vezes is not None:
            canvas.bind("<Double-1>",
                        lambda evento: ao_clicar_duas_vezes(self.desenho.item_para_editar(evento.x, evento.y)))
        return painel

    def ao_redimensionar_o_desenho(self, evento=None):
        self.agendar(40, self.redesenhar)

    def ao_recolher(self):
        self.escolhas["recolhidos"] = self.recolhidos()
        self.agendar(30, self.redesenhar)

    # Os painéis recolhidos da parte (as partes que têm painéis recolhíveis respondem)
    def recolhidos(self):
        return {}

    # Agenda um redesenho, cancelando o anterior (para não redesenhar dez vezes seguidas)
    def agendar(self, milissegundos, funcao):
        if getattr(self, "agendamento_do_desenho", None) is not None:
            try:
                self.app.raiz.after_cancel(self.agendamento_do_desenho)
            except tk.TclError:
                pass
        self.agendamento_do_desenho = self.app.raiz.after(milissegundos, funcao)
        self.agendamentos.append(self.agendamento_do_desenho)

    # Agenda uma função sem cancelar nada (tudo é cancelado quando a parte sai da tela)
    def depois(self, milissegundos, funcao):
        self.agendamentos.append(self.app.raiz.after(milissegundos, funcao))

    # Divide o espaço de uma divisão (PanedWindow) depois que ela aparece: "fracao" para o primeiro
    # painel. Sem isto, um painel que pede muito espaço (uma matriz larga) espreme o desenho.
    def posicionar_divisao(self, divisao, fracao, tentativas=10):
        def posicionar():
            try:
                largura = divisao.winfo_width() if str(divisao.cget("orient")) == "horizontal" \
                    else divisao.winfo_height()
            except tk.TclError:
                return          # a parte já saiu da tela
            if largura < 100:
                if tentativas > 0:
                    self.posicionar_divisao(divisao, fracao, tentativas - 1)
                return
            if len(divisao.panes()) >= 2:
                divisao.sashpos(0, int(largura * fracao))
        self.depois(80, posicionar)

    # As opções do desenho que valem em toda parte (nomes, pesos e arrumação, do menu Exibir)
    def opcoes_do_desenho(self, **outras):
        opcoes = {
            "algoritmo": self.sessao.algoritmo,
            "destino": self.sessao.destino_da_busca(),
            "arrumacao": self.app.preferencias.get("arrumacao", "circulo"),
            "nomes": self.app.preferencias.get("nomes_das_arestas", True),
            "pesos": self.app.preferencias.get("pesos_das_arestas", True),
            "informacao": self.sessao.descricao(),
        }
        opcoes.update(outras)
        return opcoes

    # Uma tabela (Treeview) com as colunas pedidas: [(nome, título, largura, estica?), ...].
    # As colunas que esticam (textos compridos: listas, conclusões) ficam alinhadas à esquerda.
    # A linha escolhida fica na cor da parte (cada parte tem o seu estilo de tabela).
    def criar_tabela(self, pai, colunas, selecao="browse", altura=8):
        quadro = ttk.Frame(pai)
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        nomes = [coluna[0] for coluna in colunas]
        estilo = f"Parte_{self.chave}.Treeview"
        ttk.Style(self.app.raiz).map(estilo, background=[("selected", self.tinta)],
                                     foreground=[("selected", self.tema["texto"])])
        tabela = ttk.Treeview(quadro, columns=nomes, show="headings", selectmode=selecao, height=altura, style=estilo)
        for nome, titulo, largura, estica in colunas:
            tabela.heading(nome, text=titulo, anchor="w" if estica and largura >= 150 else "center")
            tabela.column(nome, width=largura, minwidth=30, stretch=estica,
                          anchor="w" if estica and largura >= 150 else "center")
        tabela.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
        rolagem.grid(row=0, column=1, sticky="ns")
        tabela.configure(yscrollcommand=rolagem.set)
        tabela.tag_configure("escolhida", background=self.tinta, foreground=self.tema["texto"])
        tabela.tag_configure("destaque", background=self.tema["fundo_destaque"], foreground=self.tema["texto"])
        tabela.tag_configure("suave", foreground=self.tema["texto_suave"])
        return quadro, tabela

    # Um título da parte: o nome na cor da parte e a frase de explicação embaixo
    # com_descricao=False: só o título (no Passo a passo, o lado dele é dos botões das 6 etapas)
    def criar_titulo(self, pai, com_descricao=True):
        quadro = ttk.Frame(pai)
        rotulo = ttk.Label(quadro, text=self.titulo, style="TituloDaParte.TLabel", foreground=self.cor)
        rotulo.pack(side="left")
        if self.descricao and com_descricao:
            explicacao = ttk.Label(quadro, text=self.descricao, style="Suave.TLabel")
            explicacao.pack(side="left", padx=(12, 0))
        return quadro


def limpar_tabela(tabela):
    for item in tabela.get_children():
        tabela.delete(item)


# O nome da coluna de uma tabela que está na posição x (do mouse), ou None.
# O Treeview responde "#1", "#2"... (a ordem das colunas que aparecem); aqui vira o nome ("peso").
def coluna_em(tabela, x):
    texto = tabela.identify_column(x)
    if not texto.startswith("#") or not texto[1:].isdigit():
        return None
    exibidas = tabela.cget("displaycolumns")
    if isinstance(exibidas, str):
        exibidas = (exibidas,)
    if tuple(exibidas) == ("#all",):             # "#all" = todas as colunas, na ordem em que foram criadas
        exibidas = tabela.cget("columns")
    indice = int(texto[1:]) - 1
    if 0 <= indice < len(exibidas):
        return exibidas[indice]
    return None
