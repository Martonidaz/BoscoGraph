'''
    Gera o ícone do Windows (instalador/boscograph.ico) com o mesmo desenho do logo (visual/logo.py) e as
    imagens do assistente de instalação (instalador/assistente_*.bmp), com as cores da paleta.

    Um arquivo .ico guarda o MESMO desenho em vários tamanhos (16, 24, 32, 48, 64, 128 e 256 pixels):
    o Windows escolhe o tamanho certo para cada lugar (barra de tarefas, área de trabalho, Explorer).
    Diminuir uma imagem grande na hora deixa o ícone pequeno borrado; por isso cada tamanho é desenhado
    à parte, a partir do desenho em 4 vezes o tamanho e reduzido com média (fica suave, sem "serrilhado").

    As imagens do assistente: a faixa da esquerda das telas de boas-vindas e de fim (164 x 314 pixels a 100%)
    e o quadradinho do canto das outras telas (58 x 58). Cada uma sai em quatro tamanhos (100%, 150%, 200%
    e 250%): o Inno Setup escolhe o que combina com a escala da tela do Windows. São BMP de 24 bits, o
    formato que toda versão do Inno Setup 6 aceita.

    Precisa da biblioteca Pillow (pip install pillow). Uso: python instalador/gerar_icone.py
'''

import sys
from pathlib import Path

PASTA_DO_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA_DO_PROJETO))

from visual.logo import VERTICES_DO_LOGO, ARESTAS_DO_LOGO, COR_DO_FUNDO, COR_DAS_ARESTAS, COR_DO_CONTORNO

TAMANHOS = [16, 24, 32, 48, 64, 128, 256]
ARQUIVO_DO_ICONE = PASTA_DO_PROJETO / "instalador" / "boscograph.ico"
ESCALAS = [100, 150, 200, 250]          # em %, como a escala da tela do Windows

# A paleta da universidade (a mesma do visual/tema.py)
AZUL_MARINHO = "#03296a"
AZUL_MARINHO_2 = "#053e75"
AZUL_ACINZENTADO = "#6880a1"
CINZA_AZULADO = "#d7dce4"
VERMELHO = "#fd2016"
SALMAO = "#fe7874"
ROSA_CLARO = "#febbb9"

# Os vértices de enfeite da faixa (x, y como fração da faixa, cor) e as arestas entre eles
ENFEITE_VERTICES = [(0.22, 0.58, SALMAO), (0.66, 0.54, CINZA_AZULADO), (0.80, 0.70, ROSA_CLARO),
                    (0.38, 0.76, VERMELHO), (0.18, 0.88, CINZA_AZULADO), (0.62, 0.90, SALMAO)]
ENFEITE_ARESTAS = [(0, 1), (1, 2), (0, 3), (1, 3), (2, 5), (3, 4), (3, 5)]


# O logo num quadrado de "tamanho" pixels (as mesmas frações e cores do visual/logo.py)
def desenhar(tamanho):
    from PIL import Image, ImageDraw
    grande = tamanho * 4                                     # desenha em 4x e depois reduz
    imagem = Image.new("RGBA", (grande, grande), (0, 0, 0, 0))
    lapis = ImageDraw.Draw(imagem)
    lapis.rounded_rectangle((0, 0, grande - 1, grande - 1), radius=int(grande * 0.22), fill=COR_DO_FUNDO)
    centros = []
    for fracao_x, fracao_y, cor in VERTICES_DO_LOGO:
        centros.append((fracao_x * grande, fracao_y * grande))
    for origem, destino in ARESTAS_DO_LOGO:
        lapis.line([centros[origem], centros[destino]], fill=COR_DAS_ARESTAS, width=max(1, int(grande * 0.06)))
    raio = grande * 0.14
    for i in range(len(centros)):
        cx, cy = centros[i]
        lapis.ellipse((cx - raio, cy - raio, cx + raio, cy + raio), fill=VERTICES_DO_LOGO[i][2],
                      outline=COR_DO_CONTORNO, width=max(1, int(grande * 0.035)))
    return imagem.resize((tamanho, tamanho), Image.LANCZOS)


# Uma cor "#rrggbb" vira (r, g, b)
def rgb(cor):
    return tuple(int(cor[posicao:posicao + 2], 16) for posicao in (1, 3, 5))


# O grafo do logo (sem o quadrado) dentro do quadrado de lado "lado" com o canto em (x, y)
def desenhar_grafo_do_logo(lapis, x, y, lado):
    centros = []
    for fracao_x, fracao_y, cor in VERTICES_DO_LOGO:
        centros.append((x + fracao_x * lado, y + fracao_y * lado))
    for origem, destino in ARESTAS_DO_LOGO:
        lapis.line([centros[origem], centros[destino]], fill=COR_DAS_ARESTAS, width=max(1, int(lado * 0.06)))
    raio = lado * 0.14
    for i in range(len(centros)):
        cx, cy = centros[i]
        lapis.ellipse((cx - raio, cy - raio, cx + raio, cy + raio), fill=VERTICES_DO_LOGO[i][2],
                      outline=COR_DO_CONTORNO, width=max(1, int(lado * 0.035)))


# A faixa da esquerda: o azul-marinho em degradê, o grafo do logo em cima, um grafo de enfeite embaixo e
# uma linha vermelha no pé. Desenha em 4 vezes o tamanho e reduz (as bordas ficam suaves).
def desenhar_faixa(largura, altura):
    from PIL import Image, ImageDraw
    grande_l, grande_a = largura * 4, altura * 4
    imagem = Image.new("RGB", (grande_l, grande_a))
    lapis = ImageDraw.Draw(imagem)
    cima, baixo = rgb(AZUL_MARINHO), rgb(AZUL_MARINHO_2)
    for y in range(grande_a):                                   # o degradê, uma linha por vez
        fracao = y / (grande_a - 1)
        cor = tuple(round(cima[i] + (baixo[i] - cima[i]) * fracao) for i in range(3))
        lapis.line([(0, y), (grande_l, y)], fill=cor)
    lado = grande_l * 0.64
    desenhar_grafo_do_logo(lapis, (grande_l - lado) / 2, grande_a * 0.07, lado)
    pontos = [(x * grande_l, y * grande_a) for x, y, cor in ENFEITE_VERTICES]
    for origem, destino in ENFEITE_ARESTAS:
        lapis.line([pontos[origem], pontos[destino]], fill=AZUL_ACINZENTADO, width=max(1, int(grande_l * 0.012)))
    raio = grande_l * 0.045
    for (x, y), (fx, fy, cor) in zip(pontos, ENFEITE_VERTICES):
        lapis.ellipse((x - raio, y - raio, x + raio, y + raio), fill=cor)
    lapis.rectangle((0, grande_a * 0.985, grande_l, grande_a), fill=VERMELHO)
    return imagem.resize((largura, altura), Image.LANCZOS)


# O quadradinho do canto: o logo num fundo branco (o fundo do topo das telas do assistente)
def desenhar_quadradinho(lado):
    from PIL import Image
    imagem = Image.new("RGB", (lado, lado), "#ffffff")
    logo = desenhar(round(lado * 0.86))
    margem = (lado - logo.width) // 2
    imagem.paste(logo, (margem, margem), logo)                  # a transparência do logo vira o branco
    return imagem


# Grava as imagens do assistente (8 arquivos .bmp) e devolve a lista
def gerar_imagens_do_assistente(pasta=PASTA_DO_PROJETO / "instalador"):
    feitos = []
    for escala in ESCALAS:
        faixa = pasta / f"assistente_{escala}.bmp"
        desenhar_faixa(round(164 * escala / 100), round(314 * escala / 100)).save(faixa, format="BMP")
        quadradinho = pasta / f"assistente_pequena_{escala}.bmp"
        desenhar_quadradinho(round(58 * escala / 100)).save(quadradinho, format="BMP")
        feitos += [faixa, quadradinho]
    return feitos


def gerar(destino=ARQUIVO_DO_ICONE):
    imagens = []
    for tamanho in TAMANHOS:
        imagens.append(desenhar(tamanho))
    # O Pillow grava todos os tamanhos num .ico só: o maior é a base e os outros vão junto
    imagens[-1].save(destino, format="ICO", sizes=[(t, t) for t in TAMANHOS], append_images=imagens[:-1])
    return destino


if __name__ == "__main__":
    print(f"Ícone gerado: {gerar()}")
    print(f"Imagens do assistente: {len(gerar_imagens_do_assistente())} arquivos .bmp")
