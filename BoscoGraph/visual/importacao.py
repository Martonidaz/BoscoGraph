# A conferência da importação: o que foi lido do arquivo, antes de abrir o grafo.
# É a etapa 2 da tela "Importar um desenho" (visual/tela_importar.py):
#
#   - à esquerda, a prévia: o grafo desenhado nas posições do arquivo (ou em círculo); no PDF e na
#     imagem, o que foi reconhecido aparece POR CIMA da imagem original, para comparar;
#   - à direita, o resumo e as escolhas:
#       Orientação -> detectada no arquivo, mas dá para trocar (Orientado  A → B  ou  Não orientado  A — B);
#       Pesos      -> manter os do arquivo, tirar todos ou sortear de 1 a 9 (cada clique sorteia de novo);
#       Desenho    -> como no arquivo ou em círculo (só aparece se o arquivo tem as posições);
#       Avisos     -> o que precisou ser ajustado (nomes, arestas ignoradas, textos soltos...).
# Quem decide o que fazer com o grafo (editar ou visualizar) é a tela; este painel só monta o grafo
# com as escolhas (grafo_escolhido).

import base64
import random
import tkinter as tk
from tkinter import ttk

import entrada
import importacao
from visual import previa
from visual.botoes import Segmentos, desenhar_icone
from visual.rolagem import QuadroRolavel

# O que fazer com os pesos do arquivo: (valor, texto do botão, ícone)
OPCOES_DE_PESO = [("manter", "Manter", None), ("tirar", "Tirar", None), ("sortear", "Sortear", "dado")]
LARGURA_DO_LADO = 360           # a coluna das escolhas, em pixels a 100% de zoom


class PainelDeConferencia:
    # escolhas: as escolhas de antes (quando a tela é recriada na troca de tema); None = as do arquivo
    # ao_mudar: chamado depois de cada mudança (a tela atualiza o "pronto para visualizar")
    def __init__(self, pai, app, importado, escolhas=None, ao_mudar=None):
        self.app = app
        self.tema = app.tema
        self.importado = importado
        self.ao_mudar = ao_mudar
        detectado = importado["orientacao_detectada"]
        direcionado = importado["direcionado"] if detectado is not None else True
        pesos = "manter"
        sorteados = []
        arrumacao = "arquivo" if importado["posicoes"] else "circulo"
        if escolhas is not None:
            direcionado = escolhas["direcionado"]
            pesos = escolhas["pesos"]
            sorteados = list(escolhas["pesos_sorteados"])
            arrumacao = escolhas["arrumacao"]
        self.direcionado = tk.BooleanVar(value=direcionado)
        self.pesos = tk.StringVar(value=pesos)
        self.pesos_sorteados = sorteados        # os pesos do último sorteio (um por aresta)
        self.arrumacao = tk.StringVar(value=arrumacao)
        # As imagens (PDF e foto) ficam guardadas: sem isso, o Tkinter apaga a imagem e a prévia some
        self.imagem_inteira = None
        self.imagem_metade = None
        self.montar(pai, detectado)
        self.atualizar(avisar=False)

    def montar(self, pai, detectado):
        tema = self.tema
        app = self.app
        importado = self.importado
        largura_do_lado = round(LARGURA_DO_LADO * app.zoom)
        self.quadro = ttk.Frame(pai)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(0, weight=1)

        # A prévia (estica com a janela)
        moldura = ttk.Frame(self.quadro, style="Painel.TFrame", padding=8)
        moldura.grid(row=0, column=0, sticky="nsew")
        moldura.columnconfigure(0, weight=1)
        moldura.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(moldura, bg=tema["canvas"], highlightthickness=0, width=420, height=300)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda evento: self.desenhar_previa())
        legenda = "A prévia do grafo como ele vai abrir."
        if importado.get("imagem"):
            legenda = ("Por cima da imagem original: em azul, os vértices reconhecidos; em laranja, as arestas. "
                       "Compare com o desenho.")
        ttk.Label(moldura, text=legenda, style="CartaoSuave.TLabel", wraplength=600, justify="left").grid(
            row=1, column=0, sticky="w", pady=(6, 0))

        # As escolhas (coluna da direita, largura fixa; rola se não couber na altura)
        moldura_do_lado = tk.Frame(self.quadro, bg=tema["superficie"], highlightthickness=1,
                                   highlightbackground=tema["borda"])
        moldura_do_lado.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        self.rolagem = QuadroRolavel(moldura_do_lado, app, tema["superficie"])
        self.rolagem.pack(fill="both", expand=True)
        lado = ttk.Frame(self.rolagem.conteudo, style="Cartao.TFrame", padding=(16, 12, 16, 12))
        lado.pack(fill="both", expand=True)
        lado.columnconfigure(0, weight=1)
        quebra = largura_do_lado - 36
        ttk.Label(lado, text=importado["fonte"], style="TituloDoPainel.TLabel", wraplength=quebra).grid(
            row=0, column=0, sticky="w")
        self.rotulo_resumo = ttk.Label(lado, style="Cartao.TLabel", wraplength=quebra, justify="left")
        self.rotulo_resumo.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.titulo_da_secao(lado, 2, "Orientação")
        self.escolha_orientacao = Segmentos(lado, app, [(True, "Orientado", "aresta_orientada"),
                                                        (False, "Não orientado", "aresta_simples")],
                                            self.direcionado, comando=self.atualizar, fundo=tema["superficie"])
        self.escolha_orientacao.grid(row=3, column=0, sticky="w")
        if detectado is None:
            origem = "O arquivo não diz se o grafo é orientado: escolha acima."
        elif importado["orientacao_veio_de"] == "arquivo":
            origem = "Lido do arquivo: " + ("orientado (A → B)." if detectado else "não orientado (A — B).")
        else:
            origem = ("Pelas setas do desenho: " + ("orientado (A → B)." if detectado else
                                                    "não orientado (nenhuma seta)."))
        ttk.Label(lado, text=origem, style="CartaoSuave.TLabel", wraplength=quebra, justify="left").grid(
            row=4, column=0, sticky="w", pady=(4, 0))

        # Os pesos: os do arquivo, nenhum ou sorteados (como na parte Pesos da visualização)
        self.titulo_da_secao(lado, 5, "Pesos")
        linha = ttk.Frame(lado, style="Cartao.TFrame")
        linha.grid(row=6, column=0, sticky="w")
        self.escolha_pesos = Segmentos(linha, app, OPCOES_DE_PESO, self.pesos, comando=self.mudar_pesos,
                                       fundo=tema["superficie"])
        self.escolha_pesos.pack(side="left")
        self.rotulo_pesos = ttk.Label(lado, style="CartaoSuave.TLabel", wraplength=quebra, justify="left")
        self.rotulo_pesos.grid(row=7, column=0, sticky="w", pady=(4, 0))

        # O desenho: nas posições do arquivo (se ele tiver) ou em círculo
        linha_dos_avisos = 8
        if importado["posicoes"]:
            self.titulo_da_secao(lado, 8, "Desenho")
            Segmentos(lado, app, [("arquivo", "Como no arquivo", None), ("circulo", "Em círculo", None)],
                      self.arrumacao, comando=self.atualizar, fundo=tema["superficie"]).grid(row=9, column=0, sticky="nw")
            linha_dos_avisos = 10

        self.titulo_da_secao(lado, linha_dos_avisos, "Avisos")
        moldura = ttk.Frame(lado, style="Cartao.TFrame")
        moldura.grid(row=linha_dos_avisos + 1, column=0, sticky="nsew")
        moldura.columnconfigure(0, weight=1)
        moldura.rowconfigure(0, weight=1)
        self.caixa_de_avisos = tk.Text(moldura, width=30, height=4, wrap="word", font=app.fontes["pequena"],
                                       bg=tema["codigo_fundo"], fg=tema["texto"], relief="flat",
                                       highlightthickness=1, highlightbackground=tema["borda"], padx=8, pady=6,
                                       cursor="arrow")
        self.caixa_de_avisos.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(moldura, orient="vertical", command=self.caixa_de_avisos.yview)
        rolagem.grid(row=0, column=1, sticky="ns")
        self.caixa_de_avisos.configure(yscrollcommand=rolagem.set)
        avisos = importado["avisos"]
        if not avisos:
            avisos = ["Nada precisou ser ajustado."]
        self.caixa_de_avisos.insert("1.0", "• " + "\n• ".join(avisos))
        self.caixa_de_avisos.configure(state="disabled")

        if importado["conferir"]:
            aviso = tk.Frame(lado, bg=tema["superficie"])
            aviso.grid(row=linha_dos_avisos + 2, column=0, sticky="ew", pady=(10, 0))
            icone = tk.Canvas(aviso, width=20, height=20, bg=tema["superficie"], highlightthickness=0)
            icone.pack(side="left", anchor="n", padx=(0, 6))
            desenhar_icone(icone, "alerta", 10, 10, 18, tema["destaque"], tema["superficie"])
            ttk.Label(aviso, text="O reconhecimento de PDF e de imagem pode errar: compare a prévia com o "
                                  "desenho e, se precisar, corrija no editor.",
                      style="CartaoSuave.TLabel", wraplength=quebra - 26, justify="left").pack(side="left")
        self.rolagem.ligar_roda()

    def titulo_da_secao(self, pai, linha, texto):
        ttk.Label(pai, text=texto, style="TituloDoPainel.TLabel").grid(row=linha, column=0, sticky="w", pady=(14, 4))

    # As escolhas de agora (a tela guarda para recriar o painel igual, na troca de tema)
    def escolhas(self):
        return {"direcionado": self.direcionado.get(), "pesos": self.pesos.get(),
                "pesos_sorteados": list(self.pesos_sorteados), "arrumacao": self.arrumacao.get()}

    # O grafo como vai ser aberto: a orientação, os pesos e o desenho escolhidos aqui
    def grafo_escolhido(self):
        grafo = importacao.grafo_para_o_editor(self.importado, self.direcionado.get())
        modo = self.pesos.get()
        if modo == "sortear" and len(self.pesos_sorteados) != len(grafo["arestas"]):
            self.sortear()              # a orientação mudou o número de arestas: sorteia de novo
        arestas = []
        for numero in range(len(grafo["arestas"])):
            origem, destino, nome, peso = grafo["arestas"][numero]
            if modo == "tirar":
                peso = None
            elif modo == "sortear":
                peso = self.pesos_sorteados[numero]
            arestas.append((origem, destino, nome, peso))
        grafo["arestas"] = arestas
        if self.arrumacao.get() == "circulo" or not grafo["posicoes"]:
            grafo["arrumacao"] = "circulo"
        else:
            grafo["arrumacao"] = "arquivo"
        return grafo

    def sortear(self):
        quantidade = len(importacao.grafo_para_o_editor(self.importado, self.direcionado.get())["arestas"])
        self.pesos_sorteados = entrada.sortear_numeros(quantidade, 1, 9, random.randint(0, 10 ** 6))

    def mudar_pesos(self):
        if self.pesos.get() == "sortear":
            self.sortear()              # cada clique em "Sortear" sorteia de novo
        self.atualizar()

    # avisar=False: na montagem (a tela ainda não está pronta para ouvir as mudanças)
    def atualizar(self, avisar=True):
        grafo = self.grafo_escolhido()
        texto = (f"Encontrei {entrada.contar(len(grafo['vertices']), 'vértice', 'vértices')} e "
                 f"{entrada.contar(len(grafo['arestas']), 'aresta', 'arestas')}")
        com_peso_no_arquivo = len(self.importado["arestas"]) - len(entrada.indices_sem_peso(self.importado["arestas"]))
        if com_peso_no_arquivo:
            texto += f" ({com_peso_no_arquivo} com peso no arquivo)"
        texto += "."
        if grafo["posicoes"] and grafo["arrumacao"] == "arquivo":
            texto += " O desenho vai abrir nas mesmas posições do arquivo."
        self.rotulo_resumo.configure(text=texto)
        modo = self.pesos.get()
        if modo == "manter":
            explicacao = ("Os pesos ficam como vieram do arquivo." if com_peso_no_arquivo else
                          "O arquivo não tem pesos (o Dijkstra, o Bellman-Ford, o Floyd-Warshall e o A* precisam).")
        elif modo == "tirar":
            explicacao = "Nenhuma aresta vai ter peso."
        else:
            explicacao = "Cada aresta ganha um peso inteiro de 1 a 9 (clique de novo em Sortear para outro sorteio)."
        self.rotulo_pesos.configure(text=explicacao)
        self.desenhar_previa()
        if avisar and self.ao_mudar is not None:
            self.ao_mudar()

    # A prévia: a imagem original (PDF ou foto) com o que foi reconhecido por cima, ou o grafo sozinho
    def desenhar_previa(self):
        c = self.canvas
        c.delete("all")
        largura = c.winfo_width()
        altura = c.winfo_height()
        if largura < 40 or altura < 40:
            return                      # ainda não apareceu na tela
        if self.importado.get("imagem"):
            self.desenhar_sobre_a_imagem(largura, altura)
            return
        grafo = self.grafo_escolhido()
        previa.desenhar_grafo(c, self.app, grafo["vertices"], grafo["arestas"], self.direcionado.get(),
                              grafo["posicoes"], grafo["arrumacao"], 0, 0, largura, altura, self.tema["canvas"])

    # PDF e imagem: a imagem original e, por cima, os vértices (círculos azuis) e as arestas
    # (linhas laranja) que foram reconhecidos, nas posições em que foram encontrados.
    # A imagem fica no meio da prévia; se não couber, aparece pela metade do tamanho.
    def desenhar_sobre_a_imagem(self, largura, altura):
        c = self.canvas
        tema = self.tema
        if self.imagem_inteira is None:
            dados = base64.b64encode(self.importado["imagem"]).decode("ascii")
            self.imagem_inteira = tk.PhotoImage(data=dados)
        escala = 1
        imagem = self.imagem_inteira
        if imagem.width() > largura or imagem.height() > altura:
            escala = 0.5
            if self.imagem_metade is None:
                self.imagem_metade = self.imagem_inteira.subsample(2)     # um pixel a cada dois
            imagem = self.imagem_metade
        x0 = (largura - imagem.width()) / 2
        y0 = (altura - imagem.height()) / 2
        c.create_image(x0, y0, anchor="nw", image=imagem)
        marcas = self.importado.get("marcas") or {}
        for x1, y1, x2, y2, seta_no_fim in marcas.get("arestas", []):
            seta = "last" if seta_no_fim and self.direcionado.get() else "none"
            c.create_line(x0 + x1 * escala, y0 + y1 * escala, x0 + x2 * escala, y0 + y2 * escala, fill=tema["destaque"],
                          width=3, arrow=seta, arrowshape=(10, 12, 4))
        altura_do_nome = self.app.fontes["negrito"].metrics("linespace")
        for nome, x, y, raio in marcas.get("vertices", []):
            x = x0 + x * escala
            y = y0 + y * escala
            raio = raio * escala
            c.create_oval(x - raio, y - raio, x + raio, y + raio, outline=tema["acento"], width=3)
            # O nome vai em cima do vértice; perto da borda de cima da imagem, vai embaixo (senão some)
            if y - raio - 3 - altura_do_nome >= y0:
                texto = c.create_text(x, y - raio - 3, text=nome, anchor="s", fill=tema["acento"],
                                      font=self.app.fontes["negrito"])
            else:
                texto = c.create_text(x, y + raio + 3, text=nome, anchor="n", fill=tema["acento"],
                                      font=self.app.fontes["negrito"])
            caixa = c.bbox(texto)
            fundo = c.create_rectangle(caixa[0] - 2, caixa[1], caixa[2] + 2, caixa[3], fill=tema["superficie"],
                                       outline="")
            c.tag_lower(fundo, texto)
