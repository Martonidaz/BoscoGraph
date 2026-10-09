# O "perfil" de cada busca: o que a janela de visualização mostra para ela.
#
#   etapa_5 / etapa_6   -> o nome das duas últimas etapas ("DFS" e "Tipo"; "Dijkstra" e "Resultado"...)
#   estrutura           -> o que o painel da estrutura desenha: "pilha", "fila", "prioridade", "rodadas",
#                          "duas_filas" (bidirecional), "matriz" (Floyd-Warshall) ou "conjuntos" (Kruskal)
#   titulo_estrutura    -> o título desse painel
#   titulo_tabela       -> o título da tabela da direita
#   colunas             -> as colunas da tabela, depois da coluna "Vértice": (chave, título, largura)
#   legenda             -> os itens da legenda embaixo do desenho: (símbolo, texto)
#   trechos             -> a linha de código que cada passo destaca: (arquivo, a partir de qual linha
#                          procurar, trecho da linha). "a partir de" serve quando o mesmo trecho
#                          aparece em dois lugares (como self.tempo = 0)
#
# Este arquivo não usa Tkinter: os testes conferem que todo trecho existe no código.

import algoritmos
from entrada import formatar_numero

# As etapas 1 a 4 (montar o grafo) são iguais em todas as buscas
TRECHOS_DA_MONTAGEM = {
    "criar_vertice": ("boscograph.py", None, "dicionario_vertice[nome] = Vertice(nome)"),
    "criar_aresta": ("boscograph.py", None, "lista_arestas.append(Aresta("),
    "sem_ordenar": ("boscograph.py", None, "if ordenar:"),
    "criar_lista": ("classes/grafo.py", None, "self.grafo[vertice.nome] = []"),
    "adicionar_vizinho": ("classes/grafo.py", None, "self.grafo[origem].append(destino)"),
    "adicionar_volta": ("classes/grafo.py", None, "self.grafo[destino].append(origem)"),
    "ordenar": ("classes/grafo.py", None, "self.grafo[nome].sort()"),
}

TRECHOS_DA_PROFUNDIDADE = {
    "pintar_branco": ("classes/busca_em_profundidade.py", None, 'self.cor[vertice] = "Branco"'),
    "zerar_tempo": ("classes/busca_em_profundidade.py", "def inicializar", "self.tempo = 0"),
    "nova_arvore": ("classes/busca_em_profundidade.py", "def dfs(", "self.dfs_visit(vertice)"),
    "descobrir": ("classes/busca_em_profundidade.py", None, 'self.cor[vertice] = "Cinza"'),
    "examinar_arvore": ("classes/busca_em_profundidade.py", None, "self.dfs_visit(vizinho)"),
    "examinar_outra": ("classes/busca_em_profundidade.py", None, "tipo_aresta = self.classificar(vertice, vizinho)"),
    "revisitar": ("classes/busca_em_profundidade.py", None, "self.anotar_volta(vertice, vizinho)"),
    "finalizar": ("classes/busca_em_profundidade.py", None, 'self.cor[vertice] = "Preto"'),
    "tipo_orientacao": ("classes/tipo_do_grafo.py", None, "def anotar_orientacao(self):"),
    "tipo_simples": ("classes/tipo_do_grafo.py", None, "simples = not lacos and not paralelas"),
    "tipo_completo": ("classes/tipo_do_grafo.py", None, "completo = self.resultado[\"simples\"] and len(ligados) == possiveis"),
    "tipo_valorado": ("classes/tipo_do_grafo.py", None, "def anotar_valorado(self):"),
    "tipo_ciclo": ("classes/tipo_do_grafo.py", None, "retornos = self.busca.arestas_de_retorno"),
    "tipo_dag": ("classes/tipo_do_grafo.py", None, "def anotar_dag(self):"),
    "ordem_topologica": ("classes/tipo_do_grafo.py", None, "ordem.sort(key=self.tempo_de_finalizacao, reverse=True)"),
    "tipo_componentes": ("classes/tipo_do_grafo.py", None, "def anotar_componentes(self):"),
    "tipo_resumo": ("classes/tipo_do_grafo.py", None, "def anotar_resumo(self):"),
}

# A etapa 6 das buscas a partir de uma origem
TRECHOS_DO_RESULTADO = {
    "resultado_distancias": ("classes/resultado_da_busca.py", None, "def anotar_distancias(self):"),
    "resultado_arvore": ("classes/resultado_da_busca.py", None, "def anotar_arvore(self):"),
    "resultado_caminho": ("classes/resultado_da_busca.py", None, "def anotar_caminho(self, destino):"),
    "resultado_ciclo_negativo": ("classes/resultado_da_busca.py", None, "def anotar_ciclo_negativo(self):"),
    "resultado_comparacao": ("classes/resultado_da_busca.py", None, "def anotar_comparacao(self, destino):"),
    "resultado_heuristica": ("classes/resultado_da_busca.py", None, "def anotar_heuristica(self, destino):"),
}

LARGURA = "classes/busca_em_largura.py"
TRECHOS_DA_LARGURA = {
    "inicializar": (LARGURA, None, 'self.cor[vertice] = "Branco"'),
    "origem": (LARGURA, None, "self.fila.append(origem)"),
    "desenfileirar": (LARGURA, None, "vertice = self.fila.pop(0)"),
    "descobrir_vizinho": (LARGURA, None, "self.fila.append(vizinho)"),
    "ignorar_vizinho": (LARGURA, None, 'if self.cor[vizinho] == "Branco":'),
    "terminar_vertice": (LARGURA, None, 'self.cor[vertice] = "Preto"'),
}

DIJKSTRA = "classes/dijkstra.py"
TRECHOS_DO_DIJKSTRA = {
    "inicializar": (DIJKSTRA, None, "self.d[vertice] = INFINITO"),
    "origem": (DIJKSTRA, None, "self.d[origem] = 0"),
    "extrair": (DIJKSTRA, None, "vertice = self.extrair_minimo()"),
    "relaxar_melhorou": (DIJKSTRA, None, "self.d[vizinho] = novo"),
    "relaxar_nao": (DIJKSTRA, None, "if novo < self.d[vizinho]:"),
}

BELLMAN_FORD = "classes/bellman_ford.py"
TRECHOS_DO_BELLMAN_FORD = {
    "inicializar": (BELLMAN_FORD, None, "self.d[vertice] = INFINITO"),
    "origem": (BELLMAN_FORD, None, "self.d[origem] = 0"),
    "rodada": (BELLMAN_FORD, None, "for rodada in range(1, total + 1):"),
    "relaxar_melhorou": (BELLMAN_FORD, None, "self.d[ate] = novo"),
    "relaxar_nao": (BELLMAN_FORD, None, "if novo < antes:"),
    "rodada_sem_mudanca": (BELLMAN_FORD, None, "if not mudou:"),
    "verificar_ciclo": (BELLMAN_FORD, 'self.anotar("verificar_ciclo"', "for de, ate, peso, numero in self.arcos:"),
    "ciclo_negativo": (BELLMAN_FORD, None, "if self.d[de] + peso < self.d[ate]:"),
    "sem_ciclo_negativo": (BELLMAN_FORD, None, "if parou_antes:"),
}

GULOSA = "classes/busca_gulosa.py"
TRECHOS_DA_GULOSA = {
    "inicializar": (GULOSA, "def buscar", 'self.cor[vertice] = "Branco"'),
    "origem": (GULOSA, None, "self.fila.append(origem)"),
    "extrair": (GULOSA, None, "vertice = self.extrair_minimo()"),
    "chegou": (GULOSA, None, "if vertice == destino:"),
    "descobrir_vizinho": (GULOSA, None, "self.fila.append(vizinho)"),
    "ignorar_vizinho": (GULOSA, "for vizinho, peso, numero in self.lista_adjacencia[vertice]:",
                        'if self.cor[vizinho] == "Branco":'),
    "nao_chegou": (GULOSA, None, "while self.fila:"),
}

A_ESTRELA = "classes/a_estrela.py"
TRECHOS_DO_A_ESTRELA = {
    "inicializar": (A_ESTRELA, None, "self.g[vertice] = INFINITO"),
    "origem": (A_ESTRELA, None, "self.f[origem] = self.h[origem]"),
    "extrair": (A_ESTRELA, None, "vertice = self.extrair_minimo()"),
    "chegou": (A_ESTRELA, None, "if vertice == destino:"),
    "relaxar_melhorou": (A_ESTRELA, None, "self.f[vizinho] = novo + self.h[vizinho]"),
    "relaxar_reabriu": (A_ESTRELA, None, 'elif self.cor[vizinho] == "Preto":'),
    "relaxar_nao": (A_ESTRELA, None, "if novo < self.g[vizinho]:"),
    "nao_chegou": (A_ESTRELA, None, "while self.fila:"),
}


LIMITADA = "classes/busca_limitada.py"
TRECHOS_DA_LIMITADA = {
    "inicializar": (LIMITADA, "def inicializar", 'self.cor[vertice] = "Branco"'),
    "entrar": (LIMITADA, "def entrar", 'self.cor[vertice] = "Cinza"'),
    "chegou": (LIMITADA, None, "if vertice == self.destino:"),
    "corte": (LIMITADA, None, "if restante == 0:"),
    "ignorar_vizinho": (LIMITADA, None, "if vizinho in self.caminho:"),
    "subir": (LIMITADA, "houve_corte = False", "self.sair(vertice)"),
}

ITERATIVA = "classes/aprofundamento_iterativo.py"
TRECHOS_DA_ITERATIVA = {
    "nova_iteracao": (ITERATIVA, None, "self.nova_iteracao(limite)"),
}

BIDIRECIONAL = "classes/busca_bidirecional.py"
TRECHOS_DA_BIDIRECIONAL = {
    "inicializar": (BIDIRECIONAL, None, 'self.cor[vertice] = "Branco"'),
    "origem": (BIDIRECIONAL, None, "self.fila.append(origem)"),
    "encontro_na_origem": (BIDIRECIONAL, None, "if origem == destino:"),
    "origem_tras": (BIDIRECIONAL, None, "self.fila_tras.append(destino)"),
    "nova_camada": (BIDIRECIONAL, None, "tamanho = len(fila)"),
    "desenfileirar": (BIDIRECIONAL, None, "vertice = fila.pop(0)"),
    "encontro": (BIDIRECIONAL, None, "if self.lado[vizinho] == outro:"),
    "descobrir_vizinho": (BIDIRECIONAL, None, "fila.append(vizinho)"),
    "ignorar_vizinho": (BIDIRECIONAL, "def expandir", 'if self.cor[vizinho] == "Branco":'),
    "terminar_vertice": (BIDIRECIONAL, None, 'self.cor[vertice] = "Preto"'),
    "sem_encontro": (BIDIRECIONAL, None, 'self.anotar("sem_encontro"'),
}

FLOYD = "classes/floyd_warshall.py"
TRECHOS_DO_FLOYD = {
    "inicializar_linha": (FLOYD, None, "self.d[i][i] = 0"),
    "arco_melhorou": (FLOYD, None, "self.d[origem][destino] = peso"),
    "arco_nao": (FLOYD, None, "melhorou = peso < antes"),
    "rodada_k": (FLOYD, None, "for k in self.vertices:"),
    "par_melhorou": (FLOYD, None, "self.d[i][j] = por_k"),
    "par_nao": (FLOYD, None, "melhorou = por_k < antes"),
    "diagonal_negativa": (FLOYD, "def conferir_ciclo_negativo", "if self.d[i][i] < 0:"),
    "sem_ciclo_negativo": (FLOYD, "def conferir_ciclo_negativo", "if self.ciclo_negativo:"),
}

PRIM = "classes/prim.py"
TRECHOS_DO_PRIM = {
    "inicializar": (PRIM, None, "self.chave[vertice] = INFINITO"),
    "raiz": (PRIM, None, "self.fila.append(raiz)"),
    "extrair": (PRIM, None, "vertice = self.extrair_minimo()"),
    "ignorar_vizinho": (PRIM, None, 'if self.cor[vizinho] == "Preto":'),
    "atualizar_melhorou": (PRIM, None, "self.chave[vizinho] = peso"),
    "atualizar_nao": (PRIM, None, "if peso < self.chave[vizinho]:"),
}

KRUSKAL = "classes/kruskal.py"
TRECHOS_DO_KRUSKAL = {
    "criar_conjunto": (KRUSKAL, None, "self.conjunto[vertice] = vertice"),
    "ordenar_arestas": (KRUSKAL, None, "numeros.sort(key=self.peso_da_aresta)"),
    "aceitar": (KRUSKAL, None, "self.arvore.append(numero)"),
    "rejeitar": (KRUSKAL, None, "if self.conjunto[u] == self.conjunto[v]:"),
    "unir": (KRUSKAL, None, "self.conjunto[x] = a"),
}

RESULTADO = "classes/resultado_da_busca.py"
# O resultado da busca limitada, do aprofundamento iterativo, da bidirecional e do Floyd-Warshall
TRECHOS_DO_RESULTADO_NOVO = {
    "resultado_caminho": (RESULTADO, None, "def anotar_caminho_pronto(self, vertices, arestas):"),
    "resultado_limitada": (RESULTADO, None, "def anotar_limitada(self, destino):"),
    "resultado_iteracoes": (RESULTADO, None, "def anotar_iteracoes(self, destino):"),
    "resultado_comparacao": (RESULTADO, "def concluir_bidirecional", 'self.anotar("resultado_comparacao"'),
}
TRECHOS_DO_RESULTADO_DO_FLOYD = {
    "resultado_matriz": (RESULTADO, None, 'self.anotar("resultado_matriz"'),
    "resultado_diagonal_negativa": (RESULTADO, None, 'self.anotar("resultado_diagonal_negativa"'),
    "resultado_caminho": (RESULTADO, "def concluir_floyd_warshall", 'self.anotar("resultado_caminho"'),
}

# O resultado do Prim e do Kruskal: a árvore (ou floresta) e a comparação com o outro algoritmo
TRECHOS_DO_RESULTADO_DA_ARVORE = {
    "resultado_arvore_minima": (RESULTADO, None, "def anotar_arvore_minima(self, arestas, total):"),
    "resultado_mesmo_peso": (RESULTADO, None, "def anotar_mesmo_peso(self, arestas, total):"),
}


# Junta vários dicionários de trechos num só
def juntar(*partes):
    junto = {}
    for parte in partes:
        for chave in parte:
            junto[chave] = parte[chave]
    return junto


# Itens da legenda que se repetem
VERTICE_SEM_COR = ("sem_cor", "sem cor (antes da busca)")
DESTAQUE = ("destaque", "destaque do passo")
ARESTA_CRIADA = ("objeto", "aresta criada (fora do grafo)")
ARESTA_NA_LISTA = ("grafo", "na lista de adjacência")
ORIGEM = ("raiz", "origem")
DESTINO = ("destino", "destino")
CORTADO = ("cortado", "cortado pelo limite")

PERFIS = {
    algoritmos.PROFUNDIDADE: {
        "etapa_5": "DFS",
        "etapa_6": "Tipo",
        "estrutura": "pilha",
        "titulo_estrutura": "Pilha",
        "titulo_tabela": "Cores e tempos",
        "colunas": [("cor", "Cor", 76), ("d", "d", 44), ("f", "f", 44)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco"), ("Cinza", "Cinza"), ("Preto", "Preto"), DESTAQUE,
                    ARESTA_CRIADA, ARESTA_NA_LISTA, ("arvore", "árvore"), ("retorno", "retorno (fecha ciclo)"),
                    ("avanco", "avanço"), ("cruzamento", "cruzamento")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_PROFUNDIDADE),
    },
    algoritmos.LIMITADA: {
        "etapa_5": "Limitada",
        "etapa_6": "Resultado",
        "estrutura": "pilha",
        "titulo_estrutura": "Caminho (pilha)",
        "titulo_tabela": "Profundidade",
        "colunas": [("cor", "Cor", 76), ("prof", "prof.", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: fora do caminho"), ("Cinza", "Cinza: no caminho"),
                    ("Preto", "Preto: já saiu do caminho"), ORIGEM, DESTINO, CORTADO, DESTAQUE, ARESTA_CRIADA,
                    ARESTA_NA_LISTA, ("arvore", "caminho atual"), ("examinada", "já percorrida ou ignorada")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_LIMITADA, TRECHOS_DO_RESULTADO_NOVO),
    },
    algoritmos.ITERATIVA: {
        "etapa_5": "Iterativo",
        "etapa_6": "Resultado",
        "estrutura": "pilha",
        "titulo_estrutura": "Caminho (pilha)",
        "titulo_tabela": "Profundidade",
        "colunas": [("cor", "Cor", 76), ("prof", "prof.", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: fora do caminho"), ("Cinza", "Cinza: no caminho"),
                    ("Preto", "Preto: já saiu do caminho"), ORIGEM, DESTINO, CORTADO, DESTAQUE, ARESTA_CRIADA,
                    ARESTA_NA_LISTA, ("arvore", "caminho atual"), ("examinada", "já percorrida ou ignorada")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_LIMITADA, TRECHOS_DA_ITERATIVA, TRECHOS_DO_RESULTADO_NOVO),
    },
    algoritmos.BIDIRECIONAL: {
        "etapa_5": "Bidirecional",
        "etapa_6": "Resultado",
        "estrutura": "duas_filas",
        "titulo_estrutura": "Filas (frente e trás)",
        "titulo_tabela": "Os dois lados (d e π: da frente · d' e π': de trás)",
        "colunas": [("cor", "Cor", 70), ("lado", "lado", 60), ("d", "d", 44), ("pai", "π", 50), ("d_tras", "d'", 44),
                    ("pai_tras", "π'", 50)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: ninguém descobriu"), ("frente", "descoberto pela frente"),
                    ("tras", "descoberto por trás"), ("Preto", "Preto: expandido"), ORIGEM, DESTINO, DESTAQUE,
                    ARESTA_CRIADA, ARESTA_NA_LISTA, ("arvore", "árvore da frente"), ("arvore_tras", "árvore de trás"),
                    ("examinada", "examinada (já descoberto)")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_BIDIRECIONAL, TRECHOS_DO_RESULTADO_NOVO),
    },
    algoritmos.FLOYD_WARSHALL: {
        "etapa_5": "Floyd-Warshall",
        "etapa_6": "Resultado",
        "estrutura": "matriz",
        "titulo_estrutura": "Matriz d",
        "titulo_tabela": "Matriz π",
        "colunas": [],                  # a tabela do Floyd-Warshall é a matriz π: uma coluna por vértice
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: ainda não foi o k"), ("Cinza", "Cinza: o k desta rodada"),
                    ("Preto", "Preto: já foi o k"), DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "aresta na matriz inicial"), ("examinada", "paralela mais cara (fora da matriz)")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_FLOYD, TRECHOS_DO_RESULTADO_DO_FLOYD),
    },
    algoritmos.LARGURA: {
        "etapa_5": "BFS",
        "etapa_6": "Resultado",
        "estrutura": "fila",
        "titulo_estrutura": "Fila",
        "titulo_tabela": "Cores e distâncias",
        "colunas": [("cor", "Cor", 76), ("d", "d", 44), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: não descoberto"), ("Cinza", "Cinza: na fila"),
                    ("Preto", "Preto: terminado"), ORIGEM, DESTINO, DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "árvore da BFS (π)"), ("examinada", "examinada (vizinho já descoberto)")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_LARGURA, TRECHOS_DO_RESULTADO),
    },
    algoritmos.DIJKSTRA: {
        "etapa_5": "Dijkstra",
        "etapa_6": "Resultado",
        "estrutura": "prioridade",
        "titulo_estrutura": "Fila de prioridade",
        "titulo_tabela": "Distâncias",
        "colunas": [("cor", "Cor", 76), ("d", "d", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: d = ∞"), ("Cinza", "Cinza: na fila"),
                    ("Preto", "Preto: d definitivo"), ORIGEM, DESTINO, DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "melhor caminho conhecido (π)"), ("examinada", "relaxada, sem melhorar")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_DIJKSTRA, TRECHOS_DO_RESULTADO),
    },
    algoritmos.BELLMAN_FORD: {
        "etapa_5": "Bellman-Ford",
        "etapa_6": "Resultado",
        "estrutura": "rodadas",
        "titulo_estrutura": "Rodadas",
        "titulo_tabela": "Distâncias",
        "colunas": [("cor", "Cor", 76), ("d", "d", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: d = ∞"), ("Cinza", "Cinza: d provisório"),
                    ("Preto", "Preto: d final"), ORIGEM, DESTINO, DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "melhor caminho conhecido (π)"), ("examinada", "relaxada, sem melhorar")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_BELLMAN_FORD, TRECHOS_DO_RESULTADO),
    },
    algoritmos.GULOSA: {
        "etapa_5": "Gulosa",
        "etapa_6": "Resultado",
        "estrutura": "prioridade",
        "titulo_estrutura": "Fronteira (por h)",
        "titulo_tabela": "Heurística e caminho",
        "colunas": [("cor", "Cor", 76), ("h", "h", 52), ("g", "g", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: não visto"), ("Cinza", "Cinza: na fronteira"),
                    ("Preto", "Preto: expandido"), ORIGEM, DESTINO, DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "caminho escolhido (π)"), ("examinada", "examinada (já visto)")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DA_GULOSA, TRECHOS_DO_RESULTADO),
    },
    algoritmos.A_ESTRELA: {
        "etapa_5": "A*",
        "etapa_6": "Resultado",
        "estrutura": "prioridade",
        "titulo_estrutura": "Fronteira (por f)",
        "titulo_tabela": "g + h = f",
        "colunas": [("cor", "Cor", 76), ("g", "g", 52), ("h", "h", 52), ("f", "f", 52), ("pai", "π", 60)],
        "legenda": [VERTICE_SEM_COR, ("Branco", "Branco: não visto"), ("Cinza", "Cinza: na fronteira"),
                    ("Preto", "Preto: expandido"), ORIGEM, DESTINO, DESTAQUE, ARESTA_CRIADA, ARESTA_NA_LISTA,
                    ("arvore", "melhor caminho conhecido (π)"), ("examinada", "relaxada, sem melhorar")],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_A_ESTRELA, TRECHOS_DO_RESULTADO),
    },
    algoritmos.PRIM: {
        "etapa_5": "Prim",
        "etapa_6": "Resultado",
        "estrutura": "prioridade",
        "titulo_estrutura": "Fila de prioridade (por chave)",
        "titulo_tabela": "Chaves",
        "colunas": [("cor", "Cor", 76), ("d", "chave", 60), ("pai", "π", 60)],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_PRIM, TRECHOS_DO_RESULTADO_DA_ARVORE),
    },
    algoritmos.KRUSKAL: {
        "etapa_5": "Kruskal",
        "etapa_6": "Resultado",
        "estrutura": "conjuntos",
        "titulo_estrutura": "Arestas em ordem e conjuntos",
        "titulo_tabela": "Conjuntos",
        "colunas": [("conjunto", "conjunto (representante)", 150)],
        "trechos": juntar(TRECHOS_DA_MONTAGEM, TRECHOS_DO_KRUSKAL, TRECHOS_DO_RESULTADO_DA_ARVORE),
    },
}


def perfil(chave):
    if chave in PERFIS:
        return PERFIS[chave]
    return PERFIS[algoritmos.PROFUNDIDADE]


# Qual trecho de código corresponde a um passo
def chave_do_trecho(passo):
    tipo = passo["tipo"]
    if tipo == "examinar":
        if passo["classe"] == "arvore":
            return "examinar_arvore"
        return "examinar_outra"
    if tipo == "adicionar_vizinho" and passo.get("volta"):
        return "adicionar_volta"
    if tipo == "atualizar":
        if passo["melhorou"]:
            return "atualizar_melhorou"
        return "atualizar_nao"
    if tipo == "relaxar":
        if passo.get("reabriu"):
            return "relaxar_reabriu"
        if passo["melhorou"]:
            return "relaxar_melhorou"
        return "relaxar_nao"
    if tipo == "arco_inicial":
        if passo["melhorou"]:
            return "arco_melhorou"
        return "arco_nao"
    if tipo == "comparar_par":
        if passo["melhorou"]:
            return "par_melhorou"
        return "par_nao"
    if tipo == "encontro" and passo.get("na_origem"):
        return "encontro_na_origem"
    return tipo


# ----------------------------------------------------------------------
# O que aparece na tabela e ao lado de cada vértice
# ----------------------------------------------------------------------

def texto_ou_traco(dicionario, vertice):
    if vertice in dicionario:
        return formatar_numero(dicionario[vertice])
    return "—"


# Os valores de uma linha da tabela, na ordem das colunas do perfil (depois do nome do vértice)
def valores_da_tabela(chave, estado, vertice):
    valores = []
    for coluna, titulo, largura in perfil(chave)["colunas"]:
        if coluna == "cor":
            cor = estado.cor.get(vertice)
            valores.append(cor if cor is not None else "—")
        elif coluna == "d" and chave == algoritmos.PROFUNDIDADE:
            valores.append(estado.d.get(vertice, "—"))
        elif coluna == "f" and chave == algoritmos.PROFUNDIDADE:
            valores.append(estado.f.get(vertice, "—"))
        elif coluna in ("d", "g"):
            valores.append(texto_ou_traco(estado.distancia, vertice))
        elif coluna == "h":
            valores.append(texto_ou_traco(estado.h, vertice))
        elif coluna == "f":
            valores.append(texto_ou_traco(estado.prioridade, vertice))
        elif coluna == "pai":
            pai = estado.pai.get(vertice)
            valores.append(pai if pai is not None else "—")
        elif coluna == "prof":
            valores.append(estado.profundidade.get(vertice, "—"))
        elif coluna == "lado":
            valores.append({"frente": "frente", "tras": "trás"}.get(estado.lado.get(vertice), "—"))
        elif coluna == "d_tras":
            valores.append(texto_ou_traco(estado.distancia_tras, vertice))
        elif coluna == "pai_tras":
            pai = estado.pai_tras.get(vertice)
            valores.append(pai if pai is not None else "—")
        elif coluna == "conjunto":
            valores.append(estado.conjunto.get(vertice, "—"))
    return valores


# O texto ao lado do vértice no desenho ("" = nada)
#   DFS             -> "d/f" (os tempos de descoberta e de finalização)
#   BFS e Dijkstra  -> d (a distância; "∞" antes de ser alcançado)
#   gulosa          -> "h=5" (a estimativa que decide a ordem)
#   A*              -> "g+h", por exemplo "140+253"
#   limitada e iterativa -> "p=2" (a profundidade no caminho)
#   bidirecional    -> a distância desde a origem (frente) ou até o destino (trás)
#   Floyd-Warshall  -> nada (a matriz mostra tudo)
#   Prim            -> a chave ("∞" antes de ter uma ligação com a árvore)
#   Kruskal         -> nada (a cor do vértice mostra o conjunto dele)
def rotulo_do_vertice(chave, estado, vertice):
    if chave in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        if vertice in estado.profundidade:
            return f"p={estado.profundidade[vertice]}"
        return ""
    if chave == algoritmos.FLOYD_WARSHALL:
        return ""
    if chave == algoritmos.BIDIRECIONAL:
        if estado.lado.get(vertice) == "tras":
            return formatar_numero(estado.distancia_tras.get(vertice))
        if estado.lado.get(vertice) == "frente":
            return formatar_numero(estado.distancia.get(vertice))
        return ""
    if chave == algoritmos.PROFUNDIDADE:
        if vertice not in estado.d:
            return ""
        if vertice in estado.f:
            return f"{estado.d[vertice]}/{estado.f[vertice]}"
        return f"{estado.d[vertice]}/"
    if chave == algoritmos.GULOSA:
        if vertice in estado.h:
            return "h=" + formatar_numero(estado.h[vertice])
        return ""
    if vertice not in estado.distancia:
        return ""
    if chave == algoritmos.A_ESTRELA:
        return formatar_numero(estado.distancia[vertice]) + "+" + formatar_numero(estado.h.get(vertice))
    return formatar_numero(estado.distancia[vertice])
