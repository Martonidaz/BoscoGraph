# As partes "A BUSCA" da tela por partes: Passo a passo, Linha a linha, Comparar códigos e Resultado.
#
#   Passo a passo -> cada clique mostra um passo da busca (etapa 5) e do resultado (etapa 6). A tela
#                    começa simples (o desenho, a estrutura e a explicação) e os botões "Mostrar"
#                    acrescentam a tabela, o código e o log quando a pessoa quiser.
#   Linha a linha -> o programa em Python RODA de verdade, como num depurador: desde a primeira linha
#                    do arquivo (o cabeçalho, os comentários, a classe, o grafo, a chamada da busca e os
#                    print do fim), uma linha por clique. Clicar numa linha do código mostra quantas vezes
#                    ela roda e leva à primeira, à anterior, à próxima ou à última vez: é assim que se
#                    escolhe de onde partir. O painel Saída mostra o que o programa já escreveu.
#   Comparar      -> duas linguagens LADO A LADO, com a mesma linha destacada nas duas.
#   Resultado     -> as conclusões do fim (distâncias, caminho, tipo do grafo...), uma de cada vez.

import tkinter as tk
from tkinter import ttk

import algoritmos
import entrada
import estudo
from entrada import formatar_numero
from visual import explicacoes, perfis
from visual.botoes import Botao, Segmentos
from visual.codigo import BOSCOGRAPH, PASTA_DO_PROJETO, PainelDeCodigo, localizar_trechos
from visual.componentes import BarraDoTocador, Chips
from visual.estruturas import DesenhoDaEstrutura
from visual.matrizes import GradeDeMatriz
from visual.parte import Parte, limpar_tabela
from visual.tema import CORES_DOS_CONJUNTOS, misturar
from visual.variaveis import PainelDeVariaveis, nome_da_chamada


# A pilha de chamadas numa linha: "em relaxar() ← dijkstra() ← programa"
def texto_da_pilha(pilha):
    nomes = [nome_da_chamada(chamada) for chamada in pilha]
    if len(nomes) <= 4:
        return "em " + " ← ".join(nomes)
    return "em " + " ← ".join(nomes[:3]) + " ← … ← " + nomes[-1] + f"   ({len(nomes)} chamadas)"


# A matriz d (ou π) do Floyd-Warshall num momento, no formato da GradeDeMatriz
def matriz_do_floyd(estado, vertices, qual):
    celulas = {}
    for i in range(len(vertices)):
        for j in range(len(vertices)):
            par = (vertices[i], vertices[j])
            if qual == "d":
                if par in estado.matriz_d:
                    celulas[(i, j)] = formatar_numero(estado.matriz_d[par])
                else:
                    celulas[(i, j)] = ""
            else:
                valor = estado.matriz_pi.get(par)
                celulas[(i, j)] = valor if valor is not None else ("—" if par in estado.matriz_pi else "")
    return {"linhas": list(vertices), "colunas": list(vertices), "celulas": celulas}


# Os destaques da matriz d: a linha e a coluna de k, o par de agora e os que melhoraram nesta rodada
def destaques_do_floyd(estado, vertices, tema, cor):
    posicao = {}
    for indice in range(len(vertices)):
        posicao[vertices[indice]] = indice
    destaques = {"linhas": {}, "colunas": {}, "celulas": {}, "contorno": {}}
    clarinho = misturar(tema["superficie"], cor, 0.18)
    if estado.k_atual is not None:
        destaques["linhas"][posicao[estado.k_atual]] = clarinho
        destaques["colunas"][posicao[estado.k_atual]] = clarinho
    for i, j in estado.melhoras_na_rodada:
        destaques["celulas"][(posicao[i], posicao[j])] = misturar(tema["superficie"], tema["sucesso"], 0.3)
    if estado.par_atual is not None:
        i, j = estado.par_atual
        destaques["celulas"][(posicao[i], posicao[j])] = tema["fundo_destaque"]
        destaques["contorno"][(posicao[i], posicao[j])] = tema["destaque"]
    return destaques


class ParteDaBusca(Parte):
    grupo = "busca"

    def __init__(self, tela, escolhas):
        Parte.__init__(self, tela, escolhas)
        self.algoritmo = self.sessao.algoritmo
        self.perfil = perfis.perfil(self.algoritmo)
        self.linhas_do_arquivo = {}
        self.linha_do_trecho = {}
        self.barra = None

    # Quando a busca não pode rodar (falta peso, destino...): o motivo e um atalho para resolver
    def montar_problema(self, pai):
        pai.columnconfigure(0, weight=1)
        self.criar_titulo(pai).grid(row=0, column=0, sticky="w")
        quadro = ttk.Frame(pai, style="Painel.TFrame", padding=16)
        quadro.grid(row=1, column=0, sticky="nw", pady=(16, 0))
        nome = self.sessao.informacoes_da_busca()["nome"]
        ttk.Label(quadro, text=f"A busca \"{nome}\" ainda não pode rodar neste grafo:", style="TituloDoPainel.TLabel"
                  ).pack(anchor="w")
        for problema in self.sessao.problemas:
            ttk.Label(quadro, text="⚠ " + problema, style="Erro.TLabel", wraplength=640, justify="left").pack(
                anchor="w", pady=(6, 0))
        atalhos = ttk.Frame(quadro, style="Cartao.TFrame")
        atalhos.pack(anchor="w", pady=(12, 0))
        texto = " ".join(self.sessao.problemas)
        if "não orientado" in texto:
            ttk.Button(atalhos, text="Tornar não orientado", style="Acento.TButton",
                       command=self.tornar_nao_orientado).pack(side="left", padx=(0, 6))
        if "peso" in texto:
            ttk.Button(atalhos, text="Ir para Pesos", style="Acento.TButton",
                       command=lambda: self.tela.escolher_parte("pesos")).pack(side="left", padx=(0, 6))
        if " h " in texto or "heurística" in texto:
            ttk.Button(atalhos, text="Heurística (em Pesos)",
                       command=lambda: self.tela.escolher_parte("pesos")).pack(side="left", padx=(0, 6))
        ttk.Label(atalhos, text="Destino, origem, limite e a própria busca ficam na barra de cima.",
                  style="CartaoSuave.TLabel").pack(side="left", padx=(6, 0))

    # Prim e Kruskal: a árvore geradora mínima é para grafos não orientados
    def tornar_nao_orientado(self):
        self.tela.mudar_grafo("Agora o grafo é não orientado: cada aresta vale nos dois sentidos (A — B). "
                              "Ctrl+Z desfaz.", direcionado=False)

    # ------------------------------------------------------------------
    # O que o painel de código (visual/codigo.py) pergunta
    # ------------------------------------------------------------------

    def carregar_trechos(self):
        if not self.linhas_do_arquivo:
            self.linhas_do_arquivo, self.linha_do_trecho = localizar_trechos(self.perfil["trechos"])
            if "boscograph.py" not in self.linhas_do_arquivo:
                texto = (PASTA_DO_PROJETO / "boscograph.py").read_text(encoding="utf-8")
                self.linhas_do_arquivo["boscograph.py"] = texto.split("\n")

    # O programa da busca na linguagem (o arquivo inteiro, com o grafo dentro; veja Sessao.programas)
    def codigo_de_estudo(self, chave):
        return self.sessao.programas()[chave]

    # As linhas a destacar no programa de uma linguagem: (as do momento, as do momento anterior).
    # No passo a passo: as linhas com o rótulo do passo. (O linha a linha e a comparação, no modo
    # linha, trocam esta função: veja linhas_no_linha_a_linha.)
    def linhas_do_momento(self, chave, programa):
        atual, anterior = self.rotulos_do_momento()
        atuais = list(programa["linhas_do_rotulo"].get(atual, [])) if atual else []
        anteriores = list(programa["linhas_do_rotulo"].get(anterior, [])) if anterior else []
        return atuais, anteriores

    # No linha a linha: no Python, as linhas do comando que vai rodar (e as do que acabou de rodar);
    # nas outras linguagens, as linhas com o mesmo rótulo
    def linhas_no_linha_a_linha(self, chave, programa, posicao):
        passos = self.sessao.rastro["passos_de_linha"]
        atual = passos[posicao] if posicao < len(passos) else None
        anterior = passos[posicao - 1] if posicao > 0 else None
        resultado = []
        for passo in (atual, anterior):
            if passo is None:
                resultado.append([])
            elif chave == "python":
                resultado.append(list(passo["linhas"]))
            elif passo["rotulo"]:
                resultado.append(list(programa["linhas_do_rotulo"].get(passo["rotulo"], [])))
            else:
                resultado.append([])
        return resultado[0], resultado[1]

    # O passo que está no desenho agora (as partes de baixo dizem qual)
    def passo_no_desenho(self):
        return -1

    def trecho_do_momento(self):
        self.carregar_trechos()
        indice = self.passo_no_desenho()
        if indice < 0 or indice > len(self.sessao.passos) - 1:
            return "boscograph.py", None
        chave = perfis.chave_do_trecho(self.sessao.passos[indice])
        if chave not in self.perfil["trechos"]:
            return "boscograph.py", None
        return self.perfil["trechos"][chave][0], self.linha_do_trecho[chave]

    def aviso_sem_linha_de_estudo(self):
        indice = self.passo_no_desenho()
        if indice < 0 or self.sessao.etapas.get(indice, 1) < 5:
            return "o código de estudo começa na busca (etapa 5)"
        return "este passo é do resultado (etapa 6), que o código de estudo não tem"

    # ------------------------------------------------------------------
    # Painéis que várias partes da busca usam
    # ------------------------------------------------------------------

    def criar_tabela_da_busca(self, pai):
        quadro = ttk.LabelFrame(pai, text=self.perfil["titulo_tabela"], padding=6)
        if self.perfil["estrutura"] == "matriz":
            self.grade_pi = GradeDeMatriz(quadro, self.app)
            self.grade_pi.quadro.pack(fill="both", expand=True)
            self.tabela = None
            return quadro
        largura = 70
        for vertice in self.sessao.vertices:
            largura = max(largura, self.fontes["codigo"].measure(vertice) + 20)
        colunas = [("vertice", "Vértice", largura, True)]
        for chave, titulo, tamanho in self.perfil["colunas"]:
            colunas.append((chave, titulo, tamanho, True))
        interno, self.tabela = self.criar_tabela(quadro, colunas, altura=6)
        interno.pack(fill="both", expand=True)
        tema = self.tema
        self.tabela.tag_configure("sem_cor", background=tema["superficie"], foreground=tema["texto_suave"])
        for cor in ("Branco", "Cinza", "Preto"):
            self.tabela.tag_configure(cor, background=tema["vertice_" + cor.lower()],
                                      foreground=tema["texto_vertice_" + cor.lower()])
        # Bidirecional: a linha tem o tom do lado que descobriu o vértice (como no desenho)
        for lado in ("frente", "tras"):
            self.tabela.tag_configure(lado + "_Cinza", background=tema["lado_" + lado], foreground=tema["texto"])
            self.tabela.tag_configure(lado + "_Preto", background=tema["lado_" + lado + "_preto"],
                                      foreground=tema["texto_lado_preto"])
        # Kruskal: a linha tem a cor do conjunto do vértice (como no desenho)
        for numero in range(CORES_DOS_CONJUNTOS):
            self.tabela.tag_configure(f"conjunto_{numero}", background=tema[f"conjunto_{numero}"],
                                      foreground=tema["texto_conjunto"])
        return quadro

    def atualizar_tabela_da_busca(self, estado):
        if self.perfil["estrutura"] == "matriz":
            matriz = matriz_do_floyd(estado, self.sessao.vertices, "pi")
            destaques = {}
            if estado.par_atual is not None:
                i, j = estado.par_atual
                posicao = {self.sessao.vertices[k]: k for k in range(len(self.sessao.vertices))}
                destaques = {"contorno": {(posicao[i], posicao[j]): self.tema["destaque"]}}
            self.grade_pi.mostrar(matriz, destaques)
            return
        tabela = self.tabela
        limpar_tabela(tabela)
        for nome in estado.vertices_criados:
            cor = estado.cor.get(nome)
            marca = "sem_cor" if cor is None else cor
            if estado.lado.get(nome) in ("frente", "tras") and cor in ("Cinza", "Preto"):
                marca = estado.lado[nome] + "_" + cor
            if estado.numero_da_cor_do_conjunto(nome) is not None:
                marca = f"conjunto_{estado.numero_da_cor_do_conjunto(nome) % CORES_DOS_CONJUNTOS}"
            if nome == estado.vertice_em_destaque:
                marca = "destaque"
            tabela.insert("", "end", iid=nome, values=[nome] + perfis.valores_da_tabela(self.algoritmo, estado, nome),
                          tags=(marca,))
        if estado.vertice_em_destaque in estado.vertices_criados:
            tabela.see(estado.vertice_em_destaque)

    def informacao(self, estado=None):
        texto = self.sessao.descricao()
        if self.sessao.ordenar:
            texto += " · listas ordenadas"
        else:
            texto += " · sem ordenar"
        if self.algoritmo == algoritmos.PROFUNDIDADE:
            if estado is not None and estado.raizes:
                texto += " · raízes: " + ", ".join(estado.raizes)
        elif self.algoritmo == algoritmos.PRIM:
            texto += " · raiz: " + str(self.sessao.origem())
        elif self.algoritmo != algoritmos.FLOYD_WARSHALL and self.sessao.informacoes_da_busca().get("usa_origem", True):
            texto += " · origem: " + str(self.sessao.origem())
        if self.algoritmo in (algoritmos.PRIM, algoritmos.KRUSKAL) and estado is not None:
            texto += (" · na árvore: " + entrada.contar(len(estado.arvore_minima), "aresta", "arestas")
                      + ", peso " + formatar_numero(estado.peso_da_arvore))
        if self.sessao.destino_da_busca() is not None:
            texto += " · destino: " + self.sessao.destino_da_busca()
        if self.algoritmo == algoritmos.LIMITADA:
            texto += f" · limite {self.sessao.limite}"
        return texto

    def informacao_final(self):
        estado = None
        if self.sessao.passos:
            estado = self.sessao.estado_no_passo(len(self.sessao.passos) - 1)
        return self.informacao(estado)

    def tecla(self, nome):
        if self.barra is None:
            return False
        acoes = {"direita": self.barra.avancar, "esquerda": self.barra.voltar, "espaco": self.barra.play_pausa,
                 "inicio": self.barra.inicio, "fim": self.barra.fim, "mais_rapido": self.barra.mais_rapido,
                 "mais_devagar": self.barra.mais_devagar}
        if nome in acoes:
            acoes[nome]()
            return True
        return False

    def destruir(self):
        if self.barra is not None:
            self.barra.destruir()
        Parte.destruir(self)


# ----------------------------------------------------------------------
# Passo a passo
# ----------------------------------------------------------------------

class PartePassoAPasso(ParteDaBusca):
    chave = "passo"
    titulo = "Passo a passo"
    descricao = "Cada clique mostra um passo: o grafo sendo montado, a busca e, no fim, o resultado."
    escolhas_iniciais = {"posicao": None,
                         "mostrar": {"estrutura": True, "tabela": False, "codigo": False, "explicacao": True,
                                     "log": False},
                         "recolhidos": {}}
    modo = "passo"

    def montar(self, pai):
        if not self.sessao.pode_buscar():
            self.montar_problema(pai)
            return
        self.pai = pai
        pai.columnconfigure(0, weight=1)
        pai.rowconfigure(3, weight=1)
        cabecalho = ttk.Frame(pai)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        self.criar_titulo(cabecalho, com_descricao=False).grid(row=0, column=0, sticky="w")
        etapas = ttk.Frame(cabecalho)
        etapas.grid(row=0, column=1, sticky="e")
        self.botoes_da_etapa = {}
        # 1 a 4 montam o grafo (um vértice, uma aresta, uma lista por vez); 5 é a busca e 6, o resultado
        for numero, nome in ((1, "Vértices"), (2, "Arestas"), (3, "Listas"), (4, "Ordenação"),
                             (5, self.perfil["etapa_5"]), (6, self.perfil["etapa_6"])):
            botao = ttk.Button(etapas, text=f"{numero}. {nome}", style="Etapa.TButton",
                               command=lambda numero=numero: self.ir_para_etapa(numero))
            botao.pack(side="left", padx=(4, 0))
            if numero not in self.sessao.primeiro_da_etapa:
                botao.state(["disabled"])
            self.botoes_da_etapa[numero] = botao

        opcoes = [("estrutura", self.perfil["titulo_estrutura"], "A estrutura que guia a busca"),
                  ("tabela", self.perfil["titulo_tabela"].split(" (")[0],
                   "Os valores de cada vértice (cor, distância, pai...)"),
                  ("codigo", "Código", "A linha de código que faz cada passo, em 6 linguagens"),
                  ("explicacao", "Explicação", "O porquê de cada passo"),
                  ("log", "Log", "Todas as mensagens até aqui")]
        self.chips = Chips(pai, opcoes, self.escolhas["mostrar"], self.ao_mudar_chip)
        self.chips.quadro.grid(row=1, column=0, sticky="w", pady=(6, 4))

        status = ttk.Frame(pai)
        status.grid(row=2, column=0, sticky="ew", pady=(2, 6))
        status.columnconfigure(0, weight=1)
        self.rotulo_mensagem = ttk.Label(status, style="Mensagem.TLabel", justify="left")
        self.rotulo_mensagem.grid(row=0, column=0, sticky="w")
        self.rotulo_explicacao = ttk.Label(status, style="Explicacao.TLabel", justify="left")
        self.rotulo_explicacao.grid(row=1, column=0, sticky="w")
        status.bind("<Configure>", self.quebrar_linhas)

        self.divisao = ttk.PanedWindow(pai, orient="horizontal")
        self.divisao.grid(row=3, column=0, sticky="nsew")
        self.painel_do_grafo = self.criar_painel_do_grafo(self.divisao)
        self.painel_do_grafo.colocar()
        self.direita = ttk.PanedWindow(self.divisao, orient="vertical")
        self.divisao.add(self.direita, weight=2)
        self.paineis = {}
        self.montar_paineis_da_direita()
        if self.escolhas.get("recolhidos", {}).get("grafo"):
            self.painel_do_grafo.recolher()
        else:
            self.posicionar_divisao(self.divisao, 0.56)

        self.primeira = -1                  # antes do primeiro passo: o grafo ainda vazio
        self.ultima = len(self.sessao.passos) - 1
        posicao = self.escolhas.get("posicao")
        if posicao is None or not self.primeira <= posicao <= self.ultima:
            posicao = self.primeira
        self.posicao = posicao
        self.barra = BarraDoTocador(pai, self.app, self.ir_para)
        self.barra.quadro.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.barra.configurar(self.primeira, self.ultima, self.posicao)
        self.mostrar_paineis()

    def quebrar_linhas(self, evento):
        largura = max(240, evento.width - 10)
        self.rotulo_mensagem.configure(wraplength=largura)
        self.rotulo_explicacao.configure(wraplength=largura)

    def recolhidos(self):
        return {"grafo": self.painel_do_grafo.recolhido}

    # Os painéis da direita (estrutura, tabela, código, log): cada um só entra se estiver ligado
    def montar_paineis_da_direita(self):
        quadro = ttk.LabelFrame(self.direita, text=self.perfil["titulo_estrutura"], padding=6)
        if self.perfil["estrutura"] == "matriz":
            self.grade_d = GradeDeMatriz(quadro, self.app)
            self.grade_d.quadro.pack(fill="both", expand=True)
            self.desenho_da_estrutura = None
        else:
            canvas = tk.Canvas(quadro, width=140, height=160, bg=self.tema["superficie"], highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.bind("<Configure>", self.ao_redimensionar_o_desenho)
            self.desenho_da_estrutura = DesenhoDaEstrutura(canvas, self.app, self.algoritmo, self.perfil,
                                                           self.sessao.arestas, self.sessao.direcionado)
        self.paineis["estrutura"] = (quadro, 2)
        self.paineis["tabela"] = (self.criar_tabela_da_busca(self.direita), 2)
        self.painel_codigo = PainelDeCodigo(self.direita, self, preferencias=("linguagem", "comparar"))
        self.paineis["codigo"] = (self.painel_codigo.quadro, 3)
        quadro = ttk.LabelFrame(self.direita, text="Log", padding=6)
        self.painel_log = tk.Listbox(quadro, height=4, font=self.fontes["pequena"], activestyle="none",
                                     bg=self.tema["superficie"], fg=self.tema["texto"], relief="flat",
                                     highlightthickness=0, selectbackground=self.tema["fundo_destaque"],
                                     selectforeground=self.tema["texto"])
        self.painel_log.pack(side="left", fill="both", expand=True)
        rolagem = ttk.Scrollbar(quadro, orient="vertical", command=self.painel_log.yview)
        rolagem.pack(side="left", fill="y")
        self.painel_log.configure(yscrollcommand=rolagem.set)
        self.paineis["log"] = (quadro, 1)

    def mostrar_paineis(self):
        mostrar = self.escolhas["mostrar"]
        for chave in mostrar:
            if chave in self.chips.variaveis:
                self.chips.definir(chave, mostrar[chave])
        for chave in self.paineis:
            if str(self.paineis[chave][0]) in [str(pane) for pane in self.direita.panes()]:
                self.direita.forget(self.paineis[chave][0])
        algum = False
        for chave in ("estrutura", "tabela", "codigo", "log"):
            if mostrar.get(chave):
                quadro, peso = self.paineis[chave]
                self.direita.add(quadro, weight=peso)
                algum = True
        # Sem nenhum painel ligado, a direita sai e o desenho fica com a largura toda
        panes = [str(pane) for pane in self.divisao.panes()]
        if not algum and str(self.direita) in panes:
            self.divisao.forget(self.direita)
        elif algum and str(self.direita) not in panes:
            self.divisao.add(self.direita, weight=2)
        if mostrar.get("explicacao"):
            self.rotulo_explicacao.grid()
        else:
            self.rotulo_explicacao.grid_remove()
        self.mostrar()

    def ao_mudar_chip(self, chave):
        self.escolhas["mostrar"][chave] = self.chips.valor(chave)
        self.mostrar_paineis()

    def passo_no_desenho(self):
        return self.posicao

    def rotulos_do_momento(self):
        if self.posicao < 0 or self.sessao.etapas.get(self.posicao, 1) < 5:
            return None, None
        chave = perfis.chave_do_trecho(self.sessao.passos[self.posicao])
        if chave in self.codigo_de_estudo("python")["linhas_do_rotulo"]:
            return chave, None
        return None, None

    def ir_para(self, posicao):
        self.posicao = max(self.primeira, min(posicao, self.ultima))
        self.escolhas["posicao"] = self.posicao
        self.mostrar()

    def ir_para_etapa(self, numero):
        if numero in self.sessao.primeiro_da_etapa:
            self.barra.pausar()
            self.ir_para(self.sessao.primeiro_da_etapa[numero])

    # Page Down / Page Up: o começo da próxima etapa / da etapa anterior (pulando as etapas sem passos)
    def tecla(self, nome):
        if nome not in ("proxima_etapa", "etapa_anterior"):
            return ParteDaBusca.tecla(self, nome)
        atual = self.sessao.etapas.get(self.posicao, 0)
        numeros = range(atual + 1, 7) if nome == "proxima_etapa" else range(atual - 1, 0, -1)
        for numero in numeros:
            if numero in self.sessao.primeiro_da_etapa:
                self.ir_para_etapa(numero)
                return True
        self.barra.pausar()
        self.ir_para(self.ultima if nome == "proxima_etapa" else self.primeira)
        return True

    def mostrar(self):
        if not self.sessao.pode_buscar() or self.barra is None:
            return
        estado = self.sessao.estado_no_passo(self.posicao)
        self.estado = estado
        if self.posicao <= self.primeira:
            self.rotulo_mensagem.configure(text="Pronto para começar: o grafo ainda está vazio")
            self.rotulo_explicacao.configure(text="Use ▶ (ou a seta →) para montar o grafo um vértice e uma aresta por "
                                                  "vez (etapas 1 a 4) e depois ver a busca; o Play mostra sozinho. Para "
                                                  "ir direto à busca, clique na etapa 5. Os botões \"Mostrar\" "
                                                  "acrescentam a tabela, o código e o log quando você quiser.")
        else:
            passo = self.sessao.passos[self.posicao]
            self.rotulo_mensagem.configure(text=estado.mensagem)
            self.rotulo_explicacao.configure(text=explicacoes.explicar(self.algoritmo, passo))
        total = self.ultima - self.primeira
        self.barra.atualizar(self.posicao, f"passo {self.posicao - self.primeira} de {total}")
        etapa = self.sessao.etapas.get(self.posicao, 0)
        for numero in self.botoes_da_etapa:
            self.botoes_da_etapa[numero].configure(style="EtapaAtual.TButton" if numero == etapa else "Etapa.TButton")
        if self.desenho is not None:
            self.desenho.desenhar(estado, self.opcoes_do_desenho(informacao=self.informacao(estado),
                                                                 informacao_final=self.informacao_final()))
        mostrar = self.escolhas["mostrar"]
        if mostrar.get("estrutura"):
            if self.desenho_da_estrutura is not None:
                self.desenho_da_estrutura.desenhar(estado)
            else:
                self.grade_d.mostrar(matriz_do_floyd(estado, self.sessao.vertices, "d"),
                                     destaques_do_floyd(estado, self.sessao.vertices, self.tema, self.cor))
                if estado.par_atual is not None:
                    i, j = estado.par_atual
                    self.grade_d.mostrar_celula(self.sessao.vertices.index(i), self.sessao.vertices.index(j))
        if mostrar.get("tabela"):
            self.atualizar_tabela_da_busca(estado)
        if mostrar.get("codigo"):
            self.painel_codigo.atualizar()
        if mostrar.get("log"):
            self.painel_log.delete(0, "end")
            for mensagem in estado.log:
                self.painel_log.insert("end", mensagem)
            if self.painel_log.size():
                self.painel_log.itemconfigure("end", background=self.tema["fundo_destaque"])
                self.painel_log.see("end")


# ----------------------------------------------------------------------
# Linha a linha
# ----------------------------------------------------------------------

class ParteLinhaALinha(ParteDaBusca):
    chave = "linha"
    titulo = "Linha a linha"
    descricao = "O programa em Python roda de verdade, desde a primeira linha, uma por clique."
    escolhas_iniciais = {"linha": 0, "mostrar": {"variaveis": True, "saida": True, "grafo": True, "explicacao": True},
                         "escolhida": None}
    modo = "linha"

    def montar(self, pai):
        if not self.sessao.pode_buscar():
            self.montar_problema(pai)
            return
        self.pai = pai
        pai.columnconfigure(0, weight=1)
        if not self.sessao.preparar_linha_a_linha():
            self.criar_titulo(pai).grid(row=0, column=0, sticky="w")
            ttk.Label(pai, text=self.sessao.problema_da_linha, style="ErroFundo.TLabel", wraplength=700,
                      justify="left").grid(row=1, column=0, sticky="w", pady=(16, 0))
            return
        self.escolhas["mostrar"].setdefault("saida", True)     # (os .bosco antigos não tinham a Saída)
        pai.rowconfigure(3, weight=1)
        cabecalho = ttk.Frame(pai)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        self.criar_titulo(cabecalho).grid(row=0, column=0, sticky="w")
        depurador = ttk.Frame(cabecalho)
        depurador.grid(row=0, column=1, sticky="e")
        Botao(depurador, self.app, "Pular a chamada", icone="seta_direita", comando=self.pular_chamada,
              dica="Roda de uma vez a função chamada nesta linha, sem entrar nela (F10)").pack(side="left")
        Botao(depurador, self.app, "Sair da função", icone="chevron_cima", comando=self.sair_da_funcao,
              dica="Roda até a função de agora terminar e voltar para quem chamou (Shift+F11)").pack(
            side="left", padx=(6, 0))

        opcoes = [("variaveis", "Variáveis", "A memória do programa: a pilha de chamadas e os campos do objeto"),
                  ("saida", "Saída", "O que o programa já escreveu (o print)"),
                  ("grafo", "Desenho", "O desenho do grafo acompanhando as linhas"),
                  ("explicacao", "Explicação", "O que a próxima linha vai fazer, com os valores de agora")]
        self.chips = Chips(pai, opcoes, self.escolhas["mostrar"], self.ao_mudar_chip)
        self.chips.quadro.grid(row=1, column=0, sticky="w", pady=(6, 4))

        status = ttk.Frame(pai)
        status.grid(row=2, column=0, sticky="ew", pady=(2, 6))
        status.columnconfigure(0, weight=1)
        self.rotulo_mensagem = ttk.Label(status, style="Mensagem.TLabel", justify="left")
        self.rotulo_mensagem.grid(row=0, column=0, sticky="w")
        self.rotulo_explicacao = ttk.Label(status, style="Explicacao.TLabel", justify="left")
        self.rotulo_explicacao.grid(row=1, column=0, sticky="w")
        self.rotulo_da_pilha = ttk.Label(status, style="Suave.TLabel")
        self.rotulo_da_pilha.grid(row=2, column=0, sticky="w")
        status.bind("<Configure>", self.quebrar_linhas)

        self.divisao = ttk.PanedWindow(pai, orient="horizontal")
        self.divisao.grid(row=3, column=0, sticky="nsew")
        if "linguagem_da_linha" not in self.app.preferencias:
            self.app.preferencias["linguagem_da_linha"] = "python"
        self.painel_codigo = PainelDeCodigo(self.divisao, self, preferencias=("linguagem_da_linha", "comparar_da_linha"),
                                            ao_clicar_na_linha=self.clicou_na_linha,
                                            titulo="Código (clique numa linha para escolher de onde partir)")
        self.divisao.add(self.painel_codigo.quadro, weight=3)
        self.direita = ttk.PanedWindow(self.divisao, orient="vertical")
        self.divisao.add(self.direita, weight=2)
        self.painel_variaveis = PainelDeVariaveis(self.direita, self)
        self.montar_saida()
        self.painel_do_grafo = self.criar_painel_do_grafo(self.direita, peso=2)
        self.posicionar_divisao(self.divisao, 0.52)
        self.posicionar_divisao(self.direita, 0.45)

        # A barra "ir para a linha" (aparece quando uma linha é escolhida)
        self.barra_da_linha = ttk.Frame(pai, style="Painel.TFrame", padding=(10, 6))
        self.rotulo_da_linha = ttk.Label(self.barra_da_linha, style="Cartao.TLabel")
        self.rotulo_da_linha.pack(side="left")
        self.botoes_da_linha = {}
        fundo = self.tema["superficie"]
        for chave, texto, icone, dica in (
                ("primeira", "primeira", "primeiro", "Vai para a primeira vez que esta linha roda: começa daqui"),
                ("anterior", "anterior", "anterior", "A vez anterior a esta posição"),
                ("proxima", "próxima", "proximo", "Roda até a próxima vez que esta linha vai rodar"),
                ("ultima", "última", "ultimo", "A última vez que esta linha roda")):
            botao = Botao(self.barra_da_linha, self.app, texto, icone=icone, tamanho="pequeno", fundo=fundo,
                          comando=lambda chave=chave: self.ir_para_vez(chave), dica=dica)
            botao.pack(side="left", padx=(6, 0))
            self.botoes_da_linha[chave] = botao
        Botao(self.barra_da_linha, self.app, icone="x", papel="icone", tamanho="pequeno", fundo=fundo,
              comando=self.esquecer_linha, dica="Esquece a linha escolhida").pack(side="right")

        self.total = self.sessao.total_de_linhas
        self.posicao = max(0, min(self.escolhas.get("linha") or 0, self.total))
        self.barra = BarraDoTocador(pai, self.app, self.ir_para, unidade="linha")
        self.barra.quadro.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        self.barra.configurar(0, self.total, self.posicao)
        self.mostrar_paineis()

    # O painel Saída: o que o programa escreveu até agora (o print), como no terminal
    def montar_saida(self):
        tema = self.tema
        self.quadro_da_saida = ttk.LabelFrame(self.direita, text="Saída (o que o programa escreveu até aqui)",
                                              padding=6)
        self.quadro_da_saida.columnconfigure(0, weight=1)
        self.quadro_da_saida.rowconfigure(0, weight=1)
        self.texto_da_saida = tk.Text(self.quadro_da_saida, height=4, wrap="none", font=self.fontes["codigo"],
                                      bg=tema["codigo_fundo"], fg=tema["codigo_texto"], relief="flat",
                                      highlightthickness=0, padx=6, pady=4, state="disabled", takefocus=False)
        self.texto_da_saida.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(self.quadro_da_saida, orient="vertical", command=self.texto_da_saida.yview)
        rolagem.grid(row=0, column=1, sticky="ns")
        self.texto_da_saida.configure(yscrollcommand=rolagem.set)
        self.texto_da_saida.tag_configure("nova", background=tema["fundo_destaque"], foreground=tema["texto"])
        self.texto_da_saida.tag_configure("vazia", foreground=tema["texto_suave"])
        self.saida_mostrada = None

    def quebrar_linhas(self, evento):
        largura = max(240, evento.width - 10)
        self.rotulo_mensagem.configure(wraplength=largura)
        self.rotulo_explicacao.configure(wraplength=largura)

    def recolhidos(self):
        return {"grafo": self.painel_do_grafo.recolhido}

    def mostrar_paineis(self):
        mostrar = self.escolhas["mostrar"]
        for chave in mostrar:
            if chave in self.chips.variaveis:
                self.chips.definir(chave, mostrar[chave])
        for componente in (self.painel_variaveis.quadro, self.quadro_da_saida, self.painel_do_grafo.quadro,
                           self.painel_do_grafo.faixa):
            if str(componente) in [str(pane) for pane in self.direita.panes()]:
                self.direita.forget(componente)
        algum = False
        if mostrar.get("variaveis"):
            self.direita.add(self.painel_variaveis.quadro, weight=2)
            algum = True
        if mostrar.get("saida"):
            self.direita.add(self.quadro_da_saida, weight=1)
            algum = True
        if mostrar.get("grafo"):
            self.painel_do_grafo.colocar()
            algum = True
        panes = [str(pane) for pane in self.divisao.panes()]
        if not algum and str(self.direita) in panes:
            self.divisao.forget(self.direita)
        elif algum and str(self.direita) not in panes:
            self.divisao.add(self.direita, weight=2)
        if mostrar.get("explicacao"):
            self.rotulo_explicacao.grid()
        else:
            self.rotulo_explicacao.grid_remove()
        self.saida_mostrada = None
        self.mostrar()

    def ao_mudar_chip(self, chave):
        self.escolhas["mostrar"][chave] = self.chips.valor(chave)
        self.mostrar_paineis()

    def passo_no_desenho(self):
        return self.sessao.passo_da_linha[self.posicao]

    def linhas_do_momento(self, chave, programa):
        return self.linhas_no_linha_a_linha(chave, programa, self.posicao)

    def ir_para(self, posicao):
        self.posicao = max(0, min(posicao, self.total))
        self.escolhas["linha"] = self.posicao
        self.mostrar()

    def pular_chamada(self, evento=None):
        if self.posicao >= self.total:
            return "break"
        self.barra.pausar()
        linhas = self.sessao.rastro["passos_de_linha"]
        profundidade = linhas[self.posicao]["profundidade"]
        destino = self.posicao + 1
        while destino < len(linhas) and linhas[destino]["profundidade"] > profundidade:
            destino += 1
        self.ir_para(destino)
        return "break"

    def sair_da_funcao(self, evento=None):
        if self.posicao >= self.total:
            return "break"
        self.barra.pausar()
        linhas = self.sessao.rastro["passos_de_linha"]
        profundidade = linhas[self.posicao]["profundidade"]
        destino = self.posicao + 1
        while destino < len(linhas) and linhas[destino]["profundidade"] >= profundidade:
            destino += 1
        self.ir_para(destino)
        return "break"

    def tecla(self, nome):
        if nome == "pular":
            self.pular_chamada()
            return True
        if nome == "sair":
            self.sair_da_funcao()
            return True
        return ParteDaBusca.tecla(self, nome)

    # ------------------------------------------------------------------
    # Escolher uma linha do código: as vezes em que ela roda
    # ------------------------------------------------------------------

    # As linhas do programa em Python que correspondem a uma linha de outra linguagem (pelos rótulos dela)
    def linhas_python(self, chave, numero):
        if chave == "python":
            return [numero]
        if chave == BOSCOGRAPH or chave is None:
            return []
        linhas = []
        for rotulo in self.codigo_de_estudo(chave)["rotulos_da_linha"].get(numero, []):
            for linha in self.codigo_de_estudo("python")["linhas_do_rotulo"].get(rotulo, []):
                if linha not in linhas:
                    linhas.append(linha)
        return sorted(linhas)

    def clicou_na_linha(self, chave, numero):
        self.escolhas["escolhida"] = (chave, numero)
        self.mostrar()

    def esquecer_linha(self):
        self.escolhas["escolhida"] = None
        self.mostrar()

    # As posições em que a linha escolhida roda (as execuções dela, na ordem)
    def vezes_da_escolhida(self):
        escolhida = self.escolhas.get("escolhida")
        if not escolhida:
            return None, []
        chave, numero = escolhida
        posicoes = []
        for linha in self.linhas_python(chave, numero):
            for posicao in self.sessao.posicoes_da_linha(linha):
                if posicao not in posicoes:
                    posicoes.append(posicao)
        posicoes.sort()
        return escolhida, posicoes

    def ir_para_vez(self, qual):
        escolhida, posicoes = self.vezes_da_escolhida()
        if not posicoes:
            return
        self.barra.pausar()
        if qual == "primeira":
            self.ir_para(posicoes[0])
        elif qual == "ultima":
            self.ir_para(posicoes[-1])
        elif qual == "proxima":
            for posicao in posicoes:
                if posicao > self.posicao:
                    self.ir_para(posicao)
                    return
        else:
            for posicao in reversed(posicoes):
                if posicao < self.posicao:
                    self.ir_para(posicao)
                    return

    # A linha escolhida fica marcada em todas as caixas de código (na outra linguagem, as linhas dos
    # mesmos rótulos)
    def mostrar_barra_da_linha(self):
        escolhida, posicoes = self.vezes_da_escolhida()
        for visao, chave in self.painel_codigo.visoes_visiveis():
            linhas = []
            if escolhida is not None and chave not in (BOSCOGRAPH, None):
                origem, numero = escolhida
                if chave == origem:
                    linhas = [numero]
                elif origem not in (BOSCOGRAPH, None):
                    for rotulo in self.codigo_de_estudo(origem)["rotulos_da_linha"].get(numero, []):
                        for linha in self.codigo_de_estudo(chave)["linhas_do_rotulo"].get(rotulo, []):
                            if linha not in linhas:
                                linhas.append(linha)
            visao.escolher(sorted(linhas), self.tinta)
        if escolhida is None:
            self.barra_da_linha.grid_remove()
            return
        self.barra_da_linha.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        chave, numero = escolhida
        nome = estudo.linguagem(chave)["nome"] if chave not in (BOSCOGRAPH, None) else "BoscoGraph"
        if not posicoes:
            texto = f"{nome}, linha {numero}: não roda neste programa (ou não tem uma linha igual no Python)."
            for botao in self.botoes_da_linha.values():
                botao.ligar(False)
        else:
            antes = 0
            for posicao in posicoes:
                if posicao < self.posicao:
                    antes += 1
            vez = f"já passou {antes} " + ("vez" if antes == 1 else "vezes")
            texto = f"{nome}, linha {numero}: passa {len(posicoes)} " + ("vez" if len(posicoes) == 1 else "vezes") + \
                    f" neste programa ({vez})."
            for botao in self.botoes_da_linha.values():
                botao.ligar(True)
        self.rotulo_da_linha.configure(text=texto)

    # O que o programa escreveu antes do passo de agora; o que a linha anterior escreveu fica em destaque
    def mostrar_saida(self):
        sessao = self.sessao
        linhas = sessao.rastro["passos_de_linha"]
        saida = sessao.rastro["saida"]
        ate = linhas[self.posicao]["saida"] if self.posicao < len(linhas) else len(saida)
        antes = linhas[self.posicao - 1]["saida"] if self.posicao > 0 else 0
        if self.saida_mostrada == (antes, ate):
            return
        self.saida_mostrada = (antes, ate)
        caixa = self.texto_da_saida
        caixa.configure(state="normal")
        caixa.delete("1.0", "end")
        if ate == 0:
            caixa.insert("end", "(nada ainda: o programa escreve o resultado no fim, com o print)", "vazia")
        else:
            caixa.insert("end", saida[:antes])
            caixa.insert("end", saida[antes:ate], "nova")
        caixa.configure(state="disabled")
        caixa.see("end")

    def mostrar(self):
        if not self.sessao.pode_buscar() or self.barra is None:
            return
        sessao = self.sessao
        linhas = sessao.rastro["passos_de_linha"]
        programa = self.codigo_de_estudo("python")
        indice = sessao.passo_da_linha[self.posicao]
        estado = sessao.estado_no_passo(indice)
        arquivo = programa["nome"]
        if self.posicao < len(linhas):
            atual = linhas[self.posicao]
            codigo = programa["linhas"][atual["linha"] - 1].strip()
            if atual["tipo"] == "branco":
                codigo = "(linha em branco)"
            self.rotulo_mensagem.configure(text=f"Próxima linha: {codigo}")
            texto = f"{atual['explicacao']}   ({arquivo}, linha {atual['linha']})"
            self.rotulo_da_pilha.configure(text=texto_da_pilha(atual["antes"]["pilha"]))
        else:
            resposta = sessao.rastro["resposta"]
            mensagem = "O programa terminou."
            if resposta is not None:
                mensagem = f"O programa terminou: a busca devolveu {resposta}."
            self.rotulo_mensagem.configure(text=mensagem)
            texto = "O que ele escreveu está no painel Saída; o resultado da busca também está na parte Resultado."
            self.rotulo_da_pilha.configure(text="")
        if self.posicao > 0 and sessao.passo_da_linha[self.posicao] != sessao.passo_da_linha[self.posicao - 1]:
            texto += "   ·   No desenho: " + estado.mensagem
        self.rotulo_explicacao.configure(text=texto)
        self.barra.atualizar(self.posicao, f"linha {self.posicao} de {self.total}")
        self.painel_codigo.atualizar()
        self.mostrar_barra_da_linha()
        mostrar = self.escolhas["mostrar"]
        if mostrar.get("variaveis"):
            if self.posicao < len(linhas):
                foto = linhas[self.posicao]["antes"]
                aviso = (f"Os valores agora, antes de a linha {linhas[self.posicao]['linha']} rodar. Em amarelo, o que "
                         f"a linha anterior mudou.")
            else:
                foto = sessao.rastro["foto_final"]
                aviso = "O programa terminou: os valores finais. Em amarelo, o que a última linha mudou."
            anterior = linhas[self.posicao - 1]["antes"] if self.posicao > 0 else None
            self.painel_variaveis.mostrar(foto, anterior, aviso)
        if mostrar.get("saida"):
            self.mostrar_saida()
        if self.desenho is not None:
            opcoes = self.opcoes_do_desenho(informacao=self.informacao(estado), informacao_final=self.informacao_final())
            if mostrar.get("grafo"):
                self.desenho.desenhar(estado, opcoes)
            else:
                self.desenho.ultimo = (estado, opcoes)      # escondido: só anota (a exportação usa)


# ----------------------------------------------------------------------
# Comparar códigos (lado a lado)
# ----------------------------------------------------------------------

class ParteDeComparar(ParteDaBusca):
    chave = "comparar"
    titulo = "Comparar códigos"
    descricao = "Duas linguagens lado a lado, com a mesma linha destacada nas duas."
    escolhas_iniciais = {"modo": None, "posicao_passo": None, "posicao_linha": 0, "recolhidos": {"grafo": True},
                         "explicacao": True}

    def montar(self, pai):
        if not self.sessao.pode_buscar():
            self.montar_problema(pai)
            return
        self.pai = pai
        pai.columnconfigure(0, weight=1)
        pai.rowconfigure(2, weight=1)
        tem_linha = self.sessao.preparar_linha_a_linha()
        if self.escolhas.get("modo") not in ("passo", "linha"):
            self.escolhas["modo"] = "linha" if tem_linha else "passo"
        if not tem_linha:
            self.escolhas["modo"] = "passo"
        self.modo = self.escolhas["modo"]
        cabecalho = ttk.Frame(pai)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        self.criar_titulo(cabecalho).grid(row=0, column=0, sticky="w")
        self.variavel_do_modo = tk.StringVar(value=self.modo)
        opcoes = [("passo", "Passo a passo", None)]
        if tem_linha:
            opcoes.append(("linha", "Linha a linha", None))
        dica = ("Passo a passo: cada clique é um passo da busca. Linha a linha: o programa roda desde a primeira "
                "linha, uma por clique, e as duas linguagens andam juntas.")
        if not tem_linha:
            dica = self.sessao.problema_da_linha or dica
        Segmentos(cabecalho, self.app, opcoes, self.variavel_do_modo, comando=self.mudar_modo, dica=dica).grid(
            row=0, column=1, sticky="e")

        status = ttk.Frame(pai)
        status.grid(row=1, column=0, sticky="ew", pady=(6, 6))
        status.columnconfigure(0, weight=1)
        self.rotulo_mensagem = ttk.Label(status, style="Mensagem.TLabel", justify="left")
        self.rotulo_mensagem.grid(row=0, column=0, sticky="w")
        status.bind("<Configure>", lambda evento: self.rotulo_mensagem.configure(wraplength=max(240, evento.width - 10)))

        self.divisao = ttk.PanedWindow(pai, orient="horizontal")
        self.divisao.grid(row=2, column=0, sticky="nsew")
        self.painel_do_grafo = self.criar_painel_do_grafo(self.divisao, peso=2)
        self.painel_do_grafo.colocar()
        preferencias = self.app.preferencias
        preferencias.setdefault("comparar_1", "python")
        preferencias.setdefault("comparar_2", "java")
        if preferencias.get("comparar_2") is None:
            preferencias["comparar_2"] = "java"
        self.painel_codigo = PainelDeCodigo(self.divisao, self, orientacao="horizontal",
                                            preferencias=("comparar_1", "comparar_2"), titulo="Código lado a lado")
        self.divisao.add(self.painel_codigo.quadro, weight=5)
        if self.escolhas.get("recolhidos", {}).get("grafo", True):
            self.painel_do_grafo.recolher()
        else:
            self.posicionar_divisao(self.divisao, 0.3)
        self.barra = BarraDoTocador(pai, self.app, self.ir_para)
        self.barra.quadro.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.configurar_barra()

    def recolhidos(self):
        return {"grafo": self.painel_do_grafo.recolhido}

    def configurar_barra(self):
        if self.modo == "linha":
            self.posicao = max(0, min(self.escolhas.get("posicao_linha") or 0, self.sessao.total_de_linhas))
            self.barra.configurar(0, self.sessao.total_de_linhas, self.posicao, unidade="linha")
        else:
            primeira = self.sessao.primeiro_da_etapa.get(5, 0) - 1
            posicao = self.escolhas.get("posicao_passo")
            if posicao is None or posicao < primeira:
                posicao = primeira
            self.posicao = min(posicao, len(self.sessao.passos) - 1)
            self.barra.configurar(primeira, len(self.sessao.passos) - 1, self.posicao, unidade="passo")
        self.mostrar()

    # Troca o modo mantendo o mesmo momento da busca (o desenho não muda na troca)
    def mudar_modo(self):
        novo = self.variavel_do_modo.get()
        if novo == self.modo:
            return
        self.barra.pausar()
        if novo == "linha":
            self.escolhas["posicao_linha"] = self.sessao.linha_do_passo(self.posicao)
        else:
            self.escolhas["posicao_passo"] = self.sessao.passo_da_linha[self.posicao]
        self.modo = novo
        self.escolhas["modo"] = novo
        self.configurar_barra()

    def ir_para(self, posicao):
        if self.modo == "linha":
            self.posicao = max(0, min(posicao, self.sessao.total_de_linhas))
            self.escolhas["posicao_linha"] = self.posicao
        else:
            self.posicao = max(self.sessao.primeiro_da_etapa.get(5, 0) - 1, min(posicao, len(self.sessao.passos) - 1))
            self.escolhas["posicao_passo"] = self.posicao
        self.mostrar()

    def passo_no_desenho(self):
        if self.modo == "linha":
            return self.sessao.passo_da_linha[self.posicao]
        return self.posicao

    def rotulos_do_momento(self):
        if self.modo == "linha":
            linhas = self.sessao.rastro["passos_de_linha"]
            atual = linhas[self.posicao]["rotulo"] if self.posicao < len(linhas) else None
            anterior = linhas[self.posicao - 1]["rotulo"] if self.posicao > 0 else None
            return atual, anterior
        if self.posicao < 0 or self.sessao.etapas.get(self.posicao, 1) < 5:
            return None, None
        chave = perfis.chave_do_trecho(self.sessao.passos[self.posicao])
        if chave in self.codigo_de_estudo("python")["linhas_do_rotulo"]:
            return chave, None
        return None, None

    def linhas_do_momento(self, chave, programa):
        if self.modo == "linha":
            return self.linhas_no_linha_a_linha(chave, programa, self.posicao)
        return ParteDaBusca.linhas_do_momento(self, chave, programa)

    def mostrar(self):
        if self.barra is None:
            return
        indice = self.passo_no_desenho()
        estado = self.sessao.estado_no_passo(indice)
        if self.modo == "linha":
            linhas = self.sessao.rastro["passos_de_linha"]
            if self.posicao < len(linhas):
                self.rotulo_mensagem.configure(text=linhas[self.posicao]["explicacao"])
            else:
                self.rotulo_mensagem.configure(text="O programa terminou.")
            self.barra.atualizar(self.posicao, f"linha {self.posicao} de {self.sessao.total_de_linhas}")
        else:
            primeira = self.sessao.primeiro_da_etapa.get(5, 0) - 1
            if self.posicao <= primeira:
                self.rotulo_mensagem.configure(text="Pronto para começar")
            else:
                self.rotulo_mensagem.configure(text=estado.mensagem)
            self.barra.atualizar(self.posicao, f"passo {self.posicao - primeira} de "
                                               f"{len(self.sessao.passos) - 1 - primeira}")
        self.painel_codigo.atualizar()
        if self.desenho is not None:
            opcoes = self.opcoes_do_desenho(informacao=self.informacao(estado), informacao_final=self.informacao_final())
            if not self.painel_do_grafo.recolhido:
                self.desenho.desenhar(estado, opcoes)
            else:
                self.desenho.ultimo = (estado, opcoes)      # minimizado: só anota (a exportação usa)


# ----------------------------------------------------------------------
# Resultado
# ----------------------------------------------------------------------

class ParteDoResultado(ParteDaBusca):
    chave = "resultado"
    titulo = "Resultado"
    descricao = "O que a busca concluiu, uma conclusão de cada vez (clique para ver no desenho)."
    escolhas_iniciais = {"passo": None}

    def montar(self, pai):
        if not self.sessao.pode_buscar():
            self.montar_problema(pai)
            return
        self.pai = pai
        pai.columnconfigure(0, weight=1)
        pai.rowconfigure(1, weight=1)
        self.criar_titulo(pai).grid(row=0, column=0, sticky="w")
        self.divisao = ttk.PanedWindow(pai, orient="horizontal")
        self.divisao.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.painel_do_grafo = self.criar_painel_do_grafo(self.divisao)
        self.painel_do_grafo.colocar()
        direita = ttk.PanedWindow(self.divisao, orient="vertical")
        self.divisao.add(direita, weight=2)
        quadro = ttk.LabelFrame(direita, text="Conclusões", padding=6)
        colunas = [("numero", "nº", 36, False), ("conclusao", "Conclusão", 420, True)]
        interno, self.lista = self.criar_tabela(quadro, colunas, altura=7)
        interno.pack(fill="both", expand=True)
        self.lista.bind("<<TreeviewSelect>>", self.ao_escolher)
        self.rotulo_explicacao = ttk.Label(quadro, style="Explicacao.TLabel", justify="left")
        self.rotulo_explicacao.pack(fill="x", pady=(6, 0))
        quadro.bind("<Configure>", lambda evento: self.rotulo_explicacao.configure(
            wraplength=max(200, evento.width - 20)))
        direita.add(quadro, weight=2)
        if self.perfil["estrutura"] == "matriz":
            final = ttk.LabelFrame(direita, text="Matriz d final (o menor custo de cada linha até cada coluna)",
                                   padding=6)
            self.grade_final = GradeDeMatriz(final, self.app)
            self.grade_final.quadro.pack(fill="both", expand=True)
            direita.add(final, weight=2)
        else:
            self.grade_final = None
            direita.add(self.criar_tabela_da_busca(direita), weight=2)
        if self.escolhas.get("recolhidos", {}).get("grafo"):
            self.painel_do_grafo.recolher()
        else:
            self.posicionar_divisao(self.divisao, 0.5)
        self.indices = self.sessao.indices_do_resultado()
        for posicao in range(len(self.indices)):
            passo = self.sessao.passos[self.indices[posicao]]
            self.lista.insert("", "end", iid=str(self.indices[posicao]), values=(posicao + 1, passo["mensagem"]))
        escolhido = self.escolhas.get("passo")
        if (escolhido is None or not self.lista.exists(escolhido)) and self.indices:
            escolhido = str(self.indices[-1])
            self.escolhas["passo"] = escolhido
        if escolhido is not None and self.lista.exists(escolhido):
            self.lista.selection_set(escolhido)
            self.lista.see(escolhido)
        self.mostrar()

    def recolhidos(self):
        return {"grafo": self.painel_do_grafo.recolhido}

    def ao_escolher(self, evento=None):
        selecionados = self.lista.selection()
        self.escolhas["passo"] = selecionados[0] if selecionados else None
        self.mostrar()

    def mostrar(self):
        if not self.sessao.pode_buscar() or not hasattr(self, "lista"):
            return
        escolhido = self.escolhas.get("passo")
        if escolhido is not None and escolhido.isdigit() and int(escolhido) < len(self.sessao.passos):
            indice = int(escolhido)
        elif self.indices:
            indice = self.indices[-1]
        else:
            indice = len(self.sessao.passos) - 1
        estado = self.sessao.estado_no_passo(indice)
        self.rotulo_explicacao.configure(text=explicacoes.explicar(self.algoritmo, self.sessao.passos[indice]))
        if self.desenho is not None:
            self.desenho.desenhar(estado, self.opcoes_do_desenho(informacao=self.informacao(estado),
                                                                 informacao_final=self.informacao_final()))
        if self.grade_final is not None:
            self.grade_final.mostrar(matriz_do_floyd(estado, self.sessao.vertices, "d"),
                                     {"celulas": {}, "linhas": {}, "colunas": {}})
        else:
            self.atualizar_tabela_da_busca(estado)


PARTES_DA_BUSCA = [PartePassoAPasso, ParteLinhaALinha, ParteDeComparar, ParteDoResultado]
