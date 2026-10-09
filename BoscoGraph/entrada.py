'''
    Entrada do grafo: nomes dos vértices, pesos, sorteios, leitura de arestas digitadas e edição.
    Tudo aqui é Python puro (sem Tkinter): o editor usa estas funções e os testes também.

    Um grafo é representado por duas listas (e, se for o caso, um dicionário de heurísticas):
      vertices   -> nomes dos vértices, por exemplo ["A", "B", "C"]
      arestas    -> quartetos (origem, destino, nome, peso), por exemplo
                    [("A", "B", "e1", Decimal("5")), ("B", "C", "", None)]
                    (nome "" = aresta sem nome; peso None = aresta sem peso)
      heuristica -> h(v) de cada vértice, usada pela busca gulosa e pelo A*,
                    por exemplo {"A": Decimal("7"), "B": Decimal("3")}
'''

import random
import re
from decimal import Decimal

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAXIMO_DE_VERTICES = 26             # mais que isso não cabe de forma legível no círculo
LIMITE_DE_ARESTAS = 60              # acima disso o desenho fica poluído demais para a aula
TAMANHO_MAXIMO_DO_VERTICE = 10      # caracteres no nome de um vértice
TAMANHO_MAXIMO_DA_ARESTA = 16       # caracteres no nome de uma aresta

# Pesos: números com até 3 casas decimais, entre -1.000.000 e 1.000.000.
# São guardados como Decimal (e não float) para as somas serem exatas: no float,
# 0.1 + 0.2 dá 0.30000000000000004, e um Dijkstra acharia que 0,3 "melhorou" 0,3.
MAIOR_PESO = Decimal("1000000")
CASAS_DECIMAIS = 3
# O infinito do Decimal: qualquer número é menor que ele, e infinito + 5 continua infinito.
# É o "∞" do pseudocódigo (v.d = ∞ antes de a busca alcançar v).
INFINITO = Decimal("Infinity")

# Estilos de nome para gerar vértices: (chave, texto que aparece na tela)
ESTILOS_DE_NOME = [
    ("letras", "Letras (A, B, C...)"),
    ("numeros", "Números (1, 2, 3...)"),
    ("prefixo", "Prefixo + número (R1, R2...)"),
]


# ----------------------------------------------------------------------
# Vértices
# ----------------------------------------------------------------------

# Gera os nomes em sequência. Com 10 ou mais vértices, os números ganham zero à esquerda
# (01, 02, ..., 12). Motivo: a ordenação é alfabética, ou seja, compara TEXTO, e no texto
# "10" vem antes de "2" (o "1" vem antes do "2"). Já "02" vem antes de "10", como esperado.
def nomes_dos_vertices(quantidade, estilo="letras", prefixo="R"):
    digitos = len(str(quantidade))                  # 8 -> 1 dígito; 12 -> 2 dígitos
    nomes = []
    for i in range(quantidade):
        numero = str(i + 1).zfill(digitos)          # zfill completa com zeros à esquerda: "2" -> "02"
        if estilo == "letras":
            nomes.append(LETRAS[i])
        elif estilo == "numeros":
            nomes.append(numero)
        else:
            nomes.append(prefixo + numero)
    return nomes


# Devolve "" se o nome de vértice serve, ou a explicação do problema.
# Só letras, números e "_": assim o nome nunca se confunde com os separadores
# do texto das arestas ("A->B: e1", separadas por vírgula).
def validar_nome_de_vertice(nome, existentes):
    if nome == "":
        return "O nome do vértice não pode ficar vazio."
    if len(nome) > TAMANHO_MAXIMO_DO_VERTICE:
        return f"O nome do vértice pode ter no máximo {TAMANHO_MAXIMO_DO_VERTICE} caracteres."
    for caractere in nome:
        # isalnum() = é letra ou número (inclusive letras com acento, como "ã")
        if not caractere.isalnum() and caractere != "_":
            if caractere == " ":
                return "O nome do vértice não pode ter espaço (use _ no lugar)."
            return f"O nome do vértice só pode ter letras, números e _ (o '{caractere}' não pode)."
    if nome in existentes:
        return f"Já existe um vértice chamado {nome}."
    return ""


# Nome de aresta é opcional (vazio = sem nome). Vírgula, ponto e vírgula, dois pontos e "="
# são proibidos porque separam as partes do texto das arestas ("A -> B: e1 = 5").
def validar_nome_de_aresta(nome):
    if len(nome) > TAMANHO_MAXIMO_DA_ARESTA:
        return f"O nome da aresta pode ter no máximo {TAMANHO_MAXIMO_DA_ARESTA} caracteres."
    for caractere in nome:
        if caractere in ",;:":
            return f"O nome da aresta não pode ter '{caractere}' (ele separa as arestas no texto)."
        if caractere == "=":
            return "O nome da aresta não pode ter '=' (ele separa o peso no texto)."
        if not caractere.isprintable():
            return "O nome da aresta não pode ter quebra de linha nem tabulação."
    return ""


# Sugere o nome do próximo vértice, seguindo o padrão do último:
#   ["A", "B"] -> "C";   ["R1", "R2"] -> "R3";   ["01", "02"] -> "03";   [] -> "A"
def proximo_nome_livre(vertices):
    if vertices:
        ultimo = vertices[-1]
        # Separa o número do fim do nome: "R07" -> prefixo "R" e número "07"
        corte = len(ultimo)
        while corte > 0 and ultimo[corte - 1] in "0123456789":
            corte -= 1
        prefixo = ultimo[:corte]
        numero = ultimo[corte:]
        if numero != "":
            valor = int(numero) + 1
            while True:
                candidato = prefixo + str(valor).zfill(len(numero))    # mantém os zeros: "07" -> "08"
                if candidato not in vertices:
                    break
                valor += 1
            if validar_nome_de_vertice(candidato, vertices) == "":
                return candidato
    # Sem número no fim: a primeira letra que ainda não foi usada
    for letra in LETRAS:
        if letra not in vertices:
            return letra
    return ""


# Troca o nome de um vértice na lista de vértices e em todas as arestas que usam esse vértice
def renomear_vertice(vertices, arestas, antigo, novo):
    novos_vertices = []
    for vertice in vertices:
        if vertice == antigo:
            novos_vertices.append(novo)
        else:
            novos_vertices.append(vertice)
    novas_arestas = []
    for origem, destino, nome, peso in arestas:
        if origem == antigo:
            origem = novo
        if destino == antigo:
            destino = novo
        novas_arestas.append((origem, destino, nome, peso))
    return novos_vertices, novas_arestas


# Remove um vértice e todas as arestas que saem dele ou chegam nele
def remover_vertice(vertices, arestas, removido):
    novos_vertices = []
    for vertice in vertices:
        if vertice != removido:
            novos_vertices.append(vertice)
    return novos_vertices, manter_arestas_validas(novos_vertices, arestas)


# Fica só com as arestas cujos dois vértices ainda existem
def manter_arestas_validas(vertices, arestas):
    validas = []
    for origem, destino, nome, peso in arestas:
        if origem in vertices and destino in vertices:
            validas.append((origem, destino, nome, peso))
    return validas


# ----------------------------------------------------------------------
# A quantidade de vértices (o contador "Quantidade" do editor)
# ----------------------------------------------------------------------

# O estilo dos nomes, se eles forem exatamente a sequência de um estilo: "letras" (A, B, C...),
# "numeros" (1, 2, 3... ou 01, 02, ... 12) ou None (nomes próprios, como Arad e Sibiu, ou grafo vazio)
def estilo_dos_nomes(vertices):
    if not vertices:
        return None
    for estilo in ("letras", "numeros"):
        if vertices == nomes_dos_vertices(len(vertices), estilo):
            return estilo
    return None


# O primeiro nome do estilo que ainda não existe. "total" é quantos vértices o grafo vai ter:
# com 10 ou mais, os números ganham o zero à esquerda (como em nomes_dos_vertices).
def proximo_nome_do_estilo(existentes, estilo, total):
    if estilo == "letras":
        for letra in LETRAS:
            if letra not in existentes:
                return letra
        return ""
    digitos = len(str(total))
    numero = 1
    while str(numero).zfill(digitos) in existentes:
        numero += 1
    return str(numero).zfill(digitos)


# Os vértices com a quantidade nova, aproveitando os que já existem:
#  - nomes na sequência do estilo (A, B, C... ou 1, 2, 3...): a sequência é refeita com a quantidade nova.
#    De 9 para 10 vértices, "1".."9" viram "01".."09" (para a ordem alfabética continuar certa);
#  - nomes próprios: os que sobram saem do FIM da lista e os novos ganham o próximo nome livre do estilo.
# Devolve a lista nova e o "mapa" de cada nome antigo que continua no grafo -> o nome novo dele
# (quem não está no mapa saiu do grafo).
def vertices_para_a_quantidade(vertices, quantidade, estilo):
    mapa = {}
    if not vertices or estilo_dos_nomes(vertices) == estilo:
        novos = nomes_dos_vertices(quantidade, estilo)
        for i in range(min(len(vertices), quantidade)):
            mapa[vertices[i]] = novos[i]        # o i-ésimo vértice continua sendo o i-ésimo
        return novos, mapa
    novos = list(vertices[:quantidade])
    while len(novos) < quantidade:
        novos.append(proximo_nome_do_estilo(novos, estilo, quantidade))
    for nome in novos:
        if nome in vertices:
            mapa[nome] = nome
    return novos, mapa


# Os mesmos vértices com os nomes de outro estilo, na mesma ordem (A, B, C -> 1, 2, 3)
def renomear_para_o_estilo(vertices, estilo):
    novos = nomes_dos_vertices(len(vertices), estilo)
    mapa = {}
    for i in range(len(vertices)):
        mapa[vertices[i]] = novos[i]
    return novos, mapa


# As arestas com os nomes do mapa (antigo -> novo); as que usam um vértice fora do mapa saem
def renomear_arestas(arestas, mapa):
    novas = []
    for origem, destino, nome, peso in arestas:
        if origem in mapa and destino in mapa:
            novas.append((mapa[origem], mapa[destino], nome, peso))
    return novas


# Um dicionário "por vértice" com os nomes do mapa (as chaves fora do mapa saem)
def renomear_chaves(dicionario, mapa):
    novo_dicionario = {}
    for chave in dicionario:
        if chave in mapa:
            novo_dicionario[mapa[chave]] = dicionario[chave]
    return novo_dicionario


# Dicionários "por vértice" (a heurística h, as posições do desenho): quando um vértice muda
# de nome, a chave muda junto; quando ele sai do grafo, a chave sai também.
def renomear_chave(dicionario, antigo, novo):
    novo_dicionario = {}
    for chave in dicionario:
        if chave == antigo:
            novo_dicionario[novo] = dicionario[chave]
        else:
            novo_dicionario[chave] = dicionario[chave]
    return novo_dicionario


def manter_chaves(dicionario, vertices):
    novo_dicionario = {}
    for chave in dicionario:
        if chave in vertices:
            novo_dicionario[chave] = dicionario[chave]
    return novo_dicionario


# ----------------------------------------------------------------------
# O grafo da Prova 01 (vira o modelo padrão)
# ----------------------------------------------------------------------

# 16 roteadores e 24 links, com 1 laço (A, A) e 2 arestas paralelas (B, C)
def grafo_da_prova():
    vertices = nomes_dos_vertices(16)
    pares = [
        ("A", "A"), ("A", "B"),
        ("B", "C"), ("B", "C"), ("B", "D"),
        ("C", "D"), ("C", "E"),
        ("D", "E"),
        ("E", "F"), ("E", "H"),
        ("F", "G"),
        ("G", "H"),
        ("H", "I"), ("H", "K"),
        ("I", "J"),
        ("J", "K"),
        ("K", "L"), ("K", "N"),
        ("L", "M"),
        ("M", "N"),
        ("N", "B"), ("N", "O"),
        ("O", "P"),
        ("P", "A"),
    ]
    arestas = []
    for origem, destino in pares:
        arestas.append((origem, destino, "", None))
    return vertices, arestas


# ----------------------------------------------------------------------
# Orientado ou não orientado
# ----------------------------------------------------------------------

# A "chave" de uma aresta para saber se duas arestas ligam o mesmo par de vértices:
# - orientado: o par é ordenado, então A -> B e B -> A são pares diferentes;
# - não orientado: o par não tem ordem, então A — B e B — A são o MESMO par
#   (a chave coloca os dois nomes em ordem alfabética: ("B", "A") vira ("A", "B")).
def chave_do_par(origem, destino, direcionado):
    if direcionado or origem <= destino:
        return (origem, destino)
    return (destino, origem)


# ----------------------------------------------------------------------
# Pesos (das arestas) e heurística (dos vértices)
# ----------------------------------------------------------------------

# Lê um número digitado: "5", "-2", "3,5" ou "3.5" (vírgula ou ponto para os decimais).
# Devolve (numero, problema): o número como Decimal e "" se deu certo; texto vazio = (None, "")
# (sem peso); se não der, (None, explicação do problema).
def ler_numero(texto):
    texto = texto.strip()
    if texto == "":
        return None, ""
    # fullmatch = o texto INTEIRO tem que seguir o padrão: sinal opcional, dígitos e,
    # se tiver, vírgula ou ponto seguido de mais dígitos ("1.000,5" e "2e3" não passam)
    if re.fullmatch(r"[+-]?\d+([.,]\d+)?", texto) is None:
        return None, f"'{texto}' não é um número (exemplos: 5, -2, 3,5)."
    numero = Decimal(texto.replace(",", "."))
    casas = 0
    if "." in texto or "," in texto:
        casas = len(re.split(r"[.,]", texto)[1])
    if casas > CASAS_DECIMAIS:
        return None, f"Use no máximo {CASAS_DECIMAIS} casas decimais ('{texto}' tem {casas})."
    if abs(numero) > MAIOR_PESO:
        return None, f"Use um número entre -{formatar_numero(MAIOR_PESO)} e {formatar_numero(MAIOR_PESO)}."
    return numero, ""


# O caminho inverso: o número como aparece na tela. Decimal("2.50") -> "2,5"; Decimal("3") -> "3";
# infinito -> "∞"; None (sem peso) -> "". A vírgula é a do português.
def formatar_numero(valor):
    if valor is None:
        return ""
    valor = Decimal(valor)               # aceita também int (a busca em largura conta arestas: 0, 1, 2...)
    if valor.is_infinite():
        if valor < 0:
            return "-∞"
        return "∞"
    if valor == valor.to_integral_value():
        return str(int(valor))           # 3.000 -> "3" (e -0 -> "0")
    # normalize() tira os zeros do fim (2.50 -> 2.5); format "f" nunca usa notação científica
    texto = format(valor.normalize(), "f")
    return texto.replace(".", ",")


# Há alguma aresta com peso? (com isso o grafo é "valorado", ao menos em parte)
def tem_pesos(arestas):
    for origem, destino, nome, peso in arestas:
        if peso is not None:
            return True
    return False


# As posições (na lista de arestas) das arestas que ainda não têm peso
def indices_sem_peso(arestas):
    indices = []
    for i in range(len(arestas)):
        if arestas[i][3] is None:
            indices.append(i)
    return indices


# As arestas com peso negativo, no texto das mensagens: ["A -> B (-2)", ...]
def arestas_com_peso_negativo(arestas, direcionado=True):
    ligacao = "->"
    if not direcionado:
        ligacao = "—"
    lista = []
    for origem, destino, nome, peso in arestas:
        if peso is not None and peso < 0:
            lista.append(f"{origem} {ligacao} {destino} ({formatar_numero(peso)})")
    return lista


# Troca o peso das arestas que estão nas posições "indices".
# pesos: um peso para cada posição, na mesma ordem (None = tirar o peso)
def trocar_pesos(arestas, indices, pesos):
    novas = list(arestas)                # list(...) faz uma cópia: a lista original não muda
    for i in range(len(indices)):
        origem, destino, nome, peso_antigo = novas[indices[i]]
        novas[indices[i]] = (origem, destino, nome, pesos[i])
    return novas


# Sorteia "quantidade" números inteiros de "minimo" até "maximo" (os dois inclusive)
def sortear_numeros(quantidade, minimo, maximo, semente=None):
    sorteio = random.Random(semente)
    numeros = []
    for i in range(quantidade):
        numeros.append(Decimal(sorteio.randint(int(minimo), int(maximo))))
    return numeros


# Troca a heurística dos vértices escolhidos (um valor para cada; None = tirar a heurística)
def trocar_heuristicas(heuristica, vertices_escolhidos, valores):
    nova = dict(heuristica)
    for i in range(len(vertices_escolhidos)):
        if valores[i] is None:
            nova.pop(vertices_escolhidos[i], None)       # pop com padrão None: não dá erro se não existir
        else:
            nova[vertices_escolhidos[i]] = valores[i]
    return nova


# ----------------------------------------------------------------------
# Sorteios (a mesma semente sempre gera o mesmo resultado; semente None = cada vez um)
# ----------------------------------------------------------------------

# Quantas arestas cabem com essa quantidade de vértices.
# Pares de vértices diferentes: n x (n - 1) no orientado (A -> B e B -> A contam separado)
# e n x (n - 1) / 2 no não orientado (A — B é um par só).
def maximo_de_arestas(quantidade_vertices, permitir_lacos, permitir_paralelas, direcionado=True):
    total = quantidade_vertices * (quantidade_vertices - 1)    # pares (origem, destino) com origem diferente do destino
    if not direcionado:
        total = total // 2                                     # no não orientado, cada par conta uma vez só
    if permitir_lacos:
        total = total + quantidade_vertices                    # mais um laço por vértice
    if permitir_paralelas:
        total = total * 2                                      # cada par pode aparecer até 2 vezes
    return min(total, LIMITE_DE_ARESTAS)


# Quantos vizinhos um vértice pode ter na sua lista de adjacência
def maximo_de_vizinhos(quantidade_vertices, permitir_lacos, permitir_paralelas):
    total = quantidade_vertices - 1
    if permitir_lacos:
        total = total + 1
    if permitir_paralelas:
        total = total * 2
    return total


# O máximo de vizinhos por vértice no sorteio das listas, respeitando também o limite
# total de arestas (26 vértices x 3 vizinhos = 78 arestas: passaria do limite de 60)
def limite_de_vizinhos(quantidade_vertices, permitir_lacos, permitir_paralelas):
    if quantidade_vertices == 0:
        return 0
    return min(maximo_de_vizinhos(quantidade_vertices, permitir_lacos, permitir_paralelas),
               LIMITE_DE_ARESTAS // quantidade_vertices)


# Sorteia uma quantidade total de arestas entre os vértices dados (as arestas sorteadas vêm sem peso)
def arestas_aleatorias(vertices, quantidade, permitir_lacos, permitir_paralelas, semente=None, direcionado=True):
    sorteio = random.Random(semente)
    # Nunca pede mais do que cabe: sem isso, o while abaixo nunca terminaria
    quantidade = min(quantidade, maximo_de_arestas(len(vertices), permitir_lacos, permitir_paralelas, direcionado))
    pares = []
    repeticoes_do_par = {}
    while len(pares) < quantidade:
        origem = sorteio.choice(vertices)
        destino = sorteio.choice(vertices)
        if origem == destino and not permitir_lacos:
            continue
        chave = chave_do_par(origem, destino, direcionado)
        repeticoes = repeticoes_do_par.get(chave, 0)
        if repeticoes == 1 and not permitir_paralelas:
            continue
        if repeticoes == 2:
            continue                                           # no máximo 2 arestas paralelas por par
        repeticoes_do_par[chave] = repeticoes + 1
        pares.append((origem, destino))
    arestas = []
    for origem, destino in pares:
        arestas.append((origem, destino, "", None))
    return arestas


# Sorteia a lista de adjacência de cada vértice: cada um escolhe entre "minimo" e "maximo" vizinhos.
# Os vizinhos saem em ordem aleatória, o que deixa visível o efeito de ordenar (ou não) as listas.
# No não orientado, a aresta escolhida por A também aparece na lista do vizinho, e um par
# que já foi escolhido por um lado não pode ser escolhido de novo pelo outro (a não ser como paralela).
def listas_aleatorias(vertices, minimo, maximo, permitir_lacos, permitir_paralelas, semente=None, direcionado=True):
    sorteio = random.Random(semente)
    arestas = []
    repeticoes_do_par = {}
    limite_por_par = 1
    if permitir_paralelas:
        limite_por_par = 2                                     # cada par pode aparecer até 2 vezes (aresta paralela)
    for origem in vertices:
        possiveis = []
        for destino in vertices:
            if destino == origem and not permitir_lacos:
                continue
            ja_usadas = repeticoes_do_par.get(chave_do_par(origem, destino, direcionado), 0)
            for vez in range(limite_por_par - ja_usadas):      # quantas vezes ainda pode ser sorteado
                possiveis.append(destino)
        maior = min(maximo, len(possiveis))                    # não dá para sortear mais do que existe
        menor = min(minimo, maior)
        quantidade = sorteio.randint(menor, maior)
        for destino in sorteio.sample(possiveis, quantidade):
            arestas.append((origem, destino, "", None))
            chave = chave_do_par(origem, destino, direcionado)
            repeticoes_do_par[chave] = repeticoes_do_par.get(chave, 0) + 1
    return arestas


# Dá nomes em sequência para as arestas: e1, e2, e3... (os pesos continuam como estavam)
def numerar_arestas(arestas):
    numeradas = []
    for i in range(len(arestas)):
        origem, destino, nome, peso = arestas[i]
        numeradas.append((origem, destino, f"e{i + 1}", peso))
    return numeradas


# Tira o nome de todas as arestas (os pesos continuam como estavam)
def arestas_sem_nome(arestas):
    sem_nome = []
    for origem, destino, nome, peso in arestas:
        sem_nome.append((origem, destino, "", peso))
    return sem_nome


# ----------------------------------------------------------------------
# Arestas em texto
# ----------------------------------------------------------------------

# Lê arestas digitadas: "A B", "A->B" ou "A-B", com nome opcional depois de ":" ("A->B: e1")
# e peso opcional depois de "=" ("A->B = 5" ou "A->B: e1 = 2,5").
# Separadas por vírgula, ponto e vírgula ou quebra de linha.
# criar_vertices=False: os vértices precisam existir.
# criar_vertices=True: vértice que não existe é criado (se o nome for válido).
# Devolve: as arestas lidas, a lista de problemas e os vértices novos (na ordem em que apareceram).
def ler_arestas(texto, vertices, criar_vertices=False):
    arestas = []
    problemas = []
    novos = []
    # A vírgula também separa as arestas. Por isso, ANTES de separar, a vírgula decimal do peso
    # vira ponto: depois de um "=", "2,5" (vírgula colada nos dígitos) é o número 2.5.
    # \s* = espaços opcionais; os parênteses guardam os pedaços que \1 e \2 repetem na troca.
    texto = re.sub(r"=\s*([+-]?\d+),(\d)", r"= \1.\2", texto)
    texto = texto.replace("\n", ",").replace(";", ",")
    for trecho in texto.split(","):
        trecho = trecho.strip()
        if trecho == "":
            continue
        resto = trecho
        peso = None
        if "=" in resto:
            resto, texto_do_peso = resto.split("=", 1)
            peso, problema = ler_numero(texto_do_peso)
            if problema == "" and peso is None:
                problema = "faltou o peso depois do ="
            if problema:
                problemas.append(f"'{trecho}': {problema}")
                continue
        nome = ""
        par = resto
        if ":" in resto:
            par, nome = resto.split(":", 1)         # o 1 separa só no primeiro ":"
            nome = nome.strip()
        partes = par.replace("->", " ").replace("-", " ").split()
        if len(partes) != 2:
            problemas.append(f"'{trecho}' não está no formato A->B")
            continue
        origem, destino = partes

        existentes = list(vertices) + novos
        # Ajuda com letras minúsculas: "a b" vira "A B" se existirem os vértices A e B
        if origem not in existentes and origem.upper() in existentes:
            origem = origem.upper()
        if destino not in existentes and destino.upper() in existentes:
            destino = destino.upper()

        faltando = []
        for vertice in (origem, destino):
            if vertice not in existentes and vertice not in faltando:
                faltando.append(vertice)
        if faltando and not criar_vertices:
            problemas.append(f"'{trecho}': não existe o vértice {', '.join(faltando)}")
            continue

        problema = validar_nome_de_aresta(nome)
        for vertice in faltando:
            if problema == "":
                problema = validar_nome_de_vertice(vertice, existentes)
        if problema == "" and len(existentes) + len(faltando) > MAXIMO_DE_VERTICES:
            problema = f"passaria do limite de {MAXIMO_DE_VERTICES} vértices"
        if problema:
            problemas.append(f"'{trecho}': {problema}")
            continue

        for vertice in faltando:
            novos.append(vertice)
        arestas.append((origem, destino, nome, peso))
    return arestas, problemas, novos


# O caminho inverso do ler_arestas: uma aresta por linha, no formato "A -> B: nome = peso"
# (no não orientado, "A - B: nome = peso"; os dois formatos são lidos pelo ler_arestas)
def texto_das_arestas(arestas, direcionado=True):
    ligacao = "->"
    if not direcionado:
        ligacao = "-"
    linhas = []
    for origem, destino, nome, peso in arestas:
        linha = f"{origem} {ligacao} {destino}"
        if nome:
            linha += f": {nome}"
        if peso is not None:
            linha += f" = {formatar_numero(peso)}"
        linhas.append(linha)
    return "\n".join(linhas)


# ----------------------------------------------------------------------
# Informações sobre o grafo
# ----------------------------------------------------------------------

# Grau de saída (quantas arestas saem) e grau de entrada (quantas chegam) de cada vértice.
# Um laço conta 1 na saída e 1 na entrada do mesmo vértice.
def graus(vertices, arestas):
    grau_saida = {}
    grau_entrada = {}
    for vertice in vertices:
        grau_saida[vertice] = 0
        grau_entrada[vertice] = 0
    for origem, destino, nome, peso in arestas:
        grau_saida[origem] += 1
        grau_entrada[destino] += 1
    return grau_saida, grau_entrada


# Grau no não orientado: quantas pontas de aresta tocam o vértice.
# Um laço tem as duas pontas no mesmo vértice, então conta 2 (como o "2" na matriz de incidência).
def graus_nao_orientados(vertices, arestas):
    grau = {}
    for vertice in vertices:
        grau[vertice] = 0
    for origem, destino, nome, peso in arestas:
        grau[origem] += 1
        grau[destino] += 1
    return grau


# Quantas vezes cada par aparece: mais de 1 vez = arestas paralelas
# (no não orientado, A — B e B — A são o mesmo par)
def contar_pares(arestas, direcionado=True):
    quantidade_do_par = {}
    for origem, destino, nome, peso in arestas:
        par = chave_do_par(origem, destino, direcionado)
        quantidade_do_par[par] = quantidade_do_par.get(par, 0) + 1
    return quantidade_do_par


# Uma observação curta para cada aresta, na mesma ordem: "laço", "paralela", "laço, paralela" ou ""
def observacoes(arestas, direcionado=True):
    quantidade_do_par = contar_pares(arestas, direcionado)
    lista = []
    for origem, destino, nome, peso in arestas:
        partes = []
        if origem == destino:
            partes.append("laço")
        if quantidade_do_par[chave_do_par(origem, destino, direcionado)] > 1:
            partes.append("paralela")
        lista.append(", ".join(partes))
    return lista


# "1 vértice", mas "2 vértices": escolhe a palavra certa para a quantidade
def contar(quantidade, singular, plural):
    if quantidade == 1:
        return f"1 {singular}"
    return f"{quantidade} {plural}"


# Resumo em texto: "16 vértices · 24 arestas · 1 laço · 2 arestas paralelas"
# (paralelas = as arestas que repetem o mesmo par; na prova, as duas B -> C)
def resumo(vertices, arestas, direcionado=True):
    quantidade_do_par = contar_pares(arestas, direcionado)
    lacos = 0
    paralelas = 0
    for origem, destino, nome, peso in arestas:
        if origem == destino:
            lacos += 1
        if quantidade_do_par[chave_do_par(origem, destino, direcionado)] > 1:
            paralelas += 1

    texto = contar(len(vertices), "vértice", "vértices") + " · " + contar(len(arestas), "aresta", "arestas")
    if lacos > 0:
        texto += " · " + contar(lacos, "laço", "laços")
    if paralelas > 0:
        texto += " · " + contar(paralelas, "aresta paralela", "arestas paralelas")
    return texto
