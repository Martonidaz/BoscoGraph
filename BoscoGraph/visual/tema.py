# Cores dos temas claro e escuro, e o estilo dos componentes (ttk) de cada tema.
#
# As cores de base vêm da paleta da universidade (a do logo dela):
#   #03296a azul-marinho     -> o botão principal, a seleção e o fundo do logo (no tema claro)
#   #053e75 azul-marinho 2   -> o "ativo" do tema claro
#   #6880a1 azul-acinzentado -> os textos suaves (escurecido, para ler bem) e as arestas do grafo
#   #d7dce4 cinza-azulado    -> as bordas e, clareado, o fundo da janela
#   #fd2016 vermelho         -> o destaque (o que acabou de mudar) e o contorno dos vértices do logo
#   #fd4943 vermelho médio   -> o erro, no tema escuro
#   #fe7874 salmão           -> o botão principal e a seleção, no tema escuro (o azul-marinho sumiria no fundo)
#   #febbb9 rosa-claro       -> o "ativo" do tema escuro
# Os textos e fundos escuros são esses azuis misturados com preto ou branco (a função misturar, no fim).
#
# O que NÃO muda, porque ajuda a entender o que está na tela: as cores do algoritmo nos vértices
# (Branco, Cinza, Preto), as cores das arestas (árvore, retorno, avanço, cruzamento, examinada), a cor de
# cada parte, os dois lados da bidirecional, os conjuntos do Kruskal, o amarelo da linha em destaque, o
# verde de "certo" e, no tema claro, o vermelho de "erro" (mais escuro que os da paleta, para ler bem).

from tkinter import ttk

CLARO = {
    "nome": "claro",
    "fundo": "#ebeef2",
    "superficie": "#ffffff",
    "texto": "#11294e",
    "texto_suave": "#4a6690",
    "borda": "#d7dce4",
    "acento": "#03296a",            # botão principal e etapa atual
    "acento_ativo": "#053e75",
    "texto_acento": "#ffffff",
    "destaque": "#fd2016",          # laranja: o que acabou de mudar
    "fundo_destaque": "#ffefb3",    # amarelo: linha em destaque nos painéis
    "fundo_anterior": "#e2f1e4",    # verde-claro: a linha de código que acabou de rodar
    "erro": "#c62828",
    "sucesso": "#2e7d32",
    "canvas": "#f3f5f7",
    "vertice_branco": "#ffffff",
    "vertice_cinza": "#9e9e9e",
    "vertice_preto": "#1b1b1b",
    "texto_vertice_branco": "#1b1b1b",
    "texto_vertice_cinza": "#1b1b1b",
    "texto_vertice_preto": "#ffffff",
    "contorno_vertice": "#11294e",
    "contorno_sem_cor": "#6880a1",
    "texto_sem_cor": "#4a6690",
    "rotulo": "#11294e",
    "aresta_objeto": "#a4b3c7",
    "aresta_grafo": "#6880a1",
    "aresta_arvore": "#1565c0",
    "aresta_retorno": "#c62828",
    "aresta_avanco": "#2e7d32",
    "aresta_cruzamento": "#7b1fa2",
    "aresta_examinada": "#9c8ac4",  # lilás claro: a busca olhou, mas a aresta não está no caminho
    "codigo_fundo": "#fbfcfd",
    "codigo_texto": "#11294e",
    "codigo_numero": "#a0aab5",
    "codigo_comentario": "#7b8794",
    "codigo_string": "#2e7d32",
    "codigo_palavra": "#1565c0",
    "pilha_caixa": "#9e9e9e",
    "pilha_texto": "#1b1b1b",
    # Busca bidirecional: o lado da frente (azul) e o de trás (verde-azulado)
    "lado_frente": "#bbdefb",
    "lado_frente_preto": "#1565c0",
    "lado_tras": "#b2dfdb",
    "lado_tras_preto": "#00796b",
    "texto_lado_preto": "#ffffff",
    "aresta_arvore_tras": "#00897b",
    "cortado": "#c62828",           # o anel do vértice cortado pelo limite
    # Árvore geradora mínima: a ligação provisória do Prim (tracejada) e as cores dos conjuntos do Kruskal
    # (cada conjunto com 2 ou mais vértices ganha uma; o texto do vértice fica escuro em todas)
    "aresta_candidata": "#1565c0",
    "texto_conjunto": "#1b1b1b",
    # A cor de cada parte da tela (a trilha da esquerda, o título e o destaque do que foi escolhido)
    "parte_vertices": "#1565c0",
    "parte_arestas": "#00897b",
    "parte_pesos": "#e65100",
    "parte_lista": "#6a1b9a",
    "parte_adjacencia": "#c2185b",
    "parte_incidencia": "#2e7d32",
    "parte_tipo": "#455a64",
    "parte_passo": "#d84315",
    "parte_linha": "#283593",
    "parte_comparar": "#00838f",
    "parte_resultado": "#9a6b00",
}

ESCURO = {
    "nome": "escuro",
    "fundo": "#112233",
    "superficie": "#182a3e",
    "texto": "#e3e6ec",
    "texto_suave": "#9dacc2",
    "borda": "#2c4057",
    "acento": "#fe7874",
    "acento_ativo": "#febbb9",
    "texto_acento": "#03296a",
    "destaque": "#ffab40",
    "fundo_destaque": "#4b3d17",
    "fundo_anterior": "#1f3326",
    "erro": "#fd4943",
    "sucesso": "#5ccf7a",
    "canvas": "#152638",
    "vertice_branco": "#ffffff",
    "vertice_cinza": "#9e9e9e",
    "vertice_preto": "#000000",
    "texto_vertice_branco": "#111111",
    "texto_vertice_cinza": "#111111",
    "texto_vertice_preto": "#ffffff",
    "contorno_vertice": "#d7dce4",  # contorno claro: o vértice Preto não some no fundo escuro
    "contorno_sem_cor": "#6880a1",
    "texto_sem_cor": "#9dacc2",
    "rotulo": "#e3e6ec",
    "aresta_objeto": "#384c64",
    "aresta_grafo": "#8699b4",
    "aresta_arvore": "#64a8ff",
    "aresta_retorno": "#ff6b6b",
    "aresta_avanco": "#5ccf7a",
    "aresta_cruzamento": "#c792ea",
    "aresta_examinada": "#8a7bb0",
    "codigo_fundo": "#172535",
    "codigo_texto": "#d7dce4",
    "codigo_numero": "#5c6773",
    "codigo_comentario": "#7f8c98",
    "codigo_string": "#a5d6a7",
    "codigo_palavra": "#82aaff",
    "pilha_caixa": "#9e9e9e",
    "pilha_texto": "#111111",
    "lado_frente": "#90caf9",
    "lado_frente_preto": "#64a8ff",
    "lado_tras": "#80cbc4",
    "lado_tras_preto": "#26a69a",
    "texto_lado_preto": "#0b0d10",
    "aresta_arvore_tras": "#4db6ac",
    "cortado": "#ff6b6b",
    "aresta_candidata": "#64a8ff",
    "texto_conjunto": "#111111",
    "parte_vertices": "#64a8ff",
    "parte_arestas": "#4db6ac",
    "parte_pesos": "#ffa040",
    "parte_lista": "#ce93d8",
    "parte_adjacencia": "#f48fb1",
    "parte_incidencia": "#81c784",
    "parte_tipo": "#b0bec5",
    "parte_passo": "#ff8a65",
    "parte_linha": "#9fa8da",
    "parte_comparar": "#80deea",
    "parte_resultado": "#ffd54f",
}

# As cores dos conjuntos do Kruskal (as mesmas nos dois temas): "conjunto_0", "conjunto_1"...
PALETA_DOS_CONJUNTOS = ["#ffcc80", "#a5d6a7", "#90caf9", "#ce93d8", "#fff59d", "#80cbc4", "#f48fb1", "#bcaaa4"]
CORES_DOS_CONJUNTOS = len(PALETA_DOS_CONJUNTOS)
for numero in range(CORES_DOS_CONJUNTOS):
    CLARO[f"conjunto_{numero}"] = ESCURO[f"conjunto_{numero}"] = PALETA_DOS_CONJUNTOS[numero]


# Mistura duas cores ("#rrggbb"): fracao 0 = só a primeira, 1 = só a segunda.
# Serve para o fundo clarinho da parte escolhida (a cor da parte misturada com a cor do cartão).
def misturar(cor_1, cor_2, fracao):
    resultado = "#"
    for posicao in (1, 3, 5):
        a = int(cor_1[posicao:posicao + 2], 16)
        b = int(cor_2[posicao:posicao + 2], 16)
        resultado += f"{round(a + (b - a) * fracao):02x}"
    return resultado


# Aplica as cores do tema em todos os componentes ttk da janela
def aplicar_estilo(raiz, tema, fontes):
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")        # o "clam" é o tema do ttk que aceita trocar as cores
    raiz.configure(bg=tema["fundo"])

    altura_linha = fontes["codigo"].metrics("linespace") + 8

    estilo.configure(".", background=tema["fundo"], foreground=tema["texto"],
                     fieldbackground=tema["superficie"], bordercolor=tema["borda"],
                     lightcolor=tema["fundo"], darkcolor=tema["fundo"],
                     troughcolor=tema["borda"], selectbackground=tema["acento"],
                     selectforeground=tema["texto_acento"], font=fontes["texto"])
    estilo.configure("TFrame", background=tema["fundo"])
    estilo.configure("Cartao.TFrame", background=tema["superficie"])
    # Painel = cartão com borda fina (as colunas do editor)
    estilo.configure("Painel.TFrame", background=tema["superficie"], bordercolor=tema["borda"],
                     lightcolor=tema["superficie"], darkcolor=tema["superficie"], relief="solid", borderwidth=1)
    estilo.configure("TituloDoPainel.TLabel", background=tema["superficie"], foreground=tema["texto"],
                     font=fontes["negrito"])
    estilo.configure("TLabel", background=tema["fundo"], foreground=tema["texto"])
    estilo.configure("Cartao.TLabel", background=tema["superficie"])
    estilo.configure("Suave.TLabel", foreground=tema["texto_suave"])
    estilo.configure("CartaoSuave.TLabel", background=tema["superficie"], foreground=tema["texto_suave"])
    estilo.configure("Titulo.TLabel", background=tema["superficie"], font=fontes["titulo"])
    estilo.configure("Erro.TLabel", background=tema["superficie"], foreground=tema["erro"])
    estilo.configure("Sucesso.TLabel", background=tema["superficie"], foreground=tema["sucesso"])
    # Rótulos que ficam direto no fundo da janela (fora dos cartões)
    estilo.configure("Marca.TLabel", font=fontes["titulo"])
    estilo.configure("Negrito.TLabel", font=fontes["negrito"])
    estilo.configure("Alterado.TLabel", foreground=tema["destaque"], font=fontes["negrito"])
    estilo.configure("ErroFundo.TLabel", foreground=tema["erro"])
    estilo.configure("TSeparator", background=tema["borda"])
    estilo.configure("Mensagem.TLabel", font=fontes["mensagem"], foreground=tema["destaque"])
    estilo.configure("Explicacao.TLabel", font=fontes["explicacao"], foreground=tema["texto_suave"])
    estilo.configure("Relogio.TLabel", font=fontes["relogio"], foreground=tema["acento"])
    estilo.configure("RelogioVazio.TLabel", font=fontes["relogio"], foreground=tema["borda"])

    estilo.configure("TLabelframe", background=tema["fundo"], bordercolor=tema["borda"])
    estilo.configure("TLabelframe.Label", background=tema["fundo"], foreground=tema["texto_suave"],
                     font=fontes["negrito"])
    estilo.configure("Cartao.TLabelframe", background=tema["superficie"])
    estilo.configure("Cartao.TLabelframe.Label", background=tema["superficie"])

    # width=-6: largura mínima de 6 letras (o padrão do "clam" é 11, largo demais para telas pequenas)
    estilo.configure("TButton", background=tema["superficie"], foreground=tema["texto"],
                     bordercolor=tema["borda"], padding=(8, 4), width=-6)
    estilo.map("TButton",
               background=[("disabled", tema["fundo"]), ("pressed", tema["borda"]), ("active", tema["borda"])],
               foreground=[("disabled", tema["texto_suave"])])
    # Botão com menu (o "Nomes" do editor): a mesma cara dos outros botões, com a setinha da cor do texto
    estilo.configure("TMenubutton", background=tema["superficie"], foreground=tema["texto"],
                     bordercolor=tema["borda"], arrowcolor=tema["texto"], padding=(8, 4))
    estilo.map("TMenubutton", background=[("pressed", tema["borda"]), ("active", tema["borda"])])
    estilo.configure("Acento.TButton", background=tema["acento"], foreground=tema["texto_acento"],
                     font=fontes["negrito"], padding=(14, 6))
    estilo.map("Acento.TButton", background=[("pressed", tema["acento_ativo"]), ("active", tema["acento_ativo"])])
    estilo.configure("Etapa.TButton", padding=(8, 3))
    estilo.configure("EtapaAtual.TButton", background=tema["acento"], foreground=tema["texto_acento"],
                     font=fontes["negrito"], padding=(8, 3))
    estilo.map("EtapaAtual.TButton", background=[("active", tema["acento_ativo"])])

    for nome in ("TCheckbutton", "TRadiobutton"):
        estilo.configure(nome, background=tema["superficie"], foreground=tema["texto"],
                         indicatorbackground=tema["superficie"], indicatorforeground=tema["acento"])
        estilo.map(nome, background=[("active", tema["superficie"])],
                   indicatorbackground=[("pressed", tema["borda"]), ("selected", tema["superficie"])],
                   foreground=[("disabled", tema["texto_suave"])])
    # Caixa de marcar que fica direto no fundo (barra de controles da visualização)
    estilo.configure("Barra.TCheckbutton", background=tema["fundo"])
    estilo.map("Barra.TCheckbutton", background=[("active", tema["fundo"])])

    # Botões lado a lado (velocidade, orientação): funcionam como opções (só um fica marcado),
    # com cara de botão.
    # "Toolbutton" é o estilo do ttk que desenha um Radiobutton como botão.
    estilo.configure("Segmento.Toolbutton", background=tema["superficie"], foreground=tema["texto"],
                     bordercolor=tema["borda"], lightcolor=tema["superficie"], darkcolor=tema["superficie"],
                     relief="solid", borderwidth=1, padding=(8, 3), anchor="center", font=fontes["texto"])
    estilo.map("Segmento.Toolbutton",
               background=[("selected", tema["acento"]), ("active", tema["borda"])],
               foreground=[("selected", tema["texto_acento"])],
               lightcolor=[("selected", tema["acento"])],
               darkcolor=[("selected", tema["acento"])],
               relief=[("selected", "solid"), ("pressed", "solid")])
    estilo.configure("TEntry", fieldbackground=tema["superficie"], foreground=tema["texto"],
                     insertcolor=tema["texto"])
    estilo.configure("TSpinbox", fieldbackground=tema["superficie"], foreground=tema["texto"],
                     arrowcolor=tema["texto"], insertcolor=tema["texto"])
    estilo.configure("TCombobox", fieldbackground=tema["superficie"], foreground=tema["texto"],
                     arrowcolor=tema["texto"])
    estilo.map("TCombobox", fieldbackground=[("readonly", tema["superficie"])],
               foreground=[("readonly", tema["texto"])])
    raiz.option_add("*TCombobox*Listbox.background", tema["superficie"])
    raiz.option_add("*TCombobox*Listbox.foreground", tema["texto"])

    estilo.configure("Treeview", background=tema["superficie"], fieldbackground=tema["superficie"],
                     foreground=tema["texto"], rowheight=altura_linha, font=fontes["codigo"])
    estilo.configure("Treeview.Heading", background=tema["fundo"], foreground=tema["texto_suave"],
                     font=fontes["negrito"])
    estilo.map("Treeview", background=[("selected", tema["fundo_destaque"])],
               foreground=[("selected", tema["texto"])])

    # Abas (os painéis de baixo da visualização): a aba escolhida tem a cor dos cartões
    estilo.configure("TNotebook", background=tema["fundo"], bordercolor=tema["borda"], tabmargins=(0, 2, 0, 0))
    estilo.configure("TNotebook.Tab", background=tema["fundo"], foreground=tema["texto_suave"],
                     bordercolor=tema["borda"], lightcolor=tema["fundo"], padding=(12, 4), font=fontes["negrito"])
    estilo.map("TNotebook.Tab", background=[("selected", tema["superficie"]), ("active", tema["borda"])],
               foreground=[("selected", tema["texto"])], lightcolor=[("selected", tema["superficie"])])
    # A tela por partes: a trilha da esquerda, os títulos das partes e os botões de "mostrar"
    estilo.configure("Trilha.TFrame", background=tema["superficie"])
    estilo.configure("TrilhaGrupo.TLabel", background=tema["superficie"], foreground=tema["texto_suave"],
                     font=fontes["pequena"])
    estilo.configure("TituloDaParte.TLabel", font=fontes["mensagem"])
    estilo.configure("TrilhaErro.TLabel", background=tema["superficie"], foreground=tema["erro"], font=fontes["pequena"])
    estilo.configure("Chip.TCheckbutton", background=tema["fundo"], foreground=tema["texto"], padding=(6, 2))
    estilo.map("Chip.TCheckbutton", background=[("active", tema["fundo"])])
    estilo.configure("Chip.Toolbutton", background=tema["superficie"], foreground=tema["texto"],
                     bordercolor=tema["borda"], lightcolor=tema["superficie"], darkcolor=tema["superficie"],
                     relief="solid", borderwidth=1, padding=(8, 2), font=fontes["pequena"])
    estilo.map("Chip.Toolbutton",
               background=[("selected", tema["fundo_destaque"]), ("active", tema["borda"])],
               foreground=[("selected", tema["texto"])],
               relief=[("selected", "solid"), ("pressed", "solid")])
    estilo.configure("Pequeno.TButton", padding=(6, 2), font=fontes["pequena"])
    estilo.configure("TPanedwindow", background=tema["fundo"])
    estilo.configure("Sash", sashthickness=6, gripcount=0, background=tema["borda"])
    estilo.configure("Horizontal.TScale", background=tema["fundo"], troughcolor=tema["borda"])
    for nome in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        estilo.configure(nome, background=tema["superficie"], troughcolor=tema["fundo"],
                         arrowcolor=tema["texto_suave"], bordercolor=tema["borda"])
