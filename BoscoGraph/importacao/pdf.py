'''
    Fase 2 da importação: PDF exportado de um programa de desenho (draw.io, PowerPoint, Graphviz...).

    Um PDF desenhado guarda os desenhos como "caminhos" (sequências de linhas "l" e curvas de
    Bézier "c") e os textos com a posição de cada um. A biblioteca PyMuPDF lê os dois:
      page.get_drawings()   -> cada caminho, com os pontos, se é preenchido e o retângulo que ocupa
      page.get_text("dict") -> cada linha de texto, com o retângulo que ocupa

    Daí, cada caminho é classificado:
      - fechado, feito de curvas e mais ou menos redondo -> um vértice (círculo ou elipse);
      - fechado, retangular e com texto dentro          -> um vértice (caixa);
      - fechado, preenchido e pequeno                    -> uma ponta de seta;
      - aberto                                           -> uma linha (talvez uma aresta).
    E a montagem (importacao/montagem.py) liga tudo. O resultado sempre passa pela conferência.
'''

import caminhos
from importacao import ProblemaNaImportacao
from importacao import geometria
from importacao import montagem

TAMANHO_DA_PREVIA = 520             # o lado maior da imagem da conferência, em pixels


def carregar_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        try:
            import fitz                 # o nome antigo da PyMuPDF
            return fitz
        except ImportError:
            if caminhos.esta_empacotado():
                raise ProblemaNaImportacao("Esta instalação do BoscoGraph foi gerada sem a leitura de PDF. "
                                           "Exporte o desenho como imagem (PNG) e importe a imagem.")
            raise ProblemaNaImportacao("Para importar PDF, instale a biblioteca PyMuPDF: "
                                       "pip install pymupdf")


def ler_pdf(caminho):
    pymupdf = carregar_pymupdf()
    try:
        documento = pymupdf.open(str(caminho))
    except Exception as erro:
        raise ProblemaNaImportacao(f"Não consegui abrir o PDF: {erro}")
    if documento.needs_pass:
        raise ProblemaNaImportacao("O PDF está protegido por senha.")
    if documento.page_count == 0:
        raise ProblemaNaImportacao("O PDF não tem páginas.")

    # A primeira página que tem pelo menos uma forma que parece um vértice
    for numero in range(documento.page_count):
        pagina = documento[numero]
        formas, tracos, pontas = classificar_desenhos(pagina)
        if formas:
            textos = textos_da_pagina(pagina)
            formas = formas_com_texto(formas, textos)
            bruto = montagem.montar(formas, tracos, pontas, textos)
            if documento.page_count > 1:
                bruto["avisos"].insert(0, f"O PDF tem {documento.page_count} páginas; importei a página "
                                          f"{numero + 1}.")
            bruto["imagem"], escala = imagem_da_pagina(pagina, pymupdf)
            bruto["marcas"] = marcas_na_escala(bruto, escala)
            return bruto
    raise ProblemaNaImportacao("Não encontrei vértices (círculos ou caixas com texto) no PDF. Se o PDF é uma "
                               "foto ou um desenho escaneado, exporte a página como imagem e importe a imagem.")


# Os pontos de um caminho, na ordem: cada curva de Bézier vira 11 pontos sobre a curva
def pontos_do_caminho(caminho):
    pontos = []
    for item in caminho["items"]:
        tipo = item[0]
        if tipo == "l":
            novos = [item[1], item[2]]
        elif tipo == "c":
            novos = geometria.pontos_da_bezier(item[1], item[2], item[3], item[4])
        elif tipo == "re":
            r = item[1]
            novos = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)]
        elif tipo == "qu":
            q = item[1]
            novos = [q.ul, q.ur, q.lr, q.ll, q.ul]
        else:
            continue
        for ponto in novos:
            ponto = (float(ponto[0]), float(ponto[1]))
            if not pontos or geometria.distancia(pontos[-1], ponto) > 0.01:
                pontos.append(ponto)
    return pontos


def classificar_desenhos(pagina):
    candidatos = []
    for caminho in pagina.get_drawings():
        pontos = pontos_do_caminho(caminho)
        if len(pontos) < 2:
            continue
        retangulo = caminho["rect"]
        largura = retangulo.width
        altura = retangulo.height
        tipos = []
        for item in caminho["items"]:
            tipos.append(item[0])
        # "Fechado": marcado como fechado, ou termina onde começou (o Graphviz não marca)
        fechado = bool(caminho.get("closePath")) or geometria.distancia(pontos[0], pontos[-1]) < 1.0 \
            or "re" in tipos or "qu" in tipos
        preenchido = caminho.get("fill") is not None
        candidatos.append({"pontos": pontos, "tipos": tipos, "fechado": fechado, "preenchido": preenchido,
                           "caixa": (retangulo.x0, retangulo.y0, retangulo.x1, retangulo.y1),
                           "largura": largura, "altura": altura})

    area_da_pagina = pagina.rect.width * pagina.rect.height
    redondas = []
    caixas = []
    pequenas_preenchidas = []
    abertos = []
    for candidato in candidatos:
        largura = candidato["largura"]
        altura = candidato["altura"]
        if candidato["fechado"]:
            if largura * altura > 0.5 * area_da_pagina:
                continue                            # o fundo ou a moldura da página
            proporcao = largura / altura if altura > 0 else 0
            so_curvas = all(tipo == "c" for tipo in candidato["tipos"])
            if so_curvas and len(candidato["tipos"]) >= 2 and 0.5 <= proporcao <= 2 and min(largura, altura) >= 6:
                redondas.append(candidato)
            elif candidato["preenchido"] and max(largura, altura) < 25:
                pequenas_preenchidas.append(candidato)
            elif min(largura, altura) >= 10:
                caixas.append(candidato)
        else:
            abertos.append(candidato)

    # Vértices: os círculos e elipses e as caixas (que só ficam se tiverem texto dentro; veja abaixo),
    # na ordem em que aparecem no desenho
    formas = []
    for candidato in candidatos:
        x0, y0, x1, y1 = candidato["caixa"]
        centro = ((x0 + x1) / 2, (y0 + y1) / 2)
        if candidato in redondas:
            formas.append({"centro": centro, "raio": (x1 - x0 + y1 - y0) / 4})
        elif candidato in caixas:
            formas.append({"centro": centro, "caixa": (x0, y0, x1, y1), "caixa_sem_texto": True})
    formas = sem_formas_repetidas(formas)

    # Pontas de seta: pequenas e preenchidas, menores que um vértice
    tamanho_tipico = geometria.mediana([montagem.tamanho_da_forma(forma) for forma in formas]) or 30
    pontas = []
    for candidato in pequenas_preenchidas:
        tamanho = max(candidato["largura"], candidato["altura"])
        if tamanho <= 0.9 * tamanho_tipico:
            x0, y0, x1, y1 = candidato["caixa"]
            pontas.append({"centro": ((x0 + x1) / 2, (y0 + y1) / 2), "pontos": candidato["pontos"],
                           "tamanho": tamanho})
    tracos = []
    for candidato in abertos:
        tracos.append({"pontos": candidato["pontos"]})
    return formas, tracos, pontas


# Um mesmo vértice às vezes vem desenhado duas vezes (o preenchimento e o contorno separados):
# formas com o mesmo centro e quase o mesmo tamanho viram uma só
def sem_formas_repetidas(formas):
    unicas = []
    for forma in formas:
        repetida = False
        for outra in unicas:
            if geometria.distancia(forma["centro"], outra["centro"]) < 2 and \
                    abs(montagem.tamanho_da_forma(forma) - montagem.tamanho_da_forma(outra)) < 3:
                repetida = True
        if not repetida:
            unicas.append(forma)
    return unicas


# As caixas (retângulos) só ficam como vértice se tiverem texto dentro: retângulo vazio é
# moldura, legenda ou enfeite
def formas_com_texto(formas, textos):
    resultado = []
    for forma in formas:
        if forma.get("caixa_sem_texto"):
            tem_texto = False
            for texto in textos:
                if geometria.dentro_da_forma(montagem.centro_da_caixa(texto["caixa"]), forma):
                    tem_texto = True
            if not tem_texto:
                continue
            forma = {"centro": forma["centro"], "caixa": forma["caixa"]}
        resultado.append(forma)
    return resultado


# Os textos da página, com o retângulo que cada um ocupa.
# A unidade é cada "pedaço" (span) que o programa escreveu de uma vez: o Graphviz escreve o rótulo
# de cada aresta separado, mesmo quando dois rótulos ficam na mesma altura ("2" e "26" lado a lado),
# e um rótulo com várias palavras ("Fluxo de pedidos") vem num pedaço só. Pedaços colados (vão
# menor que 15% do tamanho da letra) são partes da mesma palavra e voltam a se juntar.
def textos_da_pagina(pagina):
    textos = []
    for bloco in pagina.get_text("dict")["blocks"]:
        for linha in bloco.get("lines", []):
            atual = None
            for pedaco in linha["spans"]:
                if pedaco["text"].strip() == "":
                    continue                    # espaço que a PyMuPDF põe entre pedaços separados
                caixa = tuple(pedaco["bbox"])
                if atual is not None and caixa[0] - atual["caixa"][2] < 0.15 * pedaco["size"]:
                    atual["texto"] += pedaco["text"]
                    atual["caixa"] = (atual["caixa"][0], min(atual["caixa"][1], caixa[1]),
                                      caixa[2], max(atual["caixa"][3], caixa[3]))
                else:
                    if atual is not None:
                        textos.append(atual)
                    atual = {"texto": pedaco["text"], "caixa": caixa}
            if atual is not None:
                textos.append(atual)
    for texto in textos:
        texto["texto"] = texto["texto"].strip()
    return textos


# A página como imagem PNG, para a conferência (e a escala: pixels por ponto do PDF)
def imagem_da_pagina(pagina, pymupdf):
    escala = TAMANHO_DA_PREVIA / max(pagina.rect.width, pagina.rect.height)
    figura = pagina.get_pixmap(matrix=pymupdf.Matrix(escala, escala), alpha=False)
    return figura.tobytes("png"), escala


# As marcas da montagem, na escala da imagem da conferência
def marcas_na_escala(bruto, escala):
    originais = bruto["marcas_originais"]
    marcas = {"vertices": [], "arestas": []}
    for identificador, centro, raio in originais["vertices"]:
        marcas["vertices"].append((identificador, centro[0] * escala, centro[1] * escala, raio * escala))
    for primeiro, ultimo, seta in originais["arestas"]:
        marcas["arestas"].append((primeiro[0] * escala, primeiro[1] * escala, ultimo[0] * escala,
                                  ultimo[1] * escala, seta in ("fim", "ambas")))
    return marcas
