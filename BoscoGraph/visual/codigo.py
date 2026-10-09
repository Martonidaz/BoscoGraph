# O painel "Código" da visualização: mostra o código da busca e destaca a linha do momento.
#
# Duas fontes de código:
#   - "Código do BoscoGraph": os arquivos .py do próprio programa (classes/...), que fazem a busca E
#     anotam cada passo para a tela. A linha destacada é a que fez o passo (veja "trechos" em perfis.py).
#   - O programa da busca em Pseudocódigo, Python, Java, C, C++ e JavaScript: o arquivo inteiro, o
#     mesmo que "Exportar > Código-fonte" grava (o cabeçalho, o código de estudo da busca, o grafo e a
#     chamada). No modo passo a passo, a linha destacada é a que faz o passo; no modo linha a linha, o
#     Python RODA, desde a primeira linha, e a linha destacada é a próxima que ele vai rodar. Nas outras
#     linguagens, a linha destacada é a que tem o mesmo RÓTULO (veja estudo/estrutura.py): a linha que
#     faz o mesmo que a do Python.
#
# "Comparar com" divide o painel em dois, cada um com a sua linguagem: um em cima do outro, ou um do
# lado do outro (orientacao="horizontal", na parte "Comparar códigos" da tela por partes).
# Um clique numa linha avisa a tela (ao_clicar_na_linha): no linha a linha, é assim que a pessoa
# escolhe de que linha quer partir.

import re
import tkinter as tk
from tkinter import ttk

import caminhos
import estudo
from visual.dica import Dica

# Pasta de onde os arquivos do BoscoGraph são lidos: a do projeto, ou a pasta interna do executável
# (o BoscoGraph.spec manda os .py junto com o executável, como dados, só para este painel)
PASTA_DO_PROJETO = caminhos.pasta_dos_recursos()

BOSCOGRAPH = "boscograph"           # a "linguagem" que mostra o código do próprio programa
SEM_COMPARACAO = "(nenhuma)"

# As escolhas das caixas de linguagem: (chave, texto)
ESCOLHAS = [(BOSCOGRAPH, "Código do BoscoGraph")]
for _informacoes in estudo.LINGUAGENS:
    ESCOLHAS.append((_informacoes["chave"], _informacoes["nome"]))

PALAVRAS_DO_BOSCOGRAPH = ["def", "class", "for", "in", "if", "elif", "else", "return", "import", "from", "while",
                          "and", "or", "not", "None", "True", "False", "continue", "break", "try", "except",
                          "raise", "self", "lambda", "with", "as", "pass"]

MARCA_DA_PROXIMA = "▶"              # na margem: a próxima linha a rodar (ou a linha do passo)
MARCA_DA_ANTERIOR = "·"             # na margem: a linha que acabou de rodar (só no modo linha a linha)


def texto_da_escolha(chave):
    for chave_da_escolha, texto in ESCOLHAS:
        if chave_da_escolha == chave:
            return texto
    return SEM_COMPARACAO


def chave_da_escolha(texto):
    for chave, texto_da_lista in ESCOLHAS:
        if texto_da_lista == texto:
            return chave
    return None


# Posição em que começa o comentário da linha (fora de aspas); -1 se não houver
def inicio_do_comentario(linha, marcador, aspas):
    dentro = None                       # o caractere de aspas aberto agora (None = fora de aspas)
    i = 0
    while i < len(linha):
        caractere = linha[i]
        if dentro is None and caractere in aspas:
            dentro = caractere
        elif dentro is not None and caractere == dentro:
            dentro = None
        elif dentro is None and linha.startswith(marcador, i):
            return i
        i += 1
    return -1


# Lê os arquivos do BoscoGraph e descobre em que linha está cada trecho (veja "trechos" em perfis.py).
# Se alguém mudar o código e um trecho sumir, o programa avisa na hora (e o testes.py também).
# Devolve: arquivo -> lista de linhas, e chave do trecho -> número da linha (a 1ª linha é 1)
def localizar_trechos(trechos):
    linhas_do_arquivo = {}
    linha_do_trecho = {}
    for chave in trechos:
        arquivo, a_partir_de, trecho = trechos[chave]
        if arquivo not in linhas_do_arquivo:
            texto = (PASTA_DO_PROJETO / arquivo).read_text(encoding="utf-8")
            linhas_do_arquivo[arquivo] = texto.split("\n")

        linhas = linhas_do_arquivo[arquivo]
        procurando = a_partir_de is None     # sem "a partir de": procura desde a 1ª linha
        numero = None
        for i in range(len(linhas)):
            if not procurando and a_partir_de in linhas[i]:
                procurando = True
            if procurando and trecho in linhas[i]:
                numero = i + 1
                break
        if numero is None:
            raise ValueError(f"O trecho '{trecho}' não foi encontrado em {arquivo}")
        linha_do_trecho[chave] = numero
    return linhas_do_arquivo, linha_do_trecho


# As regras de cor de uma linguagem: as palavras reservadas (uma expressão regular só), as aspas e
# o começo do comentário
def regras_de_cor(chave):
    if chave == BOSCOGRAPH:
        palavras, aspas, comentario = PALAVRAS_DO_BOSCOGRAPH, "\"'", "#"
    else:
        informacoes = estudo.linguagem(chave)
        palavras, aspas, comentario = informacoes["palavras"], informacoes["aspas"], informacoes["comentario"]
    # (?<![\w#]) e (?![\w]): a palavra inteira ("for" não acende dentro de "format")
    alternativas = "|".join(re.escape(palavra) for palavra in sorted(palavras, key=len, reverse=True))
    expressao_das_palavras = re.compile(r"(?<![\w#])(?:" + alternativas + r")(?!\w)")
    expressoes_das_aspas = []
    for aspa in aspas:
        expressoes_das_aspas.append(re.compile(re.escape(aspa) + "[^" + re.escape(aspa) + "]*" + re.escape(aspa)))
    return expressao_das_palavras, expressoes_das_aspas, comentario, aspas


# Uma caixa de código: título, texto com os números das linhas e as marcas na margem
class VisaoDeCodigo:
    def __init__(self, pai, tema, fontes):
        self.tema = tema
        self.fontes = fontes
        self.quadro = ttk.Frame(pai)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        self.titulo = ttk.Label(self.quadro, style="Suave.TLabel")
        self.titulo.grid(row=0, column=0, columnspan=2, sticky="w")
        self.texto = tk.Text(self.quadro, height=6, wrap="none", font=fontes["codigo"],
                             bg=tema["codigo_fundo"], fg=tema["codigo_texto"], relief="flat",
                             highlightthickness=0, padx=4, pady=4, state="disabled", cursor="arrow",
                             takefocus=False)
        self.texto.grid(row=1, column=0, sticky="nsew")
        rolagem_vertical = ttk.Scrollbar(self.quadro, orient="vertical", command=self.texto.yview)
        rolagem_vertical.grid(row=1, column=1, sticky="ns")
        rolagem_horizontal = ttk.Scrollbar(self.quadro, orient="horizontal", command=self.texto.xview)
        rolagem_horizontal.grid(row=2, column=0, sticky="ew")
        self.texto.configure(yscrollcommand=rolagem_vertical.set, xscrollcommand=rolagem_horizontal.set)

        self.texto.tag_configure("numero", foreground=tema["codigo_numero"])
        self.texto.tag_configure("marca", foreground=tema["destaque"])
        self.texto.tag_configure("palavra", foreground=tema["codigo_palavra"])
        self.texto.tag_configure("string", foreground=tema["codigo_string"])
        self.texto.tag_configure("comentario", foreground=tema["codigo_comentario"])
        self.texto.tag_configure("linha_atual", background=tema["fundo_destaque"])
        self.texto.tag_configure("linha_anterior", background=tema["fundo_anterior"])
        # A linha escolhida com o clique (a cor é a da parte da tela; veja cor_da_escolha)
        self.texto.tag_configure("linha_escolhida", underline=False, borderwidth=1, relief="solid")
        self.texto.tag_raise("comentario")          # o comentário ganha das outras cores
        self.texto.tag_raise("marca")
        self.ao_clicar_na_linha = None              # função (número da linha) chamada no clique
        self.texto.bind("<Button-1>", self.clicou)

        self.conteudo = None                # o que está na caixa agora: (linguagem, arquivo)
        self.quantidade_de_linhas = 0
        self.marcadas = []                  # linhas com uma marca na margem (para apagar depois)
        self.linha_em_foco = None           # a linha que tem que ficar visível
        # A caixa mudou de tamanho (a comparação dividiu o painel, a janela cresceu...): rola de novo
        # para a linha em foco continuar visível
        self.texto.bind("<Configure>", self.ao_redimensionar)

    # Coloca um arquivo na caixa, com os números das linhas e as cores da linguagem.
    # Cada linha começa com "  12  ": duas posições para a marca, o número e dois espaços.
    def colocar(self, chave, arquivo, linhas, titulo):
        self.titulo.configure(text=titulo)
        if self.conteudo == (chave, arquivo):
            return
        self.conteudo = (chave, arquivo)
        expressao_das_palavras, expressoes_das_aspas, comentario, aspas = regras_de_cor(chave)
        texto = self.texto
        texto.configure(state="normal")
        texto.delete("1.0", "end")
        largura_do_numero = len(str(len(linhas)))
        for i in range(len(linhas)):
            linha = linhas[i]
            numero_da_linha = i + 1
            prefixo = f"  {numero_da_linha:>{largura_do_numero}}  "
            texto.insert("end", prefixo, "numero")
            texto.insert("end", linha + "\n")
            deslocamento = len(prefixo)     # o código começa depois do número da linha
            for achado in expressao_das_palavras.finditer(linha):
                self.colorir(numero_da_linha, deslocamento + achado.start(), deslocamento + achado.end(), "palavra")
            for expressao in expressoes_das_aspas:
                for achado in expressao.finditer(linha):
                    self.colorir(numero_da_linha, deslocamento + achado.start(), deslocamento + achado.end(),
                                 "string")
            comeco = inicio_do_comentario(linha, comentario, aspas)
            if comeco >= 0:
                self.colorir(numero_da_linha, deslocamento + comeco, deslocamento + len(linha), "comentario")
        texto.configure(state="disabled")
        self.quantidade_de_linhas = len(linhas)
        self.marcadas = []

    def colorir(self, linha, coluna_inicial, coluna_final, cor):
        self.texto.tag_add(cor, f"{linha}.{coluna_inicial}", f"{linha}.{coluna_final}")

    # Destaca as linhas do momento: "atuais" em amarelo (com ▶ na margem) e "anteriores" num tom mais
    # fraco (com ·). Rola a caixa para a primeira linha atual ficar perto do meio.
    def destacar(self, atuais, anteriores=()):
        texto = self.texto
        texto.configure(state="normal")
        texto.tag_remove("linha_atual", "1.0", "end")
        texto.tag_remove("linha_anterior", "1.0", "end")
        for linha in self.marcadas:
            texto.delete(f"{linha}.0", f"{linha}.1")
            texto.insert(f"{linha}.0", " ", "numero")
        self.marcadas = []
        for linha in anteriores:
            if linha not in atuais:
                texto.tag_add("linha_anterior", f"{linha}.0", f"{linha + 1}.0")
                self.marcar(linha, MARCA_DA_ANTERIOR)
        for linha in atuais:
            texto.tag_add("linha_atual", f"{linha}.0", f"{linha + 1}.0")
        if atuais:
            self.marcar(atuais[0], MARCA_DA_PROXIMA)
        texto.configure(state="disabled")
        self.linha_em_foco = None
        if atuais:
            self.linha_em_foco = atuais[0]
        elif anteriores:
            self.linha_em_foco = anteriores[0]
        if self.linha_em_foco is not None:
            self.rolar_para(self.linha_em_foco)

    def ao_redimensionar(self, evento=None):
        if self.linha_em_foco is not None:
            self.rolar_para(self.linha_em_foco)

    # O clique numa linha: descobre o número dela ("@x,y" = o caractere debaixo do mouse)
    def clicou(self, evento):
        if self.ao_clicar_na_linha is None or self.quantidade_de_linhas == 0:
            return
        numero = int(self.texto.index(f"@{evento.x},{evento.y}").split(".")[0])
        if 1 <= numero <= self.quantidade_de_linhas:
            self.ao_clicar_na_linha(numero)

    # Marca as linhas escolhidas (com uma moldura na cor dada); [] tira a marca
    def escolher(self, linhas, cor=None):
        self.texto.tag_remove("linha_escolhida", "1.0", "end")
        if cor is not None:
            self.texto.tag_configure("linha_escolhida", background=cor)
        for linha in linhas:
            self.texto.tag_add("linha_escolhida", f"{linha}.0", f"{linha + 1}.0")
        self.texto.tag_lower("linha_escolhida", "linha_atual")

    def marcar(self, linha, marca):
        self.texto.delete(f"{linha}.0", f"{linha}.1")
        self.texto.insert(f"{linha}.0", marca, "marca")
        self.marcadas.append(linha)

    # Rola a caixa para a linha ficar perto do meio (se ela já está bem visível, não mexe)
    def rolar_para(self, linha):
        if self.quantidade_de_linhas == 0:
            return
        altura_da_linha = max(1, self.fontes["codigo"].metrics("linespace"))
        visiveis = max(3, int(self.texto.winfo_height() / altura_da_linha))
        primeira = int(self.texto.index("@0,0").split(".")[0])
        if primeira + 1 <= linha <= primeira + visiveis - 3:
            return
        topo = max(0, linha - visiveis // 2)
        self.texto.yview_moveto(topo / max(1, self.quantidade_de_linhas))


class PainelDeCodigo:
    # janela: quem diz o que destacar em cada momento (a parte da tela). Ela precisa ter: tema, fontes,
    # app, modo ("passo" ou "linha"), trecho_do_momento(), linhas_do_arquivo, codigo_de_estudo(chave),
    # linhas_do_momento(chave, programa) e aviso_sem_linha_de_estudo().
    #   orientacao      -> "vertical" (a comparação embaixo) ou "horizontal" (a comparação do lado)
    #   preferencias    -> as chaves em app.preferencias onde a escolha das linguagens fica guardada
    #   ao_clicar_na_linha(chave da linguagem, número da linha) -> chamada no clique numa linha
    def __init__(self, pai, janela, orientacao="vertical", preferencias=("linguagem", "comparar"),
                 ao_clicar_na_linha=None, titulo="Código"):
        self.janela = janela
        self.tema = janela.tema
        self.fontes = janela.fontes
        self.chaves_das_preferencias = preferencias
        self.ao_clicar_na_linha = ao_clicar_na_linha
        guardadas = janela.app.preferencias
        self.linguagem = tk.StringVar(value=texto_da_escolha(guardadas.get(preferencias[0], BOSCOGRAPH)))
        self.comparar = tk.StringVar(value=texto_da_escolha(guardadas.get(preferencias[1])))

        self.quadro = ttk.LabelFrame(pai, text=titulo, padding=6)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(1, weight=1)

        escolhas = ttk.Frame(self.quadro)
        escolhas.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        textos = [texto for chave, texto in ESCOLHAS]
        ttk.Label(escolhas, text="Linguagem", style="Suave.TLabel").pack(side="left")
        caixa = ttk.Combobox(escolhas, textvariable=self.linguagem, values=textos, state="readonly", width=20)
        caixa.pack(side="left", padx=(6, 12))
        caixa.bind("<<ComboboxSelected>>", self.ao_escolher)
        Dica(caixa, "Código do BoscoGraph: os arquivos do próprio programa, que fazem a busca e anotam cada passo.\n"
                    "As linguagens: a busca escrita como no livro, para estudar. No modo linha a linha, o Python "
                    "roda de verdade; nas outras, a linha destacada é a que faz a mesma coisa.")
        ttk.Label(escolhas, text="Comparar com", style="Suave.TLabel").pack(side="left")
        caixa = ttk.Combobox(escolhas, textvariable=self.comparar, values=[SEM_COMPARACAO] + textos,
                             state="readonly", width=20)
        caixa.pack(side="left", padx=(6, 0))
        caixa.bind("<<ComboboxSelected>>", self.ao_escolher)
        Dica(caixa, "Mostra uma segunda linguagem embaixo, com a mesma linha destacada")

        self.divisao = ttk.PanedWindow(self.quadro, orient=orientacao)
        self.divisao.grid(row=1, column=0, sticky="nsew")
        self.visoes = [VisaoDeCodigo(self.divisao, self.tema, self.fontes),
                       VisaoDeCodigo(self.divisao, self.tema, self.fontes)]
        self.visoes[0].ao_clicar_na_linha = lambda numero: self.clicou(0, numero)
        self.visoes[1].ao_clicar_na_linha = lambda numero: self.clicou(1, numero)
        self.divisao.add(self.visoes[0].quadro, weight=1)
        self.segunda_visivel = False
        self.arrumar_visoes()

    def chave_da_linguagem(self):
        return chave_da_escolha(self.linguagem.get()) or BOSCOGRAPH

    def chave_da_comparacao(self):
        return chave_da_escolha(self.comparar.get())

    def escolher_linguagem(self, chave):
        self.linguagem.set(texto_da_escolha(chave))
        self.ao_escolher()

    def clicou(self, qual, numero):
        if self.ao_clicar_na_linha is None:
            return
        chave = self.chave_da_linguagem() if qual == 0 else self.chave_da_comparacao()
        self.ao_clicar_na_linha(chave, numero)

    # As visões que estão aparecendo: [(visão, chave da linguagem), ...]
    def visoes_visiveis(self):
        lista = [(self.visoes[0], self.chave_da_linguagem())]
        if self.segunda_visivel:
            lista.append((self.visoes[1], self.chave_da_comparacao()))
        return lista

    def ao_escolher(self, evento=None):
        preferencias = self.janela.app.preferencias
        preferencias[self.chaves_das_preferencias[0]] = self.chave_da_linguagem()
        preferencias[self.chaves_das_preferencias[1]] = self.chave_da_comparacao()
        self.arrumar_visoes()
        self.atualizar()
        self.janela.app.raiz.focus_set()     # as setas voltam a controlar a busca (e não a caixa)

    # Com "Comparar com", a segunda caixa aparece embaixo da primeira (e some sem comparação)
    def arrumar_visoes(self):
        quer_a_segunda = self.chave_da_comparacao() is not None
        if quer_a_segunda and not self.segunda_visivel:
            self.divisao.add(self.visoes[1].quadro, weight=1)
            self.segunda_visivel = True
        elif not quer_a_segunda and self.segunda_visivel:
            self.divisao.forget(self.visoes[1].quadro)
            self.segunda_visivel = False

    # Mostra o momento atual nas caixas visíveis
    def atualizar(self):
        self.mostrar(self.visoes[0], self.chave_da_linguagem())
        if self.segunda_visivel:
            self.mostrar(self.visoes[1], self.chave_da_comparacao())

    def mostrar(self, visao, chave):
        janela = self.janela
        if chave == BOSCOGRAPH:
            arquivo, linha = janela.trecho_do_momento()
            visao.colocar(chave, arquivo, janela.linhas_do_arquivo[arquivo], f"Código do BoscoGraph · {arquivo}")
            visao.destacar([linha] if linha else [])
            return
        programa = janela.codigo_de_estudo(chave)
        nome = estudo.linguagem(chave)["nome"]
        arquivo = programa["nome"]
        atuais, anteriores = janela.linhas_do_momento(chave, programa)
        if janela.modo == "linha":
            if chave == "python":
                titulo = f"{nome} · {arquivo} · é este que roda, linha por linha"
            else:
                titulo = f"{nome} · {arquivo} · destaca a linha que faz o mesmo que a do Python"
        elif not atuais:
            titulo = f"{nome} · {arquivo} · {janela.aviso_sem_linha_de_estudo()}"
        else:
            titulo = f"{nome} · {arquivo} · a linha que faz este passo"
        visao.colocar(chave, arquivo, programa["linhas"], titulo)
        visao.destacar(atuais, anteriores)
