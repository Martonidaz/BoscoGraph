'''
    Contas de geometria usadas para reconhecer um grafo num desenho (PDF e imagem):
    distância de um ponto a uma linha, pontos de uma curva de Bézier, a forma mais próxima...
    Só Python (math), sem nenhuma biblioteca.
'''

import math


def distancia(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


# Distância do ponto p ao segmento de reta a-b.
# Ideia: projeta p na reta que passa por a e b (o "t" diz onde: 0 = em a, 1 = em b);
# se a projeção cair fora do segmento, o ponto mais perto é a ponta mais próxima.
def distancia_ao_segmento(p, a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    comprimento_ao_quadrado = dx * dx + dy * dy
    if comprimento_ao_quadrado == 0:
        return distancia(p, a)
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / comprimento_ao_quadrado
    t = max(0.0, min(1.0, t))
    return distancia(p, (a[0] + t * dx, a[1] + t * dy))


# Distância do ponto p a uma linha quebrada (uma lista de pontos ligados em sequência)
def distancia_a_linha(p, pontos):
    if len(pontos) == 1:
        return distancia(p, pontos[0])
    menor = None
    for i in range(len(pontos) - 1):
        d = distancia_ao_segmento(p, pontos[i], pontos[i + 1])
        if menor is None or d < menor:
            menor = d
    return menor


# Pontos de uma curva de Bézier cúbica (a curva dos programas de desenho e do PDF):
# B(t) = (1-t)³·p0 + 3(1-t)²t·p1 + 3(1-t)t²·p2 + t³·p3, com t indo de 0 a 1
def pontos_da_bezier(p0, p1, p2, p3, quantidade=10):
    pontos = []
    for i in range(quantidade + 1):
        t = i / quantidade
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        pontos.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                       a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pontos


# Distância de um ponto até a BORDA de um vértice (0 = em cima da borda).
# forma: {"centro": (x, y), "raio": r} para círculos, ou {"caixa": (x0, y0, x1, y1)} para retângulos.
def distancia_a_borda(p, forma):
    if "raio" in forma:
        return abs(distancia(p, forma["centro"]) - forma["raio"])
    x0, y0, x1, y1 = forma["caixa"]
    dentro = x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    fora_x = max(x0 - p[0], 0, p[0] - x1)
    fora_y = max(y0 - p[1], 0, p[1] - y1)
    if not dentro:
        return math.hypot(fora_x, fora_y)
    return min(p[0] - x0, x1 - p[0], p[1] - y0, y1 - p[1])


# O ponto está dentro do vértice?
def dentro_da_forma(p, forma):
    if "raio" in forma:
        return distancia(p, forma["centro"]) <= forma["raio"]
    x0, y0, x1, y1 = forma["caixa"]
    return x0 <= p[0] <= x1 and y0 <= p[1] <= y1


# A forma cuja borda está mais perto do ponto, se estiver a no máximo "tolerancia"
def forma_mais_proxima(p, formas, tolerancia):
    escolhida = None
    menor = None
    for i in range(len(formas)):
        limite = tolerancia(formas[i]) if callable(tolerancia) else tolerancia
        d = distancia_a_borda(p, formas[i])
        if d <= limite and (menor is None or d < menor):
            escolhida = i
            menor = d
    return escolhida


def mediana(valores):
    ordenados = sorted(valores)
    if not ordenados:
        return 0
    meio = len(ordenados) // 2
    if len(ordenados) % 2 == 1:
        return ordenados[meio]
    return (ordenados[meio - 1] + ordenados[meio]) / 2


# O ponto do meio de uma linha quebrada, medindo pelo comprimento (e não o ponto do meio da lista)
def ponto_do_meio(pontos):
    total = 0
    for i in range(len(pontos) - 1):
        total += distancia(pontos[i], pontos[i + 1])
    falta = total / 2
    for i in range(len(pontos) - 1):
        trecho = distancia(pontos[i], pontos[i + 1])
        if trecho >= falta and trecho > 0:
            t = falta / trecho
            return (pontos[i][0] + t * (pontos[i + 1][0] - pontos[i][0]),
                    pontos[i][1] + t * (pontos[i + 1][1] - pontos[i][1]))
        falta -= trecho
    return pontos[-1]
