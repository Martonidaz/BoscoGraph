# A tela "Importar um desenho": traz um grafo feito em outro programa, uma etapa de cada vez.
#
#   Etapa 1 — Escolher o arquivo: o botão "Escolher arquivo…" abre a janela do sistema; embaixo, os
#             formatos que o BoscoGraph entende. Enquanto o arquivo é lido (PDF e imagem podem levar
#             alguns segundos), aparece "Lendo…". Se der problema, a explicação aparece aqui mesmo.
#   Etapa 2 — Conferir o que foi lido: a prévia e as escolhas (orientação, pesos, desenho), no
#             painel de visual/importacao.py.
#   Etapa 3 — Editar ou visualizar: "Editar grafo" abre o editor com o grafo; "Visualizar grafo" vai
#             direto para a visualização, com a busca escolhida.
# "◀ Início" volta para a tela inicial. Um arquivo .bosco escolhido aqui vai para a tela do .bosco
# (ele abre a visualização salva, sem conferência).
#
# O que estava no editor não se perde: o grafo importado entra no editor com o grafo de antes no
# Desfazer (Ctrl+Z volta para ele).

import gc
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import ttk

import algoritmos
import entrada
import importacao
from visual.botoes import Botao, Etapas, cor_do_papel, desenhar_icone, quebrar_texto, redesenhar_componentes
from visual.cabecalho import Cabecalho
from visual.dica import Dica
from visual.editor import configuracao_da_visualizacao, valores_para_abrir
from visual.importacao import PainelDeConferencia
from visual.logo import retangulo_arredondado
from visual.tema import misturar

ETAPAS = ["Escolher o arquivo", "Conferir o que foi lido", "Editar ou visualizar"]

# Os formatos que aparecem na etapa 1: (nome, extensões, explicação, ícone)
FORMATOS = [
    ("draw.io", ".drawio  .xml", "Diagramas do draw.io (diagrams.net)", "grafo"),
    ("GraphML", ".graphml", "Do yEd, do Gephi e de outros programas", "grafo"),
    ("DOT", ".dot  .gv", "O texto do Graphviz", "codigo"),
    ("CSV", ".csv  .tsv  .txt", "Lista de arestas ou matriz de adjacência", "matriz"),
    ("PDF", ".pdf", "Um desenho exportado em PDF", "arquivo"),
    ("Imagem", ".png  .jpg  .bmp…", "Foto ou print do desenho (confira: pode errar)", "imagem"),
]
INTERVALO_DA_LEITURA = 80           # de quantos em quantos milissegundos a tela olha se a leitura terminou


# A coleta de lixo do Python (o "gc", que apaga os objetos que ninguém mais usa) fica desligada enquanto
# uma leitura roda em segundo plano. Motivo: a coleta pode acontecer DENTRO da linha de execução da
# leitura e apagar ali objetos do Tkinter de telas que já fecharam (variáveis, imagens, fontes); só que
# o Tkinter só aceita ser usado pela linha principal (a das janelas). Antes de começar, o lixo que já
# existe é apagado na linha principal; quando a última leitura termina, a coleta volta a funcionar.
leituras_em_andamento = 0


def desligar_a_coleta():
    global leituras_em_andamento
    if leituras_em_andamento == 0:
        gc.collect()
        gc.disable()
    leituras_em_andamento += 1


# Olha de tempos em tempos (pela janela principal, que existe até o programa fechar) se a leitura acabou
def religar_a_coleta_quando_terminar(raiz, tarefa):
    global leituras_em_andamento
    if tarefa.is_alive():
        raiz.after(INTERVALO_DA_LEITURA, lambda: religar_a_coleta_quando_terminar(raiz, tarefa))
        return
    leituras_em_andamento -= 1
    if leituras_em_andamento == 0:
        gc.enable()


# A busca que já vem escolhida: a da tela inicial, a do editor ou a busca em profundidade
def busca_inicial(app):
    chave = app.preferencias.get("busca_da_tela_inicial")
    if chave is None and app.ultimo_editor is not None:
        chave = app.ultimo_editor["grafo"]["algoritmo"]
    if chave is None:
        chave = algoritmos.PROFUNDIDADE
    return algoritmos.algoritmo(chave)["nome"]


class TelaDeImportacao:
    # estado: como a tela estava (na troca de tema); None = começa na etapa 1
    def __init__(self, app, estado=None):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.etapa = 1
        self.caminho = None             # o arquivo escolhido
        self.importado = None           # o que foi lido dele (importacao.importar_arquivo)
        self.erro = None                # o problema da última leitura (aparece na etapa 1)
        self.lendo = False
        self.leitura = None             # {"numero": n, "importado": ... ou "erro": ...} da leitura em andamento
        self.numero_da_leitura = 0      # cada leitura tem um número: o resultado de uma leitura cancelada é ignorado
        self.agendamento = None
        self.painel = None
        self.variavel_da_busca = tk.StringVar(value=busca_inicial(app))
        self.montar()
        if estado is not None and estado.get("busca"):
            self.variavel_da_busca.set(estado["busca"])
        if estado is not None and estado.get("lendo") and estado.get("caminho"):
            self.ler_arquivo(estado["caminho"])
        elif estado is not None and estado.get("etapa") == 2 and estado.get("importado") is not None:
            self.caminho = estado["caminho"]
            self.importado = estado["importado"]
            self.mostrar_conferencia(estado.get("escolhas"))
        else:
            if estado is not None:
                self.caminho = estado.get("caminho")
                self.erro = estado.get("erro")
            self.mostrar_escolha()
        self.app.raiz.bind("<Control-o>", self.escolher_arquivo)
        self.app.raiz.bind("<Control-O>", self.escolher_arquivo)

    def montar(self):
        self.quadro = ttk.Frame(self.app.raiz, padding=(24, 16, 24, 14))
        self.quadro.pack(fill="both", expand=True)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(2, weight=1)
        self.cabecalho = Cabecalho(self.quadro, self.app, "Importar um desenho",
                                   "Traga um grafo feito em outro programa e confira antes de abrir",
                                   voltar=self.voltar_ao_inicio)
        self.cabecalho.grid(row=0, column=0, sticky="ew")
        self.etapas = Etapas(self.quadro, self.app, ETAPAS, atual=0, ao_clicar=self.voltar_para_a_etapa)
        self.etapas.grid(row=1, column=0, sticky="ew", pady=(16, 12))
        self.corpo = None

    # Troca o miolo da tela (cada etapa monta o seu)
    def novo_corpo(self):
        self.parar_animacoes()
        if self.corpo is not None:
            self.corpo.destroy()
        self.painel = None
        self.corpo = ttk.Frame(self.quadro)
        self.corpo.grid(row=2, column=0, sticky="nsew")
        return self.corpo

    # ------------------------------------------------------------------
    # Etapa 1: escolher o arquivo
    # ------------------------------------------------------------------

    def mostrar_escolha(self):
        self.etapa = 1
        self.etapas.mudar(0)
        self.app.raiz.unbind("<Return>")
        corpo = self.novo_corpo()
        corpo.columnconfigure(0, weight=1)
        linha = 0
        if self.erro:
            self.montar_caixa_de_erro(corpo).grid(row=linha, column=0, sticky="ew", pady=(0, 12))
            linha += 1
        self.zona = tk.Canvas(corpo, bg=self.tema["fundo"], highlightthickness=0,
                              cursor="" if self.lendo else "hand2")
        self.zona.grid(row=linha, column=0, sticky="ew")
        self.zona.bind("<Configure>", lambda evento: self.desenhar_zona())
        self.zona.bind("<ButtonRelease-1>", self.escolher_arquivo)
        self.zona.bind("<Enter>", lambda evento: self.desenhar_zona(em_cima=True))
        self.zona.bind("<Leave>", self.saiu_da_zona)
        self.zona_em_cima = False
        self.botao_escolher = Botao(self.zona, self.app, "Escolher arquivo…", icone="pasta", papel="info",
                                    tamanho="grande", comando=self.escolher_arquivo, fundo=self.tema["superficie"],
                                    dica="Abre a janela para escolher o arquivo (Ctrl+O)")
        self.barra_de_leitura = None
        self.botao_cancelar_leitura = None
        if self.lendo:
            self.barra_de_leitura = ttk.Progressbar(self.zona, mode="indeterminate", length=round(320 * self.app.zoom))
            self.barra_de_leitura.start(12)
            self.botao_cancelar_leitura = Botao(self.zona, self.app, "Cancelar", icone="x", papel="neutro",
                                                comando=self.cancelar_leitura, fundo=self.tema["superficie"])
        self.desenhar_zona()

        # Os formatos que dá para importar
        ttk.Label(corpo, text="O BoscoGraph entende estes formatos", style="Negrito.TLabel").grid(
            row=linha + 1, column=0, sticky="w", pady=(18, 8))
        grade = ttk.Frame(corpo)
        grade.grid(row=linha + 2, column=0, sticky="ew")
        for indice in range(len(FORMATOS)):
            grade.columnconfigure(indice, weight=1, uniform="formatos")
            self.montar_formato(grade, FORMATOS[indice]).grid(row=0, column=indice, sticky="nsew",
                                                              padx=(0 if indice == 0 else 8, 0))
        bosco = ttk.Frame(corpo)
        bosco.grid(row=linha + 3, column=0, sticky="w", pady=(16, 0))
        ttk.Label(bosco, text="Tem um arquivo .bosco (salvo pelo próprio BoscoGraph)? Ele abre na tela dele:",
                  style="Suave.TLabel").pack(side="left", padx=(0, 10))
        Botao(bosco, self.app, "Abrir arquivo .bosco", icone="bosco", papel="roxo", tamanho="pequeno",
              comando=lambda: self.app.mostrar_bosco()).pack(side="left")

    # A área grande do meio: o ícone, o convite e o botão (ou o "Lendo…" com a barra andando)
    def desenhar_zona(self, em_cima=None):
        if em_cima is not None:
            self.zona_em_cima = em_cima
        z = self.zona
        tema = self.tema
        zoom = self.app.zoom
        z.delete("all")             # apaga o desenho e tira o botão do lugar (o botão continua existindo)
        largura = max(z.winfo_width(), 300)
        cor = cor_do_papel(tema, "info")
        diametro = round(64 * zoom)
        fonte_do_titulo = self.fontes["mensagem"]
        fonte_do_texto = self.fontes["texto"]
        if self.lendo:
            titulo = f"Lendo {Path(self.caminho).name}…"
            texto = "PDF e imagem podem levar alguns segundos: o BoscoGraph procura os círculos, as linhas e os nomes."
        elif self.erro:
            titulo = "Tente outro arquivo"
            texto = "Ou confira se o arquivo abre no programa em que ele foi feito."
        else:
            titulo = "Escolha o arquivo com o desenho do grafo"
            texto = ("O BoscoGraph lê os vértices, as arestas, os nomes e os pesos. "
                     "Depois você confere tudo antes de abrir.")
        linhas = quebrar_texto(texto, fonte_do_texto, min(620 * zoom, largura - 60))
        y = round(22 * zoom)
        altura_do_titulo = fonte_do_titulo.metrics("linespace")
        altura_do_texto = len(linhas) * fonte_do_texto.metrics("linespace")
        altura_do_botao = self.botao_escolher.altura
        altura = (y + diametro + round(12 * zoom) + altura_do_titulo + round(4 * zoom) + altura_do_texto
                  + round(16 * zoom) + altura_do_botao + round(26 * zoom))
        if self.lendo:
            altura += round(30 * zoom)
        else:
            altura += fonte_do_texto.metrics("linespace")
        if int(z.cget("height")) != altura:
            z.configure(height=altura)
        # A moldura tracejada (o mouse em cima deixa a linha cheia e o fundo levemente colorido)
        fundo = tema["superficie"] if not self.zona_em_cima or self.lendo else misturar(tema["superficie"], cor, 0.05)
        retangulo_arredondado(z, 2, 2, largura - 2, altura - 2, round(14 * zoom), fill=fundo,
                              outline=cor if self.zona_em_cima else misturar(tema["borda"], cor, 0.5),
                              width=2, dash=() if self.zona_em_cima else (6, 4))
        cx = largura / 2
        z.create_oval(cx - diametro / 2, y, cx + diametro / 2, y + diametro, fill=cor, outline=cor)
        icone = "relogio" if self.lendo else "importar"
        desenhar_icone(z, icone, cx, y + diametro / 2, diametro * 0.5, "#ffffff" if tema["nome"] == "claro" else "#0b0d10",
                       cor)
        y += diametro + round(12 * zoom)
        z.create_text(cx, y, text=titulo, anchor="n", font=fonte_do_titulo, fill=tema["texto"])
        y += altura_do_titulo + round(4 * zoom)
        z.create_text(cx, y, text="\n".join(linhas), anchor="n", justify="center", font=fonte_do_texto,
                      fill=tema["texto_suave"])
        y += altura_do_texto + round(16 * zoom)
        if self.lendo:
            z.create_window(cx, y + 6, window=self.barra_de_leitura, anchor="n", )
            z.create_window(cx, y + round(30 * zoom), window=self.botao_cancelar_leitura, anchor="n",
                            )
        else:
            z.create_window(cx, y, window=self.botao_escolher, anchor="n", )
            y += altura_do_botao + round(6 * zoom)
            z.create_text(cx, y, text="ou aperte Ctrl+O", anchor="n", font=self.fontes["pequena"],
                          fill=tema["texto_suave"])

    # O mouse saiu da área grande. Passar para cima do botão de dentro também conta como "sair" para o
    # Tkinter: nesse caso a área continua destacada (o mouse ainda está dentro dela)
    def saiu_da_zona(self, evento=None):
        z = self.zona
        x, y = z.winfo_pointerxy()
        dentro = (z.winfo_rootx() <= x < z.winfo_rootx() + z.winfo_width()
                  and z.winfo_rooty() <= y < z.winfo_rooty() + z.winfo_height())
        if not dentro:
            self.desenhar_zona(em_cima=False)

    # Um formato: o ícone, o nome, as extensões e a explicação
    def montar_formato(self, pai, formato):
        nome, extensoes, explicacao, icone = formato
        tema = self.tema
        cartao = tk.Frame(pai, bg=tema["superficie"], highlightthickness=1, highlightbackground=tema["borda"],
                          padx=10, pady=8)
        lado = round(self.fontes["negrito"].metrics("linespace") * 1.2)
        desenho = tk.Canvas(cartao, width=lado, height=lado, bg=tema["superficie"], highlightthickness=0)
        desenho.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 8))
        desenhar_icone(desenho, icone, lado / 2, lado / 2, lado * 0.9, cor_do_papel(tema, "info"), tema["superficie"])
        tk.Label(cartao, text=nome, font=self.fontes["negrito"], bg=tema["superficie"], fg=tema["texto"],
                 anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(cartao, text=extensoes, font=self.fontes["pequena"], bg=tema["superficie"], fg=cor_do_papel(tema, "info"),
                 anchor="w").grid(row=1, column=1, sticky="w")
        rotulo = tk.Label(cartao, text=explicacao, font=self.fontes["pequena"], bg=tema["superficie"],
                          fg=tema["texto_suave"], anchor="w", justify="left", wraplength=150)
        rotulo.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        cartao.columnconfigure(1, weight=1)
        # A explicação quebra a linha na largura que o cartão tiver
        cartao.bind("<Configure>", lambda evento: rotulo.configure(wraplength=max(80, evento.width - 24)))
        return cartao

    # A caixa vermelha com o problema da última leitura
    def montar_caixa_de_erro(self, pai):
        tema = self.tema
        fundo = misturar(tema["superficie"], tema["erro"], 0.07)
        caixa = tk.Frame(pai, bg=fundo, highlightthickness=1, highlightbackground=tema["erro"], padx=14, pady=10)
        lado = round(self.fontes["mensagem"].metrics("linespace") * 1.2)
        desenho = tk.Canvas(caixa, width=lado, height=lado, bg=fundo, highlightthickness=0)
        desenho.grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 12))
        desenhar_icone(desenho, "alerta", lado / 2, lado / 2, lado * 0.95, tema["erro"], fundo)
        nome = Path(self.caminho).name if self.caminho else "o arquivo"
        tk.Label(caixa, text=f"Não consegui ler {nome}", font=self.fontes["negrito"], bg=fundo, fg=tema["erro"],
                 anchor="w").grid(row=0, column=1, sticky="w")
        self.rotulo_do_erro = tk.Label(caixa, text=self.erro, font=self.fontes["texto"], bg=fundo, fg=tema["texto"],
                                       anchor="w", justify="left", wraplength=800)
        self.rotulo_do_erro.grid(row=1, column=1, sticky="w", pady=(2, 0))
        caixa.columnconfigure(1, weight=1)
        caixa.bind("<Configure>", lambda evento: self.rotulo_do_erro.configure(wraplength=max(200, evento.width - lado - 60)))
        return caixa

    # Abre a janela do sistema para escolher o arquivo (começa na pasta da última importação)
    def escolher_arquivo(self, evento=None):
        if self.lendo:
            return "break"
        pasta = self.app.preferencias.get("pasta_de_importacao")
        caminho = filedialog.askopenfilename(parent=self.app.raiz, title="Importar um desenho de grafo",
                                             initialdir=pasta or None, filetypes=importacao.TIPOS_DE_ARQUIVO)
        if not caminho:
            return "break"              # desistiu: a tela continua como estava
        self.app.preferencias["pasta_de_importacao"] = str(Path(caminho).parent)
        if caminho.lower().endswith(".bosco"):
            self.app.mostrar_bosco(caminho)     # o .bosco abre na tela dele, com a prévia
            return "break"
        self.ler_arquivo(caminho)
        return "break"

    # Lê o arquivo. PDF e imagem podem demorar: a leitura roda numa "thread" (uma linha de execução
    # separada), e a tela continua respondendo; de tempos em tempos ela olha se a leitura terminou.
    # em_segundo_plano=False lê de uma vez (os testes usam assim).
    def ler_arquivo(self, caminho, em_segundo_plano=True):
        self.caminho = caminho
        self.erro = None
        self.numero_da_leitura += 1
        numero = self.numero_da_leitura
        resultado = {"numero": numero}
        self.leitura = resultado

        def ler():
            try:
                resultado["importado"] = importacao.importar_arquivo(caminho)
            except importacao.ProblemaNaImportacao as problema:
                resultado["erro"] = str(problema)
            except Exception as erro:          # a rede de segurança: nunca deixar a tela presa em "Lendo…"
                resultado["erro"] = f"Erro inesperado ao ler o arquivo ({type(erro).__name__}: {erro})."
            resultado["pronto"] = True

        if not em_segundo_plano:
            ler()
            self.terminar_leitura(resultado)
            return
        self.lendo = True
        self.mostrar_escolha()
        desligar_a_coleta()
        tarefa = threading.Thread(target=ler, daemon=True)
        tarefa.start()
        religar_a_coleta_quando_terminar(self.app.raiz, tarefa)
        self.agendamento = self.app.raiz.after(INTERVALO_DA_LEITURA, self.olhar_leitura)

    def olhar_leitura(self):
        self.agendamento = None
        resultado = self.leitura
        if resultado is None:
            return
        if not resultado.get("pronto"):
            self.agendamento = self.app.raiz.after(INTERVALO_DA_LEITURA, self.olhar_leitura)
            return
        self.terminar_leitura(resultado)

    def terminar_leitura(self, resultado):
        if resultado["numero"] != self.numero_da_leitura:
            return                          # uma leitura cancelada: o resultado não vale mais
        self.lendo = False
        self.leitura = None
        if "erro" in resultado:
            self.erro = resultado["erro"]
            self.mostrar_escolha()
            return
        self.importado = resultado["importado"]
        self.mostrar_conferencia()

    def cancelar_leitura(self):
        self.numero_da_leitura += 1         # a leitura em andamento vai ser ignorada quando terminar
        self.lendo = False
        self.leitura = None
        self.mostrar_escolha()

    # ------------------------------------------------------------------
    # Etapas 2 e 3: conferir e escolher o que fazer
    # ------------------------------------------------------------------

    def mostrar_conferencia(self, escolhas=None):
        self.etapa = 2
        self.etapas.mudar(1)
        corpo = self.novo_corpo()
        corpo.columnconfigure(0, weight=1)
        corpo.rowconfigure(0, weight=1)
        self.painel = PainelDeConferencia(corpo, self.app, self.importado, escolhas, ao_mudar=self.atualizar_status)
        self.painel.quadro.grid(row=0, column=0, sticky="nsew")

        # O rodapé: voltar à etapa 1, a busca e as duas saídas (editar ou visualizar)
        rodape = ttk.Frame(corpo, style="Painel.TFrame", padding=(14, 10, 14, 10))
        rodape.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        rodape.columnconfigure(1, weight=1)
        Botao(rodape, self.app, "Outro arquivo", icone="seta_esquerda", papel="neutro",
              comando=self.voltar_para_a_escolha, fundo=self.tema["superficie"],
              dica="Volta para a etapa 1 e escolhe outro arquivo").grid(row=0, column=0, rowspan=2, sticky="w",
                                                                         padx=(0, 18))
        linha = ttk.Frame(rodape, style="Cartao.TFrame")
        linha.grid(row=0, column=1, sticky="w")
        ttk.Label(linha, text="E agora?", style="TituloDoPainel.TLabel").pack(side="left", padx=(0, 12))
        ttk.Label(linha, text="Busca:", style="Cartao.TLabel").pack(side="left", padx=(0, 6))
        caixa = ttk.Combobox(linha, textvariable=self.variavel_da_busca, values=algoritmos.nomes(), state="readonly",
                             width=24, font=self.fontes["texto"])
        Dica(caixa, "A busca que a visualização vai mostrar (dá para trocar depois, lá dentro)")
        caixa.pack(side="left")
        caixa.bind("<<ComboboxSelected>>", lambda evento: self.atualizar_status())
        self.rotulo_status = ttk.Label(rodape, style="CartaoSuave.TLabel", justify="left")
        self.rotulo_status.grid(row=1, column=1, sticky="w", pady=(4, 0))
        rodape.bind("<Configure>", self.ajustar_quebra_do_status)
        self.botao_editar = Botao(rodape, self.app, "Editar grafo", icone="lapis", papel="info", tamanho="grande",
                                  subtitulo="ajustar no editor", comando=self.editar, fundo=self.tema["superficie"],
                                  dica="Abre o editor com este grafo (o grafo de antes fica no Ctrl+Z)")
        self.botao_editar.grid(row=0, column=2, rowspan=2, sticky="e", padx=(12, 8))
        self.botao_visualizar = Botao(rodape, self.app, "Visualizar grafo", icone="play", papel="principal",
                                      tamanho="grande", subtitulo="ver a busca rodando", comando=self.visualizar,
                                      fundo=self.tema["superficie"], dica="Abre a visualização com a busca escolhida (Enter)")
        self.botao_visualizar.grid(row=0, column=3, rowspan=2, sticky="e")
        self.app.raiz.bind("<Return>", lambda evento: self.visualizar())
        self.atualizar_status()

    # O texto do status quebra a linha no espaço que sobra entre os botões
    def ajustar_quebra_do_status(self, evento):
        ocupado = self.botao_editar.winfo_width() + self.botao_visualizar.winfo_width() + round(260 * self.app.zoom)
        self.rotulo_status.configure(wraplength=max(240, evento.width - ocupado))

    # O grafo com as escolhas da conferência e a busca escolhida embaixo
    def grafo_para_abrir(self):
        grafo = self.painel.grafo_escolhido()
        chave = algoritmos.chave_pelo_nome(self.variavel_da_busca.get())
        grafo["algoritmo"] = chave
        if algoritmos.algoritmo(chave)["usa_limite"] and grafo.get("limite") is None:
            grafo["limite"] = 3                 # o mesmo limite que o editor sugere
        return grafo

    # Embaixo da busca: se ela já pode rodar neste grafo, ou o que falta (a visualização ajuda a resolver)
    def atualizar_status(self):
        if self.painel is None:
            return
        grafo = self.grafo_para_abrir()
        if not grafo["vertices"]:
            self.rotulo_status.configure(text="O arquivo não tem nenhum vértice: escolha outro arquivo.",
                                         style="Erro.TLabel")
            self.botao_visualizar.configurar(habilitado=False)
            self.botao_editar.configurar(habilitado=False)
            return
        self.botao_visualizar.configurar(habilitado=True)
        self.botao_editar.configurar(habilitado=True)
        problemas, avisos = algoritmos.conferir(grafo["algoritmo"], grafo["vertices"], grafo["arestas"],
                                                grafo["direcionado"], grafo["inicio"], grafo["destino"],
                                                grafo["heuristica"], grafo.get("limite"), grafo["ordenar"])
        if problemas:
            texto = "Falta algo para esta busca: " + problemas[0] + " A visualização mostra onde resolver."
            self.rotulo_status.configure(text=texto, style="Erro.TLabel")
        elif avisos:
            self.rotulo_status.configure(text="Pronto para visualizar. " + avisos[0], style="CartaoSuave.TLabel")
        else:
            self.rotulo_status.configure(text="Pronto para visualizar.", style="Sucesso.TLabel")

    # O texto que aparece embaixo, no editor ou na visualização
    def aviso_do_importado(self, grafo):
        texto = (f"Importado de {self.importado['fonte']}: "
                 f"{entrada.resumo(grafo['vertices'], grafo['arestas'], grafo['direcionado'])}.")
        if self.importado["conferir"]:
            texto += " Confira os vértices e as arestas: o reconhecimento pode errar."
        if self.app.ultimo_editor is not None:
            texto += " Ctrl+Z volta para o grafo de antes."
        return texto

    def valores_do_editor(self, grafo):
        return valores_para_abrir(self.app, grafo, self.importado["nome"] or "Grafo importado",
                                  self.aviso_do_importado(grafo), igual_ao_arquivo=False)

    def editar(self):
        grafo = self.grafo_para_abrir()
        if not grafo["vertices"]:
            return
        self.app.mostrar_editor(self.valores_do_editor(grafo))

    # Vai direto para a visualização (mesmo se a busca ainda não puder rodar: lá dentro, as partes
    # explicam o problema e levam a quem resolve, por exemplo a parte Pesos para sortear os pesos)
    def visualizar(self):
        grafo = self.grafo_para_abrir()
        if not grafo["vertices"]:
            return
        valores = self.valores_do_editor(grafo)
        # O editor passa a ter o grafo importado ("Continuar no editor" abre ele, com o de antes no Ctrl+Z)
        self.app.ultimo_editor = valores
        titulo = self.importado["nome"] or "Grafo importado"
        self.app.visualizar(configuracao_da_visualizacao(grafo, titulo, valores))

    # ------------------------------------------------------------------
    # Voltar
    # ------------------------------------------------------------------

    def voltar_para_a_etapa(self, indice):
        if indice == 0:
            self.voltar_para_a_escolha()

    def voltar_para_a_escolha(self):
        self.erro = None
        self.mostrar_escolha()

    def voltar_ao_inicio(self):
        self.app.mostrar_inicio()

    # ------------------------------------------------------------------
    # O que toda tela tem (o aplicativo chama ao trocar o tema, mudar o zoom e trocar de tela)
    # ------------------------------------------------------------------

    def estado_atual(self):
        escolhas = None
        if self.painel is not None:
            escolhas = self.painel.escolhas()
        return {"etapa": self.etapa, "caminho": self.caminho, "importado": self.importado, "erro": self.erro,
                "escolhas": escolhas, "busca": self.variavel_da_busca.get(), "lendo": self.lendo}

    def reconstruir(self):
        self.app.mostrar_importacao(self.estado_atual())

    def redesenhar(self):
        redesenhar_componentes(self.quadro)
        if self.etapa == 1:
            self.desenhar_zona()
        elif self.painel is not None:
            self.painel.desenhar_previa()

    def parar_animacoes(self):
        if self.agendamento is not None:
            self.app.raiz.after_cancel(self.agendamento)
            self.agendamento = None
        barra = getattr(self, "barra_de_leitura", None)
        if barra is not None:
            try:
                barra.stop()
            except tk.TclError:
                pass

    def destruir(self):
        self.numero_da_leitura += 1         # uma leitura em andamento é esquecida
        self.parar_animacoes()
        for tecla in ("<Control-o>", "<Control-O>", "<Return>"):
            self.app.raiz.unbind(tecla)
        self.quadro.destroy()
