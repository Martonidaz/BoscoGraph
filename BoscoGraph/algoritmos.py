'''
    As buscas que o BoscoGraph sabe visualizar e o que cada uma precisa para rodar.

    Cada busca é um dicionário com:
      chave         -> o identificador usado no código e nos modelos ("dijkstra")
      nome          -> como aparece na lista do editor ("Dijkstra (custo uniforme)")
      nome_curto    -> o nome da etapa 5 na visualização ("Dijkstra")
      descricao     -> uma frase sobre a ideia da busca
      estrutura     -> a estrutura de dados que guia a busca (pilha, fila, fila de prioridade...)
      usa_pesos     -> "nao", "sim" (todas as arestas precisam de peso) ou "opcional"
      negativos     -> aceita peso negativo?
      usa_heuristica-> precisa de h(v) em todos os vértices?
      destino       -> "nao", "opcional" (marca o caminho no resultado) ou "obrigatorio"
      usa_limite    -> precisa de um limite de profundidade? (só a busca em profundidade limitada)
      usa_origem    -> parte de um vértice escolhido? (sem o campo: sim; o Kruskal não, ele olha as arestas)
      so_nao_orientado -> só funciona no grafo não orientado? (sem o campo: não; Prim e Kruskal: sim)

    A função conferir() diz o que falta para visualizar (problemas, que impedem) e o que vale
    a pena saber (avisos, que não impedem). O editor mostra os dois enquanto o grafo é montado.
    Este arquivo não usa Tkinter.
'''

import entrada

PROFUNDIDADE = "profundidade"
LIMITADA = "limitada"
ITERATIVA = "iterativa"
LARGURA = "largura"
BIDIRECIONAL = "bidirecional"
DIJKSTRA = "dijkstra"
BELLMAN_FORD = "bellman_ford"
FLOYD_WARSHALL = "floyd_warshall"
GULOSA = "gulosa"
A_ESTRELA = "a_estrela"
PRIM = "prim"                       # versão 7.3: a árvore geradora mínima
KRUSKAL = "kruskal"

# A busca limitada e o aprofundamento iterativo são buscas em "árvore": o mesmo vértice pode entrar
# no caminho muitas vezes, por caminhos diferentes, e num grafo cheio de ligações a quantidade de nós
# cresce muito rápido com o limite. Acima disso a visualização ficaria grande demais.
LIMITE_DE_NOS = 1500
MAIOR_LIMITE = 25                   # o maior limite de profundidade que o editor aceita
# O Floyd-Warshall faz n³ comparações: com 12 vértices já são 1728
MAXIMO_FLOYD = 12

ALGORITMOS = [
    {
        "chave": PROFUNDIDADE,
        "nome": "Profundidade (DFS)",
        "nome_curto": "DFS",
        "descricao": "Vai o mais fundo possível antes de voltar. Mostra os tempos d/f, os tipos de aresta, "
                     "ciclos e DAG.",
        "estrutura": "pilha",
        "usa_pesos": "nao",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "nao",
        "usa_limite": False,
    },
    {
        "chave": LIMITADA,
        "nome": "Profundidade limitada",
        "nome_curto": "Limitada",
        "descricao": "A busca em profundidade com um limite: não desce mais que L arestas a partir da origem. "
                     "No limite ela corta (não olha os vizinhos) e não repete vértices do caminho atual.",
        "estrutura": "pilha",
        "usa_pesos": "nao",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "opcional",
        "usa_limite": True,
    },
    {
        "chave": ITERATIVA,
        "nome": "Aprofundamento iterativo",
        "nome_curto": "Iterativo",
        "descricao": "Repete a busca limitada com limite 0, 1, 2... até achar o destino: acha o caminho com "
                     "menos arestas, como a busca em largura, gastando só a memória de um caminho.",
        "estrutura": "pilha",
        "usa_pesos": "nao",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "obrigatorio",
        "usa_limite": False,
    },
    {
        "chave": LARGURA,
        "nome": "Largura (BFS)",
        "nome_curto": "BFS",
        "descricao": "Explora em camadas a partir da origem: primeiro os vizinhos, depois os vizinhos dos "
                     "vizinhos. Acha o menor número de arestas até cada vértice.",
        "estrutura": "fila",
        "usa_pesos": "nao",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "opcional",
        "usa_limite": False,
    },
    {
        "chave": BIDIRECIONAL,
        "nome": "Bidirecional",
        "nome_curto": "Bidirecional",
        "descricao": "Duas buscas em largura ao mesmo tempo, uma saindo da origem e outra do destino, até se "
                     "encontrarem no meio: examina bem menos vértices que uma busca só.",
        "estrutura": "duas filas",
        "usa_pesos": "nao",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "obrigatorio",
        "usa_limite": False,
    },
    {
        "chave": DIJKSTRA,
        "nome": "Dijkstra (custo uniforme)",
        "nome_curto": "Dijkstra",
        "descricao": "Caminho de menor custo a partir da origem: sempre sai da fila o vértice de menor "
                     "distância. Os pesos não podem ser negativos.",
        "estrutura": "fila de prioridade",
        "usa_pesos": "sim",
        "negativos": False,
        "usa_heuristica": False,
        "destino": "opcional",
        "usa_limite": False,
    },
    {
        "chave": BELLMAN_FORD,
        "nome": "Bellman-Ford",
        "nome_curto": "Bellman-Ford",
        "descricao": "Caminho de menor custo mesmo com pesos negativos: relaxa todas as arestas |V| − 1 "
                     "vezes e depois confere se existe ciclo negativo.",
        "estrutura": "rodadas",
        "usa_pesos": "sim",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "opcional",
        "usa_limite": False,
    },
    {
        "chave": FLOYD_WARSHALL,
        "nome": "Floyd-Warshall (todos os pares)",
        "nome_curto": "Floyd-Warshall",
        "descricao": "Menor custo entre TODOS os pares de vértices, numa matriz: na rodada de cada vértice k, "
                     "cada par pergunta se passar por k fica mais barato. Aceita pesos negativos.",
        "estrutura": "matriz",
        "usa_pesos": "sim",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "opcional",
        "usa_limite": False,
    },
    {
        "chave": GULOSA,
        "nome": "Gulosa (melhor primeiro)",
        "nome_curto": "Gulosa",
        "descricao": "Vai sempre para o vértice que parece mais perto do destino (menor h). É rápida, "
                     "mas não garante o caminho de menor custo.",
        "estrutura": "fila de prioridade",
        "usa_pesos": "opcional",
        "negativos": False,
        "usa_heuristica": True,
        "destino": "obrigatorio",
        "usa_limite": False,
    },
    {
        "chave": A_ESTRELA,
        "nome": "A* (A estrela)",
        "nome_curto": "A*",
        "descricao": "Escolhe pelo menor f = g + h: o custo até aqui mais a estimativa até o destino. "
                     "Com h admissível, acha o caminho de menor custo.",
        "estrutura": "fila de prioridade",
        "usa_pesos": "sim",
        "negativos": False,
        "usa_heuristica": True,
        "destino": "obrigatorio",
        "usa_limite": False,
    },
    {
        "chave": PRIM,
        "nome": "Prim (árvore mínima)",
        "nome_curto": "Prim",
        "descricao": "Cresce uma árvore a partir da raiz: a cada passo entra o vértice mais barato de ligar (a aresta "
                     "mais leve que sai da árvore). Parece o Dijkstra, mas a prioridade é o peso da aresta, não a "
                     "distância.",
        "estrutura": "fila de prioridade",
        "usa_pesos": "sim",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "nao",
        "usa_limite": False,
        "so_nao_orientado": True,
    },
    {
        "chave": KRUSKAL,
        "nome": "Kruskal (árvore mínima)",
        "nome_curto": "Kruskal",
        "descricao": "Olha as arestas da mais leve para a mais pesada: aceita a que liga duas partes diferentes e "
                     "recusa a que fecharia um ciclo. Os conjuntos disjuntos dizem quem já está ligado com quem.",
        "estrutura": "conjuntos disjuntos",
        "usa_pesos": "sim",
        "negativos": True,
        "usa_heuristica": False,
        "destino": "nao",
        "usa_limite": False,
        "usa_origem": False,
        "so_nao_orientado": True,
    },
]


# Os TIPOS de busca: a tela inicial mostra as buscas agrupadas assim (em sanfona) e o editor também
# (na etapa Busca). "cor" é o nome de uma cor do tema (visual/tema.py), igual nos dois temas.
TIPOS_DE_BUSCA = [
    {"titulo": "Sem pesos", "subtitulo": "Seguem as ligações do grafo", "cor": "parte_vertices",
     "buscas": [PROFUNDIDADE, LIMITADA, ITERATIVA, LARGURA, BIDIRECIONAL],
     "explicacao": "Estas buscas só olham as ligações: de cada vértice, vão para os vizinhos. O que muda entre "
                   "elas é a ORDEM das visitas: a profundidade vai fundo primeiro (usa uma pilha) e a largura "
                   "visita em camadas (usa uma fila). Servem para percorrer o grafo, achar caminhos com menos "
                   "arestas e descobrir a estrutura dele (ciclos, componentes, ordem topológica)."},
    {"titulo": "Menor custo", "subtitulo": "Somam os pesos do caminho", "cor": "parte_pesos",
     "buscas": [DIJKSTRA, BELLMAN_FORD, FLOYD_WARSHALL],
     "explicacao": "Aqui cada aresta tem um peso (uma distância, um tempo, um custo) e o melhor caminho é o de "
                   "menor SOMA de pesos, não o de menos arestas. O Dijkstra é o mais rápido, mas não aceita "
                   "peso negativo; o Bellman-Ford aceita e ainda descobre ciclo negativo; o Floyd-Warshall "
                   "calcula de uma vez a menor distância entre todos os pares."},
    {"titulo": "Com heurística", "subtitulo": "Estimam quanto falta até o destino", "cor": "parte_adjacencia",
     "buscas": [GULOSA, A_ESTRELA],
     "explicacao": "Além do grafo, estas buscas usam uma ESTIMATIVA h de quanto falta até o destino (como a "
                   "distância em linha reta num mapa). A gulosa vai sempre para quem parece mais perto; o A* "
                   "soma o que já andou com o que falta (g + h) e, se a estimativa nunca exagera, acha o "
                   "caminho de menor custo."},
    {"titulo": "Árvore geradora mínima", "subtitulo": "Ligam todos os vértices pelo menor peso",
     "cor": "parte_incidencia",
     "buscas": [PRIM, KRUSKAL],
     "explicacao": "Aqui não se procura um caminho: o objetivo é escolher arestas que liguem TODOS os vértices sem "
                   "formar ciclo (uma árvore), com a menor soma de pesos possível. Serve para projetar redes "
                   "gastando o mínimo (cabos, estradas, canos). O Prim cresce uma árvore só, sempre pela aresta "
                   "mais leve que sai dela; o Kruskal junta pedaços, da aresta mais leve para a mais pesada. Os "
                   "dois chegam ao mesmo peso total."},
]


# Como cada busca usa os pesos, em poucas palavras (as etiquetas da tela inicial e do editor)
TEXTO_DOS_PESOS = {"nao": "não usa pesos", "sim": "precisa de pesos", "opcional": "pesos opcionais"}


# Os fatos de uma busca, um por etiqueta: ["pilha", "não usa pesos", "precisa de destino"]
def fatos(informacoes):
    partes = [informacoes["estrutura"], TEXTO_DOS_PESOS[informacoes["usa_pesos"]]]
    if informacoes["usa_pesos"] != "nao" and informacoes["negativos"]:
        partes.append("aceita negativos")
    if informacoes["usa_heuristica"]:
        partes.append("heurística h")
    if informacoes["usa_limite"]:
        partes.append("limite de profundidade")
    if informacoes["destino"] == "obrigatorio":
        partes.append("precisa de destino")
    if informacoes.get("so_nao_orientado"):
        partes.append("só não orientado")
    return partes


# Em qual tipo (a posição na lista TIPOS_DE_BUSCA) uma busca está
def tipo_da_busca(chave):
    for indice in range(len(TIPOS_DE_BUSCA)):
        if chave in TIPOS_DE_BUSCA[indice]["buscas"]:
            return indice
    return 0


# O dicionário de uma busca a partir da chave (chave desconhecida -> a busca em profundidade)
def algoritmo(chave):
    for informacoes in ALGORITMOS:
        if informacoes["chave"] == chave:
            return informacoes
    return ALGORITMOS[0]


def existe(chave):
    for informacoes in ALGORITMOS:
        if informacoes["chave"] == chave:
            return True
    return False


# Os nomes que aparecem na lista do editor, na ordem da lista ALGORITMOS
def nomes():
    lista = []
    for informacoes in ALGORITMOS:
        lista.append(informacoes["nome"])
    return lista


def chave_pelo_nome(nome):
    for informacoes in ALGORITMOS:
        if informacoes["nome"] == nome:
            return informacoes["chave"]
    return PROFUNDIDADE


# ----------------------------------------------------------------------
# O que falta para visualizar
# ----------------------------------------------------------------------

# Confere se a busca escolhida pode rodar neste grafo.
# Devolve (problemas, avisos), duas listas de textos:
#   problemas -> impedem a visualização (por exemplo, Dijkstra com peso negativo);
#   avisos    -> não impedem, mas ajudam a entender (por exemplo, "a BFS ignora os pesos").
#   limite    -> o limite de profundidade (só a busca limitada usa)
#   ordenar   -> se as listas vão ser ordenadas (muda a ordem da busca limitada, e por isso
#                quantos nós ela gera até achar o destino)
def conferir(chave, vertices, arestas, direcionado, inicio, destino, heuristica, limite=None, ordenar=True):
    informacoes = algoritmo(chave)
    nome = informacoes["nome_curto"]
    problemas = []
    avisos = []
    if not vertices:
        problemas.append("Crie pelo menos um vértice.")
        return problemas, avisos

    # Limite de profundidade (busca limitada)
    if informacoes["usa_limite"]:
        if limite is None or isinstance(limite, bool) or not isinstance(limite, int):
            problemas.append("A busca limitada precisa de um limite de profundidade (um número inteiro): "
                             "escolha em \"Limite\".")
        elif limite < 0 or limite > MAIOR_LIMITE:
            problemas.append(f"O limite de profundidade vai de 0 a {MAIOR_LIMITE}.")

    # Tamanho: o Floyd-Warshall faz n³ comparações
    if chave == FLOYD_WARSHALL and len(vertices) > MAXIMO_FLOYD:
        problemas.append(f"O Floyd-Warshall compara todos os pares em cada rodada (n³ = {len(vertices) ** 3} "
                         f"comparações com {len(vertices)} vértices): use no máximo {MAXIMO_FLOYD} vértices.")

    # Árvore geradora mínima (Prim e Kruskal): só no grafo não orientado, em que a aresta liga os dois
    # lados, sem sentido
    if informacoes.get("so_nao_orientado") and direcionado:
        problemas.append(f"O {nome} monta uma árvore geradora mínima, que é para grafos não orientados: torne o grafo "
                         f"não orientado (na etapa Arestas do editor, ou na parte Tipo do grafo).")

    # Destino
    if informacoes["destino"] == "obrigatorio" and destino not in vertices:
        problemas.append(f"A busca {nome} precisa de um destino: escolha em \"Destino\".")

    # Pesos das arestas
    sem_peso = len(entrada.indices_sem_peso(arestas))
    if informacoes["usa_pesos"] == "sim" and sem_peso > 0:
        problemas.append(f"{nome} usa os pesos das arestas, mas "
                         + entrada.contar(sem_peso, "aresta está sem peso", "arestas estão sem peso")
                         + ": dê pesos a elas (na parte Pesos, ou no botão Pesos… do editor).")
    negativas = entrada.arestas_com_peso_negativo(arestas, direcionado)
    if negativas and informacoes["usa_pesos"] != "nao" and not informacoes["negativos"]:
        problemas.append(f"{nome} não aceita peso negativo ({', '.join(negativas[:3])}): "
                         f"use Bellman-Ford ou troque o peso.")
    if negativas and informacoes["chave"] in (BELLMAN_FORD, FLOYD_WARSHALL) and not direcionado:
        avisos.append("No não orientado, uma aresta de peso negativo já forma um ciclo negativo "
                      f"(A — B — A): o {nome} vai apontar isso.")
    if informacoes["usa_pesos"] == "nao" and entrada.tem_pesos(arestas):
        avisos.append(f"A busca {nome} ignora os pesos: ela só olha quem é vizinho de quem.")
    if informacoes["usa_pesos"] == "opcional" and sem_peso > 0 and arestas:
        avisos.append("Sem peso em todas as arestas, o resultado conta o caminho em arestas (e não em custo).")

    # Heurística dos vértices
    if informacoes["usa_heuristica"]:
        faltando = []
        for vertice in vertices:
            if vertice not in heuristica:
                faltando.append(vertice)
        if faltando:
            exemplos = ", ".join(faltando[:4])
            if len(faltando) > 4:
                exemplos += "…"
            problemas.append(f"{nome} usa a heurística h dos vértices, mas "
                             + entrada.contar(len(faltando), "vértice está sem h", "vértices estão sem h")
                             + f" ({exemplos}): dê h a eles (na parte Pesos, botão Heurística h…).")
        elif destino in vertices and not problemas:
            avisos = avisos + avisos_da_heuristica(vertices, arestas, direcionado, destino, heuristica)

    # Busca limitada e aprofundamento iterativo: quantos nós a árvore de busca vai ter
    if chave in (LIMITADA, ITERATIVA) and not problemas:
        origem = inicio if inicio in vertices else sorted(vertices)[0]
        nos = contar_nos(chave, vertices, arestas, direcionado, ordenar, origem, destino, limite)
        if nos > LIMITE_DE_NOS:
            if chave == LIMITADA:
                problemas.append(f"Com limite {limite}, a busca geraria mais de {LIMITE_DE_NOS} nós (o mesmo vértice "
                                 f"entra no caminho várias vezes, por caminhos diferentes): diminua o limite.")
            else:
                problemas.append(f"Até achar o destino, as rodadas gerariam mais de {LIMITE_DE_NOS} nós: o grafo "
                                 f"tem ligações demais para o aprofundamento iterativo (use a largura ou a "
                                 f"bidirecional).")
        elif chave == ITERATIVA and inicio == destino:
            avisos.append("A origem já é o destino: a primeira rodada (limite 0) já acha.")
    if chave == FLOYD_WARSHALL and not problemas and destino in vertices:
        avisos.append("Com origem e destino, o resultado mostra também o caminho entre os dois.")
    if informacoes.get("so_nao_orientado") and not problemas:
        partes = contar_partes(vertices, arestas)
        if partes > 1:
            avisos.append(f"O grafo tem {partes} partes desligadas: nenhuma árvore liga todos os vértices. O resultado "
                          f"vai ser uma floresta geradora mínima (uma árvore mínima em cada parte).")
    return problemas, avisos


# ----------------------------------------------------------------------
# Árvore geradora mínima (Prim e Kruskal)
# ----------------------------------------------------------------------

# Quantas partes desligadas (componentes conexas) o grafo tem, sem olhar o sentido das arestas.
# É uma busca em largura simples, repetida a partir de cada vértice que ainda não foi alcançado.
def contar_partes(vertices, arestas):
    vizinhos = lista_de_vizinhos(vertices, arestas, False, False)
    alcancados = set()
    partes = 0
    for vertice in vertices:
        if vertice in alcancados:
            continue
        partes += 1                     # um vértice que nenhuma parte anterior alcançou: começa outra parte
        alcancados.add(vertice)
        fila = [vertice]
        while fila:
            atual = fila.pop(0)
            for vizinho in vizinhos[atual]:
                if vizinho not in alcancados:
                    alcancados.add(vizinho)
                    fila.append(vizinho)
    return partes


# ----------------------------------------------------------------------
# A árvore da busca limitada (para saber o tamanho antes de rodar)
# ----------------------------------------------------------------------

# As listas de vizinhos como o Grafo monta: na ordem de criação das arestas (no não orientado, a
# aresta entra nas duas listas, menos o laço) e, se ordenar, em ordem alfabética
def lista_de_vizinhos(vertices, arestas, direcionado, ordenar):
    lista = {}
    for vertice in vertices:
        lista[vertice] = []
    for origem, destino, nome, peso in arestas:
        lista[origem].append(destino)
        if not direcionado and origem != destino:
            lista[destino].append(origem)
    if ordenar:
        for vertice in lista:
            lista[vertice].sort()
    return lista


# Quantos nós (entradas no caminho) a busca limitada gera, ou as rodadas do aprofundamento
# iterativo somadas. Para de contar quando passa de LIMITE_DE_NOS (devolve LIMITE_DE_NOS + 1).
def contar_nos(chave, vertices, arestas, direcionado, ordenar, origem, destino, limite):
    lista = lista_de_vizinhos(vertices, arestas, direcionado, ordenar)
    if chave == LIMITADA:
        contagem = {"nos": 0}
        simular_limitada(lista, origem, destino, limite, [], contagem)
        return contagem["nos"]
    total = 0
    limite = 0
    while True:
        contagem = {"nos": 0}
        resultado = simular_limitada(lista, origem, destino, limite, [], contagem)
        total += contagem["nos"]
        if total > LIMITE_DE_NOS or resultado != "corte":
            return total
        limite += 1


# A mesma recursão de classes/busca_limitada.py, só contando (sem anotar passos)
def simular_limitada(lista, vertice, destino, restante, caminho, contagem):
    contagem["nos"] += 1
    if contagem["nos"] > LIMITE_DE_NOS:
        return "parou"
    if vertice == destino:
        return "achou"
    if restante == 0:
        return "corte"
    caminho.append(vertice)
    houve_corte = False
    for vizinho in lista[vertice]:
        if vizinho in caminho:
            continue
        resultado = simular_limitada(lista, vizinho, destino, restante - 1, caminho, contagem)
        if resultado in ("achou", "parou"):
            caminho.pop()
            return resultado
        if resultado == "corte":
            houve_corte = True
    caminho.pop()
    if houve_corte:
        return "corte"
    return "falha"


# ----------------------------------------------------------------------
# Custo real até o destino (usado pela heurística e pelas conferências do A*)
# ----------------------------------------------------------------------

# O menor custo de cada vértice ATÉ o destino, calculado por um Dijkstra "de trás para frente":
# começa no destino e anda pelas arestas ao contrário (no orientado, A -> B vira B -> A).
# Precisa de pesos em todas as arestas e sem negativos; senão devolve None.
# Vértice que não chega ao destino fica com custo infinito.
# (Esta conta não aparece na visualização: é uma ferramenta para gerar e conferir a heurística.)
def custos_ate_o_destino(vertices, arestas, destino, direcionado):
    if destino not in vertices:
        return None
    for origem, chegada, nome, peso in arestas:
        if peso is None or peso < 0:
            return None

    # Lista de adjacência ao contrário: chegam[v] = (quem chega em v, peso)
    chegam = {}
    for vertice in vertices:
        chegam[vertice] = []
    for origem, chegada, nome, peso in arestas:
        chegam[chegada].append((origem, peso))
        if not direcionado:
            chegam[origem].append((chegada, peso))

    custo = {}
    for vertice in vertices:
        custo[vertice] = entrada.INFINITO
    custo[destino] = entrada.Decimal(0)
    finalizados = []
    while len(finalizados) < len(vertices):
        # O vértice ainda não finalizado de menor custo
        menor = None
        for vertice in vertices:
            if vertice not in finalizados and (menor is None or custo[vertice] < custo[menor]):
                menor = vertice
        if custo[menor] == entrada.INFINITO:
            break                       # os que sobraram não chegam ao destino
        finalizados.append(menor)
        for vizinho, peso in chegam[menor]:
            if custo[menor] + peso < custo[vizinho]:
                custo[vizinho] = custo[menor] + peso
    return custo


# Avisos sobre a heurística de um A* ou de uma busca gulosa:
# - admissível = nunca passa do custo real até o destino (h(v) <= custo real);
# - o destino deveria ter h = 0 (já chegou: não falta nada).
def avisos_da_heuristica(vertices, arestas, direcionado, destino, heuristica):
    avisos = []
    if heuristica.get(destino, 0) != 0:
        avisos.append(f"h({destino}) deveria ser 0: o destino já chegou.")
    custo = custos_ate_o_destino(vertices, arestas, destino, direcionado)
    if custo is None:
        return avisos
    exageros = violacoes_de_admissibilidade(vertices, heuristica, custo)
    if exageros:
        vertice, h, real = exageros[0]
        texto = (f"h({vertice}) = {entrada.formatar_numero(h)} passa do custo real até {destino} "
                 f"({entrada.formatar_numero(real)}): a heurística não é admissível")
        if len(exageros) > 1:
            texto += f" (e mais {len(exageros) - 1})"
        avisos.append(texto + ", então o A* pode errar o caminho de menor custo.")
    return avisos


# Os vértices em que h passa do custo real: [(vértice, h, custo real), ...]
def violacoes_de_admissibilidade(vertices, heuristica, custo):
    violacoes = []
    for vertice in vertices:
        if vertice in heuristica and heuristica[vertice] > custo[vertice]:
            violacoes.append((vertice, heuristica[vertice], custo[vertice]))
    return violacoes


# Os pares em que h não é consistente: h(u) > peso(u, v) + h(v) (a estimativa "cai" mais do que
# o custo da aresta). Consistente => admissível, e o A* nunca precisa reabrir um vértice.
def violacoes_de_consistencia(arestas, direcionado, heuristica):
    violacoes = []
    for origem, destino, nome, peso in arestas:
        sentidos = [(origem, destino)]
        if not direcionado:
            sentidos.append((destino, origem))
        for u, v in sentidos:
            if u in heuristica and v in heuristica and peso is not None:
                if heuristica[u] > peso + heuristica[v]:
                    violacoes.append((u, v))
    return violacoes
