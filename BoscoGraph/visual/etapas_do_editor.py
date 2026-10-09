# As três etapas do editor do grafo (visual/editor.py), cada uma numa tela:
#   EtapaDosVertices -> ① Vértices: um de cada vez | vários de uma vez | a tabela dos vértices
#   EtapaDasArestas  -> ② Arestas: orientação; uma de cada vez | sorteadas | a tabela das arestas
#   EtapaDaBusca     -> ③ Busca: as buscas em três colunas, as opções e o que falta para visualizar
# Nas duas primeiras, os controles ficam à esquerda (numa coluna que rola se a janela for baixa) e a
# tabela fica à direita, ocupando o resto da tela.
#
# Cada etapa só monta e mostra. Quem muda o grafo é o editor: os botões chamam as funções dele
# (editor.adicionar_vertice, editor.remover_arestas...), que guardam o estado anterior para o Ctrl+Z
# e depois chamam o atualizar() de todas as etapas.

import tkinter as tk
from tkinter import ttk

import algoritmos
import entrada
from visual.botoes import Botao, Lembrete, Segmentos, desenhar_icone
from visual.campos import CampoDeTexto, Contador, EscolhaDaBusca, Interruptor, Seletor
from visual.rolagem import QuadroRolavel
from visual.tema import misturar

SEM_DESTINO = "(nenhum)"            # o mesmo valor do editor: a busca não tem destino


class Etapa:
    def __init__(self, editor, pai):
        self.editor = editor
        self.app = editor.app
        self.tema = editor.tema
        self.fontes = editor.fontes
        self.quadro = ttk.Frame(pai)
        self.montar()

    def montar(self):
        pass

    def atualizar(self):
        pass

    # Chamada quando a etapa aparece (o cursor vai para o primeiro campo)
    def ao_mostrar(self):
        pass

    # Depois de uma mudança de zoom (os componentes desenhados já se medem sozinhos)
    def redesenhar(self):
        pass

    # ------------------------------------------------------------------
    # Peças que as três etapas usam
    # ------------------------------------------------------------------

    # O título da etapa, com a explicação ao lado: "Vértices   os pontos do grafo: ..."
    def criar_titulo(self, pai, linha, titulo, explicacao):
        quadro = ttk.Frame(pai)
        quadro.grid(row=linha, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(quadro, text=titulo, font=self.fontes["mensagem"]).pack(side="left")
        ttk.Label(quadro, text=explicacao, style="Suave.TLabel").pack(side="left", padx=(12, 0), pady=(3, 0))
        return quadro

    # Um cartão (quadro branco com borda) com um título em cima; quem chama coloca o cartão na tela
    def criar_cartao(self, pai, titulo):
        cartao = ttk.Frame(pai, style="Painel.TFrame", padding=(14, 10, 14, 12))
        if titulo:
            ttk.Label(cartao, text=titulo, style="TituloDoPainel.TLabel").pack(anchor="w", pady=(0, 8))
        return cartao

    # Uma tabela com barra de rolagem: colunas = (nome, título, largura, estica?, alinhamento).
    # As linhas ímpares ficam listradas (a tag "listra"), para o olho seguir a linha.
    def criar_tabela(self, pai, colunas):
        tema = self.tema
        moldura = ttk.Frame(pai, style="Cartao.TFrame")
        moldura.columnconfigure(0, weight=1)
        moldura.rowconfigure(0, weight=1)
        nomes = []
        for coluna in colunas:
            nomes.append(coluna[0])
        tabela = ttk.Treeview(moldura, columns=nomes, show="headings", selectmode="extended", height=6)
        for nome, titulo, largura, estica, alinhamento in colunas:
            tabela.heading(nome, text=titulo, anchor=alinhamento)
            tabela.column(nome, width=largura, minwidth=30, stretch=estica, anchor=alinhamento)
        tabela.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(moldura, orient="vertical", command=tabela.yview)
        rolagem.grid(row=0, column=1, sticky="ns")
        tabela.configure(yscrollcommand=rolagem.set)
        tabela.tag_configure("listra", background=misturar(tema["superficie"], tema["fundo"], 0.55))
        # O aviso de tabela vazia fica por cima da tabela, no meio (aparece só quando não há linhas)
        self.rotulo_vazio = tk.Label(moldura, bg=tema["superficie"], fg=tema["texto_suave"],
                                     font=self.fontes["texto"], justify="center")
        tabela.bind("<Configure>", lambda evento: self.rotulo_vazio.configure(wraplength=max(200, evento.width - 60)),
                    add="+")
        return moldura, tabela

    def mostrar_vazio(self, texto):
        if texto:
            self.rotulo_vazio.configure(text=texto, wraplength=max(200, self.tabela.winfo_width() - 60))
            self.rotulo_vazio.place(relx=0.5, rely=0.55, anchor="center")
        else:
            self.rotulo_vazio.place_forget()

    def limpar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

    # Troca as colunas visíveis de uma tabela e divide a largura entre as que esticam
    # (o Treeview só estica as colunas quando muda de tamanho; por isso a conta é feita aqui)
    def mostrar_colunas(self, tabela, colunas):
        if tuple(tabela.cget("displaycolumns")) == colunas:
            return
        tabela.configure(displaycolumns=colunas)
        largura = tabela.winfo_width()
        if largura < 50:
            return          # a tabela ainda não apareceu na tela: o Tkinter divide sozinho quando aparecer
        fixas = 0
        esticaveis = []
        for coluna in colunas:
            if tabela.column(coluna, "stretch"):
                esticaveis.append(coluna)
            else:
                fixas += tabela.column(coluna, "width")
        for coluna in esticaveis:
            tabela.column(coluna, width=max(30, (largura - fixas - 4) // len(esticaveis)))

    # Os botões da tabela (Renomear/Editar e Remover) só ficam ligados com alguma linha escolhida
    def atualizar_botoes(self):
        quantas = len(self.tabela.selection())
        self.botao_editar.configurar(habilitado=quantas == 1)
        self.botao_remover.configurar(habilitado=quantas >= 1)

    # O cartão da tabela: título e botões em cima, a tabela no meio e um lembrete embaixo
    def montar_cartao_da_tabela(self, titulo, colunas, texto_do_editar, dica_do_editar, comando_do_editar,
                                dica_do_remover, comando_do_remover, lembrete):
        tema = self.tema
        superficie = tema["superficie"]
        cartao = ttk.Frame(self.quadro, style="Painel.TFrame", padding=(14, 10, 14, 10))
        cartao.grid(row=1, column=1, sticky="nsew")
        cartao.columnconfigure(0, weight=1)
        cartao.rowconfigure(1, weight=1)
        topo = ttk.Frame(cartao, style="Cartao.TFrame")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.titulo_da_tabela = titulo
        self.rotulo_da_tabela = ttk.Label(topo, text=titulo, style="TituloDoPainel.TLabel")
        self.rotulo_da_tabela.pack(side="left")
        self.botao_remover = Botao(topo, self.app, "Remover", icone="lixeira", papel="perigo",
                                   comando=comando_do_remover, fundo=superficie, dica=dica_do_remover)
        self.botao_remover.pack(side="right")
        self.botao_editar = Botao(topo, self.app, texto_do_editar, icone="lapis", papel="info",
                                  comando=comando_do_editar, fundo=superficie, dica=dica_do_editar)
        self.botao_editar.pack(side="right", padx=(0, 8))
        moldura, self.tabela = self.criar_tabela(cartao, colunas)
        moldura.grid(row=1, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", lambda evento: self.atualizar_botoes())
        Lembrete(cartao, self.app, lembrete, fundo=superficie).grid(row=2, column=0, sticky="w", pady=(8, 0))

    # O título da tabela com a quantidade: "Os vértices (8)"
    def contar_no_titulo(self, quantidade):
        texto = self.titulo_da_tabela
        if quantidade:
            texto += f" ({quantidade})"
        self.rotulo_da_tabela.configure(text=texto)


# ----------------------------------------------------------------------
# ① Vértices
# ----------------------------------------------------------------------

class EtapaDosVertices(Etapa):
    def montar(self):
        editor = self.editor
        tema = self.tema
        superficie = tema["superficie"]
        self.quadro.columnconfigure(1, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        self.criar_titulo(self.quadro, 0, "Vértices", "os pontos do grafo: crie um de cada vez ou vários de uma vez")

        # A coluna da esquerda rola se a janela for baixa demais para os dois cartões
        lado = QuadroRolavel(self.quadro, self.app, tema["fundo"])
        lado.grid(row=1, column=0, sticky="nsw", padx=(0, 14))
        coluna = lado.conteudo

        # Um de cada vez: o nome e o Adicionar
        cartao = self.criar_cartao(coluna, "Um de cada vez")
        cartao.pack(fill="x")
        grade = ttk.Frame(cartao, style="Cartao.TFrame")
        grade.pack(fill="x")
        ttk.Label(grade, text="Nome", style="Cartao.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.campo_nome = CampoDeTexto(grade, self.app, editor.novo_vertice, largura=12, fundo=superficie,
                                       ao_enter=editor.adicionar_vertice)
        self.campo_nome.grid(row=0, column=1, sticky="w")
        Botao(grade, self.app, "Adicionar", icone="mais", papel="sucesso", comando=editor.adicionar_vertice,
              fundo=superficie, dica="Cria o vértice com este nome (Enter)").grid(row=0, column=2, padx=(8, 0))
        Lembrete(cartao, self.app, "Letras, números e _ (até 10); o próximo nome já vem sugerido", icone="info",
                 fundo=superficie).pack(anchor="w", pady=(10, 0))

        # Vários de uma vez: a quantidade (já cria ou tira) e o estilo dos nomes
        cartao = self.criar_cartao(coluna, "Vários de uma vez")
        cartao.pack(fill="x", pady=(12, 0))
        grade = ttk.Frame(cartao, style="Cartao.TFrame")
        grade.pack(fill="x")
        ttk.Label(grade, text="Quantidade", style="Cartao.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.contador = Contador(grade, self.app, editor.quantidade_vertices, 0, entrada.MAXIMO_DE_VERTICES,
                                 ao_mudar=editor.mudar_quantidade_de_vertices, fundo=superficie,
                                 dica="Quantos vértices o grafo tem: o + e o − criam e tiram na hora "
                                      "(as setas ↑ e ↓ também; ou digite e aperte Enter)")
        self.contador.grid(row=0, column=1, sticky="w")
        ttk.Label(grade, text="Nomes", style="Cartao.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 10),
                                                                   pady=(10, 0))
        self.segmentos_do_estilo = Segmentos(grade, self.app, [("letras", "A, B, C…", None),
                                                               ("numeros", "1, 2, 3…", None)],
                                             editor.estilo, comando=editor.mudar_estilo, fundo=superficie,
                                             dica="Os nomes dos vértices criados pela Quantidade (os que já estão "
                                                  "na sequência mudam junto)")
        self.segmentos_do_estilo.grid(row=1, column=1, sticky="w", pady=(10, 0))
        Botao(cartao, self.app, "Sortear quantidade", icone="dado", papel="suave",
              comando=editor.sortear_quantidade_de_vertices, fundo=superficie,
              dica="Sorteia quantos vértices o grafo tem (de 4 a 12) e já cria").pack(anchor="w", pady=(12, 0))
        Lembrete(cartao, self.app, "A quantidade já cria os vértices (ou tira os do fim)", icone="info",
                 fundo=superficie).pack(anchor="w", pady=(10, 0))
        lado.ligar_roda()

        # A tabela dos vértices, à direita
        self.montar_cartao_da_tabela(
            "Os vértices", [("numero", "#", 48, False, "center"), ("nome", "Vértice", 160, True, "w"),
                            ("h", "h (heurística)", 120, True, "center")],
            "Renomear", "Muda o nome do vértice escolhido (ou duplo clique na linha)", editor.renomear_vertice,
            "Remove os vértices escolhidos e as arestas ligadas a eles (Delete)", editor.remover_vertices,
            "Duplo clique renomeia (na coluna h, muda o h) · Delete remove · Ctrl+clique escolhe vários")
        self.tabela.bind("<Double-1>", editor.duplo_clique_no_vertice)
        self.tabela.bind("<Delete>", editor.remover_vertices)

    def atualizar(self):
        editor = self.editor
        self.limpar_tabela()
        colunas = ["numero", "nome"]
        if editor.mostrar_coluna_de_heuristica():
            colunas.append("h")
        self.mostrar_colunas(self.tabela, tuple(colunas))
        for i in range(len(editor.vertices)):
            nome = editor.vertices[i]
            h = "—"
            if nome in editor.heuristica:
                h = entrada.formatar_numero(editor.heuristica[nome])
            listra = ("listra",) if i % 2 == 1 else ()
            # iid = identificador da linha; o índice serve porque cada linha é um vértice
            self.tabela.insert("", "end", iid=str(i), values=(i + 1, nome, h), tags=listra)
        self.contar_no_titulo(len(editor.vertices))
        self.contador.mostrar(len(editor.vertices))
        if editor.vertices:
            self.mostrar_vazio("")
        else:
            self.mostrar_vazio("Nenhum vértice ainda.\nDigite um nome e clique em Adicionar, ou use a Quantidade.")
        self.atualizar_botoes()

    def ao_mostrar(self):
        self.campo_nome.focar()


# ----------------------------------------------------------------------
# ② Arestas
# ----------------------------------------------------------------------

class EtapaDasArestas(Etapa):
    def montar(self):
        editor = self.editor
        tema = self.tema
        superficie = tema["superficie"]
        self.quadro.columnconfigure(1, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        titulo = self.criar_titulo(self.quadro, 0, "Arestas", "as ligações entre os vértices")
        # Orientado ou não orientado: a seta (A → B) ou o traço (A — B) dizem a diferença
        self.segmentos_da_orientacao = Segmentos(titulo, self.app,
                                                 [(True, "Orientado", "aresta_orientada"),
                                                  (False, "Não orientado", "aresta_simples")],
                                                 editor.direcionado, comando=editor.mudar_orientacao,
                                                 dica="Orientado: cada aresta tem sentido (A → B). Não orientado: "
                                                      "vale nos dois sentidos (A — B)")
        self.segmentos_da_orientacao.pack(side="right")

        lado = QuadroRolavel(self.quadro, self.app, tema["fundo"])
        lado.grid(row=1, column=0, sticky="nsw", padx=(0, 14))
        coluna = lado.conteudo

        # Uma de cada vez: de onde sai, para onde vai, o nome e o peso
        cartao = self.criar_cartao(coluna, "Uma de cada vez")
        cartao.pack(fill="x")
        grade = ttk.Frame(cartao, style="Cartao.TFrame")
        grade.pack(fill="x")
        ttk.Label(grade, text="De", style="Cartao.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ligacao = ttk.Frame(grade, style="Cartao.TFrame")
        ligacao.grid(row=0, column=1, sticky="w")
        self.seletor_origem = Seletor(ligacao, self.app, editor.nova_origem, fundo=superficie,
                                      dica="O vértice de onde a aresta sai (↑ e ↓ trocam)")
        self.seletor_origem.pack(side="left")
        lado_da_seta = self.fontes["texto"].metrics("linespace")
        self.seta = tk.Canvas(ligacao, width=round(lado_da_seta * 1.8), height=lado_da_seta, bg=superficie,
                              highlightthickness=0)
        self.seta.pack(side="left", padx=6)
        ttk.Label(ligacao, text="Para", style="Cartao.TLabel").pack(side="left", padx=(0, 8))
        self.seletor_destino = Seletor(ligacao, self.app, editor.novo_destino, fundo=superficie,
                                       dica="O vértice aonde a aresta chega (o mesmo de onde sai = um laço)")
        self.seletor_destino.pack(side="left")
        # O nome e o peso na mesma linha (os dois são opcionais)
        ttk.Label(grade, text="Nome", style="Cartao.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 10),
                                                                  pady=(10, 0))
        linha = ttk.Frame(grade, style="Cartao.TFrame")
        linha.grid(row=1, column=1, sticky="w", pady=(10, 0))
        self.campo_nome = CampoDeTexto(linha, self.app, editor.novo_nome_da_aresta, largura=9, fundo=superficie,
                                       ao_enter=editor.adicionar_aresta,
                                       dica="Opcional: um nome para a aresta (e1, rodovia...)")
        self.campo_nome.pack(side="left")
        ttk.Label(linha, text="Peso", style="Cartao.TLabel").pack(side="left", padx=(12, 8))
        self.campo_peso = CampoDeTexto(linha, self.app, editor.novo_peso, largura=5, fundo=superficie,
                                       ao_enter=editor.adicionar_aresta, centralizar=True,
                                       dica="Opcional: o custo da aresta (2,5 ou 2.5); as buscas de menor custo usam")
        self.campo_peso.pack(side="left")
        Botao(cartao, self.app, "Adicionar aresta", icone="mais", papel="sucesso", comando=editor.adicionar_aresta,
              fundo=superficie, dica="Cria a aresta (Enter num dos campos também)").pack(anchor="w", pady=(12, 0))
        Lembrete(cartao, self.app, "Nome e peso são opcionais · De = Para é um laço", icone="info",
                 fundo=superficie).pack(anchor="w", pady=(10, 0))

        # Várias de uma vez: sorteadas (no lugar das de agora)
        cartao = self.criar_cartao(coluna, "Várias de uma vez")
        cartao.pack(fill="x", pady=(12, 0))
        grade = ttk.Frame(cartao, style="Cartao.TFrame")
        grade.pack(fill="x")
        ttk.Label(grade, text="Quantidade", style="Cartao.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.contador = Contador(grade, self.app, editor.quantidade_arestas, 0, entrada.LIMITE_DE_ARESTAS,
                                 fundo=superficie, dica="Quantas arestas o sorteio cria")
        self.contador.grid(row=0, column=1, sticky="w")
        self.rotulo_maximo = ttk.Label(grade, style="CartaoSuave.TLabel")
        self.rotulo_maximo.grid(row=0, column=2, sticky="w", padx=(10, 0))
        chaves = ttk.Frame(cartao, style="Cartao.TFrame")
        chaves.pack(anchor="w", pady=(10, 0))
        Interruptor(chaves, self.app, "Laços", editor.lacos, comando=self.atualizar_maximo, fundo=superficie,
                    dica="O sorteio pode criar laços (uma aresta de um vértice para ele mesmo)").pack(side="left")
        Interruptor(chaves, self.app, "Paralelas", editor.paralelas, comando=self.atualizar_maximo, fundo=superficie,
                    dica="O sorteio pode repetir um par (duas arestas ligando os mesmos vértices)").pack(
            side="left", padx=(16, 0))
        Botao(cartao, self.app, "Sortear arestas", icone="dado", papel="suave", comando=editor.sortear_arestas,
              fundo=superficie, dica="Sorteia as arestas no lugar das de agora (Ctrl+Z desfaz)").pack(
            anchor="w", pady=(12, 0))

        # Mais: todas as arestas como texto e os pesos
        mais = ttk.Frame(coluna)
        mais.pack(fill="x", pady=(12, 0))
        Botao(mais, self.app, "Editar como texto…", icone="codigo", papel="suave",
              comando=editor.editar_arestas_em_texto,
              dica="Todas as arestas num texto, uma por linha (A -> B: nome = peso)").pack(side="left")
        Botao(mais, self.app, "Pesos…", icone="etiqueta", papel="suave", comando=editor.abrir_pesos,
              dica="Dar peso às arestas ou a heurística h aos vértices: todas, as escolhidas ou só as sem valor; "
                   "um valor fixo, sorteado ou o custo real até o destino").pack(side="left", padx=(8, 0))
        lado.ligar_roda()

        # A tabela das arestas, à direita ("Nº" = a ordem de criação: é a ordem dos vizinhos nas listas)
        self.montar_cartao_da_tabela(
            "As arestas", [("numero", "Nº", 48, False, "center"), ("aresta", "Aresta", 120, True, "center"),
                           ("nome", "Nome", 100, True, "center"), ("peso", "Peso", 70, True, "center"),
                           ("obs", "Observação", 110, True, "center")],
            "Editar", "Muda de onde a aresta escolhida sai, para onde vai, o nome e o peso (ou duplo clique)",
            editor.editar_aresta, "Remove as arestas escolhidas (Delete)", editor.remover_arestas,
            "Duplo clique edita · Delete remove · Nº é a ordem em que os vizinhos entram nas listas")
        self.tabela.bind("<Double-1>", editor.duplo_clique_na_aresta)
        self.tabela.bind("<Delete>", editor.remover_arestas)

    # Quantas arestas cabem com as opções de agora (e o contador não deixa passar disso)
    def atualizar_maximo(self):
        maximo = self.editor.maximo_de_arestas()
        self.contador.mudar_limites(0, maximo)
        atual = self.contador.numero_digitado()
        if atual is not None and atual > maximo:
            self.contador.mostrar(maximo)
        self.rotulo_maximo.configure(text=f"cabem até {maximo}")

    def atualizar(self):
        editor = self.editor
        self.limpar_tabela()
        colunas = ["numero", "aresta", "nome"]
        if editor.mostrar_coluna_de_peso():
            colunas.append("peso")
        colunas.append("obs")
        self.mostrar_colunas(self.tabela, tuple(colunas))
        observacoes = entrada.observacoes(editor.arestas, editor.direcionado.get())
        for i in range(len(editor.arestas)):
            origem, destino, nome, peso = editor.arestas[i]
            texto_do_peso = entrada.formatar_numero(peso) or "—"
            listra = ("listra",) if i % 2 == 1 else ()
            self.tabela.insert("", "end", iid=str(i),
                               values=(i + 1, editor.ligacao(origem, destino), nome or "—", texto_do_peso,
                                       observacoes[i] or "—"), tags=listra)
        self.contar_no_titulo(len(editor.arestas))
        if not editor.vertices:
            self.mostrar_vazio("Ainda não há vértices.\nCrie os vértices na etapa ① antes das arestas.")
        elif not editor.arestas:
            self.mostrar_vazio("Nenhuma aresta ainda.\nEscolha De e Para e clique em Adicionar aresta, ou sorteie.")
        else:
            self.mostrar_vazio("")
        self.seletor_origem.mudar_opcoes(editor.vertices)
        self.seletor_destino.mudar_opcoes(editor.vertices)
        self.desenhar_seta()
        self.atualizar_maximo()
        self.atualizar_botoes()

    # A seta entre De e Para: → no orientado, — no não orientado
    def desenhar_seta(self):
        lado = self.fontes["texto"].metrics("linespace")
        self.seta.configure(width=round(lado * 1.8), height=lado)
        self.seta.delete("all")
        icone = "aresta_orientada" if self.editor.direcionado.get() else "aresta_simples"
        desenhar_icone(self.seta, icone, lado * 0.9, lado / 2, lado * 1.1, self.tema["texto_suave"],
                       self.tema["superficie"])

    def ao_mostrar(self):
        self.seletor_origem.focus_set()

    def redesenhar(self):
        self.desenhar_seta()


# ----------------------------------------------------------------------
# ③ Busca
# ----------------------------------------------------------------------

class EtapaDaBusca(Etapa):
    def montar(self):
        editor = self.editor
        tema = self.tema
        superficie = tema["superficie"]
        # A etapa inteira rola se não couber (janela baixa ou letras grandes)
        self.rolagem = QuadroRolavel(self.quadro, self.app, tema["fundo"], largura_do_conteudo=False)
        self.rolagem.pack(fill="both", expand=True)
        conteudo = self.rolagem.conteudo
        conteudo.columnconfigure(0, weight=1)
        self.criar_titulo(conteudo, 0, "Busca", "qual busca vai rodar no seu grafo, por onde começa e até onde vai")

        self.escolha = EscolhaDaBusca(conteudo, self.app, editor.busca, comando=editor.ao_mudar_busca,
                                      fundo=tema["fundo"])
        self.escolha.grid(row=1, column=0, sticky="ew")

        # A busca escolhida: o nome, as etiquetas (pilha, pesos, destino...) e a ideia dela
        sobre = ttk.Frame(conteudo)
        sobre.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        cima = ttk.Frame(sobre)
        cima.pack(fill="x")
        self.rotulo_nome = ttk.Label(cima, font=self.fontes["negrito"])
        self.rotulo_nome.pack(side="left")
        self.etiquetas = ttk.Frame(cima)
        self.etiquetas.pack(side="left", padx=(12, 0))
        self.rotulo_descricao = ttk.Label(sobre, style="Suave.TLabel", justify="left")
        self.rotulo_descricao.pack(fill="x", pady=(4, 0))

        # Embaixo, lado a lado: as opções (por onde começar, o destino, o limite e a ordenação das listas)
        # e o que falta para a busca rodar ("Antes de visualizar")
        baixo = ttk.Frame(conteudo)
        baixo.grid(row=3, column=0, sticky="ew", pady=(12, 4))
        baixo.columnconfigure(0, weight=1, uniform="baixo")
        baixo.columnconfigure(1, weight=1, uniform="baixo")
        cartao = self.criar_cartao(baixo, "Opções da busca")
        cartao.grid(row=0, column=0, sticky="nsew")
        grade = ttk.Frame(cartao, style="Cartao.TFrame")
        grade.pack(fill="x")
        # "Começar por" (a origem): no Prim é a raiz da árvore; o Kruskal não parte de um vértice
        self.rotulo_inicio = ttk.Label(grade, text="Começar por", style="Cartao.TLabel")
        self.rotulo_inicio.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.seletor_inicio = Seletor(grade, self.app, editor.inicio, comando=editor.ao_mudar_busca, fundo=superficie,
                                      icone="play", dica="O vértice de onde a busca sai (a origem; no Prim, a raiz)")
        self.seletor_inicio.grid(row=0, column=1, sticky="w")
        self.rotulo_destino = ttk.Label(grade, text="Destino", style="Cartao.TLabel")
        self.rotulo_destino.grid(row=0, column=2, sticky="w", padx=(20, 10))
        self.seletor_destino = Seletor(grade, self.app, editor.destino, comando=editor.ao_mudar_busca,
                                       fundo=superficie, icone="alvo", vazio="escolha",
                                       dica="Até onde a busca vai (ela para ao chegar)")
        self.seletor_destino.grid(row=0, column=3, sticky="w")
        self.rotulo_limite = ttk.Label(grade, text="Limite", style="Cartao.TLabel")
        self.rotulo_limite.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.contador_do_limite = Contador(grade, self.app, editor.limite, 0, algoritmos.MAIOR_LIMITE,
                                           ao_mudar=lambda numero: editor.ao_mudar_busca(), fundo=superficie,
                                           dica="Até quantas arestas a busca limitada desce a partir da origem")
        self.contador_do_limite.grid(row=1, column=1, sticky="w", pady=(10, 0))
        self.interruptor_ordenar = Interruptor(
            cartao, self.app, "Ordenar as listas (ordem alfabética)", editor.ordenar, comando=editor.ao_mudar_busca,
            fundo=superficie, dica="Ligado: a busca visita os vizinhos em ordem alfabética (é o critério de desempate). "
                                   "Desligado: na ordem em que as arestas foram criadas")
        self.interruptor_ordenar.pack(anchor="w", pady=(12, 0))
        # O Kruskal não tem opção nenhuma: no lugar delas, uma frase dizendo por quê
        self.rotulo_sem_opcoes = ttk.Label(cartao, style="CartaoSuave.TLabel", justify="left",
                                           text="O Kruskal não tem opções: ele não parte de um vértice e não usa as "
                                                "listas de vizinhos. Olha todas as arestas, da mais leve para a mais "
                                                "pesada (as de mesmo peso, na ordem em que foram criadas).")
        self.rotulos_que_quebram_fixos = [self.rotulo_sem_opcoes]

        cartao = self.criar_cartao(baixo, "Antes de visualizar")
        cartao.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.lista_do_que_falta = ttk.Frame(cartao, style="Cartao.TFrame")
        self.lista_do_que_falta.pack(fill="x")
        self.rotulos_que_quebram = []
        conteudo.bind("<Configure>", self.ajustar_quebras_de_linha, add="+")
        self.rolagem.ligar_roda()

    def ajustar_quebras_de_linha(self, evento=None):
        largura = self.rolagem.conteudo.winfo_width()
        if largura < 50:
            return
        self.rotulo_descricao.configure(wraplength=max(300, largura - 20))
        for rotulo in self.rotulos_que_quebram + self.rotulos_que_quebram_fixos:
            if rotulo.winfo_exists():
                rotulo.configure(wraplength=max(200, largura // 2 - 200))

    def atualizar(self):
        editor = self.editor
        tema = self.tema
        busca = editor.busca_escolhida()
        cor = tema[algoritmos.TIPOS_DE_BUSCA[algoritmos.tipo_da_busca(busca["chave"])]["cor"]]
        self.rotulo_nome.configure(text=busca["nome"], foreground=cor)
        for filho in self.etiquetas.winfo_children():
            filho.destroy()
        for fato in algoritmos.fatos(busca):
            tk.Label(self.etiquetas, text=fato, bg=misturar(tema["fundo"], cor, 0.12), fg=cor,
                     font=self.fontes["pequena"], padx=8, pady=1).pack(side="left", padx=(0, 6))
        self.rotulo_descricao.configure(text=busca["descricao"])

        self.seletor_inicio.mudar_opcoes(editor.vertices)
        if busca.get("usa_origem", True):
            self.rotulo_inicio.configure(text="Raiz" if busca["chave"] == algoritmos.PRIM else "Começar por")
            self.rotulo_inicio.grid()
            self.seletor_inicio.grid()
            self.rotulo_sem_opcoes.pack_forget()
            if self.interruptor_ordenar.winfo_manager() != "pack":
                self.interruptor_ordenar.pack(anchor="w", pady=(12, 0))
        else:
            self.rotulo_inicio.grid_remove()
            self.seletor_inicio.grid_remove()
            self.interruptor_ordenar.pack_forget()
            self.rotulo_sem_opcoes.pack(anchor="w", fill="x")
        # O destino só aparece nas buscas que usam; quando é opcional, dá para escolher "nenhum"
        if busca["destino"] == "nao":
            self.rotulo_destino.grid_remove()
            self.seletor_destino.grid_remove()
        else:
            self.rotulo_destino.grid()
            self.seletor_destino.grid()
            opcoes = list(editor.vertices)
            if busca["destino"] == "opcional":
                opcoes = [(SEM_DESTINO, "nenhum")] + opcoes
            self.seletor_destino.mudar_opcoes(opcoes)
        if busca["usa_limite"]:
            self.rotulo_limite.grid()
            self.contador_do_limite.grid()
            numero = self.contador_do_limite.numero_digitado()
            self.contador_do_limite.mostrar(numero if numero is not None else 3)
        else:
            self.rotulo_limite.grid_remove()
            self.contador_do_limite.grid_remove()
        self.montar_lista_do_que_falta()

    # Cada problema numa linha (com um botão que resolve, quando dá), depois os avisos; sem nada, "tudo pronto"
    def montar_lista_do_que_falta(self):
        tema = self.tema
        superficie = tema["superficie"]
        for filho in self.lista_do_que_falta.winfo_children():
            filho.destroy()
        self.rotulos_que_quebram = []
        problemas, avisos = self.editor.conferir_busca()
        linhas = []
        for problema in problemas:
            linhas.append(("alerta", tema["erro"], problema, self.editor.acao_do_problema(problema)))
        for aviso in avisos:
            linhas.append(("info", tema["texto_suave"], aviso, None))
        if not problemas:
            linhas.insert(0, ("check", tema["sucesso"], "Tudo pronto: clique em Visualizar (ou aperte F5).", None))
        for icone, cor, texto, acao in linhas:
            linha = ttk.Frame(self.lista_do_que_falta, style="Cartao.TFrame")
            linha.pack(fill="x", pady=2)
            lado = self.fontes["texto"].metrics("linespace")
            marca = tk.Canvas(linha, width=lado, height=lado, bg=superficie, highlightthickness=0)
            marca.pack(side="left", anchor="n", padx=(0, 8), pady=(1, 0))
            desenhar_icone(marca, icone, lado / 2, lado / 2, lado * 0.9, cor, superficie)
            rotulo = ttk.Label(linha, text=texto, style="Cartao.TLabel", justify="left", foreground=cor)
            rotulo.pack(side="left", anchor="w")
            self.rotulos_que_quebram.append(rotulo)
            if acao is not None:
                texto_do_botao, comando = acao
                Botao(linha, self.app, texto_do_botao, papel="suave", tamanho="pequeno", comando=comando,
                      fundo=superficie).pack(side="right", padx=(8, 0))
        self.ajustar_quebras_de_linha()
        self.rolagem.ligar_roda(self.lista_do_que_falta)

    def ao_mostrar(self):
        self.escolha.focus_set()
