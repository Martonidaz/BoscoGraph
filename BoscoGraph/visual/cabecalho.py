# O cabeçalho das telas, sempre no mesmo lugar e com a mesma cara:
#
#   [◀ Início]  [logo]  Título                                   [botões da tela]  [☀ ● ☾]
#                       Subtítulo (o que dá para fazer aqui)
#
# - "◀ Início" volta para a tela inicial (a tela inicial não tem, ela já é o início);
# - à direita ficam os botões próprios de cada tela e, por último, a chave do tema (sol e lua).
# Uso:
#   cabecalho = Cabecalho(quadro, app, "Importar um desenho", "Traga um grafo feito em outro programa",
#                         voltar=app.mostrar_inicio)
#   cabecalho.grid(row=0, column=0, sticky="ew")
#   Botao(cabecalho.botoes, app, "Sobre", icone="info", papel="icone").pack(side="left")

import tkinter as tk
from tkinter import ttk

from visual import logo
from visual.botoes import Botao, ChaveDoTema


class Cabecalho(ttk.Frame):
    # voltar: a função do botão "◀ Início" (None = sem o botão)
    def __init__(self, pai, app, titulo, subtitulo, voltar=None):
        super().__init__(pai)
        self.app = app
        self.columnconfigure(2, weight=1)
        if voltar is not None:
            # O "suave" (fundo azul clarinho, letras azuis) destaca o Início sem competir com a ação principal
            Botao(self, app, "Início", icone="seta_esquerda", papel="suave", comando=voltar,
                  dica="Volta para a tela inicial").grid(row=0, column=0, rowspan=2, padx=(0, 14))
        self.canvas_logo = tk.Canvas(self, bg=app.tema["fundo"], highlightthickness=0)
        self.canvas_logo.grid(row=0, column=1, rowspan=2, padx=(0, 12))
        self.desenhar_logo()
        self.rotulo_titulo = ttk.Label(self, text=titulo, style="Marca.TLabel")
        self.rotulo_titulo.grid(row=0, column=2, sticky="sw")
        self.rotulo_subtitulo = ttk.Label(self, text=subtitulo, style="Suave.TLabel")
        self.rotulo_subtitulo.grid(row=1, column=2, sticky="nw")
        # Os botões de cada tela entram aqui (com pack, da esquerda para a direita)
        self.botoes = ttk.Frame(self)
        self.botoes.grid(row=0, column=3, rowspan=2, sticky="e", padx=(12, 12))
        self.chave_do_tema = ChaveDoTema(self, app)
        self.chave_do_tema.grid(row=0, column=4, rowspan=2, sticky="e")

    # O logo tem o tamanho de duas linhas do título (acompanha o zoom)
    def desenhar_logo(self):
        tamanho = self.app.fontes["titulo"].metrics("linespace") * 2
        self.canvas_logo.configure(width=tamanho, height=tamanho)
        self.canvas_logo.delete("all")
        logo.desenhar_logo(self.canvas_logo, 1, 1, tamanho - 2)

    # Depois de uma mudança de zoom (o redesenhar_componentes chama todos os que têm "remedir")
    def remedir(self):
        self.desenhar_logo()

    def mudar_textos(self, titulo=None, subtitulo=None):
        if titulo is not None:
            self.rotulo_titulo.configure(text=titulo)
        if subtitulo is not None:
            self.rotulo_subtitulo.configure(text=subtitulo)
