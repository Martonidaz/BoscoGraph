# Pedaços de tela que as partes da visualização repetem:
#   PainelRecolhivel -> um painel com título que pode ser minimizado (vira uma faixa fina com o nome)
#   BarraDoTocador   -> os botões |◀ ◀ ▶ ▶| , o Play, a linha do tempo e a velocidade
#   Chips            -> a fileira "Mostrar: Estrutura · Tabela · Código..." (cada botão liga ou desliga um painel)

import tkinter as tk
from tkinter import ttk

from visual.dica import Dica

# Velocidades do Play: (passos por segundo, texto do botão). "2×" = 2 passos (ou linhas) por segundo.
VELOCIDADES = [(0.5, "0,5×"), (1, "1×"), (2, "2×"), (4, "4×"), (8, "8×")]
LARGURA_DA_FAIXA = 24


# O texto ao lado dos botões de velocidade ("unidade" = "passo" ou "linha")
def texto_da_velocidade(por_segundo, unidade="passo"):
    if por_segundo < 1:
        return f"1 {unidade} a cada {round(1 / por_segundo)} s"
    if por_segundo == 1:
        return f"1 {unidade} por segundo"
    return f"{por_segundo} {unidade}s por segundo"


class PainelRecolhivel:
    # divisao: o ttk.PanedWindow onde o painel fica; peso: quanto do espaço extra ele ganha.
    # Recolhido, o painel some e no lugar dele fica uma faixa fina com o título (clique para abrir).
    def __init__(self, divisao, app, titulo, peso=1, ao_mudar=None):
        self.divisao = divisao
        self.app = app
        self.tema = app.tema
        self.titulo = titulo
        self.peso = peso
        self.ao_mudar = ao_mudar
        self.recolhido = False
        horizontal = str(divisao.cget("orient")) == "horizontal"
        self.horizontal = horizontal

        self.quadro = ttk.Frame(divisao)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        cabecalho = ttk.Frame(self.quadro)
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        cabecalho.columnconfigure(1, weight=1)
        self.rotulo = ttk.Label(cabecalho, text=titulo, style="Negrito.TLabel")
        self.rotulo.grid(row=0, column=0, sticky="w")
        self.extras = ttk.Frame(cabecalho)          # controles do painel (linguagem, modo...), à direita
        self.extras.grid(row=0, column=1, sticky="e", padx=(8, 4))
        botao = ttk.Button(cabecalho, text="–", width=2, style="Pequeno.TButton", command=self.recolher)
        botao.grid(row=0, column=2, sticky="e")
        Dica(botao, f"Minimizar \"{titulo}\" (a faixa com o nome traz de volta)")
        self.corpo = ttk.Frame(self.quadro)
        self.corpo.grid(row=1, column=0, sticky="nsew")

        # A faixa do painel recolhido: o título escrito de lado (num Canvas, que sabe girar texto)
        if horizontal:
            self.faixa = tk.Canvas(divisao, width=LARGURA_DA_FAIXA, bg=self.tema["superficie"],
                                   highlightthickness=1, highlightbackground=self.tema["borda"], cursor="hand2")
        else:
            self.faixa = tk.Canvas(divisao, height=LARGURA_DA_FAIXA, bg=self.tema["superficie"],
                                   highlightthickness=1, highlightbackground=self.tema["borda"], cursor="hand2")
        self.faixa.bind("<Configure>", self.desenhar_faixa)
        self.faixa.bind("<Button-1>", self.abrir)
        Dica(self.faixa, f"Mostrar \"{titulo}\" de novo")

    def desenhar_faixa(self, evento=None):
        c = self.faixa
        c.delete("all")
        fonte = self.app.fontes["negrito"]
        if self.horizontal:
            c.create_text(LARGURA_DA_FAIXA / 2, 10, text="+", anchor="n", fill=self.tema["acento"], font=fonte)
            c.create_text(LARGURA_DA_FAIXA / 2, 30, text=self.titulo, angle=-90, anchor="w", fill=self.tema["texto"],
                          font=fonte)
        else:
            c.create_text(10, LARGURA_DA_FAIXA / 2, text="+  " + self.titulo, anchor="w", fill=self.tema["texto"],
                          font=fonte)

    # Coloca o painel (ou a faixa, se estiver recolhido) no fim da divisão
    def colocar(self):
        if self.recolhido:
            self.divisao.add(self.faixa, weight=0)
        else:
            self.divisao.add(self.quadro, weight=self.peso)

    def posicao_na_divisao(self, componente):
        panes = [str(pane) for pane in self.divisao.panes()]
        if str(componente) in panes:
            return panes.index(str(componente))
        return None

    def trocar(self, sai, entra, peso):
        posicao = self.posicao_na_divisao(sai)
        if posicao is None:
            return
        self.divisao.forget(sai)
        if posicao >= len(self.divisao.panes()):
            self.divisao.add(entra, weight=peso)
        else:
            self.divisao.insert(posicao, entra, weight=peso)

    def recolher(self, evento=None):
        if self.recolhido:
            return
        self.recolhido = True
        self.trocar(self.quadro, self.faixa, 0)
        if self.ao_mudar:
            self.ao_mudar()

    def abrir(self, evento=None):
        if not self.recolhido:
            return
        self.recolhido = False
        self.trocar(self.faixa, self.quadro, self.peso)
        if self.ao_mudar:
            self.ao_mudar()

    def definir(self, recolhido):
        if recolhido:
            self.recolher()
        else:
            self.abrir()


class BarraDoTocador:
    # ao_ir(posicao): a barra pede para a tela ir para uma posição; a tela responde com atualizar().
    # primeira e ultima: as posições possíveis (o passo -1 = antes de começar)
    def __init__(self, pai, app, ao_ir, unidade="passo"):
        self.app = app
        self.ao_ir = ao_ir
        self.unidade = unidade
        self.primeira = 0
        self.ultima = 0
        self.posicao = 0
        self.tocando = False
        self.agendamento = None
        self.mexendo = False
        self.indice_da_velocidade = tk.IntVar(value=app.preferencias.get("velocidade", 2))

        self.quadro = ttk.Frame(pai)
        self.quadro.columnconfigure(5, weight=1)
        ttk.Button(self.quadro, text="|◀", width=3, command=self.inicio).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(self.quadro, text="◀", width=3, command=self.voltar).grid(row=0, column=1, padx=2)
        self.botao_play = ttk.Button(self.quadro, text="▶ Play", width=9, style="Acento.TButton",
                                     command=self.play_pausa)
        self.botao_play.grid(row=0, column=2, padx=2)
        ttk.Button(self.quadro, text="▶", width=3, command=self.avancar).grid(row=0, column=3, padx=2)
        ttk.Button(self.quadro, text="▶|", width=3, command=self.fim).grid(row=0, column=4, padx=(2, 10))
        self.linha_do_tempo = ttk.Scale(self.quadro, from_=0, to=1, orient="horizontal",
                                        command=self.ao_mover_linha_do_tempo)
        self.linha_do_tempo.grid(row=0, column=5, sticky="ew")
        self.rotulo_posicao = ttk.Label(self.quadro, style="Suave.TLabel", width=16, anchor="e")
        self.rotulo_posicao.grid(row=0, column=6, padx=(8, 10))
        velocidades = ttk.Frame(self.quadro)
        velocidades.grid(row=0, column=7)
        for indice in range(len(VELOCIDADES)):
            botao = ttk.Radiobutton(velocidades, text=VELOCIDADES[indice][1], value=indice,
                                    variable=self.indice_da_velocidade, style="Segmento.Toolbutton", width=4,
                                    command=self.ao_mudar_velocidade)
            botao.pack(side="left")
            Dica(botao, lambda indice=indice: "Velocidade do Play: " + texto_da_velocidade(VELOCIDADES[indice][0],
                                                                                         self.unidade))
        self.ao_mudar_velocidade()

    def configurar(self, primeira, ultima, posicao, unidade=None):
        if unidade is not None:
            self.unidade = unidade
        self.primeira = primeira
        self.ultima = max(primeira, ultima)
        self.linha_do_tempo.configure(from_=self.primeira, to=self.ultima)
        self.atualizar(posicao)
        self.ao_mudar_velocidade()

    # A tela mudou de posição: a linha do tempo e o contador acompanham
    def atualizar(self, posicao, texto=None):
        self.posicao = posicao
        self.mexendo = True                 # o set() abaixo não pode chamar ao_ir de novo
        self.linha_do_tempo.set(posicao)
        self.mexendo = False
        if texto is None:
            total = self.ultima - self.primeira
            texto = f"{self.unidade} {posicao - self.primeira} de {total}"
        self.rotulo_posicao.configure(text=texto)

    def ao_mover_linha_do_tempo(self, valor):
        if self.mexendo:
            return
        self.ao_ir(round(float(valor)))

    def avancar(self, evento=None):
        self.ao_ir(min(self.posicao + 1, self.ultima))

    def voltar(self, evento=None):
        self.ao_ir(max(self.posicao - 1, self.primeira))

    def inicio(self, evento=None):
        self.pausar()
        self.ao_ir(self.primeira)

    def fim(self, evento=None):
        self.pausar()
        self.ao_ir(self.ultima)

    def play_pausa(self, evento=None):
        if self.tocando:
            self.pausar()
            return
        if self.posicao >= self.ultima:
            self.ao_ir(self.primeira)       # no fim, o Play recomeça do início
        self.tocando = True
        self.botao_play.configure(text="|| Pausar")
        self.tocar()

    def pausar(self):
        self.tocando = False
        self.botao_play.configure(text="▶ Play")
        if self.agendamento is not None:
            self.app.raiz.after_cancel(self.agendamento)
            self.agendamento = None

    # Avança um e agenda o próximo (2 por segundo = um a cada 500 milissegundos)
    def tocar(self):
        self.agendamento = None
        if not self.tocando:
            return
        if self.posicao >= self.ultima:
            self.pausar()
            return
        self.avancar()
        por_segundo = VELOCIDADES[self.indice_da_velocidade.get()][0]
        self.agendamento = self.app.raiz.after(round(1000 / por_segundo), self.tocar)

    def ao_mudar_velocidade(self):
        self.app.preferencias["velocidade"] = self.indice_da_velocidade.get()

    def mais_rapido(self, evento=None):
        self.indice_da_velocidade.set(min(self.indice_da_velocidade.get() + 1, len(VELOCIDADES) - 1))
        self.ao_mudar_velocidade()

    def mais_devagar(self, evento=None):
        self.indice_da_velocidade.set(max(self.indice_da_velocidade.get() - 1, 0))
        self.ao_mudar_velocidade()

    def destruir(self):
        self.pausar()


class Chips:
    # opcoes: [(chave, texto, dica), ...]; valores: {chave: True/False}; ao_mudar(chave) a cada clique
    def __init__(self, pai, opcoes, valores, ao_mudar, titulo="Mostrar:"):
        self.quadro = ttk.Frame(pai)
        self.variaveis = {}
        ttk.Label(self.quadro, text=titulo, style="Suave.TLabel").pack(side="left", padx=(0, 6))
        for chave, texto, dica in opcoes:
            variavel = tk.BooleanVar(value=valores.get(chave, False))
            self.variaveis[chave] = variavel
            botao = ttk.Checkbutton(self.quadro, text=texto, variable=variavel, style="Chip.Toolbutton",
                                    command=lambda chave=chave: ao_mudar(chave))
            botao.pack(side="left", padx=(0, 4))
            if dica:
                Dica(botao, dica)

    def valor(self, chave):
        return self.variaveis[chave].get()

    def definir(self, chave, valor):
        self.variaveis[chave].set(valor)
