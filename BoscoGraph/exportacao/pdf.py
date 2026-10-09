'''
    Um escritor de PDF mínimo, só com a biblioteca padrão do Python (o relatório do BoscoGraph não pode
    depender de nada que precise ser instalado).

    Como é um arquivo PDF por dentro (simplificado):
        %PDF-1.4                              <- o cabeçalho
        1 0 obj << ... >> endobj              <- "objetos" numerados: o catálogo, as páginas, as fontes...
        5 0 obj << /Length 120 >> stream      <- o conteúdo de uma página é um "stream": uma lista de
        ... comandos de desenho ...              comandos de desenho, como "100 200 m 300 200 l S"
        endstream endobj                         (vá para 100,200; linha até 300,200; risque)
        xref ...                              <- a tabela que diz em que byte começa cada objeto
        trailer << /Root 1 0 R >>             <- onde está o catálogo
        %%EOF
    O leitor de PDF usa a tabela xref para achar cada objeto sem ler o arquivo inteiro: por isso os
    deslocamentos (em bytes) têm que estar certos.

    As fontes são as 14 fontes padrão que todo leitor de PDF já tem (não precisam ir dentro do arquivo):
    Helvetica (como a Arial), Courier (para código) e Symbol (para ∞, →, π, ≤...). O texto vai na
    codificação WinAnsi (a do Windows: tem todos os acentos do português); o que ela não tem e a Symbol
    tem é escrito com a Symbol no meio do texto.

    Coordenadas como no Canvas do Tkinter: (0, 0) no canto de CIMA à esquerda e y crescendo para BAIXO.
    O PDF faz o contrário (y cresce para cima): a Pagina converte (y_do_pdf = altura - y).
    Medidas em pontos: 1 ponto = 1/72 de polegada (a folha A4 tem 595 × 842 pontos).
'''

import datetime
import os
import zlib

from exportacao.geometria import aplicar_pontas, cubicas_da_curva

A4 = (595.28, 841.89)
FONTES = ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Courier", "Courier-Bold")

# O nome de cada fonte dentro do arquivo (/F1, /F2...) e o nome dela no padrão do PDF
NOMES_INTERNOS = {"Helvetica": "F1", "Helvetica-Bold": "F2", "Helvetica-Oblique": "F3", "Courier": "F4",
                  "Courier-Bold": "F5", "Symbol": "F6"}

# A parte de cima (ascendente) e de baixo (descendente) das letras, em milésimos do tamanho da fonte
# (das tabelas AFM da Adobe): servem para saber a altura de uma linha de texto
METRICAS = {"Helvetica": (718, -207), "Helvetica-Bold": (718, -207), "Helvetica-Oblique": (718, -207),
            "Courier": (629, -157), "Courier-Bold": (629, -157)}

# Os caracteres que a fonte Symbol tem: {caractere: (código na Symbol, largura em milésimos)}
SIMBOLOS = {
    "∞": (0xA5, 713), "→": (0xAE, 987), "←": (0xAC, 987), "↑": (0xAD, 603), "↓": (0xAF, 603), "↔": (0xAB, 1042),
    "⇒": (0xDE, 987), "π": (0x70, 549), "Σ": (0x53, 592), "∑": (0xE5, 713), "Δ": (0x44, 612), "≤": (0xA3, 549),
    "≥": (0xB3, 549), "≠": (0xB9, 549), "∅": (0xC6, 823), "∈": (0xCE, 713), "α": (0x61, 631), "β": (0x62, 549),
    "γ": (0x67, 411), "δ": (0x64, 494), "λ": (0x6C, 549), "μ": (0x6D, 576), "√": (0xD6, 549), "∂": (0xB6, 494),
}

# O que nem a WinAnsi nem a Symbol têm vira um substituto parecido
SUBSTITUTOS = {"⇝": "->", "▶": ">", "◀": "<", "✓": "v", "✔": "v", "⚠": "!", "ⓘ": "i", "★": "*", "●": "•",
               "−": "-", "″": "\"", "′": "'", "▸": ">", "◂": "<", "×": "×", "≈": "~", "…": "…"}


# ----------------------------------------------------------------------
# Texto: codificação e largura
# ----------------------------------------------------------------------

# Separa um texto em pedaços de uma fonte só: [(fonte, bytes, largura em milésimos), ...]
# (os caracteres da Symbol viram pedaços com a fonte "Symbol")
def pedacos_do_texto(texto, fonte):
    pedacos = []
    for caractere in texto:
        if caractere in SUBSTITUTOS and caractere not in SIMBOLOS:
            substituto = SUBSTITUTOS[caractere]
            try:
                substituto.encode("cp1252")
            except UnicodeEncodeError:
                substituto = "?"
            caractere = substituto
        if len(caractere) == 1 and caractere in SIMBOLOS:
            codigo, largura = SIMBOLOS[caractere]
            acrescentar(pedacos, "Symbol", bytes([codigo]), largura)
            continue
        for letra in caractere:                 # um substituto pode ter mais de uma letra ("->")
            try:
                codigo = letra.encode("cp1252")
            except UnicodeEncodeError:
                codigo = b"?"
            acrescentar(pedacos, fonte, codigo, largura_da_letra(codigo[0], fonte))
    return pedacos


# Junta com o pedaço anterior se for da mesma fonte
def acrescentar(pedacos, fonte, codigo, largura):
    if pedacos and pedacos[-1][0] == fonte:
        anterior_fonte, anterior_bytes, anterior_largura = pedacos[-1]
        pedacos[-1] = (fonte, anterior_bytes + codigo, anterior_largura + largura)
    else:
        pedacos.append((fonte, codigo, largura))


def largura_da_letra(codigo, fonte):
    if fonte.startswith("Courier"):
        return 600
    tabela = LARGURA_HELVETICA_NEGRITO if fonte == "Helvetica-Bold" else LARGURA_HELVETICA
    return tabela.get(codigo, 556)


# A largura de um texto (em pontos) numa fonte e num tamanho
def largura_do_texto(texto, tamanho, fonte="Helvetica"):
    total = 0
    for nome, codigo, largura in pedacos_do_texto(texto, fonte):
        total += largura
    return total * tamanho / 1000


# Quebra um texto em linhas que cabem na largura (nos espaços; uma palavra grande demais é partida).
# Respeita as quebras de linha que já existem ("\n").
def quebrar_texto(texto, largura_maxima, tamanho, fonte="Helvetica"):
    linhas = []
    for paragrafo in texto.split("\n"):
        atual = ""
        for palavra in paragrafo.split(" "):
            tentativa = palavra if atual == "" else atual + " " + palavra
            if largura_do_texto(tentativa, tamanho, fonte) <= largura_maxima:
                atual = tentativa
                continue
            if atual != "":
                linhas.append(atual)
                atual = ""
            # A palavra sozinha não cabe: parte em pedaços
            while largura_do_texto(palavra, tamanho, fonte) > largura_maxima and len(palavra) > 1:
                corte = len(palavra) - 1
                while corte > 1 and largura_do_texto(palavra[:corte], tamanho, fonte) > largura_maxima:
                    corte -= 1
                linhas.append(palavra[:corte])
                palavra = palavra[corte:]
            atual = palavra
        linhas.append(atual)
    return linhas


# Um texto entre parênteses no formato do PDF: ( e ) e \ precisam de uma barra antes; o resto que não
# é letra comum vai como número octal (\245)
def string_do_pdf(dados):
    partes = ["("]
    for byte in dados:
        if byte in (0x28, 0x29, 0x5C):
            partes.append("\\" + chr(byte))
        elif 32 <= byte < 127:
            partes.append(chr(byte))
        else:
            partes.append("\\%03o" % byte)
    partes.append(")")
    return "".join(partes)


# ----------------------------------------------------------------------
# Cores e números
# ----------------------------------------------------------------------

# (r, g, b) de 0 a 255, ou "#rrggbb" -> três números de 0 a 1, como o PDF quer
def cor_do_pdf(cor):
    if isinstance(cor, str):
        cor = cor.lstrip("#")
        cor = (int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16))
    return f"{cor[0] / 255:.3f} {cor[1] / 255:.3f} {cor[2] / 255:.3f}"


def n(numero):
    texto = f"{numero:.2f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto if texto != "-0" else "0"


# ----------------------------------------------------------------------
# A página
# ----------------------------------------------------------------------

class Pagina:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        # Pontas retas e junções arredondadas, como o Tkinter desenha (capstyle "butt", joinstyle "round")
        self.comandos = ["0 J 1 j"]
        self.fontes_usadas = set()

    def y(self, y):
        return self.altura - y

    def p(self, ponto):
        return f"{n(ponto[0])} {n(self.y(ponto[1]))}"

    def estilo_do_traco(self, cor, espessura, tracejado):
        comandos = [f"{cor_do_pdf(cor)} RG", f"{n(espessura)} w"]
        if tracejado:
            comandos.append("[" + " ".join(n(valor) for valor in tracejado) + "] 0 d")
        else:
            comandos.append("[] 0 d")
        return comandos

    # Uma linha (reta ou curva suave), com ponta de seta se pedir
    def linha(self, pontos, cor=(0, 0, 0), espessura=1.0, tracejado=None, suave=False, ponta=None,
              forma_da_ponta=(8, 10, 3)):
        if len(pontos) < 2:
            return
        pontos, poligonos = aplicar_pontas(pontos, ponta, forma_da_ponta, espessura)
        comandos = ["q"] + self.estilo_do_traco(cor, espessura, tracejado)
        if suave and len(pontos) > 2:
            inicio, cubicas = cubicas_da_curva(pontos)
            comandos.append(f"{self.p(inicio)} m")
            for c1, c2, fim in cubicas:
                comandos.append(f"{self.p(c1)} {self.p(c2)} {self.p(fim)} c")
        else:
            comandos.append(f"{self.p(pontos[0])} m")
            for ponto in pontos[1:]:
                comandos.append(f"{self.p(ponto)} l")
        comandos.append("S Q")
        self.comandos.append(" ".join(comandos))
        for poligono in poligonos:
            self.poligono(poligono, preenchimento=cor, contorno=None)

    def caminho_fechado(self, comandos_do_caminho, preenchimento, contorno, espessura, tracejado):
        if preenchimento is None and contorno is None:
            return
        comandos = ["q"]
        if contorno is not None:
            comandos += self.estilo_do_traco(contorno, espessura, tracejado)
        if preenchimento is not None:
            comandos.append(f"{cor_do_pdf(preenchimento)} rg")
        comandos += comandos_do_caminho
        if preenchimento is not None and contorno is not None:
            comandos.append("B")           # preenche e risca
        elif preenchimento is not None:
            comandos.append("f")
        else:
            comandos.append("s")           # fecha e risca
        comandos.append("Q")
        self.comandos.append(" ".join(comandos))

    def poligono(self, pontos, preenchimento=None, contorno=(0, 0, 0), espessura=1.0, tracejado=None):
        if len(pontos) < 2:
            return
        caminho = [f"{self.p(pontos[0])} m"]
        for ponto in pontos[1:]:
            caminho.append(f"{self.p(ponto)} l")
        caminho.append("h")
        self.caminho_fechado(caminho, preenchimento, contorno, espessura, tracejado)

    def retangulo(self, x0, y0, x1, y1, preenchimento=None, contorno=(0, 0, 0), espessura=1.0, tracejado=None):
        esquerda, direita = min(x0, x1), max(x0, x1)
        cima, baixo = min(y0, y1), max(y0, y1)
        caminho = [f"{n(esquerda)} {n(self.y(baixo))} {n(direita - esquerda)} {n(baixo - cima)} re"]
        self.caminho_fechado(caminho, preenchimento, contorno, espessura, tracejado)

    # A elipse dentro da caixa (como o create_oval do Tkinter): 4 Béziers cúbicas, uma por quarto.
    # k = 0,5523 é o quanto os pontos de controle se afastam para a curva ficar redonda.
    def elipse(self, x0, y0, x1, y1, preenchimento=None, contorno=(0, 0, 0), espessura=1.0, tracejado=None):
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        rx = abs(x1 - x0) / 2
        ry = abs(y1 - y0) / 2
        k = 0.5523
        caminho = [
            f"{self.p((cx + rx, cy))} m",
            f"{self.p((cx + rx, cy - k * ry))} {self.p((cx + k * rx, cy - ry))} {self.p((cx, cy - ry))} c",
            f"{self.p((cx - k * rx, cy - ry))} {self.p((cx - rx, cy - k * ry))} {self.p((cx - rx, cy))} c",
            f"{self.p((cx - rx, cy + k * ry))} {self.p((cx - k * rx, cy + ry))} {self.p((cx, cy + ry))} c",
            f"{self.p((cx + k * rx, cy + ry))} {self.p((cx + rx, cy + k * ry))} {self.p((cx + rx, cy))} c",
            "h",
        ]
        self.caminho_fechado(caminho, preenchimento, contorno, espessura, tracejado)

    # Escreve um texto (pode ter várias linhas, separadas por "\n"), preso pela âncora como no Tkinter.
    # Devolve a caixa ocupada (x0, y0, x1, y1).
    def texto(self, x, y, texto, tamanho=10, fonte="Helvetica", cor=(0, 0, 0), ancora="nw"):
        if fonte not in METRICAS:
            fonte = "Helvetica"
        ascendente, descendente = METRICAS[fonte]
        altura_da_letra = (ascendente - descendente) * tamanho / 1000
        entrelinha = tamanho * 1.2
        linhas = texto.split("\n")
        altura_total = altura_da_letra + entrelinha * (len(linhas) - 1)
        larguras = [largura_do_texto(linha, tamanho, fonte) for linha in linhas]
        largura_total = max(larguras) if larguras else 0
        # Onde fica o canto de cima à esquerda da caixa, conforme a âncora
        if "n" in ancora:
            topo = y
        elif "s" in ancora:
            topo = y - altura_total
        else:
            topo = y - altura_total / 2
        if "w" in ancora:
            esquerda = x
        elif "e" in ancora:
            esquerda = x - largura_total
        else:
            esquerda = x - largura_total / 2
        for posicao in range(len(linhas)):
            # Cada linha alinhada como a âncora pede (à esquerda, centralizada ou à direita da caixa)
            if "w" in ancora:
                inicio_x = esquerda
            elif "e" in ancora:
                inicio_x = esquerda + largura_total - larguras[posicao]
            else:
                inicio_x = esquerda + (largura_total - larguras[posicao]) / 2
            base = topo + posicao * entrelinha + ascendente * tamanho / 1000
            self.escrever_linha(inicio_x, base, linhas[posicao], tamanho, fonte, cor)
        return (esquerda, topo, esquerda + largura_total, topo + altura_total)

    # Uma linha de texto com a linha de base em "base" (a linha onde as letras "sentam"); x é a ponta
    # esquerda, o meio ou a ponta direita do texto, conforme o alinhamento ("esquerda", "centro", "direita")
    def texto_na_base(self, x, base, texto, tamanho=10, fonte="Helvetica", cor=(0, 0, 0), alinhamento="esquerda"):
        if fonte not in METRICAS:
            fonte = "Helvetica"
        largura = largura_do_texto(texto, tamanho, fonte)
        if alinhamento == "centro":
            x = x - largura / 2
        elif alinhamento == "direita":
            x = x - largura
        self.escrever_linha(x, base, texto, tamanho, fonte, cor)
        return largura

    def escrever_linha(self, x, base, linha, tamanho, fonte, cor):
        if linha == "":
            return
        comandos = ["BT", f"{cor_do_pdf(cor)} rg", f"{n(x)} {n(self.y(base))} Td"]
        for nome, dados, largura in pedacos_do_texto(linha, fonte):
            self.fontes_usadas.add(nome)
            comandos.append(f"/{NOMES_INTERNOS[nome]} {n(tamanho)} Tf {string_do_pdf(dados)} Tj")
        comandos.append("ET")
        self.comandos.append(" ".join(comandos))

    def conteudo(self):
        return "\n".join(self.comandos).encode("latin-1")


# ----------------------------------------------------------------------
# O documento
# ----------------------------------------------------------------------

def data_do_pdf(momento):
    return momento.strftime("D:%Y%m%d%H%M%S")


class DocumentoPdf:
    def __init__(self, titulo="", autor=""):
        self.titulo = titulo
        self.autor = autor
        self.paginas = []

    def nova_pagina(self, largura=A4[0], altura=A4[1]):
        pagina = Pagina(largura, altura)
        self.paginas.append(pagina)
        return pagina

    # Monta o arquivo inteiro. Os objetos:
    #   1 = catálogo, 2 = lista de páginas, 3 = informações (título...), 4 a 9 = as seis fontes,
    #   e depois, para cada página, a página e o conteúdo dela
    def para_bytes(self):
        objetos = {}
        quantidade_de_paginas = len(self.paginas) or 1
        primeira_pagina = 10
        filhos = []
        for indice in range(quantidade_de_paginas):
            filhos.append(f"{primeira_pagina + 2 * indice} 0 R")
        objetos[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
        objetos[2] = f"<< /Type /Pages /Kids [{' '.join(filhos)}] /Count {quantidade_de_paginas} >>".encode("latin-1")
        agora = datetime.datetime.now()
        objetos[3] = ("<< /Title " + string_do_pdf(texto_em_bytes(self.titulo)) + " /Author " +
                      string_do_pdf(texto_em_bytes(self.autor)) + " /Producer (BoscoGraph) /Creator (BoscoGraph)"
                      f" /CreationDate ({data_do_pdf(agora)}) >>").encode("latin-1")
        numero_da_fonte = {}
        proximo = 4
        for nome in ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Courier", "Courier-Bold", "Symbol"):
            if nome == "Symbol":
                objetos[proximo] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Symbol >>"
            else:
                objetos[proximo] = (f"<< /Type /Font /Subtype /Type1 /BaseFont /{nome} "
                                    f"/Encoding /WinAnsiEncoding >>").encode("latin-1")
            numero_da_fonte[nome] = proximo
            proximo += 1
        recursos = " ".join(f"/{NOMES_INTERNOS[nome]} {numero_da_fonte[nome]} 0 R" for nome in numero_da_fonte)
        paginas = self.paginas or [Pagina(A4[0], A4[1])]
        for indice in range(len(paginas)):
            pagina = paginas[indice]
            numero = primeira_pagina + 2 * indice
            objetos[numero] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {n(pagina.largura)} {n(pagina.altura)}] "
                               f"/Resources << /Font << {recursos} >> >> /Contents {numero + 1} 0 R >>").encode("latin-1")
            comprimido = zlib.compress(pagina.conteudo())
            objetos[numero + 1] = (f"<< /Length {len(comprimido)} /Filter /FlateDecode >>\nstream\n".encode("latin-1")
                                   + comprimido + b"\nendstream")

        # Escreve os objetos anotando onde cada um começa (para a tabela xref)
        saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        deslocamentos = {}
        maior = max(objetos)
        for numero in range(1, maior + 1):
            if numero not in objetos:
                continue
            deslocamentos[numero] = len(saida)
            saida += f"{numero} 0 obj\n".encode("latin-1") + objetos[numero] + b"\nendobj\n"
        inicio_da_tabela = len(saida)
        saida += f"xref\n0 {maior + 1}\n".encode("latin-1")
        saida += b"0000000000 65535 f \n"
        for numero in range(1, maior + 1):
            if numero in deslocamentos:
                saida += f"{deslocamentos[numero]:010d} 00000 n \n".encode("latin-1")
            else:
                saida += b"0000000000 65535 f \n"
        saida += (f"trailer\n<< /Size {maior + 1} /Root 1 0 R /Info 3 0 R >>\nstartxref\n{inicio_da_tabela}\n%%EOF\n"
                  ).encode("latin-1")
        return bytes(saida)

    # Grava sem deixar o arquivo pela metade: primeiro num temporário, depois troca
    def salvar(self, caminho):
        caminho = str(caminho)
        temporario = caminho + ".tmp"
        with open(temporario, "wb") as arquivo:
            arquivo.write(self.para_bytes())
        os.replace(temporario, caminho)


# Um texto para os metadados (título, autor). O PDF aceita esses textos em UTF-16 (2 bytes por letra),
# desde que comecem com a "marca" FE FF: assim cabe qualquer caractere (acentos, π, ∞...).
def texto_em_bytes(texto):
    return b"\xfe\xff" + texto.encode("utf-16-be")


# ----------------------------------------------------------------------
# As larguras das letras (das tabelas AFM da Adobe), em milésimos do tamanho da fonte
# ----------------------------------------------------------------------
# CODIGOS_DO_WINANSI são os códigos (de 32 a 255) que a codificação WinAnsi usa; HELVETICA e
# HELVETICA_NEGRITO têm a largura de cada um, NA MESMA ORDEM. Exemplo: o código 65 é o "A", que tem 667
# na Helvetica: um "A" de tamanho 10 ocupa 667 × 10 / 1000 = 6,67 pontos.
# (A Helvetica-Oblique, a inclinada, tem as mesmas larguras da Helvetica; a Courier tem 600 em tudo.)

CODIGOS_DO_WINANSI = [
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
    72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
    92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 128, 130, 131, 132, 133,
    134, 135, 136, 137, 138, 139, 140, 142, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156,
    158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
    178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197,
    198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217,
    218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237,
    238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
]

HELVETICA = [
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556,
    556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778,
    722, 278, 500, 667, 556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278,
    278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584, 556, 222, 556, 333, 1000,
    556, 556, 333, 1000, 667, 333, 1000, 611, 222, 222, 333, 333, 350, 556, 1000, 333, 1000, 500, 333, 944,
    500, 667, 278, 333, 556, 556, 556, 556, 260, 556, 333, 737, 370, 556, 584, 333, 737, 333, 400, 584,
    333, 333, 333, 556, 537, 278, 333, 333, 365, 556, 834, 834, 834, 611, 667, 667, 667, 667, 667, 667,
    1000, 722, 667, 667, 667, 667, 278, 278, 278, 278, 722, 722, 778, 778, 778, 778, 778, 584, 778, 722,
    722, 722, 722, 667, 667, 611, 556, 556, 556, 556, 556, 556, 889, 500, 556, 556, 556, 556, 278, 278,
    278, 278, 556, 556, 556, 556, 556, 556, 556, 584, 611, 556, 556, 556, 556, 500, 556, 500,
]

HELVETICA_NEGRITO = [
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556,
    556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778,
    722, 278, 556, 722, 611, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333,
    278, 333, 584, 556, 333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584, 556, 278, 556, 500, 1000,
    556, 556, 333, 1000, 667, 333, 1000, 611, 278, 278, 500, 500, 350, 556, 1000, 333, 1000, 556, 333, 944,
    500, 667, 278, 333, 556, 556, 556, 556, 280, 556, 333, 737, 370, 556, 584, 333, 737, 333, 400, 584,
    333, 333, 333, 611, 556, 278, 333, 333, 365, 556, 834, 834, 834, 611, 722, 722, 722, 722, 722, 722,
    1000, 722, 667, 667, 667, 667, 278, 278, 278, 278, 722, 722, 778, 778, 778, 778, 778, 584, 778, 722,
    722, 722, 722, 667, 667, 611, 556, 556, 556, 556, 556, 556, 889, 556, 556, 556, 556, 556, 278, 278,
    278, 278, 611, 611, 611, 611, 611, 611, 611, 584, 611, 611, 611, 611, 611, 556, 611, 556,
]

# Os dicionários {código: largura} que a largura_da_letra consulta
LARGURA_HELVETICA = {}
LARGURA_HELVETICA_NEGRITO = {}
for posicao in range(len(CODIGOS_DO_WINANSI)):
    LARGURA_HELVETICA[CODIGOS_DO_WINANSI[posicao]] = HELVETICA[posicao]
    LARGURA_HELVETICA_NEGRITO[CODIGOS_DO_WINANSI[posicao]] = HELVETICA_NEGRITO[posicao]
