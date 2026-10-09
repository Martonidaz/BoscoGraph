# A prévia de um grafo: um desenho pequeno e simples, usado na conferência da importação e na tela do
# arquivo .bosco. Vértices brancos com o nome, arestas (com seta quando o grafo é orientado) e os pesos
# no meio das arestas. A geometria é a mesma da visualização (visual/desenho.py).

from tkinter import font as tkfont

import entrada
from visual import desenho


# Desenha o grafo numa área do Canvas: o canto de cima à esquerda em (x0, y0) e o tamanho largura x altura.
#   arrumacao: "arquivo" (as posições do desenho original, se houver) ou "circulo"
#   fundo: a cor de trás (o retângulo atrás de cada peso tem essa cor, para o peso não ficar riscado)
def desenhar_grafo(canvas, app, vertices, arestas, direcionado, posicoes, arrumacao, x0, y0, largura, altura, fundo):
    tema = app.tema
    if not vertices:
        canvas.create_text(x0 + largura / 2, y0 + altura / 2, text="(nenhum vértice)", fill=tema["texto_suave"],
                           font=app.fontes["texto"])
        return
    pares = []
    for origem, destino, nome, peso in arestas:
        pares.append((origem, destino))
    if posicoes and arrumacao == "arquivo" and all(vertice in posicoes for vertice in vertices):
        medidas = desenho.medidas_livres(vertices, posicoes, largura, altura, 0.8)
        lugares = desenho.posicoes_livres(vertices, posicoes, medidas, 0)
        centro = desenho.centro_das_posicoes(lugares)
        curvar = False
    else:
        medidas = desenho.calcular_medidas(len(vertices), largura, altura, 0.8)
        centro = medidas["centro"]
        lugares = desenho.posicoes_em_circulo(vertices, centro, medidas["raio_circulo"])
        curvar = True
    raio = medidas["raio_vertice"]
    pontos = desenho.pontos_de_todas_as_arestas(pares, lugares, vertices, centro, raio, curvar)
    seta = "last" if direcionado else "none"
    marca = "previa"                # todos os itens ganham esta marca, para irem juntos para (x0, y0)
    for i in range(len(pares)):
        canvas.create_line(pontos[i], smooth=True, arrow=seta, arrowshape=medidas["ponta_da_seta"],
                           fill=tema["aresta_grafo"], width=medidas["espessura"] * 1.2, tags=marca)
        peso = arestas[i][3]
        if peso is not None:
            x, y = desenho.ponto_do_nome_da_aresta(pontos[i], raio * 0.45)
            item = canvas.create_text(x, y, text=entrada.formatar_numero(peso), fill=tema["texto_suave"],
                                      font=app.fontes["pequena"], tags=marca)
            caixa = canvas.bbox(item)
            atras = canvas.create_rectangle(caixa[0] - 2, caixa[1], caixa[2] + 2, caixa[3], fill=fundo, outline="",
                                            tags=marca)
            canvas.tag_lower(atras, item)
    # Como na visualização: o nome que não cabe no círculo vai para fora, embaixo do vértice
    fonte = tkfont.Font(root=canvas, family="Segoe UI", size=-max(9, round(raio * 0.7)), weight="bold")
    canvas.fonte_da_previa = fonte          # guardada no Canvas: o Python não pode apagar a fonte em uso
    for nome in vertices:
        x, y = lugares[nome]
        canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=tema["vertice_branco"],
                           outline=tema["contorno_vertice"], width=2, tags=marca)
        if fonte.measure(nome) > 1.7 * raio:
            canvas.create_text(x, y + raio + 2, text=nome, anchor="n", fill=tema["texto"], font=fonte, tags=marca)
        else:
            canvas.create_text(x, y, text=nome, fill=tema["texto_vertice_branco"], font=fonte, tags=marca)
    canvas.move(marca, x0, y0)
    canvas.dtag(marca, marca)
