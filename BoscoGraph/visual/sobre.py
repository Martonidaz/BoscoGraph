# A janela "Sobre": o que é o BoscoGraph, a versão, quando foi criado e por quem.
# Abre pelo botão "Sobre" da tela inicial (o Esc ou o Fechar fecham).

import platform
import tkinter as tk
from tkinter import ttk

import caminhos
from visual import logo
from visual.botoes import Botao, desenhar_icone
from visual.dialogos import Dialogo

DATA_DE_CRIACAO = "29/09/2026"
CRIADOR = "Daniel Marton Barbosa"
CO_CRIADORES = ["Breno Ryan de Andrade Fernandes", "João Vitor Ferreira Azevedo Pereira",
           "Mariana Gonçalves de Freitas Ribeiro"]
PROFESSORES = ["Bruno Bustamante Ferreira Leonor", "Warner Brezolin"]
DISCIPLINA = "Teoria dos Grafos · Engenharia de Computação, 8º período"

RESUMO = ("O BoscoGraph mostra, por partes, como os algoritmos de grafos funcionam: o grafo, a lista de adjacência, "
          "as matrizes, o passo a passo e o código rodando linha a linha, em seis linguagens. São doze algoritmos: "
          "dez buscas, da profundidade (DFS) ao A*, e a árvore geradora mínima (Prim e Kruskal), em grafos montados "
          "no editor ou importados de outros programas.")

LARGURA_DO_TEXTO = 470          # em pixels a 100% de zoom


class DialogoSobre(Dialogo):
    def __init__(self, app):
        super().__init__(app, "Sobre o BoscoGraph")
        tema = self.tema
        fontes = app.fontes
        q = self.quadro
        quebra = round(LARGURA_DO_TEXTO * app.zoom)
        q.columnconfigure(0, weight=1)

        # O logo, o nome e a versão
        topo = ttk.Frame(q, style="Cartao.TFrame")
        topo.grid(row=0, column=0, sticky="w")
        tamanho = fontes["titulo"].metrics("linespace") * 2 + 8
        desenho = tk.Canvas(topo, width=tamanho, height=tamanho, bg=tema["superficie"], highlightthickness=0)
        desenho.grid(row=0, column=0, rowspan=2, padx=(0, 14))
        logo.desenhar_logo(desenho, 1, 1, tamanho - 2)
        ttk.Label(topo, text=caminhos.NOME_DO_PROGRAMA, style="Titulo.TLabel").grid(row=0, column=1, sticky="sw")
        ttk.Label(topo, text=f"Versão {caminhos.VERSAO} · criado em {DATA_DE_CRIACAO}",
                  style="CartaoSuave.TLabel").grid(row=1, column=1, sticky="nw")

        ttk.Label(q, text=RESUMO, style="Cartao.TLabel", wraplength=quebra, justify="left").grid(
            row=1, column=0, sticky="w", pady=(14, 6))
        ttk.Separator(q).grid(row=2, column=0, sticky="ew", pady=8)

        # Quem fez: cada grupo com o seu ícone
        pessoas = ttk.Frame(q, style="Cartao.TFrame")
        pessoas.grid(row=3, column=0, sticky="w")
        grupos = [("pessoa", "Criado por", [CRIADOR]),
                  ("pessoas", "Co-criadores", CO_CRIADORES),
                  ("capelo", "Professores", PROFESSORES),
                  ("calendario", "Disciplina", [DISCIPLINA])]
        lado = round(fontes["negrito"].metrics("linespace") * 1.25)
        for linha in range(len(grupos)):
            icone, titulo, nomes = grupos[linha]
            desenho = tk.Canvas(pessoas, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0)
            desenho.grid(row=linha, column=0, sticky="nw", padx=(0, 12), pady=(0 if linha == 0 else 10, 0))
            desenhar_icone(desenho, icone, lado / 2, lado / 2, lado * 0.85, tema["acento"], tema["superficie"])
            bloco = ttk.Frame(pessoas, style="Cartao.TFrame")
            bloco.grid(row=linha, column=1, sticky="w", pady=(0 if linha == 0 else 10, 0))
            ttk.Label(bloco, text=titulo, style="CartaoSuave.TLabel", font=fontes["pequena"]).pack(anchor="w")
            for nome in nomes:
                ttk.Label(bloco, text=nome, style="TituloDoPainel.TLabel").pack(anchor="w")

        ttk.Separator(q).grid(row=4, column=0, sticky="ew", pady=(14, 8))
        versao_do_tk = app.raiz.tk.call("info", "patchlevel")
        rodape = ttk.Frame(q, style="Cartao.TFrame")
        rodape.grid(row=5, column=0, sticky="ew")
        rodape.columnconfigure(0, weight=1)
        ttk.Label(rodape, text=f"Feito em Python {platform.python_version()} com Tkinter {versao_do_tk} · "
                               f"{platform.system()} {platform.release()}",
                  style="CartaoSuave.TLabel", font=fontes["pequena"]).grid(row=0, column=0, sticky="w")
        botao = Botao(rodape, app, "Fechar", icone="check", papel="principal", comando=self.fechar,
                      fundo=tema["superficie"])
        botao.grid(row=0, column=1, sticky="e", padx=(16, 0))
        self.janela.bind("<Return>", lambda evento: self.fechar())
        self.mostrar(botao)


def mostrar_sobre(app):
    if app.dialogo is not None:
        return                      # já tem uma janelinha aberta
    DialogoSobre(app)
