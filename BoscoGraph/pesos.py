'''
    O que o diálogo "Pesos…" do editor faz: aplicar pesos nas arestas ou a heurística h nos vértices.

    O usuário escolhe três coisas:
      lugar -> "arestas" (o peso de cada aresta) ou "vertices" (a heurística h de cada vértice)
      quais -> "todas", "selecionadas" (na tabela do editor) ou "sem_valor" (só as que ainda não têm)
      valor -> "fixo" (o mesmo valor para todas), "sortear" (inteiros num intervalo), "remover",
               e, só para a heurística: "custo_real" (h perfeita) ou "admissivel" (sorteada entre 0
               e o custo real, o que garante que h nunca passa do custo real)

    Python puro (sem Tkinter): o editor chama aplicar_escolha() e os testes também.
'''

import random
from decimal import Decimal

import algoritmos
import entrada


# Por que o "custo real até o destino" não está disponível ("" = está disponível)
def motivo_sem_custo_real(vertices, arestas, destino, direcionado):
    if destino not in vertices:
        return "Escolha um destino em 4. Busca para calcular o custo real."
    if algoritmos.custos_ate_o_destino(vertices, arestas, destino, direcionado) is None:
        return "O custo real precisa de peso (sem negativos) em todas as arestas."
    return ""


# Lê um número inteiro de um campo do diálogo. Devolve (número, problema).
def ler_inteiro(texto, nome):
    numero, problema = entrada.ler_numero(texto)
    if problema:
        return None, f"{nome}: {problema}"
    if numero is None:
        return None, f"{nome}: digite um número."
    if numero != numero.to_integral_value():
        return None, f"{nome}: o sorteio usa números inteiros."
    return numero, ""


# Aplica a escolha do diálogo. Devolve (novas_arestas, nova_heuristica, aviso, problema):
# se "problema" não for "", nada muda e o diálogo mostra o problema.
#   indices_selecionados  -> as posições das arestas selecionadas na tabela do editor
#   vertices_selecionados -> os nomes dos vértices selecionados na tabela do editor
def aplicar_escolha(escolha, vertices, arestas, heuristica, direcionado, destino,
                    indices_selecionados, vertices_selecionados, semente=None):
    nas_arestas = escolha["lugar"] == "arestas"
    nome = "peso" if nas_arestas else "h"

    # 1. Quais itens recebem o valor
    if nas_arestas:
        if escolha["quais"] == "todas":
            alvos = list(range(len(arestas)))
        elif escolha["quais"] == "selecionadas":
            alvos = list(indices_selecionados)
        else:
            alvos = entrada.indices_sem_peso(arestas)
    else:
        if escolha["quais"] == "todas":
            alvos = list(vertices)
        elif escolha["quais"] == "selecionadas":
            alvos = list(vertices_selecionados)
        else:
            alvos = []
            for vertice in vertices:
                if vertice not in heuristica:
                    alvos.append(vertice)
    if not alvos:
        return arestas, heuristica, "", "Nenhum item nessa escolha: nada para mudar."

    # 2. Os valores, um para cada item
    valor = escolha["valor"]
    if valor == "fixo":
        numero, problema = entrada.ler_numero(escolha["fixo"])
        if problema == "" and numero is None:
            problema = "Digite o valor (por exemplo 1 ou 2,5)."
        if problema == "" and not nas_arestas and numero < 0:
            problema = "A heurística não pode ser negativa: ela estima quanto falta até o destino."
        if problema:
            return arestas, heuristica, "", problema
        valores = []
        for item in alvos:
            valores.append(numero)
        resumo = f"{nome} {entrada.formatar_numero(numero)}"
    elif valor == "sortear":
        minimo, problema = ler_inteiro(escolha["minimo"], "Mínimo")
        if problema == "":
            maximo, problema = ler_inteiro(escolha["maximo"], "Máximo")
        if problema == "" and minimo > maximo:
            problema = "O mínimo não pode ser maior que o máximo."
        if problema == "" and not nas_arestas and minimo < 0:
            problema = "A heurística não pode ser negativa: use um mínimo de 0 ou mais."
        if problema:
            return arestas, heuristica, "", problema
        valores = entrada.sortear_numeros(len(alvos), minimo, maximo, semente)
        resumo = f"{nome} sorteado de {entrada.formatar_numero(minimo)} a {entrada.formatar_numero(maximo)}"
    elif valor in ("custo_real", "admissivel") and not nas_arestas:
        custo = algoritmos.custos_ate_o_destino(vertices, arestas, destino, direcionado)
        if custo is None:
            return arestas, heuristica, "", motivo_sem_custo_real(vertices, arestas, destino, direcionado)
        sorteio = random.Random(semente)
        valores = []
        for vertice in alvos:
            real = custo[vertice]
            if real == entrada.INFINITO:
                valores.append(Decimal(0))      # não chega ao destino: h não importa, fica 0
            elif valor == "custo_real":
                valores.append(real)
            else:
                # Inteiro entre 0 e o custo real (int() de um número positivo corta as casas decimais)
                valores.append(Decimal(sorteio.randint(0, int(real))))
        if valor == "custo_real":
            resumo = f"h = custo real até {destino}"
        else:
            resumo = f"h admissível (entre 0 e o custo real até {destino})"
    else:
        valores = []
        for item in alvos:
            valores.append(None)
        resumo = None

    # 3. Aplica
    if nas_arestas:
        novas_arestas = entrada.trocar_pesos(arestas, alvos, valores)
        nova_heuristica = heuristica
        coisas = entrada.contar(len(alvos), "aresta", "arestas")
    else:
        novas_arestas = arestas
        nova_heuristica = entrada.trocar_heuristicas(heuristica, alvos, valores)
        coisas = entrada.contar(len(alvos), "vértice", "vértices")
    if resumo is None:
        aviso = f"{nome.capitalize()} tirado de {coisas}. Ctrl+Z desfaz."
    else:
        aviso = f"{resumo[0].upper() + resumo[1:]} em {coisas}. Ctrl+Z desfaz."
    return novas_arestas, nova_heuristica, aviso, ""
