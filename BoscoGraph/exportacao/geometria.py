# As contas de geometria que o PDF, o SVG e o PNG repetem para desenhar IGUAL ao Tkinter:
#   - a curva "suave" (smooth=True) das arestas;
#   - a ponta de seta (arrow="last");
#   - a curva e a elipse viradas em muitos pontinhos (para o PNG e para o tracejado);
#   - o tracejado (dash=(5, 4): 5 pixels de traço, 4 de espaço).
# Este arquivo não usa Tkinter: as contas são as mesmas do código do Tk (escrito em C), refeitas aqui.

import math


def meio(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


# A curva "smooth" do Tkinter (TkMakeBezierCurve): cada ponto do meio é o ponto de controle de uma
# Bézier quadrática que vai do meio do segmento anterior até o meio do próximo; a curva começa no
# primeiro ponto e termina no último. Devolve (início, cúbicas), cada cúbica = (c1, c2, fim).
# (Uma quadrática Q0-Q1-Q2 é a cúbica com C1 = Q0 + 2/3·(Q1 − Q0) e C2 = Q2 + 2/3·(Q1 − Q2).)
# Curva fechada (o primeiro ponto igual ao último): todos os trechos usam os pontos médios, como o Tk.
def cubicas_da_curva(pontos):
    fechada = len(pontos) > 3 and pontos[0] == pontos[-1]
    if fechada:
        pontos = [pontos[-2]] + list(pontos) + [pontos[1]]
    cubicas = []
    inicio = None
    for i in range(1, len(pontos) - 1):
        anterior, controle, seguinte = pontos[i - 1], pontos[i], pontos[i + 1]
        primeiro = i == 1 and not fechada
        ultimo = i == len(pontos) - 2 and not fechada
        q0 = anterior if primeiro else meio(anterior, controle)
        q2 = seguinte if ultimo else meio(controle, seguinte)
        if inicio is None:
            inicio = q0
        c1 = (q0[0] + 2 / 3 * (controle[0] - q0[0]), q0[1] + 2 / 3 * (controle[1] - q0[1]))
        c2 = (q2[0] + 2 / 3 * (controle[0] - q2[0]), q2[1] + 2 / 3 * (controle[1] - q2[1]))
        cubicas.append((c1, c2, q2))
    return inicio, cubicas


# Um ponto da cúbica P0-C1-C2-P3 no instante t (de 0 a 1): a fórmula de Bézier
#   B(t) = (1−t)³·P0 + 3(1−t)²t·C1 + 3(1−t)t²·C2 + t³·P3
def ponto_da_cubica(p0, c1, c2, p3, t):
    a = (1 - t) ** 3
    b = 3 * (1 - t) ** 2 * t
    c = 3 * (1 - t) * t ** 2
    d = t ** 3
    return (a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1])


# A linha virada em pontinhos: reta = os próprios pontos; suave = cada cúbica amostrada em "passos"
# pedaços (quem desenha só sabe fazer retas, como o Pillow, liga esses pontinhos)
def pontos_da_linha(pontos, suave, passos=16):
    pontos = [tuple(ponto) for ponto in pontos]
    if not suave or len(pontos) < 3:
        return pontos
    inicio, cubicas = cubicas_da_curva(pontos)
    resultado = [inicio]
    atual = inicio
    for c1, c2, fim in cubicas:
        for passo in range(1, passos + 1):
            resultado.append(ponto_da_cubica(atual, c1, c2, fim, passo / passos))
        atual = fim
    return resultado


# A elipse inscrita na caixa, virada em "quantidade" pontos (o primeiro se repete no fim)
def pontos_da_elipse(x0, y0, x1, y1, quantidade=72):
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    rx = abs(x1 - x0) / 2
    ry = abs(y1 - y0) / 2
    pontos = []
    for indice in range(quantidade + 1):
        angulo = 2 * math.pi * indice / quantidade
        pontos.append((cx + rx * math.cos(angulo), cy + ry * math.sin(angulo)))
    return pontos


# Corta uma linha (lista de pontos) nos traços do tracejado: devolve a lista dos traços, cada um uma
# lista de pontos. padrao = (traço, espaço, traço, espaço...), em pixels, como o dash do Tkinter.
def tracejar(pontos, padrao):
    if not padrao or min(padrao) <= 0:
        return [list(pontos)]
    if len(padrao) % 2 == 1:
        padrao = tuple(padrao) * 2      # como no Tk: (5,) vale (5, 5) — traço e espaço do mesmo tamanho
    tracos = []
    indice_do_padrao = 0
    falta = padrao[0]                   # quanto falta do pedaço atual do padrão
    desenhando = True                   # os pedaços pares são traço; os ímpares, espaço
    atual = [pontos[0]] if pontos else []
    for posicao in range(1, len(pontos)):
        inicio = pontos[posicao - 1]
        fim = pontos[posicao]
        comprimento = math.hypot(fim[0] - inicio[0], fim[1] - inicio[1])
        andado = 0.0
        while comprimento - andado > falta:
            andado += falta
            t = andado / comprimento
            ponto = (inicio[0] + (fim[0] - inicio[0]) * t, inicio[1] + (fim[1] - inicio[1]) * t)
            if desenhando:
                atual.append(ponto)
                tracos.append(atual)
                atual = []
            else:
                atual = [ponto]
            desenhando = not desenhando
            indice_do_padrao = (indice_do_padrao + 1) % len(padrao)
            falta = padrao[indice_do_padrao]
        falta -= comprimento - andado
        if desenhando:
            atual.append(fim)
    if desenhando and len(atual) >= 2:
        tracos.append(atual)
    return tracos


# A ponta de seta do Tkinter (ConfigureArrows): a ponta fica no último ponto; o polígono tem a ponta,
# as duas "asas" (a d2 para trás, deslocadas d3 + metade da espessura) e o "pescoço"; e a linha passa a
# terminar um pouco antes da ponta (o "recuo"), para não aparecer por baixo dela.
# Devolve (o polígono, o novo último ponto da linha).
def ponta_de_seta(antes, ponta, forma, espessura):
    d1 = forma[0] + 0.001
    d2 = forma[1] + 0.001
    d3 = forma[2] + espessura / 2 + 0.001
    fracao = (espessura / 2) / d3
    recuo = fracao * d2 + d1 * (1 - fracao) / 2
    dx = ponta[0] - antes[0]
    dy = ponta[1] - antes[1]
    comprimento = math.hypot(dx, dy)
    if comprimento == 0:
        seno = cosseno = 0.0
    else:
        seno = dy / comprimento
        cosseno = dx / comprimento
    vertice = (ponta[0] - d1 * cosseno, ponta[1] - d1 * seno)
    asa_1 = (ponta[0] - d2 * cosseno + d3 * seno, ponta[1] - d2 * seno - d3 * cosseno)
    asa_2 = (asa_1[0] - 2 * d3 * seno, asa_1[1] + 2 * d3 * cosseno)
    pescoco_1 = (asa_1[0] * fracao + vertice[0] * (1 - fracao), asa_1[1] * fracao + vertice[1] * (1 - fracao))
    pescoco_2 = (asa_2[0] * fracao + vertice[0] * (1 - fracao), asa_2[1] * fracao + vertice[1] * (1 - fracao))
    poligono = [ponta, asa_1, pescoco_1, pescoco_2, asa_2]
    novo_fim = (ponta[0] - recuo * cosseno, ponta[1] - recuo * seno)
    return poligono, novo_fim


# As setas de uma linha: devolve (os pontos da linha já encurtados, os polígonos das pontas).
# ponta = None, "fim", "inicio" ou "ambas" (o arrow do Tkinter: none, last, first, both)
def aplicar_pontas(pontos, ponta, forma, espessura):
    pontos = [tuple(ponto) for ponto in pontos]
    poligonos = []
    if len(pontos) < 2:
        return pontos, poligonos
    if ponta in ("fim", "ambas"):
        poligono, pontos[-1] = ponta_de_seta(pontos[-2], pontos[-1], forma, espessura)
        poligonos.append(poligono)
    if ponta in ("inicio", "ambas"):
        poligono, pontos[0] = ponta_de_seta(pontos[1], pontos[0], forma, espessura)
        poligonos.append(poligono)
    return pontos, poligonos
