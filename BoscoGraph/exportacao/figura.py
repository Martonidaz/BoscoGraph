'''
    Uma "figura": o desenho do grafo (ou de qualquer Canvas) como uma lista de formas simples, sem
    Tkinter. A tela (visual/exportar.py) lê os itens do Canvas e monta a figura; este arquivo escreve a
    mesma figura em três formatos:
        SVG -> texto (XML) que descreve as formas: vetorial, abre em qualquer navegador, não perde
               qualidade ao ampliar (bom para relatórios e slides);
        PNG -> uma imagem de pixels, desenhada com a biblioteca Pillow (se estiver instalada);
        PDF -> as formas desenhadas numa página do escritor de PDF (exportacao/pdf.py).

    A figura é um dicionário:
        {"largura": 1000, "altura": 750, "fundo": (244, 246, 249), "formas": [forma, forma, ...]}
    e cada forma é um dicionário com "tipo" (na ordem: a primeira fica por baixo de todas):
        linha     -> pontos, cor, espessura, tracejado, suave, ponta, forma_da_ponta
        poligono  -> pontos, preenchimento, contorno, espessura, tracejado
        elipse    -> caixa (x0, y0, x1, y1), preenchimento, contorno, espessura, tracejado
        retangulo -> caixa, preenchimento, contorno, espessura, tracejado
        texto     -> x, base, texto, tamanho (em pixels), negrito, italico, mono, cor, alinhamento
    As cores são (r, g, b) de 0 a 255; None = sem cor (sem preenchimento ou sem contorno).
    O texto é preso pela LINHA DE BASE (onde as letras "sentam"), e "alinhamento" diz se x é a ponta
    esquerda, o meio ou a ponta direita: assim o texto fica no lugar certo mesmo com outra fonte.
'''

import os

from exportacao import geometria
from exportacao.pdf import largura_do_texto


# ----------------------------------------------------------------------
# SVG
# ----------------------------------------------------------------------

def cor_em_hexa(cor):
    if cor is None:
        return "none"
    return "#%02x%02x%02x" % (round(cor[0]), round(cor[1]), round(cor[2]))


def numero_curto(numero):
    texto = f"{numero:.2f}".rstrip("0").rstrip(".")
    if texto in ("-0", ""):
        return "0"
    return texto


# Os caracteres que o XML não aceita dentro do texto viram "entidades" (& vira &amp;, < vira &lt;...)
def escapar_xml(texto):
    return (texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def lista_de_pontos(pontos):
    return " ".join(numero_curto(x) + "," + numero_curto(y) for x, y in pontos)


# Os atributos do traço: cor, espessura e tracejado (vazio se a forma não tem contorno)
def atributos_do_traco(cor, espessura, tracejado):
    if cor is None:
        return 'stroke="none"'
    texto = f'stroke="{cor_em_hexa(cor)}" stroke-width="{numero_curto(espessura)}"'
    if tracejado:
        texto += ' stroke-dasharray="' + " ".join(numero_curto(valor) for valor in tracejado) + '"'
    return texto


def caminho_svg_da_linha(pontos, suave):
    if suave and len(pontos) > 2:
        inicio, cubicas = geometria.cubicas_da_curva(pontos)
        partes = ["M " + lista_de_pontos([inicio])]
        for c1, c2, fim in cubicas:
            partes.append("C " + lista_de_pontos([c1, c2, fim]))
        return " ".join(partes)
    partes = ["M " + lista_de_pontos([pontos[0]])]
    for ponto in pontos[1:]:
        partes.append("L " + lista_de_pontos([ponto]))
    return " ".join(partes)


FAMILIAS_DO_SVG = {False: "Segoe UI, Helvetica, Arial, sans-serif", True: "Consolas, Courier New, monospace"}
ANCORAS_DO_SVG = {"esquerda": "start", "centro": "middle", "direita": "end"}


def para_svg(figura):
    largura = figura["largura"]
    altura = figura["altura"]
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              f'<svg xmlns="http://www.w3.org/2000/svg" width="{numero_curto(largura)}" '
              f'height="{numero_curto(altura)}" viewBox="0 0 {numero_curto(largura)} {numero_curto(altura)}">',
              '<g stroke-linejoin="round" stroke-linecap="butt">']
    if figura.get("fundo") is not None:
        linhas.append(f'<rect x="0" y="0" width="{numero_curto(largura)}" height="{numero_curto(altura)}" '
                      f'fill="{cor_em_hexa(figura["fundo"])}"/>')
    for forma in figura["formas"]:
        tipo = forma["tipo"]
        if tipo == "linha":
            pontos, poligonos = geometria.aplicar_pontas(forma["pontos"], forma.get("ponta"),
                                                         forma.get("forma_da_ponta", (8, 10, 3)), forma["espessura"])
            linhas.append(f'<path d="{caminho_svg_da_linha(pontos, forma.get("suave"))}" fill="none" '
                          f'{atributos_do_traco(forma["cor"], forma["espessura"], forma.get("tracejado"))}/>')
            for poligono in poligonos:
                linhas.append(f'<polygon points="{lista_de_pontos(poligono)}" fill="{cor_em_hexa(forma["cor"])}"/>')
        elif tipo == "poligono":
            linhas.append(f'<polygon points="{lista_de_pontos(forma["pontos"])}" '
                          f'fill="{cor_em_hexa(forma.get("preenchimento"))}" '
                          f'{atributos_do_traco(forma.get("contorno"), forma["espessura"], forma.get("tracejado"))}/>')
        elif tipo == "elipse":
            x0, y0, x1, y1 = forma["caixa"]
            linhas.append(f'<ellipse cx="{numero_curto((x0 + x1) / 2)}" cy="{numero_curto((y0 + y1) / 2)}" '
                          f'rx="{numero_curto(abs(x1 - x0) / 2)}" ry="{numero_curto(abs(y1 - y0) / 2)}" '
                          f'fill="{cor_em_hexa(forma.get("preenchimento"))}" '
                          f'{atributos_do_traco(forma.get("contorno"), forma["espessura"], forma.get("tracejado"))}/>')
        elif tipo == "retangulo":
            x0, y0, x1, y1 = forma["caixa"]
            linhas.append(f'<rect x="{numero_curto(min(x0, x1))}" y="{numero_curto(min(y0, y1))}" '
                          f'width="{numero_curto(abs(x1 - x0))}" height="{numero_curto(abs(y1 - y0))}" '
                          f'fill="{cor_em_hexa(forma.get("preenchimento"))}" '
                          f'{atributos_do_traco(forma.get("contorno"), forma["espessura"], forma.get("tracejado"))}/>')
        elif tipo == "texto":
            peso = ' font-weight="bold"' if forma.get("negrito") else ""
            estilo = ' font-style="italic"' if forma.get("italico") else ""
            linhas.append(f'<text x="{numero_curto(forma["x"])}" y="{numero_curto(forma["base"])}" '
                          f'font-family="{FAMILIAS_DO_SVG[bool(forma.get("mono"))]}" '
                          f'font-size="{numero_curto(forma["tamanho"])}"{peso}{estilo} '
                          f'text-anchor="{ANCORAS_DO_SVG[forma.get("alinhamento", "esquerda")]}" '
                          f'fill="{cor_em_hexa(forma["cor"])}" xml:space="preserve">{escapar_xml(forma["texto"])}</text>')
    linhas.append("</g>")
    linhas.append("</svg>")
    return "\n".join(linhas) + "\n"


def salvar_svg(figura, caminho):
    gravar_atomico(caminho, para_svg(figura).encode("utf-8"))


# Grava sem deixar o arquivo pela metade: primeiro num temporário, depois troca
def gravar_atomico(caminho, dados):
    caminho = str(caminho)
    temporario = caminho + ".tmp"
    with open(temporario, "wb") as arquivo:
        arquivo.write(dados)
    os.replace(temporario, caminho)


# ----------------------------------------------------------------------
# PNG (com a Pillow)
# ----------------------------------------------------------------------

def tem_pillow():
    try:
        import PIL.Image          # noqa: F401  (só para saber se existe)
        import PIL.ImageDraw      # noqa: F401
        import PIL.ImageFont      # noqa: F401
    except ImportError:
        return False
    return True


# Os arquivos de fonte (.ttf) que o PNG tenta, na ordem: Windows, Linux, macOS
def candidatos_de_fonte(negrito, mono):
    windows = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
    if mono:
        return [os.path.join(windows, "consolab.ttf" if negrito else "consola.ttf"),
                os.path.join(windows, "courbd.ttf" if negrito else "cour.ttf"),
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if negrito else
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/System/Library/Fonts/Menlo.ttc"]
    return [os.path.join(windows, "segoeuib.ttf" if negrito else "segoeui.ttf"),
            os.path.join(windows, "arialbd.ttf" if negrito else "arial.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrito else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if negrito else
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if negrito else
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf"]


FONTES_DO_PNG = {}


def fonte_do_png(tamanho, negrito, mono):
    from PIL import ImageFont
    chave = (round(tamanho), negrito, mono)
    if chave in FONTES_DO_PNG:
        return FONTES_DO_PNG[chave]
    fonte = None
    for caminho in candidatos_de_fonte(negrito, mono):
        if os.path.exists(caminho):
            try:
                fonte = ImageFont.truetype(caminho, max(1, round(tamanho)))
                break
            except OSError:
                continue
    if fonte is None:
        try:
            fonte = ImageFont.load_default(size=max(1, round(tamanho)))    # Pillow 10.1 ou mais nova
        except TypeError:
            fonte = ImageFont.load_default()
    FONTES_DO_PNG[chave] = fonte
    return fonte


def rgb(cor):
    return (round(cor[0]), round(cor[1]), round(cor[2]))


# Desenha a figura num PNG. escala: o tamanho final (1,5 = 50% maior que na tela).
# A figura é desenhada "amostragem" vezes maior e depois reduzida: assim as bordas ficam suaves
# (sem os degraus de pixel), o que a Pillow sozinha não faz nas linhas.
def salvar_png(figura, caminho, escala=1.5, amostragem=3):
    from PIL import Image, ImageDraw
    fator = escala * amostragem
    largura_final = max(1, round(figura["largura"] * escala))
    altura_final = max(1, round(figura["altura"] * escala))
    fundo = figura.get("fundo") or (255, 255, 255)
    imagem = Image.new("RGB", (largura_final * amostragem, altura_final * amostragem), rgb(fundo))
    desenho = ImageDraw.Draw(imagem)

    def escalar(pontos):
        return [(x * fator, y * fator) for x, y in pontos]

    def riscar(pontos, cor, espessura, tracejado, fechado=False):
        if cor is None or len(pontos) < 2:
            return
        largura = max(1, round(espessura * fator))
        if fechado and pontos[0] != pontos[-1]:
            pontos = list(pontos) + [pontos[0]]
        pedacos = geometria.tracejar(pontos, tracejado) if tracejado else [pontos]
        for pedaco in pedacos:
            if len(pedaco) >= 2:
                desenho.line(escalar(pedaco), fill=rgb(cor), width=largura, joint="curve")

    for forma in figura["formas"]:
        tipo = forma["tipo"]
        if tipo == "linha":
            pontos, poligonos = geometria.aplicar_pontas(forma["pontos"], forma.get("ponta"),
                                                         forma.get("forma_da_ponta", (8, 10, 3)), forma["espessura"])
            pontos = geometria.pontos_da_linha(pontos, forma.get("suave"))
            riscar(pontos, forma["cor"], forma["espessura"], forma.get("tracejado"))
            for poligono in poligonos:
                desenho.polygon(escalar(poligono), fill=rgb(forma["cor"]))
        elif tipo == "poligono":
            if forma.get("preenchimento") is not None:
                desenho.polygon(escalar(forma["pontos"]), fill=rgb(forma["preenchimento"]))
            riscar(forma["pontos"], forma.get("contorno"), forma["espessura"], forma.get("tracejado"), fechado=True)
        elif tipo in ("elipse", "retangulo"):
            x0, y0, x1, y1 = forma["caixa"]
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            if forma.get("preenchimento") is not None:
                caixa = [x0 * fator, y0 * fator, x1 * fator, y1 * fator]
                if tipo == "elipse":
                    desenho.ellipse(caixa, fill=rgb(forma["preenchimento"]))
                else:
                    desenho.rectangle(caixa, fill=rgb(forma["preenchimento"]))
            if forma.get("contorno") is not None:
                if tipo == "elipse":
                    contorno = geometria.pontos_da_elipse(x0, y0, x1, y1, 96)
                else:
                    contorno = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
                riscar(contorno, forma["contorno"], forma["espessura"], forma.get("tracejado"), fechado=True)
        elif tipo == "texto":
            fonte = fonte_do_png(forma["tamanho"] * fator, bool(forma.get("negrito")), bool(forma.get("mono")))
            ancora = {"esquerda": "ls", "centro": "ms", "direita": "rs"}[forma.get("alinhamento", "esquerda")]
            try:
                desenho.text((forma["x"] * fator, forma["base"] * fator), forma["texto"], fill=rgb(forma["cor"]),
                             font=fonte, anchor=ancora)
            except ValueError:
                # Fonte antiga (bitmap) não aceita âncora: escreve sem ela, um pouco acima da base
                desenho.text((forma["x"] * fator, (forma["base"] - forma["tamanho"]) * fator), forma["texto"],
                             fill=rgb(forma["cor"]), font=fonte)
    imagem = imagem.resize((largura_final, altura_final), Image.LANCZOS)
    temporario = str(caminho) + ".tmp"
    imagem.save(temporario, format="PNG")
    os.replace(temporario, str(caminho))


# ----------------------------------------------------------------------
# PDF (numa página do exportacao/pdf.py)
# ----------------------------------------------------------------------

def fonte_do_pdf(forma):
    if forma.get("mono"):
        return "Courier-Bold" if forma.get("negrito") else "Courier"
    if forma.get("negrito"):
        return "Helvetica-Bold"
    if forma.get("italico"):
        return "Helvetica-Oblique"
    return "Helvetica"


# Desenha a figura dentro da caixa (x, y, largura, altura) da página, do maior tamanho que couber,
# centralizada na horizontal. Devolve a altura que ocupou.
def desenhar_no_pdf(pagina, figura, x, y, largura, altura, com_fundo=True, borda=None):
    escala = min(largura / figura["largura"], altura / figura["altura"])
    x0 = x + (largura - figura["largura"] * escala) / 2
    y0 = y

    def ponto(p):
        return (x0 + p[0] * escala, y0 + p[1] * escala)

    def tracejado(forma):
        if not forma.get("tracejado"):
            return None
        return [valor * escala for valor in forma["tracejado"]]

    if com_fundo and figura.get("fundo") is not None:
        pagina.retangulo(x0, y0, x0 + figura["largura"] * escala, y0 + figura["altura"] * escala,
                         preenchimento=figura["fundo"], contorno=borda, espessura=0.5)
    for forma in figura["formas"]:
        tipo = forma["tipo"]
        if tipo == "linha":
            forma_da_ponta = [valor * escala for valor in forma.get("forma_da_ponta", (8, 10, 3))]
            pagina.linha([ponto(p) for p in forma["pontos"]], cor=forma["cor"], espessura=forma["espessura"] * escala,
                         tracejado=tracejado(forma), suave=bool(forma.get("suave")), ponta=forma.get("ponta"),
                         forma_da_ponta=forma_da_ponta)
        elif tipo == "poligono":
            pagina.poligono([ponto(p) for p in forma["pontos"]], preenchimento=forma.get("preenchimento"),
                            contorno=forma.get("contorno"), espessura=forma["espessura"] * escala,
                            tracejado=tracejado(forma))
        elif tipo in ("elipse", "retangulo"):
            a = ponto(forma["caixa"][0:2])
            b = ponto(forma["caixa"][2:4])
            funcao = pagina.elipse if tipo == "elipse" else pagina.retangulo
            funcao(a[0], a[1], b[0], b[1], preenchimento=forma.get("preenchimento"), contorno=forma.get("contorno"),
                   espessura=forma["espessura"] * escala, tracejado=tracejado(forma))
        elif tipo == "texto":
            x_texto, base = ponto((forma["x"], forma["base"]))
            pagina.texto_na_base(x_texto, base, forma["texto"], forma["tamanho"] * escala, fonte_do_pdf(forma),
                                 forma["cor"], forma.get("alinhamento", "esquerda"))
    return figura["altura"] * escala


# A caixa ocupada pelas formas (para recortar as sobras de fundo em volta do desenho).
# O texto conta pela largura na Helvetica (aproximada) e pela altura da letra.
def caixa_das_formas(figura):
    xs = []
    ys = []
    for forma in figura["formas"]:
        tipo = forma["tipo"]
        folga = forma.get("espessura", 0) / 2
        if tipo in ("linha", "poligono"):
            for x, y in forma["pontos"]:
                xs += [x - folga, x + folga]
                ys += [y - folga, y + folga]
        elif tipo in ("elipse", "retangulo"):
            x0, y0, x1, y1 = forma["caixa"]
            xs += [x0 - folga, x1 + folga]
            ys += [y0 - folga, y1 + folga]
        elif tipo == "texto":
            largura = largura_do_texto(forma["texto"], forma["tamanho"])
            alinhamento = forma.get("alinhamento", "esquerda")
            esquerda = forma["x"]
            if alinhamento == "centro":
                esquerda -= largura / 2
            elif alinhamento == "direita":
                esquerda -= largura
            xs += [esquerda, esquerda + largura]
            ys += [forma["base"] - forma["tamanho"], forma["base"] + forma["tamanho"] * 0.3]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


# Uma figura recortada em volta das formas (com uma margem): o desenho fica maior no relatório
def recortar(figura, margem=12):
    caixa = caixa_das_formas(figura)
    if caixa is None:
        return figura
    x0 = max(0, caixa[0] - margem)
    y0 = max(0, caixa[1] - margem)
    x1 = min(figura["largura"], caixa[2] + margem)
    y1 = min(figura["altura"], caixa[3] + margem)
    if x1 - x0 < 10 or y1 - y0 < 10:
        return figura
    formas = []
    for forma in figura["formas"]:
        nova = dict(forma)
        if "pontos" in nova:
            nova["pontos"] = [(x - x0, y - y0) for x, y in nova["pontos"]]
        if "caixa" in nova:
            a, b, c, d = nova["caixa"]
            nova["caixa"] = (a - x0, b - y0, c - x0, d - y0)
        if nova["tipo"] == "texto":
            nova["x"] = nova["x"] - x0
            nova["base"] = nova["base"] - y0
        formas.append(nova)
    return {"largura": x1 - x0, "altura": y1 - y0, "fundo": figura.get("fundo"), "formas": formas}
