# Os botões do BoscoGraph, desenhados num Canvas: cantos arredondados, um ícone e uma cor para cada
# papel. O botão comum do Tkinter (ttk.Button) é um retângulo cinza igual para tudo, e aí "Adicionar",
# "Remover" e "Renomear" ficam iguais. Aqui cada papel tem a sua cor:
#   principal  -> azul cheio (a ação principal da tela: Ver exemplo, Visualizar, Abrir)
#   sucesso    -> verde (criar, adicionar)
#   perigo     -> vermelho (remover, apagar)
#   info       -> verde-azulado (editar, renomear, importar)
#   roxo       -> roxo (arquivos .bosco)
#   contorno   -> só a borda azul (a segunda opção, ao lado da principal)
#   suave      -> fundo azul bem clarinho e letras azuis (ações de apoio: Salvar, Sortear, Pesos…)
#   neutro     -> branco com borda cinza (o resto)
#   icone      -> sem fundo nem borda (botões só de ícone, como o "Sobre")
# O parâmetro "cor" troca a cor do papel por outra (a tela inicial pinta os botões com a cor do tipo de busca).
# Os ícones são desenhados com linhas e polígonos (desenhar_icone), e não com letras especiais: assim
# aparecem iguais em qualquer computador, mesmo sem a fonte certa.
#
# Os componentes deste arquivo:
#   Botao        -> o botão comum (texto, ícone e, se quiser, um subtítulo embaixo do texto)
#   CartaoDeAcao -> um cartão grande e clicável: ícone num círculo colorido, título e explicação
#   ChaveDoTema  -> o interruptor do tema: sol de um lado, lua do outro
#   Segmentos    -> opções lado a lado numa barra só (só uma fica marcada), como "Orientado | Não orientado"
#   Etapas       -> a trilha das etapas de uma tela em passos: ① Escolher  ─  ② Conferir  ─  ③ Abrir
#   Lembrete     -> um ícone pequeno e um texto discreto (uma dica que fica sempre à vista)
# Os campos de formulário (contador, interruptor, caixa de texto, escolha de vértice) ficam em visual/campos.py.
#
# Uso: Botao(pai, app, "Ver exemplo", icone="play", papel="principal", comando=funcao).pack()
# Com o zoom (Ctrl + roda do mouse), as letras mudam de tamanho: a tela chama redesenhar_componentes()
# para os botões se medirem de novo.

import math
import tkinter as tk

from visual.dica import Dica
from visual.logo import retangulo_arredondado
from visual.tema import misturar

# Cores fixas dos papéis que o tema não tem: (tema claro, tema escuro)
COR_INFO = ("#00838f", "#4dd0e1")
COR_ROXO = ("#6a1b9a", "#ce93d8")

# Espaços em volta do texto (em pixels, a 100% de zoom) para cada tamanho
TAMANHOS = {
    "pequeno": {"fonte": "pequena", "folga_x": 8, "folga_y": 3, "raio": 5},
    "normal": {"fonte": "texto", "folga_x": 12, "folga_y": 6, "raio": 7},
    "grande": {"fonte": "negrito", "folga_x": 18, "folga_y": 11, "raio": 9},
}

# A animação da chave do tema: quantos quadros e quantos milissegundos entre eles
QUADROS_DA_ANIMACAO = 7
MILISSEGUNDOS_POR_QUADRO = 16


# A cor principal de um papel (a do fundo do botão cheio). "cor" troca a cor do papel por outra.
def cor_do_papel(tema, papel, cor=None):
    if cor is not None:
        return cor
    escuro = tema["nome"] == "escuro"
    if papel == "sucesso":
        return tema["sucesso"]
    if papel == "perigo":
        return tema["erro"]
    if papel == "info":
        return COR_INFO[escuro]
    if papel == "roxo":
        return COR_ROXO[escuro]
    if papel == "neutro":
        return tema["texto_suave"]
    return tema["acento"]                    # principal, contorno e suave


# A cor das letras em cima de um fundo cheio: branco no tema claro, quase preto no escuro
# (no tema escuro as cores dos papéis são claras, e letra branca em cima delas não se lê)
def cor_sobre_o_papel(tema):
    if tema["nome"] == "escuro":
        return "#0b0d10"
    return "#ffffff"


# As cores de um papel: (fundo, texto, borda). None no fundo = transparente (a cor de quem está atrás).
# atras: a cor de quem está atrás do botão (o "suave" é essa cor com um pouco da cor do papel)
def cores_do_papel(tema, papel, cor=None, atras=None):
    principal = cor_do_papel(tema, papel, cor)
    if papel in ("principal", "sucesso", "perigo", "info", "roxo"):
        texto = cor_sobre_o_papel(tema)
        if papel == "principal" and cor is None:
            texto = tema["texto_acento"]
        return principal, texto, None
    if papel == "contorno":
        return None, principal, principal
    if papel == "suave":
        return misturar(atras or tema["superficie"], principal, 0.13), principal, None
    if papel == "icone":
        return None, tema["texto"], None
    return tema["superficie"], tema["texto"], tema["borda"]           # neutro


# Escurece a cor no tema claro e clareia no escuro (o "mouse em cima" e o "apertado")
def mais_escuro_ou_claro(tema, cor, quanto):
    if tema["nome"] == "escuro":
        return misturar(cor, "#ffffff", quanto)
    return misturar(cor, "#000000", quanto)


# Quebra um texto em linhas que cabem na largura (em pixels), palavra por palavra
def quebrar_texto(texto, fonte, largura):
    linhas = []
    for paragrafo in texto.split("\n"):
        linha = ""
        for palavra in paragrafo.split(" "):
            tentativa = palavra if linha == "" else linha + " " + palavra
            if linha != "" and fonte.measure(tentativa) > largura:
                linhas.append(linha)
                linha = palavra
            else:
                linha = tentativa
        linhas.append(linha)
    return linhas


# ----------------------------------------------------------------------
# A base: um Canvas que se comporta como botão
# ----------------------------------------------------------------------

class Desenhado(tk.Canvas):
    # fundo: a cor de quem está atrás (o cartão branco ou o fundo da janela), para os cantos
    # arredondados se misturarem com ela
    def __init__(self, pai, app, comando=None, dica=None, fundo=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo, cursor="hand2", takefocus=1)
        self.comando = comando
        self.habilitado = True
        self.mouse_em_cima = False
        self.apertado = False
        self.com_foco = False
        self.largura = 1                    # o tamanho pedido (calculado em medir)
        self.altura = 1
        self.bind("<Enter>", self.entrou)
        self.bind("<Leave>", self.saiu)
        self.bind("<ButtonPress-1>", self.apertou)
        self.bind("<ButtonRelease-1>", self.soltou)
        self.bind("<FocusIn>", lambda evento: self.mudar_foco(True))
        self.bind("<FocusOut>", lambda evento: self.mudar_foco(False))
        self.bind("<Return>", self.acionar)
        self.bind("<KP_Enter>", self.acionar)
        self.bind("<space>", self.acionar)
        # O grid ou o pack podem esticar o componente: aí ele se desenha de novo no tamanho de verdade
        self.bind("<Configure>", lambda evento: self.desenhar())
        if dica:
            Dica(self, dica)

    # O tamanho em que desenhar: o de verdade, ou o pedido enquanto o componente ainda não apareceu
    def tamanho_atual(self):
        largura = self.winfo_width()
        altura = self.winfo_height()
        if largura <= 1 or altura <= 1:
            return self.largura, self.altura
        return largura, altura

    def medir(self):
        pass

    def desenhar(self):
        pass

    # Mede e desenha de novo (depois de uma mudança de zoom)
    def remedir(self):
        self.medir()
        self.desenhar()

    def entrou(self, evento=None):
        self.mouse_em_cima = True
        self.desenhar()

    def saiu(self, evento=None):
        self.mouse_em_cima = False
        self.apertado = False
        self.desenhar()

    def apertou(self, evento=None):
        if not self.habilitado:
            return
        self.apertado = True
        self.desenhar()

    # O clique vale quando o botão é solto em cima do componente (soltar fora = desistir)
    def soltou(self, evento=None):
        if not self.apertado:
            return
        self.apertado = False
        largura, altura = self.tamanho_atual()
        dentro = 0 <= evento.x <= largura and 0 <= evento.y <= altura
        self.desenhar()
        if dentro:
            self.acionar()

    def acionar(self, evento=None):
        if self.habilitado and self.comando is not None:
            self.comando()
        return "break"

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()

    def ligar(self, habilitado):
        self.habilitado = habilitado
        self.configure(cursor="hand2" if habilitado else "arrow")
        self.desenhar()


# ----------------------------------------------------------------------
# O botão comum
# ----------------------------------------------------------------------

class Botao(Desenhado):
    # menu: um tk.Menu que abre embaixo do botão quando ele é clicado (aparece uma setinha ▾ à direita);
    # antes_de_abrir: chamada logo antes de o menu abrir (para montar os itens na hora, como a lista de modelos);
    # cor: troca a cor do papel (por exemplo, a cor do tipo de busca);
    # icone_depois: o ícone vem depois do texto (o "Próximo →" do editor)
    def __init__(self, pai, app, texto="", icone=None, papel="neutro", comando=None, dica=None, tamanho="normal",
                 largura=None, fundo=None, subtitulo=None, menu=None, antes_de_abrir=None, cor=None,
                 icone_depois=False):
        super().__init__(pai, app, comando, dica, fundo)
        self.texto = texto
        self.subtitulo = subtitulo
        self.icone = icone
        self.icone_depois = icone_depois
        self.papel = papel
        self.cor = cor
        self.tamanho = tamanho
        self.largura_pedida = largura
        self.menu = menu
        self.antes_de_abrir = antes_de_abrir
        if menu is not None:
            self.comando = self.abrir_menu
        self.medir()
        self.desenhar()

    # O menu abre logo abaixo do botão (o tk_popup prende o mouse até a pessoa escolher ou desistir)
    def abrir_menu(self):
        if self.antes_de_abrir is not None:
            self.antes_de_abrir()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    # O espaço da setinha do menu (0 sem menu)
    def largura_da_seta(self):
        if self.menu is None:
            return 0
        return round(self.lado_do_icone * 0.7) + round(6 * self.app.zoom)

    def fonte(self):
        return self.app.fontes[TAMANHOS[self.tamanho]["fonte"]]

    def fonte_do_subtitulo(self):
        return self.app.fontes["pequena"]

    # A largura e a altura do botão, a partir do texto e do zoom
    def medir(self):
        medidas = TAMANHOS[self.tamanho]
        zoom = self.app.zoom
        fonte = self.fonte()
        altura_do_texto = fonte.metrics("linespace")
        self.lado_do_icone = round(altura_do_texto * (1.1 if self.tamanho == "grande" else 0.95))
        largura = 0
        if self.texto:
            largura = fonte.measure(self.texto)
            if self.subtitulo:
                largura = max(largura, self.fonte_do_subtitulo().measure(self.subtitulo))
        if self.icone:
            largura += self.lado_do_icone + (round(8 * zoom) if self.texto else 0)
        largura += self.largura_da_seta()
        folga_x = round(medidas["folga_x"] * zoom)
        folga_y = round(medidas["folga_y"] * zoom)
        altura = altura_do_texto + 2 * folga_y
        if self.subtitulo:
            altura += self.fonte_do_subtitulo().metrics("linespace")
        if not self.texto:
            largura = self.lado_do_icone + 2 * folga_y          # botão só de ícone: quadrado
        else:
            largura += 2 * folga_x
        if self.largura_pedida:
            largura = max(largura, round(self.largura_pedida * zoom))
        self.largura = largura
        self.altura = altura
        self.configure(width=largura, height=altura)

    def cores_agora(self):
        fundo, texto, borda = cores_do_papel(self.tema, self.papel, self.cor, self.fundo)
        if not self.habilitado:
            if fundo is not None:
                fundo = self.tema["fundo"] if self.fundo != self.tema["fundo"] else self.tema["superficie"]
            return fundo, self.tema["texto_suave"], self.tema["borda"]
        if self.papel == "suave":
            # O suave só fica com mais cor (escurecer um fundo clarinho deixaria o botão cinza)
            if self.apertado:
                fundo = misturar(self.fundo, texto, 0.30)
            elif self.mouse_em_cima:
                fundo = misturar(self.fundo, texto, 0.21)
            return fundo, texto, borda
        realce = self.cor or self.tema["acento"]        # a cor que tinge o fundo dos botões sem fundo
        if self.apertado:
            if fundo is None:
                fundo = misturar(self.fundo, realce, 0.22)
            else:
                fundo = mais_escuro_ou_claro(self.tema, fundo, 0.25)
        elif self.mouse_em_cima:
            if fundo is None:
                fundo = misturar(self.fundo, realce, 0.12)
            else:
                fundo = mais_escuro_ou_claro(self.tema, fundo, 0.13)
        return fundo, texto, borda

    def desenhar(self):
        self.delete("all")
        largura, altura = self.tamanho_atual()
        raio = round(TAMANHOS[self.tamanho]["raio"] * self.app.zoom)
        fundo, cor_do_texto, borda = self.cores_agora()
        deslocamento = 1 if self.apertado else 0            # apertado: o conteúdo desce 1 pixel
        if fundo is not None or borda is not None:
            retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, raio,
                                  fill=fundo if fundo is not None else self.fundo,
                                  outline=borda if borda is not None else "", width=1)
        if self.com_foco:
            # O anel tracejado do foco (quem usa o Tab para andar pelos botões sabe onde está)
            retangulo_arredondado(self, 3, 3, largura - 3, altura - 3, max(2, raio - 2), fill="",
                                  outline=misturar(cor_do_texto, fundo or self.fundo, 0.45), width=1, dash=(2, 2))
        fonte = self.fonte()
        if not self.texto:
            desenhar_icone(self, self.icone, largura / 2, altura / 2 + deslocamento, self.lado_do_icone, cor_do_texto,
                           fundo or self.fundo)
            return
        # Ícone à esquerda e o texto (com o subtítulo embaixo, se houver), os dois centralizados
        conteudo = fonte.measure(self.texto)
        if self.subtitulo:
            conteudo = max(conteudo, self.fonte_do_subtitulo().measure(self.subtitulo))
        espaco = round(8 * self.app.zoom)
        if self.icone:
            conteudo += self.lado_do_icone + espaco
        conteudo += self.largura_da_seta()
        x = (largura - conteudo) / 2
        if self.icone and self.icone_depois:
            # O ícone depois do texto: desenha o ícone no fim e o texto começa no mesmo x de sempre
            x_do_icone = x + fonte.measure(self.texto) + espaco
            desenhar_icone(self, self.icone, x_do_icone + self.lado_do_icone / 2, altura / 2 + deslocamento,
                           self.lado_do_icone, cor_do_texto, fundo or self.fundo)
        elif self.icone:
            desenhar_icone(self, self.icone, x + self.lado_do_icone / 2, altura / 2 + deslocamento, self.lado_do_icone,
                           cor_do_texto, fundo or self.fundo)
            x += self.lado_do_icone + espaco
        if self.menu is not None:
            # A setinha ▾ do menu, depois do texto
            lado = self.lado_do_icone * 0.7
            fim_do_texto = x + fonte.measure(self.texto)
            desenhar_icone(self, "chevron_baixo", fim_do_texto + round(6 * self.app.zoom) + lado / 2,
                           altura / 2 + deslocamento, lado, cor_do_texto, fundo or self.fundo)
        if self.subtitulo:
            linha = fonte.metrics("linespace")
            meio = altura / 2 + deslocamento
            self.create_text(x, meio - linha / 2 + 1, text=self.texto, anchor="w", fill=cor_do_texto, font=fonte)
            self.create_text(x, meio + linha / 2, text=self.subtitulo, anchor="w",
                             fill=misturar(cor_do_texto, fundo or self.fundo, 0.25), font=self.fonte_do_subtitulo())
        else:
            self.create_text(x, altura / 2 + deslocamento, text=self.texto, anchor="w", fill=cor_do_texto, font=fonte)

    # Muda o que o botão mostra (o texto, o ícone, o papel) ou liga/desliga o botão
    def configurar(self, texto=None, icone=None, papel=None, habilitado=None, subtitulo=None, comando=None):
        if texto is not None:
            self.texto = texto
        if icone is not None:
            self.icone = icone
        if papel is not None:
            self.papel = papel
        if subtitulo is not None:
            self.subtitulo = subtitulo
        if comando is not None:
            self.comando = comando
        if habilitado is not None:
            self.habilitado = habilitado
            self.configure(cursor="hand2" if habilitado else "arrow")
        self.medir()
        self.desenhar()


# ----------------------------------------------------------------------
# O cartão de ação: grande, com o ícone num círculo colorido, o título e uma explicação
# ----------------------------------------------------------------------

class CartaoDeAcao(Desenhado):
    # papel: a cor do cartão (os mesmos papéis do Botao: "sucesso", "info", "roxo", "principal", "neutro")
    # largura_minima: em pixels a 100% de zoom (o cartão pode esticar mais que isso)
    # cor: troca a cor do papel (a tela inicial usa a cor do tipo de busca)
    # cheio: True = o cartão inteiro na cor (a ação principal); False = clarinho, com a borda na cor
    # grande: True = título com letra maior (os dois caminhos do algoritmo escolhido, na tela inicial)
    def __init__(self, pai, app, titulo, explicacao, icone, papel, comando=None, dica=None, fundo=None,
                 largura_minima=220, cor=None, cheio=False, grande=False):
        super().__init__(pai, app, comando, dica, fundo)
        self.titulo = titulo
        self.explicacao = explicacao
        self.icone = icone
        self.papel = papel
        self.cor = cor
        self.cheio = cheio
        self.grande = grande
        self.largura_minima = largura_minima
        self.medir()
        self.desenhar()

    def fonte_do_titulo(self):
        if self.grande:
            return self.app.fontes["destaque"]
        return self.app.fontes["negrito"]

    def fonte_da_explicacao(self):
        if self.grande:
            return self.app.fontes["texto"]
        return self.app.fontes["pequena"]

    # As medidas que dependem do zoom: a folga das bordas, o círculo do ícone e o espaço entre eles
    def medidas(self):
        zoom = self.app.zoom
        folga = round((16 if self.grande else 14) * zoom)
        diametro = round(self.app.fontes["negrito"].metrics("linespace") * (2.7 if self.grande else 2.3))
        espaco = round(12 * zoom)
        seta = round(14 * zoom)                 # o espaço da setinha da direita
        return folga, diametro, espaco, seta

    # A largura que sobra para o título e a explicação, num cartão de "largura" pixels
    def largura_do_texto(self, largura):
        folga, diametro, espaco, seta = self.medidas()
        return max(40, largura - 2 * folga - diametro - espaco - seta)

    # A altura que o cartão precisa com "largura" pixels (a explicação quebra em mais linhas se for estreito)
    # (o título também quebra: numa janela estreita, "Ver um exemplo pronto" vira duas linhas em vez de ser cortado)
    def altura_para(self, largura):
        folga, diametro, espaco, seta = self.medidas()
        linhas_do_titulo = quebrar_texto(self.titulo, self.fonte_do_titulo(), self.largura_do_texto(largura))
        linhas = quebrar_texto(self.explicacao, self.fonte_da_explicacao(), self.largura_do_texto(largura))
        altura_do_texto = (len(linhas_do_titulo) * self.fonte_do_titulo().metrics("linespace")
                           + len(linhas) * self.fonte_da_explicacao().metrics("linespace") + 2)
        return 2 * folga + max(diametro, altura_do_texto)

    def medir(self):
        self.largura = round(self.largura_minima * self.app.zoom)
        self.altura = self.altura_para(self.largura)
        self.configure(width=self.largura, height=self.altura)

    # As cores do cartão agora (depende do mouse em cima e de estar apertado):
    # (fundo, borda, cor do círculo, cor do ícone, cor do título, cor da explicação, cor da setinha)
    def cores_agora(self):
        tema = self.tema
        cor = cor_do_papel(tema, self.papel, self.cor)
        realcado = self.mouse_em_cima or self.com_foco
        if self.cheio:
            fundo = cor
            if self.apertado:
                fundo = mais_escuro_ou_claro(tema, cor, 0.22)
            elif realcado:
                fundo = mais_escuro_ou_claro(tema, cor, 0.11)
            letra = cor_sobre_o_papel(tema)
            circulo = misturar(fundo, letra, 0.22)
            return fundo, fundo, circulo, letra, letra, misturar(letra, fundo, 0.22), letra
        tom = 0.07
        borda = misturar(tema["borda"], cor, 0.35)
        if self.apertado:
            tom = 0.2
            borda = cor
        elif realcado:
            tom = 0.13
            borda = cor
        fundo = misturar(tema["superficie"], cor, tom)
        seta = cor if self.mouse_em_cima else tema["texto_suave"]
        return fundo, borda, cor, cor_sobre_o_papel(tema), tema["texto"], tema["texto_suave"], seta

    def desenhar(self):
        self.delete("all")
        largura, altura = self.tamanho_atual()
        # Mais estreito que o previsto, a explicação ganha linhas: o cartão pede a altura de que precisa
        if self.winfo_width() > 1:
            precisa = self.altura_para(largura)
            if precisa != self.altura:
                self.altura = precisa
                self.configure(height=precisa)
        folga, diametro, espaco, seta = self.medidas()
        fundo, borda, cor_do_circulo, cor_do_icone, cor_do_titulo, cor_da_explicacao, cor_da_seta = self.cores_agora()
        raio = round(10 * self.app.zoom)
        realcado = self.mouse_em_cima or self.com_foco
        retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, raio, fill=fundo, outline=borda,
                              width=2 if (realcado and not self.cheio) else 1)
        if self.cheio and self.com_foco:
            # O anel tracejado do foco, por dentro (a borda do cartão cheio é da cor dele)
            retangulo_arredondado(self, 4, 4, largura - 4, altura - 4, max(2, raio - 3), fill="",
                                  outline=cor_da_explicacao, width=1, dash=(2, 2))
        # O círculo colorido com o ícone
        cx = folga + diametro / 2
        cy = altura / 2
        self.create_oval(cx - diametro / 2, cy - diametro / 2, cx + diametro / 2, cy + diametro / 2,
                         fill=cor_do_circulo, outline=cor_do_circulo)
        desenhar_icone(self, self.icone, cx, cy, diametro * 0.5, cor_do_icone, cor_do_circulo)
        # O título e a explicação (quebrada em linhas), centralizados na altura
        x = folga + diametro + espaco
        fonte_do_titulo = self.fonte_do_titulo()
        fonte_da_explicacao = self.fonte_da_explicacao()
        linhas_do_titulo = quebrar_texto(self.titulo, fonte_do_titulo, self.largura_do_texto(largura))
        linhas = quebrar_texto(self.explicacao, fonte_da_explicacao, self.largura_do_texto(largura))
        altura_do_texto = (len(linhas_do_titulo) * fonte_do_titulo.metrics("linespace")
                           + len(linhas) * fonte_da_explicacao.metrics("linespace"))
        y = (altura - altura_do_texto) / 2
        self.create_text(x, y, text="\n".join(linhas_do_titulo), anchor="nw", fill=cor_do_titulo,
                         font=fonte_do_titulo)
        y += len(linhas_do_titulo) * fonte_do_titulo.metrics("linespace") + 1
        self.create_text(x, y, text="\n".join(linhas), anchor="nw", fill=cor_da_explicacao, font=fonte_da_explicacao)
        # A setinha da direita anda um pouco quando o mouse está em cima ("clique aqui")
        avanco = 3 * self.app.zoom if self.mouse_em_cima else 0
        desenhar_icone(self, "chevron_direita", largura - folga - seta / 2 + avanco, cy, seta, cor_da_seta, fundo)

    def configurar(self, titulo=None, explicacao=None):
        if titulo is not None:
            self.titulo = titulo
        if explicacao is not None:
            self.explicacao = explicacao
        self.medir()
        self.desenhar()


# ----------------------------------------------------------------------
# A chave do tema: um interruptor com o sol (claro) de um lado e a lua (escuro) do outro
# ----------------------------------------------------------------------

class ChaveDoTema(Desenhado):
    def __init__(self, pai, app, fundo=None):
        super().__init__(pai, app, comando=self.alternar, dica="Troca entre o tema claro (sol) e o escuro (lua)",
                         fundo=fundo)
        self.escuro = app.tema["nome"] == "escuro"
        self.posicao = 1.0 if self.escuro else 0.0      # 0 = bolinha no sol, 1 = bolinha na lua
        self.animando = None
        self.medir()
        self.desenhar()

    def medir(self):
        self.altura = round(self.app.fontes["texto"].metrics("linespace") * 1.9)
        self.largura = round(self.altura * 2.1)
        self.configure(width=self.largura, height=self.altura)

    def desenhar(self):
        self.delete("all")
        tema = self.tema
        largura, altura = self.tamanho_atual()
        trilho = tema["superficie"]
        borda = tema["acento"] if (self.mouse_em_cima or self.com_foco) else tema["borda"]
        retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, (altura - 2) / 2, fill=trilho, outline=borda,
                              width=1)
        raio = altura / 2 - 3
        centro_do_sol = 2 + raio + 1
        centro_da_lua = largura - 2 - raio - 1
        cy = altura / 2
        # A bolinha (atrás do ícone escolhido), na posição da animação
        cx = centro_do_sol + (centro_da_lua - centro_do_sol) * self.posicao
        cor_da_bolinha = tema["acento"]
        self.create_oval(cx - raio, cy - raio, cx + raio, cy + raio, fill=cor_da_bolinha, outline=cor_da_bolinha)
        lado = raio * 1.3
        no_sol = self.posicao < 0.5
        desenhar_icone(self, "sol", centro_do_sol, cy, lado, tema["texto_acento"] if no_sol else tema["texto_suave"],
                       cor_da_bolinha if no_sol else trilho)
        desenhar_icone(self, "lua", centro_da_lua, cy, lado,
                       tema["texto_acento"] if not no_sol else tema["texto_suave"],
                       cor_da_bolinha if not no_sol else trilho)

    # O clique: a bolinha desliza para o outro lado e só então o tema troca (a tela é recriada)
    def alternar(self):
        if self.animando is not None:
            return
        self.animar(0)

    def animar(self, quadro):
        if not self.winfo_exists():
            return
        if quadro >= QUADROS_DA_ANIMACAO:
            # A troca recria a tela (e destrói esta chave). Ela fica para DEPOIS deste "after", pedida à
            # janela principal: destruir um componente dentro do "after" dele mesmo confunde o Tkinter (no
            # fim do "after", ele apaga um comando pelo nome, e o nome pode já ser de um componente novo).
            # O animando continua ocupado: um clique a mais, até a tela ser recriada, não faz nada.
            self.animando = self.app.raiz.after_idle(self.app.trocar_tema)
            return
        fracao = (quadro + 1) / QUADROS_DA_ANIMACAO
        self.posicao = fracao if not self.escuro else 1.0 - fracao
        self.desenhar()
        self.animando = self.after(MILISSEGUNDOS_POR_QUADRO, lambda: self.animar(quadro + 1))


# ----------------------------------------------------------------------
# Segmentos: opções lado a lado numa barra só; a escolhida fica azul
# ----------------------------------------------------------------------

class Segmentos(tk.Canvas):
    # opcoes: [(valor, texto, icone ou None), ...]; variavel: a variável do Tkinter com o valor escolhido;
    # comando: chamado depois de cada troca (sem argumentos)
    def __init__(self, pai, app, opcoes, variavel, comando=None, fundo=None, dica=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo, cursor="hand2", takefocus=1)
        self.opcoes = list(opcoes)
        self.variavel = variavel
        self.comando = comando
        self.em_cima = None             # o segmento com o mouse em cima (None = nenhum)
        self.com_foco = False
        self.bind("<Motion>", self.moveu)
        self.bind("<Leave>", self.saiu)
        self.bind("<ButtonRelease-1>", self.clicou)
        self.bind("<Left>", lambda evento: self.andar(-1))
        self.bind("<Right>", lambda evento: self.andar(1))
        self.bind("<FocusIn>", lambda evento: self.mudar_foco(True))
        self.bind("<FocusOut>", lambda evento: self.mudar_foco(False))
        self.bind("<Configure>", lambda evento: self.desenhar())
        # Se a variável mudar por outro caminho (o Ctrl+Z, por exemplo), a barra acompanha
        self.observador = variavel.trace_add("write", lambda *argumentos: self.desenhar())
        self.bind("<Destroy>", self.ao_destruir)
        if dica:
            Dica(self, dica)
        self.medir()
        self.desenhar()

    def ao_destruir(self, evento):
        if evento.widget is self and self.observador is not None:
            try:
                self.variavel.trace_remove("write", self.observador)
            except (tk.TclError, AttributeError):       # a variável já foi apagada (no fim do programa)
                pass
            self.observador = None

    def medir(self):
        fonte = self.app.fontes["texto"]
        zoom = self.app.zoom
        self.lado_do_icone = round(fonte.metrics("linespace") * 1.1)
        maior = 0
        for valor, texto, icone in self.opcoes:
            largura = fonte.measure(texto)
            if icone:
                largura += self.lado_do_icone + round(7 * zoom)
            maior = max(maior, largura)
        # Todos os segmentos com a mesma largura: a barra fica arrumada
        self.largura_do_segmento = maior + round(2 * 13 * zoom)
        self.largura = self.largura_do_segmento * len(self.opcoes) + 2
        self.altura = fonte.metrics("linespace") + round(2 * 6 * zoom)
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def indice_escolhido(self):
        atual = self.variavel.get()
        for indice in range(len(self.opcoes)):
            if self.opcoes[indice][0] == atual:
                return indice
        return None

    def desenhar(self):
        if not self.winfo_exists():
            return
        self.delete("all")
        tema = self.tema
        fonte = self.app.fontes["texto"]
        zoom = self.app.zoom
        altura = self.altura
        raio = round(7 * zoom)
        borda = tema["acento"] if self.com_foco else tema["borda"]
        retangulo_arredondado(self, 1, 1, self.largura - 1, altura - 1, raio, fill=tema["superficie"], outline=borda)
        escolhido = self.indice_escolhido()
        for indice in range(len(self.opcoes)):
            valor, texto, icone = self.opcoes[indice]
            x1 = 1 + indice * self.largura_do_segmento
            x2 = x1 + self.largura_do_segmento
            cor_do_texto = tema["texto"]
            fundo_do_segmento = tema["superficie"]
            if indice == escolhido:
                fundo_do_segmento = tema["acento"]
                cor_do_texto = tema["texto_acento"]
                retangulo_arredondado(self, x1 + 3, 4, x2 - 3, altura - 4, max(2, raio - 2), fill=fundo_do_segmento,
                                      outline=fundo_do_segmento)
            elif indice == self.em_cima:
                fundo_do_segmento = misturar(tema["superficie"], tema["acento"], 0.12)
                retangulo_arredondado(self, x1 + 3, 4, x2 - 3, altura - 4, max(2, raio - 2), fill=fundo_do_segmento,
                                      outline=fundo_do_segmento)
            # A linha fina entre dois segmentos que não estão marcados
            if indice > 0 and escolhido not in (indice, indice - 1):
                self.create_line(x1, 7, x1, altura - 7, fill=tema["borda"])
            largura_do_conteudo = fonte.measure(texto)
            if icone:
                largura_do_conteudo += self.lado_do_icone + round(7 * zoom)
            x = (x1 + x2 - largura_do_conteudo) / 2
            if icone:
                desenhar_icone(self, icone, x + self.lado_do_icone / 2, altura / 2, self.lado_do_icone, cor_do_texto,
                               fundo_do_segmento)
                x += self.lado_do_icone + round(7 * zoom)
            self.create_text(x, altura / 2, text=texto, anchor="w", fill=cor_do_texto, font=fonte)

    def segmento_em(self, x):
        indice = int((x - 1) // self.largura_do_segmento)
        if 0 <= indice < len(self.opcoes):
            return indice
        return None

    def moveu(self, evento):
        indice = self.segmento_em(evento.x)
        if indice != self.em_cima:
            self.em_cima = indice
            self.desenhar()

    def saiu(self, evento=None):
        self.em_cima = None
        self.desenhar()

    def clicou(self, evento):
        if 0 <= evento.y <= self.altura:
            indice = self.segmento_em(evento.x)
            if indice is not None:
                self.escolher(indice)

    def escolher(self, indice):
        valor = self.opcoes[indice][0]
        mudou = self.variavel.get() != valor
        self.variavel.set(valor)
        self.desenhar()
        if self.comando is not None:
            self.comando()
        return mudou

    def andar(self, sentido):
        atual = self.indice_escolhido()
        if atual is None:
            atual = 0
        novo = atual + sentido
        if 0 <= novo < len(self.opcoes):
            self.escolher(novo)
        return "break"

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()


# ----------------------------------------------------------------------
# Etapas: ① Escolher o arquivo ── ② Conferir ── ③ Abrir
# ----------------------------------------------------------------------

class Etapas(tk.Canvas):
    # textos: o nome de cada etapa; atual: a etapa de agora (0 = a primeira);
    # ao_clicar(indice): chamado ao clicar numa etapa que já passou (para voltar a ela);
    # livre: True = dá para clicar em qualquer etapa, para a frente também (o editor do grafo);
    # feitas: as etapas que ganham o "certo" verde (None = as que já passaram, antes da atual)
    def __init__(self, pai, app, textos, atual=0, ao_clicar=None, fundo=None, livre=False, feitas=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo)
        self.textos = list(textos)
        self.atual = atual
        self.ao_clicar = ao_clicar
        self.livre = livre
        self.feitas = feitas
        self.em_cima = None             # a etapa com o mouse em cima (None = nenhuma)
        self.areas = []                 # (x1, x2) de cada etapa, para saber onde foi o clique
        self.bind("<Configure>", lambda evento: self.desenhar())
        self.bind("<ButtonRelease-1>", self.clicou)
        self.bind("<Motion>", self.moveu)
        self.bind("<Leave>", self.saiu)
        self.medir()
        self.desenhar()

    # A etapa "indice" ganha o "certo" verde?
    def esta_feita(self, indice):
        if self.feitas is None:
            return indice < self.atual
        return indice in self.feitas

    # Dá para clicar na etapa "indice"? (na de agora, não: ela já está aberta)
    def pode_clicar(self, indice):
        if indice is None or indice == self.atual or self.ao_clicar is None:
            return False
        return self.livre or indice < self.atual

    def medidas(self):
        zoom = self.app.zoom
        diametro = round(self.app.fontes["negrito"].metrics("linespace") * 1.55)
        return diametro, round(8 * zoom), round(44 * zoom)      # círculo, espaço até o texto, ligação

    def largura_da_etapa(self, indice):
        diametro, espaco, ligacao = self.medidas()
        return diametro + espaco + self.app.fontes["negrito"].measure(self.textos[indice])

    def medir(self):
        diametro, espaco, ligacao = self.medidas()
        total = 0
        for indice in range(len(self.textos)):
            total += self.largura_da_etapa(indice)
        total += ligacao * (len(self.textos) - 1) + 2 * round(12 * self.app.zoom)
        self.largura = total
        self.altura = diametro + round(10 * self.app.zoom)
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    # feitas: as etapas com o "certo" (None = continua como estava)
    def mudar(self, atual, feitas=None):
        self.atual = atual
        if feitas is not None:
            self.feitas = feitas
        self.desenhar()

    # Troca os nomes das etapas (o editor mostra quantos vértices e arestas já existem: "Vértices (8)")
    def mudar_textos(self, textos):
        if list(textos) != self.textos:
            self.textos = list(textos)
            self.medir()
            self.desenhar()

    def desenhar(self):
        self.delete("all")
        tema = self.tema
        diametro, espaco, ligacao = self.medidas()
        largura = max(self.winfo_width(), self.largura)
        cy = self.altura / 2
        total = self.largura - 2 * round(12 * self.app.zoom)
        x = (largura - total) / 2
        self.areas = []
        for indice in range(len(self.textos)):
            if indice > 0:
                cor = tema["sucesso"] if self.esta_feita(indice - 1) else tema["borda"]
                self.create_line(x + 4, cy, x + ligacao - 4, cy, fill=cor, width=2, capstyle="round")
                x += ligacao
            inicio = x
            if indice == self.em_cima and self.pode_clicar(indice):
                # O mouse em cima de uma etapa que dá para abrir: um fundo clarinho atrás dela
                folga = round(6 * self.app.zoom)
                retangulo_arredondado(self, x - folga, cy - diametro / 2 - 3, x + self.largura_da_etapa(indice) + folga,
                                      cy + diametro / 2 + 3, diametro / 2 + 3,
                                      fill=misturar(self.fundo, tema["acento"], 0.12), outline="")
            if indice != self.atual and self.esta_feita(indice):     # feita: círculo verde com o "certo"
                cor = tema["sucesso"]
                self.create_oval(x, cy - diametro / 2, x + diametro, cy + diametro / 2, fill=cor, outline=cor)
                desenhar_icone(self, "check", x + diametro / 2, cy, diametro * 0.55, cor_sobre_o_papel(tema), cor)
                cor_do_texto = tema["texto"]
                fonte = self.app.fontes["texto"]
            elif indice == self.atual:          # a de agora: círculo azul com o número
                cor = tema["acento"]
                self.create_oval(x, cy - diametro / 2, x + diametro, cy + diametro / 2, fill=cor, outline=cor)
                self.create_text(x + diametro / 2, cy, text=str(indice + 1), fill=tema["texto_acento"],
                                 font=self.app.fontes["negrito"])
                cor_do_texto = tema["acento"]
                fonte = self.app.fontes["negrito"]
            else:                               # ainda vai chegar: só o contorno
                self.create_oval(x + 1, cy - diametro / 2 + 1, x + diametro - 1, cy + diametro / 2 - 1,
                                 fill=self.fundo, outline=tema["borda"], width=2)
                self.create_text(x + diametro / 2, cy, text=str(indice + 1), fill=tema["texto_suave"],
                                 font=self.app.fontes["negrito"])
                cor_do_texto = tema["texto_suave"]
                fonte = self.app.fontes["texto"]
            self.create_text(x + diametro + espaco, cy, text=self.textos[indice], anchor="w", fill=cor_do_texto,
                             font=fonte)
            x += self.largura_da_etapa(indice)
            self.areas.append((inicio, x))

    def etapa_em(self, x):
        for indice in range(len(self.areas)):
            if self.areas[indice][0] <= x <= self.areas[indice][1]:
                return indice
        return None

    def moveu(self, evento):
        indice = self.etapa_em(evento.x)
        self.configure(cursor="hand2" if self.pode_clicar(indice) else "")
        if indice != self.em_cima:
            self.em_cima = indice
            self.desenhar()

    def saiu(self, evento=None):
        if self.em_cima is not None:
            self.em_cima = None
            self.desenhar()

    def clicou(self, evento):
        indice = self.etapa_em(evento.x)
        if self.pode_clicar(indice):
            self.ao_clicar(indice)


# ----------------------------------------------------------------------
# Lembrete: um ícone pequeno e um texto discreto, como "✎ Duplo clique num vértice renomeia"
# (não é botão: não reage ao clique)
# ----------------------------------------------------------------------

class Lembrete(tk.Canvas):
    def __init__(self, pai, app, texto, icone="lapis", fundo=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo)
        self.texto = texto
        self.icone = icone
        self.bind("<Configure>", lambda evento: self.desenhar())
        self.medir()
        self.desenhar()

    def medir(self):
        fonte = self.app.fontes["pequena"]
        self.lado_do_icone = round(fonte.metrics("linespace") * 1.05)
        self.espaco = round(5 * self.app.zoom)
        self.largura = self.lado_do_icone + self.espaco + fonte.measure(self.texto) + 2
        self.altura = fonte.metrics("linespace") + 4
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def desenhar(self):
        self.delete("all")
        # Sem espaço para o texto inteiro (janela estreita ou letras grandes): o lembrete some, em vez de
        # aparecer cortado no meio de uma palavra. Quando a janela cresce, ele volta.
        if 1 < self.winfo_width() < self.largura - 1:
            return
        cor = self.tema["texto_suave"]
        meio = self.altura / 2
        desenhar_icone(self, self.icone, self.lado_do_icone / 2, meio, self.lado_do_icone * 0.85, cor, self.fundo)
        self.create_text(self.lado_do_icone + self.espaco, meio, text=self.texto, anchor="w", fill=cor,
                         font=self.app.fontes["pequena"])


# Depois de uma mudança de zoom: todos os componentes desenhados dentro de "componente" se medem de novo
def redesenhar_componentes(componente):
    for filho in componente.winfo_children():
        if hasattr(filho, "remedir"):
            filho.remedir()
        redesenhar_componentes(filho)


# ----------------------------------------------------------------------
# Os ícones
# ----------------------------------------------------------------------

def pontos_do_circulo(cx, cy, raio, quantidade=24, inicio=0.0, fim=2 * math.pi):
    pontos = []
    for indice in range(quantidade + 1):
        angulo = inicio + (fim - inicio) * indice / quantidade
        pontos += [cx + raio * math.cos(angulo), cy + raio * math.sin(angulo)]
    return pontos


# Um triângulo cheio apontando para a direita (sentido=1) ou para a esquerda (sentido=-1)
def triangulo(canvas, cx, cy, m, sentido, cor):
    canvas.create_polygon(cx - sentido * m * 0.45, cy - m * 0.6, cx + sentido * m * 0.45, cy,
                          cx - sentido * m * 0.45, cy + m * 0.6, fill=cor, outline=cor, joinstyle="round")


# Desenha o ícone "nome" centralizado em (cx, cy), num quadrado de "lado" pixels.
# fundo: a cor de trás (alguns ícones "recortam" partes com ela, como a lua).
def desenhar_icone(canvas, nome, cx, cy, lado, cor, fundo):
    m = lado / 2                            # metade do lado
    espessura = max(1.5, lado / 9)
    fina = max(1, espessura / 1.5)
    if nome == "play":
        canvas.create_polygon(cx - m * 0.55, cy - m * 0.75, cx + m * 0.75, cy, cx - m * 0.55, cy + m * 0.75,
                              fill=cor, outline=cor, joinstyle="round")
    elif nome == "pausa":
        for deslocamento in (-0.35, 0.35):
            x = cx + deslocamento * m
            canvas.create_rectangle(x - m * 0.17, cy - m * 0.7, x + m * 0.17, cy + m * 0.7, fill=cor, outline=cor)
    elif nome in ("anterior", "proximo"):
        # |◀ e ▶| : um passo para trás ou para a frente
        sentido = 1 if nome == "proximo" else -1
        triangulo(canvas, cx - sentido * m * 0.2, cy, m, sentido, cor)
        x = cx + sentido * m * 0.5
        canvas.create_rectangle(x - m * 0.12, cy - m * 0.6, x + m * 0.12, cy + m * 0.6, fill=cor, outline=cor)
    elif nome in ("primeiro", "ultimo"):
        # |◀◀ e ▶▶| : para o começo ou para o fim
        sentido = 1 if nome == "ultimo" else -1
        triangulo(canvas, cx - sentido * m * 0.55, cy, m * 0.85, sentido, cor)
        triangulo(canvas, cx + sentido * m * 0.1, cy, m * 0.85, sentido, cor)
        x = cx + sentido * m * 0.7
        canvas.create_rectangle(x - m * 0.11, cy - m * 0.55, x + m * 0.11, cy + m * 0.55, fill=cor, outline=cor)
    elif nome in ("mais", "mais_circulo"):
        if nome == "mais_circulo":
            canvas.create_oval(cx - m, cy - m, cx + m, cy + m, fill=cor, outline=cor)
            cor_do_sinal = fundo
            tamanho = 0.5
        else:
            cor_do_sinal = cor
            tamanho = 0.75
        canvas.create_line(cx - m * tamanho, cy, cx + m * tamanho, cy, fill=cor_do_sinal, width=espessura * 1.3,
                           capstyle="round")
        canvas.create_line(cx, cy - m * tamanho, cx, cy + m * tamanho, fill=cor_do_sinal, width=espessura * 1.3,
                           capstyle="round")
    elif nome == "menos":
        canvas.create_line(cx - m * 0.75, cy, cx + m * 0.75, cy, fill=cor, width=espessura * 1.3, capstyle="round")
    elif nome == "lapis":
        # Um lápis inclinado: o corpo (paralelogramo) e a ponta
        a = (cx - m * 0.85, cy + m * 0.85)
        canvas.create_polygon(a[0], a[1], a[0] + m * 0.15, a[1] - m * 0.45, cx + m * 0.55, cy - m * 0.95,
                              cx + m * 0.95, cy - m * 0.55, a[0] + m * 0.45, a[1] - m * 0.15,
                              fill=cor, outline=cor, joinstyle="round")
        canvas.create_line(cx + m * 0.3, cy - m * 0.7, cx + m * 0.7, cy - m * 0.3, fill=fundo, width=fina)
    elif nome == "lixeira":
        canvas.create_line(cx - m * 0.8, cy - m * 0.55, cx + m * 0.8, cy - m * 0.55, fill=cor, width=espessura,
                           capstyle="round")
        canvas.create_line(cx - m * 0.25, cy - m * 0.8, cx + m * 0.25, cy - m * 0.8, fill=cor, width=espessura,
                           capstyle="round")
        canvas.create_polygon(cx - m * 0.6, cy - m * 0.4, cx + m * 0.6, cy - m * 0.4, cx + m * 0.48, cy + m * 0.9,
                              cx - m * 0.48, cy + m * 0.9, fill=cor, outline=cor)
        for deslocamento in (-0.22, 0.22):
            canvas.create_line(cx + deslocamento * m, cy - m * 0.2, cx + deslocamento * m, cy + m * 0.65, fill=fundo,
                               width=fina)
    elif nome == "pasta":
        canvas.create_polygon(cx - m * 0.9, cy - m * 0.6, cx - m * 0.25, cy - m * 0.6, cx - m * 0.1, cy - m * 0.4,
                              cx + m * 0.9, cy - m * 0.4, cx + m * 0.9, cy + m * 0.75, cx - m * 0.9, cy + m * 0.75,
                              fill=cor, outline=cor, joinstyle="round")
    elif nome in ("arquivo", "bosco"):
        canvas.create_polygon(cx - m * 0.65, cy - m * 0.9, cx + m * 0.25, cy - m * 0.9, cx + m * 0.65, cy - m * 0.5,
                              cx + m * 0.65, cy + m * 0.9, cx - m * 0.65, cy + m * 0.9, fill=cor, outline=cor,
                              joinstyle="round")
        canvas.create_polygon(cx + m * 0.25, cy - m * 0.9, cx + m * 0.25, cy - m * 0.5, cx + m * 0.65, cy - m * 0.5,
                              fill=misturar(cor, fundo, 0.45), outline=fundo)
        if nome == "bosco":
            # O mini grafo do logo dentro da folha
            centros = [(cx - m * 0.3, cy - m * 0.1), (cx + m * 0.3, cy + m * 0.05), (cx - m * 0.1, cy + m * 0.55)]
            for i, j in ((0, 1), (1, 2), (2, 0)):
                canvas.create_line(*centros[i], *centros[j], fill=fundo, width=max(1, espessura / 1.4))
            for x, y in centros:
                r = m * 0.16
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=fundo, outline=fundo)
        else:
            for altura in (-0.1, 0.25, 0.6):
                canvas.create_line(cx - m * 0.4, cy + altura * m, cx + m * 0.4, cy + altura * m, fill=fundo, width=fina)
    elif nome in ("importar", "exportar"):
        canvas.create_line(cx - m * 0.85, cy + m * 0.25, cx - m * 0.85, cy + m * 0.85, cx + m * 0.85, cy + m * 0.85,
                           cx + m * 0.85, cy + m * 0.25, fill=cor, width=espessura, capstyle="round", joinstyle="round")
        if nome == "importar":
            canvas.create_line(cx, cy - m * 0.9, cx, cy + m * 0.45, fill=cor, width=espessura, arrow="last",
                               arrowshape=(m * 0.55, m * 0.55, m * 0.38))
        else:
            canvas.create_line(cx, cy + m * 0.45, cx, cy - m * 0.9, fill=cor, width=espessura, arrow="last",
                               arrowshape=(m * 0.55, m * 0.55, m * 0.38))
    elif nome == "imagem":
        canvas.create_rectangle(cx - m * 0.9, cy - m * 0.7, cx + m * 0.9, cy + m * 0.7, fill=cor, outline=cor)
        canvas.create_polygon(cx - m * 0.75, cy + m * 0.55, cx - m * 0.2, cy - m * 0.1, cx + m * 0.15, cy + m * 0.3,
                              cx + m * 0.4, cy + m * 0.05, cx + m * 0.75, cy + m * 0.55, fill=fundo, outline=fundo)
        r = m * 0.16
        canvas.create_oval(cx + m * 0.35 - r, cy - m * 0.38 - r, cx + m * 0.35 + r, cy - m * 0.38 + r, fill=fundo,
                           outline=fundo)
    elif nome == "sol":
        # O miolo e os raios. Pequeno (menos de 22 pixels), os raios viram bolinhas: risquinhos tão
        # curtos parecem um floco de neve.
        if lado < 22:
            r = m * 0.46
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor)
            for indice in range(8):
                angulo = indice * math.pi / 4
                x = cx + m * 0.82 * math.cos(angulo)
                y = cy + m * 0.82 * math.sin(angulo)
                r = max(0.9, m * 0.12)
                canvas.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline=cor)
        else:
            r = m * 0.42
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor)
            for indice in range(8):
                angulo = indice * math.pi / 4
                canvas.create_line(cx + m * 0.62 * math.cos(angulo), cy + m * 0.62 * math.sin(angulo),
                                   cx + m * 0.95 * math.cos(angulo), cy + m * 0.95 * math.sin(angulo),
                                   fill=cor, width=espessura, capstyle="round")
    elif nome == "lua":
        # A lua crescente: um círculo cheio e, por cima, um círculo da cor de fundo um pouco deslocado
        r = m * 0.8
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor)
        canvas.create_oval(cx - r + m * 0.55, cy - r - m * 0.3, cx + r + m * 0.55, cy + r - m * 0.3, fill=fundo,
                           outline=fundo)
    elif nome == "info":
        # Um círculo cheio com o "i" recortado (se lê bem até pequeno)
        canvas.create_oval(cx - m * 0.92, cy - m * 0.92, cx + m * 0.92, cy + m * 0.92, fill=cor, outline=cor)
        r = m * 0.14
        canvas.create_oval(cx - r, cy - m * 0.45 - r, cx + r, cy - m * 0.45 + r, fill=fundo, outline=fundo)
        canvas.create_line(cx, cy - m * 0.1, cx, cy + m * 0.55, fill=fundo, width=max(1.5, m * 0.26), capstyle="round")
    elif nome == "alerta":
        canvas.create_polygon(cx, cy - m * 0.9, cx + m * 0.95, cy + m * 0.8, cx - m * 0.95, cy + m * 0.8, fill=cor,
                              outline=cor, joinstyle="round", width=max(1, espessura / 2))
        canvas.create_line(cx, cy - m * 0.35, cx, cy + m * 0.25, fill=fundo, width=max(1.5, m * 0.2), capstyle="round")
        r = m * 0.11
        canvas.create_oval(cx - r, cy + m * 0.52 - r, cx + r, cy + m * 0.52 + r, fill=fundo, outline=fundo)
    elif nome in ("seta_esquerda", "seta_direita"):
        sinal = -1 if nome == "seta_esquerda" else 1
        canvas.create_line(cx - sinal * m * 0.8, cy, cx + sinal * m * 0.8, cy, fill=cor, width=espessura,
                           capstyle="round")
        canvas.create_line(cx + sinal * m * 0.1, cy - m * 0.65, cx + sinal * m * 0.8, cy, cx + sinal * m * 0.1,
                           cy + m * 0.65, fill=cor, width=espessura, capstyle="round", joinstyle="round")
    elif nome in ("chevron_direita", "chevron_baixo", "chevron_esquerda", "chevron_cima"):
        if nome == "chevron_direita":
            pontos = (cx - m * 0.25, cy - m * 0.55, cx + m * 0.3, cy, cx - m * 0.25, cy + m * 0.55)
        elif nome == "chevron_esquerda":
            pontos = (cx + m * 0.25, cy - m * 0.55, cx - m * 0.3, cy, cx + m * 0.25, cy + m * 0.55)
        elif nome == "chevron_baixo":
            pontos = (cx - m * 0.55, cy - m * 0.25, cx, cy + m * 0.3, cx + m * 0.55, cy - m * 0.25)
        else:
            pontos = (cx - m * 0.55, cy + m * 0.25, cx, cy - m * 0.3, cx + m * 0.55, cy + m * 0.25)
        canvas.create_line(*pontos, fill=cor, width=espessura * 1.15, capstyle="round", joinstyle="round")
    elif nome == "casa":
        canvas.create_polygon(cx, cy - m * 0.9, cx + m * 0.9, cy - m * 0.05, cx + m * 0.6, cy - m * 0.05,
                              cx + m * 0.6, cy + m * 0.85, cx - m * 0.6, cy + m * 0.85, cx - m * 0.6, cy - m * 0.05,
                              cx - m * 0.9, cy - m * 0.05, fill=cor, outline=cor, joinstyle="round")
        canvas.create_rectangle(cx - m * 0.18, cy + m * 0.25, cx + m * 0.18, cy + m * 0.85, fill=fundo, outline=fundo)
    elif nome == "olho":
        # O contorno do olho (duas curvas) e a pupila cheia
        canvas.create_polygon(cx - m * 0.95, cy, cx, cy - m * 0.68, cx + m * 0.95, cy, cx, cy + m * 0.68,
                              smooth=True, fill="", outline=cor, width=espessura)
        r = m * 0.3
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor)
    elif nome == "x":
        canvas.create_line(cx - m * 0.65, cy - m * 0.65, cx + m * 0.65, cy + m * 0.65, fill=cor, width=espessura * 1.2,
                           capstyle="round")
        canvas.create_line(cx - m * 0.65, cy + m * 0.65, cx + m * 0.65, cy - m * 0.65, fill=cor, width=espessura * 1.2,
                           capstyle="round")
    elif nome == "check":
        canvas.create_line(cx - m * 0.7, cy, cx - m * 0.15, cy + m * 0.55, cx + m * 0.75, cy - m * 0.6, fill=cor,
                           width=espessura * 1.3, capstyle="round", joinstyle="round")
    elif nome == "dado":
        retangulo_arredondado(canvas, cx - m * 0.85, cy - m * 0.85, cx + m * 0.85, cy + m * 0.85, m * 0.3, fill=cor,
                              outline=cor)
        r = m * 0.13
        for px, py in ((-0.42, -0.42), (0.42, -0.42), (0, 0), (-0.42, 0.42), (0.42, 0.42)):
            canvas.create_oval(cx + px * m - r, cy + py * m - r, cx + px * m + r, cy + py * m + r, fill=fundo,
                               outline=fundo)
    elif nome == "estrela":
        pontos = []
        for indice in range(10):
            raio = m * (0.95 if indice % 2 == 0 else 0.4)
            angulo = -math.pi / 2 + indice * math.pi / 5
            pontos += [cx + raio * math.cos(angulo), cy + raio * math.sin(angulo)]
        canvas.create_polygon(pontos, fill=cor, outline=cor, joinstyle="round")
    elif nome == "disquete":
        canvas.create_polygon(cx - m * 0.85, cy - m * 0.85, cx + m * 0.55, cy - m * 0.85, cx + m * 0.85, cy - m * 0.55,
                              cx + m * 0.85, cy + m * 0.85, cx - m * 0.85, cy + m * 0.85, fill=cor, outline=cor)
        canvas.create_rectangle(cx - m * 0.45, cy - m * 0.85, cx + m * 0.35, cy - m * 0.35, fill=fundo, outline=fundo)
        canvas.create_rectangle(cx - m * 0.5, cy + m * 0.15, cx + m * 0.5, cy + m * 0.7, fill=fundo, outline=fundo)
    elif nome == "grafo":
        centros = [(cx - m * 0.55, cy - m * 0.45), (cx + m * 0.6, cy - m * 0.2), (cx - m * 0.15, cy + m * 0.6)]
        for i, j in ((0, 1), (1, 2), (2, 0)):
            canvas.create_line(*centros[i], *centros[j], fill=cor, width=max(1, espessura / 1.2))
        for x, y in centros:
            r = m * 0.28
            canvas.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline=cor)
    elif nome in ("aresta_orientada", "aresta_simples"):
        # Dois vértices (bolinhas) ligados: com a ponta de seta (A → B) ou sem (A — B).
        # O desenho é mais largo que alto (vai um pouco além do quadrado, para os lados).
        r = m * 0.28
        for x in (cx - m * 0.85, cx + m * 0.85):
            canvas.create_oval(x - r, cy - r, x + r, cy + r, fill=cor, outline=cor)
        if nome == "aresta_orientada":
            canvas.create_line(cx - m * 0.55, cy, cx + m * 0.55, cy, fill=cor, width=max(1.5, espessura),
                               arrow="last", arrowshape=(m * 0.5, m * 0.5, m * 0.3))
        else:
            canvas.create_line(cx - m * 0.55, cy, cx + m * 0.55, cy, fill=cor, width=max(1.5, espessura))
    elif nome == "tela_cheia":
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            canvas.create_line(cx + sx * m * 0.85, cy + sy * m * 0.35, cx + sx * m * 0.85, cy + sy * m * 0.85,
                               cx + sx * m * 0.35, cy + sy * m * 0.85, fill=cor, width=espessura, capstyle="round",
                               joinstyle="round")
    elif nome == "codigo":
        canvas.create_line(cx - m * 0.35, cy - m * 0.6, cx - m * 0.9, cy, cx - m * 0.35, cy + m * 0.6, fill=cor,
                           width=espessura, capstyle="round", joinstyle="round")
        canvas.create_line(cx + m * 0.35, cy - m * 0.6, cx + m * 0.9, cy, cx + m * 0.35, cy + m * 0.6, fill=cor,
                           width=espessura, capstyle="round", joinstyle="round")
        canvas.create_line(cx + m * 0.15, cy - m * 0.8, cx - m * 0.15, cy + m * 0.8, fill=cor, width=espessura,
                           capstyle="round")
    elif nome == "lista":
        for altura in (-0.6, 0, 0.6):
            r = m * 0.13
            canvas.create_oval(cx - m * 0.85 - r, cy + altura * m - r, cx - m * 0.85 + r, cy + altura * m + r,
                               fill=cor, outline=cor)
            canvas.create_line(cx - m * 0.45, cy + altura * m, cx + m * 0.9, cy + altura * m, fill=cor,
                               width=espessura, capstyle="round")
    elif nome == "matriz":
        # Uma tabela 3 x 3: a moldura e as linhas de dentro (se lê bem até pequena)
        canvas.create_rectangle(cx - m * 0.85, cy - m * 0.85, cx + m * 0.85, cy + m * 0.85, fill="", outline=cor,
                                width=max(1.2, espessura * 0.9))
        for fracao in (-0.28, 0.28):
            canvas.create_line(cx + fracao * m, cy - m * 0.85, cx + fracao * m, cy + m * 0.85, fill=cor,
                               width=max(1, espessura * 0.7))
            canvas.create_line(cx - m * 0.85, cy + fracao * m, cx + m * 0.85, cy + fracao * m, fill=cor,
                               width=max(1, espessura * 0.7))
    elif nome == "relogio":
        canvas.create_oval(cx - m * 0.88, cy - m * 0.88, cx + m * 0.88, cy + m * 0.88, outline=cor, width=espessura)
        canvas.create_line(cx, cy - m * 0.55, cx, cy, cx + m * 0.4, cy + m * 0.25, fill=cor, width=espessura,
                           capstyle="round", joinstyle="round")
    elif nome == "lupa":
        r = m * 0.55
        canvas.create_oval(cx - m * 0.85, cy - m * 0.85, cx - m * 0.85 + 2 * r, cy - m * 0.85 + 2 * r, outline=cor,
                           width=espessura)
        canvas.create_line(cx + m * 0.2, cy + m * 0.2, cx + m * 0.85, cy + m * 0.85, fill=cor, width=espessura * 1.3,
                           capstyle="round")
    elif nome in ("pessoa", "pessoas"):
        if nome == "pessoas":
            # A segunda pessoa, atrás e um pouco mais clara
            atras = misturar(cor, fundo, 0.45)
            canvas.create_oval(cx + m * 0.05, cy - m * 0.85, cx + m * 0.75, cy - m * 0.15, fill=atras, outline=atras)
            canvas.create_polygon(pontos_do_circulo(cx + m * 0.4, cy + m * 0.85, m * 0.6, 12, math.pi, 2 * math.pi),
                                  fill=atras, outline=atras)
            cx -= m * 0.3
            escala = 0.85
        else:
            escala = 1.0
        r = m * 0.38 * escala
        canvas.create_oval(cx - r, cy - m * 0.5 * escala - r, cx + r, cy - m * 0.5 * escala + r, fill=cor, outline=cor)
        canvas.create_polygon(pontos_do_circulo(cx, cy + m * 0.92, m * 0.78 * escala, 14, math.pi, 2 * math.pi),
                              fill=cor, outline=cor)
    elif nome == "capelo":
        # O chapéu de formatura: o losango de cima, a base e a borla
        canvas.create_polygon(cx - m * 0.95, cy - m * 0.25, cx, cy - m * 0.7, cx + m * 0.95, cy - m * 0.25, cx, cy + m * 0.2,
                              fill=cor, outline=cor, joinstyle="round")
        canvas.create_polygon(cx - m * 0.55, cy, cx + m * 0.55, cy, cx + m * 0.55, cy + m * 0.5, cx, cy + m * 0.72,
                              cx - m * 0.55, cy + m * 0.5, fill=cor, outline=cor, joinstyle="round")
        canvas.create_line(cx + m * 0.8, cy - m * 0.3, cx + m * 0.8, cy + m * 0.45, fill=cor, width=fina)
    elif nome == "calendario":
        retangulo_arredondado(canvas, cx - m * 0.85, cy - m * 0.7, cx + m * 0.85, cy + m * 0.85, m * 0.15, fill="",
                              outline=cor, width=espessura)
        canvas.create_rectangle(cx - m * 0.85, cy - m * 0.7, cx + m * 0.85, cy - m * 0.3, fill=cor, outline=cor)
        for x in (-0.4, 0.4):
            canvas.create_line(cx + x * m, cy - m * 0.95, cx + x * m, cy - m * 0.55, fill=cor, width=espessura,
                               capstyle="round")
        r = m * 0.1
        for x in (-0.4, 0, 0.4):
            for y in (0.05, 0.45):
                canvas.create_oval(cx + x * m - r, cy + y * m - r, cx + x * m + r, cy + y * m + r, fill=cor, outline=cor)
    elif nome == "etiqueta":
        canvas.create_polygon(cx - m * 0.9, cy - m * 0.55, cx + m * 0.35, cy - m * 0.55, cx + m * 0.9, cy,
                              cx + m * 0.35, cy + m * 0.55, cx - m * 0.9, cy + m * 0.55, fill=cor, outline=cor,
                              joinstyle="round")
        r = m * 0.13
        canvas.create_oval(cx + m * 0.3 - r, cy - r, cx + m * 0.3 + r, cy + r, fill=fundo, outline=fundo)
    elif nome == "alvo":
        # O alvo (o destino da busca): dois anéis e o miolo cheio
        canvas.create_oval(cx - m * 0.9, cy - m * 0.9, cx + m * 0.9, cy + m * 0.9, outline=cor, width=espessura)
        canvas.create_oval(cx - m * 0.52, cy - m * 0.52, cx + m * 0.52, cy + m * 0.52, outline=cor, width=espessura)
        r = m * 0.2
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=cor, outline=cor)
    elif nome == "recarregar":
        # Uma volta quase completa com a ponta de seta no fim
        canvas.create_arc(cx - m * 0.75, cy - m * 0.75, cx + m * 0.75, cy + m * 0.75, start=60, extent=280,
                          style="arc", outline=cor, width=espessura)
        angulo = math.radians(60)
        px = cx + m * 0.75 * math.cos(angulo)
        py = cy - m * 0.75 * math.sin(angulo)
        canvas.create_polygon(px - m * 0.35, py - m * 0.3, px + m * 0.3, py - m * 0.05, px - m * 0.15, py + m * 0.4,
                              fill=cor, outline=cor)
    else:
        # Ícone desconhecido: um círculo (nunca dá erro)
        canvas.create_oval(cx - m * 0.5, cy - m * 0.5, cx + m * 0.5, cy + m * 0.5, outline=cor, width=espessura)


# Os ícones que existem (os testes desenham todos)
ICONES = ["play", "pausa", "anterior", "proximo", "primeiro", "ultimo", "mais", "mais_circulo", "menos", "lapis",
          "lixeira", "pasta", "arquivo", "bosco", "importar", "exportar", "imagem", "sol", "lua", "info", "alerta",
          "seta_esquerda", "seta_direita", "chevron_direita", "chevron_baixo", "chevron_esquerda", "chevron_cima",
          "casa", "olho", "x", "check", "dado", "estrela", "disquete", "grafo", "aresta_orientada", "aresta_simples",
          "tela_cheia", "codigo", "lista", "matriz", "relogio", "lupa", "pessoa", "pessoas", "capelo", "calendario",
          "etiqueta", "recarregar", "alvo"]
