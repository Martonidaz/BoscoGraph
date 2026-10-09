# Uma matriz desenhada num Canvas, com os nomes das linhas e das colunas e barras de rolagem.
# Serve para a matriz de adjacência, a de incidência e as matrizes d e π do Floyd-Warshall.
#
#   grade.mostrar(matriz, destaques)
#     matriz    -> {"linhas": [...], "colunas": [...], "celulas": {(linha, coluna): texto}}
#     destaques -> o que pintar: {"celulas": {(i, j): cor}, "linhas": {i: cor}, "colunas": {j: cor},
#                                 "contorno": {(i, j): cor}}
#   ao_clicar(linha, coluna): chamada no clique (linha ou coluna None = clique no cabeçalho)
#
# Por que um Canvas e não uma tabela (Treeview)? A tabela não pinta uma célula sozinha, só a linha
# inteira; a matriz precisa destacar a célula (i, j), a linha i e a coluna j ao mesmo tempo.

import tkinter as tk
from tkinter import ttk

MARGEM = 8                  # espaço dentro de cada célula, dos dois lados do texto
LARGURA_MINIMA = 30


class GradeDeMatriz:
    def __init__(self, pai, app, ao_clicar=None):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.ao_clicar = ao_clicar
        self.quadro = ttk.Frame(pai)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.quadro, bg=self.tema["superficie"], highlightthickness=1,
                                highlightbackground=self.tema["borda"])
        self.canvas.grid(row=0, column=0, sticky="nsew")
        rolagem_y = ttk.Scrollbar(self.quadro, orient="vertical", command=self.canvas.yview)
        rolagem_y.grid(row=0, column=1, sticky="ns")
        rolagem_x = ttk.Scrollbar(self.quadro, orient="horizontal", command=self.canvas.xview)
        rolagem_x.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=rolagem_y.set, xscrollcommand=rolagem_x.set)
        self.canvas.bind("<Button-1>", self.clicou)
        self.matriz = None
        self.destaques = {}
        self.posicoes_x = []        # onde começa cada coluna (a primeira é a dos nomes das linhas)
        self.posicoes_y = []

    def mostrar(self, matriz, destaques=None):
        self.matriz = matriz
        self.destaques = destaques or {}
        self.desenhar()

    def desenhar(self):
        c = self.canvas
        c.delete("all")
        if self.matriz is None:
            return
        tema = self.tema
        fonte = self.fontes["codigo"]
        negrito = self.fontes["negrito"]
        linhas = self.matriz["linhas"]
        colunas = self.matriz["colunas"]
        celulas = self.matriz["celulas"]
        altura = fonte.metrics("linespace") + 10

        # A largura de cada coluna: o maior texto dela (ou o nome no cabeçalho), mais as margens
        larguras = [LARGURA_MINIMA]
        for nome in linhas:
            larguras[0] = max(larguras[0], negrito.measure(str(nome)) + 2 * MARGEM)
        for j in range(len(colunas)):
            maior = negrito.measure(str(colunas[j]))
            for i in range(len(linhas)):
                maior = max(maior, fonte.measure(celulas.get((i, j), "")))
            larguras.append(max(LARGURA_MINIMA, maior + 2 * MARGEM))
        self.posicoes_x = [0]
        for largura in larguras:
            self.posicoes_x.append(self.posicoes_x[-1] + largura)
        self.posicoes_y = [0]
        for i in range(len(linhas) + 1):
            self.posicoes_y.append(self.posicoes_y[-1] + altura)

        cor_das_linhas = self.destaques.get("linhas", {})
        cor_das_colunas = self.destaques.get("colunas", {})
        cor_das_celulas = self.destaques.get("celulas", {})
        contornos = self.destaques.get("contorno", {})

        # Cabeçalhos
        c.create_rectangle(0, 0, self.posicoes_x[-1], altura, fill=tema["fundo"], outline="")
        c.create_rectangle(0, 0, larguras[0], self.posicoes_y[-1], fill=tema["fundo"], outline="")
        for j in range(len(colunas)):
            x0, x1 = self.posicoes_x[j + 1], self.posicoes_x[j + 2]
            if j in cor_das_colunas:
                c.create_rectangle(x0, 0, x1, altura, fill=cor_das_colunas[j], outline="")
            c.create_text((x0 + x1) / 2, altura / 2, text=str(colunas[j]), font=negrito, fill=tema["texto"])
        for i in range(len(linhas)):
            y0, y1 = self.posicoes_y[i + 1], self.posicoes_y[i + 2]
            if i in cor_das_linhas:
                c.create_rectangle(0, y0, larguras[0], y1, fill=cor_das_linhas[i], outline="")
            c.create_text(larguras[0] / 2, (y0 + y1) / 2, text=str(linhas[i]), font=negrito, fill=tema["texto"])

        # As células (a linha e a coluna destacadas ganham um tom clarinho; a célula, o tom forte)
        for i in range(len(linhas)):
            for j in range(len(colunas)):
                x0, x1 = self.posicoes_x[j + 1], self.posicoes_x[j + 2]
                y0, y1 = self.posicoes_y[i + 1], self.posicoes_y[i + 2]
                fundo = None
                if i in cor_das_linhas:
                    fundo = cor_das_linhas[i]
                if j in cor_das_colunas:
                    fundo = cor_das_colunas[j]
                if (i, j) in cor_das_celulas:
                    fundo = cor_das_celulas[(i, j)]
                if fundo is not None:
                    c.create_rectangle(x0, y0, x1, y1, fill=fundo, outline="")
                texto = celulas.get((i, j), "")
                cor = tema["texto"]
                if texto in ("0", "∞", ""):
                    cor = tema["texto_suave"]           # o que "não tem nada" fica mais apagado
                c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=texto, font=fonte, fill=cor)

        # A grade por cima
        for x in self.posicoes_x:
            c.create_line(x, 0, x, self.posicoes_y[-1], fill=tema["borda"])
        for y in self.posicoes_y:
            c.create_line(0, y, self.posicoes_x[-1], y, fill=tema["borda"])
        for (i, j), cor in contornos.items():
            if i < len(linhas) and j < len(colunas):
                c.create_rectangle(self.posicoes_x[j + 1] + 1, self.posicoes_y[i + 1] + 1, self.posicoes_x[j + 2] - 1,
                                   self.posicoes_y[i + 2] - 1, outline=cor, width=3)
        c.configure(scrollregion=(0, 0, self.posicoes_x[-1] + 2, self.posicoes_y[-1] + 2))

    # Rola para a célula (i, j) ficar visível
    def mostrar_celula(self, i, j):
        if self.matriz is None or not self.posicoes_x:
            return
        largura_total = max(1, self.posicoes_x[-1])
        altura_total = max(1, self.posicoes_y[-1])
        visivel_x0, visivel_x1 = self.canvas.xview()
        visivel_y0, visivel_y1 = self.canvas.yview()
        if j is not None and j + 2 < len(self.posicoes_x):
            x0 = self.posicoes_x[j + 1] / largura_total
            x1 = self.posicoes_x[j + 2] / largura_total
            if x0 < visivel_x0 or x1 > visivel_x1:
                self.canvas.xview_moveto(max(0, x0 - (visivel_x1 - visivel_x0) / 2))
        if i is not None and i + 2 < len(self.posicoes_y):
            y0 = self.posicoes_y[i + 1] / altura_total
            y1 = self.posicoes_y[i + 2] / altura_total
            if y0 < visivel_y0 or y1 > visivel_y1:
                self.canvas.yview_moveto(max(0, y0 - (visivel_y1 - visivel_y0) / 2))

    # Que célula foi clicada: (linha, coluna); None numa das duas = clique no cabeçalho
    def clicou(self, evento):
        if self.ao_clicar is None or self.matriz is None:
            return
        x = self.canvas.canvasx(evento.x)
        y = self.canvas.canvasy(evento.y)
        coluna = None
        for j in range(len(self.posicoes_x) - 1):
            if self.posicoes_x[j] <= x < self.posicoes_x[j + 1]:
                coluna = j - 1          # -1 = a coluna dos nomes das linhas
        linha = None
        for i in range(len(self.posicoes_y) - 1):
            if self.posicoes_y[i] <= y < self.posicoes_y[i + 1]:
                linha = i - 1           # -1 = a linha dos nomes das colunas
        if coluna is None or linha is None:
            return
        self.ao_clicar(None if linha < 0 else linha, None if coluna < 0 else coluna)
