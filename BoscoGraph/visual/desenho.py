# Geometria do desenho: onde fica cada vértice, por onde passa cada seta e onde vai cada texto.
# Só contas; quem desenha de verdade é a janela.
#
# Os tamanhos não são fixos: dependem da quantidade de vértices e do espaço
# que a janela tem no momento (a janela pode ser redimensionada).

import math

# Giro (em graus) do laço e do rótulo de um vértice que tem laço:
# o laço vai um pouco para um lado e o rótulo d/f para o outro, para não se cobrirem
GIRO_DO_LACO = -35
GIRO_DO_ROTULO_COM_LACO = 55


def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


# Calcula os tamanhos do desenho para uma área de largura x altura com essa quantidade de vértices.
# A distância entre dois vértices vizinhos no círculo é uma corda: 2 * R * sen(pi / n).
# O raio do vértice é uma fração dessa distância, para os vértices nunca se encostarem.
# raio_para_os_nomes: o raio que o nome mais comprido precisa para caber dentro do círculo.
# Nomes curtos (como "A") não mudam nada; nomes compridos deixam o vértice um pouco maior
# (até 40 pixels, vezes o zoom), se houver espaço. O resto do ajuste é feito diminuindo a fonte.
def calcular_medidas(quantidade, largura, altura, zoom, raio_para_os_nomes=0):
    menor_lado = min(largura, altura)
    raio_vertice = 22 * zoom
    raio_maximo = max(30 * zoom, min(raio_para_os_nomes, 40 * zoom))

    # Algumas rodadas: a margem depende do raio do vértice, e o raio depende do espaço que sobra.
    # A cada rodada os dois valores se aproximam do ponto em que um combina com o outro.
    for rodada in range(4):
        margem = raio_vertice * 2.6 + 14
        raio_circulo = max(menor_lado / 2 - margem, 10)
        if quantidade >= 2:
            espaco_entre_vizinhos = 2 * raio_circulo * math.sin(math.pi / quantidade)
        else:
            espaco_entre_vizinhos = raio_circulo
        raio_vertice = limitar(espaco_entre_vizinhos * 0.32, 8, raio_maximo)

    medidas = medidas_do_vertice(raio_vertice)
    medidas["centro"] = (largura / 2, altura / 2)
    medidas["raio_circulo"] = raio_circulo
    return medidas


# Tudo o que depende do tamanho do vértice: fontes, espessura das linhas e ponta da seta
def medidas_do_vertice(raio_vertice):
    return {
        "raio_vertice": raio_vertice,
        # tamanhos negativos no Tkinter = tamanho em pixels (acompanha o desenho)
        "fonte_vertice": -round(raio_vertice * 0.95),
        "fonte_rotulo": -round(limitar(raio_vertice * 0.62, 9, 18)),
        "espessura": limitar(raio_vertice / 11, 1, 3),
        "ponta_da_seta": (limitar(raio_vertice * 0.6, 6, 14),
                          limitar(raio_vertice * 0.75, 8, 17),
                          limitar(raio_vertice * 0.28, 3, 7)),
    }


# Posições dos vértices num círculo: o primeiro no topo e os outros em sentido horário
def posicoes_em_circulo(nomes, centro, raio):
    if len(nomes) == 1:
        return {nomes[0]: centro}
    posicoes = {}
    for i in range(len(nomes)):
        angulo = math.radians(-90 + i * 360 / len(nomes))
        x = centro[0] + raio * math.cos(angulo)
        y = centro[1] + raio * math.sin(angulo)
        posicoes[nomes[i]] = (x, y)
    return posicoes


# Ponto na borda do círculo de um vértice, na direção de um alvo
def ponto_na_borda(centro_do_vertice, alvo, raio_vertice):
    dx = alvo[0] - centro_do_vertice[0]
    dy = alvo[1] - centro_do_vertice[1]
    distancia = math.hypot(dx, dy)
    if distancia == 0:
        return centro_do_vertice
    return (centro_do_vertice[0] + dx / distancia * raio_vertice,
            centro_do_vertice[1] + dy / distancia * raio_vertice)


# Ponto que "puxa" a curva da seta.
# desvio_lateral: empurra a curva para um dos lados (arestas paralelas e arestas de ida e volta)
# puxar_para_o_centro: fração do caminho até o centro do desenho (cordas: a seta não passa por cima de outro vértice)
def ponto_de_controle(p1, p2, centro, desvio_lateral, puxar_para_o_centro):
    meio_x = (p1[0] + p2[0]) / 2
    meio_y = (p1[1] + p2[1]) / 2

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    comprimento = math.hypot(dx, dy)
    perpendicular_x = -dy / comprimento     # vetor de tamanho 1, perpendicular à reta p1 -> p2
    perpendicular_y = dx / comprimento
    meio_x = meio_x + perpendicular_x * desvio_lateral
    meio_y = meio_y + perpendicular_y * desvio_lateral

    meio_x = meio_x + (centro[0] - meio_x) * puxar_para_o_centro
    meio_y = meio_y + (centro[1] - meio_y) * puxar_para_o_centro
    return (meio_x, meio_y)


# Os três pontos da seta de uma aresta entre vértices diferentes: início, controle e fim.
# Início e fim ficam na borda dos círculos, para a ponta da seta não sumir dentro do vértice.
def pontos_da_seta(p1, p2, centro, raio_vertice, desvio_lateral, puxar_para_o_centro):
    controle = ponto_de_controle(p1, p2, centro, desvio_lateral, puxar_para_o_centro)
    inicio = ponto_na_borda(p1, controle, raio_vertice)
    fim = ponto_na_borda(p2, controle, raio_vertice)
    return [inicio, controle, fim]


# Os pontos de um laço (aresta de um vértice para ele mesmo): um pequeno círculo encostado no vértice.
# "numero" é qual laço deste vértice (0 = primeiro); o segundo laço fica girado para o lado.
def pontos_do_laco(p, centro, raio_vertice, numero):
    if p == centro:
        direcao = math.radians(-90 + GIRO_DO_LACO - 60 * numero)
    else:
        direcao = (math.atan2(p[1] - centro[1], p[0] - centro[0])
                   + math.radians(GIRO_DO_LACO - 60 * numero))
    raio_laco = raio_vertice * 0.75
    distancia = raio_vertice + 0.6 * raio_laco      # o centro do laço fica um pouco para fora do vértice
    centro_laco = (p[0] + distancia * math.cos(direcao),
                   p[1] + distancia * math.sin(direcao))

    # Lei dos cossenos: o ângulo (visto do centro do laço) em que o laço encosta na borda do vértice
    cos_alfa = (raio_laco ** 2 + distancia ** 2 - raio_vertice ** 2) / (2 * raio_laco * distancia)
    alfa = math.acos(cos_alfa)

    # Percorre o laço pelo lado de fora do vértice, de um ponto de contato até o outro
    comeco = direcao + math.pi + alfa
    volta = 2 * math.pi - 2 * alfa
    pontos = []
    for i in range(13):
        angulo = comeco + volta * i / 12
        pontos.append((centro_laco[0] + raio_laco * math.cos(angulo),
                       centro_laco[1] + raio_laco * math.sin(angulo)))
    return pontos


# Onde escrever o nome de uma aresta: no meio da curva.
# - Seta (3 pontos): com smooth=True e 3 pontos, o Tkinter desenha uma curva de Bézier quadrática.
#   O ponto do meio dela (t = 0,5 na fórmula da Bézier) é (início + 2 x controle + fim) / 4.
# - Laço (13 pontos): o ponto do meio do laço (o mais longe do vértice), empurrado um pouco
#   para fora ("afastamento" pixels), para o nome não ficar em cima da linha do laço.
def ponto_do_nome_da_aresta(pontos, afastamento):
    if len(pontos) == 3:
        inicio, controle, fim = pontos
        return ((inicio[0] + 2 * controle[0] + fim[0]) / 4,
                (inicio[1] + 2 * controle[1] + fim[1]) / 4)
    meio = pontos[len(pontos) // 2]
    # A base do laço fica entre o primeiro e o último ponto (onde ele encosta no vértice)
    base_x = (pontos[0][0] + pontos[-1][0]) / 2
    base_y = (pontos[0][1] + pontos[-1][1]) / 2
    dx = meio[0] - base_x
    dy = meio[1] - base_y
    distancia = math.hypot(dx, dy)
    if distancia == 0:
        return meio
    return (meio[0] + dx / distancia * afastamento, meio[1] + dy / distancia * afastamento)


# Posição e âncora do rótulo d/f: do lado de fora do círculo, sem encostar no vértice.
# A âncora diz que ponta do texto fica presa na posição:
# "w" = o texto começa ali e cresce para a direita; "e" = cresce para a esquerda;
# "s" = o texto fica acima do ponto; "n" = o texto fica abaixo do ponto.
def rotulo_do_vertice(p, centro, distancia, giro_em_graus):
    if p == centro:
        angulo = math.radians(-90 + giro_em_graus)
    else:
        angulo = math.atan2(p[1] - centro[1], p[0] - centro[0]) + math.radians(giro_em_graus)
    x = p[0] + distancia * math.cos(angulo)
    y = p[1] + distancia * math.sin(angulo)
    if math.cos(angulo) > 0.35:
        ancora = "w"
    elif math.cos(angulo) < -0.35:
        ancora = "e"
    elif math.sin(angulo) < 0:
        ancora = "s"
    else:
        ancora = "n"
    return x, y, ancora


# Calcula os pontos de todas as setas, na ordem da lista de arestas.
# curvar_cordas=False: nenhuma seta é puxada para o centro (arrumação "como no arquivo", em que os
# vértices não estão num círculo e as linhas retas são as do desenho original).
def pontos_de_todas_as_arestas(arestas, posicoes, nomes, centro, raio_vertice, curvar_cordas=True):
    # Quantas vezes cada par aparece (arestas paralelas) e quantos laços cada vértice tem
    quantidade_do_par = {}
    for par in arestas:
        quantidade_do_par[par] = quantidade_do_par.get(par, 0) + 1

    ja_desenhadas = {}      # quantas vezes cada par já foi calculado neste laço de repetição
    pontos = []
    for origem, destino in arestas:
        vez = ja_desenhadas.get((origem, destino), 0)
        ja_desenhadas[(origem, destino)] = vez + 1

        if origem == destino:
            pontos.append(pontos_do_laco(posicoes[origem], centro, raio_vertice, vez))
            continue

        # Desvio para o lado:
        # - se existe a aresta de volta (destino -> origem), cada sentido curva para o seu lado;
        # - se há arestas paralelas, a 1ª curva para um lado e a 2ª para o outro.
        base = raio_vertice * 1.3
        desvio_lateral = 0
        if (destino, origem) in quantidade_do_par:
            desvio_lateral = base * 0.8 * (vez + 1)
        elif quantidade_do_par[(origem, destino)] > 1:
            if vez % 2 == 0:
                desvio_lateral = base * (vez // 2 + 1)
            else:
                desvio_lateral = -base * (vez // 2 + 1)

        # Vizinhos no círculo: seta reta. Cordas: curva puxada para o centro.
        distancia_no_circulo = abs(nomes.index(origem) - nomes.index(destino))
        distancia_no_circulo = min(distancia_no_circulo, len(nomes) - distancia_no_circulo)
        puxar_para_o_centro = 0
        if distancia_no_circulo > 1 and curvar_cordas:
            puxar_para_o_centro = 0.28

        pontos.append(pontos_da_seta(posicoes[origem], posicoes[destino], centro,
                                     raio_vertice, desvio_lateral, puxar_para_o_centro))
    return pontos


# ----------------------------------------------------------------------
# Arrumação em linha: a ordem topológica de um DAG
# ----------------------------------------------------------------------
# Os vértices ficam numa linha, da esquerda para a direita, na ordem topológica.
# Cada aresta vira um arco por cima da linha. Num DAG, todas as setas apontam para a direita.

# Medidas do desenho em linha para uma área de largura x altura
def medidas_da_linha(quantidade, largura, altura, zoom, raio_para_os_nomes=0):
    raio_maximo = max(30 * zoom, min(raio_para_os_nomes, 40 * zoom))
    margem = 18
    raio_vertice = raio_maximo
    if quantidade >= 2:
        distancia_entre_vizinhos = (largura - 2 * margem) / quantidade
        raio_vertice = limitar(distancia_entre_vizinhos * 0.34, 8, raio_maximo)
    medidas = medidas_do_vertice(raio_vertice)
    medidas["margem"] = raio_vertice + margem
    # A linha fica a 70% da altura: o espaço de cima é dos arcos, o de baixo é dos rótulos d/f
    medidas["y_da_linha"] = altura * 0.70
    medidas["espaco_acima"] = max(20, medidas["y_da_linha"] - raio_vertice - 8)
    return medidas


# Posições dos vértices em linha, na ordem dada; "topo" é onde a área de desenho começa
def posicoes_em_linha(nomes, largura, medidas, topo):
    y = topo + medidas["y_da_linha"]
    if len(nomes) == 1:
        return {nomes[0]: (largura / 2, y)}
    esquerda = medidas["margem"]
    direita = largura - medidas["margem"]
    distancia = (direita - esquerda) / (len(nomes) - 1)
    posicoes = {}
    for i in range(len(nomes)):
        posicoes[nomes[i]] = (esquerda + i * distancia, y)
    return posicoes


# Os três pontos do arco de cada aresta (início, controle e fim), na ordem da lista de arestas.
# A altura do arco cresce com a distância entre os vértices, para os arcos não se sobreporem tanto.
# Numa Bézier quadrática, o ponto mais alto da curva fica na METADE da altura do ponto de controle,
# por isso o controle sobe o dobro do "pico" que queremos.
def pontos_em_arco(pares, posicoes, raio_vertice, espaco_acima):
    ja_desenhadas = {}
    pontos = []
    for origem, destino in pares:
        vez = ja_desenhadas.get((origem, destino), 0)       # arestas paralelas: a 2ª fica mais alta
        ja_desenhadas[(origem, destino)] = vez + 1
        p1 = posicoes[origem]
        p2 = posicoes[destino]
        if origem == destino:
            # Laço (não acontece num DAG, mas o desenho não pode quebrar): um laço por cima do vértice
            pontos.append(pontos_do_laco(p1, (p1[0], p1[1] + 100), raio_vertice, vez))
            continue
        distancia = abs(p2[0] - p1[0])
        pico = (distancia * 0.30 + raio_vertice) * (1 + 0.35 * vez)
        pico = min(pico, espaco_acima)
        controle = ((p1[0] + p2[0]) / 2, min(p1[1], p2[1]) - 2 * pico)
        inicio = ponto_na_borda(p1, controle, raio_vertice)
        fim = ponto_na_borda(p2, controle, raio_vertice)
        pontos.append([inicio, controle, fim])
    return pontos


# ----------------------------------------------------------------------
# Arrumação "como no arquivo": as posições vêm do desenho importado (draw.io, GraphML, PDF, foto...)
# ----------------------------------------------------------------------
# O desenho original é encaixado na área disponível sem distorcer: a mesma escala nos dois eixos
# (senão um círculo do desenho viraria uma elipse), centralizado e com margem para os rótulos.

# Medidas do desenho "como no arquivo" para uma área de largura x altura.
#   originais -> {vértice: (x, y)} no sistema do arquivo (y cresce para baixo, como na tela)
def medidas_livres(nomes, originais, largura, altura, zoom, raio_para_os_nomes=0):
    xs = []
    ys = []
    for nome in nomes:
        xs.append(originais[nome][0])
        ys.append(originais[nome][1])
    menor_x = min(xs)
    menor_y = min(ys)
    largura_original = max(xs) - menor_x
    altura_original = max(ys) - menor_y

    raio_maximo = max(30 * zoom, min(raio_para_os_nomes, 40 * zoom))
    raio_vertice = 22 * zoom
    escala = 1
    # Como no círculo: a margem depende do raio, e o raio depende da escala (algumas rodadas)
    for rodada in range(4):
        margem = raio_vertice * 2.6 + 14
        escalas = []
        if largura_original > 0:
            escalas.append(max(largura - 2 * margem, 10) / largura_original)
        if altura_original > 0:
            escalas.append(max(altura - 2 * margem, 10) / altura_original)
        if escalas:
            escala = min(escalas)            # o eixo que ficaria mais apertado decide a escala
        # A menor distância entre dois vértices, já na escala da tela
        menor_distancia = None
        for i in range(len(nomes)):
            for j in range(i + 1, len(nomes)):
                distancia = math.hypot(xs[i] - xs[j], ys[i] - ys[j]) * escala
                if menor_distancia is None or distancia < menor_distancia:
                    menor_distancia = distancia
        if menor_distancia is None:
            menor_distancia = min(largura, altura) / 2      # um vértice só
        raio_vertice = limitar(menor_distancia * 0.32, 8, raio_maximo)

    medidas = medidas_do_vertice(raio_vertice)
    medidas["escala"] = escala
    medidas["canto_original"] = (menor_x, menor_y)
    # Sobra de espaço dividida igualmente dos dois lados: o desenho fica centralizado
    medidas["deslocamento"] = ((largura - largura_original * escala) / 2,
                               (altura - altura_original * escala) / 2)
    return medidas


# Posições na tela; "topo" é onde a área de desenho começa
def posicoes_livres(nomes, originais, medidas, topo):
    escala = medidas["escala"]
    canto_x, canto_y = medidas["canto_original"]
    deslocamento_x, deslocamento_y = medidas["deslocamento"]
    posicoes = {}
    for nome in nomes:
        x, y = originais[nome]
        posicoes[nome] = (deslocamento_x + (x - canto_x) * escala,
                          topo + deslocamento_y + (y - canto_y) * escala)
    return posicoes


# O centro de massa dos vértices (a média das posições): é para "fora" dele que vão os laços
# e os rótulos d/f na arrumação livre
def centro_das_posicoes(posicoes):
    soma_x = 0
    soma_y = 0
    for nome in posicoes:
        soma_x += posicoes[nome][0]
        soma_y += posicoes[nome][1]
    return (soma_x / len(posicoes), soma_y / len(posicoes))
