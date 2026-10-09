# O aplicativo: a janela principal do Tkinter e o que vale para todas as telas
# (tema, fontes, zoom, tela cheia e ícone). Ele troca entre as telas:
#   1. TelaInicial        -> a escolha da busca (com um exemplo pronto ou o grafo da pessoa)
#   2. EditorDoGrafo      -> monta o grafo e escolhe as opções da busca
#   3. TelaDaVisualizacao -> a visualização por partes (o grafo, as matrizes, o passo a passo, o linha a
#                            linha, a comparação de códigos e o resultado)
#   4. TelaDeImportacao   -> traz um grafo desenhado em outro programa, em etapas
#   5. TelaDoBosco        -> abre um arquivo .bosco (a visualização salva como estava)
# O zoom (o tamanho das letras) muda com Ctrl + roda do mouse, como no navegador, ou com Ctrl + e Ctrl −.

import sys
import tkinter as tk
from tkinter import font as tkfont

import caminhos
from visual import tema as temas
from visual.codigo import BOSCOGRAPH
from visual.editor import EditorDoGrafo
from visual.inicio import TelaInicial
from visual.tela_bosco import TelaDoBosco
from visual.tela_importar import TelaDeImportacao
from visual.visualizacao import TelaDaVisualizacao

NOME_DO_PROGRAMA = caminhos.NOME_DO_PROGRAMA
ARQUIVO_DO_ICONE = caminhos.pasta_dos_recursos() / "visual" / "icone.png"

# Tamanho base de cada fonte; o zoom multiplica todos de uma vez
TAMANHOS_DAS_FONTES = {
    "texto": 10,
    "negrito": 10,
    "pequena": 9,
    "titulo": 17,
    "mensagem": 14,
    "destaque": 12,             # títulos dos cartões grandes (os dois caminhos da tela inicial)
    "explicacao": 11,
    "codigo": 10,
    "relogio": 22,
}


# Ajustes que só existem no Windows (nos outros sistemas o try/except simplesmente ignora):
# 1. Nitidez: com a tela em escala (125%, 150%...), sem isto a janela aparece borrada.
#    É o mesmo ajuste que o IDLE (o editor que vem com o Python) faz.
# 2. Identidade própria: sem isto, a barra de tarefas agrupa a janela com o ícone do Python.
def ajustar_para_o_windows():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(NOME_DO_PROGRAMA)
    except Exception:
        pass


class Aplicativo:
    def __init__(self, montar_passos):
        self.montar_passos = montar_passos      # a função do boscograph.py que calcula os passos
        ajustar_para_o_windows()
        self.raiz = tk.Tk()
        self.raiz.title(NOME_DO_PROGRAMA)
        self.colocar_icone()
        self.tema = temas.CLARO
        self.zoom = 1.0
        self.configuracao = None                # a última configuração visualizada
        self.tela = None                        # a tela que está aparecendo agora
        self.dialogo = None                     # o diálogo aberto (renomear, editar texto...), se houver
        self.ultimo_editor = None               # como o editor estava da última vez (para voltar a ele igual)
        # Escolhas da visualização que valem até fechar o programa (mesmo trocando de grafo ou de tema):
        #   velocidade        -> a posição do botão marcado (2 = "2×")
        #   nomes/pesos       -> se os nomes e os pesos das arestas aparecem no desenho
        #   modo              -> "passo" (passo a passo) ou "linha" (linha a linha)
        #   linguagem         -> o código mostrado; comparar -> a segunda linguagem (None = sem comparação)
        #   codigo, legenda, explicacao -> se o painel de código, a legenda e a explicação aparecem
        #   parte             -> a parte da visualização que estava aberta; partes -> as escolhas de cada uma
        self.preferencias = {"velocidade": 2, "nomes_das_arestas": True, "pesos_das_arestas": True,
                             "linguagem": BOSCOGRAPH, "comparar": None, "parte": None, "partes": {}}
        # O zoom pela roda do mouse: os "dentes" da roda são somados e aplicados de uma vez (girar rápido
        # não redesenha a tela a cada dente)
        self.roda_acumulada = 0
        self.zoom_pendente = 0
        self.agendamento_do_zoom = None
        self.aviso_de_zoom = None               # o "Letras: 120%" que aparece em cima por um instante
        self.agendamento_do_aviso = None

        self.criar_fontes()
        self.posicionar_janela()
        temas.aplicar_estilo(self.raiz, self.tema, self.fontes)
        self.ligar_atalhos_gerais()
        self.mostrar_inicio()

    # O ícone da janela e da barra de tarefas (se o arquivo sumir, o programa funciona sem ele)
    def colocar_icone(self):
        try:
            self.icone = tk.PhotoImage(file=str(ARQUIVO_DO_ICONE))
            self.raiz.iconphoto(True, self.icone)
        except tk.TclError:
            self.icone = None

    # Todas as fontes ficam num dicionário: mudar o tamanho de uma muda em todos os lugares que a usam
    def criar_fontes(self):
        self.fontes = {}
        for nome in TAMANHOS_DAS_FONTES:
            familia = "Segoe UI"
            if nome == "codigo" or nome == "relogio":
                familia = "Consolas"
            peso = "normal"
            if nome in ("negrito", "titulo", "mensagem", "destaque", "relogio"):
                peso = "bold"
            self.fontes[nome] = tkfont.Font(root=self.raiz, family=familia,
                                            size=TAMANHOS_DAS_FONTES[nome], weight=peso)

    # A janela abre centralizada, ocupando quase a tela toda (proporcional ao tamanho da tela)
    def posicionar_janela(self):
        largura_tela = self.raiz.winfo_screenwidth()
        altura_tela = self.raiz.winfo_screenheight()
        largura = int(largura_tela * 0.9)
        altura = int(altura_tela * 0.85)
        x = (largura_tela - largura) // 2
        y = max(0, (altura_tela - altura) // 2 - 20)
        self.raiz.geometry(f"{largura}x{altura}+{x}+{y}")
        self.raiz.minsize(960, 600)

    def ligar_atalhos_gerais(self):
        self.raiz.bind("<Control-plus>", self.aumentar_zoom)
        self.raiz.bind("<Control-equal>", self.aumentar_zoom)
        self.raiz.bind("<Control-KP_Add>", self.aumentar_zoom)          # + do teclado numérico
        self.raiz.bind("<Control-minus>", self.diminuir_zoom)
        self.raiz.bind("<Control-KP_Subtract>", self.diminuir_zoom)     # - do teclado numérico
        self.raiz.bind("<Control-0>", self.zoom_normal)
        self.raiz.bind("<F11>", self.alternar_tela_cheia)
        self.raiz.bind("<Escape>", self.sair_da_tela_cheia)
        self.ligar_zoom_pela_roda()

    # Ctrl + roda do mouse: letras maiores ou menores, em qualquer lugar da janela.
    # O bind_all vale para todos os componentes. Mas as caixas que rolam com a roda (texto, tabelas,
    # listas, desenhos) têm a rolagem ligada na "classe" delas, que roda antes do bind_all: por isso a
    # mesma ligação é feita nessas classes, e o "break" no fim impede que a caixa role junto.
    # No Windows e no macOS a roda é o evento <MouseWheel>; no Linux, os botões 4 (para cima) e 5 (para baixo).
    def ligar_zoom_pela_roda(self):
        for evento in ("<Control-MouseWheel>", "<Control-Button-4>", "<Control-Button-5>"):
            self.raiz.bind_all(evento, self.roda_com_ctrl)
            for classe in ("Text", "Treeview", "Listbox", "Canvas", "TCombobox", "TScrollbar", "Scrollbar",
                           "TEntry", "Entry", "TSpinbox", "Spinbox"):
                self.raiz.bind_class(classe, evento, self.roda_com_ctrl)

    # ------------------------------------------------------------------
    # Troca de telas
    # ------------------------------------------------------------------

    # Fecha a tela atual antes de abrir a próxima (duas nunca ficam abertas juntas).
    # O editor deixa guardado como estava: voltar para ele (da tela inicial) não perde nada.
    def fechar_tela_atual(self):
        if self.tela is not None:
            if isinstance(self.tela, EditorDoGrafo):
                self.ultimo_editor = self.tela.valores_atuais()
            self.tela.destruir()
            self.tela = None

    def mostrar_inicio(self):
        self.fechar_tela_atual()
        self.raiz.title(NOME_DO_PROGRAMA)
        self.tela = TelaInicial(self)

    # valores: o estado do editor (None = como ele estava da última vez, ou o modelo padrão).
    # busca: a busca escolhida na tela inicial ("Montar meu grafo"): o editor abre na primeira etapa.
    def mostrar_editor(self, valores=None, busca=None):
        if valores is None:
            valores = self.ultimo_editor
        self.fechar_tela_atual()
        self.raiz.title(NOME_DO_PROGRAMA)
        self.tela = EditorDoGrafo(self, valores)
        if busca is not None:
            self.tela.escolher_busca(busca)
            self.tela.mostrar_etapa(0, animar=False)

    # estado: como a tela de importação estava (na troca de tema); None = começa na etapa 1
    def mostrar_importacao(self, estado=None):
        self.fechar_tela_atual()
        self.raiz.title(f"{NOME_DO_PROGRAMA} — Importar um desenho")
        self.tela = TelaDeImportacao(self, estado)

    # caminho: um arquivo já escolhido (aparece a prévia dele); erro: o problema de um arquivo que não abriu
    def mostrar_bosco(self, caminho=None, erro=None):
        self.fechar_tela_atual()
        self.raiz.title(f"{NOME_DO_PROGRAMA} — Abrir arquivo .bosco")
        self.tela = TelaDoBosco(self, caminho, erro)

    # estado_da_tela: como a visualização estava (vem do .bosco ou da troca de tema); None = começo
    def mostrar_visualizacao(self, configuracao, estado_da_tela=None):
        self.fechar_tela_atual()
        self.configuracao = configuracao
        self.raiz.title(f"{NOME_DO_PROGRAMA} — {configuracao['titulo']}")
        self.tela = TelaDaVisualizacao(self, configuracao, estado_da_tela)

    # Chamado pelo editor quando o usuário clica em "Visualizar" (e pelo "Ver exemplo" da tela inicial).
    # Um grafo novo começa do começo: as escolhas das partes (posição, célula escolhida...) são esquecidas,
    # mas os painéis ligados e a parte aberta continuam como a pessoa deixou.
    def visualizar(self, configuracao, estado_da_tela=None):
        self.fechar_tela_atual()        # primeiro: ao fechar, a tela guarda as escolhas dela
        for chave in list(self.preferencias["partes"]):
            escolhas = self.preferencias["partes"][chave]
            guardar = {}
            for nome in ("mostrar", "recolhidos", "modo"):
                if nome in escolhas:
                    guardar[nome] = escolhas[nome]
            self.preferencias["partes"][chave] = guardar
        # Cada grafo abre com a arrumação dele ("como no arquivo" quando veio de um desenho importado)
        self.preferencias["arrumacao"] = configuracao.get("arrumacao") or "circulo"
        self.mostrar_visualizacao(configuracao, estado_da_tela)

    def voltar_para_o_editor(self):
        self.mostrar_editor(self.configuracao["valores"])

    # ------------------------------------------------------------------
    # Tema, zoom e tela cheia (valem para as duas telas)
    # ------------------------------------------------------------------

    def trocar_tema(self, evento=None):
        if self.tema is temas.CLARO:
            self.definir_tema("escuro")
        else:
            self.definir_tema("claro")

    def definir_tema(self, nome):
        if nome == "escuro":
            self.tema = temas.ESCURO
        else:
            self.tema = temas.CLARO
        temas.aplicar_estilo(self.raiz, self.tema, self.fontes)
        self.tela.reconstruir()     # a tela se recria com as cores novas, sem perder onde estava

    def aumentar_zoom(self, evento=None):
        self.mudar_zoom(self.zoom + 0.1)

    def diminuir_zoom(self, evento=None):
        self.mudar_zoom(self.zoom - 0.1)

    def zoom_normal(self, evento=None):
        self.mudar_zoom(1.0)

    def mudar_zoom(self, novo_zoom):
        antes = self.zoom
        self.mudar_zoom_sem_redesenhar(novo_zoom)
        if self.zoom != antes:              # no limite (70% ou 200%) nada muda: não precisa redesenhar
            self.tela.redesenhar()
        self.mostrar_aviso_de_zoom()

    # Um giro da roda com o Ctrl apertado. No Windows, cada "dente" da roda vale 120 no delta (os touchpads
    # mandam pedaços menores, que vão sendo somados); no macOS, cada evento é um dente; no Linux, o botão
    # 4 é para cima e o 5 é para baixo.
    def roda_com_ctrl(self, evento):
        if evento.num == 4:
            passos = 1
        elif evento.num == 5:
            passos = -1
        elif sys.platform == "darwin":
            passos = 0
            if evento.delta > 0:
                passos = 1
            elif evento.delta < 0:
                passos = -1
        else:
            self.roda_acumulada += evento.delta
            passos = int(self.roda_acumulada / 120)
            self.roda_acumulada -= passos * 120
        if passos != 0:
            self.zoom_pendente += passos
            if self.agendamento_do_zoom is None:
                self.agendamento_do_zoom = self.raiz.after(60, self.aplicar_zoom_da_roda)
        return "break"

    def aplicar_zoom_da_roda(self):
        self.agendamento_do_zoom = None
        passos = self.zoom_pendente
        self.zoom_pendente = 0
        if passos != 0:
            self.mudar_zoom(self.zoom + 0.1 * passos)

    # "Letras: 120%" no alto da janela por um instante, para a pessoa saber o que o Ctrl + roda fez
    def mostrar_aviso_de_zoom(self):
        texto = f"Letras: {round(self.zoom * 100)}%   (Ctrl + 0 volta para 100%)"
        if self.aviso_de_zoom is None or not self.aviso_de_zoom.winfo_exists():
            self.aviso_de_zoom = tk.Label(self.raiz, padx=14, pady=5, relief="solid", borderwidth=1)
        self.aviso_de_zoom.configure(text=texto, font=self.fontes["negrito"], bg=self.tema["texto"],
                                     fg=self.tema["superficie"])
        self.aviso_de_zoom.place(relx=0.5, y=10, anchor="n")
        self.aviso_de_zoom.lift()
        if self.agendamento_do_aviso is not None:
            self.raiz.after_cancel(self.agendamento_do_aviso)
        self.agendamento_do_aviso = self.raiz.after(1400, self.esconder_aviso_de_zoom)

    def esconder_aviso_de_zoom(self):
        self.agendamento_do_aviso = None
        if self.aviso_de_zoom is not None and self.aviso_de_zoom.winfo_exists():
            self.aviso_de_zoom.place_forget()

    # Só muda o tamanho das letras (o arquivo .bosco usa antes de abrir a tela nova)
    def mudar_zoom_sem_redesenhar(self, novo_zoom):
        self.zoom = round(max(0.7, min(novo_zoom, 2.0)), 2)
        for nome in self.fontes:
            self.fontes[nome].configure(size=round(TAMANHOS_DAS_FONTES[nome] * self.zoom))
        temas.aplicar_estilo(self.raiz, self.tema, self.fontes)     # a altura das linhas das tabelas depende da fonte

    def alternar_tela_cheia(self, evento=None):
        cheia = int(self.raiz.attributes("-fullscreen")) == 1
        self.raiz.attributes("-fullscreen", not cheia)

    def sair_da_tela_cheia(self, evento=None):
        self.raiz.attributes("-fullscreen", False)

    def abrir(self):
        self.raiz.mainloop()
