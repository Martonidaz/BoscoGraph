'''
    Conferências automáticas do BoscoGraph, sem mostrar a janela (a seção 12 monta as telas com a
    janela escondida).
    Rode com: python testes.py
    Se algo estiver errado, o assert para o programa e mostra a mensagem.

    Além do grafo da prova, os testes sorteiam centenas de grafos (com nomes
    livres nos vértices e nas arestas) e conferem propriedades que a teoria
    garante para qualquer busca em profundidade.
'''

import math
import random
from decimal import Decimal
import tempfile
from pathlib import Path

import entrada
import modelos
from boscograph import montar_passos
from visual.estado import EstadoVisual
from visual import desenho


# ----------------------------------------------------------------------
# Funções de apoio
# ----------------------------------------------------------------------

def contar_tipos(passos):
    contagem = {}
    for passo in passos:
        tipo = passo["tipo"]
        if tipo not in contagem:
            contagem[tipo] = 0
        contagem[tipo] += 1
    return contagem


def tempos(passos):
    tempo_d = {}
    tempo_f = {}
    for passo in passos:
        if passo["tipo"] == "descobrir":
            tempo_d[passo["vertice"]] = passo["tempo"]
        if passo["tipo"] == "finalizar":
            tempo_f[passo["vertice"]] = passo["tempo"]
    return tempo_d, tempo_f


def arestas_examinadas(passos):
    lista = []
    for passo in passos:
        if passo["tipo"] == "examinar":
            lista.append((passo["origem"], passo["destino"], passo["classe"]))
    return lista


def estado_final(passos, direcionado=True):
    arestas = []
    for passo in passos:
        if passo["tipo"] == "criar_aresta":
            arestas.append((passo["origem"], passo["destino"], passo["nome"], passo["peso"]))
    estado = EstadoVisual(arestas, direcionado)
    for passo in passos:
        estado.aplicar(passo)
    return estado


# O passo da etapa 6 com esse tipo (por exemplo "tipo_ciclo"), ou None
def passo_do_tipo(passos, tipo):
    for passo in passos:
        if passo["tipo"] == tipo:
            return passo
    return None


# União-busca (union-find), outro algoritmo que não tem nada a ver com a DFS:
# junta os vértices ligados em grupos. Se uma aresta liga dois vértices que já estão no
# mesmo grupo (ou é um laço), ela fecha um ciclo. No fim, cada grupo é uma componente conexa.
def componentes_e_ciclo_nao_orientado(vertices, arestas):
    grupo = {}
    for vertice in vertices:
        grupo[vertice] = vertice

    def chefe(vertice):             # sobe até o vértice que representa o grupo
        while grupo[vertice] != vertice:
            vertice = grupo[vertice]
        return vertice

    tem_ciclo = False
    for origem, destino, nome, peso in arestas:
        a = chefe(origem)
        b = chefe(destino)
        if a == b:
            tem_ciclo = True
        else:
            grupo[a] = b
    chefes = []
    grupo_do_vertice = {}
    for vertice in vertices:
        grupo_do_vertice[vertice] = chefe(vertice)
        if chefe(vertice) not in chefes:
            chefes.append(chefe(vertice))
    return len(chefes), tem_ciclo, grupo_do_vertice


# Confere se a lista [v0, v1, ..., v0] é mesmo um ciclo do grafo: fecha no começo e cada
# passo usa uma aresta que existe (no orientado, no sentido certo)
def eh_ciclo(ciclo, arestas, direcionado):
    if len(ciclo) < 2 or ciclo[0] != ciclo[-1]:
        return False
    for posicao in range(len(ciclo) - 1):
        a = ciclo[posicao]
        b = ciclo[posicao + 1]
        existe = False
        for origem, destino, nome, peso in arestas:
            if (origem, destino) == (a, b) or (not direcionado and (origem, destino) == (b, a)):
                existe = True
        if not existe:
            return False
    return True


# Algoritmo de Kahn (ordenação topológica), que não tem nada a ver com a DFS:
# vai tirando vértices sem nenhuma aresta chegando; se sobrar algum, o grafo tem ciclo.
def tem_ciclo(vertices, arestas):
    chegando = {}
    for vertice in vertices:
        chegando[vertice] = 0
    for origem, destino, nome, peso in arestas:
        chegando[destino] += 1
    fila = []
    for vertice in vertices:
        if chegando[vertice] == 0:
            fila.append(vertice)
    removidos = 0
    while fila:
        vertice = fila.pop()
        removidos += 1
        for origem, destino, nome, peso in arestas:
            if origem == vertice:
                chegando[destino] -= 1
                if chegando[destino] == 0:
                    fila.append(destino)
    return removidos < len(vertices)


# Um nome de vértice sorteado, só com letras, números e _ (como o editor aceita)
def nome_aleatorio(sorteio):
    caracteres = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzãçé0123456789_"
    tamanho = sorteio.randint(1, entrada.TAMANHO_MAXIMO_DO_VERTICE)
    nome = ""
    for i in range(tamanho):
        nome += sorteio.choice(caracteres)
    return nome


# ----------------------------------------------------------------------
# 1. O grafo da prova continua dando exatamente o resultado da prova
# ----------------------------------------------------------------------

vertices, arestas = entrada.grafo_da_prova()
passos = montar_passos(vertices, arestas, True, "A")
contagem = contar_tipos(passos)
assert contagem["criar_vertice"] == 16 and contagem["criar_aresta"] == 24
assert contagem["pintar_branco"] == 16, "cada vértice é pintado de Branco uma vez"
assert contagem["descobrir"] == 16 and contagem["finalizar"] == 16
assert contagem["examinar"] == 24, "cada aresta é examinada uma vez: O(|V| + |E|)"

tempo_d, tempo_f = tempos(passos)
for i in range(16):
    letra = vertices[i]
    assert tempo_d[letra] == i + 1 and tempo_f[letra] == 32 - i, f"tempos de {letra} diferentes da prova"

tipos = {"arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0}
for origem, destino, classe in arestas_examinadas(passos):
    tipos[classe] += 1
assert tipos == {"arvore": 15, "retorno": 3, "avanco": 6, "cruzamento": 0}, tipos

# Antes da busca os vértices ficam sem cor; depois da pintura, todos Brancos
estado = EstadoVisual(arestas)
for passo in passos:
    if passo["tipo"] == "pintar_branco":
        assert estado.cor[passo["vertice"]] is None, "antes de pintar, o vértice está sem cor"
    estado.aplicar(passo)
    if passo["tipo"] == "zerar_tempo":
        for letra in vertices:
            assert estado.cor[letra] == "Branco", "depois da pintura, todos estão Brancos"

# O modelo "Prova 01" que vem na pasta modelos é exatamente o grafo da prova
do_modelo = modelos.carregar_modelo("Prova 01")
assert (do_modelo["vertices"], do_modelo["arestas"]) == entrada.grafo_da_prova(), "o modelo da prova mudou"
assert do_modelo["ordenar"] is True and do_modelo["inicio"] == "A" and do_modelo["direcionado"] is True
assert do_modelo["algoritmo"] == "profundidade" and do_modelo["heuristica"] == {}, "arquivo antigo: valores padrão"

# A classificação pedida na Parte 1 da prova
assert passo_do_tipo(passos, "tipo_resumo")["resumo"] == \
    "orientado · não simples · não completo · não valorado · cíclico · não é DAG"
assert passo_do_tipo(passos, "tipo_simples")["mensagem"] == "Simples: não, tem laço em A e arestas paralelas B -> C"
ciclo = passo_do_tipo(passos, "tipo_ciclo")
assert ciclo["retorno"] == ("N", "B") and eh_ciclo(ciclo["ciclo"], arestas, True), ciclo
print("1. Grafo da prova: igual ao resultado da prova (e o modelo Prova 01 também)")


# ----------------------------------------------------------------------
# 2. Nomes, validações e edição
# ----------------------------------------------------------------------

assert entrada.nomes_dos_vertices(3) == ["A", "B", "C"]
assert entrada.nomes_dos_vertices(3, "numeros") == ["1", "2", "3"]
assert entrada.nomes_dos_vertices(12, "numeros")[:2] == ["01", "02"], "10 ou mais: zero à esquerda"
assert entrada.nomes_dos_vertices(10, "prefixo", "R")[-1] == "R10"
# Com o zero à esquerda, a ordem alfabética (de texto) fica igual à ordem dos números
numeros = entrada.nomes_dos_vertices(12, "numeros")
assert sorted(numeros) == numeros

assert entrada.validar_nome_de_vertice("SP", []) == ""
assert entrada.validar_nome_de_vertice("São_Paulo", []) == "", "acentos e _ são aceitos"
assert entrada.validar_nome_de_vertice("", []) != ""
assert "espaço" in entrada.validar_nome_de_vertice("A B", [])
assert entrada.validar_nome_de_vertice("A-B", []) != "", "o '-' separa as arestas no texto"
assert entrada.validar_nome_de_vertice("A:B", []) != ""
assert entrada.validar_nome_de_vertice("ABCDEFGHIJK", []) != "", "mais de 10 caracteres"
assert "Já existe" in entrada.validar_nome_de_vertice("A", ["A"])
assert entrada.validar_nome_de_aresta("") == "", "aresta sem nome é permitida"
assert entrada.validar_nome_de_aresta("link SP-RJ") == ""
assert entrada.validar_nome_de_aresta("a:b") != "" and entrada.validar_nome_de_aresta("a,b") != ""
assert entrada.validar_nome_de_aresta("x" * 17) != ""
assert "peso" in entrada.validar_nome_de_aresta("a=b"), "o '=' separa o peso no texto"

vertices, arestas = entrada.renomear_vertice(["A", "B"], [("A", "A", "l", None), ("A", "B", "", None)], "A", "SP")
assert vertices == ["SP", "B"] and arestas == [("SP", "SP", "l", None), ("SP", "B", "", None)]
vertices, arestas = entrada.remover_vertice(["A", "B", "C"], [("A", "B", "", None), ("B", "C", "", None), ("C", "C", "", None)], "C")
assert vertices == ["A", "B"] and arestas == [("A", "B", "", None)]

assert entrada.proximo_nome_livre([]) == "A"
assert entrada.proximo_nome_livre(["A", "B"]) == "C"
assert entrada.proximo_nome_livre(["A", "C"]) == "B"
assert entrada.proximo_nome_livre(["R1", "R2"]) == "R3"
assert entrada.proximo_nome_livre(["08", "09"]) == "10"
assert entrada.proximo_nome_livre(["R07", "R08"]) == "R09", "mantém os zeros à esquerda"
assert entrada.proximo_nome_livre(["X1", "X2", "X1b"]) == "A"

# A Quantidade do editor: a sequência é refeita (de 9 para 10, "1".."9" viram "01".."09", com as arestas);
# com nomes próprios, os novos entram no fim com o próximo nome livre do estilo
assert entrada.estilo_dos_nomes(list("ABC")) == "letras" and entrada.estilo_dos_nomes(["1", "2"]) == "numeros"
assert entrada.estilo_dos_nomes(["01", "02"]) is None and entrada.estilo_dos_nomes([]) is None
assert entrada.estilo_dos_nomes(["A", "C"]) is None, "pulou o B: não é a sequência"
novos, mapa = entrada.vertices_para_a_quantidade([str(numero) for numero in range(1, 10)], 10, "numeros")
assert novos == [f"{numero:02d}" for numero in range(1, 11)] and mapa["1"] == "01" and mapa["9"] == "09"
novos, mapa = entrada.vertices_para_a_quantidade(list("ABCDE"), 3, "letras")
assert novos == list("ABC") and mapa == {"A": "A", "B": "B", "C": "C"}
novos, mapa = entrada.vertices_para_a_quantidade(["Arad", "Sibiu"], 4, "letras")
assert novos == ["Arad", "Sibiu", "A", "B"] and mapa == {"Arad": "Arad", "Sibiu": "Sibiu"}
novos, mapa = entrada.vertices_para_a_quantidade(["Arad", "A"], 11, "numeros")
assert novos[:3] == ["Arad", "A", "01"] and novos[-1] == "09" and len(novos) == 11
novos, mapa = entrada.vertices_para_a_quantidade(["Arad", "Sibiu", "Zerind"], 1, "letras")
assert novos == ["Arad"] and mapa == {"Arad": "Arad"}
assert entrada.vertices_para_a_quantidade([], 3, "numeros") == (["1", "2", "3"], {})
assert entrada.renomear_para_o_estilo(list("AB"), "numeros") == (["1", "2"], {"A": "1", "B": "2"})
assert entrada.proximo_nome_do_estilo(["A", "C"], "letras", 3) == "B"
assert entrada.proximo_nome_do_estilo(["01"], "numeros", 12) == "02"
assert entrada.renomear_arestas([("A", "B", "e1", None), ("B", "C", "", Decimal(2))], {"A": "1", "B": "2"}) == \
    [("1", "2", "e1", None)], "a aresta com o C (que saiu) sai junto"
assert entrada.renomear_chaves({"A": 1, "C": 3}, {"A": "1", "B": "2"}) == {"1": 1}

# Leitura das arestas digitadas, com nomes e com criação de vértices
lidas, problemas, novos = entrada.ler_arestas("A B, b->c: e2\nC-D; AB C, A=>B, A->Z", ["A", "B", "C", "D"])
assert lidas == [("A", "B", "", None), ("B", "C", "e2", None), ("C", "D", "", None)], lidas
assert len(problemas) == 3 and novos == [], problemas
lidas, problemas, novos = entrada.ler_arestas("A -> Z9: via 1\nZ9 -> W", ["A"], criar_vertices=True)
assert lidas == [("A", "Z9", "via 1", None), ("Z9", "W", "", None)] and novos == ["Z9", "W"] and problemas == []
lidas, problemas, novos = entrada.ler_arestas("A -> B-C", ["A"], criar_vertices=True)
assert problemas != [], "três partes não formam uma aresta"
# Texto e leitura são inversos: escrever e ler de volta dá as mesmas arestas
vertices, arestas = entrada.grafo_da_prova()
arestas = entrada.numerar_arestas(arestas)
lidas, problemas, novos = entrada.ler_arestas(entrada.texto_das_arestas(arestas), vertices)
assert lidas == arestas and problemas == [] and novos == []
assert entrada.arestas_sem_nome(arestas) == entrada.grafo_da_prova()[1]

grau_saida, grau_entrada = entrada.graus(vertices, arestas)
assert sum(grau_saida.values()) == 24 and sum(grau_entrada.values()) == 24, "soma dos graus = número de arestas"
assert grau_saida["B"] == 3 and grau_entrada["A"] == 2
assert entrada.observacoes([("A", "A", "", None), ("A", "B", "", None), ("A", "B", "", None), ("B", "A", "", None)]) == \
    ["laço", "paralela", "paralela", ""]
assert entrada.resumo(*entrada.grafo_da_prova()) == "16 vértices · 24 arestas · 1 laço · 2 arestas paralelas"
assert entrada.resumo(["A"], [("A", "A", "", None)]) == "1 vértice · 1 aresta · 1 laço"

assert entrada.maximo_de_arestas(5, False, False) == 20     # 5 * 4 pares possíveis
assert entrada.maximo_de_arestas(5, True, False) == 25      # mais 5 laços
assert entrada.maximo_de_arestas(3, False, True) == 12      # 3 * 2 pares, cada um até 2 vezes
assert entrada.maximo_de_arestas(3, True, True) == 18       # (6 pares + 3 laços) * 2
assert entrada.maximo_de_arestas(26, True, True) == entrada.LIMITE_DE_ARESTAS
assert entrada.maximo_de_vizinhos(4, True, True) == 8       # (3 outros + ele mesmo) * 2
assert entrada.limite_de_vizinhos(26, False, False) == 2, "26 x 2 = 52 cabe em 60; 26 x 3 = 78 não"
assert entrada.limite_de_vizinhos(3, False, False) == 2
# Pesos: vírgula ou ponto, até 3 casas, guardados como Decimal (somas exatas)
assert entrada.ler_numero("5") == (Decimal(5), "")
assert entrada.ler_numero(" -2,5 ") == (Decimal("-2.5"), "")
assert entrada.ler_numero("0.125") == (Decimal("0.125"), "")
assert entrada.ler_numero("") == (None, ""), "vazio = sem peso"
for ruim in ("abc", "1.000,5", "2e3", "1,2345", "5,", ",5", "1000001", "--1"):
    assert entrada.ler_numero(ruim)[0] is None and entrada.ler_numero(ruim)[1] != "", ruim
assert entrada.ler_numero("0,1")[0] + entrada.ler_numero("0,2")[0] == entrada.ler_numero("0,3")[0], \
    "com Decimal, 0,1 + 0,2 é exatamente 0,3 (no float daria 0.30000000000000004)"
assert [entrada.formatar_numero(x) for x in (Decimal("2.50"), Decimal("3.000"), Decimal("-0"), Decimal("-1.25"),
        entrada.INFINITO, None, 7)] == ["2,5", "3", "0", "-1,25", "∞", "", "7"]
assert entrada.INFINITO + 5 == entrada.INFINITO and Decimal(10 ** 6) < entrada.INFINITO

# Arestas com peso no texto: "A -> B: nome = peso" (vírgula decimal depois do "=")
lidas, problemas, novos = entrada.ler_arestas("A->B = 2,5, B->C: e2 = -1\nC - A = 3.25; A B=7", ["A", "B", "C"])
assert problemas == [], problemas
assert lidas == [("A", "B", "", Decimal("2.5")), ("B", "C", "e2", Decimal(-1)), ("C", "A", "", Decimal("3.25")),
                 ("A", "B", "", Decimal(7))], lidas
lidas, problemas, novos = entrada.ler_arestas("A->B =, A->B = x, A->B = 1,2345", ["A", "B"])
assert lidas == [] and len(problemas) == 3, problemas
com_pesos = [("A", "B", "e1", Decimal("2.5")), ("B", "C", "", Decimal(-3)), ("C", "A", "x", None)]
for direcionado in (True, False):
    texto = entrada.texto_das_arestas(com_pesos, direcionado)
    assert entrada.ler_arestas(texto, ["A", "B", "C"]) == (com_pesos, [], []), texto
assert entrada.texto_das_arestas(com_pesos).split("\n")[0] == "A -> B: e1 = 2,5"
assert entrada.numerar_arestas(com_pesos)[1] == ("B", "C", "e2", Decimal(-3)), "numerar mantém o peso"
assert entrada.arestas_sem_nome(com_pesos)[0] == ("A", "B", "", Decimal("2.5")), "limpar nomes mantém o peso"
assert entrada.renomear_vertice(["A", "B", "C"], com_pesos, "A", "Z")[1][0] == ("Z", "B", "e1", Decimal("2.5"))
assert entrada.indices_sem_peso(com_pesos) == [2] and entrada.tem_pesos(com_pesos)
assert entrada.arestas_com_peso_negativo(com_pesos) == ["B -> C (-3)"]
assert entrada.trocar_pesos(com_pesos, [0, 2], [None, Decimal(1)]) == \
    [("A", "B", "e1", None), ("B", "C", "", Decimal(-3)), ("C", "A", "x", Decimal(1))]
sorteados = entrada.sortear_numeros(200, 1, 9, 5)
assert min(sorteados) >= 1 and max(sorteados) <= 9 and sorteados == entrada.sortear_numeros(200, 1, 9, 5)
assert entrada.trocar_heuristicas({"A": Decimal(1)}, ["A", "B"], [None, Decimal(2)]) == {"B": Decimal(2)}
assert entrada.renomear_chave({"A": 1, "B": 2}, "A", "Z") == {"Z": 1, "B": 2}
assert entrada.manter_chaves({"A": 1, "B": 2}, ["B"]) == {"B": 2}
print("2. Nomes, validações, edição, pesos e leitura de texto: ok")


# ----------------------------------------------------------------------
# 3. Os sorteios respeitam as opções
# ----------------------------------------------------------------------

sorteio = random.Random(7)
for rodada in range(300):
    n = sorteio.randint(1, 26)
    vertices = entrada.nomes_dos_vertices(n)
    lacos = sorteio.random() < 0.5
    paralelas = sorteio.random() < 0.5
    maximo = entrada.maximo_de_arestas(n, lacos, paralelas)
    m = sorteio.randint(0, maximo)
    arestas = entrada.arestas_aleatorias(vertices, m, lacos, paralelas, sorteio.randint(0, 10 ** 6))
    assert len(arestas) == m
    pares = []
    for origem, destino, nome, peso in arestas:
        pares.append((origem, destino))
    for par in pares:
        assert lacos or par[0] != par[1], "laço sorteado sem permissão"
        assert pares.count(par) <= 2, "mais de 2 arestas paralelas"
        assert paralelas or pares.count(par) == 1, "paralela sorteada sem permissão"
    # Pedir mais do que cabe não trava: devolve o máximo
    assert len(entrada.arestas_aleatorias(vertices, maximo + 10, lacos, paralelas, 1)) == maximo

    limite = entrada.limite_de_vizinhos(n, lacos, paralelas)
    minimo = sorteio.randint(0, limite)
    maximo_vizinhos = sorteio.randint(minimo, limite)
    arestas = entrada.listas_aleatorias(vertices, minimo, maximo_vizinhos, lacos, paralelas, sorteio.randint(0, 10 ** 6))
    assert len(arestas) <= entrada.LIMITE_DE_ARESTAS
    grau_saida, grau_entrada = entrada.graus(vertices, arestas)
    for vertice in vertices:
        assert minimo <= grau_saida[vertice] <= maximo_vizinhos, "quantidade de vizinhos fora do pedido"
    for origem, destino, nome, peso in arestas:
        assert lacos or origem != destino
        conta = 0
        for outra_origem, outro_destino, outro_nome, outro_peso in arestas:
            if (outra_origem, outro_destino) == (origem, destino):
                conta += 1
        assert conta <= 2 and (paralelas or conta == 1)

# A mesma semente sempre gera o mesmo resultado
assert entrada.arestas_aleatorias(list("ABCD"), 6, True, True, 42) == entrada.arestas_aleatorias(list("ABCD"), 6, True, True, 42)
print("3. Sorteios de arestas e de listas: respeitam quantidade, laços e paralelas")


# ----------------------------------------------------------------------
# 4. Modelos (numa pasta temporária, para não mexer nos modelos de verdade)
# ----------------------------------------------------------------------

pasta_original = modelos.PASTA_DOS_MODELOS
exemplos_originais = modelos.PASTA_DOS_EXEMPLOS
with tempfile.TemporaryDirectory() as temporaria:
    modelos.PASTA_DOS_MODELOS = Path(temporaria) / "modelos"
    modelos.PASTA_DOS_EXEMPLOS = Path(temporaria) / "sem_exemplos"      # sem exemplos: só o código recria a prova
    assert modelos.listar_modelos() == ["Prova 01"], "a pasta e o modelo da prova são criados sozinhos"
    assert modelos.nome_do_padrao() == "Prova 01"

    vertices = ["São_Paulo", "Rio", "BH"]
    arestas = [("São_Paulo", "Rio", "via Dutra", Decimal("429.5")), ("Rio", "BH", "", Decimal(434)),
               ("BH", "BH", "volta", None)]
    estradas = modelos.novo_grafo(vertices, arestas, False, "Rio", False, "a_estrela", "BH",
                                  {"São_Paulo": Decimal("586.25"), "Rio": Decimal(340), "BH": Decimal(0)},
                                  {"São_Paulo": (10.5, 20.0), "Rio": (30.0, 25.0), "BH": (25.0, 5.0)})
    modelos.salvar_modelo("Estradas", estradas)
    assert modelos.carregar_modelo("Estradas") == estradas, "salvar e carregar é ida e volta (pesos, h e posições)"
    assert '"peso": 429.5' in (modelos.PASTA_DOS_MODELOS / "Estradas.json").read_text(encoding="utf-8")
    # Modelo antigo, sem as chaves novas: orientado, DFS, sem pesos, sem heurística
    (modelos.PASTA_DOS_MODELOS / "Antigo.json").write_text('{"vertices": ["A"], "arestas": []}', encoding="utf-8")
    antigo = modelos.carregar_modelo("Antigo")
    assert antigo["direcionado"] is True and antigo["algoritmo"] == "profundidade" and antigo["destino"] is None
    # Peso escrito como texto com vírgula (arquivo editado à mão) também é aceito
    (modelos.PASTA_DOS_MODELOS / "Texto.json").write_text(
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "A", "peso": "2,5"}]}', encoding="utf-8")
    assert modelos.carregar_modelo("Texto")["arestas"] == [("A", "A", "", Decimal("2.5"))]
    assert "São_Paulo" in (modelos.PASTA_DOS_MODELOS / "Estradas.json").read_text(encoding="utf-8"), "acentos legíveis"
    modelos.definir_padrao("Estradas")
    assert modelos.nome_do_padrao() == "Estradas"
    (modelos.PASTA_DOS_MODELOS / "Estradas.json").unlink()
    assert modelos.nome_do_padrao() == "Prova 01", "padrão apagado: volta para a prova"

    for nome_ruim in ("", " a", "a/b", "a:b", "a.", "x" * 41):
        assert modelos.validar_nome_de_modelo(nome_ruim) != "", nome_ruim
    assert modelos.validar_nome_de_modelo("Aula 3 - ciclos") == ""
    assert modelos.mesmo_nome("PROVA 01", "Prova 01"), "no Windows é o mesmo arquivo"

    # Arquivos quebrados ou editados errado viram ValueError com explicação (e não um travamento)
    conteudos_ruins = [
        "{ isto não é json",
        '{"vertices": "A", "arestas": []}',
        '{"vertices": ["A", "A"], "arestas": []}',
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "Z"}]}',
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "A", "nome": "a:b"}]}',
        '{"vertices": ["A B"], "arestas": []}',
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "A", "peso": "muito"}]}',
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "A", "peso": true}]}',
        '{"vertices": ["A"], "arestas": [{"origem": "A", "destino": "A", "peso": 1.23456}]}',
        '{"vertices": ["A"], "arestas": [], "heuristica": {"Z": 1}}',
        '{"vertices": ["A"], "arestas": [], "heuristica": {"A": -1}}',
        '{"vertices": ["A"], "arestas": [], "posicoes": {"A": [1]}}',
        '{"vertices": ["A"], "arestas": [], "posicoes": {"A": ["x", 2]}}',
    ]
    for conteudo in conteudos_ruins:
        (modelos.PASTA_DOS_MODELOS / "Ruim.json").write_text(conteudo, encoding="utf-8")
        try:
            modelos.carregar_modelo("Ruim")
            assert False, f"deveria recusar: {conteudo}"
        except ValueError:
            pass
    try:
        modelos.definir_padrao("Não existe")
        assert False, "não pode tornar padrão um modelo que não existe"
    except ValueError:
        pass
modelos.PASTA_DOS_MODELOS = pasta_original
modelos.PASTA_DOS_EXEMPLOS = exemplos_originais

# Instalado: os exemplos que vêm com o programa são copiados para a pasta do usuário na
# primeira vez, sem substituir um modelo que o usuário já tenha com o mesmo nome
with tempfile.TemporaryDirectory() as temporaria:
    modelos.PASTA_DOS_MODELOS = Path(temporaria) / "AppData" / "BoscoGraph" / "modelos"
    nomes_dos_exemplos = []
    for arquivo in modelos.PASTA_DOS_EXEMPLOS.glob("*.json"):
        nomes_dos_exemplos.append(arquivo.stem)
    assert modelos.listar_modelos() == sorted(nomes_dos_exemplos), "pastas de cima criadas e exemplos copiados"
    modelos.salvar_modelo("Prova 01", modelos.novo_grafo(["X"], []))     # o usuário mudou o seu
    modelos.copiar_exemplos()
    assert modelos.carregar_modelo("Prova 01")["vertices"] == ["X"], "a cópia nunca substitui o modelo do usuário"
    assert not list(modelos.PASTA_DOS_MODELOS.glob("*.tmp")), "a gravação não deixa arquivo temporário"
modelos.PASTA_DOS_MODELOS = pasta_original

# Onde ficam os recursos e os dados, rodando pelo código e "congelado" pelo PyInstaller
import os
import sys
import caminhos
assert caminhos.pasta_dos_modelos() == pasta_original, "pelo código-fonte: a pasta modelos/ do projeto"
estado_original = (getattr(sys, "frozen", None), getattr(sys, "_MEIPASS", None), sys.platform,
                   os.environ.get("APPDATA"), os.environ.get("BOSCOGRAPH_DADOS"))
try:
    os.environ.pop("BOSCOGRAPH_DADOS", None)
    sys.frozen = True
    sys._MEIPASS = "/pasta/interna"
    sys.platform = "win32"
    os.environ["APPDATA"] = "/Users/Ana/AppData/Roaming"
    assert caminhos.pasta_dos_recursos() == Path("/pasta/interna"), "o código mostrado vem de dentro do executável"
    assert caminhos.pasta_dos_modelos() == Path("/Users/Ana/AppData/Roaming/BoscoGraph/modelos"), \
        "instalado: os modelos vão para %APPDATA%\\BoscoGraph"
    os.environ["BOSCOGRAPH_DADOS"] = "/pendrive/BG"
    assert caminhos.pasta_dos_modelos() == Path("/pendrive/BG/modelos"), "a variável escolhe outra pasta"
finally:
    if estado_original[0] is None:
        del sys.frozen
    if estado_original[1] is None:
        del sys._MEIPASS
    sys.platform = estado_original[2]
    for nome, valor in (("APPDATA", estado_original[3]), ("BOSCOGRAPH_DADOS", estado_original[4])):
        if valor is None:
            os.environ.pop(nome, None)
        else:
            os.environ[nome] = valor
print("4. Modelos: salvar, carregar, padrão, arquivos com problema, exemplos e pasta do usuário")


# ----------------------------------------------------------------------
# 5. Propriedades da DFS em centenas de grafos sorteados, com nomes livres
# ----------------------------------------------------------------------

sorteio = random.Random(2026)
quantidade_de_grafos = 400
for rodada in range(quantidade_de_grafos):
    n = sorteio.randint(1, 26)
    estilo = sorteio.choice(["letras", "numeros", "prefixo"])
    vertices = entrada.nomes_dos_vertices(n, estilo, "R")
    # Alguns vértices ganham nomes livres (como quem renomeia no editor)
    for i in range(n):
        if sorteio.random() < 0.3:
            novo = nome_aleatorio(sorteio)
            if entrada.validar_nome_de_vertice(novo, vertices) == "":
                vertices[i] = novo
    lacos = sorteio.random() < 0.5
    paralelas = sorteio.random() < 0.5
    if sorteio.random() < 0.5:
        m = sorteio.randint(0, entrada.maximo_de_arestas(n, lacos, paralelas))
        arestas = entrada.arestas_aleatorias(vertices, m, lacos, paralelas, sorteio.randint(0, 10 ** 6))
    else:
        limite = entrada.limite_de_vizinhos(n, lacos, paralelas)
        arestas = entrada.listas_aleatorias(vertices, 0, limite, lacos, paralelas, sorteio.randint(0, 10 ** 6))
        m = len(arestas)
    if sorteio.random() < 0.5:
        arestas = entrada.numerar_arestas(arestas)
    ordenar = sorteio.random() < 0.5
    inicio = sorteio.choice(vertices)
    descricao = f"grafo {rodada}: {n} vértices, {m} arestas"

    passos = montar_passos(vertices, arestas, ordenar, inicio)
    tempo_d, tempo_f = tempos(passos)
    examinadas = arestas_examinadas(passos)
    raizes = []
    for passo in passos:
        if passo["tipo"] == "nova_arvore":
            raizes.append(passo["vertice"])

    # Cada vértice é descoberto e finalizado uma vez; os tempos são 1, 2, ..., 2n, sem repetir
    assert sorted(tempo_d) == sorted(vertices) and sorted(tempo_f) == sorted(vertices), descricao
    todos_os_tempos = sorted(list(tempo_d.values()) + list(tempo_f.values()))
    assert todos_os_tempos == list(range(1, 2 * n + 1)), descricao
    for v in vertices:
        assert tempo_d[v] < tempo_f[v], descricao

    # Teorema dos parênteses: dois intervalos [d, f] nunca se cruzam pela metade
    for u in vertices:
        for v in vertices:
            if u != v:
                separados = tempo_f[u] < tempo_d[v] or tempo_f[v] < tempo_d[u]
                u_dentro_de_v = tempo_d[v] < tempo_d[u] and tempo_f[u] < tempo_f[v]
                v_dentro_de_u = tempo_d[u] < tempo_d[v] and tempo_f[v] < tempo_f[u]
                assert separados or u_dentro_de_v or v_dentro_de_u, descricao

    # Cada aresta é examinada uma vez; arestas de árvore = vértices - árvores
    assert len(examinadas) == m, descricao
    quantidade_de_arvore = 0
    for origem, destino, classe in examinadas:
        du, fu = tempo_d[origem], tempo_f[origem]
        dv, fv = tempo_d[destino], tempo_f[destino]
        if classe == "arvore":
            quantidade_de_arvore += 1
            assert du < dv < fv < fu, descricao
        elif classe == "avanco":
            assert du < dv < fv < fu, descricao
        elif classe == "retorno":
            assert dv <= du < fu <= fv, descricao
        else:
            assert dv < fv < du < fu, descricao
    assert quantidade_de_arvore == n - len(raizes), descricao

    # O grafo tem ciclo se, e somente se, a DFS encontra aresta de retorno (conferido com Kahn)
    tem_retorno = False
    for origem, destino, classe in examinadas:
        if classe == "retorno":
            tem_retorno = True
    assert tem_retorno == tem_ciclo(vertices, arestas), descricao

    # A busca começa pelo vértice escolhido
    assert raizes[0] == inicio, descricao

    # A tela no último passo: tudo Preto, pilha vazia, arestas classificadas, listas certas
    estado = estado_final(passos)
    for v in vertices:
        assert estado.cor[v] == "Preto", descricao
    assert estado.pilha == [] and estado.tempo == 2 * n, descricao
    for situacao in estado.situacao_aresta:
        assert situacao in ("arvore", "retorno", "avanco", "cruzamento"), descricao
    for v in vertices:
        na_ordem_de_criacao = []
        for origem, destino, nome, peso in arestas:
            if origem == v:
                na_ordem_de_criacao.append(destino)
        if ordenar:
            assert estado.lista[v] == sorted(na_ordem_de_criacao), descricao
        else:
            assert estado.lista[v] == na_ordem_de_criacao, descricao

    # Passo a passo na tela:
    # - a pilha é sempre formada pelos vértices Cinza, na ordem em que foram descobertos;
    # - os nomes das arestas aparecem nas mensagens de exame (uma vez por aresta com nome)
    com_nome = 0
    for origem, destino, nome, peso in arestas:
        if nome != "":
            com_nome += 1
    mensagens_com_nome = 0
    estado = EstadoVisual(arestas)
    for passo in passos:
        estado.aplicar(passo)
        cinzas = []
        for v in estado.vertices_criados:
            if estado.cor[v] == "Cinza":
                cinzas.append(v)
        cinzas.sort(key=lambda v: estado.d[v])      # ordena pelos tempos de descoberta
        assert estado.pilha == cinzas, descricao
        if passo["tipo"] == "examinar" and estado.mensagem.endswith("]"):
            mensagens_com_nome += 1
    assert mensagens_com_nome == com_nome, descricao

    # Etapa 6: cíclico e DAG batem com Kahn; o ciclo de exemplo é um ciclo de verdade;
    # num DAG, a ordem topológica deixa toda aresta apontando para a frente
    ciclo = passo_do_tipo(passos, "tipo_ciclo")
    dag = passo_do_tipo(passos, "tipo_dag")
    assert ciclo["ciclico"] == tem_ciclo(vertices, arestas) and dag["dag"] == (not ciclo["ciclico"]), descricao
    if ciclo["ciclico"]:
        assert eh_ciclo(ciclo["ciclo"], arestas, True), descricao
        assert passo_do_tipo(passos, "ordem_topologica") is None, descricao
    else:
        ordem = passo_do_tipo(passos, "ordem_topologica")["ordem"]
        assert sorted(ordem) == sorted(vertices), descricao
        for origem, destino, nome, peso in arestas:
            assert ordem.index(origem) < ordem.index(destino), descricao
        assert estado.layout == "linha" and estado.ordem_topologica == ordem, "no fim, o desenho fica em linha"

print(f"5. Propriedades da DFS conferidas em {quantidade_de_grafos} grafos sorteados, com nomes livres")


# ----------------------------------------------------------------------
# 5b. Grafos não orientados: a aresta entra nas duas listas e só existem árvore e retorno
# ----------------------------------------------------------------------

sorteio = random.Random(31)
quantidade_nao_orientados = 400
for rodada in range(quantidade_nao_orientados):
    n = sorteio.randint(1, 26)
    vertices = entrada.nomes_dos_vertices(n, sorteio.choice(["letras", "numeros", "prefixo"]), "R")
    lacos = sorteio.random() < 0.5
    paralelas = sorteio.random() < 0.5
    if sorteio.random() < 0.5:
        m = sorteio.randint(0, entrada.maximo_de_arestas(n, lacos, paralelas, False))
        arestas = entrada.arestas_aleatorias(vertices, m, lacos, paralelas, sorteio.randint(0, 10 ** 6), False)
    else:
        limite = entrada.limite_de_vizinhos(n, lacos, paralelas)
        arestas = entrada.listas_aleatorias(vertices, 0, limite, lacos, paralelas, sorteio.randint(0, 10 ** 6), False)
    m = len(arestas)
    if sorteio.random() < 0.5:
        arestas = entrada.numerar_arestas(arestas)
    ordenar = sorteio.random() < 0.5
    inicio = sorteio.choice(vertices)
    descricao = f"não orientado {rodada}: {n} vértices, {m} arestas"

    # O sorteio não orientado respeita laços e paralelas contando A — B e B — A como o mesmo par
    contagem = entrada.contar_pares(arestas, False)
    for origem, destino, nome, peso in arestas:
        assert lacos or origem != destino, descricao
        repeticoes = contagem[entrada.chave_do_par(origem, destino, False)]
        assert repeticoes <= 2 and (paralelas or repeticoes == 1), descricao

    passos = montar_passos(vertices, arestas, ordenar, inicio, False)
    tempo_d, tempo_f = tempos(passos)
    examinadas = arestas_examinadas(passos)
    revisitas = contar_tipos(passos).get("revisitar", 0)
    raizes = []
    for passo in passos:
        if passo["tipo"] == "nova_arvore":
            raizes.append(passo["vertice"])
    lacos_no_grafo = 0
    for origem, destino, nome, peso in arestas:
        if origem == destino:
            lacos_no_grafo += 1

    # Cada aresta é classificada uma vez; a volta (na lista do outro vértice) aparece uma vez,
    # menos no laço, que está uma vez só na lista
    assert len(examinadas) == m and revisitas == m - lacos_no_grafo, descricao
    # Só existem arestas de árvore e de retorno (CLRS, Teorema 22.10)
    for origem, destino, classe in examinadas:
        assert classe in ("arvore", "retorno"), descricao
    # Parênteses continuam valendo; árvore = n - componentes
    for u in vertices:
        for v in vertices:
            if u != v:
                separados = tempo_f[u] < tempo_d[v] or tempo_f[v] < tempo_d[u]
                aninhados = (tempo_d[v] < tempo_d[u] and tempo_f[u] < tempo_f[v]) or \
                            (tempo_d[u] < tempo_d[v] and tempo_f[v] < tempo_f[u])
                assert separados or aninhados, descricao
    quantidade_de_arvore = 0
    for origem, destino, classe in examinadas:
        if classe == "arvore":
            quantidade_de_arvore += 1
    assert quantidade_de_arvore == n - len(raizes), descricao

    # Componentes e ciclo conferidos com a união-busca (que não usa a DFS)
    componentes, tem_ciclo_nao_orientado, grupo_do_vertice = componentes_e_ciclo_nao_orientado(vertices, arestas)
    assert len(raizes) == componentes, descricao
    ciclo = passo_do_tipo(passos, "tipo_ciclo")
    assert ciclo["ciclico"] == tem_ciclo_nao_orientado, descricao
    if ciclo["ciclico"]:
        assert eh_ciclo(ciclo["ciclo"], arestas, False), descricao
    forma = passo_do_tipo(passos, "tipo_componentes")
    assert len(forma["componentes"]) == componentes, descricao
    # Cada componente da DFS é exatamente um grupo da união-busca
    grupos_usados = []
    for componente in forma["componentes"]:
        grupos = []
        for vertice in componente:
            if grupo_do_vertice[vertice] not in grupos:
                grupos.append(grupo_do_vertice[vertice])
        assert len(grupos) == 1 and grupos[0] not in grupos_usados, descricao
        grupos_usados.append(grupos[0])

    # A tela: cada lista tem os vizinhos dos dois sentidos, e toda aresta termina árvore ou retorno
    estado = estado_final(passos, False)
    assert estado.pilha == [] and estado.tempo == 2 * n, descricao
    for indice in range(m):
        origem, destino, nome, peso = arestas[indice]
        assert estado.situacao_aresta[indice] in ("arvore", "retorno"), descricao
        assert estado.revisitada[indice] == (origem != destino), descricao
    for v in vertices:
        vizinhos = []
        for origem, destino, nome, peso in arestas:
            if origem == v:
                vizinhos.append(destino)
            elif destino == v:
                vizinhos.append(origem)
        assert sorted(estado.lista[v]) == sorted(vizinhos), descricao

    # O nome da aresta aparece no exame e também na volta (menos no laço, que não tem volta)
    com_nome = 0
    voltas_com_nome = 0
    for origem, destino, nome, peso in arestas:
        if nome != "":
            com_nome += 1
            if origem != destino:
                voltas_com_nome += 1
    exames = 0
    voltas = 0
    estado = EstadoVisual(arestas, False)
    for passo in passos:
        estado.aplicar(passo)
        if passo["tipo"] == "examinar" and estado.mensagem.endswith("]"):
            exames += 1
        if passo["tipo"] == "revisitar" and estado.mensagem.endswith("]"):
            voltas += 1
    assert exames == com_nome and voltas == voltas_com_nome, descricao

# Exemplos pequenos, conferidos à mão
passos = montar_passos(["A", "B"], [("A", "B", "", None), ("B", "A", "", None)], True, "A", False)
assert passo_do_tipo(passos, "tipo_simples")["simples"] is False, "A — B e B — A são paralelas no não orientado"
assert passo_do_tipo(passos, "tipo_completo")["completo"] is False, "todos os pares ligados, mas não é simples"
assert entrada.chave_do_par("B", "A", False) == ("A", "B") and entrada.chave_do_par("B", "A", True) == ("B", "A")
assert entrada.observacoes([("A", "B", "", None), ("B", "A", "", None)], False) == ["paralela", "paralela"]
assert entrada.observacoes([("A", "B", "", None), ("B", "A", "", None)], True) == ["", ""]
assert passo_do_tipo(passos, "tipo_ciclo")["ciclo"] == ["A", "B", "A"], "duas arestas paralelas formam um ciclo"
passos = montar_passos(["A", "B"], [("A", "B", "", None), ("B", "A", "", None)], True, "A", True)
assert passo_do_tipo(passos, "tipo_simples")["simples"] is True, "A -> B e B -> A não são paralelas no orientado"
passos = montar_passos(["A", "B", "C"], [("A", "B", "", None), ("B", "C", "", None)], True, "A", False)
assert passo_do_tipo(passos, "tipo_resumo")["resumo"].endswith("acíclico · árvore")
assert entrada.graus_nao_orientados(["A", "B"], [("A", "A", "", None), ("A", "B", "", None)]) == {"A": 3, "B": 1}, "laço conta 2"
assert entrada.maximo_de_arestas(4, False, False, False) == 6, "K4 tem 6 arestas"
lidas = entrada.ler_arestas(entrada.texto_das_arestas([("A", "B", "x", Decimal(2))], False), ["A", "B"])[0]
assert lidas == [("A", "B", "x", Decimal(2))], "o texto não orientado (A - B) é lido de volta"
print(f"5b. Não orientado conferido em {quantidade_nao_orientados} grafos: só árvore e retorno, componentes e ciclos")


# ----------------------------------------------------------------------
# 5c. Classificação: simples, completo, valorado
# ----------------------------------------------------------------------

def resumo_do_tipo(vertices, arestas, direcionado):
    return passo_do_tipo(montar_passos(vertices, arestas, True, None, direcionado), "tipo_resumo")["resumo"]

k4 = []
for i in range(4):
    for j in range(i + 1, 4):
        k4.append(("ABCD"[i], "ABCD"[j], "", None))
assert resumo_do_tipo(list("ABCD"), k4, False) == "não orientado · simples · completo · não valorado · cíclico · conexo"
completo_orientado = []
for origem in "ABC":
    for destino in "ABC":
        if origem != destino:
            completo_orientado.append((origem, destino, "", Decimal(5)))
assert resumo_do_tipo(list("ABC"), completo_orientado, True) == "orientado · simples · completo · valorado · cíclico · não é DAG"
assert resumo_do_tipo(list("ABC"), [], True) == "orientado · simples · não completo · não valorado · acíclico · DAG"
assert "É um grafo vazio" in passo_do_tipo(montar_passos(["A", "B"], [], True, None), "tipo_completo")["mensagem"]
assert resumo_do_tipo(["A"], [], False).endswith("completo · não valorado · acíclico · árvore"), "1 vértice: K1"
meio = resumo_do_tipo(list("ABC"), [("A", "B", "x", Decimal(3)), ("B", "C", "", None)], True)
assert "valorado em parte" in meio
simetrico = passo_do_tipo(montar_passos(["A", "B"], [("A", "B", "", None), ("B", "A", "", None)], True, None), "tipo_orientacao")
assert simetrico["simetrico"] and "daria para tratar como não orientado" in simetrico["mensagem"]
print("5c. Classificação (simples, completo, valorado, vazio, simétrico): ok")


# ----------------------------------------------------------------------
# 6. Geometria do desenho
# ----------------------------------------------------------------------

for n in range(1, 27):
    for largura, altura in ((560, 420), (900, 700), (300, 240)):
        for raio_para_os_nomes in (0, 55):
            medidas = desenho.calcular_medidas(n, largura, altura, 1.0, raio_para_os_nomes)
            raio = medidas["raio_vertice"]
            assert 8 <= raio <= 40, "raio do vértice dentro dos limites"
            if n >= 2:
                # Vizinhos no círculo nunca se encostam: a distância entre os centros (a corda)
                # é maior que dois raios
                corda = 2 * medidas["raio_circulo"] * math.sin(math.pi / n)
                assert corda > 2 * raio or raio == 8, (n, largura, altura)

# O nome de uma aresta fica no meio da curva (e não no ponto de controle); o de um laço fica do lado de fora
reta = [(0, 0), (50, 0), (100, 0)]
assert desenho.ponto_do_nome_da_aresta(reta, 10) == (50, 0)
curva = [(0, 0), (50, 40), (100, 0)]
assert desenho.ponto_do_nome_da_aresta(curva, 10) == (50, 20), "meio da Bézier: (0 + 2 x 40 + 0) / 4 = 20"
laco = desenho.pontos_do_laco((100, 100), (100, 300), 20, 0)
x, y = desenho.ponto_do_nome_da_aresta(laco, 10)
assert math.hypot(x - 100, y - 100) > 20, "o nome do laço fica fora do vértice"

# Em linha (ordem topológica): da esquerda para a direita, na mesma altura, arcos por cima
medidas = desenho.medidas_da_linha(5, 600, 400, 1.0)
posicoes = desenho.posicoes_em_linha(list("ABCDE"), 600, medidas, 30)
xs = [posicoes[nome][0] for nome in "ABCDE"]
assert xs == sorted(xs) and len(set(posicoes[nome][1] for nome in "ABCDE")) == 1
for inicio, controle, fim in desenho.pontos_em_arco([("A", "C"), ("A", "C"), ("B", "E")], posicoes,
                                                    medidas["raio_vertice"], medidas["espaco_acima"]):
    assert controle[1] < inicio[1] and controle[1] < fim[1], "o arco passa por cima da linha"
    assert controle[1] >= 30 + medidas["y_da_linha"] - 2 * medidas["espaco_acima"], "e não sai do desenho"
print("6. Geometria: vértices sem se encostar e nomes das arestas no lugar certo")


# ----------------------------------------------------------------------
# 7. Cada passo aponta para uma linha que existe no código mostrado na tela
#    (precisa do Tkinter, que já vem com o Python no Windows)
# ----------------------------------------------------------------------

try:
    from visual.codigo import localizar_trechos
    from visual import perfis
    for algoritmo in perfis.PERFIS:
        trechos = perfis.PERFIS[algoritmo]["trechos"]
        linhas_do_arquivo, linha_do_trecho = localizar_trechos(trechos)
        assert set(linha_do_trecho) == set(trechos)
        for chave in linha_do_trecho:
            arquivo, a_partir_de, trecho = trechos[chave]
            assert trecho in linhas_do_arquivo[arquivo][linha_do_trecho[chave] - 1]
    print(f"7. Trechos de código destacados na tela: todos encontrados ({len(perfis.PERFIS)} buscas)")
except ImportError:
    print("7. Pulado: este Python não tem Tkinter")

# ----------------------------------------------------------------------
# 8. As outras buscas (largura, Dijkstra, Bellman-Ford, gulosa e A*), no arquivo testes_buscas.py
# ----------------------------------------------------------------------

import testes_buscas
testes_buscas.rodar()

# As buscas novas da versão 6 (limitada, iterativa, bidirecional e Floyd-Warshall), no arquivo
# testes_novas_buscas.py
import testes_novas_buscas
testes_novas_buscas.rodar()

# A árvore geradora mínima da versão 7.3 (Prim e Kruskal), no arquivo testes_arvore_minima.py
import testes_arvore_minima
testes_arvore_minima.rodar()

# ----------------------------------------------------------------------
# 9. Importação de grafos de outros programas, no arquivo testes_importacao.py
# ----------------------------------------------------------------------

import testes_importacao
testes_importacao.rodar()

# ----------------------------------------------------------------------
# 10. O autoteste do executável (verificacao.py, "--verificar") passa pelo código-fonte.
#     A pasta de dados vai para uma pasta temporária (BOSCOGRAPH_DADOS), como no construir.py.
# ----------------------------------------------------------------------

import os
import caminhos
import verificacao

with tempfile.TemporaryDirectory() as pasta_temporaria:
    antes = os.environ.get(caminhos.VARIAVEL_DA_PASTA_DE_DADOS)
    os.environ[caminhos.VARIAVEL_DA_PASTA_DE_DADOS] = pasta_temporaria
    try:
        resultados = verificacao.verificar()
        assert caminhos.pasta_dos_modelos() == Path(pasta_temporaria) / "modelos"
    finally:
        if antes is None:
            del os.environ[caminhos.VARIAVEL_DA_PASTA_DE_DADOS]
        else:
            os.environ[caminhos.VARIAVEL_DA_PASTA_DE_DADOS] = antes
    for certo, texto in resultados:
        assert certo or texto.startswith("Painel de código: No module named"), texto
print("10. Autoteste do executável (--verificar): tudo certo pelo código-fonte")

# ----------------------------------------------------------------------
# 11. O código de estudo (pasta estudo/), no arquivo testes_estudo.py: o Python faz a mesma busca que
#     o BoscoGraph, os rótulos de linha batem e as traduções dão o mesmo resultado
# ----------------------------------------------------------------------

import testes_estudo
testes_estudo.rodar()

# ----------------------------------------------------------------------
# 12. As telas (tela inicial, editor e visualização, passo a passo e linha a linha), no arquivo
#     testes_tela.py. A janela fica escondida; sem tela gráfica, a seção é pulada.
# ----------------------------------------------------------------------

import testes_tela
testes_tela.rodar()

# ----------------------------------------------------------------------
# 13. O escritor de PDF (exportacao/pdf.py), no arquivo testes_pdf.py
# ----------------------------------------------------------------------

import testes_pdf
testes_pdf.rodar()

# ----------------------------------------------------------------------
# 14. As exportações (.bosco, código-fonte nas cinco linguagens, figuras e o relatório), no arquivo
#     testes_exportacao.py
# ----------------------------------------------------------------------

import testes_exportacao
testes_exportacao.rodar()

print("Todos os testes passaram.")
