# A tela da visualização, POR PARTES: em vez de mostrar tudo ao mesmo tempo (desenho, código, pilha,
# tabela, lista, log...), ela mostra UMA parte de cada vez, e a pessoa escolhe qual na trilha da esquerda:
#
#   O GRAFO   -> Vértices · Arestas · Pesos · Lista de adjacência · Matriz de adjacência ·
#                Matriz de incidência · Tipo do grafo
#   A BUSCA   -> Passo a passo · Linha a linha · Comparar códigos · Resultado
#
# Cada parte tem a sua cor: o nome dela na trilha, o título e o destaque do que foi escolhido nela
# (o vértice, a aresta, a célula da matriz, a linha do código) ficam nessa cor.
# Dentro de cada parte, o desenho e o código podem ser minimizados (o botão "–" do painel), e os botões
# "Mostrar" acrescentam informação aos poucos (a tabela, o código, o log...).
#
# Em cima ficam as opções da busca (qual busca, de onde, até onde, o limite): mudar qualquer uma
# recalcula tudo na hora. O grafo também pode mudar dentro das partes (pesos, orientação, nomes,
# ordenação), sempre com Ctrl+Z para desfazer. Tudo isso pode ser exportado (imagem, PDF, .bosco e
# código-fonte) pelo menu Exportar.

import tkinter as tk
import traceback
from tkinter import ttk

import algoritmos
import caminhos
from visual.botoes import Botao, ChaveDoTema, redesenhar_componentes
from visual.dica import Dica
from visual.dialogos import DialogoDeInformacao
from visual.partes_da_busca import PARTES_DA_BUSCA
from visual.partes_do_grafo import PARTES_DO_GRAFO
from visual.sessao import Sessao
from visual.tema import misturar

SEM_DESTINO = "(nenhum)"
PARTES = PARTES_DO_GRAFO + PARTES_DA_BUSCA

ATALHOS = [
    ("Ctrl + Page Down  /  Ctrl + Page Up", "próxima parte / parte anterior (a trilha da esquerda)"),
    ("→  /  ←", "próximo / anterior (passo, linha ou aresta, conforme a parte)"),
    ("Espaço", "Play / Pausar"),
    ("Home  /  End", "início / fim"),
    ("Page Down  /  Page Up", "Passo a passo: próxima etapa / etapa anterior"),
    ("↑  /  ↓", "mais rápido / mais devagar"),
    ("F10  /  Shift + F11", "Linha a linha: pula a chamada / sai da função"),
    ("Ctrl + Z", "desfaz a última mudança no grafo (pesos, orientação, nomes...)"),
    ("Ctrl + S", "exporta o arquivo .bosco (abre depois exatamente como está)"),
    ("Duplo clique", "num vértice, numa aresta ou num peso (na tabela ou no desenho): renomeia ou muda o peso"),
    ("Delete", "Tipo do grafo: remove o vértice ou a aresta escolhida no desenho"),
    ("Ctrl + roda do mouse", "letras maiores / menores (Ctrl + e Ctrl − também; Ctrl 0 volta ao normal)"),
    ("F11  /  Esc", "tela cheia / sair da tela cheia"),
]

# Os componentes que "seguram" o teclado: neles, as setas e o espaço não são da tela
COMPONENTES_DE_DIGITAR = ("Entry", "TEntry", "TCombobox", "TSpinbox", "Spinbox", "Text", "Treeview")


def classe_da_parte(chave):
    for classe in PARTES:
        if classe.chave == chave:
            return classe
    return PARTES[0]


class TelaDaVisualizacao:
    # estado_da_tela: como a tela estava (a parte escolhida e as escolhas de cada parte) — vem do
    # arquivo .bosco ou da troca de tema; None = como da última vez (ou a parte Passo a passo)
    def __init__(self, app, configuracao, estado_da_tela=None):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        self.configuracao = configuracao
        self.sessao = Sessao(configuracao, app.montar_passos)
        preferencias = app.preferencias
        preferencias.setdefault("partes", {})
        preferencias.setdefault("arrumacao", configuracao.get("arrumacao") or "circulo")
        parte_inicial = None
        if estado_da_tela:
            for chave, escolhas in estado_da_tela.get("partes", {}).items():
                preferencias["partes"][chave] = escolhas
            parte_inicial = estado_da_tela.get("parte")
            # O menu Exibir como estava (vem do .bosco ou da troca de tema)
            exibir = estado_da_tela.get("exibir", {})
            if "pesos" in exibir:
                preferencias["pesos_das_arestas"] = exibir["pesos"]
            if "nomes" in exibir:
                preferencias["nomes_das_arestas"] = exibir["nomes"]
        if parte_inicial is None:
            parte_inicial = preferencias.get("parte")
        if parte_inicial is None:
            parte_inicial = "passo" if self.sessao.pode_buscar() else "vertices"
        self.parte = None
        self.chave_da_parte = parte_inicial
        self.agendamento = None
        self.aviso_atual = ""
        # As opções da busca (ficam na trilha, embaixo de "A BUSCA"): mudar qualquer uma recalcula tudo
        self.variavel_da_busca = tk.StringVar()
        self.variavel_da_origem = tk.StringVar()
        self.variavel_do_destino = tk.StringVar()
        self.variavel_do_limite = tk.StringVar()
        self.montar_tela()
        self.ligar_atalhos()
        self.escolher_parte(parte_inicial)

    # ------------------------------------------------------------------
    # Montagem da tela
    # ------------------------------------------------------------------

    def montar_tela(self):
        self.quadro = ttk.Frame(self.app.raiz, padding=(10, 8, 10, 6))
        self.quadro.pack(fill="both", expand=True)
        self.quadro.columnconfigure(1, weight=1)
        self.quadro.rowconfigure(1, weight=1)
        self.montar_barra()
        self.montar_trilha()
        self.conteudo_externo = ttk.Frame(self.quadro, padding=(12, 4, 0, 0))
        self.conteudo_externo.grid(row=1, column=1, sticky="nsew")
        self.conteudo_externo.columnconfigure(0, weight=1)
        self.conteudo_externo.rowconfigure(0, weight=1)
        self.conteudo = None
        self.rotulo_aviso = ttk.Label(self.quadro, style="Suave.TLabel")
        self.rotulo_aviso.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.quadro.bind("<Configure>", lambda evento: self.rotulo_aviso.configure(wraplength=max(300, evento.width - 40)))

    # A barra de cima: Início e Editar grafo à esquerda, o nome do grafo, e à direita os menus Exportar e
    # Exibir e a chave do tema. Cada botão tem a sua cor e o seu ícone (não são todos iguais).
    def montar_barra(self):
        barra = ttk.Frame(self.quadro)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        # Os da direita entram PRIMEIRO: se faltar largura, quem encolhe é o resto (nunca eles)
        ChaveDoTema(barra, self.app).pack(side="right")
        self.menu_exibir = tk.Menu(self.app.raiz, tearoff=False)
        self.menu_exportar = tk.Menu(self.app.raiz, tearoff=False)
        self.montar_menus()
        self.botao_exibir = Botao(barra, self.app, "Exibir", icone="olho", papel="neutro", menu=self.menu_exibir,
                                  dica="Pesos e nomes no desenho, arrumação, tamanho das letras, tela cheia e atalhos")
        self.botao_exibir.pack(side="right", padx=(0, 12))
        self.botao_exportar = Botao(barra, self.app, "Exportar", icone="exportar", papel="roxo", menu=self.menu_exportar,
                                    dica="Imagem, relatório em PDF, arquivo .bosco ou o código-fonte da busca")
        self.botao_exportar.pack(side="right", padx=(0, 6))

        Botao(barra, self.app, "Início", icone="seta_esquerda", papel="suave", comando=self.app.mostrar_inicio,
              dica="Volta para a tela inicial, a da escolha da busca").pack(side="left")
        Botao(barra, self.app, "Editar grafo", icone="lapis", papel="info", comando=self.editar_grafo,
              dica="Abre o editor com este grafo (com as mudanças feitas aqui)").pack(side="left", padx=(6, 14))
        titulo = self.sessao.nome
        if len(titulo) > 60:
            titulo = titulo[:59] + "…"
        rotulo = ttk.Label(barra, text=titulo, style="Marca.TLabel")
        rotulo.pack(side="left", padx=(4, 16))
        Dica(rotulo, self.sessao.titulo)

    def estilo_do_menu(self, menu):
        tema = self.tema
        menu.configure(bg=tema["superficie"], fg=tema["texto"], activebackground=tema["acento"],
                       activeforeground=tema["texto_acento"], selectcolor=tema["texto"], font=self.fontes["texto"],
                       relief="solid", borderwidth=1)

    def montar_menus(self):
        menu = self.menu_exportar
        self.estilo_do_menu(menu)
        menu.add_command(label="Imagem do desenho (PNG)…", command=lambda: self.exportar("png"))
        menu.add_command(label="Imagem do desenho (SVG, vetorial)…", command=lambda: self.exportar("svg"))
        menu.add_command(label="PDF só com o desenho…", command=lambda: self.exportar("pdf_desenho"))
        menu.add_command(label="Relatório completo em PDF…", command=lambda: self.exportar("pdf"))
        menu.add_separator()
        menu.add_command(label="Arquivo do BoscoGraph (.bosco)…", accelerator="Ctrl+S",
                         command=lambda: self.exportar("bosco"))
        codigo = tk.Menu(menu, tearoff=False)
        self.estilo_do_menu(codigo)
        import estudo
        for informacoes in estudo.LINGUAGENS:
            codigo.add_command(label=informacoes["nome"] + "…",
                               command=lambda chave=informacoes["chave"]: self.exportar("codigo", chave))
        menu.add_cascade(label="Código-fonte da busca, com este grafo", menu=codigo)

        menu = self.menu_exibir
        self.estilo_do_menu(menu)
        preferencias = self.app.preferencias
        self.mostrar_pesos = tk.BooleanVar(value=preferencias.get("pesos_das_arestas", True))
        self.mostrar_nomes = tk.BooleanVar(value=preferencias.get("nomes_das_arestas", True))
        self.arrumacao = tk.StringVar(value=preferencias.get("arrumacao", "circulo"))
        menu.add_checkbutton(label="Pesos das arestas", variable=self.mostrar_pesos, command=self.mudar_rotulos)
        menu.add_checkbutton(label="Nomes das arestas", variable=self.mostrar_nomes, command=self.mudar_rotulos)
        menu.add_separator()
        menu.add_radiobutton(label="Desenho em círculo", value="circulo", variable=self.arrumacao,
                             command=self.mudar_arrumacao)
        menu.add_radiobutton(label="Desenho como no arquivo (posições importadas)", value="arquivo",
                             variable=self.arrumacao, command=self.mudar_arrumacao)
        if not self.tem_posicoes():
            menu.entryconfigure(menu.index("end"), state="disabled")
        menu.add_separator()
        # O tema fica na chave do sol e da lua, no canto de cima
        menu.add_command(label="Letras maiores", accelerator="Ctrl +", command=self.app.aumentar_zoom)
        menu.add_command(label="Letras menores", accelerator="Ctrl −", command=self.app.diminuir_zoom)
        menu.add_command(label="Letras no tamanho normal", accelerator="Ctrl 0", command=self.app.zoom_normal)
        menu.add_command(label="Tela cheia", accelerator="F11", command=self.app.alternar_tela_cheia)
        menu.add_separator()
        menu.add_command(label="Atalhos do teclado…", command=self.mostrar_atalhos)

    def tem_posicoes(self):
        posicoes = self.sessao.posicoes
        return bool(self.sessao.vertices) and all(vertice in posicoes for vertice in self.sessao.vertices)

    # A trilha da esquerda: as partes, cada uma com a sua cor
    def montar_trilha(self):
        tema = self.tema
        self.trilha = ttk.Frame(self.quadro, style="Trilha.TFrame", padding=(8, 10, 8, 10))
        self.trilha.grid(row=1, column=0, sticky="ns")
        self.itens_da_trilha = {}
        linha = 0
        for grupo, titulo in (("grafo", "O GRAFO"), ("busca", "A BUSCA")):
            if grupo == "busca":
                titulo = "A BUSCA · " + self.sessao.informacoes_da_busca()["nome_curto"]
            self.rotulo_do_grupo = ttk.Label(self.trilha, text=titulo, style="TrilhaGrupo.TLabel")
            self.rotulo_do_grupo.grid(row=linha, column=0, sticky="w", pady=(10 if linha else 0, 4))
            linha += 1
            if grupo == "busca":
                self.montar_opcoes_da_busca(self.trilha).grid(row=linha, column=0, sticky="ew", pady=(0, 6))
                linha += 1
            if grupo == "busca" and self.sessao.problemas:
                aviso = ttk.Label(self.trilha, text="⚠ Ainda não pode rodar: veja em Passo a passo",
                                  style="TrilhaErro.TLabel", wraplength=170, justify="left")
                aviso.grid(row=linha, column=0, sticky="w", pady=(0, 4))
                Dica(aviso, self.texto_dos_problemas)
                linha += 1
            for classe in PARTES:
                if classe.grupo != grupo:
                    continue
                item = tk.Frame(self.trilha, bg=tema["superficie"], cursor="hand2")
                item.grid(row=linha, column=0, sticky="ew", pady=1)
                barra = tk.Frame(item, bg=tema["superficie"], width=5)
                barra.pack(side="left", fill="y")
                ponto = tk.Label(item, text="●", bg=tema["superficie"], fg=tema["parte_" + classe.chave],
                                 font=self.fontes["pequena"])
                ponto.pack(side="left", padx=(6, 4))
                rotulo = tk.Label(item, text=classe.titulo, bg=tema["superficie"], fg=tema["texto"], anchor="w",
                                  font=self.fontes["texto"], padx=2, pady=5)
                rotulo.pack(side="left", fill="x", expand=True, padx=(0, 10))
                for componente in (item, barra, ponto, rotulo):
                    componente.bind("<Button-1>", lambda evento, chave=classe.chave: self.escolher_parte(chave))
                    componente.bind("<Enter>", lambda evento, chave=classe.chave: self.passar_o_mouse(chave, True))
                    componente.bind("<Leave>", lambda evento, chave=classe.chave: self.passar_o_mouse(chave, False))
                Dica(rotulo, classe.descricao)
                self.itens_da_trilha[classe.chave] = (item, barra, ponto, rotulo)
                linha += 1
        self.trilha.columnconfigure(0, weight=1)

    # A busca, a origem, o destino e o limite, um embaixo do outro (dentro da trilha)
    def montar_opcoes_da_busca(self, pai):
        quadro = ttk.Frame(pai, style="Trilha.TFrame")
        quadro.columnconfigure(1, weight=1)
        caixa = ttk.Combobox(quadro, textvariable=self.variavel_da_busca, values=algoritmos.nomes(), state="readonly",
                             width=22)
        caixa.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        caixa.bind("<<ComboboxSelected>>", self.mudar_busca)
        Dica(caixa, "Qual busca visualizar (tudo é recalculado na hora; Ctrl+Z desfaz)")
        # "de" (a origem) some no Kruskal, que não parte de um vértice; no Prim, vira "raiz"
        self.rotulo_da_origem = ttk.Label(quadro, text="de", style="TrilhaGrupo.TLabel")
        self.rotulo_da_origem.grid(row=1, column=0, sticky="w", padx=(0, 6))
        self.caixa_origem = ttk.Combobox(quadro, textvariable=self.variavel_da_origem, values=self.sessao.vertices,
                                         state="readonly", width=12)
        self.caixa_origem.grid(row=1, column=1, sticky="ew", pady=1)
        self.caixa_origem.bind("<<ComboboxSelected>>", self.mudar_busca)
        Dica(self.caixa_origem, self.texto_da_origem)
        # "até" (o destino) só aparece nas buscas que usam destino (a busca em profundidade não usa)
        self.rotulo_do_destino = ttk.Label(quadro, text="até", style="TrilhaGrupo.TLabel")
        self.rotulo_do_destino.grid(row=2, column=0, sticky="w", padx=(0, 6))
        self.caixa_destino = ttk.Combobox(quadro, textvariable=self.variavel_do_destino,
                                          values=[SEM_DESTINO] + self.sessao.vertices, state="readonly", width=12)
        self.caixa_destino.grid(row=2, column=1, sticky="ew", pady=1)
        self.caixa_destino.bind("<<ComboboxSelected>>", self.mudar_busca)
        Dica(self.caixa_destino, self.texto_do_destino)
        self.rotulo_do_limite = ttk.Label(quadro, text="limite", style="TrilhaGrupo.TLabel")
        self.rotulo_do_limite.grid(row=3, column=0, sticky="w", padx=(0, 6))
        self.caixa_limite = ttk.Spinbox(quadro, from_=0, to=algoritmos.MAIOR_LIMITE, width=5,
                                        textvariable=self.variavel_do_limite, command=self.mudar_busca)
        self.caixa_limite.grid(row=3, column=1, sticky="w", pady=1)
        self.caixa_limite.bind("<Return>", self.mudar_busca)
        self.caixa_limite.bind("<FocusOut>", self.mudar_busca)
        Dica(self.caixa_limite, "Até quantas arestas a busca limitada desce a partir da origem")
        self.atualizar_barra()
        return quadro

    # As dicas da origem e do destino (cada busca usa os dois de um jeito)
    def texto_da_origem(self):
        chave = self.sessao.algoritmo
        if chave == algoritmos.PROFUNDIDADE:
            return "O vértice por onde a DFS começa (depois ela continua pelos que sobrarem, em ordem alfabética)"
        if chave == algoritmos.FLOYD_WARSHALL:
            return ("O Floyd-Warshall calcula todos os pares de uma vez: a origem e o destino só escolhem o caminho "
                    "que o resultado mostra")
        if chave == algoritmos.PRIM:
            return ("A raiz, onde a árvore começa a crescer (com qualquer raiz, o peso total da árvore mínima é o "
                    "mesmo)")
        return "De onde a busca parte"

    def texto_do_destino(self):
        informacoes = self.sessao.informacoes_da_busca()
        if informacoes["destino"] == "obrigatorio":
            return "Aonde a busca quer chegar (esta busca precisa de um destino)"
        return "Aonde a busca quer chegar (opcional: sem destino, ela explora tudo o que alcança)"

    def pintar_trilha(self):
        tema = self.tema
        for chave, (item, barra, ponto, rotulo) in self.itens_da_trilha.items():
            cor = tema["parte_" + chave]
            escolhida = chave == self.chave_da_parte
            fundo = misturar(tema["superficie"], cor, 0.18) if escolhida else tema["superficie"]
            texto = tema["texto"]
            classe = classe_da_parte(chave)
            if classe.grupo == "busca" and not self.sessao.pode_buscar():
                texto = tema["texto_suave"]
            for componente in (item, ponto, rotulo):
                componente.configure(bg=fundo)
            barra.configure(bg=cor if escolhida else tema["superficie"])
            rotulo.configure(fg=texto, font=self.fontes["negrito"] if escolhida else self.fontes["texto"])

    def passar_o_mouse(self, chave, dentro):
        if chave == self.chave_da_parte:
            return
        item, barra, ponto, rotulo = self.itens_da_trilha[chave]
        fundo = self.tema["borda"] if dentro else self.tema["superficie"]
        for componente in (item, ponto, rotulo):
            componente.configure(bg=fundo)

    # ------------------------------------------------------------------
    # As partes
    # ------------------------------------------------------------------

    def escolher_parte(self, chave):
        if self.parte is not None:
            self.guardar_escolhas()
            self.parte.destruir()
        if self.conteudo is not None:
            self.conteudo.destroy()
        self.chave_da_parte = chave
        self.app.preferencias["parte"] = chave
        self.conteudo = ttk.Frame(self.conteudo_externo)
        self.conteudo.grid(row=0, column=0, sticky="nsew")
        classe = classe_da_parte(chave)
        escolhas = self.app.preferencias["partes"].get(chave)
        parte = None
        try:
            parte = classe(self, escolhas)
            parte.montar(self.conteudo)
        except Exception:
            if not escolhas:
                raise
            # As escolhas guardadas não servem para este grafo (um arquivo .bosco editado à mão, por
            # exemplo): a parte começa do zero, sem elas
            traceback.print_exc()
            if parte is not None:
                parte.destruir()
            self.conteudo.destroy()
            self.conteudo = ttk.Frame(self.conteudo_externo)
            self.conteudo.grid(row=0, column=0, sticky="nsew")
            self.app.preferencias["partes"][chave] = {}
            parte = classe(self, None)
            parte.montar(self.conteudo)
        self.parte = parte
        self.tirar_foco_dos_controles(self.conteudo)
        self.pintar_trilha()
        self.app.raiz.title(f"{caminhos.NOME_DO_PROGRAMA} — {self.sessao.titulo} · {classe.titulo}")
        # O desenho só tem tamanho depois que a tela aparece: mostra um pouquinho depois
        self.agendar_mostrar()

    def agendar_mostrar(self):
        if self.agendamento is not None:
            self.app.raiz.after_cancel(self.agendamento)
        self.agendamento = self.app.raiz.after(60, self.mostrar_parte)

    def mostrar_parte(self):
        self.agendamento = None
        if self.parte is None:
            return
        try:
            self.parte.mostrar()
        except Exception:
            # Como no escolher_parte: escolhas guardadas que não servem mais -> a parte começa do zero
            chave = self.chave_da_parte
            if not self.app.preferencias["partes"].get(chave) or getattr(self.parte, "recomecou", False):
                raise
            traceback.print_exc()
            self.parte.destruir()
            self.parte = None
            self.app.preferencias["partes"][chave] = {}
            self.escolher_parte(chave)
            self.parte.recomecou = True

    def guardar_escolhas(self):
        if self.parte is not None:
            escolhas = dict(self.parte.escolhas)
            escolhas["recolhidos"] = self.parte.recolhidos() if hasattr(self.parte, "painel_do_grafo") else {}
            self.app.preferencias["partes"][self.parte.chave] = escolhas

    def proxima_parte(self, evento=None, passo=1):
        chaves = [classe.chave for classe in PARTES]
        posicao = (chaves.index(self.chave_da_parte) + passo) % len(chaves)
        self.escolher_parte(chaves[posicao])
        return "break"

    # Nenhum botão "rouba" o teclado ao ser clicado: as setas e o espaço continuam com a tela
    def tirar_foco_dos_controles(self, componente):
        for filho in componente.winfo_children():
            if isinstance(filho, (ttk.Button, ttk.Scale, ttk.Radiobutton, ttk.Checkbutton, ttk.Menubutton)):
                filho.configure(takefocus=False)
            self.tirar_foco_dos_controles(filho)

    # ------------------------------------------------------------------
    # Mudanças no grafo e nas opções da busca
    # ------------------------------------------------------------------

    # Toda mudança passa por aqui: a sessão recalcula, e a parte de agora é montada de novo
    def mudar_grafo(self, aviso, **mudancas):
        if not self.sessao.mudar(**mudancas):
            self.avisar("Nada mudou.")
            return
        self.depois_de_mudar(aviso)

    def depois_de_mudar(self, aviso):
        self.atualizar_configuracao()
        self.atualizar_barra()
        self.recriar_trilha()           # o nome da busca e o aviso de problema ficam na trilha
        self.escolher_parte(self.chave_da_parte)
        self.avisar(aviso)

    def desfazer(self, evento=None):
        if self.foco_em_campo():
            return None
        if self.sessao.desfazer():
            self.depois_de_mudar("Última mudança desfeita.")
        else:
            self.avisar("Não há mais nada para desfazer.")
        return "break"

    # A configuração que o editor recebe de volta ("Editar grafo") acompanha as mudanças
    def atualizar_configuracao(self):
        grafo = self.sessao.grafo()
        for chave in ("vertices", "arestas", "ordenar", "inicio", "direcionado", "algoritmo", "destino", "heuristica",
                      "posicoes", "limite"):
            self.configuracao[chave] = grafo[chave]
        valores = self.configuracao.get("valores")
        if valores is not None:
            valores["grafo"] = grafo

    def mudar_busca(self, evento=None):
        chave = algoritmos.chave_pelo_nome(self.variavel_da_busca.get())
        inicio = self.variavel_da_origem.get() or None
        destino = self.variavel_do_destino.get()
        if destino not in self.sessao.vertices:
            destino = None
        limite = self.sessao.limite
        texto = self.variavel_do_limite.get().strip()
        if texto.isdigit():
            limite = max(0, min(int(texto), algoritmos.MAIOR_LIMITE))
        mudou = self.sessao.mudar(algoritmo=chave, inicio=inicio, destino=destino, limite=limite)
        if mudou:
            nome = algoritmos.algoritmo(chave)["nome"]
            self.depois_de_mudar(f"Busca: {nome}. Ctrl+Z desfaz.")

    def recriar_trilha(self):
        self.trilha.destroy()
        self.montar_trilha()
        self.pintar_trilha()

    def atualizar_barra(self):
        sessao = self.sessao
        informacoes = sessao.informacoes_da_busca()
        self.variavel_da_busca.set(informacoes["nome"])
        self.caixa_origem.configure(values=sessao.vertices)
        self.caixa_destino.configure(values=[SEM_DESTINO] + sessao.vertices)
        self.variavel_da_origem.set(sessao.origem() or "")
        self.variavel_do_destino.set(sessao.destino if sessao.destino in sessao.vertices else SEM_DESTINO)
        self.variavel_do_limite.set(str(sessao.limite))
        if informacoes["destino"] == "nao":
            self.rotulo_do_destino.grid_remove()
            self.caixa_destino.grid_remove()
        else:
            self.rotulo_do_destino.grid()
            self.caixa_destino.grid()
        if informacoes.get("usa_origem", True):
            self.rotulo_da_origem.configure(text="raiz" if sessao.algoritmo == algoritmos.PRIM else "de")
            self.rotulo_da_origem.grid()
            self.caixa_origem.grid()
        else:
            self.rotulo_da_origem.grid_remove()
            self.caixa_origem.grid_remove()
        if informacoes["usa_limite"]:
            self.rotulo_do_limite.grid()
            self.caixa_limite.grid()
        else:
            self.rotulo_do_limite.grid_remove()
            self.caixa_limite.grid_remove()

    def texto_dos_problemas(self):
        return "\n".join(self.sessao.problemas)

    def avisar(self, texto, erro=False):
        self.aviso_atual = texto
        self.rotulo_aviso.configure(text=texto, style="ErroFundo.TLabel" if erro else "Suave.TLabel")

    # ------------------------------------------------------------------
    # Menu Exibir
    # ------------------------------------------------------------------

    def mudar_rotulos(self):
        self.app.preferencias["pesos_das_arestas"] = self.mostrar_pesos.get()
        self.app.preferencias["nomes_das_arestas"] = self.mostrar_nomes.get()
        self.mostrar_parte()

    def mudar_arrumacao(self):
        self.app.preferencias["arrumacao"] = self.arrumacao.get()
        self.configuracao["arrumacao"] = self.arrumacao.get()
        self.mostrar_parte()

    def mostrar_atalhos(self):
        DialogoDeInformacao(self.app, "Atalhos do teclado", ATALHOS)

    # ------------------------------------------------------------------
    # Exportar (visual/exportar.py faz o trabalho)
    # ------------------------------------------------------------------

    def exportar(self, tipo, linguagem=None):
        from visual import exportar
        exportar.exportar(self, tipo, linguagem)
        return "break"

    # Como a tela está agora (para o .bosco e para recriar a tela com outro tema)
    def estado_da_tela(self):
        self.guardar_escolhas()
        return {"parte": self.chave_da_parte, "partes": dict(self.app.preferencias["partes"]),
                "exibir": {"pesos": self.mostrar_pesos.get(), "nomes": self.mostrar_nomes.get(),
                           "arrumacao": self.arrumacao.get()}}

    # ------------------------------------------------------------------
    # Teclado
    # ------------------------------------------------------------------

    def foco_em_campo(self):
        try:
            foco = self.app.raiz.focus_get()
        except (KeyError, tk.TclError):
            return False
        return foco is not None and foco.winfo_class() in COMPONENTES_DE_DIGITAR

    def tecla(self, nome):
        if self.foco_em_campo() or self.parte is None:
            return None
        if self.parte.tecla(nome):
            return "break"
        return None

    def ligar_atalhos(self):
        raiz = self.app.raiz
        self.atalhos = {
            "<Right>": lambda evento: self.tecla("direita"),
            "<Left>": lambda evento: self.tecla("esquerda"),
            "<space>": lambda evento: self.tecla("espaco"),
            "<Home>": lambda evento: self.tecla("inicio"),
            "<End>": lambda evento: self.tecla("fim"),
            "<Next>": lambda evento: self.tecla("proxima_etapa"),
            "<Prior>": lambda evento: self.tecla("etapa_anterior"),
            "<Up>": lambda evento: self.tecla("mais_rapido"),
            "<Down>": lambda evento: self.tecla("mais_devagar"),
            "<F10>": lambda evento: self.tecla("pular") or "break",
            "<Shift-F11>": lambda evento: self.tecla("sair") or "break",
            "<Control-Next>": lambda evento: self.proxima_parte(passo=1),
            "<Control-Prior>": lambda evento: self.proxima_parte(passo=-1),
            "<Delete>": lambda evento: self.tecla("apagar"),
            "<Control-z>": self.desfazer,
            "<Control-Z>": self.desfazer,
            "<Control-s>": lambda evento: self.exportar("bosco"),
            "<Control-S>": lambda evento: self.exportar("bosco"),
        }
        for tecla, funcao in self.atalhos.items():
            raiz.bind(tecla, funcao)

    # ------------------------------------------------------------------
    # O que toda tela tem (o aplicativo chama ao trocar o tema, mudar o zoom e trocar de tela)
    # ------------------------------------------------------------------

    def editar_grafo(self):
        self.atualizar_configuracao()
        valores = self.configuracao.get("valores")
        if valores is None:
            # Veio de um .bosco: o editor abre com este grafo (o grafo de antes do editor vai para o Ctrl+Z)
            from visual.editor import valores_para_abrir
            valores = valores_para_abrir(self.app, self.sessao.grafo(), self.sessao.nome,
                                         "Grafo vindo da visualização. Edite à vontade: Ctrl+Z desfaz.")
            self.configuracao["valores"] = valores
        self.app.mostrar_editor(valores)

    def reconstruir(self):
        estado = self.estado_da_tela()
        self.app.mostrar_visualizacao(self.configuracao, estado)

    def redesenhar(self):
        redesenhar_componentes(self.quadro)
        self.mostrar_parte()

    def destruir(self):
        if self.parte is not None:
            self.guardar_escolhas()
            self.parte.destruir()
            self.parte = None
        if self.agendamento is not None:
            self.app.raiz.after_cancel(self.agendamento)
            self.agendamento = None
        if self.app.dialogo is not None:
            self.app.dialogo.fechar()
        for tecla in self.atalhos:
            self.app.raiz.unbind(tecla)
        self.quadro.destroy()
