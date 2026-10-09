# A tela "Abrir arquivo .bosco": o arquivo que o BoscoGraph salva (Exportar ▸ Arquivo .bosco) com o grafo,
# a busca e a tela do jeito que estavam.
#
#   - à esquerda: o que é um .bosco, o botão "Escolher arquivo .bosco…" e os abertos recentemente;
#   - à direita: a prévia do arquivo escolhido (o nome, a busca, quantos vértices e arestas, quando foi
#     salvo, em que parte abre e o desenho do grafo) e o botão "Abrir", que vai para a visualização
#     exatamente como ela foi salva.
# Se o arquivo tiver um problema (não é do BoscoGraph, está estragado, sumiu...), a explicação aparece
# no lugar da prévia, com os botões para escolher outro ou tirar o arquivo da lista.

import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import algoritmos
import entrada
from exportacao import bosco
from visual import previa
from visual.botoes import Botao, cor_do_papel, cor_sobre_o_papel, desenhar_icone, redesenhar_componentes
from visual.cabecalho import Cabecalho
from visual.tema import misturar

LARGURA_DA_ESQUERDA = 400           # a coluna da esquerda, em pixels a 100% de zoom


# "2026-10-01 14:30" -> "01/10/2026 às 14:30" (o que não estiver nesse formato fica como veio)
def data_brasileira(texto):
    partes = texto.split(" ")
    data = partes[0].split("-")
    if len(data) != 3:
        return texto
    resultado = f"{data[2]}/{data[1]}/{data[0]}"
    if len(partes) > 1:
        resultado += " às " + partes[1]
    return resultado


# O nome de cada parte da visualização ("passo" -> "Passo a passo")
def nome_da_parte(chave):
    from visual.visualizacao import PARTES
    for classe in PARTES:
        if classe.chave == chave:
            return classe.titulo
    return None


class TelaDoBosco:
    # caminho: um arquivo já escolhido (mostra a prévia); erro: o problema dele (mostra a explicação)
    def __init__(self, app, caminho=None, erro=None):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.caminho = caminho
        self.erro = erro
        self.detalhes = None            # o que foi lido do arquivo (bosco.ler_com_detalhes)
        self.montar()
        if caminho is not None and erro is None:
            self.ler(caminho)
        else:
            self.mostrar_previa()
        self.app.raiz.bind("<Control-o>", self.escolher)
        self.app.raiz.bind("<Control-O>", self.escolher)
        self.app.raiz.bind("<Return>", self.abrir)

    def montar(self):
        tema = self.tema
        zoom = self.app.zoom
        self.quadro = ttk.Frame(self.app.raiz, padding=(24, 16, 24, 14))
        self.quadro.pack(fill="both", expand=True)
        self.quadro.columnconfigure(1, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        self.cabecalho = Cabecalho(self.quadro, self.app, "Abrir arquivo .bosco",
                                   "Volte exatamente para onde parou: a mesma parte, o mesmo passo, as mesmas escolhas",
                                   voltar=self.app.mostrar_inicio)
        self.cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # A coluna da esquerda
        esquerda = ttk.Frame(self.quadro, width=round(LARGURA_DA_ESQUERDA * zoom))
        esquerda.grid(row=1, column=0, sticky="nsw", padx=(0, 16))
        esquerda.columnconfigure(0, weight=1)
        quebra = round(LARGURA_DA_ESQUERDA * zoom) - 90
        roxo = cor_do_papel(tema, "roxo")
        fundo = misturar(tema["superficie"], roxo, 0.06)
        explicacao = tk.Frame(esquerda, bg=fundo, highlightthickness=1, highlightbackground=misturar(tema["borda"], roxo, 0.4),
                              padx=14, pady=12)
        explicacao.grid(row=0, column=0, sticky="ew")
        lado = round(self.fontes["negrito"].metrics("linespace") * 2.3)
        desenho = tk.Canvas(explicacao, width=lado, height=lado, bg=fundo, highlightthickness=0)
        desenho.grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 12))
        desenho.create_oval(1, 1, lado - 1, lado - 1, fill=roxo, outline=roxo)
        desenhar_icone(desenho, "bosco", lado / 2, lado / 2, lado * 0.5, cor_sobre_o_papel(tema), roxo)
        tk.Label(explicacao, text="O que é um arquivo .bosco?", font=self.fontes["negrito"], bg=fundo,
                 fg=tema["texto"], anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(explicacao, text="É o arquivo que o BoscoGraph salva em Exportar ▸ Arquivo .bosco. Ele guarda "
                                  "o grafo, a busca e a tela do jeito que estavam. No Windows, dois cliques no "
                                  "arquivo também abrem.",
                 font=self.fontes["pequena"], bg=fundo, fg=tema["texto_suave"], anchor="w", justify="left",
                 wraplength=quebra).grid(row=1, column=1, sticky="w", pady=(2, 0))
        self.botao_escolher = Botao(esquerda, self.app, "Escolher arquivo .bosco…", icone="pasta", papel="roxo",
                                    tamanho="grande", comando=self.escolher, dica="Abre a janela para escolher o arquivo (Ctrl+O)")
        self.botao_escolher.grid(row=1, column=0, sticky="ew", pady=(14, 18))
        ttk.Label(esquerda, text="Abertos recentemente", style="Negrito.TLabel").grid(row=2, column=0, sticky="w",
                                                                                     pady=(0, 6))
        self.lista_de_recentes = ttk.Frame(esquerda)
        self.lista_de_recentes.grid(row=3, column=0, sticky="ew")
        self.lista_de_recentes.columnconfigure(0, weight=1)
        self.montar_recentes()

        # A prévia (à direita)
        self.cartao = ttk.Frame(self.quadro, style="Painel.TFrame", padding=(20, 16, 20, 16))
        self.cartao.grid(row=1, column=1, sticky="nsew")
        self.cartao.columnconfigure(0, weight=1)
        self.rotulo_do_caminho = None
        self.cartao.bind("<Configure>", self.ajustar_caminho)

    # ------------------------------------------------------------------
    # Os abertos recentemente
    # ------------------------------------------------------------------

    def montar_recentes(self):
        for filho in self.lista_de_recentes.winfo_children():
            filho.destroy()
        tema = self.tema
        recentes = bosco.listar_recentes()
        if not recentes:
            ttk.Label(self.lista_de_recentes, text="Os arquivos .bosco que você abrir ou salvar vão aparecer aqui.",
                      style="Suave.TLabel", wraplength=round(LARGURA_DA_ESQUERDA * self.app.zoom) - 20,
                      justify="left").grid(row=0, column=0, sticky="w")
            return
        for indice in range(len(recentes)):
            caminho = recentes[indice]
            escolhido = self.caminho is not None and bosco.mesmo_arquivo(caminho, self.caminho)
            existe = os.path.isfile(caminho)
            fundo = misturar(tema["superficie"], cor_do_papel(tema, "roxo"), 0.12) if escolhido else tema["superficie"]
            linha = tk.Frame(self.lista_de_recentes, bg=fundo, highlightthickness=1,
                             highlightbackground=cor_do_papel(tema, "roxo") if escolhido else tema["borda"],
                             padx=10, pady=6, cursor="hand2")
            linha.grid(row=indice, column=0, sticky="ew", pady=(0, 6))
            linha.columnconfigure(1, weight=1)
            lado = round(self.fontes["negrito"].metrics("linespace") * 1.1)
            desenho = tk.Canvas(linha, width=lado, height=lado, bg=fundo, highlightthickness=0, cursor="hand2")
            desenho.grid(row=0, column=0, rowspan=2, padx=(0, 10))
            cor = cor_do_papel(tema, "roxo") if existe else tema["texto_suave"]
            desenhar_icone(desenho, "bosco", lado / 2, lado / 2, lado * 0.95, cor, fundo)
            nome = Path(caminho).name
            rotulo_nome = tk.Label(linha, text=nome, font=self.fontes["negrito"], bg=fundo,
                                   fg=tema["texto"] if existe else tema["texto_suave"], anchor="w", cursor="hand2")
            rotulo_nome.grid(row=0, column=1, sticky="w")
            pasta = str(Path(caminho).parent)
            if not existe:
                pasta = "não encontrado em " + pasta
            rotulo_pasta = tk.Label(linha, text=self.encurtar(pasta, round(LARGURA_DA_ESQUERDA * self.app.zoom) - 90),
                                    font=self.fontes["pequena"], bg=fundo,
                                    fg=tema["texto_suave"], anchor="w", cursor="hand2")
            rotulo_pasta.grid(row=1, column=1, sticky="w")
            for componente in (linha, desenho, rotulo_nome, rotulo_pasta):
                componente.bind("<Button-1>", lambda evento, caminho=caminho: self.ler(caminho))
                componente.bind("<Double-1>", lambda evento, caminho=caminho: self.abrir_direto(caminho))
            if not escolhido:
                self.ligar_destaque(linha, (desenho, rotulo_nome, rotulo_pasta))

    # O mouse em cima de uma linha da lista: o fundo fica levemente roxo
    def ligar_destaque(self, linha, componentes):
        tema = self.tema
        destaque = misturar(tema["superficie"], cor_do_papel(tema, "roxo"), 0.06)

        def pintar(cor):
            linha.configure(bg=cor)
            for componente in componentes:
                componente.configure(bg=cor)

        linha.bind("<Enter>", lambda evento: pintar(destaque))
        linha.bind("<Leave>", lambda evento: pintar(tema["superficie"]))

    # Um caminho comprido fica "…" no começo (o fim do caminho é o que mais ajuda a reconhecer)
    def encurtar(self, texto, largura):
        fonte = self.fontes["pequena"]
        if fonte.measure(texto) <= largura:
            return texto
        while len(texto) > 4 and fonte.measure("…" + texto) > largura:
            texto = texto[1:]
        return "…" + texto

    # ------------------------------------------------------------------
    # A prévia
    # ------------------------------------------------------------------

    def ler(self, caminho):
        self.caminho = caminho
        self.erro = None
        self.detalhes = None
        try:
            self.detalhes = bosco.ler_com_detalhes(caminho)
        except ValueError as problema:
            self.erro = str(problema)
        self.montar_recentes()
        self.mostrar_previa()

    def novo_cartao(self):
        self.rotulo_do_caminho = None
        for filho in self.cartao.winfo_children():
            filho.destroy()
        for linha in range(8):
            self.cartao.rowconfigure(linha, weight=0)

    def mostrar_previa(self):
        self.novo_cartao()
        if self.erro is not None:
            self.mostrar_erro()
        elif self.detalhes is None:
            self.mostrar_vazio()
        else:
            self.mostrar_detalhes()

    # Nada escolhido ainda
    def mostrar_vazio(self):
        tema = self.tema
        self.cartao.rowconfigure(0, weight=1)
        miolo = ttk.Frame(self.cartao, style="Cartao.TFrame")
        miolo.grid(row=0, column=0)
        lado = round(72 * self.app.zoom)
        desenho = tk.Canvas(miolo, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0)
        desenho.pack()
        desenhar_icone(desenho, "bosco", lado / 2, lado / 2, lado * 0.8, misturar(tema["superficie"],
                                                                                 cor_do_papel(tema, "roxo"), 0.35),
                       tema["superficie"])
        ttk.Label(miolo, text="Escolha um arquivo para ver a prévia aqui", style="Cartao.TLabel",
                  font=self.fontes["mensagem"]).pack(pady=(12, 4))
        ttk.Label(miolo, text="Você vê o grafo, a busca e onde a visualização vai abrir antes de abrir.",
                  style="CartaoSuave.TLabel").pack()

    # O arquivo tem um problema: a explicação e o que dá para fazer
    def mostrar_erro(self):
        tema = self.tema
        fundo = misturar(tema["superficie"], tema["erro"], 0.07)
        caixa = tk.Frame(self.cartao, bg=fundo, highlightthickness=1, highlightbackground=tema["erro"], padx=14, pady=12)
        caixa.grid(row=0, column=0, sticky="ew")
        caixa.columnconfigure(1, weight=1)
        lado = round(self.fontes["mensagem"].metrics("linespace") * 1.2)
        desenho = tk.Canvas(caixa, width=lado, height=lado, bg=fundo, highlightthickness=0)
        desenho.grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 12))
        desenhar_icone(desenho, "alerta", lado / 2, lado / 2, lado * 0.95, tema["erro"], fundo)
        nome = Path(self.caminho).name if self.caminho else "o arquivo"
        tk.Label(caixa, text=f"Não consegui abrir {nome}", font=self.fontes["negrito"], bg=fundo, fg=tema["erro"],
                 anchor="w").grid(row=0, column=1, sticky="w")
        self.rotulo_do_erro = tk.Label(caixa, text=self.erro, font=self.fontes["texto"], bg=fundo, fg=tema["texto"],
                                       anchor="w", justify="left", wraplength=600)
        self.rotulo_do_erro.grid(row=1, column=1, sticky="w", pady=(2, 0))
        caixa.bind("<Configure>", lambda evento: self.rotulo_do_erro.configure(wraplength=max(200, evento.width - lado - 60)))
        botoes = ttk.Frame(self.cartao, style="Cartao.TFrame")
        botoes.grid(row=1, column=0, sticky="w", pady=(14, 0))
        Botao(botoes, self.app, "Escolher outro arquivo", icone="pasta", papel="roxo", comando=self.escolher,
              fundo=tema["superficie"]).pack(side="left")
        # O que costuma causar o problema (ajuda a pessoa a decidir o que fazer)
        dicas = ttk.Frame(self.cartao, style="Cartao.TFrame")
        dicas.grid(row=2, column=0, sticky="w", pady=(22, 0))
        ttk.Label(dicas, text="O que pode ter acontecido", style="TituloDoPainel.TLabel").pack(anchor="w")
        for texto in ("O arquivo não foi salvo pelo BoscoGraph (só o Exportar ▸ Arquivo .bosco cria um .bosco).",
                      "O arquivo foi editado à mão e ficou com um erro.",
                      "O arquivo foi salvo por uma versão mais nova do BoscoGraph.",
                      "O arquivo mudou de pasta ou foi apagado depois de aberto."):
            ttk.Label(dicas, text="•  " + texto, style="CartaoSuave.TLabel").pack(anchor="w", pady=(4, 0))
        if self.esta_nos_recentes(self.caminho):
            Botao(botoes, self.app, "Tirar da lista", icone="lixeira", papel="perigo", comando=self.tirar_da_lista,
                  fundo=tema["superficie"], dica="Tira este arquivo dos abertos recentemente (o arquivo não é apagado)"
                  ).pack(side="left", padx=(8, 0))

    def esta_nos_recentes(self, caminho):
        if caminho is None:
            return False
        for outro in bosco.listar_recentes():
            if bosco.mesmo_arquivo(outro, caminho):
                return True
        return False

    # Tudo certo: o resumo, o desenho e o botão Abrir
    def mostrar_detalhes(self):
        tema = self.tema
        detalhes = self.detalhes
        grafo = detalhes["grafo"]
        tela = detalhes["tela"]
        busca = algoritmos.algoritmo(grafo["algoritmo"])
        ttk.Label(self.cartao, text=detalhes["nome"], style="TituloDoPainel.TLabel", font=self.fontes["titulo"]).grid(
            row=0, column=0, sticky="w")
        # As etiquetas: a busca, a orientação, quantos vértices e arestas, os pesos
        etiquetas = ttk.Frame(self.cartao, style="Cartao.TFrame")
        etiquetas.grid(row=1, column=0, sticky="w", pady=(6, 8))
        textos = [busca["nome"], "orientado" if grafo["direcionado"] else "não orientado",
                  entrada.contar(len(grafo["vertices"]), "vértice", "vértices"),
                  entrada.contar(len(grafo["arestas"]), "aresta", "arestas")]
        if entrada.tem_pesos(grafo["arestas"]):
            textos.append("com pesos")
        roxo = cor_do_papel(tema, "roxo")
        for indice in range(len(textos)):
            if indice == 0:                 # a busca, em destaque
                fundo = misturar(tema["superficie"], roxo, 0.14)
                cor = roxo
                fonte = self.fontes["negrito"]
            else:
                fundo = misturar(tema["superficie"], tema["borda"], 0.6)
                cor = tema["texto"]
                fonte = self.fontes["pequena"]
            tk.Label(etiquetas, text=textos[indice], font=fonte, bg=fundo, fg=cor, padx=8, pady=2).pack(
                side="left", padx=(0, 6))
        # Onde a visualização abre, quando foi salvo e onde está o arquivo
        parte = nome_da_parte(tela.get("parte"))
        linhas = []
        if parte is not None:
            linhas.append(f"Abre na parte \"{parte}\", com as escolhas que estavam na tela.")
        else:
            linhas.append("Abre a visualização do começo.")
        salvo = ""
        if detalhes["salvo_em"]:
            salvo = "Salvo em " + data_brasileira(detalhes["salvo_em"])
        if detalhes["programa"]:
            salvo += (" · " if salvo else "") + "pelo " + detalhes["programa"]
        if salvo:
            linhas.append(salvo + ".")
        ttk.Label(self.cartao, text="\n".join(linhas), style="Cartao.TLabel", justify="left").grid(
            row=2, column=0, sticky="w")
        self.rotulo_do_caminho = ttk.Label(self.cartao, style="CartaoSuave.TLabel", font=self.fontes["pequena"])
        self.rotulo_do_caminho.grid(row=3, column=0, sticky="w", pady=(2, 8))
        self.ajustar_caminho()
        # O desenho do grafo (estica com a janela)
        self.cartao.rowconfigure(4, weight=1)
        self.desenho = tk.Canvas(self.cartao, bg=tema["canvas"], highlightthickness=1,
                                 highlightbackground=tema["borda"], height=200)
        self.desenho.grid(row=4, column=0, sticky="nsew")
        self.desenho.bind("<Configure>", lambda evento: self.desenhar_grafo())
        botoes = ttk.Frame(self.cartao, style="Cartao.TFrame")
        botoes.grid(row=5, column=0, sticky="e", pady=(14, 0))
        Botao(botoes, self.app, "Escolher outro", icone="pasta", papel="contorno", comando=self.escolher,
              fundo=tema["superficie"]).pack(side="left", padx=(0, 8))
        Botao(botoes, self.app, "Abrir", icone="play", papel="roxo", tamanho="grande", subtitulo="ir para a visualização",
              comando=self.abrir, fundo=tema["superficie"], dica="Abre a visualização como ela foi salva (Enter)"
              ).pack(side="left")

    # O caminho do arquivo cabe na largura do cartão (se não couber, o começo vira "…")
    def ajustar_caminho(self, evento=None):
        if self.rotulo_do_caminho is None or not self.rotulo_do_caminho.winfo_exists():
            return
        largura = self.cartao.winfo_width() - 50
        if evento is not None:
            largura = evento.width - 50
        caminho = os.path.abspath(self.caminho)
        self.rotulo_do_caminho.configure(text=self.encurtar(caminho, max(200, largura)))

    def desenhar_grafo(self):
        c = self.desenho
        c.delete("all")
        largura = c.winfo_width()
        altura = c.winfo_height()
        if largura < 40 or altura < 40 or self.detalhes is None:
            return
        grafo = self.detalhes["grafo"]
        exibir = self.detalhes["tela"].get("exibir", {})
        arrumacao = exibir.get("arrumacao") or grafo["arrumacao"]
        previa.desenhar_grafo(c, self.app, grafo["vertices"], grafo["arestas"], grafo["direcionado"],
                              grafo["posicoes"], arrumacao, 0, 0, largura, altura, self.tema["canvas"])

    # ------------------------------------------------------------------
    # Os botões
    # ------------------------------------------------------------------

    def escolher(self, evento=None):
        from visual import exportar
        caminho = exportar.escolher_bosco(self.app)
        if caminho is not None:
            self.ler(caminho)
        return "break"

    def abrir(self, evento=None):
        if self.detalhes is None or self.caminho is None:
            return "break"
        from visual import exportar
        exportar.abrir_bosco(self.app, self.caminho)
        return "break"

    # Duplo clique num recente: abre direto (se tiver problema, a explicação aparece aqui)
    def abrir_direto(self, caminho):
        self.ler(caminho)
        if self.detalhes is not None:
            self.abrir()

    def tirar_da_lista(self):
        bosco.esquecer_recente(self.caminho)
        self.caminho = None
        self.erro = None
        self.detalhes = None
        self.montar_recentes()
        self.mostrar_previa()

    # ------------------------------------------------------------------
    # O que toda tela tem
    # ------------------------------------------------------------------

    def reconstruir(self):
        self.app.mostrar_bosco(self.caminho, self.erro)

    def redesenhar(self):
        redesenhar_componentes(self.quadro)
        if self.detalhes is not None and self.erro is None:
            self.desenhar_grafo()

    def destruir(self):
        for tecla in ("<Control-o>", "<Control-O>", "<Return>"):
            self.app.raiz.unbind(tecla)
        self.quadro.destroy()
