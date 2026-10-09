# Editor do grafo: a tela que vem depois da tela inicial ("Montar meu grafo", "Começar do zero" ou
# "Continuar no editor"). O grafo é montado em três etapas, uma tela de cada vez:
#   ① Vértices -> um de cada vez (o nome e Adicionar) ou vários de uma vez (a Quantidade já cria ou tira os
#                 vértices, com os nomes A, B, C... ou 1, 2, 3...); a tabela dos vértices (Renomear, Remover);
#   ② Arestas  -> orientado ou não orientado; uma de cada vez (de, para, nome e peso opcionais) ou sorteadas
#                 (com ou sem laços e paralelas); a tabela das arestas (Editar, Remover); editar como texto;
#                 os pesos;
#   ③ Busca    -> qual busca (em três colunas, uma por tipo), por onde começar, o destino, o limite, ordenar
#                 as listas e o que falta para a busca rodar; o Visualizar.
# Em cima: o modelo (o grafo salvo com um nome; a lista dos modelos abre no botão do nome), o aviso de
# alterações não salvas, o Salvar e o Tornar padrão; e a trilha ① ② ③, que leva a qualquer etapa.
# Embaixo: o Voltar, o resumo do grafo e o Próximo (na última etapa, o Visualizar).
# O Ctrl+Z desfaz a última mudança (o botão Desfazer saiu: fica só o aviso de que há alterações).
#
# O grafo que está valendo fica em listas e dicionários, no mesmo formato do entrada.py:
#   self.vertices   -> ["A", "B", ...]
#   self.arestas    -> [("A", "B", "e1", peso), ...]
#   self.heuristica -> {"A": h, ...}
#   self.posicoes   -> {"A": (x, y), ...} (só quando o grafo veio de um desenho importado)
# Toda mudança no grafo passa por self.mudar_grafo(), que guarda o estado anterior (para o Ctrl+Z)
# e atualiza a tela. As três etapas (visual/etapas_do_editor.py) só montam e mostram; quem muda o
# grafo são as funções daqui.

import random
import tkinter as tk
from tkinter import ttk

import algoritmos
import entrada
import modelos
import pesos
from visual.botoes import Botao, Etapas, redesenhar_componentes
from visual.cabecalho import Cabecalho
from visual.campos import Selo
from visual.dialogos import DialogoDeAresta, DialogoDeArestas, DialogoDeConfirmacao, DialogoDePesos, DialogoDeTexto
from visual.etapas_do_editor import EtapaDaBusca, EtapaDasArestas, EtapaDosVertices

# Valores iniciais dos campos de sorteio (em texto, como aparecem na tela)
CAMPOS_INICIAIS = {
    "estilo": "letras",             # os nomes que a Quantidade cria: "letras" (A, B, C...) ou "numeros" (1, 2, 3...)
    "quantidade_arestas": "12",
    "lacos": False,
    "paralelas": False,
}
MENOR_SORTEIO_DE_VERTICES = 4       # "Sortear quantidade" escolhe de 4 a 12 vértices
MAIOR_SORTEIO_DE_VERTICES = 12
TAMANHO_DO_HISTORICO = 50           # quantas mudanças o Ctrl+Z lembra
SEM_DESTINO = "(nenhum)"            # o valor da escolha do destino quando não há destino
NOMES_DAS_ETAPAS = ["Vértices", "Arestas", "Busca"]
# A troca de etapa desliza a tela: quantos quadros a animação tem e o tempo entre eles
QUADROS_DO_DESLIZE = 8
MILISSEGUNDOS_DO_DESLIZE = 15


# Os valores da tela quando o BoscoGraph abre: o grafo do modelo padrão e os campos iniciais
def valores_iniciais():
    valores = dict(CAMPOS_INICIAIS)
    try:
        nome = modelos.nome_do_padrao()
        grafo = modelos.carregar_modelo(nome)
        aviso = f"Modelo padrão \"{nome}\" carregado. Edite à vontade: Ctrl+Z desfaz a última mudança."
        aviso_de_erro = False
    except (OSError, ValueError) as problema:
        nome = modelos.NOME_DO_MODELO_DA_PROVA
        vertices, arestas = entrada.grafo_da_prova()
        grafo = modelos.novo_grafo(vertices, arestas, True, "A", True)
        aviso = f"Não consegui abrir o modelo padrão ({problema}). Abri o grafo da prova."
        aviso_de_erro = True
    valores["modelo"] = nome
    valores["modelo_aberto"] = nome         # o arquivo de onde o grafo veio (Salvar nele não pergunta nada)
    valores["grafo"] = grafo
    valores["referencia"] = None            # é preenchida quando a tela abre (veja o __init__)
    valores["historico"] = []
    valores["etapa"] = 0
    valores["aviso"] = aviso
    valores["aviso_de_erro"] = aviso_de_erro
    return valores


# O grafo como o editor o compara com o arquivo (o mesmo formato de EditorDoGrafo.estado_do_grafo)
def estado_de_um_grafo(grafo):
    return {
        "vertices": list(grafo["vertices"]),
        "arestas": list(grafo["arestas"]),
        "ordenar": grafo["ordenar"],
        "inicio": grafo["inicio"] or "",
        "direcionado": grafo["direcionado"],
        "algoritmo": grafo["algoritmo"],
        "destino": grafo["destino"],
        "heuristica": dict(grafo["heuristica"]),
        "posicoes": dict(grafo["posicoes"]),
        "arrumacao": grafo["arrumacao"],
        "limite": grafo.get("limite"),
    }


# Os valores do editor para um grafo que vem de fora (um exemplo da tela inicial), no formato de
# valores_iniciais. Ele começa "igual ao arquivo" (não alterado); modelo_aberto vazio faz o Salvar
# pedir um nome antes de gravar. Um grafo que chega começa na primeira etapa.
def valores_de_um_grafo(grafo, nome, aviso):
    valores = dict(CAMPOS_INICIAIS)
    valores["modelo"] = nome
    valores["modelo_aberto"] = ""
    valores["grafo"] = grafo
    valores["referencia"] = estado_de_um_grafo(grafo)
    valores["historico"] = []
    valores["etapa"] = 0
    valores["aviso"] = aviso
    valores["aviso_de_erro"] = False
    return valores


# Os valores do editor para abrir um grafo que vem de fora (um exemplo, uma importação, um .bosco ou o
# "Começar do zero") SEM PERDER o que estava no editor: o grafo de antes vai para o Desfazer, e o Ctrl+Z
# no editor volta para ele. Os campos de sorteio também continuam como estavam.
# igual_ao_arquivo: True = o grafo é igual ao arquivo de onde veio (um exemplo, um .bosco);
#                   False = nunca foi salvo como modelo (aparece "Ainda não salvo").
def valores_para_abrir(app, grafo, nome, aviso, igual_ao_arquivo=True):
    valores = valores_de_um_grafo(grafo, nome, aviso)
    if not igual_ao_arquivo:
        valores["referencia"] = None
    anterior = app.ultimo_editor
    if anterior is not None:
        foto = estado_de_um_grafo(anterior["grafo"])        # a mesma "foto" que o Desfazer do editor guarda
        foto["modelo"] = anterior["modelo"]
        foto["modelo_aberto"] = anterior["modelo_aberto"]
        foto["referencia"] = anterior["referencia"]
        historico = list(anterior["historico"]) + [foto]
        valores["historico"] = historico[-TAMANHO_DO_HISTORICO:]
        for campo in CAMPOS_INICIAIS:
            if campo in anterior:
                valores[campo] = anterior[campo]
    return valores


# O que a visualização recebe: o grafo, as opções da busca e os textos do título.
# "valores" é o estado do editor, para o "Editar grafo" voltar a ele igual.
def configuracao_da_visualizacao(grafo, titulo, valores):
    busca = algoritmos.algoritmo(grafo["algoritmo"])
    orientacao = "orientado" if grafo["direcionado"] else "não orientado"
    return {
        "vertices": list(grafo["vertices"]),
        "arestas": list(grafo["arestas"]),
        "ordenar": grafo["ordenar"],
        "inicio": grafo["inicio"] or None,
        "direcionado": grafo["direcionado"],
        "algoritmo": busca["chave"],
        "destino": grafo["destino"],
        "heuristica": dict(grafo["heuristica"]),
        "posicoes": dict(grafo["posicoes"]),
        "arrumacao": grafo["arrumacao"],
        "limite": grafo.get("limite"),
        "nome": titulo,
        "titulo": titulo + " · " + busca["nome_curto"],
        "descricao": (titulo + " · " + orientacao + " · "
                      + entrada.resumo(grafo["vertices"], grafo["arestas"], grafo["direcionado"])),
        "valores": valores,
    }


class EditorDoGrafo:
    def __init__(self, app, valores):
        self.app = app
        self.tema = app.tema
        self.fontes = app.fontes
        primeira_vez = valores is None
        if primeira_vez:
            valores = valores_iniciais()
        grafo = valores["grafo"]

        # O grafo que está valendo agora
        self.vertices = list(grafo["vertices"])
        self.arestas = list(grafo["arestas"])
        self.heuristica = dict(grafo["heuristica"])
        self.posicoes = dict(grafo["posicoes"])
        self.historico = list(valores["historico"])     # estados anteriores, para o Ctrl+Z
        self.modelo_aberto = valores["modelo_aberto"]
        # Como o grafo estava no arquivo quando foi aberto ou salvo. Se o grafo atual
        # for diferente disso, ele está "alterado" (None = nunca foi salvo)
        self.referencia = valores["referencia"]
        self.etapa = max(0, min(len(NOMES_DAS_ETAPAS) - 1, valores.get("etapa", 0)))
        estilo = valores.get("estilo", "letras")
        if estilo not in ("letras", "numeros"):
            estilo = "letras"           # o estilo "Prefixo" saiu do editor (o Daniel pediu)

        # Variáveis do Tkinter ligadas aos campos: quando o campo muda, a variável muda (e vice-versa)
        self.nome_do_modelo = tk.StringVar(value=valores["modelo"])
        self.ordenar = tk.BooleanVar(value=grafo["ordenar"])
        self.direcionado = tk.BooleanVar(value=grafo["direcionado"])     # orientado (A -> B) ou não (A — B)
        self.inicio = tk.StringVar(value=grafo["inicio"] or "")
        self.busca = tk.StringVar(value=algoritmos.algoritmo(grafo["algoritmo"])["chave"])
        self.destino = tk.StringVar(value=grafo["destino"] or SEM_DESTINO)
        self.arrumacao = tk.StringVar(value=grafo["arrumacao"])
        self.limite = tk.StringVar(value=str(grafo.get("limite") if grafo.get("limite") is not None else 3))
        self.quantidade_vertices = tk.StringVar(value=str(len(self.vertices)))
        self.estilo = tk.StringVar(value=estilo)
        self.quantidade_arestas = tk.StringVar(value=valores.get("quantidade_arestas", "12"))
        self.lacos = tk.BooleanVar(value=valores.get("lacos", False))
        self.paralelas = tk.BooleanVar(value=valores.get("paralelas", False))
        self.novo_vertice = tk.StringVar()
        self.nova_origem = tk.StringVar()
        self.novo_destino = tk.StringVar()
        self.novo_nome_da_aresta = tk.StringVar()
        self.novo_peso = tk.StringVar()
        self.aviso = valores["aviso"]
        self.aviso_de_erro = valores["aviso_de_erro"]
        self.atualizando = False        # True enquanto a tela é atualizada (as escolhas não reagem)
        self.deslize = None             # o "after" da animação de troca de etapa

        self.montar()
        self.atualizar()
        if primeira_vez:
            self.referencia = self.estado_do_grafo()    # acabou de abrir: igual ao arquivo
            self.atualizar_modelo()
        self.avisar(self.aviso, self.aviso_de_erro)
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))
        self.ligar_atalhos()
        self.mostrar_etapa(self.etapa, animar=False)

    # ------------------------------------------------------------------
    # Montagem da tela
    # ------------------------------------------------------------------

    def montar(self):
        self.quadro = ttk.Frame(self.app.raiz, padding=(16, 10, 16, 8))
        self.quadro.pack(fill="both", expand=True)
        self.quadro.columnconfigure(0, weight=1)
        self.quadro.rowconfigure(3, weight=1)       # a linha das etapas é a que cresce

        self.cabecalho = Cabecalho(self.quadro, self.app, "Editor do grafo",
                                   "Monte o grafo em três etapas: os vértices, as arestas e a busca",
                                   voltar=self.app.mostrar_inicio)
        self.cabecalho.grid(row=0, column=0, sticky="ew")
        # Importar fica no topo: é o jeito de começar a partir de um desenho feito em outro programa
        Botao(self.cabecalho.botoes, self.app, "Importar desenho", icone="importar", papel="info",
              comando=self.importar,
              dica="Traz um grafo desenhado em outro programa: draw.io, GraphML, DOT, CSV, PDF ou imagem "
                   "(Ctrl+O). O grafo de agora vai para o Ctrl+Z.").pack(side="left")

        self.montar_barra_do_modelo()
        self.montar_trilha()

        # As três etapas ficam uma em cima da outra, na mesma área: só a de agora aparece
        self.area = ttk.Frame(self.quadro)
        self.area.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        self.etapas = [EtapaDosVertices(self, self.area), EtapaDasArestas(self, self.area),
                       EtapaDaBusca(self, self.area)]
        self.montar_rodape()

    # O modelo: [📄 Meu grafo ▾]  ● Alterações não salvas   [Salvar] [Tornar padrão]
    def montar_barra_do_modelo(self):
        tema = self.tema
        barra = ttk.Frame(self.quadro)
        barra.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(barra, text="Modelo", style="Suave.TLabel").pack(side="left", padx=(0, 8))
        self.menu_dos_modelos = tk.Menu(barra, tearoff=False, bg=tema["superficie"], fg=tema["texto"],
                                        activebackground=tema["acento"], activeforeground=tema["texto_acento"],
                                        disabledforeground=tema["texto_suave"], font=self.fontes["texto"])
        self.botao_do_modelo = Botao(barra, self.app, self.titulo_do_modelo(), icone="arquivo", papel="neutro",
                                     menu=self.menu_dos_modelos, antes_de_abrir=self.montar_menu_dos_modelos,
                                     dica="Os grafos salvos (modelos): clique para abrir outro ou salvar com outro "
                                          "nome")
        self.botao_do_modelo.pack(side="left")
        self.selo = Selo(barra, self.app, dica="Ctrl+Z desfaz a última mudança; Ctrl+S salva o modelo")
        self.selo.pack(side="left", padx=(10, 0))
        self.botao_salvar = Botao(barra, self.app, "Salvar", icone="disquete", papel="suave",
                                  comando=self.salvar_modelo, dica=self.texto_do_salvar)
        self.botao_salvar.pack(side="left", padx=(14, 0))
        self.botao_padrao = Botao(barra, self.app, "Tornar padrão", icone="estrela", papel="suave",
                                  comando=self.tornar_padrao,
                                  dica="O modelo padrão é o que abre quando o BoscoGraph começa")
        self.botao_padrao.pack(side="left", padx=(8, 0))

    # A trilha ① Vértices ── ② Arestas ── ③ Busca: clicar numa etapa leva até ela
    def montar_trilha(self):
        linha = ttk.Frame(self.quadro)
        linha.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.trilha = Etapas(linha, self.app, self.textos_das_etapas(), atual=self.etapa,
                             ao_clicar=self.mostrar_etapa, livre=True, feitas=self.etapas_feitas())
        self.trilha.pack()
        ttk.Separator(linha, orient="horizontal").pack(fill="x", pady=(8, 0))

    # Embaixo: [◀ Voltar]   8 vértices · 12 arestas · Tipo: ...   [Próximo: Arestas ▶] (ou [▶ Visualizar])
    # e, mais embaixo, o resultado da última ação (em vermelho, se for um problema)
    def montar_rodape(self):
        rodape = ttk.Frame(self.quadro)
        rodape.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        rodape.columnconfigure(1, weight=1)
        self.botao_voltar = Botao(rodape, self.app, "Voltar", icone="seta_esquerda", papel="contorno",
                                  comando=self.etapa_anterior, dica="A etapa anterior (Alt+←)")
        self.botao_voltar.grid(row=0, column=0, sticky="w")
        self.rotulo_resumo = ttk.Label(rodape, style="Suave.TLabel", anchor="center", justify="center")
        self.rotulo_resumo.grid(row=0, column=1, sticky="ew", padx=12)
        self.botao_proximo = Botao(rodape, self.app, "Próximo", icone="seta_direita", papel="principal",
                                   comando=self.proxima_etapa, icone_depois=True, dica="A próxima etapa (Alt+→)")
        self.botao_proximo.grid(row=0, column=2, sticky="e")
        self.botao_visualizar = Botao(rodape, self.app, "Visualizar", icone="play", papel="principal",
                                      tamanho="grande", comando=self.visualizar, dica=self.texto_do_visualizar)
        self.botao_visualizar.grid(row=0, column=2, sticky="e")
        self.rotulo_aviso = ttk.Label(self.quadro, style="Suave.TLabel", justify="left")
        self.rotulo_aviso.grid(row=5, column=0, sticky="ew", pady=(6, 0))
        self.quadro.bind("<Configure>", self.ajustar_quebras_de_linha)

    def ajustar_quebras_de_linha(self, evento):
        self.rotulo_aviso.configure(wraplength=max(300, evento.width - 40))
        self.rotulo_resumo.configure(wraplength=max(200, evento.width - 420))

    def ligar_atalhos(self):
        teclas = {"<F5>": self.visualizar, "<Control-Return>": self.visualizar,
                  "<Control-z>": self.desfazer, "<Control-Z>": self.desfazer,         # Z: com Caps Lock ligado
                  "<Control-s>": self.salvar_modelo, "<Control-S>": self.salvar_modelo,
                  "<Control-o>": self.importar, "<Control-O>": self.importar,
                  "<Alt-Right>": self.proxima_etapa, "<Alt-Left>": self.etapa_anterior}
        for tecla in teclas:
            self.app.raiz.bind(tecla, teclas[tecla])
        self.teclas = list(teclas)

    # ------------------------------------------------------------------
    # As etapas: qual aparece, a trilha e o rodapé
    # ------------------------------------------------------------------

    # Os nomes na trilha, com quantos vértices e arestas já existem: "Vértices (8)"
    def textos_das_etapas(self):
        textos = list(NOMES_DAS_ETAPAS)
        if self.vertices:
            textos[0] += f" ({len(self.vertices)})"
        if self.arestas:
            textos[1] += f" ({len(self.arestas)})"
        return textos

    # As etapas que ganham o "certo" verde na trilha: tem vértice, tem aresta, a busca pode rodar
    def etapas_feitas(self):
        feitas = []
        if self.vertices:
            feitas.append(0)
        if self.arestas:
            feitas.append(1)
        problemas, avisos = self.conferir_busca()
        if not problemas:
            feitas.append(2)
        return feitas

    # Mostra a etapa "indice". animar: a tela desliza (para a esquerda quando avança, para a direita quando volta)
    def mostrar_etapa(self, indice, animar=True):
        self.confirmar_contadores()
        indice = max(0, min(len(self.etapas) - 1, indice))
        anterior = self.etapa
        self.etapa = indice
        self.parar_deslize()
        nova = self.etapas[indice].quadro
        if animar and anterior != indice and self.quadro.winfo_ismapped():
            velha = self.etapas[anterior].quadro
            for etapa in self.etapas:
                if etapa.quadro is not nova and etapa.quadro is not velha:
                    etapa.quadro.place_forget()
            sentido = 1 if indice > anterior else -1
            self.deslizar(velha, nova, sentido, 1)
        else:
            for etapa in self.etapas:
                if etapa.quadro is not nova:
                    etapa.quadro.place_forget()
            nova.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.trilha.mudar(indice, self.etapas_feitas())
        self.atualizar_rodape()
        self.etapas[indice].ao_mostrar()
        return "break"

    # Um número digitado numa Quantidade (ou no Limite) sem o Enter também vale: o clique nos botões
    # desenhados não tira o foco da caixa, então o "sair da caixa" não aconteceria
    def confirmar_contadores(self):
        for contador in (self.etapas[0].contador, self.etapas[1].contador, self.etapas[2].contador_do_limite):
            contador.ao_sair()

    # Um quadro da animação: as duas telas andam juntas (começa rápido e termina devagar)
    def deslizar(self, velha, nova, sentido, quadro):
        self.deslize = None
        fracao = 1 - (1 - quadro / QUADROS_DO_DESLIZE) ** 2
        velha.place(relx=-sentido * fracao, rely=0, relwidth=1, relheight=1)
        nova.place(relx=sentido * (1 - fracao), rely=0, relwidth=1, relheight=1)
        if quadro >= QUADROS_DO_DESLIZE:
            velha.place_forget()
            nova.place(relx=0, rely=0, relwidth=1, relheight=1)
            return
        self.deslize = self.app.raiz.after(MILISSEGUNDOS_DO_DESLIZE,
                                           lambda: self.deslizar(velha, nova, sentido, quadro + 1))

    def parar_deslize(self):
        if self.deslize is not None:
            self.app.raiz.after_cancel(self.deslize)
            self.deslize = None

    def proxima_etapa(self, evento=None):
        if self.etapa < len(self.etapas) - 1:
            self.mostrar_etapa(self.etapa + 1)
        return "break"

    def etapa_anterior(self, evento=None):
        if self.etapa > 0:
            self.mostrar_etapa(self.etapa - 1)
        return "break"

    # O rodapé muda com a etapa: na primeira não há Voltar; na última, o Próximo vira o Visualizar
    def atualizar_rodape(self):
        if self.etapa == 0:
            self.botao_voltar.grid_remove()
        else:
            self.botao_voltar.grid()
            self.botao_voltar.configurar(texto="Voltar: " + NOMES_DAS_ETAPAS[self.etapa - 1])
        if self.etapa < len(self.etapas) - 1:
            self.botao_visualizar.grid_remove()
            self.botao_proximo.grid()
            self.botao_proximo.configurar(texto="Próximo: " + NOMES_DAS_ETAPAS[self.etapa + 1])
        else:
            self.botao_proximo.grid_remove()
            self.botao_visualizar.grid()
        problemas, avisos = self.conferir_busca()
        self.botao_visualizar.configurar(habilitado=not problemas)
        # No meio: o resumo do grafo; na etapa Busca, se algo impede a busca, o primeiro problema (em vermelho)
        if self.etapa == len(self.etapas) - 1 and problemas:
            texto = "Falta: " + problemas[0]
            if len(problemas) > 1:
                texto += f" (e mais {len(problemas) - 1})"
            self.rotulo_resumo.configure(text=texto, style="ErroFundo.TLabel")
            return
        if self.vertices:
            texto = entrada.resumo(self.vertices, self.arestas, self.direcionado.get())
            texto += " · " + self.nome_da_orientacao() + "\nTipo: " + self.tipo_do_grafo()
        else:
            texto = "Grafo vazio: comece pelos vértices"
        self.rotulo_resumo.configure(text=texto, style="Suave.TLabel")

    # ------------------------------------------------------------------
    # Atualização da tela (depois de qualquer mudança)
    # ------------------------------------------------------------------

    def atualizar(self):
        self.atualizando = True
        self.orientacao_mostrada = self.direcionado.get()     # para o mudar_orientacao saber se mudou mesmo
        # O estilo dos nomes acompanha os vértices (depois de um Ctrl+Z, por exemplo)
        estilo = entrada.estilo_dos_nomes(self.vertices)
        if estilo is not None and estilo != self.estilo.get():
            self.estilo.set(estilo)
        self.conferir_escolhas_de_vertice()
        for etapa in self.etapas:
            etapa.atualizar()
        self.atualizar_modelo()
        self.trilha.mudar_textos(self.textos_das_etapas())
        self.trilha.mudar(self.etapa, self.etapas_feitas())
        self.atualizar_rodape()
        self.atualizando = False

    # As escolhas de vértice (origem e destino da aresta nova, início e destino da busca) só podem ter
    # vértices que existem
    def conferir_escolhas_de_vertice(self):
        if self.destino.get() not in self.vertices:
            self.destino.set(SEM_DESTINO)
        if not self.vertices:
            self.nova_origem.set("")
            self.novo_destino.set("")
            self.inicio.set("")
            return
        if self.nova_origem.get() not in self.vertices:
            self.nova_origem.set(self.vertices[0])
        if self.novo_destino.get() not in self.vertices:
            self.novo_destino.set(self.vertices[min(1, len(self.vertices) - 1)])
        if self.inicio.get() not in self.vertices:
            self.inicio.set(sorted(self.vertices)[0])       # o mesmo que a busca faria sem escolher

    # A busca escolhida (o dicionário de algoritmos.py)
    def busca_escolhida(self):
        return algoritmos.algoritmo(self.busca.get())

    # As colunas Peso e h só aparecem quando fazem sentido: quando a busca usa, ou quando o grafo já tem
    def mostrar_coluna_de_peso(self):
        return self.busca_escolhida()["usa_pesos"] != "nao" or entrada.tem_pesos(self.arestas)

    def mostrar_coluna_de_heuristica(self):
        return self.busca_escolhida()["usa_heuristica"] or len(self.heuristica) > 0

    # Como a aresta aparece nas tabelas: A → B (orientado) ou A — B (não orientado)
    def ligacao(self, origem, destino):
        if self.direcionado.get():
            return f"{origem} → {destino}"
        return f"{origem} — {destino}"

    def titulo_do_modelo(self):
        return self.nome_do_modelo.get().strip() or "Grafo sem nome"

    # O botão do modelo, o selo (alterações não salvas ou não) e o Tornar padrão
    def atualizar_modelo(self):
        tema = self.tema
        self.botao_do_modelo.configurar(texto=self.titulo_do_modelo())
        if self.referencia is None:
            self.selo.mudar("Ainda não salvo", tema["destaque"], "bolinha")
        elif self.esta_alterado():
            self.selo.mudar("Alterações não salvas", tema["destaque"], "bolinha")
        else:
            self.selo.mudar("Sem alterações", tema["sucesso"], "check")
        salvo = self.modelo_salvo()
        padrao = salvo and modelos.mesmo_nome(self.modelo_aberto, self.nome_do_padrao())
        if padrao:
            self.botao_padrao.configurar(texto="Modelo padrão", habilitado=False)
        else:
            self.botao_padrao.configurar(texto="Tornar padrão", habilitado=salvo)

    # O modelo aberto existe como arquivo? (um exemplo, uma importação ou um grafo novo ainda não existem)
    def modelo_salvo(self):
        if self.modelo_aberto == "":
            return False
        try:
            return modelos.existe_modelo(self.modelo_aberto)
        except OSError:
            return False

    def nome_do_padrao(self):
        try:
            return modelos.nome_do_padrao()
        except OSError:
            return ""

    # O destino escolhido (None = nenhum)
    def destino_escolhido(self):
        destino = self.destino.get()
        if destino in self.vertices:
            return destino
        return None

    def conferir_busca(self):
        return algoritmos.conferir(self.busca.get(), self.vertices, self.arestas, self.direcionado.get(),
                                   self.inicio.get() or None, self.destino_escolhido(), self.heuristica,
                                   self.limite_escolhido(), self.ordenar.get())

    # O limite escolhido (None = ainda não é um número; só a busca limitada usa)
    def limite_escolhido(self):
        if not self.busca_escolhida()["usa_limite"]:
            return None
        texto = self.limite.get().strip()
        if texto.isdigit():
            return int(texto)
        return None

    # Textos das dicas (calculados na hora em que aparecem)
    def texto_do_visualizar(self):
        problemas, avisos = self.conferir_busca()
        if problemas:
            return "Ainda não dá para visualizar: " + problemas[0]
        return "Abre a visualização passo a passo (F5)"

    def texto_do_salvar(self):
        return f"Grava o grafo como um modelo (Ctrl+S), na pasta:\n{modelos.PASTA_DOS_MODELOS}"

    # Escreve o resultado da última ação na linha de baixo (em vermelho se for um problema)
    def avisar(self, texto, erro=False):
        self.aviso = texto
        self.aviso_de_erro = erro
        self.rotulo_aviso.configure(text=texto, style="ErroFundo.TLabel" if erro else "Suave.TLabel")

    # O que a pessoa pode fazer para resolver um problema da busca: (texto do botão, o que ele faz) ou None.
    # Os botões aparecem na lista "Antes de visualizar" da etapa Busca.
    def acao_do_problema(self, problema):
        if problema.startswith("Crie pelo menos um vértice") or "Floyd-Warshall compara" in problema:
            return "Ir para Vértices", lambda: self.mostrar_etapa(0)
        if "sem peso" in problema:
            return "Dar pesos…", lambda: self.abrir_pesos("arestas")
        if "sem h" in problema:
            return "Dar h…", lambda: self.abrir_pesos("vertices")
        if "peso negativo" in problema:
            return "Ir para Arestas", lambda: self.mostrar_etapa(1)
        if "grafos não orientados" in problema:
            return "Tornar não orientado", self.tornar_nao_orientado
        return None

    # A busca, o início, o destino, o limite ou a ordenação mudaram (nas escolhas da etapa Busca):
    # as colunas das tabelas, o que falta e o aviso de alterações mudam junto
    def ao_mudar_busca(self, *argumentos):
        if not self.atualizando:
            self.atualizar()

    # ------------------------------------------------------------------
    # Mudanças no grafo e Desfazer
    # ------------------------------------------------------------------

    # O que vai para o arquivo do modelo: serve para saber se o grafo foi alterado
    def estado_do_grafo(self):
        return {
            "vertices": list(self.vertices),
            "arestas": list(self.arestas),
            "ordenar": self.ordenar.get(),
            "inicio": self.inicio.get(),
            "direcionado": self.direcionado.get(),
            "algoritmo": self.busca.get(),
            "destino": self.destino_escolhido(),
            "heuristica": dict(self.heuristica),
            "posicoes": dict(self.posicoes),
            "arrumacao": self.arrumacao.get(),
            "limite": self.limite_escolhido(),
        }

    # O grafo com as opções, no formato de modelos.novo_grafo (para salvar e para voltar à tela)
    def grafo_atual(self):
        return modelos.novo_grafo(self.vertices, self.arestas, self.ordenar.get(), self.inicio.get() or None,
                                  self.direcionado.get(), self.busca.get(), self.destino_escolhido(),
                                  self.heuristica, self.posicoes, self.arrumacao.get(), self.limite_escolhido())

    # Alterado = diferente de como estava no arquivo quando foi aberto ou salvo
    def esta_alterado(self):
        return self.referencia is None or self.estado_do_grafo() != self.referencia

    # Uma "foto" de tudo o que o Desfazer precisa restaurar
    def foto_do_estado(self):
        foto = self.estado_do_grafo()
        foto["modelo"] = self.nome_do_modelo.get()
        foto["modelo_aberto"] = self.modelo_aberto
        foto["referencia"] = self.referencia
        return foto

    def guardar_para_desfazer(self, foto=None):
        if foto is None:
            foto = self.foto_do_estado()
        self.historico.append(foto)
        if len(self.historico) > TAMANHO_DO_HISTORICO:
            self.historico.pop(0)       # esquece a mudança mais antiga

    # Toda mudança no grafo passa por aqui: guarda o estado de antes, troca as listas
    # e atualiza a tela. A heurística e as posições acompanham os vértices: se não vierem
    # novas, as de quem saiu do grafo são esquecidas. inicio e destino: None = continuam como estão.
    def mudar_grafo(self, vertices, arestas, aviso, inicio=None, heuristica=None, posicoes=None, destino=None):
        self.guardar_para_desfazer()
        self.vertices = vertices
        self.arestas = arestas
        if heuristica is None:
            heuristica = self.heuristica
        if posicoes is None:
            posicoes = self.posicoes
        self.heuristica = entrada.manter_chaves(heuristica, vertices)
        self.posicoes = entrada.manter_chaves(posicoes, vertices)
        if inicio is not None:
            self.inicio.set(inicio)
        if destino is not None:
            self.destino.set(destino)
        self.atualizar()
        self.avisar(aviso)

    # Troca os vértices por "novos", com o "mapa" de nomes (antigo -> novo) das funções do entrada.py:
    # as arestas, a heurística, as posições, o início e o destino acompanham
    def aplicar_novos_nomes(self, novos, mapa, aviso):
        inicio = mapa.get(self.inicio.get(), "")
        destino = mapa.get(self.destino.get(), SEM_DESTINO)
        self.mudar_grafo(novos, entrada.renomear_arestas(self.arestas, mapa), aviso, inicio=inicio,
                         heuristica=entrada.renomear_chaves(self.heuristica, mapa),
                         posicoes=entrada.renomear_chaves(self.posicoes, mapa), destino=destino)
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))

    # Clique em "Orientado" ou "Não orientado". Quando esta função é chamada, a variável já mudou;
    # por isso a foto para o Desfazer é corrigida com a orientação de antes do clique.
    def mudar_orientacao(self):
        if self.direcionado.get() == self.orientacao_mostrada:
            return          # clicou no que já estava marcado: nada mudou
        foto = self.foto_do_estado()
        foto["direcionado"] = self.orientacao_mostrada
        self.guardar_para_desfazer(foto)
        self.atualizar()
        if self.direcionado.get():
            self.avisar("Grafo orientado: cada aresta tem sentido (A → B) e entra só na lista da origem. "
                        "Ctrl+Z desfaz.")
        else:
            self.avisar("Grafo não orientado: cada aresta vale nos dois sentidos (A — B) e entra nas duas listas. "
                        "Ctrl+Z desfaz.")

    # Prim e Kruskal: a árvore geradora mínima é para grafos não orientados (o botão do que falta)
    def tornar_nao_orientado(self):
        self.direcionado.set(False)
        self.mudar_orientacao()

    def nome_da_orientacao(self):
        if self.direcionado.get():
            return "orientado"
        return "não orientado"

    # O tipo do grafo (simples, completo, cíclico, DAG...), calculado pela mesma análise da etapa 6 da DFS:
    # roda a busca em profundidade inteira (é instantâneo) e pega o resumo, que é o último passo anotado
    def tipo_do_grafo(self):
        passos = self.app.montar_passos(self.vertices, self.arestas, self.ordenar.get(), self.inicio.get() or None,
                                        self.direcionado.get())
        for passo in reversed(passos):
            if passo["tipo"] == "tipo_resumo":
                return passo["resumo_curto"]
        return ""

    def desfazer(self, evento=None):
        if not self.historico:
            self.avisar("Não há mais nada para desfazer.")
            return "break"
        anterior = self.historico.pop()
        self.atualizando = True
        self.vertices = anterior["vertices"]
        self.arestas = anterior["arestas"]
        self.heuristica = anterior["heuristica"]
        self.posicoes = anterior["posicoes"]
        self.nome_do_modelo.set(anterior["modelo"])
        self.modelo_aberto = anterior["modelo_aberto"]
        self.referencia = anterior["referencia"]
        self.ordenar.set(anterior["ordenar"])
        self.inicio.set(anterior["inicio"])
        self.direcionado.set(anterior["direcionado"])
        self.busca.set(algoritmos.algoritmo(anterior["algoritmo"])["chave"])
        self.destino.set(anterior["destino"] or SEM_DESTINO)
        self.arrumacao.set(anterior["arrumacao"])
        if anterior.get("limite") is not None:
            self.limite.set(str(anterior["limite"]))
        self.atualizar()
        self.avisar("Última mudança desfeita.")
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))
        return "break"

    # ------------------------------------------------------------------
    # Leitura dos campos e das tabelas
    # ------------------------------------------------------------------

    # Converte o texto de um campo em número inteiro dentro dos limites.
    # Se não der, mostra o problema e devolve None.
    def ler_numero(self, variavel, nome, minimo, maximo, explicacao=""):
        try:
            numero = int(variavel.get())
        except ValueError:
            self.avisar(f"{nome}: digite um número inteiro.", erro=True)
            return None
        if numero < minimo or numero > maximo:
            texto = f"{nome}: use um valor de {minimo} a {maximo}."
            if explicacao:
                texto += " " + explicacao
            self.avisar(texto, erro=True)
            return None
        return numero

    def tabela_vertices(self):
        return self.etapas[0].tabela

    def tabela_arestas(self):
        return self.etapas[1].tabela

    # Índices das linhas selecionadas numa tabela (o iid de cada linha é o índice)
    def indices_selecionados(self, tabela):
        indices = []
        for iid in tabela.selection():
            indices.append(int(iid))
        return sorted(indices)

    def selecionar(self, tabela, indice):
        iid = str(indice)
        if tabela.exists(iid):
            tabela.selection_set(iid)
            tabela.see(iid)             # rola a tabela até a linha, se ela estiver escondida

    # Por que cabem só tantas arestas: "Com 5 vértices, sem laços e sem paralelas, cabem no máximo 20."
    def maximo_de_arestas(self):
        return entrada.maximo_de_arestas(len(self.vertices), self.lacos.get(), self.paralelas.get(),
                                         self.direcionado.get())

    def explicar_maximo_de_arestas(self):
        quantidade = len(self.vertices)
        maximo = self.maximo_de_arestas()
        if maximo == entrada.LIMITE_DE_ARESTAS:
            return f"Acima de {entrada.LIMITE_DE_ARESTAS} arestas o desenho fica ilegível."
        opcoes = "sem laços"
        if self.lacos.get():
            opcoes = "com laços"
        if self.paralelas.get():
            opcoes += " e com paralelas"
        else:
            opcoes += " e sem paralelas"
        return (f"Com {entrada.contar(quantidade, 'vértice', 'vértices')}, {opcoes}, num grafo "
                f"{self.nome_da_orientacao()}, cabem no máximo {maximo}.")

    # Clique duplo fora de uma linha (no título da coluna, por exemplo) não conta
    def clicou_fora_das_linhas(self, tabela, evento):
        return evento is not None and tabela.identify_region(evento.x, evento.y) != "cell"

    # Em qual coluna foi o clique ("peso", "h"...). O Treeview conta as colunas VISÍVEIS: "#1", "#2"...
    def coluna_clicada(self, tabela, evento):
        if evento is None:
            return None
        posicao = int(tabela.identify_column(evento.x)[1:]) - 1
        visiveis = tabela.cget("displaycolumns")
        if tuple(visiveis) == ("#all",):
            visiveis = tabela.cget("columns")
        if 0 <= posicao < len(visiveis):
            return visiveis[posicao]
        return None

    # ------------------------------------------------------------------
    # ① Vértices
    # ------------------------------------------------------------------

    def adicionar_vertice(self, evento=None):
        nome = self.novo_vertice.get().strip()
        problema = entrada.validar_nome_de_vertice(nome, self.vertices)
        if problema == "" and len(self.vertices) >= entrada.MAXIMO_DE_VERTICES:
            problema = f"O limite é de {entrada.MAXIMO_DE_VERTICES} vértices."
        if problema:
            self.avisar(problema, erro=True)
            self.etapas[0].campo_nome.marcar_erro(True)
            return "break"      # "break": o Enter para aqui e não chega a outros atalhos
        aviso = f"Vértice {nome} adicionado."
        if self.posicoes:
            aviso += " Ele não tem posição no desenho importado: o desenho volta a ser em círculo."
        self.mudar_grafo(self.vertices + [nome], self.arestas, aviso)
        self.selecionar(self.tabela_vertices(), len(self.vertices) - 1)
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))     # já sugere o próximo nome
        self.etapas[0].campo_nome.focar()
        return "break"

    # O contador "Quantidade": cria ou tira vértices na hora (os que saem são os do fim da lista)
    def mudar_quantidade_de_vertices(self, quantidade):
        quantidade = max(0, min(entrada.MAXIMO_DE_VERTICES, quantidade))
        if quantidade == len(self.vertices):
            return
        antes = list(self.vertices)
        novos, mapa = entrada.vertices_para_a_quantidade(self.vertices, quantidade, self.estilo.get())
        criados = []
        for nome in novos:
            if nome not in mapa.values():
                criados.append(nome)
        tirados = []
        for nome in antes:
            if nome not in mapa:
                tirados.append(nome)
        arestas_que_saem = len(self.arestas) - len(entrada.renomear_arestas(self.arestas, mapa))
        if criados:
            aviso = entrada.contar(len(criados), "vértice criado", "vértices criados") + f" ({criados[0]}"
            if len(criados) > 1:
                aviso += f" a {criados[-1]}"
            aviso += ")."
        else:
            aviso = entrada.contar(len(tirados), "vértice tirado", "vértices tirados") + \
                f" do fim da lista ({', '.join(tirados)})."
        renomeados = 0
        for antigo in mapa:
            if mapa[antigo] != antigo:
                renomeados += 1
        if renomeados and novos:
            aviso += f" Os nomes foram refeitos ({novos[0]} a {novos[-1]}) para a ordem alfabética continuar certa."
        if arestas_que_saem:
            aviso += " " + entrada.contar(arestas_que_saem, "aresta saiu junto", "arestas saíram junto") + "."
        if criados and self.posicoes:
            aviso += " Os novos não têm posição no desenho importado: o desenho volta a ser em círculo."
        self.aplicar_novos_nomes(novos, mapa, aviso + " Ctrl+Z desfaz.")

    # "A, B, C…" ou "1, 2, 3…": vértices na sequência de um estilo são renomeados para o outro;
    # com nomes próprios, o estilo vale só para os próximos vértices criados pela Quantidade
    def mudar_estilo(self):
        estilo = self.estilo.get()
        atual = entrada.estilo_dos_nomes(self.vertices)
        if atual is None:
            if self.vertices:
                exemplo = entrada.proximo_nome_do_estilo(self.vertices, estilo, len(self.vertices) + 1)
                self.avisar(f"Os vértices têm nomes próprios e continuam com eles: os próximos criados pela "
                            f"Quantidade vão se chamar {exemplo}, ...")
            return
        if atual == estilo:
            return
        novos, mapa = entrada.renomear_para_o_estilo(self.vertices, estilo)
        self.aplicar_novos_nomes(novos, mapa, f"Vértices renomeados: {novos[0]} a {novos[-1]}. Ctrl+Z desfaz.")

    def sortear_quantidade_de_vertices(self):
        quantidade = len(self.vertices)
        tentativas = 0
        while quantidade == len(self.vertices) and tentativas < 10:      # sorteia de novo se der a mesma
            quantidade = random.randint(MENOR_SORTEIO_DE_VERTICES, MAIOR_SORTEIO_DE_VERTICES)
            tentativas += 1
        self.mudar_quantidade_de_vertices(quantidade)

    # Duplo clique: na coluna h edita a heurística; nas outras, renomeia
    def duplo_clique_no_vertice(self, evento):
        if self.clicou_fora_das_linhas(self.tabela_vertices(), evento):
            return
        if self.coluna_clicada(self.tabela_vertices(), evento) == "h":
            self.editar_heuristica()
        else:
            self.renomear_vertice()

    def renomear_vertice(self, evento=None):
        indices = self.indices_selecionados(self.tabela_vertices())
        if len(indices) != 1:
            self.avisar("Escolha um vértice na tabela para renomear (um clique na linha).", erro=True)
            return
        indice = indices[0]
        antigo = self.vertices[indice]

        # Chamada pelo diálogo quando o usuário clica em OK: devolve "" se deu certo, ou o problema
        def aplicar(novo):
            if antigo not in self.vertices:
                return f"O vértice {antigo} não existe mais."
            if novo == antigo:
                return ""
            outros = []
            for vertice in self.vertices:
                if vertice != antigo:
                    outros.append(vertice)
            problema = entrada.validar_nome_de_vertice(novo, outros)
            if problema:
                return problema
            mapa = {}
            for vertice in self.vertices:
                mapa[vertice] = novo if vertice == antigo else vertice
            novos = []
            for vertice in self.vertices:
                novos.append(mapa[vertice])
            self.aplicar_novos_nomes(novos, mapa, f"Vértice {antigo} renomeado para {novo}.")
            self.selecionar(self.tabela_vertices(), indice)
            return ""

        DialogoDeTexto(self.app, "Renomear vértice", f"Novo nome para o vértice {antigo}:", antigo, aplicar)

    # A heurística h de um vértice: duplo clique na coluna h
    def editar_heuristica(self):
        indices = self.indices_selecionados(self.tabela_vertices())
        if len(indices) != 1:
            return
        vertice = self.vertices[indices[0]]
        atual = entrada.formatar_numero(self.heuristica.get(vertice))

        def aplicar(texto):
            if vertice not in self.vertices:
                return f"O vértice {vertice} não existe mais."
            numero, problema = entrada.ler_numero(texto)
            if problema:
                return problema
            if numero is not None and numero < 0:
                return "A heurística não pode ser negativa: ela estima quanto falta até o destino."
            heuristica = entrada.trocar_heuristicas(self.heuristica, [vertice], [numero])
            if heuristica == self.heuristica:
                return ""
            aviso = f"h({vertice}) = {entrada.formatar_numero(numero)}."
            if numero is None:
                aviso = f"{vertice} ficou sem heurística."
            self.mudar_grafo(self.vertices, self.arestas, aviso, heuristica=heuristica)
            self.selecionar(self.tabela_vertices(), indices[0])
            return ""

        DialogoDeTexto(self.app, "Heurística", f"h({vertice}): a estimativa de quanto falta até o destino "
                                               f"(vazio = sem h):", atual, aplicar)

    def remover_vertices(self, evento=None):
        indices = self.indices_selecionados(self.tabela_vertices())
        if not indices:
            self.avisar("Escolha um ou mais vértices na tabela para remover (Ctrl+clique escolhe vários).",
                        erro=True)
            return "break"
        removidos = []
        for indice in indices:
            removidos.append(self.vertices[indice])
        vertices = self.vertices
        arestas = self.arestas
        for nome in removidos:
            vertices, arestas = entrada.remover_vertice(vertices, arestas, nome)
        aviso = "Removido: " + ", ".join(removidos)
        arestas_removidas = len(self.arestas) - len(arestas)
        if arestas_removidas > 0:
            aviso += " (e " + entrada.contar(arestas_removidas, "aresta ligada a ele", "arestas ligadas a eles") + ")"
        self.mudar_grafo(vertices, arestas, aviso + ". Ctrl+Z desfaz.")
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))
        return "break"

    # ------------------------------------------------------------------
    # ② Arestas
    # ------------------------------------------------------------------

    # O que uma aresta nova tem de especial: " (é um laço, paralela a outra aresta igual)" ou ""
    def detalhes_da_aresta(self, origem, destino, ignorar=None):
        detalhes = []
        if origem == destino:
            detalhes.append("é um laço")
        for indice in range(len(self.arestas)):
            if indice == ignorar:
                continue
            origem_existente, destino_existente, nome, peso = self.arestas[indice]
            if entrada.chave_do_par(origem_existente, destino_existente, self.direcionado.get()) == \
                    entrada.chave_do_par(origem, destino, self.direcionado.get()):
                detalhes.append("paralela a outra aresta igual")
                break           # uma igual já basta para ser paralela
        if detalhes:
            return " (" + ", ".join(detalhes) + ")"
        return ""

    def adicionar_aresta(self, evento=None):
        origem = self.nova_origem.get()
        destino = self.novo_destino.get()
        nome = self.novo_nome_da_aresta.get().strip()
        etapa = self.etapas[1]
        if origem not in self.vertices or destino not in self.vertices:
            self.avisar("Escolha de onde a aresta sai e para onde vai (crie os vértices antes).", erro=True)
            return "break"
        problema = entrada.validar_nome_de_aresta(nome)
        if problema:
            etapa.campo_nome.marcar_erro(True)
        peso = None
        if problema == "":
            peso, problema = entrada.ler_numero(self.novo_peso.get())
            if problema:
                problema = "Peso: " + problema
                etapa.campo_peso.marcar_erro(True)
        if problema == "" and len(self.arestas) >= entrada.LIMITE_DE_ARESTAS:
            problema = f"O limite é de {entrada.LIMITE_DE_ARESTAS} arestas."
        if problema:
            self.avisar(problema, erro=True)
            return "break"
        detalhe = self.detalhes_da_aresta(origem, destino)
        texto = f"{origem} -> {destino}"
        if nome:
            texto = f"{nome} ({origem} -> {destino})"
        if peso is not None:
            texto += f" com peso {entrada.formatar_numero(peso)}"
        self.mudar_grafo(self.vertices, self.arestas + [(origem, destino, nome, peso)],
                         f"Aresta {texto} adicionada{detalhe}.")
        self.selecionar(self.tabela_arestas(), len(self.arestas) - 1)
        self.novo_nome_da_aresta.set("")
        return "break"

    # Duplo clique numa aresta: abre a edição, com o cursor no campo da coluna clicada
    def duplo_clique_na_aresta(self, evento):
        if self.clicou_fora_das_linhas(self.tabela_arestas(), evento):
            return
        coluna = self.coluna_clicada(self.tabela_arestas(), evento)
        foco = "origem"
        if coluna in ("nome", "peso"):
            foco = coluna
        self.editar_aresta(foco)

    # Editar uma aresta inteira: de onde sai, para onde vai, o nome, o peso e a posição (o Nº)
    def editar_aresta(self, foco="nome"):
        indices = self.indices_selecionados(self.tabela_arestas())
        if len(indices) != 1:
            self.avisar("Escolha uma aresta na tabela para editar (um clique na linha).", erro=True)
            return
        indice = indices[0]
        antiga = self.arestas[indice]

        def aplicar(origem, destino, nome, texto_do_peso, posicao):
            if indice >= len(self.arestas) or self.arestas[indice] != antiga:
                return "Essa aresta mudou enquanto a janela estava aberta. Feche e tente de novo."
            if origem not in self.vertices or destino not in self.vertices:
                return "Escolha de onde a aresta sai e para onde vai."
            problema = entrada.validar_nome_de_aresta(nome)
            if problema:
                return problema
            peso, problema = entrada.ler_numero(texto_do_peso)
            if problema:
                return "Peso: " + problema
            nova = (origem, destino, nome, peso)
            nova_posicao = max(1, min(len(self.arestas), posicao)) - 1         # o índice na lista (0 = a primeira)
            if nova == antiga and nova_posicao == indice:
                return ""
            arestas = list(self.arestas)
            del arestas[indice]
            arestas.insert(nova_posicao, nova)
            texto = f"{origem} -> {destino}"
            if nome:
                texto += f", nome {nome}"
            if peso is not None:
                texto += f", peso {entrada.formatar_numero(peso)}"
            if nova_posicao != indice:
                texto += f", agora na posição {nova_posicao + 1}"
            detalhe = self.detalhes_da_aresta(origem, destino, ignorar=indice)
            self.mudar_grafo(self.vertices, arestas, f"Aresta {indice + 1}: {texto}{detalhe}. Ctrl+Z desfaz.")
            self.selecionar(self.tabela_arestas(), nova_posicao)
            return ""

        DialogoDeAresta(self.app, f"Editar a aresta {indice + 1}", self.vertices, antiga, self.direcionado.get(),
                        aplicar, foco, posicao=indice + 1, total=len(self.arestas))

    def remover_arestas(self, evento=None):
        indices = self.indices_selecionados(self.tabela_arestas())
        if not indices:
            self.avisar("Escolha uma ou mais arestas na tabela para remover (Ctrl+clique escolhe várias).",
                        erro=True)
            return "break"
        arestas = []
        for i in range(len(self.arestas)):
            if i not in indices:
                arestas.append(self.arestas[i])
        quantidade = entrada.contar(len(indices), "aresta removida", "arestas removidas")
        self.mudar_grafo(self.vertices, arestas, f"{quantidade}. Ctrl+Z desfaz.")
        return "break"

    def editar_arestas_em_texto(self):
        # Chamada pelo diálogo ao clicar em Aplicar: devolve "" se deu certo, ou o problema
        def aplicar(texto, criar_vertices):
            arestas, problemas, novos = entrada.ler_arestas(texto, self.vertices, criar_vertices)
            if problemas:
                resposta = "Não consegui ler:\n" + "\n".join(problemas[:6])
                if len(problemas) > 6:
                    resposta += f"\n... e mais {len(problemas) - 6}"
                return resposta
            if len(arestas) > entrada.LIMITE_DE_ARESTAS:
                return f"São {len(arestas)} arestas; o limite é {entrada.LIMITE_DE_ARESTAS}."
            aviso = "Arestas atualizadas pelo texto: " + entrada.contar(len(arestas), "aresta", "arestas")
            if novos:
                aviso += " e " + entrada.contar(len(novos), "vértice novo", "vértices novos") + f" ({', '.join(novos)})"
            self.mudar_grafo(self.vertices + novos, arestas, aviso + ". Ctrl+Z desfaz.")
            return ""

        DialogoDeArestas(self.app, entrada.texto_das_arestas(self.arestas, self.direcionado.get()), aplicar)

    # O diálogo Pesos…: onde aplicar (arestas ou vértices), em quais e com que valores.
    # lugar: "arestas" ou "vertices" (None = o editor escolhe pelo que está faltando)
    def abrir_pesos(self, lugar=None):
        indices = self.indices_selecionados(self.tabela_arestas())
        selecionados = []
        for indice in self.indices_selecionados(self.tabela_vertices()):
            selecionados.append(self.vertices[indice])
        sem_h = 0
        for vertice in self.vertices:
            if vertice not in self.heuristica:
                sem_h += 1
        if lugar is None:
            lugar = "arestas"
            if self.busca_escolhida()["usa_heuristica"] and sem_h > 0 and not entrada.indices_sem_peso(self.arestas):
                lugar = "vertices"
        contexto = {
            "arestas": len(self.arestas),
            "arestas_selecionadas": len(indices),
            "arestas_sem_peso": len(entrada.indices_sem_peso(self.arestas)),
            "vertices": len(self.vertices),
            "vertices_selecionados": len(selecionados),
            "vertices_sem_h": sem_h,
            "custo_real": pesos.motivo_sem_custo_real(self.vertices, self.arestas, self.destino_escolhido(),
                                                      self.direcionado.get()),
            "destino": self.destino_escolhido(),
            "lugar": lugar,
        }

        def aplicar(escolha):
            arestas, heuristica, aviso, problema = pesos.aplicar_escolha(
                escolha, self.vertices, self.arestas, self.heuristica, self.direcionado.get(),
                self.destino_escolhido(), indices, selecionados)
            if problema:
                return problema
            self.mudar_grafo(self.vertices, arestas, aviso, heuristica=heuristica)
            return ""

        DialogoDePesos(self.app, contexto, aplicar)

    def sortear_arestas(self):
        if not self.vertices:
            self.avisar("Crie os vértices antes de sortear as arestas.", erro=True)
            return
        lacos = self.lacos.get()
        paralelas = self.paralelas.get()
        quantidade = self.ler_numero(self.quantidade_arestas, "Quantidade de arestas", 0, self.maximo_de_arestas(),
                                     self.explicar_maximo_de_arestas())
        if quantidade is None:
            return
        arestas = entrada.arestas_aleatorias(self.vertices, quantidade, lacos, paralelas,
                                             direcionado=self.direcionado.get())
        aviso = entrada.contar(quantidade, "aresta sorteada", "arestas sorteadas") + " no lugar das de antes"
        if self.busca_escolhida()["usa_pesos"] == "sim":
            aviso += " (sem peso: o botão Pesos… dá pesos a elas)"
        self.mudar_grafo(self.vertices, arestas, aviso + ". Ctrl+Z desfaz.")

    # ------------------------------------------------------------------
    # ③ Busca
    # ------------------------------------------------------------------

    # A busca escolhida na tela inicial ("Montar meu grafo")
    def escolher_busca(self, chave):
        self.busca.set(algoritmos.algoritmo(chave)["chave"])
        self.atualizar()

    # ------------------------------------------------------------------
    # Modelos
    # ------------------------------------------------------------------

    # A lista que abre no botão do modelo: os modelos salvos (o aberto com ✓, o padrão com ★),
    # "Salvar com outro nome…" e "Grafo novo, vazio"
    def montar_menu_dos_modelos(self):
        menu = self.menu_dos_modelos
        menu.delete(0, "end")
        try:
            nomes = modelos.listar_modelos()
        except OSError as problema:
            self.avisar(f"Não consegui ler a pasta de modelos: {problema}", erro=True)
            nomes = []
        padrao = self.nome_do_padrao()
        menu.add_command(label="Abrir um modelo:", state="disabled")
        for nome in nomes:
            rotulo = nome
            if modelos.mesmo_nome(nome, padrao):
                rotulo += "   ★ padrão"
            marca = "✓  " if modelos.mesmo_nome(nome, self.modelo_aberto) else "     "
            menu.add_command(label=marca + rotulo, command=lambda nome=nome: self.carregar_modelo(nome))
        menu.add_separator()
        menu.add_command(label="Salvar com outro nome…", command=self.salvar_como)
        menu.add_command(label="Grafo novo, vazio", command=self.grafo_vazio)

    # Coloca na tela um grafo com as opções (de um modelo ou de uma importação), guardando o estado
    # anterior para o Desfazer. "referencia_igual" = o grafo é igual ao arquivo (não está alterado).
    def abrir_grafo(self, grafo, nome, modelo_aberto, aviso, referencia_igual):
        self.guardar_para_desfazer()
        self.atualizando = True
        self.vertices = list(grafo["vertices"])
        self.arestas = list(grafo["arestas"])
        self.heuristica = dict(grafo["heuristica"])
        self.posicoes = dict(grafo["posicoes"])
        self.ordenar.set(grafo["ordenar"])
        self.direcionado.set(grafo["direcionado"])
        self.inicio.set(grafo["inicio"] or "")
        self.busca.set(algoritmos.algoritmo(grafo["algoritmo"])["chave"])
        self.destino.set(grafo["destino"] or SEM_DESTINO)
        self.arrumacao.set(grafo["arrumacao"])
        if grafo.get("limite") is not None:
            self.limite.set(str(grafo["limite"]))
        self.nome_do_modelo.set(nome)
        self.modelo_aberto = modelo_aberto
        self.atualizar()
        self.referencia = None
        if referencia_igual:
            self.referencia = self.estado_do_grafo()        # acabou de abrir: igual ao arquivo
        self.atualizar_modelo()
        self.avisar(aviso)
        self.novo_vertice.set(entrada.proximo_nome_livre(self.vertices))

    def carregar_modelo(self, nome):
        try:
            grafo = modelos.carregar_modelo(nome)
        except (OSError, ValueError) as problema:
            self.avisar(str(problema), erro=True)
            return
        resumo = entrada.resumo(grafo["vertices"], grafo["arestas"], grafo["direcionado"])
        self.abrir_grafo(grafo, nome, nome, f"Modelo \"{nome}\" carregado: {resumo}. Ctrl+Z desfaz.", True)

    # Um grafo vazio, com a mesma busca (o grafo de antes fica no Ctrl+Z)
    def grafo_vazio(self):
        grafo = modelos.novo_grafo([], [], self.ordenar.get(), None, self.direcionado.get(), self.busca.get())
        self.abrir_grafo(grafo, "Meu grafo", "", "Grafo novo, vazio: comece pelos vértices. Ctrl+Z volta para o "
                                                 "grafo de antes.", False)
        self.mostrar_etapa(0)

    # Salvar: no próprio arquivo, se o modelo já foi salvo antes; senão, pede um nome
    def salvar_modelo(self, evento=None):
        if not self.vertices:
            self.avisar("O grafo precisa ter pelo menos um vértice para ser salvo.", erro=True)
            return "break"
        nome = self.nome_do_modelo.get().strip()
        protegido = modelos.mesmo_nome(nome, modelos.NOME_DO_MODELO_DA_PROVA)
        if self.modelo_salvo() and modelos.mesmo_nome(self.modelo_aberto, nome) and not protegido:
            self.gravar_modelo(nome)
        elif protegido and modelos.mesmo_nome(self.modelo_aberto, nome) and not self.esta_alterado():
            self.avisar(f"Nada para salvar: \"{nome}\" está igual ao arquivo.")
        else:
            self.salvar_como()
        return "break"

    # Pede o nome e salva com ele (se já existir outro modelo com esse nome, pergunta antes de substituir)
    def salvar_como(self):
        if not self.vertices:
            self.avisar("O grafo precisa ter pelo menos um vértice para ser salvo.", erro=True)
            return
        sugestao = self.nome_do_modelo.get().strip()
        if modelos.mesmo_nome(sugestao, modelos.NOME_DO_MODELO_DA_PROVA):
            sugestao = "Meu grafo"

        def aplicar(nome):
            problema = modelos.validar_nome_de_modelo(nome)
            if problema:
                return problema
            if modelos.mesmo_nome(nome, modelos.NOME_DO_MODELO_DA_PROVA):
                return (f"\"{modelos.NOME_DO_MODELO_DA_PROVA}\" guarda o grafo da prova e não pode ser substituído: "
                        f"escolha outro nome.")
            if modelos.existe_modelo(nome) and not modelos.mesmo_nome(nome, self.modelo_aberto):
                # Pergunta depois que esta janela fechar (só uma janela de diálogo fica aberta por vez)
                self.app.raiz.after_idle(lambda: self.confirmar_substituicao(nome))
                return ""
            return self.gravar_modelo(nome)

        DialogoDeTexto(self.app, "Salvar modelo", "Nome do modelo (é o nome do arquivo):", sugestao, aplicar)

    def confirmar_substituicao(self, nome):
        DialogoDeConfirmacao(self.app, "Substituir modelo",
                             f"Já existe um modelo chamado \"{nome}\". Substituir pelo grafo atual?", "Substituir",
                             lambda: self.gravar_modelo(nome))

    # Grava o arquivo de verdade; devolve "" se deu certo (os diálogos usam isso)
    def gravar_modelo(self, nome):
        try:
            modelos.salvar_modelo(nome, self.grafo_atual())
        except (OSError, ValueError) as problema:
            self.avisar(f"Não consegui salvar: {problema}", erro=True)
            return f"Não consegui salvar: {problema}"
        self.nome_do_modelo.set(nome)
        self.modelo_aberto = nome
        self.referencia = self.estado_do_grafo()        # acabou de salvar: igual ao arquivo
        self.atualizar_modelo()
        self.avisar(f"Modelo \"{nome}\" salvo em {modelos.caminho_do_modelo(nome)}")
        return ""

    def tornar_padrao(self):
        if not self.modelo_salvo():
            self.avisar("Salve o modelo antes de torná-lo padrão.", erro=True)
            return
        nome = self.modelo_aberto
        try:
            modelos.definir_padrao(nome)
        except (OSError, ValueError) as problema:
            self.avisar(str(problema), erro=True)
            return
        aviso = f"\"{nome}\" agora é o modelo padrão: é ele que abre quando o BoscoGraph começa."
        if self.esta_alterado():
            aviso += " As mudanças ainda não salvas não entram no padrão: clique em Salvar."
        self.atualizar_modelo()
        self.avisar(aviso)

    # ------------------------------------------------------------------
    # Importar um grafo desenhado em outro programa
    # ------------------------------------------------------------------

    # Vai para a tela de importação (em etapas). Ao fechar o editor, o grafo de agora fica guardado:
    # se a pessoa escolher "Editar grafo" lá, o Ctrl+Z no editor volta para ele.
    def importar(self, evento=None):
        self.app.mostrar_importacao()
        return "break"

    # ------------------------------------------------------------------
    # Visualizar e trocar de tela
    # ------------------------------------------------------------------

    # Nome do grafo para a visualização: "Prova 01", "Prova 01 (alterado)" ou "Grafo sem nome"
    def titulo_do_grafo(self):
        titulo = self.titulo_do_modelo()
        if self.esta_alterado():
            titulo += " (alterado)"
        return titulo

    # mesmo_com_problemas: a importação abre a visualização mesmo se a busca ainda não pode rodar
    # (a visualização explica o problema e leva à parte que resolve)
    def visualizar(self, evento=None, mesmo_com_problemas=False):
        self.confirmar_contadores()
        problemas, avisos = self.conferir_busca()
        if problemas and not mesmo_com_problemas:
            self.avisar(problemas[0], erro=True)
            if self.etapa != len(self.etapas) - 1:
                self.mostrar_etapa(len(self.etapas) - 1)        # a etapa Busca mostra o que falta
            return "break"
        self.app.visualizar(configuracao_da_visualizacao(self.grafo_atual(), self.titulo_do_grafo(),
                                                         self.valores_atuais()))
        return "break"

    # Tudo o que a tela precisa para ser recriada igual (ao voltar da visualização ou trocar o tema)
    def valores_atuais(self):
        return {
            "modelo": self.nome_do_modelo.get(),
            "modelo_aberto": self.modelo_aberto,
            "grafo": self.grafo_atual(),
            "referencia": self.referencia,
            "historico": list(self.historico),
            "etapa": self.etapa,
            "estilo": self.estilo.get(),
            "quantidade_arestas": self.quantidade_arestas.get(),
            "lacos": self.lacos.get(),
            "paralelas": self.paralelas.get(),
            "aviso": self.aviso,
            "aviso_de_erro": self.aviso_de_erro,
        }

    # Recria a tela com o tema novo, mantendo tudo o que já foi feito
    def reconstruir(self):
        self.app.mostrar_editor(self.valores_atuais())

    # Com o zoom, as fontes mudam sozinhas; o logo e os componentes desenhados precisam ser medidos de novo
    def redesenhar(self):
        redesenhar_componentes(self.quadro)
        for etapa in self.etapas:
            etapa.redesenhar()

    def destruir(self):
        self.parar_deslize()
        if self.app.dialogo is not None:
            self.app.dialogo.fechar()
        for tecla in self.teclas:
            self.app.raiz.unbind(tecla)
        self.quadro.destroy()
