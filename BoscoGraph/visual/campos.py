# Os campos de formulário do BoscoGraph, desenhados num Canvas como os botões de visual/botoes.py.
# Os campos comuns do Tkinter (Entry, Spinbox, Checkbutton, Combobox) são retângulos cinza com cara de
# programa antigo; estes têm cantos arredondados, a borda azul quando o cursor está neles e as cores do tema:
#   CampoDeTexto   -> a caixa de texto (o Entry do Tkinter fica dentro de uma moldura arredondada)
#   Contador       -> [ − 8 + ]: um número que muda pelos botões, pelas setas ↑/↓ ou digitando e Enter
#   Interruptor    -> a chave liga/desliga (como a do celular), com o texto ao lado
#   Seletor        -> a caixa de escolha: mostra a opção escolhida e abre a lista ao clicar
#   Selo           -> uma etiqueta colorida em forma de pílula: "● Alterações não salvas"
#   EscolhaDaBusca -> as buscas em colunas, uma por tipo (Sem pesos, Menor custo, Com heurística, Árvore
#                     geradora mínima)
#
# Todos recebem o "app" (as fontes, o tema e o zoom) e têm o remedir(), chamado depois de uma mudança de
# zoom (Ctrl + roda do mouse) pelo redesenhar_componentes() de visual/botoes.py.

import tkinter as tk

import algoritmos
from visual.botoes import TAMANHOS, Botao, desenhar_icone
from visual.dica import Dica
from visual.logo import retangulo_arredondado
from visual.tema import misturar

# A animação da chave liga/desliga: quantos quadros e quantos milissegundos entre eles
QUADROS_DO_INTERRUPTOR = 6
MILISSEGUNDOS_DO_INTERRUPTOR = 16


# O componente que está embaixo do mouse agora (None se for outro programa ou um menu aberto)
def componente_embaixo_do_mouse(componente):
    try:
        x, y = componente.winfo_pointerxy()
        return componente.winfo_containing(x, y)
    except (tk.TclError, KeyError):
        return None


# ----------------------------------------------------------------------
# A caixa de texto
# ----------------------------------------------------------------------

class CampoDeTexto(tk.Canvas):
    # variavel: a StringVar do texto; largura: em letras; ao_enter: chamada quando a pessoa aperta Enter;
    # centralizar: o texto no meio (os números curtos, como o peso, ficam melhor assim)
    def __init__(self, pai, app, variavel, largura=10, fundo=None, ao_enter=None, dica=None, centralizar=False):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["superficie"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo, cursor="xterm")
        self.variavel = variavel
        self.letras = largura
        self.ao_enter = ao_enter
        self.com_foco = False
        self.mouse_em_cima = False
        self.com_erro = False               # True = a borda fica vermelha (o texto tem um problema)
        self.habilitado = True
        tema = self.tema
        # O Entry de verdade, sem borda nenhuma: a moldura é desenhada pelo Canvas, em volta dele
        self.entrada = tk.Entry(self, textvariable=variavel, width=largura, relief="flat", bd=0, highlightthickness=0,
                                bg=tema["superficie"], fg=tema["texto"], insertbackground=tema["texto"],
                                disabledbackground=tema["fundo"], disabledforeground=tema["texto_suave"],
                                selectbackground=tema["acento"], selectforeground=tema["texto_acento"],
                                font=app.fontes["texto"], justify="center" if centralizar else "left")
        self.janela = self.create_window(0, 0, window=self.entrada, anchor="w")
        self.entrada.bind("<FocusIn>", lambda evento: self.mudar_foco(True), add="+")
        self.entrada.bind("<FocusOut>", lambda evento: self.mudar_foco(False), add="+")
        # Digitar tira o vermelho do erro: a pessoa já está corrigindo
        self.entrada.bind("<Key>", lambda evento: self.marcar_erro(False), add="+")
        for componente in (self, self.entrada):
            componente.bind("<Enter>", self.conferir_mouse, add="+")
            componente.bind("<Leave>", self.conferir_mouse, add="+")
        # Um clique na moldura (fora do Entry) também leva o cursor para a caixa
        self.bind("<Button-1>", lambda evento: self.focar())
        if ao_enter is not None:
            self.entrada.bind("<Return>", self.enter)
            self.entrada.bind("<KP_Enter>", self.enter)
        self.bind("<Configure>", lambda evento: self.desenhar())
        if dica:
            Dica(self.entrada, dica)
        self.medir()
        self.desenhar()

    def medidas(self):
        zoom = self.app.zoom
        return round(10 * zoom), round(6 * zoom), round(7 * zoom)        # folga dos lados, folga de cima, raio

    def medir(self):
        fonte = self.app.fontes["texto"]
        folga_x, folga_y, raio = self.medidas()
        self.entrada.configure(font=fonte)
        self.largura = fonte.measure("0") * self.letras + 2 * folga_x + 4
        self.altura = fonte.metrics("linespace") + 2 * folga_y + 2
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def tamanho_atual(self):
        largura = self.winfo_width()
        altura = self.winfo_height()
        if largura <= 1 or altura <= 1:
            return self.largura, self.altura
        return largura, altura

    def desenhar(self):
        self.delete("moldura")
        tema = self.tema
        largura, altura = self.tamanho_atual()
        folga_x, folga_y, raio = self.medidas()
        if self.com_erro:
            cor = tema["erro"]
        elif self.com_foco:
            cor = tema["acento"]
        elif self.mouse_em_cima and self.habilitado:
            cor = tema["texto_suave"]
        else:
            cor = tema["borda"]
        preenchimento = tema["superficie"] if self.habilitado else tema["fundo"]
        espessura = 2 if (self.com_foco or self.com_erro) else 1
        retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, raio, fill=preenchimento, outline=cor,
                              width=espessura, tags="moldura")
        self.tag_lower("moldura")
        # O Entry ocupa o miolo da moldura (o Canvas desenha a "janela" dele sempre por cima)
        self.coords(self.janela, folga_x, altura / 2)
        self.itemconfigure(self.janela, width=max(10, largura - 2 * folga_x))

    def conferir_mouse(self, evento=None):
        dentro = componente_embaixo_do_mouse(self) in (self, self.entrada)
        if dentro != self.mouse_em_cima:
            self.mouse_em_cima = dentro
            self.desenhar()

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()

    def marcar_erro(self, com_erro=True):
        if com_erro != self.com_erro:
            self.com_erro = com_erro
            self.desenhar()

    # Leva o cursor para a caixa, com o texto todo selecionado (digitar já substitui)
    def focar(self):
        if not self.habilitado:
            return
        self.entrada.focus_set()
        self.entrada.select_range(0, "end")
        self.entrada.icursor("end")

    def enter(self, evento=None):
        if self.habilitado and self.ao_enter is not None:
            self.ao_enter()
        return "break"          # o Enter para aqui (não chega aos atalhos da janela)

    def ligar(self, habilitado):
        self.habilitado = habilitado
        self.entrada.configure(state="normal" if habilitado else "disabled")
        self.desenhar()


# ----------------------------------------------------------------------
# O contador: [ − 8 + ]
# ----------------------------------------------------------------------

class Contador(tk.Canvas):
    # variavel: a StringVar com o número (em texto, como aparece na caixa); minimo e maximo: os limites;
    # ao_mudar(numero): chamada quando o número muda pelos botões, pelas setas ou pelo Enter
    # (quem usa o contador decide o que fazer com o número novo: o editor já aplica na hora)
    def __init__(self, pai, app, variavel, minimo=0, maximo=99, ao_mudar=None, fundo=None, dica=None, letras=3):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["superficie"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo)
        self.variavel = variavel
        self.minimo = minimo
        self.maximo = maximo
        self.ao_mudar = ao_mudar
        self.letras = letras
        self.habilitado = True
        self.com_foco = False
        self.em_cima = None             # "menos", "mais" ou None: o botão com o mouse em cima
        self.apertado = None            # o botão apertado agora
        self.ultimo = self.numero_digitado()        # o último número aplicado (volta para ele se digitarem errado)
        if self.ultimo is None:
            self.ultimo = minimo
        tema = self.tema
        self.entrada = tk.Entry(self, textvariable=variavel, width=letras, justify="center", relief="flat", bd=0,
                                highlightthickness=0, bg=tema["superficie"], fg=tema["texto"],
                                insertbackground=tema["texto"], disabledbackground=tema["fundo"],
                                disabledforeground=tema["texto_suave"], selectbackground=tema["acento"],
                                selectforeground=tema["texto_acento"], font=app.fontes["negrito"])
        self.janela = self.create_window(0, 0, window=self.entrada)
        self.entrada.bind("<Return>", self.confirmar)
        self.entrada.bind("<KP_Enter>", self.confirmar)
        self.entrada.bind("<FocusOut>", self.ao_sair, add="+")
        self.entrada.bind("<FocusIn>", lambda evento: self.mudar_foco(True), add="+")
        self.entrada.bind("<Up>", lambda evento: self.passo(1))
        self.entrada.bind("<Down>", lambda evento: self.passo(-1))
        self.bind("<Motion>", self.moveu)
        self.bind("<Leave>", self.saiu)
        self.bind("<ButtonPress-1>", self.apertou)
        self.bind("<ButtonRelease-1>", self.soltou)
        self.bind("<Configure>", lambda evento: self.desenhar())
        if dica:
            Dica(self, dica)
        self.medir()
        self.desenhar()

    def numero_digitado(self):
        try:
            return int(self.variavel.get().strip())
        except (ValueError, tk.TclError):
            return None

    # Mostra um número sem chamar o ao_mudar (o editor usa quando o número muda por outro caminho)
    def mostrar(self, numero):
        self.ultimo = numero
        self.variavel.set(str(numero))
        self.desenhar()

    def mudar_limites(self, minimo, maximo):
        self.minimo = minimo
        self.maximo = maximo
        self.desenhar()

    def medidas(self):
        fonte = self.app.fontes["texto"]
        altura = fonte.metrics("linespace") + 2 * round(6 * self.app.zoom) + 2
        lado = altura - 6                               # os botões redondos dos lados
        miolo = self.app.fontes["negrito"].measure("0") * self.letras + round(10 * self.app.zoom)
        return altura, lado, miolo

    def medir(self):
        altura, lado, miolo = self.medidas()
        self.entrada.configure(font=self.app.fontes["negrito"])
        self.largura = 2 * (lado + 4) + miolo
        self.altura = altura
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    # Onde fica cada botão: (centro x, centro y, raio)
    def botao(self, qual):
        altura, lado, miolo = self.medidas()
        largura = self.winfo_width() if self.winfo_width() > 1 else self.largura
        cy = altura / 2
        if qual == "menos":
            return 3 + lado / 2, cy, lado / 2
        return largura - 3 - lado / 2, cy, lado / 2

    def botao_em(self, x, y):
        for qual in ("menos", "mais"):
            cx, cy, raio = self.botao(qual)
            if (x - cx) ** 2 + (y - cy) ** 2 <= (raio + 2) ** 2:
                return qual
        return None

    # O botão está liberado? (no mínimo, o "−" não faz nada; no máximo, o "+")
    def botao_liberado(self, qual):
        if not self.habilitado:
            return False
        atual = self.numero_digitado()
        if atual is None:
            atual = self.ultimo
        if qual == "menos":
            return atual > self.minimo
        return atual < self.maximo

    def desenhar(self):
        if not self.winfo_exists():
            return
        # Apaga tudo o que foi desenhado, menos a "janela" com a caixa do número
        for item in self.find_all():
            if item != self.janela:
                self.delete(item)
        tema = self.tema
        altura, lado, miolo = self.medidas()
        largura = self.winfo_width() if self.winfo_width() > 1 else self.largura
        borda = tema["acento"] if self.com_foco else tema["borda"]
        preenchimento = tema["superficie"] if self.habilitado else tema["fundo"]
        retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, (altura - 2) / 2, fill=preenchimento, outline=borda,
                              width=2 if self.com_foco else 1)
        for qual in ("menos", "mais"):
            cx, cy, raio = self.botao(qual)
            liberado = self.botao_liberado(qual)
            tom = 0.08
            if liberado and self.apertado == qual:
                tom = 0.30
            elif liberado and self.em_cima == qual:
                tom = 0.18
            cor = tema["acento"] if liberado else tema["borda"]
            fundo_do_botao = misturar(preenchimento, tema["acento"], tom if liberado else 0.0)
            self.create_oval(cx - raio, cy - raio, cx + raio, cy + raio, fill=fundo_do_botao, outline="")
            desenhar_icone(self, qual, cx, cy, raio * 1.15, cor, fundo_do_botao)
        self.coords(self.janela, largura / 2, altura / 2)
        self.itemconfigure(self.janela, width=max(16, largura - 2 * (lado + 6)))
        self.configure(cursor="hand2" if self.em_cima and self.botao_liberado(self.em_cima) else "")

    def moveu(self, evento):
        qual = self.botao_em(evento.x, evento.y)
        if qual != self.em_cima:
            self.em_cima = qual
            self.desenhar()

    def saiu(self, evento=None):
        self.em_cima = None
        self.apertado = None
        self.desenhar()

    def apertou(self, evento):
        self.apertado = self.botao_em(evento.x, evento.y)
        self.desenhar()

    def soltou(self, evento):
        qual = self.apertado
        self.apertado = None
        if qual is not None and qual == self.botao_em(evento.x, evento.y) and self.botao_liberado(qual):
            self.passo(-1 if qual == "menos" else 1)
        else:
            self.desenhar()

    # Um a mais ou um a menos (os botões e as setas ↑/↓)
    def passo(self, sentido):
        if not self.habilitado:
            return "break"
        atual = self.numero_digitado()
        if atual is None:
            atual = self.ultimo
        self.aplicar(max(self.minimo, min(self.maximo, atual + sentido)))
        return "break"

    # Enter: aplica o número digitado (fora dos limites, fica no limite; texto que não é número volta ao último)
    def confirmar(self, evento=None):
        if not self.winfo_exists() or not self.habilitado:
            return "break"
        numero = self.numero_digitado()
        if numero is None:
            self.mostrar(self.ultimo)
            return "break"
        self.aplicar(max(self.minimo, min(self.maximo, numero)))
        return "break"

    # Sair da caixa com o Tab ou com o mouse também confirma o número digitado
    def ao_sair(self, evento=None):
        self.com_foco = False
        if self.winfo_exists() and self.numero_digitado() != self.ultimo:
            self.confirmar()
        else:
            self.desenhar()

    def aplicar(self, numero):
        mudou = numero != self.ultimo
        self.mostrar(numero)
        if mudou and self.ao_mudar is not None:
            self.ao_mudar(numero)

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()

    def ligar(self, habilitado):
        self.habilitado = habilitado
        self.entrada.configure(state="normal" if habilitado else "disabled")
        self.desenhar()


# ----------------------------------------------------------------------
# A chave liga/desliga
# ----------------------------------------------------------------------

class Interruptor(tk.Canvas):
    # texto: o que a chave liga ("Laços", "Ordenar as listas"); variavel: a BooleanVar;
    # comando: chamado depois de cada troca (sem argumentos)
    def __init__(self, pai, app, texto, variavel, comando=None, fundo=None, dica=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["superficie"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo, cursor="hand2", takefocus=1)
        self.texto = texto
        self.variavel = variavel
        self.comando = comando
        self.habilitado = True
        self.mouse_em_cima = False
        self.com_foco = False
        self.posicao = 1.0 if variavel.get() else 0.0      # 0 = bolinha à esquerda (desligado), 1 = à direita
        self.animando = None
        self.trocando = False           # True enquanto a própria chave muda a variável (a animação cuida)
        self.bind("<ButtonRelease-1>", self.clicou)
        self.bind("<space>", self.alternar)
        self.bind("<Return>", self.alternar)
        self.bind("<KP_Enter>", self.alternar)
        self.bind("<Enter>", lambda evento: self.mudar_mouse(True))
        self.bind("<Leave>", lambda evento: self.mudar_mouse(False))
        self.bind("<FocusIn>", lambda evento: self.mudar_foco(True))
        self.bind("<FocusOut>", lambda evento: self.mudar_foco(False))
        self.bind("<Configure>", lambda evento: self.desenhar())
        # Se a variável mudar por outro caminho (o Ctrl+Z, por exemplo), a chave acompanha na hora
        self.observador = variavel.trace_add("write", lambda *argumentos: self.variavel_mudou())
        self.bind("<Destroy>", self.ao_destruir, add="+")
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

    def medidas(self):
        fonte = self.app.fontes["texto"]
        trilho_altura = round(fonte.metrics("linespace") * 1.05)
        trilho_largura = round(trilho_altura * 1.85)
        return trilho_largura, trilho_altura, round(8 * self.app.zoom)      # ..., espaço até o texto

    def medir(self):
        fonte = self.app.fontes["texto"]
        trilho_largura, trilho_altura, espaco = self.medidas()
        self.largura = 4 + trilho_largura + espaco + fonte.measure(self.texto) + 6
        self.altura = max(trilho_altura, fonte.metrics("linespace")) + round(8 * self.app.zoom)
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def desenhar(self):
        if not self.winfo_exists():
            return
        self.delete("all")
        tema = self.tema
        trilho_largura, trilho_altura, espaco = self.medidas()
        altura = self.winfo_height() if self.winfo_height() > 1 else self.altura
        cy = altura / 2
        x1 = 3
        x2 = x1 + trilho_largura
        ligado = tema["acento"] if self.habilitado else tema["texto_suave"]
        desligado = tema["borda"]
        # A cor do trilho passa aos poucos do cinza para o azul durante a animação
        cor_do_trilho = misturar(desligado, ligado, self.posicao)
        contorno = ""
        if self.habilitado and (self.mouse_em_cima or self.com_foco):
            contorno = misturar(cor_do_trilho, tema["texto"], 0.25)
        retangulo_arredondado(self, x1, cy - trilho_altura / 2, x2, cy + trilho_altura / 2, trilho_altura / 2,
                              fill=cor_do_trilho, outline=contorno or cor_do_trilho)
        raio = trilho_altura / 2 - 3
        centro = x1 + 3 + raio + (trilho_largura - 6 - 2 * raio) * self.posicao
        self.create_oval(centro - raio, cy - raio, centro + raio, cy + raio, fill="#ffffff",
                         outline=misturar("#ffffff", "#000000", 0.15))
        cor_do_texto = tema["texto"] if self.habilitado else tema["texto_suave"]
        self.create_text(x2 + espaco, cy, text=self.texto, anchor="w", fill=cor_do_texto, font=self.app.fontes["texto"])
        if self.com_foco:
            largura = self.winfo_width() if self.winfo_width() > 1 else self.largura
            retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, 6, fill="",
                                  outline=misturar(tema["texto_suave"], self.fundo, 0.3), dash=(2, 2))

    def clicou(self, evento):
        largura = self.winfo_width()
        if 0 <= evento.x <= largura and 0 <= evento.y <= self.winfo_height():
            self.alternar()

    def alternar(self, evento=None):
        if not self.habilitado:
            return "break"
        novo = not self.variavel.get()
        self.trocando = True
        self.variavel.set(novo)
        self.trocando = False
        self.animar(1.0 if novo else 0.0, 0)
        if self.comando is not None:
            self.comando()
        return "break"

    # A bolinha desliza até o outro lado (na janela escondida dos testes, vai direto)
    def animar(self, alvo, quadro):
        if self.animando is not None:
            self.after_cancel(self.animando)
            self.animando = None
        if not self.winfo_exists():
            return
        if quadro >= QUADROS_DO_INTERRUPTOR or not self.winfo_ismapped():
            self.posicao = alvo
            self.desenhar()
            return
        self.posicao += (alvo - self.posicao) * 0.5
        self.desenhar()
        self.animando = self.after(MILISSEGUNDOS_DO_INTERRUPTOR, lambda: self.animar(alvo, quadro + 1))

    def variavel_mudou(self):
        if self.trocando or not self.winfo_exists():
            return
        self.posicao = 1.0 if self.variavel.get() else 0.0
        self.desenhar()

    def mudar_mouse(self, em_cima):
        self.mouse_em_cima = em_cima
        self.desenhar()

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()

    def ligar(self, habilitado):
        self.habilitado = habilitado
        self.configure(cursor="hand2" if habilitado else "arrow")
        self.desenhar()


# ----------------------------------------------------------------------
# A caixa de escolha
# ----------------------------------------------------------------------

# As opções aceitam só o valor ("A") ou o par (valor, texto): (SEM_DESTINO, "nenhum")
def pares_das_opcoes(opcoes):
    pares = []
    for opcao in opcoes:
        if isinstance(opcao, tuple):
            pares.append(opcao)
        else:
            pares.append((opcao, str(opcao)))
    return pares


class Seletor(Botao):
    # variavel: a StringVar com o valor escolhido; opcoes: os valores (ou pares valor, texto);
    # comando: chamado depois de cada escolha (sem argumentos); vazio: o texto quando nada está escolhido
    def __init__(self, pai, app, variavel, opcoes=(), comando=None, fundo=None, dica=None, vazio="escolha",
                 icone=None, largura_minima=0):
        self.variavel = variavel
        self.opcoes = pares_das_opcoes(opcoes)
        self.vazio = vazio
        self.ao_escolher = comando
        self.largura_minima = largura_minima
        tema = app.tema
        self.lista = tk.Menu(pai, tearoff=False, bg=tema["superficie"], fg=tema["texto"],
                             activebackground=tema["acento"], activeforeground=tema["texto_acento"],
                             selectcolor=tema["acento"], font=app.fontes["texto"])
        super().__init__(pai, app, self.texto_atual(), icone=icone, papel="neutro", fundo=fundo, dica=dica,
                         menu=self.lista, antes_de_abrir=self.montar_lista)
        self.bind("<Up>", lambda evento: self.andar(-1))
        self.bind("<Down>", lambda evento: self.andar(1))
        # Se a variável mudar por outro caminho (o Ctrl+Z, por exemplo), o texto acompanha
        self.observador = variavel.trace_add("write", lambda *argumentos: self.variavel_mudou())
        self.bind("<Destroy>", self.ao_destruir, add="+")

    def ao_destruir(self, evento):
        if evento.widget is self and self.observador is not None:
            try:
                self.variavel.trace_remove("write", self.observador)
            except (tk.TclError, AttributeError):       # a variável já foi apagada (no fim do programa)
                pass
            self.observador = None

    def tem_valor(self):
        atual = self.variavel.get()
        for valor, texto in self.opcoes:
            if valor == atual:
                return True
        return False

    def texto_atual(self):
        atual = self.variavel.get()
        for valor, texto in self.opcoes:
            if valor == atual:
                return texto
        return self.vazio

    def mudar_opcoes(self, opcoes):
        pares = pares_das_opcoes(opcoes)
        if pares != self.opcoes:
            self.opcoes = pares
            self.texto = self.texto_atual()
            self.medir()
        self.variavel_mudou()

    def variavel_mudou(self):
        if not self.winfo_exists():
            return
        texto = self.texto_atual()
        if texto != self.texto:
            self.texto = texto
            self.medir()
        self.desenhar()

    # A lista é montada na hora de abrir (as opções mudam com o grafo)
    def montar_lista(self):
        self.lista.delete(0, "end")
        for valor, texto in self.opcoes:
            self.lista.add_radiobutton(label=texto, value=valor, variable=self.variavel, command=self.escolheu)

    def escolheu(self):
        self.variavel_mudou()
        if self.ao_escolher is not None:
            self.ao_escolher()

    # ↑ e ↓ trocam a escolha sem abrir a lista
    def andar(self, sentido):
        if not self.habilitado or not self.opcoes:
            return "break"
        valores = []
        for valor, texto in self.opcoes:
            valores.append(valor)
        atual = self.variavel.get()
        if atual in valores:
            posicao = max(0, min(len(valores) - 1, valores.index(atual) + sentido))
        else:
            posicao = 0
        if valores[posicao] != atual:
            self.variavel.set(valores[posicao])
            self.escolheu()
        return "break"

    # A largura é a da maior opção: a caixa não muda de tamanho a cada escolha
    def medir(self):
        medidas = TAMANHOS[self.tamanho]
        zoom = self.app.zoom
        fonte = self.fonte()
        altura_do_texto = fonte.metrics("linespace")
        self.lado_do_icone = round(altura_do_texto * 0.95)
        maior = fonte.measure(self.vazio)
        for valor, texto in self.opcoes:
            maior = max(maior, fonte.measure(texto))
        folga_x = round(medidas["folga_x"] * zoom)
        largura = maior + 2 * folga_x + round(self.lado_do_icone * 0.7) + round(10 * zoom)
        if self.icone:
            largura += self.lado_do_icone + round(8 * zoom)
        self.largura = max(largura, round(self.largura_minima * zoom))
        self.altura = altura_do_texto + 2 * round(medidas["folga_y"] * zoom)
        self.configure(width=self.largura, height=self.altura)

    def desenhar(self):
        self.delete("all")
        tema = self.tema
        largura, altura = self.tamanho_atual()
        zoom = self.app.zoom
        raio = round(TAMANHOS[self.tamanho]["raio"] * zoom)
        folga_x = round(TAMANHOS[self.tamanho]["folga_x"] * zoom)
        if not self.habilitado:
            fundo = tema["fundo"]
            borda = tema["borda"]
            cor_do_texto = tema["texto_suave"]
        else:
            fundo = tema["superficie"]
            if self.apertado:
                fundo = misturar(fundo, tema["acento"], 0.12)
            borda = tema["acento"] if (self.com_foco or self.mouse_em_cima) else tema["borda"]
            cor_do_texto = tema["texto"] if self.tem_valor() else tema["texto_suave"]
        retangulo_arredondado(self, 1, 1, largura - 1, altura - 1, raio, fill=fundo, outline=borda,
                              width=2 if self.com_foco else 1)
        x = folga_x
        if self.icone:
            desenhar_icone(self, self.icone, x + self.lado_do_icone / 2, altura / 2, self.lado_do_icone * 0.9,
                           cor_do_texto, fundo)
            x += self.lado_do_icone + round(8 * zoom)
        self.create_text(x, altura / 2, text=self.texto, anchor="w", fill=cor_do_texto, font=self.fonte())
        lado = self.lado_do_icone * 0.7
        cor_da_seta = tema["acento"] if (self.habilitado and self.mouse_em_cima) else tema["texto_suave"]
        desenhar_icone(self, "chevron_baixo", largura - folga_x - lado / 2, altura / 2, lado, cor_da_seta, fundo)


# ----------------------------------------------------------------------
# O selo: uma pílula colorida com um ícone e um texto curto
# ----------------------------------------------------------------------

class Selo(tk.Canvas):
    # icone: o nome de um ícone de visual/botoes.py, ou "bolinha" (um círculo cheio)
    def __init__(self, pai, app, texto="", cor=None, icone="bolinha", fundo=None, dica=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo)
        self.texto = texto
        self.cor = cor or app.tema["texto_suave"]
        self.icone = icone
        self.bind("<Configure>", lambda evento: self.desenhar())
        if dica:
            Dica(self, dica)
        self.medir()
        self.desenhar()

    def medir(self):
        fonte = self.app.fontes["negrito"]
        zoom = self.app.zoom
        if not self.texto:
            self.largura = 1
            self.altura = 1
        else:
            self.lado = round(fonte.metrics("linespace") * 0.8)
            self.largura = fonte.measure(self.texto) + self.lado + round(6 * zoom) + 2 * round(10 * zoom)
            self.altura = fonte.metrics("linespace") + 2 * round(4 * zoom)
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def mudar(self, texto, cor=None, icone=None):
        self.texto = texto
        if cor is not None:
            self.cor = cor
        if icone is not None:
            self.icone = icone
        self.medir()
        self.desenhar()

    def desenhar(self):
        self.delete("all")
        if not self.texto:
            return
        zoom = self.app.zoom
        fundo = misturar(self.fundo, self.cor, 0.14)
        retangulo_arredondado(self, 1, 1, self.largura - 1, self.altura - 1, (self.altura - 2) / 2, fill=fundo,
                              outline=misturar(self.fundo, self.cor, 0.35))
        x = round(10 * zoom)
        cy = self.altura / 2
        if self.icone == "bolinha":
            raio = self.lado * 0.28
            self.create_oval(x + self.lado / 2 - raio, cy - raio, x + self.lado / 2 + raio, cy + raio, fill=self.cor,
                             outline=self.cor)
        else:
            desenhar_icone(self, self.icone, x + self.lado / 2, cy, self.lado, self.cor, fundo)
        self.create_text(x + self.lado + round(6 * zoom), cy, text=self.texto, anchor="w", fill=self.cor,
                         font=self.app.fontes["negrito"])


# ----------------------------------------------------------------------
# A escolha da busca: uma coluna por tipo, com as buscas de cada uma
# ----------------------------------------------------------------------

class EscolhaDaBusca(tk.Canvas):
    # variavel: a StringVar com a chave da busca escolhida; comando: chamado depois de cada escolha
    def __init__(self, pai, app, variavel, comando=None, fundo=None):
        self.app = app
        self.tema = app.tema
        self.fundo = fundo or app.tema["fundo"]
        super().__init__(pai, highlightthickness=0, bd=0, bg=self.fundo, takefocus=1)
        self.variavel = variavel
        self.comando = comando
        self.tipos = algoritmos.TIPOS_DE_BUSCA
        self.em_cima = None             # a chave da busca com o mouse em cima
        self.com_foco = False
        self.areas = []                 # (x1, y1, x2, y2, chave): onde fica cada busca, para o clique
        self.bind("<Motion>", self.moveu)
        self.bind("<Leave>", self.saiu)
        self.bind("<ButtonRelease-1>", self.clicou)
        self.bind("<Up>", lambda evento: self.andar(-1))
        self.bind("<Down>", lambda evento: self.andar(1))
        self.bind("<Left>", lambda evento: self.trocar_de_coluna(-1))
        self.bind("<Right>", lambda evento: self.trocar_de_coluna(1))
        self.bind("<FocusIn>", lambda evento: self.mudar_foco(True))
        self.bind("<FocusOut>", lambda evento: self.mudar_foco(False))
        self.bind("<Configure>", lambda evento: self.desenhar())
        self.observador = variavel.trace_add("write", lambda *argumentos: self.desenhar())
        self.bind("<Destroy>", self.ao_destruir, add="+")
        self.medir()
        self.desenhar()

    def ao_destruir(self, evento):
        if evento.widget is self and self.observador is not None:
            try:
                self.variavel.trace_remove("write", self.observador)
            except (tk.TclError, AttributeError):       # a variável já foi apagada (no fim do programa)
                pass
            self.observador = None

    def medidas(self):
        zoom = self.app.zoom
        fontes = self.app.fontes
        linha = round(fontes["texto"].metrics("linespace") * 1.65)
        folga = round(12 * zoom)
        # O cabeçalho: a faixa, o título e o subtítulo, e um espaço antes da linha que separa as buscas
        cabecalho = (folga + 4 + fontes["negrito"].metrics("linespace") + fontes["pequena"].metrics("linespace")
                     + round(12 * zoom))
        return linha, cabecalho, folga, round(12 * zoom)      # linha, cabeçalho, folga, espaço entre as colunas

    def medir(self):
        linha, cabecalho, folga, espaco = self.medidas()
        maior_coluna = 0
        maior_nome = 0
        for tipo in self.tipos:
            maior_coluna = max(maior_coluna, len(tipo["buscas"]))
            for chave in tipo["buscas"]:
                maior_nome = max(maior_nome, self.app.fontes["negrito"].measure(algoritmos.algoritmo(chave)["nome"]))
        self.altura = cabecalho + maior_coluna * linha + folga + 2
        self.largura = len(self.tipos) * (maior_nome + 3 * folga + linha) + (len(self.tipos) - 1) * espaco
        self.configure(width=self.largura, height=self.altura)

    def remedir(self):
        self.medir()
        self.desenhar()

    def desenhar(self):
        if not self.winfo_exists():
            return
        self.delete("all")
        tema = self.tema
        fontes = self.app.fontes
        linha, cabecalho, folga, espaco = self.medidas()
        largura = self.winfo_width() if self.winfo_width() > 1 else self.largura
        altura = self.winfo_height() if self.winfo_height() > 1 else self.altura
        escolhida = self.variavel.get()
        quantidade = len(self.tipos)
        largura_da_coluna = (largura - 2 - (quantidade - 1) * espaco) / quantidade
        self.areas = []
        for indice in range(quantidade):
            tipo = self.tipos[indice]
            cor = tema[tipo["cor"]]
            x1 = 1 + indice * (largura_da_coluna + espaco)
            x2 = x1 + largura_da_coluna
            tem_a_escolhida = escolhida in tipo["buscas"]
            retangulo_arredondado(self, x1, 1, x2, altura - 1, round(10 * self.app.zoom), fill=tema["superficie"],
                                  outline=cor if tem_a_escolhida else tema["borda"], width=2 if tem_a_escolhida else 1)
            # O cabeçalho: uma faixa da cor do tipo, o título e o subtítulo
            self.create_rectangle(x1 + folga, folga - 2, x1 + folga + round(28 * self.app.zoom), folga + 1, fill=cor,
                                  outline=cor)
            self.create_text(x1 + folga, folga + 4, text=tipo["titulo"], anchor="nw", fill=cor, font=fontes["negrito"])
            self.create_text(x1 + folga, folga + 4 + fontes["negrito"].metrics("linespace"), text=tipo["subtitulo"],
                             anchor="nw", fill=tema["texto_suave"], font=fontes["pequena"])
            self.create_line(x1 + folga, cabecalho - 6, x2 - folga, cabecalho - 6, fill=tema["borda"])
            for posicao in range(len(tipo["buscas"])):
                chave = tipo["buscas"][posicao]
                y1 = cabecalho + posicao * linha
                y2 = y1 + linha
                self.desenhar_busca(chave, cor, x1 + 5, y1 + 2, x2 - 5, y2 - 2, chave == escolhida)
                self.areas.append((x1, y1, x2, y2, chave))

    def desenhar_busca(self, chave, cor, x1, y1, x2, y2, escolhida):
        tema = self.tema
        fontes = self.app.fontes
        raio = round(7 * self.app.zoom)
        fundo = tema["superficie"]
        if escolhida:
            fundo = misturar(tema["superficie"], cor, 0.15)
        elif chave == self.em_cima:
            fundo = misturar(tema["superficie"], cor, 0.07)
        if fundo != tema["superficie"]:
            retangulo_arredondado(self, x1, y1, x2, y2, raio, fill=fundo, outline=fundo)
        if escolhida and self.com_foco:
            retangulo_arredondado(self, x1 + 1, y1 + 1, x2 - 1, y2 - 1, raio, fill="",
                                  outline=misturar(cor, fundo, 0.3), dash=(2, 2))
        # A bolinha de escolha (como as do rádio): cheia na escolhida, só o contorno nas outras
        cy = (y1 + y2) / 2
        lado = fontes["texto"].metrics("linespace") * 0.85
        cx = x1 + 8 + lado / 2
        self.create_oval(cx - lado / 2, cy - lado / 2, cx + lado / 2, cy + lado / 2, fill=fundo,
                         outline=cor if escolhida else tema["texto_suave"], width=2)
        if escolhida:
            miolo = lado * 0.24
            self.create_oval(cx - miolo, cy - miolo, cx + miolo, cy + miolo, fill=cor, outline=cor)
        fonte = fontes["negrito"] if escolhida else fontes["texto"]
        informacoes = algoritmos.algoritmo(chave)
        texto = informacoes["nome"]
        espaco_do_nome = x2 - (cx + lado / 2 + 8) - 6
        # Sem espaço para o nome inteiro (janela estreita ou letras grandes): o nome curto ("Floyd-Warshall",
        # "BFS"...); se nem ele couber, é cortado com "…"
        if fontes["negrito"].measure(texto) > espaco_do_nome:
            texto = informacoes["nome_curto"]
        while fonte.measure(texto) > espaco_do_nome and len(texto) > 3:
            texto = texto[:-2] + "…"
        self.create_text(cx + lado / 2 + 8, cy, text=texto, anchor="w", fill=cor if escolhida else tema["texto"],
                         font=fonte)

    def busca_em(self, x, y):
        for x1, y1, x2, y2, chave in self.areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return chave
        return None

    def moveu(self, evento):
        chave = self.busca_em(evento.x, evento.y)
        self.configure(cursor="hand2" if chave else "")
        if chave != self.em_cima:
            self.em_cima = chave
            self.desenhar()

    def saiu(self, evento=None):
        if self.em_cima is not None:
            self.em_cima = None
            self.desenhar()

    def clicou(self, evento):
        chave = self.busca_em(evento.x, evento.y)
        if chave is not None:
            self.focus_set()
            self.escolher(chave)

    def escolher(self, chave):
        mudou = chave != self.variavel.get()
        self.variavel.set(chave)
        self.desenhar()
        if mudou and self.comando is not None:
            self.comando()

    # ↑ e ↓: a busca de cima ou de baixo (passando de um tipo para o outro)
    def andar(self, sentido):
        todas = []
        for tipo in self.tipos:
            todas += tipo["buscas"]
        atual = self.variavel.get()
        posicao = todas.index(atual) + sentido if atual in todas else 0
        self.escolher(todas[max(0, min(len(todas) - 1, posicao))])
        return "break"

    # ← e →: a mesma linha no tipo do lado (ou a última dele, se ele tiver menos buscas)
    def trocar_de_coluna(self, sentido):
        atual = self.variavel.get()
        coluna = algoritmos.tipo_da_busca(atual)
        buscas = self.tipos[coluna]["buscas"]
        linha = buscas.index(atual) if atual in buscas else 0
        nova = max(0, min(len(self.tipos) - 1, coluna + sentido))
        outras = self.tipos[nova]["buscas"]
        self.escolher(outras[min(linha, len(outras) - 1)])
        return "break"

    def mudar_foco(self, com_foco):
        self.com_foco = com_foco
        self.desenhar()
