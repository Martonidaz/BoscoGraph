# Janelinhas de diálogo do editor, com as cores do tema:
#   DialogoDeTexto        -> pede uma linha de texto (renomear um vértice ou uma aresta)
#   DialogoDeAresta       -> edita uma aresta inteira: de onde sai, para onde vai, o nome e o peso
#   DialogoDeArestas      -> edita todas as arestas como texto, uma por linha
#   DialogoDeConfirmacao  -> pergunta antes de fazer algo que não dá para desfazer
#   DialogoDePesos        -> escolhe onde aplicar pesos (arestas ou vértices), em quais e com que valores
#   DialogoDeInformacao   -> só mostra uma tabela de duas colunas (os atalhos do teclado) e um Fechar
#
# Os diálogos não "travam" o programa esperando a resposta. Eles recebem uma função
# (ao_confirmar) e a chamam quando o usuário clica em OK:
#   - se a função devolver "", deu certo e o diálogo fecha;
#   - se devolver um texto, é a explicação do problema: o diálogo mostra e continua aberto.
# Enquanto um diálogo está aberto, o grab_set() faz o resto do programa ignorar cliques (modal).

import tkinter as tk
from tkinter import ttk

import entrada
from visual.botoes import Botao, Segmentos, desenhar_icone
from visual.campos import CampoDeTexto, Contador, Interruptor, Seletor


class Dialogo:
    # Parte comum: cria a janelinha por cima da janela principal, com as cores do tema
    def __init__(self, app, titulo):
        self.app = app
        self.tema = app.tema
        self.janela = tk.Toplevel(app.raiz)
        self.janela.title(titulo)
        self.janela.configure(bg=self.tema["superficie"])
        self.janela.transient(app.raiz)         # fica sempre na frente da janela principal
        self.janela.resizable(False, False)
        self.janela.protocol("WM_DELETE_WINDOW", self.cancelar)    # o X da janela = Cancelar
        self.janela.bind("<Escape>", self.cancelar)
        self.quadro = ttk.Frame(self.janela, style="Cartao.TFrame", padding=16)
        self.quadro.pack(fill="both", expand=True)
        app.dialogo = self                      # o aplicativo sabe qual diálogo está aberto

    # Botões OK e Cancelar, alinhados à direita (colunas: quantas colunas da grade os botões atravessam)
    def montar_botoes(self, linha, texto_do_ok, colunas=2):
        botoes = ttk.Frame(self.quadro, style="Cartao.TFrame")
        botoes.grid(row=linha, column=0, columnspan=colunas, sticky="e", pady=(14, 0))
        fundo = self.tema["superficie"]
        Botao(botoes, self.app, "Cancelar", papel="neutro", comando=self.cancelar, fundo=fundo).pack(side="right")
        self.botao_ok = Botao(botoes, self.app, texto_do_ok, icone="check", papel="principal", comando=self.confirmar,
                              fundo=fundo)
        self.botao_ok.pack(side="right", padx=(0, 8))

    # Centraliza o diálogo em cima da janela principal e prende o foco nele
    def mostrar(self, campo_com_foco):
        self.janela.update_idletasks()
        largura = self.janela.winfo_reqwidth()
        altura = self.janela.winfo_reqheight()
        raiz = self.app.raiz
        x = raiz.winfo_rootx() + (raiz.winfo_width() - largura) // 2
        y = raiz.winfo_rooty() + (raiz.winfo_height() - altura) // 3
        self.janela.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.campo_com_foco = campo_com_foco
        self.tentativas = 10
        self.agendamento = self.janela.after_idle(self.prender)

    # Deixa o diálogo modal. Se a janelinha ainda não apareceu na tela, o grab_set() falha:
    # aí tenta de novo daqui a pouco (no máximo 10 vezes)
    def prender(self):
        self.agendamento = None
        try:
            self.janela.grab_set()
        except tk.TclError:
            self.tentativas -= 1
            if self.tentativas > 0:
                self.agendamento = self.janela.after(50, self.prender)
        self.campo_com_foco.focus_set()

    def fechar(self):
        if self.app.dialogo is self:
            self.app.dialogo = None
        if self.agendamento is not None:
            self.janela.after_cancel(self.agendamento)      # nada pode rodar depois que o diálogo some
            self.agendamento = None
        try:
            self.janela.grab_release()
        except tk.TclError:
            pass
        self.janela.destroy()

    def cancelar(self, evento=None):
        self.fechar()

    # Mostra o problema devolvido pela função ao_confirmar (ou fecha, se deu certo)
    def resultado(self, problema):
        if problema:
            self.rotulo_erro.configure(text=problema)
        else:
            self.fechar()


class DialogoDeTexto(Dialogo):
    def __init__(self, app, titulo, pergunta, valor_inicial, ao_confirmar):
        super().__init__(app, titulo)       # super() chama o __init__ da classe Dialogo (a parte comum)
        self.ao_confirmar = ao_confirmar
        self.valor = tk.StringVar(value=valor_inicial)

        ttk.Label(self.quadro, text=pergunta, style="Cartao.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        caixa = CampoDeTexto(self.quadro, app, self.valor, largura=30, fundo=self.tema["superficie"],
                             ao_enter=self.confirmar)
        caixa.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        campo = caixa.entrada
        campo.select_range(0, "end")        # o texto atual já vem selecionado: digitar substitui
        self.rotulo_erro = ttk.Label(self.quadro, style="Erro.TLabel", wraplength=320, justify="left")
        self.rotulo_erro.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.montar_botoes(3, "OK")
        self.mostrar(campo)

    def confirmar(self, evento=None):
        self.resultado(self.ao_confirmar(self.valor.get().strip()))
        return "break"


class DialogoDeAresta(Dialogo):
    # vertices: os nomes que dá para escolher; aresta: (origem, destino, nome, peso) como está agora;
    # posicao e total: o Nº da aresta (1 = a primeira) e quantas arestas há (a posição muda a ordem das listas);
    # foco: o campo que já vem com o cursor ("origem", "nome" ou "peso");
    # ao_confirmar(origem, destino, nome, texto_do_peso, posicao) devolve "" ou o problema.
    def __init__(self, app, titulo, vertices, aresta, direcionado, ao_confirmar, foco="nome", posicao=1, total=1):
        super().__init__(app, titulo)
        self.ao_confirmar = ao_confirmar
        origem, destino, nome, peso = aresta
        self.origem = tk.StringVar(value=origem)
        self.destino = tk.StringVar(value=destino)
        self.nome = tk.StringVar(value=nome)
        self.peso = tk.StringVar(value=entrada.formatar_numero(peso))
        self.posicao = tk.StringVar(value=str(posicao))
        fundo = self.tema["superficie"]
        q = self.quadro

        # 1ª linha: de onde sai -> para onde vai (com a seta, ou o traço no não orientado)
        ttk.Label(q, text="De", style="Cartao.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ligacao = ttk.Frame(q, style="Cartao.TFrame")
        ligacao.grid(row=0, column=1, sticky="w")
        self.escolha_origem = Seletor(ligacao, app, self.origem, vertices, fundo=fundo)
        self.escolha_origem.pack(side="left")
        lado = app.fontes["texto"].metrics("linespace")
        seta = tk.Canvas(ligacao, width=lado * 1.6, height=lado, bg=fundo, highlightthickness=0)
        seta.pack(side="left", padx=8)
        desenhar_icone(seta, "aresta_orientada" if direcionado else "aresta_simples", lado * 0.8, lado / 2, lado,
                       self.tema["texto_suave"], fundo)
        ttk.Label(ligacao, text="Para", style="Cartao.TLabel").pack(side="left", padx=(0, 8))
        self.escolha_destino = Seletor(ligacao, app, self.destino, vertices, fundo=fundo)
        self.escolha_destino.pack(side="left")

        # 2ª e 3ª linhas: o nome e o peso (os dois podem ficar vazios)
        ttk.Label(q, text="Nome", style="Cartao.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.campo_nome = CampoDeTexto(q, app, self.nome, largura=16, fundo=fundo, ao_enter=self.confirmar)
        self.campo_nome.grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(q, text="Peso", style="Cartao.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.campo_peso = CampoDeTexto(q, app, self.peso, largura=8, fundo=fundo, ao_enter=self.confirmar,
                                       centralizar=True)
        self.campo_peso.grid(row=2, column=1, sticky="w", pady=(8, 0))
        # A posição (o Nº): a ordem das arestas é a ordem em que os vizinhos entram nas listas de adjacência
        ttk.Label(q, text="Posição", style="Cartao.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 0))
        linha = ttk.Frame(q, style="Cartao.TFrame")
        linha.grid(row=3, column=1, sticky="w", pady=(8, 0))
        self.contador_da_posicao = Contador(linha, app, self.posicao, 1, max(1, total), fundo=fundo)
        self.contador_da_posicao.pack(side="left")
        ttk.Label(linha, text=f"de {total} (a ordem nas listas de adjacência)", style="CartaoSuave.TLabel").pack(
            side="left", padx=(10, 0))
        ttk.Label(q, text="Vazio = sem nome ou sem peso. Vírgula ou ponto nos decimais (2,5).",
                  style="CartaoSuave.TLabel").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.rotulo_erro = ttk.Label(q, style="Erro.TLabel", wraplength=360, justify="left")
        self.rotulo_erro.grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.montar_botoes(6, "OK")
        campos = {"origem": self.escolha_origem, "nome": self.campo_nome.entrada, "peso": self.campo_peso.entrada}
        self.mostrar(campos.get(foco, self.campo_nome.entrada))
        if foco in ("nome", "peso"):
            campos[foco].select_range(0, "end")

    def confirmar(self, evento=None):
        self.contador_da_posicao.confirmar()            # um número digitado e não confirmado também vale
        self.resultado(self.ao_confirmar(self.origem.get(), self.destino.get(), self.nome.get().strip(),
                                         self.peso.get().strip(), int(self.posicao.get())))
        return "break"


class DialogoDeArestas(Dialogo):
    def __init__(self, app, texto_inicial, ao_confirmar):
        super().__init__(app, "Editar arestas como texto")
        self.ao_confirmar = ao_confirmar
        self.criar_vertices = tk.BooleanVar(value=True)
        tema = self.tema

        explicacao = ("Uma aresta por linha (ou separadas por vírgula): A -> B, A-B ou A B.\n"
                      "O nome é opcional e vem depois de dois pontos: A -> B: e1\n"
                      "O peso é opcional e vem depois de um igual: A -> B = 5   ou   A -> B: e1 = 2,5\n"
                      "A ordem das linhas é a ordem de criação das arestas.")
        ttk.Label(self.quadro, text=explicacao, style="CartaoSuave.TLabel", justify="left").grid(
            row=0, column=0, columnspan=2, sticky="w")

        # A caixa de texto e a barra de rolagem ficam juntas num quadro só delas
        moldura = ttk.Frame(self.quadro, style="Cartao.TFrame")
        moldura.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        self.caixa = tk.Text(moldura, width=44, height=16, wrap="none", undo=True,
                             font=app.fontes["codigo"], bg=tema["codigo_fundo"], fg=tema["codigo_texto"],
                             insertbackground=tema["texto"], relief="flat", highlightthickness=1,
                             highlightbackground=tema["borda"], highlightcolor=tema["acento"], padx=6, pady=4)
        self.caixa.insert("1.0", texto_inicial)
        self.caixa.pack(side="left", fill="both", expand=True)
        rolagem = ttk.Scrollbar(moldura, orient="vertical", command=self.caixa.yview)
        rolagem.pack(side="left", fill="y")
        self.caixa.configure(yscrollcommand=rolagem.set)
        # Enter pula de linha dentro da caixa; Ctrl+Enter aplica
        self.caixa.bind("<Control-Return>", self.confirmar)

        Interruptor(self.quadro, app, "Criar os vértices que ainda não existem", self.criar_vertices,
                    fundo=tema["superficie"]).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.rotulo_erro = ttk.Label(self.quadro, style="Erro.TLabel", wraplength=400, justify="left")
        self.rotulo_erro.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.montar_botoes(4, "Aplicar (Ctrl+Enter)")
        self.mostrar(self.caixa)

    def confirmar(self, evento=None):
        texto = self.caixa.get("1.0", "end")
        self.resultado(self.ao_confirmar(texto, self.criar_vertices.get()))
        return "break"


class DialogoDeConfirmacao(Dialogo):
    def __init__(self, app, titulo, pergunta, texto_do_sim, ao_confirmar):
        super().__init__(app, titulo)
        self.ao_confirmar = ao_confirmar
        ttk.Label(self.quadro, text=pergunta, style="Cartao.TLabel", wraplength=380, justify="left").grid(
            row=0, column=0, columnspan=2, sticky="w")
        self.rotulo_erro = ttk.Label(self.quadro, style="Erro.TLabel", wraplength=380, justify="left")
        self.rotulo_erro.grid(row=1, column=0, columnspan=2, sticky="w")
        self.montar_botoes(2, texto_do_sim)
        self.janela.bind("<Return>", self.confirmar)
        self.mostrar(self.botao_ok)

    def confirmar(self, evento=None):
        self.resultado(self.ao_confirmar())
        return "break"


class DialogoDePesos(Dialogo):
    # contexto: as quantidades que aparecem nas opções e o que está disponível
    #   {"arestas": 24, "arestas_selecionadas": 3, "arestas_sem_peso": 24,
    #    "vertices": 16, "vertices_selecionados": 0, "vertices_sem_h": 16,
    #    "custo_real": "" (disponível) ou o motivo de não estar, "destino": "P", "lugar": "arestas"}
    # ao_confirmar(escolha) recebe um dicionário com o que foi escolhido e devolve "" ou o problema.
    def __init__(self, app, contexto, ao_confirmar):
        super().__init__(app, "Pesos e heurística")
        self.contexto = contexto
        self.ao_confirmar = ao_confirmar
        self.lugar = tk.StringVar(value=contexto["lugar"])
        self.quais = tk.StringVar(value="todas")
        self.valor = tk.StringVar(value="fixo")
        self.fixo = tk.StringVar(value="1")
        self.minimo = tk.StringVar(value="1")
        self.maximo = tk.StringVar(value="10")
        q = self.quadro

        # 1. Onde aplicar: nas arestas (o peso) ou nos vértices (a heurística h)
        fundo = self.tema["superficie"]
        ttk.Label(q, text="Aplicar em", style="TituloDoPainel.TLabel").grid(row=0, column=0, sticky="w")
        Segmentos(q, app, [("arestas", "Arestas (peso)", "aresta_orientada"),
                           ("vertices", "Vértices (heurística h)", "estrela")],
                  self.lugar, comando=self.atualizar, fundo=fundo).grid(row=1, column=0, columnspan=2, sticky="w",
                                                                      pady=(4, 10))

        # 2. Quais: todas, as selecionadas na tabela do editor ou só as que ainda não têm valor
        ttk.Label(q, text="Quais", style="TituloDoPainel.TLabel").grid(row=2, column=0, sticky="w")
        self.opcoes_quais = {}
        for linha, valor in ((3, "todas"), (4, "selecionadas"), (5, "sem_valor")):
            botao = ttk.Radiobutton(q, value=valor, variable=self.quais, command=self.atualizar)
            botao.grid(row=linha, column=0, columnspan=2, sticky="w", padx=(8, 0))
            self.opcoes_quais[valor] = botao

        # 3. Quais valores
        ttk.Label(q, text="Valor", style="TituloDoPainel.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 0))
        linha_fixo = ttk.Frame(q, style="Cartao.TFrame")
        linha_fixo.grid(row=7, column=0, columnspan=2, sticky="w", padx=(8, 0))
        ttk.Radiobutton(linha_fixo, text="O mesmo valor:", value="fixo", variable=self.valor,
                        command=self.atualizar).pack(side="left")
        caixa_fixo = CampoDeTexto(linha_fixo, app, self.fixo, largura=6, fundo=fundo, ao_enter=self.confirmar,
                                  centralizar=True)
        caixa_fixo.pack(side="left", padx=(6, 0))
        campo_fixo = caixa_fixo.entrada

        linha_sorteio = ttk.Frame(q, style="Cartao.TFrame")
        linha_sorteio.grid(row=8, column=0, columnspan=2, sticky="w", padx=(8, 0))
        ttk.Radiobutton(linha_sorteio, text="Sortear inteiros de", value="sortear", variable=self.valor,
                        command=self.atualizar).pack(side="left")
        CampoDeTexto(linha_sorteio, app, self.minimo, largura=5, fundo=fundo, ao_enter=self.confirmar,
                     centralizar=True).pack(side="left", padx=(6, 6))
        ttk.Label(linha_sorteio, text="até", style="Cartao.TLabel").pack(side="left")
        CampoDeTexto(linha_sorteio, app, self.maximo, largura=5, fundo=fundo, ao_enter=self.confirmar,
                     centralizar=True).pack(side="left", padx=(6, 0))

        self.opcao_custo_real = ttk.Radiobutton(q, value="custo_real", variable=self.valor, command=self.atualizar)
        self.opcao_custo_real.grid(row=9, column=0, columnspan=2, sticky="w", padx=(8, 0))
        self.opcao_admissivel = ttk.Radiobutton(q, value="admissivel", variable=self.valor, command=self.atualizar)
        self.opcao_admissivel.grid(row=10, column=0, columnspan=2, sticky="w", padx=(8, 0))
        self.opcao_remover = ttk.Radiobutton(q, value="remover", variable=self.valor, command=self.atualizar)
        self.opcao_remover.grid(row=11, column=0, columnspan=2, sticky="w", padx=(8, 0))

        # Prévia do que vai acontecer, atualizada a cada mudança
        self.rotulo_previa = ttk.Label(q, style="CartaoSuave.TLabel", wraplength=380, justify="left")
        self.rotulo_previa.grid(row=12, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.rotulo_erro = ttk.Label(q, style="Erro.TLabel", wraplength=380, justify="left")
        self.rotulo_erro.grid(row=13, column=0, columnspan=2, sticky="w", pady=(4, 0))
        self.montar_botoes(14, "Aplicar")
        for variavel in (self.fixo, self.minimo, self.maximo):
            variavel.trace_add("write", self.atualizar)
        self.janela.bind("<Return>", self.confirmar)
        self.atualizar()
        self.mostrar(campo_fixo)

    # Os textos das opções mudam com o lugar (arestas ou vértices) e com as quantidades
    def atualizar(self, *argumentos):
        contexto = self.contexto
        nas_arestas = self.lugar.get() == "arestas"
        if nas_arestas:
            textos = {"todas": f"Todas as arestas ({contexto['arestas']})",
                      "selecionadas": f"As selecionadas na tabela ({contexto['arestas_selecionadas']})",
                      "sem_valor": f"Só as que estão sem peso ({contexto['arestas_sem_peso']})"}
            selecionadas = contexto["arestas_selecionadas"]
        else:
            textos = {"todas": f"Todos os vértices ({contexto['vertices']})",
                      "selecionadas": f"Os selecionados na tabela ({contexto['vertices_selecionados']})",
                      "sem_valor": f"Só os que estão sem h ({contexto['vertices_sem_h']})"}
            selecionadas = contexto["vertices_selecionados"]
        for valor in textos:
            self.opcoes_quais[valor].configure(text=textos[valor])
        if selecionadas == 0:
            self.opcoes_quais["selecionadas"].state(["disabled"])
            if self.quais.get() == "selecionadas":
                self.quais.set("todas")
        else:
            self.opcoes_quais["selecionadas"].state(["!disabled"])

        # As opções do custo real só valem para a heurística (e precisam de destino e de pesos)
        destino = contexto["destino"] or "o destino"
        self.opcao_custo_real.configure(text=f"Custo real até {destino} (h perfeita)")
        self.opcao_admissivel.configure(text=f"Admissível sorteada (entre 0 e o custo real até {destino})")
        self.opcao_remover.configure(text="Tirar o peso" if nas_arestas else "Tirar a heurística")
        for opcao in (self.opcao_custo_real, self.opcao_admissivel):
            if nas_arestas:
                opcao.grid_remove()
            else:
                opcao.grid()
                if contexto["custo_real"]:
                    opcao.state(["disabled"])
                else:
                    opcao.state(["!disabled"])
        if self.valor.get() in ("custo_real", "admissivel") and (nas_arestas or contexto["custo_real"]):
            self.valor.set("fixo")
        self.rotulo_previa.configure(text=self.previa())
        self.rotulo_erro.configure(text="")

    # "Vai dar peso 1 a 24 arestas." (o que o Aplicar vai fazer, antes de fazer)
    def previa(self):
        contexto = self.contexto
        nas_arestas = self.lugar.get() == "arestas"
        chave_da_quantidade = {"todas": "arestas", "selecionadas": "arestas_selecionadas",
                               "sem_valor": "arestas_sem_peso"}
        if not nas_arestas:
            chave_da_quantidade = {"todas": "vertices", "selecionadas": "vertices_selecionados",
                                   "sem_valor": "vertices_sem_h"}
        quantidade = contexto[chave_da_quantidade[self.quais.get()]]
        if nas_arestas:
            coisas = "1 aresta" if quantidade == 1 else f"{quantidade} arestas"
        else:
            coisas = "1 vértice" if quantidade == 1 else f"{quantidade} vértices"
        if quantidade == 0:
            return "Nenhum item nessa escolha."
        nome = "peso" if nas_arestas else "h"
        valor = self.valor.get()
        if valor == "fixo":
            return f"Vai dar {nome} {self.fixo.get().strip()} a {coisas}."
        if valor == "sortear":
            return f"Vai sortear {nome} de {self.minimo.get().strip()} a {self.maximo.get().strip()} para {coisas}."
        if valor == "custo_real":
            texto = f"Vai calcular h = custo real até {contexto['destino']} para {coisas}."
            return texto + " Quem não chega ao destino fica com h = 0."
        if valor == "admissivel":
            return (f"Vai sortear h entre 0 e o custo real até {contexto['destino']} para {coisas}: "
                    f"a heurística fica admissível.")
        return f"Vai tirar o {nome} de {coisas}."

    def confirmar(self, evento=None):
        escolha = {"lugar": self.lugar.get(), "quais": self.quais.get(), "valor": self.valor.get(),
                   "fixo": self.fixo.get(), "minimo": self.minimo.get(), "maximo": self.maximo.get()}
        self.resultado(self.ao_confirmar(escolha))
        return "break"


class DialogoDeInformacao(Dialogo):
    # linhas: [(o que está à esquerda, em negrito; o texto da direita), ...]
    def __init__(self, app, titulo, linhas):
        super().__init__(app, titulo)
        for numero in range(len(linhas)):
            esquerda, direita = linhas[numero]
            ttk.Label(self.quadro, text=esquerda, style="TituloDoPainel.TLabel").grid(
                row=numero, column=0, sticky="w", padx=(0, 18), pady=1)
            ttk.Label(self.quadro, text=direita, style="Cartao.TLabel").grid(row=numero, column=1, sticky="w", pady=1)
        botao = Botao(self.quadro, app, "Fechar", papel="principal", comando=self.cancelar,
                      fundo=self.tema["superficie"])
        botao.grid(row=len(linhas), column=0, columnspan=2, sticky="e", pady=(14, 0))
        self.janela.bind("<Return>", self.cancelar)
        self.mostrar(botao)
