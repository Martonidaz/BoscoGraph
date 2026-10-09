'''
    O conteúdo do relatório em PDF: junta tudo o que as partes da tela mostram (vértices, arestas, lista,
    matrizes, pesos, tipo do grafo, passos da busca, resultado e o código de estudo) numa lista de blocos
    que o exportacao/relatorio.py arruma nas páginas.

    Cada seção tem a cor da parte correspondente da tela (Vértices em azul, Lista em verde...), para o
    relatório "conversar" com o programa. As cores são sempre as do tema claro (o papel é branco).
'''

import datetime
from decimal import Decimal

import algoritmos
import caminhos
import entrada
import estudo
import representacoes
from entrada import formatar_numero
from visual import perfis
from visual import tema as temas
from visual.partes_da_busca import matriz_do_floyd
from visual.partes_do_grafo import NOMES_DOS_TIPOS
from visual.tema import misturar

MAXIMO_DE_PASSOS = 400              # passos da busca listados por inteiro; mais que isso, o começo e o fim
PASSOS_DO_COMECO = 300
PASSOS_DO_FIM = 60


def cor_da_parte(chave):
    return temas.CLARO["parte_" + chave]


def seta(direcionado):
    return "→" if direcionado else "—"


# As opções do desenho sem as cores da busca (o grafo "como montado")
def opcoes_neutras(tela):
    preferencias = tela.app.preferencias
    return {"arrumacao": preferencias.get("arrumacao", "circulo"), "nomes": preferencias.get("nomes_das_arestas", True),
            "pesos": preferencias.get("pesos_das_arestas", True), "informacao": "", "neutro": True,
            "algoritmo": tela.sessao.algoritmo, "destino": tela.sessao.destino_da_busca()}


# figura_do_grafo: a função do visual/exportar.py que desenha o grafo num estado e devolve a figura
def montar(tela, figura_do_grafo):
    sessao = tela.sessao
    tema = temas.CLARO
    blocos = []
    agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    informacoes = sessao.informacoes_da_busca()

    # ------------------------------------------------------------------
    # Capa: o resumo e o desenho
    # ------------------------------------------------------------------
    fatos = [("Grafo", ("orientado" if sessao.direcionado else "não orientado") + " · "
              + entrada.resumo(sessao.vertices, sessao.arestas, sessao.direcionado))]
    densidade = representacoes.densidade(len(sessao.vertices), len(sessao.arestas), sessao.direcionado)
    if densidade is not None:
        fatos.append(("Densidade", f"{representacoes.arredondado(Decimal(str(round(densidade, 4))))} "
                                   f"(arestas ÷ máximo de um grafo simples com {len(sessao.vertices)} vértices)"))
    estatisticas = representacoes.estatisticas_dos_pesos(sessao.arestas)
    if estatisticas is None:
        fatos.append(("Pesos", "nenhuma aresta tem peso"))
    else:
        fatos.append(("Pesos", f"{estatisticas['quantidade']} de {len(sessao.arestas)} arestas com peso, "
                               f"de {formatar_numero(estatisticas['menor'])} a {formatar_numero(estatisticas['maior'])}"))
    fatos.append(("Busca", informacoes["nome"]))
    fatos += opcoes_da_busca(sessao)
    fatos.append(("Listas", "ordenadas (ordem alfabética)" if sessao.ordenar else "na ordem em que as arestas foram criadas"))
    blocos.append({"tipo": "capa", "titulo": sessao.nome,
                   "subtitulo": f"Relatório do {caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO} · gerado em {agora}",
                   "fatos": fatos, "altura_maxima": 330, "legenda": "O grafo montado",
                   "figura": figura_do_grafo(tela, sessao.estado_montado(), opcoes_neutras(tela), tema)})

    blocos += blocos_do_grafo(sessao, estatisticas)
    blocos += blocos_da_busca(tela, figura_do_grafo, tema)
    blocos += blocos_do_codigo(sessao)
    return {"titulo": sessao.nome, "blocos": blocos}


def opcoes_da_busca(sessao):
    informacoes = sessao.informacoes_da_busca()
    fatos = []
    if sessao.algoritmo == algoritmos.PROFUNDIDADE:
        fatos.append(("Raízes", f"começa por {sessao.origem()}; depois, cada vértice ainda branco, em ordem alfabética"))
    elif sessao.algoritmo == algoritmos.PRIM:
        fatos.append(("Raiz", f"{sessao.origem()} (numa parte desligada, uma árvore nova começa no primeiro vértice "
                              f"que ainda está fora, em ordem alfabética)"))
    elif sessao.algoritmo != algoritmos.FLOYD_WARSHALL and informacoes.get("usa_origem", True):
        fatos.append(("Origem", str(sessao.origem())))
    if informacoes["destino"] != "nao":
        fatos.append(("Destino", sessao.destino_da_busca() or "nenhum"))
    if informacoes["usa_limite"]:
        fatos.append(("Limite", str(sessao.limite)))
    return fatos


# ----------------------------------------------------------------------
# O grafo: vértices, arestas, lista, matrizes, pesos e o tipo
# ----------------------------------------------------------------------

def blocos_do_grafo(sessao, estatisticas):
    blocos = []
    vertices = sessao.vertices
    arestas = sessao.arestas
    direcionado = sessao.direcionado

    blocos.append({"tipo": "secao", "titulo": "Vértices e arestas", "cor": cor_da_parte("vertices"),
                   "descricao": "Os vértices na ordem em que foram criados e cada aresta com as suas pontas."})
    blocos.append({"tipo": "paragrafo", "texto": entrada.contar(len(vertices), "vértice", "vértices") + ": "
                   + ", ".join(vertices) + "."})
    if arestas:
        observacoes = entrada.observacoes(arestas, direcionado)
        linhas = []
        for numero in range(len(arestas)):
            origem, destino, nome, peso = arestas[numero]
            linhas.append([str(numero + 1), nome or "—", f"{origem} {seta(direcionado)} {destino}",
                           formatar_numero(peso) if peso is not None else "—", observacoes[numero] or ""])
        blocos.append({"tipo": "tabela", "colunas": ["#", "Nome", "Aresta", "Peso", "Observação"], "linhas": linhas,
                       "alinhamentos": ["centro", "centro", "esquerda", "centro", "esquerda"]})

    # Lista de adjacência
    blocos.append({"tipo": "secao", "titulo": "Lista de adjacência", "cor": cor_da_parte("lista"),
                   "descricao": "Adj[u]: os vizinhos de cada vértice, na ordem em que a busca visita"
                                + (" (ordem alfabética)." if sessao.ordenar else " (a ordem de criação das arestas).")})
    # Como na parte Lista de adjacência: no orientado, os vizinhos para onde as arestas saem
    vizinhos = representacoes.lista_de_saida(vertices, arestas, direcionado, sessao.ordenar)
    linhas = []
    for vertice in vertices:
        linhas.append([vertice, texto_da_lista(vizinhos[vertice])])
    blocos.append({"tipo": "tabela", "colunas": ["Vértice", "Vizinhos (Adj[u])"], "linhas": linhas})

    # Matrizes
    blocos.append({"tipo": "secao", "titulo": "Matriz de adjacência", "cor": cor_da_parte("adjacencia"),
                   "descricao": "Linha = vértice de onde a aresta sai, coluna = onde ela chega"
                                + ("." if direcionado else " (não orientado: a matriz é simétrica; o laço conta 1).")})
    for modo, nome_do_modo in representacoes.modos_da_adjacencia(direcionado):
        if modo == "pesos" and estatisticas is None:
            continue
        matriz = representacoes.matriz_de_adjacencia(vertices, arestas, direcionado, modo)
        blocos.append({"tipo": "subtitulo", "texto": "Modo: " + nome_do_modo})
        blocos.append({"tipo": "grade", "matriz": matriz})
    blocos.append({"tipo": "secao", "titulo": "Matriz de incidência", "cor": cor_da_parte("incidencia"),
                   "descricao": "Uma coluna por aresta. " + ("−1 onde a aresta sai e +1 onde chega."
                                                              if direcionado else "1 nas duas pontas (o laço vale 2).")})
    if not arestas:
        blocos.append({"tipo": "paragrafo", "texto": "O grafo não tem arestas.", "estilo": "suave"})
    for modo, nome_do_modo in representacoes.MODOS_DA_INCIDENCIA:
        if not arestas or (modo == "pesos" and estatisticas is None):
            continue
        matriz = representacoes.matriz_de_incidencia(vertices, arestas, direcionado, modo)
        blocos.append({"tipo": "subtitulo", "texto": "Modo: " + nome_do_modo})
        blocos.append({"tipo": "grade", "matriz": matriz})

    # Pesos
    if estatisticas is not None or sessao.heuristica:
        blocos.append({"tipo": "secao", "titulo": "Pesos", "cor": cor_da_parte("pesos"),
                       "descricao": "As medidas dos pesos das arestas (o desvio padrão é o populacional)."})
    if estatisticas is not None:
        linhas = [["Arestas com peso", f"{estatisticas['quantidade']} de {len(arestas)}"],
                  ["Menor", formatar_numero(estatisticas["menor"])],
                  ["Maior", formatar_numero(estatisticas["maior"])],
                  ["Soma", formatar_numero(estatisticas["soma"])],
                  ["Média", representacoes.arredondado(estatisticas["media"])],
                  ["Mediana", representacoes.arredondado(estatisticas["mediana"])],
                  ["Desvio padrão", representacoes.arredondado(estatisticas["desvio"])],
                  ["Pesos negativos", str(estatisticas["negativos"])]]
        blocos.append({"tipo": "tabela", "colunas": ["Medida", "Valor"], "linhas": linhas,
                       "alinhamentos": ["esquerda", "direita"]})
    if sessao.heuristica:
        linhas = []
        for vertice in vertices:
            h = sessao.heuristica.get(vertice)
            linhas.append([vertice, formatar_numero(h) if h is not None else "—"])
        blocos.append({"tipo": "subtitulo", "texto": "Heurística h (a estimativa de cada vértice até o destino)"})
        blocos.append({"tipo": "tabela", "colunas": ["Vértice", "h"], "linhas": linhas,
                       "alinhamentos": ["esquerda", "direita"]})

    # Tipo do grafo (a análise feita com a busca em profundidade)
    linhas = []
    for passo in sessao.passos_do_grafo:
        if passo["tipo"] in NOMES_DOS_TIPOS:
            linhas.append([NOMES_DOS_TIPOS[passo["tipo"]], passo["mensagem"]])
    if linhas:
        blocos.append({"tipo": "secao", "titulo": "Tipo do grafo", "cor": cor_da_parte("tipo"),
                       "descricao": "A classificação feita com a busca em profundidade."})
        blocos.append({"tipo": "tabela", "colunas": ["Propriedade", "O que a análise diz"], "linhas": linhas})
    return blocos


# "B (3), C (5)": os vizinhos com os pesos; "—" se não há nenhum
def texto_da_lista(itens):
    if not itens:
        return "—"
    partes = []
    for vizinho, peso, numero in itens:
        if peso is not None:
            partes.append(f"{vizinho} ({formatar_numero(peso)})")
        else:
            partes.append(vizinho)
    return ", ".join(partes)


# ----------------------------------------------------------------------
# A busca: passos, resultado e a tabela do fim
# ----------------------------------------------------------------------

def blocos_da_busca(tela, figura_do_grafo, tema):
    sessao = tela.sessao
    informacoes = sessao.informacoes_da_busca()
    blocos = [{"tipo": "quebra"},
              {"tipo": "secao", "titulo": "A busca: " + informacoes["nome"], "cor": cor_da_parte("passo"),
               "descricao": informacoes["descricao"]}]
    if not sessao.pode_buscar():
        blocos.append({"tipo": "paragrafo", "estilo": "aviso",
                       "texto": "A busca não pode rodar neste grafo: " + " ".join(sessao.problemas)})
        return blocos
    for aviso in sessao.avisos:
        blocos.append({"tipo": "paragrafo", "texto": aviso, "estilo": "suave"})

    # Os passos da busca (etapa 5), numerados como no passo a passo
    da_busca = []
    do_resultado = []
    for indice in range(len(sessao.passos)):
        if sessao.etapas[indice] == 5:
            da_busca.append(sessao.passos[indice]["mensagem"])
        elif sessao.etapas[indice] == 6:
            do_resultado.append(sessao.passos[indice]["mensagem"])
    blocos.append({"tipo": "subtitulo", "texto": f"Passo a passo ({entrada.contar(len(da_busca), 'passo', 'passos')})"})
    if len(da_busca) <= MAXIMO_DE_PASSOS:
        blocos.append({"tipo": "numerada", "itens": da_busca})
    else:
        blocos.append({"tipo": "numerada", "itens": da_busca[:PASSOS_DO_COMECO]})
        pulados = len(da_busca) - PASSOS_DO_COMECO - PASSOS_DO_FIM
        blocos.append({"tipo": "paragrafo", "estilo": "suave",
                       "texto": f"(… {pulados} passos do meio não foram listados: o passo a passo do programa "
                                f"mostra todos …)"})
        blocos.append({"tipo": "numerada", "itens": da_busca[-PASSOS_DO_FIM:],
                       "inicio": len(da_busca) - PASSOS_DO_FIM + 1})

    # O resultado: as conclusões, o desenho do fim e a tabela do fim
    blocos.append({"tipo": "secao", "titulo": "Resultado", "cor": cor_da_parte("resultado")})
    if do_resultado:
        blocos.append({"tipo": "numerada", "itens": do_resultado})
    ultimo = len(sessao.passos) - 1
    final = sessao.estado_no_passo(ultimo)
    opcoes = opcoes_neutras(tela)
    opcoes["neutro"] = False
    blocos.append({"tipo": "figura", "figura": figura_do_grafo(tela, final, opcoes, tema), "altura_maxima": 330,
                   "legenda": "O grafo no fim da busca (com as cores e as marcas do resultado)"})
    perfil = perfis.perfil(sessao.algoritmo)
    if perfil["estrutura"] == "matriz":
        blocos.append({"tipo": "subtitulo", "texto": "Matriz d (as menores distâncias de cada linha para cada coluna)"})
        blocos.append({"tipo": "grade", "matriz": matriz_do_floyd(final, sessao.vertices, "d")})
        blocos.append({"tipo": "subtitulo", "texto": "Matriz π (o vértice antes da coluna no caminho que sai da linha)"})
        blocos.append({"tipo": "grade", "matriz": matriz_do_floyd(final, sessao.vertices, "pi")})
    else:
        colunas = ["Vértice"]
        for chave, titulo, largura in perfil["colunas"]:
            colunas.append(titulo)
        linhas = []
        tons = []
        for vertice in sessao.vertices:
            linhas.append([vertice] + [str(valor) for valor in perfis.valores_da_tabela(sessao.algoritmo, final, vertice)])
            cor = final.cor.get(vertice)
            numero = final.numero_da_cor_do_conjunto(vertice)
            if numero is not None:
                tons.append(misturar("#ffffff", tema[f"conjunto_{numero % temas.CORES_DOS_CONJUNTOS}"], 0.5))
            elif cor in ("Cinza", "Preto"):
                tons.append(misturar("#ffffff", tema["vertice_" + cor.lower()], 0.2))
            else:
                tons.append(None)
        blocos.append({"tipo": "subtitulo", "texto": perfil["titulo_tabela"]})
        blocos.append({"tipo": "tabela", "colunas": colunas, "linhas": linhas, "tons": tons,
                       "alinhamentos": ["esquerda"] + ["centro"] * (len(colunas) - 1)})
    return blocos


# ----------------------------------------------------------------------
# O código de estudo (o pseudocódigo e o Python)
# ----------------------------------------------------------------------

def blocos_do_codigo(sessao):
    blocos = [{"tipo": "quebra"},
              {"tipo": "secao", "titulo": "Código de estudo", "cor": cor_da_parte("linha"),
               "descricao": "O algoritmo sozinho, como no livro do Cormen (CLRS): primeiro o pseudocódigo, depois "
                            "o Python que o modo linha a linha executa. As outras linguagens saem pelo menu "
                            "Exportar > Código-fonte."}]
    for chave, titulo in (("pseudocodigo", "Pseudocódigo"), ("python", "Python")):
        try:
            arquivo = estudo.carregar(sessao.algoritmo, chave)
        except (OSError, KeyError):
            continue
        blocos.append({"tipo": "codigo", "titulo": titulo, "linhas": arquivo["linhas"]})
    return blocos
