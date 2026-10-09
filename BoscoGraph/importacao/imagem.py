'''
    Fase 3 da importação: foto ou imagem de um grafo (PNG, JPG...). É a fase que mais erra:
    numa imagem não existem "objetos", só pixels, e tudo precisa ser deduzido. Por isso o
    resultado sempre passa pela conferência (o reconhecido aparece por cima da imagem).

    Bibliotecas: OpenCV (cv2) e NumPy para a imagem; Tesseract (pelo pytesseract) para ler os textos.
    Sem o Tesseract, a importação funciona do mesmo jeito, mas os vértices ganham nomes automáticos.

    O caminho, passo a passo:
      1. Ler a imagem e deixar num tamanho padrão (o lado maior com uns 1200 pixels).
      2. "Tinta": separar o que é desenho (escuro) do fundo (claro), comparando cada pixel com a
         vizinhança (limiar adaptativo): funciona mesmo com a luz desigual de uma foto. Fundo escuro
         (tema escuro) é invertido antes; a grade de fundo de um programa de desenho é tirada.
      3. Vértices: os "buracos" redondos (círculos, elipses) ou retangulares (caixas) da tinta, e as
         manchas pintadas (vértices cheios de cor). A medida de "redondo" é a circularidade =
         4π·área / perímetro² (1 num círculo perfeito, menos em qualquer outra forma). Os buracos das
         letras ("A", "0") são separados pelo tamanho e pela grossura do anel em volta.
      4. Arestas: com os vértices apagados, cada mancha de tinta que encosta em dois vértices é uma
         aresta (em dois pontos do mesmo vértice, um laço). Linhas que se cruzam são separadas pelo
         caminho mais reto; duas ligações que dividem um trecho (junção em T) vão para o vértice do tronco.
      5. Setas: perto de uma ponta com seta, a tinta fica bem mais larga (o triângulo) do que no
         resto da linha.
      6. Textos: o nome dentro de cada vértice e, apagadas as linhas, os rótulos das arestas (OCR),
         com correções que usam o resto do desenho (maiúsculas, "R1" lido como "Ri", "l" no lugar de "1").
    E a montagem (importacao/montagem.py) junta tudo, com as mesmas regras do PDF.

    Medido nos testes (testes_importacao.py, 9h), em grafos sorteados desenhados pelo Graphviz:
    imagens limpas -> nomes 100%, ligações e sentidos 90%, pesos 92%;
    fotos sintéticas -> nomes 72% (as fotos pequenas e borradas são as que mais erram), ligações 90%,
    pesos 86%; tema escuro com grade e vértices pintados -> nomes 85%, ligações 85%, pesos 76%.
    Por isso a conferência existe: o que foi reconhecido aparece por cima da imagem.
'''

import math
import os
import re
import shutil
import sys
from collections import deque
from pathlib import Path

import caminhos
import entrada
from entrada import contar
from importacao import ProblemaNaImportacao
from importacao import geometria
from importacao import montagem

LADO_PADRAO = 1200                  # tamanho de trabalho: o lado maior da imagem, em pixels
AUMENTO_MAXIMO = 2.5                # uma imagem pequena é aumentada no máximo 2,5 vezes
TAMANHO_DA_PREVIA = 520             # o lado maior da imagem da conferência
# Letras aceitas nos nomes (o OCR só "procura" estas: erra menos). As acentuadas ficam para uma
# segunda tentativa: com elas, o "5" de "R5" já foi lido como "ô" no teste.
LETRAS_DO_OCR = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
LETRAS_ACENTUADAS = "ÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç"


def carregar_opencv():
    try:
        import cv2
        import numpy
    except ImportError:
        if caminhos.esta_empacotado():
            raise ProblemaNaImportacao("Esta instalação do BoscoGraph foi gerada sem a leitura de imagens.")
        raise ProblemaNaImportacao("Para importar imagens, instale o OpenCV e o NumPy: "
                                   "pip install opencv-python-headless numpy")
    try:
        cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)    # sem avisos no terminal
    except AttributeError:
        pass
    return cv2, numpy


def ler_imagem(caminho):
    cv2, np = carregar_opencv()
    original = ler_arquivo_de_imagem(caminho, cv2, np)
    imagem, escala = no_tamanho_padrao(original, cv2)
    cinza, invertida = com_fundo_claro(cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY), np)
    tinta = separar_a_tinta(cinza, cv2, np)
    espessura = espessura_das_linhas(tinta, cv2, np)

    formas = achar_vertices(tinta, imagem, espessura, cv2, np)
    if not formas:
        raise ProblemaNaImportacao("Não encontrei vértices (círculos ou caixas) na imagem. Ajuda: foto de frente, "
                                   "bem iluminada, com os vértices desenhados como círculos fechados.")
    avisos = []
    ocr = carregar_ocr()
    if ocr is None:
        avisos.append("O leitor de texto (Tesseract) não está instalado: os vértices ganharam nomes automáticos "
                      "e os rótulos das arestas não foram lidos. Veja o LEIAME para instalar.")

    # Os nomes dentro dos vértices (cada vértice é lido sozinho: o OCR acerta mais)
    textos = []
    duvidosos = []
    alturas_das_letras = []
    if ocr is not None:
        for forma in formas:
            texto, confianca, caixa, altura_das_letras = ler_dentro_da_forma(cinza, forma, espessura, ocr, cv2, np)
            if texto:
                textos.append({"texto": texto, "caixa": caixa, "confianca": confianca})
                alturas_das_letras.append(altura_das_letras)
        correcoes = corrigir_nomes(textos)
        if correcoes:
            avisos.append("Nomes corrigidos pelo padrão dos outros (o leitor confunde 1 com i, 5 com S...): "
                          + ", ".join(correcoes[:6]) + ". Confira.")
        for texto in textos:
            if texto["confianca"] < 60:
                duvidosos.append(texto["texto"])

    # As arestas: a tinta que sobra quando os vértices são apagados
    resto = apagar_formas(tinta, formas, espessura, cv2, np)
    tracos, cruzamentos, manchas = achar_arestas(resto, formas, espessura, cv2, np)
    if cruzamentos:
        avisos.append(contar(cruzamentos, "lugar em que linhas se cruzam ou se juntam",
                             "lugares em que linhas se cruzam ou se juntam") + ": confira se alguma aresta faltou.")

    # Os rótulos das arestas: com as linhas e as setas apagadas, o que sobra perto delas é texto
    if ocr is not None and tracos:
        tipico = geometria.mediana([montagem.tamanho_da_forma(forma) for forma in formas])
        sobra = apagar_linhas(resto, tracos, manchas, espessura, tipico, cv2, np)
        # A altura de referência das letras: a dos nomes lidos; sem nomes, uns 30% do tamanho de um vértice
        altura_das_letras = geometria.mediana(alturas_das_letras) or 0.3 * tipico
        rotulos = ler_rotulos(sobra, ocr, cv2, np, altura_das_letras)
        trocas = corrigir_numeros(rotulos)
        if trocas:
            avisos.append("Rótulos lidos como letra e trocados por número (o leitor confunde l com 1 e O com 0): "
                          + ", ".join(trocas[:6]) + ". Confira.")
        for texto in rotulos:
            textos.append(texto)

    bruto = montagem.montar(formas, tracos, [], textos)
    bruto["avisos"] = avisos + bruto["avisos"]
    if duvidosos:
        bruto["avisos"].append("Nomes lidos com pouca certeza (confira): " + ", ".join(duvidosos[:6]) + ".")
    bruto["imagem"], escala_da_previa = imagem_da_previa(imagem, cv2)
    bruto["marcas"] = marcas_na_escala(bruto, escala_da_previa)
    return bruto


# ----------------------------------------------------------------------
# 1. Ler e padronizar
# ----------------------------------------------------------------------

# cv2.imread não abre arquivos com acento no caminho no Windows ("8º Período"...). Por isso o
# arquivo é lido como bytes pelo NumPy e decodificado pelo OpenCV (imdecode).
def ler_arquivo_de_imagem(caminho, cv2, np):
    try:
        dados = np.fromfile(str(caminho), dtype=np.uint8)
    except OSError as erro:
        raise ProblemaNaImportacao(f"Não consegui ler a imagem: {erro}")
    imagem = cv2.imdecode(dados, cv2.IMREAD_UNCHANGED)
    if imagem is None:
        raise ProblemaNaImportacao("Esse arquivo não é uma imagem que eu consiga abrir (use PNG ou JPG).")
    if imagem.ndim == 2:
        imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)
    elif imagem.shape[2] == 4:
        # Fundo transparente: o desenho é colocado sobre branco (senão o transparente viraria preto)
        alfa = imagem[:, :, 3:4].astype(np.float32) / 255
        cores = imagem[:, :, :3].astype(np.float32)
        imagem = (cores * alfa + 255 * (1 - alfa)).astype(np.uint8)
    return imagem


# Deixa o lado maior com LADO_PADRAO pixels: as medidas (espessura, tamanho mínimo de um vértice...)
# passam a valer para qualquer foto, de celular ou de captura de tela. Uma imagem pequena é aumentada
# no máximo AUMENTO_MAXIMO vezes: aumentar mais não cria detalhe nenhum, só deixa os buracos das
# letras e dos números do tamanho de um vértice.
def no_tamanho_padrao(imagem, cv2):
    altura, largura = imagem.shape[:2]
    escala = min(LADO_PADRAO / max(altura, largura), AUMENTO_MAXIMO)
    if abs(escala - 1) < 0.05:
        return imagem, 1.0
    metodo = cv2.INTER_AREA if escala < 1 else cv2.INTER_CUBIC     # reduzir: média; aumentar: suave
    return cv2.resize(imagem, None, fx=escala, fy=escala, interpolation=metodo), escala


# ----------------------------------------------------------------------
# 2. Tinta
# ----------------------------------------------------------------------

# As linhas da grade numa direção. "cobertura" diz, para cada linha de pixels (ou coluna), a fração
# coberta por tinta fraca. As linhas com mais de 30% formam "faixas" (uma linha da grade tem uns 3
# pixels de grossura). É grade se pelo menos 3 faixas caem num "pente" regular (o começo mais um
# múltiplo do espaçamento, com 3 pixels de folga), quase sem dentes faltando (80%) e atravessando
# mais da metade da imagem. Faixas fora do pente (a borda de uma aresta comprida) ficam de fora;
# a moldura de uma página (só duas linhas) não é grade.
# Devolve as faixas da grade (cada uma, a lista das linhas de pixels dela).
def faixas_da_grade(cobertura, tamanho, np):
    faixas = []
    for indice in np.where(cobertura > 0.3)[0]:
        if faixas and indice - faixas[-1][-1] <= 2:
            faixas[-1].append(int(indice))
        else:
            faixas.append([int(indice)])
    if len(faixas) < 3:
        return []
    centros = []
    for faixa in faixas:
        centros.append((faixa[0] + faixa[-1]) / 2)
    melhor = []
    melhor_posicoes = 0
    for a in range(len(centros)):
        for b in range(a + 1, len(centros)):
            passo = centros[b] - centros[a]
            if passo < 8:
                continue
            no_pente = []
            posicoes = []                       # quais "dentes" do pente têm faixa (cada dente conta uma vez)
            for k in range(len(centros)):
                vezes = (centros[k] - centros[a]) / passo
                if abs(vezes - round(vezes)) * passo <= 3:
                    no_pente.append(k)
                    if round(vezes) not in posicoes:
                        posicoes.append(round(vezes))
            # O pente precisa ter pelo menos 3 dentes com faixa, quase sem falhas entre o primeiro e o
            # último (80% dos dentes do meio preenchidos) e atravessar mais da metade da imagem
            if len(posicoes) < 3:
                continue
            seguidos = max(posicoes) - min(posicoes) + 1
            if len(posicoes) >= 0.8 * seguidos and (seguidos - 1) * passo >= 0.5 * tamanho and \
                    len(posicoes) > melhor_posicoes:
                melhor = no_pente
                melhor_posicoes = len(posicoes)
    resultado = []
    for k in melhor:
        resultado.append(faixas[k])
    return resultado


# Fundo escuro (tema escuro, quadro-negro, tela de celular): a "tinta" é mais CLARA que o fundo.
# O resto do programa supõe tinta escura em fundo claro; por isso a imagem em tons de cinza é
# invertida (255 - valor). O fundo é a maioria dos pixels: a mediana diz se ele é claro ou escuro.
# Devolve a imagem (invertida ou não) e se inverteu.
def com_fundo_claro(cinza, np):
    if np.median(cinza) < 110:
        return 255 - cinza, True
    return cinza, False


# Branco = tinta, preto = fundo (o contrário da imagem). O limiar adaptativo compara cada pixel com a
# média da vizinhança: um pixel é tinta se for bem mais escuro que os vizinhos. Assim a sombra de
# um canto da foto não vira "tinta".
# A GRADE de fundo dos programas de desenho (o draw.io exporta a grade junto) também é um pouco mais
# escura que o fundo, e viraria tinta ligando tudo com tudo. Ela é reconhecida por ser
#   - fraca: só um pouco mais escura que o fundo (menos de 1/4 do contraste da tinta de verdade);
#   - feita de linhas horizontais e verticais que atravessam a imagem: numa linha (ou coluna) de
#     pixels da grade, a tinta fraca cobre mais de 30% do comprimento (mesmo interrompida pelos vértices);
#   - REGULAR: as linhas da grade se repetem com o mesmo espaçamento (veja faixas_da_grade). Uma aresta
#     comprida e reta também cobre muito de uma coluna (a borda clarinha dela é fraca), mas é uma só.
# Achada a grade (numa direção já basta: os vértices tapam pedaços dela), a imagem passa a usar só a
# tinta FORTE, e a grade some inteira. Uma aresta que passa por cima da grade fica: ela é forte.
# (Medido: só mexer no limiar de tudo atrapalhava as outras imagens; afinava as setas e os números.)
# Depois, os pontinhos isolados (ruído) são apagados.
def separar_a_tinta(cinza, cv2, np):
    suave = cv2.GaussianBlur(cinza, (3, 3), 0)
    vizinhanca = 51                                  # tamanho (ímpar) da vizinhança comparada
    tinta = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                  vizinhanca, 15)
    contraste = float(np.median(suave)) - float(np.percentile(suave, 1))
    forte = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                  vizinhanca, max(15.0, 0.25 * contraste))
    so_fraca = (tinta > 0) & (forte == 0)
    altura, largura = tinta.shape
    # mean(axis=1): a fração coberta em cada linha de pixels; mean(axis=0): em cada coluna
    if faixas_da_grade(so_fraca.mean(axis=1), altura, np) or faixas_da_grade(so_fraca.mean(axis=0), largura, np):
        tinta = forte
    quantidade, rotulos, estatisticas, centros = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    for k in range(1, quantidade):
        if estatisticas[k, cv2.CC_STAT_AREA] < 12:
            tinta[rotulos == k] = 0
    return tinta


# A espessura típica das linhas: a "transformada de distância" diz, para cada pixel de tinta, a que
# distância está do fundo; no meio de uma linha, isso é metade da espessura
def espessura_das_linhas(tinta, cv2, np):
    distancias = cv2.distanceTransform(tinta, cv2.DIST_L2, 3)
    valores = distancias[distancias > 0]
    if valores.size == 0:
        return 2.0
    return max(1.5, 2 * float(np.percentile(valores, 75)))


# ----------------------------------------------------------------------
# 3. Vértices
# ----------------------------------------------------------------------

# Os vértices são procurados de dois jeitos, e os achados se juntam:
#   1. pelos BURACOS da tinta: um círculo (ou caixa) desenhado só com a borda deixa, por dentro, um
#      buraco do formato dele, mesmo com as linhas das arestas encostando por fora;
#   2. pelas MANCHAS PINTADAS: um vértice pintado por dentro (o círculo verde com o nome em branco do
#      tema escuro do draw.io) é uma mancha grossa de cor bem diferente da do fundo (veja manchas_pintadas).
# Mas as letras e os números também têm buracos ("A", "B", "0", "8"...). Medidas em 120 grafos sorteados
# do Graphviz, com e sem efeito de foto, separaram os dois casos por duas contas:
#   - tamanho: o raio do buraco de um vértice tem pelo menos 8,5 vezes a espessura da linha; o buraco
#     de uma letra, no máximo 4,5 vezes. Limite: 5 vezes.
#   - anel fino: numa faixa em volta do buraco (de largura igual a meio raio), um vértice tem pouca
#     tinta (a borda e o começo das arestas: no máximo 27% da faixa); uma letra tem muita (o traço
#     dela é grosso perto do buraco: de 52% a 100%). Limite: 45%.
def achar_vertices(tinta, imagem, espessura, cv2, np):
    altura, largura = tinta.shape
    menor_raio = max(9, 5 * espessura)
    maior_raio = 0.5 * min(altura, largura)         # precisa caber na imagem (a moldura da página não cabe)
    candidatos = []
    # 1. Os buracos. RETR_CCOMP: os contornos de fora e os buracos (os buracos têm um "pai" na hierarquia)
    contornos, hierarquia = cv2.findContours(tinta, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    for i in range(len(contornos)):
        if hierarquia[0][i][3] < 0:
            continue                                    # não é buraco
        # O buraco é a parte de DENTRO da borda: a borda de fora fica uma espessura além
        achado = forma_do_contorno(contornos[i], espessura, menor_raio, maior_raio, cv2)
        if achado is None:
            continue
        forma, raio_do_buraco = achado
        if tinta_em_volta(tinta, contornos[i], raio_do_buraco, cv2, np) > 0.45:
            continue                                    # anel grosso: o buraco de uma letra
        candidatos.append(forma)
    # 2. As manchas pintadas (a mancha já inclui a borda: nada a somar)
    for contorno in manchas_pintadas(imagem, espessura, cv2, np):
        achado = forma_do_contorno(contorno, 0, menor_raio, maior_raio, cv2)
        if achado is not None:
            candidatos.append(achado[0])

    # Junta repetidos (o anel de fora e o buraco do mesmo círculo) e tira o que está dentro de outro
    # vértice (a letra "O" dentro de um vértice também é redonda!)
    # E tira o que está ENCOSTADO num vértice maior: a volta de um laço, junto com a borda do vértice,
    # também fecha um buraco redondo. Dois vértices de verdade não se encostam (há espaço entre eles).
    candidatos.sort(key=lambda forma: -montagem.tamanho_da_forma(forma))
    formas = []
    for candidato in candidatos:
        dentro_de_outro = False
        for forma in formas:
            if geometria.dentro_da_forma(candidato["centro"], forma):
                dentro_de_outro = True
            vao = geometria.distancia(candidato["centro"], forma["centro"]) - \
                montagem.tamanho_da_forma(candidato) / 2 - montagem.tamanho_da_forma(forma) / 2
            if vao < 2 * espessura:
                dentro_de_outro = True
        if not dentro_de_outro:
            formas.append(candidato)
    if formas:
        tipico = geometria.mediana([montagem.tamanho_da_forma(forma) for forma in formas])
        sem_pequenos = []
        for forma in formas:
            if montagem.tamanho_da_forma(forma) >= 0.45 * tipico:
                sem_pequenos.append(forma)
        formas = sem_pequenos
    # Na ordem de leitura: de cima para baixo e da esquerda para a direita
    tipico = geometria.mediana([montagem.tamanho_da_forma(forma) for forma in formas]) if formas else 1
    formas.sort(key=lambda forma: (round(forma["centro"][1] / tipico), forma["centro"][0]))
    return formas


# Que forma de vértice um contorno tem: caixa, círculo ou elipse (ou nenhuma). "borda" é quanto somar
# em volta (a espessura da borda, quando o contorno é o buraco de dentro dela).
# Devolve (a forma, o raio de dentro) ou None.
def forma_do_contorno(contorno, borda, menor_raio, maior_raio, cv2):
    area = cv2.contourArea(contorno)
    if area < math.pi * 9 ** 2:
        return None
    perimetro = cv2.arcLength(contorno, True)
    if perimetro == 0:
        return None
    circularidade = 4 * math.pi * area / perimetro ** 2
    (cx, cy), raio = cv2.minEnclosingCircle(contorno)
    if raio > maior_raio:
        return None
    preenchimento = area / (math.pi * raio ** 2)
    x, y, w, h = cv2.boundingRect(contorno)
    retangular = area / float(w * h)
    forma = None
    raio_de_dentro = 0
    # Quanto da caixa em volta o contorno ocupa: retângulo ~1; círculo e elipse, π/4 ~ 0,785.
    # Por isso a caixa é testada primeiro (um retângulo de cantos redondos também é "quase redondo").
    if retangular > 0.85 and min(w, h) >= 2 * menor_raio and max(w, h) < 5 * min(w, h):
        forma = {"centro": (x + w / 2, y + h / 2), "caixa": (x - borda, y - borda, x + w + borda, y + h + borda)}
        raio_de_dentro = min(w, h) / 2
    elif circularidade > 0.78 and preenchimento > 0.78:
        forma = {"centro": (cx, cy), "raio": raio + borda}
        raio_de_dentro = raio
    elif len(contorno) >= 5 and circularidade > 0.7:
        # Elipse (um círculo visto de lado, numa foto inclinada)
        (ex, ey), (eixo_1, eixo_2), angulo = cv2.fitEllipse(contorno)
        area_da_elipse = math.pi * eixo_1 * eixo_2 / 4
        if area_da_elipse > 0 and area / area_da_elipse > 0.9 and max(eixo_1, eixo_2) < 2.2 * min(eixo_1, eixo_2):
            forma = {"centro": (ex, ey), "raio": (eixo_1 + eixo_2) / 4 + borda}
            raio_de_dentro = min(eixo_1, eixo_2) / 2
    if forma is None or raio_de_dentro < menor_raio:
        return None
    return forma, raio_de_dentro


# As manchas grossas de cor bem diferente da do fundo (os vértices pintados por dentro).
#   - o fundo é a cor mais comum: a mediana de cada canal (azul, verde e vermelho);
#   - "bem diferente": a maior diferença entre os três canais passa de um limite que depende do
#     contraste do desenho (assim a grade de fundo, só um pouco diferente, fica de fora);
#   - a "abertura" da morfologia (opening: encolher e depois engordar com um disco) apaga o que é mais
#     fino que o disco (linhas, letras soltas) e deixa as manchas grossas do jeito que eram.
# Devolve os contornos das manchas que sobraram.
def manchas_pintadas(imagem, espessura, cv2, np):
    fundo = np.median(imagem.reshape(-1, 3), axis=0)
    diferenca = np.abs(imagem.astype(np.int16) - fundo.astype(np.int16)).max(axis=2)
    limite = max(40.0, 0.35 * float(np.percentile(diferenca, 99)))
    mancha = (diferenca > limite).astype(np.uint8) * 255
    raio = max(3, int(round(1.5 * espessura)))
    disco = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    grossas = cv2.morphologyEx(mancha, cv2.MORPH_OPEN, disco)
    contornos, hierarquia = cv2.findContours(grossas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contornos


# A fração de tinta numa faixa em volta do buraco (de largura igual a meio raio). Para ser rápido,
# a conta é feita só num recorte em volta do buraco.
def tinta_em_volta(tinta, contorno, raio, cv2, np):
    altura, largura = tinta.shape
    faixa = max(1, int(round(0.5 * raio)))
    x, y, w, h = cv2.boundingRect(contorno)
    x0, y0 = max(0, x - faixa - 1), max(0, y - faixa - 1)
    x1, y1 = min(largura, x + w + faixa + 1), min(altura, y + h + faixa + 1)
    buraco = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
    cv2.drawContours(buraco, [contorno - [x0, y0]], -1, 255, -1)
    # "Engordar" o buraco (dilatar) com um disco do tamanho da faixa e tirar o próprio buraco: sobra a faixa
    disco = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * faixa + 1, 2 * faixa + 1))
    em_volta = (cv2.dilate(buraco, disco) > 0) & (buraco == 0)
    if not em_volta.any():
        return 0.0
    return float((tinta[y0:y1, x0:x1][em_volta] > 0).mean())


# Apaga os vértices da tinta (com uma folga, para a borda sumir inteira)
def apagar_formas(tinta, formas, espessura, cv2, np):
    resto = tinta.copy()
    folga = int(round(espessura + 2))
    for forma in formas:
        if "raio" in forma:
            centro = (int(round(forma["centro"][0])), int(round(forma["centro"][1])))
            cv2.circle(resto, centro, int(round(forma["raio"] + folga)), 0, -1)
        else:
            x0, y0, x1, y1 = forma["caixa"]
            cv2.rectangle(resto, (int(x0) - folga, int(y0) - folga), (int(x1) + folga, int(y1) + folga), 0, -1)
    return resto


# ----------------------------------------------------------------------
# 4 e 5. Arestas e setas
# ----------------------------------------------------------------------

# Cada mancha de tinta (componente conexa) do que sobrou é, em geral, uma aresta inteira, com a seta.
# Os pixels da mancha que ficam numa faixa logo depois da borda de um vértice mostram onde ela encosta.
# Devolve os traços (para a montagem; cada um lembra de que manchas veio), quantos lugares têm linhas
# que se cruzam e a imagem das manchas (cada pixel com o número da sua mancha).
def achar_arestas(resto, formas, espessura, cv2, np):
    quantidade, rotulos, estatisticas, centros = cv2.connectedComponentsWithStats(resto, connectivity=8)
    tipico = geometria.mediana([montagem.tamanho_da_forma(forma) for forma in formas])
    folga = espessura + 2
    faixa = max(4.0, 1.5 * espessura)
    tracos = []
    metades = []                # pedaços presos a um vértice só (uma linha cortada por um rótulo)
    cruzamentos = 0
    for k in range(1, quantidade):
        area = estatisticas[k, cv2.CC_STAT_AREA]
        largura = estatisticas[k, cv2.CC_STAT_WIDTH]
        altura = estatisticas[k, cv2.CC_STAT_HEIGHT]
        if area < 10 or max(largura, altura) < 0.3 * tipico:
            continue                                # pequeno demais para ser uma linha (ruído, letra)
        pixels = np.argwhere(rotulos == k)           # (linha, coluna) = (y, x) de cada pixel
        xs = pixels[:, 1].astype(float)
        ys = pixels[:, 0].astype(float)
        encostos = []                                # (vértice, grupos de pixels onde encosta)
        for i in range(len(formas)):
            perto = pixels_na_faixa(xs, ys, formas[i], folga, faixa, np)
            if perto.any():
                grupos = grupos_de_encosto(xs[perto], ys[perto], formas[i], np)
                encostos.append((i, grupos))
        if len(encostos) == 2:
            (u, grupos_u), (v, grupos_v) = encostos
            tracos.append(traco_da_mancha(pixels, grupos_u[0], grupos_v[0], espessura, tipico, np, manchas=[k]))
        elif len(encostos) == 1:
            u, grupos = encostos[0]
            if len(grupos) >= 2:                     # encosta em dois lugares do mesmo vértice: um laço
                tracos.append(traco_da_mancha(pixels, grupos[0], grupos[1], espessura, tipico, np, manchas=[k]))
            else:
                metades.append((u, pixels, grupos[0], k))
        elif len(encostos) > 2:
            cruzamentos += 1
            for caminho, grupo_u, grupo_v in separar_cruzamento(pixels, encostos, formas, folga + 2,
                                                                espessura, tipico, np):
                tracos.append(traco_da_mancha(pixels, grupo_u, grupo_v, espessura, tipico, np, pontos=caminho,
                                              manchas=[k]))
    # Duas metades cujas pontas soltas estão perto uma da outra são a mesma linha
    # (o rótulo com fundo branco, no meio da linha, a cortou em duas). Os pares mais próximos primeiro.
    soltas = []
    for u, pixels, grupo, k in metades:
        soltas.append(ponto_mais_longe(pixels, grupo, np))
    pares = []
    for a in range(len(metades)):
        for b in range(a + 1, len(metades)):
            vao = geometria.distancia(soltas[a], soltas[b])
            if metades[a][0] != metades[b][0] and vao <= max(1.2 * tipico, 12 * espessura):
                pares.append((vao, a, b))
    pares.sort(key=lambda par: par[0])
    usadas = []
    for vao, a, b in pares:
        if a in usadas or b in usadas:
            continue
        u, pixels_u, grupo_u, k_u = metades[a]
        v, pixels_v, grupo_v, k_v = metades[b]
        # O caminho de cada metade até a ponta solta, e o vão entre elas, em linha reta
        pontos = caminho_por_dentro(pixels_u, grupo_u, soltas[a], np) + \
            list(reversed(caminho_por_dentro(pixels_v, grupo_v, soltas[b], np)))
        juntos = np.concatenate([pixels_u, pixels_v])
        tracos.append(traco_da_mancha(juntos, grupo_u, grupo_v, espessura, tipico, np, pontos=pontos,
                                      manchas=[k_u, k_v]))
        usadas.extend([a, b])
    return tracos, cruzamentos, rotulos


# Quais pixels ficam na faixa logo depois da borda do vértice (onde uma linha "encosta")
def pixels_na_faixa(xs, ys, forma, folga, faixa, np):
    if "raio" in forma:
        cx, cy = forma["centro"]
        distancia = np.hypot(xs - cx, ys - cy)
        return (distancia >= forma["raio"] + folga - 1) & (distancia <= forma["raio"] + folga + faixa)
    x0, y0, x1, y1 = forma["caixa"]
    fora_x = np.maximum(np.maximum(x0 - folga - xs, 0), xs - x1 - folga)
    fora_y = np.maximum(np.maximum(y0 - folga - ys, 0), ys - y1 - folga)
    # (os pixels de dentro da caixa já foram apagados: a distância deles daria 0)
    return np.hypot(fora_x, fora_y) <= faixa


# Os pixels de encosto separados em grupos pelo ângulo em volta do vértice (um laço encosta em dois
# lugares). Cada grupo é representado pelo ponto mediano dos seus pixels (fica logo fora da borda,
# no círculo e na caixa). Os grupos voltam do maior para o menor.
def grupos_de_encosto(xs, ys, forma, np):
    cx, cy = forma["centro"]
    angulos = np.arctan2(ys - cy, xs - cx)
    ordem = np.argsort(angulos)
    angulos = angulos[ordem]
    xs = xs[ordem]
    ys = ys[ordem]
    # Separa onde há um "buraco" de mais de 15 graus entre ângulos vizinhos
    cortes = list(np.where(np.diff(angulos) > math.radians(15))[0] + 1)
    pedacos = []
    comeco = 0
    for corte in cortes + [len(angulos)]:
        pedacos.append(list(range(comeco, corte)))
        comeco = corte
    # O primeiro e o último pedaço podem ser o mesmo grupo (passando pelo ângulo -180/180)
    if len(pedacos) > 1 and (angulos[0] + 2 * math.pi) - angulos[-1] <= math.radians(15):
        pedacos[0] = pedacos[-1] + pedacos[0]
        pedacos.pop()
    pedacos.sort(key=len, reverse=True)
    grupos = []
    for pedaco in pedacos:
        if len(pedaco) < 2:
            continue
        grupos.append((float(np.median(xs[pedaco])), float(np.median(ys[pedaco]))))
    if not grupos:
        grupos.append((float(np.mean(xs)), float(np.mean(ys))))
    return grupos


# O traço de uma mancha: o caminho por dentro da mancha entre os dois pontos de encosto
# (busca em largura nos pixels!) e se há seta em cada ponta.
# "pontos": o caminho, se já for conhecido; "manchas": de que manchas a aresta é feita.
def traco_da_mancha(pixels, inicio, fim, espessura, tipico, np, pontos=None, manchas=()):
    if pontos is None:
        pontos = caminho_por_dentro(pixels, inicio, fim, np)
    seta_no_inicio = tem_seta(pixels, pontos, 0, espessura, tipico, np)
    seta_no_fim = tem_seta(pixels, pontos, -1, espessura, tipico, np)
    return {"pontos": pontos, "seta_no_inicio": seta_no_inicio, "seta_no_fim": seta_no_fim,
            "manchas": list(manchas)}


# Menor caminho entre dois pontos andando só por pixels de tinta: é a busca em largura (BFS)
# de novo, agora num "grafo" em que cada pixel é um vértice ligado aos 8 vizinhos.
# Devolve os pontos do caminho, de 4 em 4 pixels.
def caminho_por_dentro(pixels, inicio, fim, np):
    conjunto = set()
    for y, x in pixels:
        conjunto.add((int(x), int(y)))
    comeco = pixel_mais_perto(pixels, inicio, np)
    chegada = pixel_mais_perto(pixels, fim, np)
    anterior = {comeco: None}
    fila = deque([comeco])
    while fila:
        atual = fila.popleft()
        if atual == chegada:
            break
        x, y = atual
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                vizinho = (x + dx, y + dy)
                if vizinho in conjunto and vizinho not in anterior:
                    anterior[vizinho] = atual
                    fila.append(vizinho)
    if chegada not in anterior:
        return [inicio, fim]
    caminho = []
    atual = chegada
    while atual is not None:
        caminho.append(atual)
        atual = anterior[atual]
    caminho.reverse()
    pontos = [inicio]
    for i in range(0, len(caminho), 4):
        pontos.append((float(caminho[i][0]), float(caminho[i][1])))
    pontos.append(fim)
    return pontos


def pixel_mais_perto(pixels, ponto, np):
    distancias = np.hypot(pixels[:, 1] - ponto[0], pixels[:, 0] - ponto[1])
    y, x = pixels[int(np.argmin(distancias))]
    return (int(x), int(y))


def ponto_mais_longe(pixels, ponto, np):
    distancias = np.hypot(pixels[:, 1] - ponto[0], pixels[:, 0] - ponto[1])
    y, x = pixels[int(np.argmax(distancias))]
    return (float(x), float(y))


# Há seta na ponta "extremo" (0 = começo, -1 = fim)? Uma seta, cheia (um triângulo) ou aberta (um "V"),
# deixa a tinta bem mais LARGA perto da ponta do que no resto da linha.
# A largura é medida em "fatias": cortes de 2 pixels atravessando a linha; a largura de uma fatia é a
# distância entre o pixel de tinta mais à esquerda e o mais à direita nela.
#   - perto da ponta: a maior largura entre as fatias do último trecho da linha;
#   - a linha normal: a largura ao longo da linha. Um rótulo encostado na linha deixa alguns trechos mais
#     largos; numa linha curta, o rótulo pode ocupar quase metade dela. Por isso a medida é o primeiro
#     quartil (a largura que 25% dos trechos não passam), e não a média nem a mediana.
# Medidas nas imagens de exemplo (Graphviz, draw.io e a foto), em vezes a largura normal:
# ponta com seta, de 2,2 a 6; ponta sem seta, de 0,67 a 1,14. O limiar fica entre os dois: 1,7.
def tem_seta(pixels, pontos, extremo, espessura, tipico, np):
    if len(pontos) < 2:
        return False
    alcance = max(6.0, 0.17 * tipico)                   # o tamanho de uma seta, mais ou menos
    referencia = ponto_a_distancia(pontos, extremo, alcance)
    ponta = fim_da_tinta(pixels, pontos[extremo], referencia, alcance, np)
    larguras = larguras_das_fatias(pixels, ponta, direcao(referencia, ponta), alcance, alcance, np)
    if not larguras:
        return False
    perto_da_ponta = max(larguras)
    ao_longo = []
    total = comprimento_da_linha(pontos)
    distancia = 1.5 * alcance
    while distancia <= total - 1.5 * alcance:
        atras = ponto_a_distancia(pontos, 0, distancia)
        adiante = ponto_a_distancia(pontos, 0, distancia + alcance / 2)
        fatias = larguras_das_fatias(pixels, adiante, direcao(atras, adiante), alcance / 2, alcance, np)
        if fatias:
            ao_longo.append(geometria.mediana(fatias))
        distancia += alcance / 2
    if ao_longo:
        ao_longo.sort()
        normal = ao_longo[len(ao_longo) // 4]
    else:
        normal = espessura                  # linha curta demais para medir: usa a espessura de todas
    return perto_da_ponta >= 1.7 * max(normal, 1.0)


# As larguras das fatias: começa em "ponto" e vai "comprimento" pixels para trás (contra a "direcao",
# que é um vetor de tamanho 1), olhando só até "alcance" pixels para cada lado
def larguras_das_fatias(pixels, ponto, direcao, comprimento, alcance, np):
    xs = pixels[:, 1].astype(float)
    ys = pixels[:, 0].astype(float)
    ux, uy = direcao
    para_tras = -((xs - ponto[0]) * ux + (ys - ponto[1]) * uy)      # produto escalar: ao longo da linha
    para_o_lado = (xs - ponto[0]) * uy - (ys - ponto[1]) * ux       # produto vetorial: atravessando
    dentro = (para_tras >= -1) & (para_tras <= comprimento) & (np.abs(para_o_lado) <= alcance)
    fatias = np.floor(para_tras[dentro] / 2).astype(int)
    lados = para_o_lado[dentro]
    larguras = []
    for fatia in np.unique(fatias):
        da_fatia = lados[fatias == fatia]
        larguras.append(float(da_fatia.max() - da_fatia.min() + 1))
    return larguras


# O vetor de tamanho 1 que aponta de "a" para "b"
def direcao(a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    comprimento = math.hypot(dx, dy)
    if comprimento == 0:
        return (1.0, 0.0)
    return (dx / comprimento, dy / comprimento)


# O fim de verdade da tinta naquela ponta: entre os pixels perto da ponta, o que vai mais longe na
# direção "para fora" da linha (de "referencia" para "ponto"). Numa seta, é o bico da seta.
def fim_da_tinta(pixels, ponto, referencia, alcance, np):
    xs = pixels[:, 1].astype(float)
    ys = pixels[:, 0].astype(float)
    dx = ponto[0] - referencia[0]
    dy = ponto[1] - referencia[1]
    perto = np.hypot(xs - ponto[0], ys - ponto[1]) <= 2 * alcance
    if not perto.any() or (dx == 0 and dy == 0):
        return ponto
    adiante = (xs[perto] - referencia[0]) * dx + (ys[perto] - referencia[1]) * dy
    escolhido = int(np.argmax(adiante))
    return (float(xs[perto][escolhido]), float(ys[perto][escolhido]))


def comprimento_da_linha(pontos):
    total = 0
    for i in range(len(pontos) - 1):
        total += geometria.distancia(pontos[i], pontos[i + 1])
    return total


# O ponto da linha a uma certa distância (medida ao longo da linha) de uma das pontas
def ponto_a_distancia(pontos, extremo, distancia):
    sequencia = pontos if extremo == 0 else list(reversed(pontos))
    falta = distancia
    for i in range(len(sequencia) - 1):
        trecho = geometria.distancia(sequencia[i], sequencia[i + 1])
        if trecho >= falta and trecho > 0:
            t = falta / trecho
            return (sequencia[i][0] + t * (sequencia[i + 1][0] - sequencia[i][0]),
                    sequencia[i][1] + t * (sequencia[i + 1][1] - sequencia[i][1]))
        falta -= trecho
    return sequencia[-1]


# Linhas que se cruzam (ou setas que se encostam na chegada): a mancha toca 3 ou mais vértices.
# Para cada par de pontos de encosto, o caminho por dentro da mancha é candidato a aresta se
#   (1) não encosta em outro vértice no meio do caminho;
#   (2) é "suave": sem curva fechada (no cruzamento de um X, ir de um braço para o do lado é uma curva);
#   (3) chega "de frente" nos dois vértices: uma aresta termina apontando para o vértice. Uma linha
#       que só passa raspando num vértice (e vai para outro) chega de lado, quase tangente à borda;
#   (4) não é um "pedaço" de outro candidato mais comprido que sai do mesmo ponto: se uma linha passa
#       raspando na seta de outra aresta, o caminho "seta -> resto da linha" é um pedaço dela.
# Num X de ângulo fechado, trocar de braço é uma curva pequena e também passaria. Por isso os
# candidatos são aceitos do mais reto para o mais curvo, e um candidato que vai quase todo (70%) por
# cima das arestas já aceitas é recusado: no X, o caminho "trocado" usa um braço de cada aresta.
# (Duas arestas que saem juntas de um vértice dividem só o começo: as duas passam.)
# Se isso não explica a mancha (alguma ponta fica sem aresta, como nas ligações ortogonais, cheias de
# cantos de 90 graus) e ela tem exatamente três pontas, vale a regra da junção (veja separar_juncao).
def separar_cruzamento(pixels, encostos, formas, distancia_minima, espessura, tipico, np):
    aceitos = separar_por_retas(pixels, encostos, formas, distancia_minima, espessura, tipico, np)
    pontas = []
    for u, grupos in encostos:
        for grupo in grupos:
            pontas.append((u, grupo))
    explicadas = []
    for caminho, grupo_u, grupo_v in aceitos:
        explicadas.extend([grupo_u, grupo_v])
    sem_aresta = False
    for u, grupo in pontas:
        if grupo not in explicadas:
            sem_aresta = True
    if sem_aresta and len(pontas) == 3:
        juncao = separar_juncao(pixels, pontas, formas, distancia_minima, espessura, tipico, np)
        if juncao is not None:
            return juncao
    return aceitos


def separar_por_retas(pixels, encostos, formas, distancia_minima, espessura, tipico, np):
    candidatos = []
    for a in range(len(encostos)):
        for b in range(a + 1, len(encostos)):
            u, grupos_u = encostos[a]
            v, grupos_v = encostos[b]
            for grupo_u in grupos_u:
                for grupo_v in grupos_v:
                    caminho = caminho_por_dentro(pixels, grupo_u, grupo_v, np)
                    curva = maior_curva(caminho, 0.5 * tipico)
                    if curva <= 45 and longe_dos_outros(caminho, formas, [u, v], distancia_minima) and \
                            chega_de_frente(caminho, 0, formas[u], 0.25 * tipico) and \
                            chega_de_frente(caminho, -1, formas[v], 0.25 * tipico):
                        candidatos.append((curva, caminho, grupo_u, grupo_v))
    inteiros = []
    for candidato in candidatos:
        curva, caminho, grupo_u, grupo_v = candidato
        pedaco = False
        for outro in candidatos:
            if outro is candidato or comprimento_da_linha(outro[1]) <= comprimento_da_linha(caminho):
                continue
            if (grupo_u in outro[2:] or grupo_v in outro[2:]) and \
                    fracao_por_cima(caminho, outro[1], 2 * espessura) >= 0.7:
                pedaco = True
        if not pedaco:
            inteiros.append(candidato)
    candidatos = inteiros
    candidatos.sort(key=lambda candidato: candidato[0])
    aceitos = []
    for curva, caminho, grupo_u, grupo_v in candidatos:
        por_cima = 0
        for ponto in caminho:
            for outro, outro_u, outro_v in aceitos:
                if geometria.distancia_a_linha(ponto, outro) <= 2 * espessura:
                    por_cima += 1
                    break
        if por_cima < 0.7 * len(caminho):
            aceitos.append((caminho, grupo_u, grupo_v))
    return aceitos


# Uma mancha com três pontas, cada uma num vértice, é uma JUNÇÃO: duas arestas que dividem um trecho
# (o "tronco"), como no draw.io quando duas ligações ortogonais chegam ao mesmo lado de um vértice, ou
# duas setas que se encostam na chegada. Das três pontas, uma é o vértice comum (o "centro") e as
# arestas são as outras duas até ele. Quem é o centro? O que está no fim do tronco:
#   - no T (duas linhas chegando de lados opostos e seguindo juntas), as duas linhas formam a barra
#     do T (direções opostas, mais de 150 graus entre elas) e o tronco é a terceira direção;
#   - no Y (linhas que vão se juntando), o tronco é a direção mais afastada das outras duas.
# As direções são medidas no ponto em que o caminho da terceira ponta encontra o das outras duas.
# Se alguma ponta chega de lado (uma linha que só passa raspando num vértice), a regra não vale e
# a separação geral decide. Devolve [(caminho, grupo, grupo), ...] ou None.
def separar_juncao(pixels, pontas, formas, distancia_minima, espessura, tipico, np):
    caminhos = {}
    for i in range(3):
        for j in range(i + 1, 3):
            u, grupo_u = pontas[i]
            v, grupo_v = pontas[j]
            caminho = caminho_por_dentro(pixels, grupo_u, grupo_v, np)
            if not longe_dos_outros(caminho, formas, [u, v], distancia_minima) or \
                    not chega_de_frente(caminho, 0, formas[u], 0.25 * tipico) or \
                    not chega_de_frente(caminho, -1, formas[v], 0.25 * tipico):
                return None
            caminhos[(i, j)] = caminho
            caminhos[(j, i)] = list(reversed(caminho))
    # O encontro: andando da ponta 2 em direção à ponta 0, o primeiro ponto em cima do caminho 0-1
    tolerancia = 2 * espessura
    de_2 = caminhos[(2, 0)]
    barra = caminhos[(0, 1)]
    encontro = None
    for indice in range(len(de_2)):
        if geometria.distancia_a_linha(de_2[indice], barra) <= tolerancia:
            encontro = indice
            break
    if encontro is None:
        return None
    centro_da_juncao = de_2[encontro]
    # Os três ramos, saindo do encontro: para a ponta 2 (de volta pelo caminho dela) e para as pontas
    # 0 e 1 (pelo caminho 0-1, a partir do ponto dele mais perto do encontro)
    mais_perto = 0
    for indice in range(len(barra)):
        if geometria.distancia(barra[indice], centro_da_juncao) < geometria.distancia(barra[mais_perto],
                                                                                        centro_da_juncao):
            mais_perto = indice
    ramos = [list(reversed(barra[:mais_perto + 1])), barra[mais_perto:], list(reversed(de_2[:encontro + 1]))]
    direcoes = []
    for ramo in ramos:
        comprimento = comprimento_da_linha(ramo)
        if comprimento < 2:
            return None
        alcance = min(0.3 * tipico, 0.6 * comprimento)
        direcoes.append(direcao(ramo[0], ponto_a_distancia(ramo, 0, alcance)))
    angulos = {}
    for i in range(3):
        for j in range(i + 1, 3):
            cosseno = direcoes[i][0] * direcoes[j][0] + direcoes[i][1] * direcoes[j][1]
            angulo = math.degrees(math.acos(max(-1.0, min(1.0, cosseno))))
            angulos[(i, j)] = angulo
            angulos[(j, i)] = angulo
    opostos = []
    for i in range(3):
        for j in range(i + 1, 3):
            if angulos[(i, j)] > 150:
                opostos.append((i, j))
    if len(opostos) == 1:
        tronco = 3 - opostos[0][0] - opostos[0][1]          # o que sobra de {0, 1, 2}
    elif not opostos:
        tronco = None
        maior = -1
        for i in range(3):
            menor_angulo = min(angulos[(i, j)] for j in range(3) if j != i)
            if menor_angulo > maior:
                maior = menor_angulo
                tronco = i
    else:
        return None
    # O ramo i leva à ponta: 0 -> ponta 0, 1 -> ponta 1, 2 -> ponta 2
    resultado = []
    for outro in range(3):
        if outro != tronco:
            resultado.append((caminhos[(outro, tronco)], pontas[outro][1], pontas[tronco][1]))
    return resultado


# O fim do caminho aponta para o vértice? Compara a direção do último trecho (de "alcance" pixels)
# com a direção do fim do caminho até o centro do vértice: até 60 graus de diferença.
def chega_de_frente(caminho, extremo, forma, alcance):
    ponta = caminho[extremo]
    chegada = direcao(ponto_a_distancia(caminho, extremo, alcance), ponta)
    para_o_centro = direcao(ponta, forma["centro"])
    return chegada[0] * para_o_centro[0] + chegada[1] * para_o_centro[1] >= math.cos(math.radians(60))


# Que fração dos pontos do caminho fica por cima (a até "tolerancia") do outro caminho
def fracao_por_cima(caminho, outro, tolerancia):
    por_cima = 0
    for ponto in caminho:
        if geometria.distancia_a_linha(ponto, outro) <= tolerancia:
            por_cima += 1
    return por_cima / len(caminho)


# O caminho fica longe de todos os vértices, menos os das duas pontas?
def longe_dos_outros(caminho, formas, pontas, distancia_minima):
    for i in range(len(formas)):
        if i in pontas:
            continue
        for ponto in caminho:
            if geometria.dentro_da_forma(ponto, formas[i]) or \
                    geometria.distancia_a_borda(ponto, formas[i]) < distancia_minima:
                return False
    return True


# A maior curva do caminho, em graus: em cada ponto (de quarto em quarto de "passo"), o ângulo entre
# a direção de quem chega (do ponto "passo" pixels antes) e a de quem sai (até "passo" pixels depois).
# Uma curva de aresta vira devagar; trocar de linha num cruzamento faz um "bico", que aparece inteiro
# em algum desses pontos (por isso a janela desliza em passos pequenos).
def maior_curva(caminho, passo):
    total = comprimento_da_linha(caminho)
    maior = 0.0
    distancia = passo
    while distancia <= total - passo:
        antes = ponto_a_distancia(caminho, 0, distancia - passo)
        ponto = ponto_a_distancia(caminho, 0, distancia)
        depois = ponto_a_distancia(caminho, 0, distancia + passo)
        ida = direcao(antes, ponto)
        volta = direcao(ponto, depois)
        cosseno = ida[0] * volta[0] + ida[1] * volta[1]           # produto escalar = cosseno do ângulo
        maior = max(maior, math.degrees(math.acos(max(-1.0, min(1.0, cosseno)))))
        distancia += passo / 4
    return maior


# ----------------------------------------------------------------------
# 6. Textos (OCR)
# ----------------------------------------------------------------------

# O Tesseract é um programa à parte; o pytesseract só o chama. Procura nesta ordem: a variável
# BOSCOGRAPH_TESSERACT, a pasta "tesseract" que o instalador do BoscoGraph pode trazer (ao lado do
# BoscoGraph.exe), o PATH do sistema e as pastas onde o instalador do Tesseract costuma colocar no Windows.
# Devolve o módulo pytesseract já configurado (e o idioma), ou None se não houver Tesseract.
def carregar_ocr():
    try:
        import pytesseract
    except ImportError:
        return None
    candidatos = [os.environ.get("BOSCOGRAPH_TESSERACT", ""),
                  str(Path(sys.executable).parent / "tesseract" / "tesseract.exe") if caminhos.esta_empacotado() else "",
                  str(caminhos.pasta_dos_recursos() / "tesseract" / "tesseract.exe"),
                  shutil.which("tesseract") or ""]
    if sys.platform.startswith("win"):
        candidatos.append(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        candidatos.append(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR",
                                       "tesseract.exe"))
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            pytesseract.pytesseract.tesseract_cmd = candidato
            pasta_dos_idiomas = Path(candidato).parent / "tessdata"
            if pasta_dos_idiomas.is_dir() and "TESSDATA_PREFIX" not in os.environ:
                os.environ["TESSDATA_PREFIX"] = str(pasta_dos_idiomas)
            try:
                idiomas = pytesseract.get_languages(config="")
            except Exception:
                return None
            idioma = "por" if "por" in idiomas else "eng"
            return {"modulo": pytesseract, "idioma": idioma}
    return None


# Prepara a tinta de um texto para o OCR. Recebe uma máscara (texto branco em fundo preto), aumenta até
# as letras ficarem com uns 40 pixels de altura (o tamanho em que o Tesseract mais acerta), inverte
# (o Tesseract quer preto no branco) e põe uma margem branca em volta.
def preparar_para_ocr(mascara, cv2, np):
    linhas = np.where(mascara.any(axis=1))[0]
    altura_do_texto = (linhas[-1] - linhas[0] + 1) if linhas.size else mascara.shape[0]
    fator = 40 / max(1, altura_do_texto)
    grande = cv2.resize(mascara, None, fx=fator, fy=fator, interpolation=cv2.INTER_LINEAR)
    grande = np.where(grande > 127, 0, 255).astype(np.uint8)
    return cv2.copyMakeBorder(grande, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)


# A mesma preparação, mas em tons de cinza: guarda o "meio-tom" da borda das letras, que ajuda o OCR
# numa imagem limpa (captura de tela, exportação). O que está longe das letras vira fundo branco e o
# contraste é esticado: a letra mais escura fica preta e o fundo, branco.
def preparar_cinza_para_ocr(recorte, mascara, cv2, np):
    linhas = np.where(mascara.any(axis=1))[0]
    altura_do_texto = (linhas[-1] - linhas[0] + 1) if linhas.size else mascara.shape[0]
    tons = recorte.astype(np.float32)
    if tons[mascara > 0].mean() > tons[mascara == 0].mean():
        tons = 255 - tons                           # letra clara em fundo escuro: inverte
    perto_das_letras = cv2.dilate(mascara, np.ones((3, 3), np.uint8)) > 0
    fundo = float(np.percentile(tons[~perto_das_letras], 50)) if (~perto_das_letras).any() else 255.0
    tons[~perto_das_letras] = fundo
    letra = float(tons.min())
    tons = np.clip((tons - letra) / max(1.0, fundo - letra) * 255, 0, 255).astype(np.uint8)
    fator = 40 / max(1, altura_do_texto)
    grande = cv2.resize(tons, None, fx=fator, fy=fator, interpolation=cv2.INTER_CUBIC)
    return cv2.copyMakeBorder(grande, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)


# Lê o texto tentando duas preparações (a máscara preto no branco e, se houver o recorte original,
# os tons de cinza) e "modos de página" do Tesseract: 10 = um caractere só; 8 = uma palavra só;
# 7 = uma linha de texto. Fica com a leitura de maior confiança e para logo que uma passar de 85.
# Se nenhuma passar de 70, tenta de novo aceitando letras acentuadas (e uma leitura com acento só
# ganha se for bem mais confiável: o "5" com serifa parece um "ô").
#   - Um texto mais estreito que alto é, provavelmente, um caractere só: modos 10, 8 e 7 (o 8 salva
#     a letra borrada de uma foto). Mais largo: só o modo 7 (no teste, o 8 leu "R5" como "E").
#   - A quantidade de letras lidas precisa combinar com a largura do texto (cada letra tem uns 3/4
#     da altura): ler "E" (uma letra) num texto da largura de duas é engano.
def ler_mascara(mascara, ocr, permitidas, cv2, np, recorte=None):
    preparados = [preparar_para_ocr(mascara, cv2, np)]
    if recorte is not None:
        preparados.append(preparar_cinza_para_ocr(recorte, mascara, cv2, np))
    linhas = np.where(mascara.any(axis=1))[0]
    colunas = np.where(mascara.any(axis=0))[0]
    if linhas.size == 0:
        return "", 0
    largura = colunas[-1] - colunas[0] + 1
    altura = linhas[-1] - linhas[0] + 1
    um_caractere = largura <= 1.1 * altura
    modos = (10, 8, 7) if um_caractere else (7,)
    letras_esperadas = largura / (0.75 * altura)
    melhor_texto, melhor_confianca = "", 0
    for letras, vantagem in ((permitidas, 0), (permitidas + LETRAS_ACENTUADAS, 20)):
        for preparado in preparados:
            for modo in modos:
                texto, confianca = ocr_de_um_recorte(preparado, modo, ocr, letras)
                quantidade = len(texto.replace(" ", ""))
                if quantidade < 0.5 * letras_esperadas or quantidade > 2.5 * letras_esperadas + 1:
                    continue
                # Com acentos, a leitura só ganha se for bem mais confiável (20 pontos a mais)
                if texto and confianca > melhor_confianca + vantagem:
                    melhor_texto, melhor_confianca = texto, confianca
                if melhor_confianca >= 85:
                    return melhor_texto, melhor_confianca
        if melhor_confianca >= 70:
            break
    return melhor_texto, melhor_confianca


# Roda o Tesseract e devolve (texto, confiança média de 0 a 100)
def ocr_de_um_recorte(imagem, modo, ocr, permitidas):
    pytesseract = ocr["modulo"]
    configuracao = f"--psm {modo} -c tessedit_char_whitelist={permitidas}"
    try:
        dados = pytesseract.image_to_data(imagem, lang=ocr["idioma"], config=configuracao,
                                          output_type=pytesseract.Output.DICT)
    except Exception:
        return "", 0
    palavras = []
    confiancas = []
    for i in range(len(dados["text"])):
        texto = dados["text"][i].strip()
        confianca = float(dados["conf"][i])
        if texto and confianca >= 0:
            palavras.append(texto)
            confiancas.append(confianca)
    if not palavras:
        return "", 0
    return " ".join(palavras), sum(confiancas) / len(confiancas)


# O nome escrito dentro de um vértice:
#   1. recorta a parte de dentro (um quadrado dentro do círculo, ou a caixa sem a borda);
#   2. separa a tinta das letras pelo limiar de Otsu (o limiar que melhor separa os dois tons do recorte)
#      e acerta o sentido: a tinta é a minoria dos pixels (assim um vértice escuro com letra clara funciona);
#   3. tira as manchas que encostam na beirada do recorte: são pedaços da borda do vértice, não letras;
#   4. lê (veja ler_mascara).
# Devolve (texto, confiança de 0 a 100, caixa do texto, altura das letras em pixels).
def ler_dentro_da_forma(cinza, forma, espessura, ocr, cv2, np):
    altura, largura = cinza.shape
    cx, cy = forma["centro"]
    if "raio" in forma:
        metade = 0.7 * (forma["raio"] - espessura)
        x0, y0, x1, y1 = cx - metade, cy - metade, cx + metade, cy + metade
    else:
        x0, y0, x1, y1 = forma["caixa"]
        x0 += 1.5 * espessura
        y0 += 1.5 * espessura
        x1 -= 1.5 * espessura
        y1 -= 1.5 * espessura
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(largura, int(x1)), min(altura, int(y1))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return "", 0, None, 0
    recorte = cinza[y0:y1, x0:x1]
    limiar, tinta = cv2.threshold(cv2.GaussianBlur(recorte, (3, 3), 0), 0, 255,
                                  cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    if np.mean(tinta) > 127:
        tinta = 255 - tinta                         # texto claro em fundo escuro (vértice preenchido)
    tinta = sem_o_que_encosta_na_beirada(tinta, cv2, np)
    if not tinta.any():
        return "", 0, None, 0
    linhas = np.where(tinta.any(axis=1))[0]
    colunas = np.where(tinta.any(axis=0))[0]
    caixa = (x0 + int(colunas[0]), y0 + int(linhas[0]), x0 + int(colunas[-1]) + 1, y0 + int(linhas[-1]) + 1)
    texto, confianca = ler_mascara(tinta, ocr, LETRAS_DO_OCR, cv2, np, recorte)
    return texto.replace(" ", "_"), confianca, caixa, int(linhas[-1] - linhas[0] + 1)


# Tira da máscara as manchas que encostam na beirada (bordas de vértice, pontas de linha) e os
# pontinhos de ruído (menores que 0,05% do recorte; o pingo do "i" fica)
def sem_o_que_encosta_na_beirada(mascara, cv2, np):
    altura, largura = mascara.shape
    quantidade, rotulos, estatisticas, centros = cv2.connectedComponentsWithStats(mascara, connectivity=8)
    limpa = np.zeros_like(mascara)
    for k in range(1, quantidade):
        x, y, w, h, area = estatisticas[k]
        na_beirada = x == 0 or y == 0 or x + w >= largura or y + h >= altura
        if not na_beirada and area >= max(4, 0.0005 * altura * largura):
            limpa[rotulos == k] = 255
    return limpa


# Correções nos nomes lidos, usando os OUTROS nomes do mesmo desenho como referência:
#   1. Nomes de uma letra só: o OCR confunde maiúscula e minúscula quando as duas têm o mesmo desenho
#      (S e s, X e x, C e c...). Se a maioria é maiúscula, todos ficam maiúsculos (e o contrário).
#   2. Nomes "letras + número" (R1, R2, v10, E5, F3...): se a maioria segue esse padrão, um nome que
#      começa com um dos prefixos lidos certo e tem letras parecidas com algarismos no lugar do número
#      é corrigido ("Ri" -> "R1", "RS" -> "R5", "ES" -> "E5"; medido no teste: o "1" com serifa vira
#      "i" com frequência, e o "5" vira "S").
# Devolve a lista das correções do item 2 ("Ri → R1"), para o aviso.
PARECIDOS_COM_ALGARISMOS = {"i": "1", "l": "1", "I": "1", "|": "1", "!": "1", "o": "0", "O": "0",
                            "Q": "0", "D": "0", "S": "5", "s": "5", "B": "8", "Z": "2",
                            "z": "2", "G": "6", "b": "6", "g": "9", "q": "9", "a": "4", "A": "4"}


def corrigir_nomes(textos):
    letras = []
    for texto in textos:
        if len(texto["texto"]) == 1 and texto["texto"].isalpha():
            letras.append(texto)
    maiusculas = 0
    for texto in letras:
        if texto["texto"].isupper():
            maiusculas += 1
    for texto in letras:
        if maiusculas * 2 >= len(letras):
            # o "l" minúsculo tem o desenho do "I" maiúsculo (e não do "L")
            texto["texto"] = "I" if texto["texto"] == "l" else texto["texto"].upper()
        else:
            texto["texto"] = "l" if texto["texto"] == "I" else texto["texto"].lower()

    # Os nomes "letras + algarismos" lidos certo: os prefixos usados e quantos algarismos eles têm
    padrao = r"([^\W\d_]+)(\d+)"
    prefixos = []
    tamanhos = []
    for texto in textos:
        partes = re.fullmatch(padrao, texto["texto"])
        if partes:
            if partes.group(1) not in prefixos:
                prefixos.append(partes.group(1))
            tamanhos.append(len(partes.group(2)))
    if not prefixos:
        return []
    prefixos.sort(key=len, reverse=True)            # o prefixo mais comprido primeiro ("RS" antes de "R")
    # Os outros nomes que, começando com um desses prefixos, viram "prefixo + número" trocando as
    # letras parecidas com algarismos (e com a mesma quantidade de algarismos dos nomes lidos certo)
    propostas = []
    for texto in textos:
        nome = texto["texto"]
        if re.fullmatch(padrao, nome):
            continue
        for prefixo in prefixos:
            resto = nome[len(prefixo):]
            if not nome.startswith(prefixo) or not min(tamanhos) <= len(resto) <= max(tamanhos):
                continue
            numero = ""
            for letra in resto:
                numero += letra if letra.isdigit() else PARECIDOS_COM_ALGARISMOS.get(letra, "?")
            if "?" not in numero:
                propostas.append((texto, prefixo + numero))
                break
    # Só vale se a maioria dos nomes segue o padrão (lidos certo ou corrigíveis)
    if (len(tamanhos) + len(propostas)) * 2 < len(textos):
        return []
    correcoes = []
    for texto, novo in propostas:
        correcoes.append(f"{texto['texto']} → {novo}")
        texto["texto"] = novo
    return correcoes


# Apaga as linhas das arestas (e as setas, nas pontas) do que sobrou: o que fica são os rótulos.
# Apagar antes de ler evita que um pedaço de linha vire um "1" ou um "l" para o OCR.
# Só se apaga a tinta da própria aresta (das manchas dela) numa faixa em volta do caminho: um rótulo
# encostado na linha perde só o pedaço que está em cima dela, e um rótulo solto (num vão da linha,
# como no draw.io) não é tocado.
def apagar_linhas(resto, tracos, manchas, espessura, tipico, cv2, np):
    faixa = np.zeros(resto.shape, dtype=np.uint8)
    largura_da_linha = int(round(2 * espessura + 3))
    # Nas pontas, um disco do tamanho de uma seta (as "asas" da seta saem da faixa da linha)
    raio_da_ponta = int(round(max(5 * espessura + 6, 0.3 * tipico)))
    das_arestas = []
    for traco in tracos:
        pontos = traco["pontos"]
        for i in range(len(pontos) - 1):
            a = (int(round(pontos[i][0])), int(round(pontos[i][1])))
            b = (int(round(pontos[i + 1][0])), int(round(pontos[i + 1][1])))
            cv2.line(faixa, a, b, 255, largura_da_linha)
        for extremo in (0, -1):
            ponta = (int(round(pontos[extremo][0])), int(round(pontos[extremo][1])))
            cv2.circle(faixa, ponta, raio_da_ponta, 255, -1)
        das_arestas.extend(traco["manchas"])
    sobra = resto.copy()
    sobra[(faixa > 0) & np.isin(manchas, das_arestas)] = 0
    return sobra


# Os rótulos das arestas: as manchas que sobraram, juntadas em palavras (manchas na mesma altura e
# coladas uma na outra), cada palavra lida pelo OCR direto da máscara (já sem as linhas).
#   - Restos de seta e de linha que escaparam são mais baixos que as letras. A altura de referência é
#     a das letras dos nomes dos vértices (os desenhos costumam usar a mesma fonte nos rótulos). Mancha com menos da metade dessa altura não começa palavra (mas, se
#     estiver dentro de uma, como a vírgula de "8,5", vai junto no recorte).
#   - Duas manchas são da mesma palavra se o vão entre elas for menor que 35% da altura: entre os
#     algarismos de um número o vão é pequeno; entre os rótulos de duas arestas vizinhas (um "45" ao
#     lado de um "62"), maior. Medido no teste: com 80%, os dois viravam "4562".
def ler_rotulos(sobra, ocr, cv2, np, altura_das_letras=None):
    quantidade, rotulos, estatisticas, centros = cv2.connectedComponentsWithStats(sobra, connectivity=8)
    letras = []
    for k in range(1, quantidade):
        x, y, w, h, area = estatisticas[k]
        if area < 4 or h > 80 or w > 120:
            continue
        letras.append([x, y, x + w, y + h])
    if not letras:
        return []
    altura_tipica = altura_das_letras or geometria.mediana([caixa[3] - caixa[1] for caixa in letras if caixa[3] - caixa[1] >= 6])
    letras.sort(key=lambda caixa: caixa[0])
    palavras = []
    for caixa in letras:
        altura_da_mancha = caixa[3] - caixa[1]
        if altura_da_mancha > 3 * altura_tipica:
            continue
        pequena = altura_da_mancha < 0.5 * altura_tipica      # vírgula, ponto ou resto de linha
        juntou = False
        for palavra in palavras:
            altura = palavra[3] - palavra[1]
            mesma_linha = abs((caixa[1] + caixa[3]) / 2 - (palavra[1] + palavra[3]) / 2) < 0.6 * altura
            perto = caixa[0] - palavra[2] < 0.35 * altura
            if mesma_linha and perto:
                palavra[0] = min(palavra[0], caixa[0])
                palavra[1] = min(palavra[1], caixa[1])
                palavra[2] = max(palavra[2], caixa[2])
                palavra[3] = max(palavra[3], caixa[3])
                juntou = True
                break
        if not juntou and not pequena:
            palavras.append(list(caixa))
    textos = []
    for x0, y0, x1, y1 in palavras:
        texto, confianca = ler_mascara(sobra[y0:y1, x0:x1], ocr, LETRAS_DO_OCR + ",.-", cv2, np)
        if texto and confianca >= 40:
            textos.append({"texto": texto, "caixa": (int(x0), int(y0), int(x1), int(y1))})
    return textos


# O OCR confunde letras e algarismos de desenho parecido: l e I com 1, O e o com 0. Se a maioria dos
# rótulos é número (o grafo tem pesos), os rótulos feitos só desses caracteres (e de algarismos, vírgula
# e ponto) também são números lidos errado e voltam a ser números. Devolve as trocas ("l → 1").
def corrigir_numeros(textos):
    parecidos = {"l": "1", "I": "1", "|": "1", "O": "0", "o": "0"}
    numeros = 0
    for texto in textos:
        if entrada.ler_numero(texto["texto"])[0] is not None:
            numeros += 1
    if numeros * 2 < len(textos):
        return []
    trocas = []
    for texto in textos:
        if entrada.ler_numero(texto["texto"])[0] is not None:
            continue
        novo = ""
        for letra in texto["texto"]:
            novo += parecidos.get(letra, letra)
        if entrada.ler_numero(novo)[0] is not None:
            trocas.append(f"{texto['texto']} → {novo}")
            texto["texto"] = novo
    return trocas


# ----------------------------------------------------------------------
# A conferência
# ----------------------------------------------------------------------

def imagem_da_previa(imagem, cv2):
    altura, largura = imagem.shape[:2]
    escala = TAMANHO_DA_PREVIA / max(altura, largura)
    pequena = cv2.resize(imagem, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    sucesso, dados = cv2.imencode(".png", pequena)
    return dados.tobytes(), escala


def marcas_na_escala(bruto, escala):
    originais = bruto["marcas_originais"]
    marcas = {"vertices": [], "arestas": []}
    for identificador, centro, raio in originais["vertices"]:
        marcas["vertices"].append((identificador, centro[0] * escala, centro[1] * escala, raio * escala))
    for primeiro, ultimo, seta in originais["arestas"]:
        marcas["arestas"].append((primeiro[0] * escala, primeiro[1] * escala, ultimo[0] * escala,
                                  ultimo[1] * escala, seta in ("fim", "ambas")))
    return marcas
