'''
    Conferências da árvore geradora mínima (versão 7.3), sem abrir janela: Prim e Kruskal.
    Rode com: python testes_arvore_minima.py   (o testes.py também chama este arquivo)

    Como nos outros testes, cada resposta é conferida com um jeito INDEPENDENTE de chegar nela:
      - força bruta: em grafos pequenos, TODOS os jeitos de escolher n − partes arestas são testados;
        a floresta mínima é a mais leve entre as escolhas que não fecham ciclo;
      - o Prim e o Kruskal conferem um ao outro: o peso total é sempre o mesmo e, com os pesos todos
        diferentes, as arestas também (a árvore mínima é única);
      - os exemplos do livro (CLRS, figuras 23.4 e 23.5): peso 37.
'''

import random
from decimal import Decimal
from itertools import combinations

import algoritmos
import entrada
import modelos
from boscograph import montar_passos
from testes_buscas import passo_do_tipo, passos_do_tipo, nenhuma_mensagem_quebrada
from testes_novas_buscas import grafo_sorteado

D = Decimal
PRIM = algoritmos.PRIM
KRUSKAL = algoritmos.KRUSKAL


# ----------------------------------------------------------------------
# Função de apoio (independente das classes do BoscoGraph)
# ----------------------------------------------------------------------

# Junta as pontas das arestas escolhidas, uma por uma (união-busca simples: cada vértice aponta para
# outro do mesmo grupo, e quem aponta para si mesmo é a "raiz" do grupo). Se as duas pontas de uma
# aresta já estão no mesmo grupo, ela fecha um ciclo. Devolve (quantos grupos sobraram, fechou ciclo?).
def juntar(vertices, arestas, escolhidas):
    grupo = {}
    for vertice in vertices:
        grupo[vertice] = vertice
    grupos = len(vertices)
    fechou_ciclo = False
    for numero in escolhidas:
        a = arestas[numero][0]
        while grupo[a] != a:
            a = grupo[a]
        b = arestas[numero][1]
        while grupo[b] != b:
            b = grupo[b]
        if a == b:
            fechou_ciclo = True
        else:
            grupo[a] = b                # os dois grupos viram um só
            grupos -= 1
    return grupos, fechou_ciclo


def peso_de(arestas, escolhidas):
    total = 0
    for numero in escolhidas:
        total += arestas[numero][3]
    return total


# ----------------------------------------------------------------------
# 8o. Força bruta: o Prim e o Kruskal acham o menor peso possível
# ----------------------------------------------------------------------

def conferir_forca_bruta(quantidade):
    sorteio = random.Random(2323)
    unicas = 0
    for rodada in range(quantidade):
        # O sentido sorteado não importa: aqui o grafo é sempre não orientado (A → B e B → A viram duas
        # arestas paralelas A — B). Pesos fracionados, repetidos e negativos; laços e paralelas às vezes.
        vertices, arestas, sentido = grafo_sorteado(sorteio, 7, 12, True, True)
        n = len(vertices)
        partes, fechou_ciclo = juntar(vertices, arestas, range(len(arestas)))

        # A resposta certa: entre todas as escolhas de n − partes arestas sem ciclo, a mais leve.
        # (n − partes arestas sem ciclo sempre ligam cada parte inteira: é uma floresta geradora.)
        menor = None
        for escolhidas in combinations(range(len(arestas)), n - partes):
            if not juntar(vertices, arestas, escolhidas)[1]:
                peso = peso_de(arestas, escolhidas)
                if menor is None or peso < menor:
                    menor = peso

        for chave in (PRIM, KRUSKAL):
            raiz = sorteio.choice(vertices) if chave == PRIM else None     # o Kruskal não usa origem
            descricao = (chave, vertices, arestas, raiz)
            passos = montar_passos(vertices, arestas, True, raiz, False, chave)
            nenhuma_mensagem_quebrada(passos, descricao)
            resultado = passo_do_tipo(passos, "resultado_arvore_minima")
            escolhidas = resultado["arestas"]
            grupos, fechou_ciclo = juntar(vertices, arestas, escolhidas)
            assert not fechou_ciclo, descricao                              # é uma floresta
            assert grupos == partes == resultado["partes"], descricao       # que liga cada parte inteira
            assert len(escolhidas) == n - partes, descricao
            assert resultado["total"] == peso_de(arestas, escolhidas) == menor, descricao    # a mais leve

            # O outro algoritmo (que roda escondido) chega ao mesmo peso. Com os pesos todos diferentes
            # (sem contar os laços, que nunca entram), a árvore mínima é única: as mesmas arestas.
            comparacao = passo_do_tipo(passos, "resultado_mesmo_peso")
            assert comparacao["outro_total"] == comparacao["total"] == menor, descricao
            pesos = []
            for origem, destino, nome, peso in arestas:
                if origem != destino:
                    pesos.append(peso)
            todos_diferentes = len(set(pesos)) == len(pesos)
            if todos_diferentes:
                assert comparacao["mesmas"], descricao
                unicas += 1
            # A frase "a árvore mínima é única" só aparece quando é verdade
            assert ("é única" in comparacao["mensagem"]) == todos_diferentes, descricao

            if chave == PRIM:
                # Uma raiz por parte; quem entra na árvore entra com a chave igual ao peso da aresta do pai
                assert len(passos_do_tipo(passos, "raiz")) == partes, descricao
                for passo in passos_do_tipo(passos, "extrair"):
                    if passo["pai"] is not None:
                        assert passo["chave"] == arestas[passo["aresta"]][3], descricao
                kruskal_escondido = comparacao["outras"]
            else:
                # O Kruskal escondido do Prim é este mesmo Kruskal: as mesmas arestas, na mesma ordem
                assert kruskal_escondido == escolhidas, descricao
                # O Kruskal decide as arestas da mais leve para a mais pesada
                pesos_decididos = []
                for passo in passos:
                    if passo["tipo"] in ("aceitar", "rejeitar"):
                        pesos_decididos.append(passo["peso"])
                assert pesos_decididos == sorted(pesos_decididos), descricao
    print(f"8o. Árvore geradora mínima: Prim e Kruskal em {quantidade} grafos sorteados, conferidos por força "
          f"bruta (todas as escolhas de arestas), um com o outro e com a árvore única em {unicas} casos")


# ----------------------------------------------------------------------
# 8p. O exemplo do livro e os requisitos
# ----------------------------------------------------------------------

def conferir_livro_e_requisitos():
    grafo = modelos.carregar_exemplo("Exemplo - Árvore geradora mínima (CLRS 23.1)")
    vertices = grafo["vertices"]
    arestas = grafo["arestas"]

    # Kruskal, figura 23.4: as arestas aceitas, na ordem do livro
    passos = montar_passos(vertices, arestas, True, None, False, KRUSKAL)
    aceitas = []
    for passo in passos_do_tipo(passos, "aceitar"):
        aceitas.append(passo["origem"] + passo["destino"])
    assert aceitas == ["hg", "ic", "gf", "ab", "cf", "cd", "ah", "de"], aceitas
    assert passo_do_tipo(passos, "resultado_arvore_minima")["total"] == 37

    # Prim, figura 23.5, a partir de a. No empate entre c e h (chave 8), sai o que entrou primeiro na
    # fila (h, alcançado pelo a); o livro tira o c, e avisa que tanto faz. O peso é o mesmo: 37.
    passos = montar_passos(vertices, arestas, True, "a", False, PRIM)
    ordem = []
    for passo in passos_do_tipo(passos, "extrair"):
        ordem.append(passo["vertice"])
    assert ordem == ["a", "b", "h", "g", "f", "c", "i", "d", "e"], ordem
    assert passo_do_tipo(passos, "resultado_arvore_minima")["total"] == 37
    assert passo_do_tipo(passos, "resultado_mesmo_peso")["mesmas"]

    # Requisitos: só não orientado, com pesos; o Kruskal não precisa de origem
    uma = [("A", "B", "", D(1))]
    problemas, avisos = algoritmos.conferir(PRIM, ["A", "B"], uma, True, "A", None, {})
    assert problemas and "não orientado" in problemas[0], problemas
    problemas, avisos = algoritmos.conferir(KRUSKAL, ["A", "B"], [("A", "B", "", None)], False, None, None, {})
    assert problemas and "sem peso" in problemas[0], problemas
    problemas, avisos = algoritmos.conferir(KRUSKAL, ["A", "B"], uma, False, None, None, {})
    assert problemas == [] and avisos == [], (problemas, avisos)
    # Desligado: o aviso da floresta
    problemas, avisos = algoritmos.conferir(PRIM, ["A", "B", "C"], uma, False, "A", None, {})
    assert problemas == [] and "floresta" in avisos[0], avisos
    # Um vértice só: árvore sem arestas, peso 0
    passos = montar_passos(["A"], [], True, "A", False, PRIM)
    resultado = passo_do_tipo(passos, "resultado_arvore_minima")
    assert resultado["total"] == 0 and resultado["arestas"] == [] and "só o vértice" in resultado["mensagem"]
    print("8p. Exemplos do livro (CLRS 23.4 e 23.5: as arestas na ordem do livro, peso 37), requisitos e "
          "casos de borda da árvore mínima: ok")


# ----------------------------------------------------------------------
# 8q. A tela, passo a passo, no Prim e no Kruskal
# ----------------------------------------------------------------------

def conferir_estado_visual(quantidade):
    from visual.estado import EstadoVisual
    from visual import explicacoes, perfis
    sorteio = random.Random(733)
    for rodada in range(quantidade):
        chave = (PRIM, KRUSKAL)[rodada % 2]
        vertices, arestas, sentido = grafo_sorteado(sorteio, 8, 14, True, True)
        if sorteio.random() < 0.4:
            arestas = entrada.numerar_arestas(arestas)
        raiz = sorteio.choice(vertices)
        descricao = (chave, vertices, arestas, raiz)
        passos = montar_passos(vertices, arestas, True, raiz, False, chave)
        estado = EstadoVisual(arestas, False, chave)
        for passo in passos:
            estado.aplicar(passo)
            assert perfis.chave_do_trecho(passo) in perfis.perfil(chave)["trechos"], (descricao, passo["tipo"])
            assert explicacoes.explicar(chave, passo) != "", (descricao, passo["tipo"])
            for vertice in vertices:
                perfis.valores_da_tabela(chave, estado, vertice)
                perfis.rotulo_do_vertice(chave, estado, vertice)
            if chave == PRIM:
                # Tracejada = a melhor ligação de um vértice da fila: uma para cada um (menos a raiz, sem pai)
                tracejadas = estado.situacao_aresta.count("candidata")
                com_pai = 0
                for vertice in estado.fila:
                    if estado.pai.get(vertice) is not None:
                        com_pai += 1
                assert tracejadas == com_pai, (descricao, passo["tipo"])
        # No fim, o desenho tem exatamente as arestas da resposta, com o peso dela
        resultado = passo_do_tipo(passos, "resultado_arvore_minima")
        na_arvore = []
        for indice in range(len(arestas)):
            assert estado.situacao_aresta[indice] != "candidata", descricao    # nenhuma ficou provisória
            if estado.situacao_aresta[indice] == "arvore":
                na_arvore.append(indice)
        assert sorted(na_arvore) == sorted(resultado["arestas"]), descricao
        assert estado.peso_da_arvore == resultado["total"], descricao
        if chave == KRUSKAL:
            assert len(estado.conjuntos()) == resultado["partes"], descricao      # um conjunto por parte
    print(f"8q. Tela conferida passo a passo em {quantidade} árvores mínimas (a tracejada de cada vértice da fila, "
          f"as arestas da árvore e o peso no desenho, os conjuntos do Kruskal, código e explicações)")


def rodar():
    conferir_forca_bruta(400)
    conferir_livro_e_requisitos()
    conferir_estado_visual(200)


if __name__ == "__main__":
    rodar()
    print("Todos os testes da árvore geradora mínima passaram.")
