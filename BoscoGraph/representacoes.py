'''
    As representações do grafo que a tela (e o relatório em PDF) mostram, calculadas a partir das
    listas de vértices e arestas, nas convenções dos slides da aula (CCC-GRAFOS-03):

    Matriz de adjacência (n × n, linha = vértice de onde sai, coluna = vértice onde chega):
      - "contagem": quantas arestas ligam i a j. No não orientado a matriz é simétrica e o LAÇO conta 1
        na diagonal (slide 11); arestas paralelas somam (slide 12). No orientado, a linha é a origem
        (a "outra forma" do slide 10).
      - "sinais" (só no orientado, a "uma forma" do slide 9): M[i][j] = −1 para cada aresta que SAI de i
        para j e +1 para cada aresta que CHEGA em i vinda de j.
      - "pesos": o peso no lugar do 1, vazio onde não há aresta (slide 13). Com arestas paralelas
        valoradas a matriz padrão não dá conta (slide 14): aqui aparecem os pesos separados por "|".

    Matriz de incidência (n × m, uma coluna por aresta):
      - "sinais": no não orientado, 1 nas duas pontas (o laço vale 2, slide 18); no orientado, −1 onde a
        aresta sai e +1 onde chega (slide 17). Laço orientado: "±1" (sai e chega no mesmo vértice).
      - "pesos": o peso no lugar do 1 (slide 20); no orientado, −peso onde sai e +peso onde chega.

    Lista de adjacência "de entrada" (quem CHEGA em cada vértice) e estatísticas dos pesos.

    Cada matriz vem como um dicionário:
      "linhas", "colunas"  -> os nomes que aparecem nos cabeçalhos
      "celulas"            -> {(linha, coluna): texto}  (posições a partir de 0; texto "" = vazio)
      "arestas"            -> {(linha, coluna): [números das arestas que formam aquela célula]}
    Este arquivo não usa Tkinter: os testes conferem tudo sem abrir janela.
'''

from entrada import formatar_numero

MODOS_DA_ADJACENCIA_NAO_ORIENTADA = [("contagem", "Contagem"), ("pesos", "Pesos")]
MODOS_DA_ADJACENCIA_ORIENTADA = [("contagem", "0 e 1"), ("sinais", "−1 e +1"), ("pesos", "Pesos")]
MODOS_DA_INCIDENCIA = [("sinais", "1 e −1"), ("pesos", "Pesos")]


# Os modos que fazem sentido para a matriz de adjacência (o "−1 e +1" só existe no orientado)
def modos_da_adjacencia(direcionado):
    if direcionado:
        return MODOS_DA_ADJACENCIA_ORIENTADA
    return MODOS_DA_ADJACENCIA_NAO_ORIENTADA


# Um número com sinal explícito: +1, −1, +2,5 (o "−" é o sinal de menos tipográfico, como nos slides)
def com_sinal(numero):
    if numero > 0:
        return "+" + formatar_numero(numero)
    if numero < 0:
        return "−" + formatar_numero(-numero)
    return "0"


def matriz_de_adjacencia(vertices, arestas, direcionado, modo="contagem"):
    if modo == "sinais" and not direcionado:
        modo = "contagem"
    posicao = {}
    for indice in range(len(vertices)):
        posicao[vertices[indice]] = indice

    # Primeiro junta, para cada célula, as arestas que caem nela
    arestas_da_celula = {}
    for linha in range(len(vertices)):
        for coluna in range(len(vertices)):
            arestas_da_celula[(linha, coluna)] = []
    for numero in range(len(arestas)):
        origem, destino, nome, peso = arestas[numero]
        i = posicao[origem]
        j = posicao[destino]
        arestas_da_celula[(i, j)].append(numero)
        if (not direcionado or modo == "sinais") and i != j:
            arestas_da_celula[(j, i)].append(numero)       # vale nos dois sentidos (ou o +1 de quem chega)

    celulas = {}
    for celula in arestas_da_celula:
        i, j = celula
        numeros = arestas_da_celula[celula]
        if modo == "pesos":
            textos = []
            for numero in numeros:
                peso = arestas[numero][3]
                textos.append(formatar_numero(peso) if peso is not None else "?")
            celulas[celula] = " | ".join(textos)            # vazio quando não há aresta
        elif modo == "sinais":
            soma = 0
            for numero in numeros:
                origem, destino, nome, peso = arestas[numero]
                if origem == vertices[i] and destino == vertices[j]:
                    soma -= 1                               # sai de i (e chega em j)
                if destino == vertices[i] and origem == vertices[j] and i != j:
                    soma += 1                               # chega em i (vindo de j)
            if i == j and numeros:
                celulas[celula] = "±" + str(len(numeros))   # laço: sai e chega no mesmo vértice
            else:
                celulas[celula] = com_sinal(soma)
        else:
            celulas[celula] = str(len(numeros))
    return {"linhas": list(vertices), "colunas": list(vertices), "celulas": celulas, "arestas": arestas_da_celula,
            "modo": modo}


# O nome da coluna de cada aresta na matriz de incidência: o nome dela, ou e1, e2... pela ordem
def nome_da_coluna(arestas, numero):
    nome = arestas[numero][2]
    if nome:
        return nome
    return f"e{numero + 1}"


def matriz_de_incidencia(vertices, arestas, direcionado, modo="sinais"):
    posicao = {}
    for indice in range(len(vertices)):
        posicao[vertices[indice]] = indice
    colunas = []
    for numero in range(len(arestas)):
        colunas.append(nome_da_coluna(arestas, numero))
    celulas = {}
    arestas_da_celula = {}
    for linha in range(len(vertices)):
        for numero in range(len(arestas)):
            celulas[(linha, numero)] = "0"
            arestas_da_celula[(linha, numero)] = []
    for numero in range(len(arestas)):
        origem, destino, nome, peso = arestas[numero]
        i = posicao[origem]
        j = posicao[destino]
        arestas_da_celula[(i, numero)] = [numero]
        arestas_da_celula[(j, numero)] = [numero]
        valor = 1
        if modo == "pesos":
            valor = peso
        if valor is None:
            texto = "?"                                     # pesos pedidos, mas esta aresta não tem
            celulas[(i, numero)] = texto
            celulas[(j, numero)] = texto
            continue
        if not direcionado:
            if i == j:
                celulas[(i, numero)] = formatar_numero(2 * valor)       # o laço toca o vértice duas vezes
            else:
                celulas[(i, numero)] = formatar_numero(valor)
                celulas[(j, numero)] = formatar_numero(valor)
        elif i == j:
            celulas[(i, numero)] = "±" + formatar_numero(valor)        # sai e chega no mesmo vértice
        else:
            celulas[(i, numero)] = com_sinal(-valor)                    # sai de i
            celulas[(j, numero)] = com_sinal(valor)                     # chega em j
    return {"linhas": list(vertices), "colunas": colunas, "celulas": celulas, "arestas": arestas_da_celula,
            "modo": modo}


# Quem CHEGA em cada vértice (a lista de adjacência "ao contrário"), na ordem de criação das arestas;
# cada item é (vizinho, peso, número da aresta). No não orientado é a mesma lista de saída.
def lista_de_entrada(vertices, arestas, direcionado, ordenar=False):
    lista = {}
    for vertice in vertices:
        lista[vertice] = []
    for numero in range(len(arestas)):
        origem, destino, nome, peso = arestas[numero]
        lista[destino].append((origem, peso, numero))
        if not direcionado and origem != destino:
            lista[origem].append((destino, peso, numero))
    if ordenar:
        for vertice in lista:
            lista[vertice].sort(key=primeiro_item)
    return lista


# Quem SAI de cada vértice, no mesmo formato (é a lista que o Grafo monta)
def lista_de_saida(vertices, arestas, direcionado, ordenar=False):
    lista = {}
    for vertice in vertices:
        lista[vertice] = []
    for numero in range(len(arestas)):
        origem, destino, nome, peso = arestas[numero]
        lista[origem].append((destino, peso, numero))
        if not direcionado and origem != destino:
            lista[destino].append((origem, peso, numero))
    if ordenar:
        for vertice in lista:
            lista[vertice].sort(key=primeiro_item)
    return lista


def primeiro_item(item):
    return item[0]


# Estatísticas dos pesos: quantas arestas têm peso, menor, maior, soma, média, mediana e desvio padrão
# (o desvio padrão populacional: raiz da média dos quadrados das diferenças para a média).
# Devolve None se nenhuma aresta tiver peso.
def estatisticas_dos_pesos(arestas):
    pesos = []
    for origem, destino, nome, peso in arestas:
        if peso is not None:
            pesos.append(peso)
    if not pesos:
        return None
    soma = 0
    for peso in pesos:
        soma += peso
    media = soma / len(pesos)
    ordenados = sorted(pesos)
    meio = len(ordenados) // 2
    if len(ordenados) % 2 == 1:
        mediana = ordenados[meio]
    else:
        mediana = (ordenados[meio - 1] + ordenados[meio]) / 2
    quadrados = 0
    for peso in pesos:
        quadrados += (peso - media) * (peso - media)
    desvio = (quadrados / len(pesos)).sqrt()
    negativos = 0
    for peso in pesos:
        if peso < 0:
            negativos += 1
    return {"quantidade": len(pesos), "sem_peso": len(arestas) - len(pesos), "menor": ordenados[0],
            "maior": ordenados[-1], "soma": soma, "media": media, "mediana": mediana, "desvio": desvio,
            "negativos": negativos}


# Um número com no máximo 2 casas (para médias e desvios: 2,33 e não 2,333333...)
def arredondado(numero):
    return formatar_numero(numero.quantize(type(numero)("0.01")).normalize())


# A densidade do grafo: quantas arestas existem, comparado com o máximo de um grafo simples
# (n(n−1) no orientado, n(n−1)/2 no não orientado). Devolve um número de 0 a 1 (ou None com n < 2).
def densidade(quantidade_de_vertices, quantidade_de_arestas, direcionado):
    n = quantidade_de_vertices
    if n < 2:
        return None
    maximo = n * (n - 1)
    if not direcionado:
        maximo = maximo // 2
    return quantidade_de_arestas / maximo
