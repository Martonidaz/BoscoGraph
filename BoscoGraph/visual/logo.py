# O logo do BoscoGraph: três vértices com as cores da busca em profundidade
# (Branco, Cinza e Preto) ligados por arestas, num quadrado azul-marinho de cantos arredondados.
# As cores são as da paleta da universidade (veja visual/tema.py): o azul-marinho no fundo, o
# cinza-azulado nas arestas e o vermelho no contorno dos vértices.
# O editor desenha o logo no canto de cima; o mesmo desenho está salvo em
# visual/icone.png, que vira o ícone da janela (barra de tarefas do Windows).

# Posição (x, y) de cada vértice como fração do tamanho do logo, e a cor dele
VERTICES_DO_LOGO = [
    (0.31, 0.31, "#ffffff"),        # Branco: ainda não descoberto
    (0.72, 0.40, "#9e9e9e"),        # Cinza: em exploração
    (0.42, 0.73, "#1b1b1b"),        # Preto: finalizado
]
ARESTAS_DO_LOGO = [(0, 1), (1, 2), (2, 0)]
COR_DO_FUNDO = "#03296a"
COR_DAS_ARESTAS = "#d7dce4"
COR_DO_CONTORNO = "#fd2016"


# Retângulo de cantos arredondados: um polígono com "smooth" (o Tkinter arredonda os cantos)
def retangulo_arredondado(canvas, x1, y1, x2, y2, raio, **opcoes):
    pontos = [
        x1 + raio, y1, x2 - raio, y1, x2, y1, x2, y1 + raio,
        x2, y2 - raio, x2, y2, x2 - raio, y2, x1 + raio, y2,
        x1, y2, x1, y2 - raio, x1, y1 + raio, x1, y1,
    ]
    return canvas.create_polygon(pontos, smooth=True, **opcoes)


# Desenha o logo com o canto de cima à esquerda em (x, y) e o lado com "tamanho" pixels
def desenhar_logo(canvas, x, y, tamanho):
    retangulo_arredondado(canvas, x, y, x + tamanho, y + tamanho, tamanho * 0.22, fill=COR_DO_FUNDO, outline="")
    centros = []
    for fracao_x, fracao_y, cor in VERTICES_DO_LOGO:
        centros.append((x + fracao_x * tamanho, y + fracao_y * tamanho))
    for origem, destino in ARESTAS_DO_LOGO:
        canvas.create_line(centros[origem], centros[destino], fill=COR_DAS_ARESTAS, width=max(1, tamanho * 0.06))
    raio = tamanho * 0.14
    for i in range(len(centros)):
        cx, cy = centros[i]
        cor = VERTICES_DO_LOGO[i][2]
        canvas.create_oval(cx - raio, cy - raio, cx + raio, cy + raio, fill=cor,
                           outline=COR_DO_CONTORNO, width=max(1, tamanho * 0.035))
