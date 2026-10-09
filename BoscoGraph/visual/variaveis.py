# O painel "Variáveis": a memória do programa em Python naquele momento, como num depurador.
#
#   - à esquerda, a pilha de chamadas: a função que está rodando fica em cima (relaxar) e, embaixo
#     dela, quem a chamou (dijkstra) e, no fundo, o "programa" (o nível de fora das funções, com as
#     variáveis dele: nomes, adj, busca...). Cada uma com as suas variáveis (u, v, peso, novo...);
#   - à direita, os campos do objeto da busca (self.cor, self.d, self.pai, self.fila...). Os
#     dicionários abrem item por item (clique no triângulo).
# O que mudou desde o momento anterior fica em destaque (amarelo): é o efeito da linha que acabou de
# rodar. Embaixo aparece o valor inteiro da linha escolhida (os longos não cabem na coluna).

from tkinter import ttk

ABRIR_ATE = 12          # dicionários com até tantos itens começam abertos (os maiores, fechados)


class PainelDeVariaveis:
    def __init__(self, pai, janela):
        self.janela = janela
        self.quadro = ttk.Frame(pai, padding=6)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(1, weight=1)

        self.aviso = ttk.Label(self.quadro, style="Suave.TLabel", justify="left")
        self.aviso.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        divisao = ttk.PanedWindow(self.quadro, orient="horizontal")
        divisao.grid(row=1, column=0, sticky="nsew")
        self.arvore_da_pilha = self.criar_arvore(divisao, "Pilha de chamadas")
        self.arvore_dos_campos = self.criar_arvore(divisao, "Campos do objeto (self)")

        # O valor inteiro da linha escolhida
        self.detalhe = ttk.Label(self.quadro, style="Suave.TLabel", justify="left")
        self.detalhe.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.quadro.bind("<Configure>", self.ao_redimensionar)

        self.abertos = set()                # o que a pessoa abriu ou fechou fica assim nos próximos passos
        self.fechados = set()
        self.textos = {}                    # identificador -> (nome, texto inteiro), para o detalhe

    def criar_arvore(self, divisao, titulo):
        tema = self.janela.tema
        quadro = ttk.LabelFrame(divisao, text=titulo, padding=4)
        divisao.add(quadro, weight=1)
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        arvore = ttk.Treeview(quadro, columns=("valor",), show="tree headings", selectmode="browse")
        arvore.heading("#0", text="Nome", anchor="w")
        arvore.heading("valor", text="Valor", anchor="w")
        arvore.column("#0", width=160, minwidth=80, stretch=False)
        arvore.column("valor", width=170, minwidth=80, stretch=True, anchor="w")
        arvore.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(quadro, orient="vertical", command=arvore.yview)
        rolagem.grid(row=0, column=1, sticky="ns")
        arvore.configure(yscrollcommand=rolagem.set)
        arvore.tag_configure("funcao", foreground=tema["acento"], font=self.janela.fontes["negrito"])
        arvore.tag_configure("mudou", background=tema["fundo_destaque"], foreground=tema["texto"])
        arvore.bind("<<TreeviewSelect>>", self.ao_escolher)
        arvore.bind("<<TreeviewOpen>>", self.ao_abrir)
        arvore.bind("<<TreeviewClose>>", self.ao_fechar)
        return arvore

    def ao_redimensionar(self, evento):
        largura = max(200, evento.width - 20)
        self.aviso.configure(wraplength=largura)
        self.detalhe.configure(wraplength=largura)

    def ao_escolher(self, evento=None):
        texto = ""
        if evento is not None:
            escolhidos = evento.widget.selection()
            if escolhidos and escolhidos[0] in self.textos:
                nome, valor = self.textos[escolhidos[0]]
                texto = f"{nome} = {valor}"
        self.detalhe.configure(text=texto)

    def ao_abrir(self, evento):
        item = evento.widget.focus()
        self.abertos.add(item)
        self.fechados.discard(item)

    def ao_fechar(self, evento):
        item = evento.widget.focus()
        self.fechados.add(item)
        self.abertos.discard(item)

    # Mostra uma foto do rastreador (estudo/rastreador.py). "anterior" é a foto do momento de antes:
    # o que for diferente dela fica em destaque. "aviso" é o texto de cima (o que esta foto é).
    def mostrar(self, foto, anterior, aviso):
        self.aviso.configure(text=aviso)
        self.limpar()
        valores_antes = {}
        if anterior is not None:
            valores_antes = valores_da_foto(anterior)

        # A pilha: a função que está rodando em cima. O identificador conta a partir da chamada mais
        # antiga (a de baixo), para a mesma chamada manter o mesmo identificador quando a pilha cresce.
        arvore = self.arvore_da_pilha
        pilha = foto["pilha"]
        for posicao in range(len(pilha)):
            chamada = pilha[posicao]
            identificador = identificador_da_chamada(pilha, posicao)
            situacao = "rodando agora" if posicao == 0 else "esperando a de cima terminar"
            # Só as duas chamadas de cima começam abertas (numa recursão funda, a lista seria enorme)
            aberta = posicao < 2
            if identificador in self.abertos:
                aberta = True
            if identificador in self.fechados:
                aberta = False
            arvore.insert("", "end", iid=identificador, text=nome_da_chamada(chamada),
                          values=(f"linha {chamada['linha']} · {situacao}",), tags=("funcao",), open=aberta)
            self.inserir_valores(arvore, identificador, chamada["variaveis"], valores_antes)
        if not pilha:
            arvore.insert("", "end", iid="vazia", text="(nenhuma)", values=("a busca terminou",))
        self.inserir_valores(self.arvore_dos_campos, "", foto["campos"], valores_antes)

    def inserir_valores(self, arvore, pai, valores, valores_antes):
        for nome, texto, itens in valores:
            identificador = f"{pai}/{nome}"
            marcas = ()
            if valores_antes and valores_antes.get(identificador) != texto:
                marcas = ("mudou",)
            aberto = itens is not None and len(itens) <= ABRIR_ATE
            if identificador in self.abertos:
                aberto = True
            if identificador in self.fechados:
                aberto = False
            arvore.insert(pai, "end", iid=identificador, text=nome, values=(texto,), tags=marcas, open=aberto)
            self.textos[identificador] = (nome, texto)
            for chave, valor in itens or ():
                filho = f"{identificador}/{chave}"
                marcas = ()
                if valores_antes and valores_antes.get(filho) != valor:
                    marcas = ("mudou",)
                arvore.insert(identificador, "end", iid=filho, text=f"[{chave}]", values=(valor,), tags=marcas)
                self.textos[filho] = (f"{nome}[{chave}]", valor)

    def limpar(self):
        for arvore in (self.arvore_da_pilha, self.arvore_dos_campos):
            for item in arvore.get_children():
                arvore.delete(item)
        self.textos = {}
        self.detalhe.configure(text="")

    # Sem foto para mostrar (antes da busca, ou no passo a passo antes de a busca começar)
    def mostrar_vazio(self, aviso):
        self.aviso.configure(text=aviso)
        self.limpar()


# Como cada chamada aparece na pilha: "relaxar()", "programa" (o nível de fora das funções) ou
# "classe Dijkstra" (o corpo da classe, enquanto ela é criada)
def nome_da_chamada(chamada):
    tipo = chamada.get("tipo", "funcao")
    if tipo == "programa":
        return "programa"
    if tipo == "classe":
        return "classe " + chamada["funcao"]
    return chamada["funcao"] + "()"


def identificador_da_chamada(pilha, posicao):
    return f"chamada/{len(pilha) - 1 - posicao}/{pilha[posicao]['funcao']}"


# Os textos de uma foto por identificador (o mesmo esquema de PainelDeVariaveis.mostrar), para comparar
# duas fotos e achar o que mudou
def valores_da_foto(foto):
    valores = {}
    pilha = foto["pilha"]
    for posicao in range(len(pilha)):
        juntar_valores(identificador_da_chamada(pilha, posicao), pilha[posicao]["variaveis"], valores)
    juntar_valores("", foto["campos"], valores)
    return valores


def juntar_valores(pai, lista, valores):
    for nome, texto, itens in lista:
        identificador = f"{pai}/{nome}"
        valores[identificador] = texto
        for chave, valor in itens or ():
            valores[f"{identificador}/{chave}"] = valor
