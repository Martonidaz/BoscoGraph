'''
    O menu Exportar da visualização (e o "Abrir arquivo .bosco" da tela inicial).

        PNG / SVG  -> o desenho do grafo COMO ESTÁ NA PARTE ABERTA (o passo, as cores, o que foi
                      escolhido), em 1000 × 750 (o PNG sai 1,5 vez maior, para ficar nítido)
        PDF        -> o relatório completo (exportacao/relatorio.py) ou uma página só com o desenho
        .bosco     -> o grafo e a tela do jeito que estão (exportacao/bosco.py)
        código     -> um programa completo na linguagem escolhida, com este grafo dentro
                      (exportacao/codigo_fonte.py)

    Como o desenho vira imagem: o desenho do grafo é feito num Canvas do Tkinter, que não sabe se salvar
    como imagem. Então este arquivo desenha o grafo de novo num Canvas que nem aparece na tela (do
    tamanho da imagem), lê cada item que o Tkinter criou (linhas, círculos, textos), com as cores, as
    espessuras e as posições, e monta uma "figura" (exportacao/figura.py): uma lista de formas que
    o SVG, o PNG e o PDF sabem desenhar. É o único arquivo das exportações que usa o Tkinter.
'''

import datetime
import os
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox

import caminhos
from exportacao import bosco
from exportacao import figura as figuras
from exportacao import pdf
from visual import tema as temas
from visual.grafo_na_tela import DesenhoDoGrafo

TAMANHO_DA_FIGURA = (1000, 750)

TIPOS = {
    "png": ("Imagem PNG", ".png"),
    "svg": ("Imagem SVG (vetorial)", ".svg"),
    "pdf": ("Relatório em PDF", ".pdf"),
    "pdf_desenho": ("PDF com o desenho", ".pdf"),
    "bosco": ("Arquivo do BoscoGraph", bosco.EXTENSAO),
}


# ----------------------------------------------------------------------
# Do Canvas para a figura
# ----------------------------------------------------------------------

# "#1f2937", "white"... -> (r, g, b) de 0 a 255; "" (sem cor) -> None
def cor_do_tk(componente, cor):
    if not cor:
        return None
    vermelho, verde, azul = componente.winfo_rgb(cor)        # o Tk devolve de 0 a 65535
    return (vermelho // 257, verde // 257, azul // 257)


def numeros(texto):
    valores = []
    for parte in str(texto).split():
        try:
            valores.append(float(parte))
        except ValueError:
            return None             # um tracejado escrito com letras ("-.") não é usado no BoscoGraph
    return valores


# As medidas de uma fonte do Tkinter, em pixels: o tamanho da letra, a parte de cima (ascendente) e a
# altura da linha. A fonte pode ser uma descrição ("{Segoe UI} -14 bold") ou o nome de uma fonte (font12).
def medidas_da_fonte(canvas, descricao, guardadas):
    if descricao in guardadas:
        return guardadas[descricao]
    tk_ = canvas.tk
    tamanho = 0
    try:
        partes = tk_.splitlist(descricao)
        if len(partes) == 1:
            tamanho = int(tk_.call("font", "configure", partes[0], "-size"))
        elif len(partes) >= 2 and not str(partes[0]).startswith("-"):
            tamanho = int(partes[1])
    except (tk.TclError, ValueError):
        tamanho = 0
    if tamanho == 0:
        tamanho = int(tk_.call("font", "actual", descricao, "-size"))
    if tamanho < 0:
        pixels = -tamanho                                     # negativo = em pixels
    else:
        pixels = tamanho * canvas.winfo_fpixels("1p")         # positivo = em pontos
    real = dict(zip(*[iter(tk_.splitlist(tk_.call("font", "actual", descricao)))] * 2))
    familia = str(real.get("-family", "")).lower()
    medidas = {
        "pixels": pixels,
        "ascendente": int(tk_.call("font", "metrics", descricao, "-ascent")),
        "entrelinha": int(tk_.call("font", "metrics", descricao, "-linespace")),
        "negrito": str(real.get("-weight")) == "bold",
        "italico": str(real.get("-slant")) == "italic",
        "mono": any(nome in familia for nome in ("courier", "consolas", "mono", "menlo", "cascadia")),
    }
    guardadas[descricao] = medidas
    return medidas


def medir(canvas, descricao, texto):
    return int(canvas.tk.call("font", "measure", descricao, texto))


# Quebra o texto como o Tkinter quebra (width = largura máxima): nos espaços; uma palavra maior que a
# linha é partida nas letras
def quebrar_como_o_tk(canvas, descricao, texto, largura_maxima):
    if largura_maxima <= 0:
        return texto.split("\n")
    linhas = []
    for paragrafo in texto.split("\n"):
        atual = ""
        for palavra in paragrafo.split(" "):
            tentativa = palavra if atual == "" else atual + " " + palavra
            if medir(canvas, descricao, tentativa) <= largura_maxima:
                atual = tentativa
                continue
            if atual != "":
                linhas.append(atual)
            atual = ""
            while medir(canvas, descricao, palavra) > largura_maxima and len(palavra) > 1:
                corte = len(palavra) - 1
                while corte > 1 and medir(canvas, descricao, palavra[:corte]) > largura_maxima:
                    corte -= 1
                linhas.append(palavra[:corte])
                palavra = palavra[corte:]
            atual = palavra
        linhas.append(atual)
    return linhas


# Um texto do Canvas vira uma forma "texto" por linha, cada uma presa pela linha de base
def formas_do_texto(canvas, item, guardadas):
    texto = canvas.itemcget(item, "text")
    if texto.strip() == "":
        return []
    descricao = canvas.itemcget(item, "font")
    medidas = medidas_da_fonte(canvas, descricao, guardadas)
    largura_maxima = float(canvas.itemcget(item, "width") or 0)
    linhas = quebrar_como_o_tk(canvas, descricao, texto, largura_maxima)
    larguras = [medir(canvas, descricao, linha) for linha in linhas]
    largura = max(larguras)
    altura = medidas["entrelinha"] * len(linhas)
    x, y = canvas.coords(item)[:2]
    ancora = canvas.itemcget(item, "anchor")
    # O canto de cima à esquerda do bloco de texto, conforme a âncora (como o Tk faz)
    if "w" in ancora:
        esquerda = x
    elif "e" in ancora:
        esquerda = x - largura
    else:
        esquerda = x - largura / 2
    if ancora.startswith("n"):
        topo = y
    elif ancora.startswith("s"):
        topo = y - altura
    else:
        topo = y - altura / 2
    justificar = canvas.itemcget(item, "justify")
    cor = cor_do_tk(canvas, canvas.itemcget(item, "fill"))
    if cor is None:
        return []
    formas = []
    for posicao in range(len(linhas)):
        if linhas[posicao].strip() == "":
            continue
        # Uma linha só: alinhada pela âncora. Várias: pelo "justify" dentro do bloco.
        if len(linhas) == 1:
            alinhamento = "esquerda" if "w" in ancora else "direita" if "e" in ancora else "centro"
        else:
            alinhamento = {"left": "esquerda", "right": "direita"}.get(justificar, "centro")
        if alinhamento == "esquerda":
            x_da_linha = esquerda
        elif alinhamento == "direita":
            x_da_linha = esquerda + largura
        else:
            x_da_linha = esquerda + largura / 2
        formas.append({"tipo": "texto", "x": x_da_linha,
                       "base": topo + posicao * medidas["entrelinha"] + medidas["ascendente"],
                       "texto": linhas[posicao], "tamanho": medidas["pixels"], "negrito": medidas["negrito"],
                       "italico": medidas["italico"], "mono": medidas["mono"], "cor": cor,
                       "alinhamento": alinhamento})
    return formas


PONTAS = {"none": None, "first": "inicio", "last": "fim", "both": "ambas"}


# Lê todos os itens do Canvas (de baixo para cima) e monta a figura
def figura_do_canvas(canvas, largura, altura):
    formas = []
    guardadas = {}
    for item in canvas.find_all():
        if canvas.itemcget(item, "state") == "hidden":
            continue
        tipo = canvas.type(item)
        coordenadas = canvas.coords(item)
        pontos = [(coordenadas[i], coordenadas[i + 1]) for i in range(0, len(coordenadas) - 1, 2)]
        if tipo == "text":
            formas += formas_do_texto(canvas, item, guardadas)
        elif tipo == "line":
            cor = cor_do_tk(canvas, canvas.itemcget(item, "fill"))
            if cor is None or len(pontos) < 2:
                continue
            suave = canvas.itemcget(item, "smooth") not in ("0", "false", "")
            formas.append({"tipo": "linha", "pontos": pontos, "cor": cor,
                           "espessura": float(canvas.itemcget(item, "width")),
                           "tracejado": numeros(canvas.itemcget(item, "dash")) or None, "suave": suave,
                           "ponta": PONTAS.get(canvas.itemcget(item, "arrow")),
                           "forma_da_ponta": numeros(canvas.itemcget(item, "arrowshape")) or (8, 10, 3)})
        elif tipo in ("oval", "rectangle", "polygon"):
            preenchimento = cor_do_tk(canvas, canvas.itemcget(item, "fill"))
            contorno = cor_do_tk(canvas, canvas.itemcget(item, "outline"))
            espessura = float(canvas.itemcget(item, "width"))
            if espessura <= 0:
                contorno = None
            forma = {"preenchimento": preenchimento, "contorno": contorno, "espessura": espessura,
                     "tracejado": numeros(canvas.itemcget(item, "dash")) or None}
            if tipo == "polygon":
                forma["tipo"] = "poligono"
                forma["pontos"] = pontos
            else:
                forma["tipo"] = "elipse" if tipo == "oval" else "retangulo"
                forma["caixa"] = tuple(coordenadas[:4])
            formas.append(forma)
        # Imagens e janelas (botões dentro do Canvas) não existem no desenho do grafo
    return {"largura": largura, "altura": altura, "fundo": cor_do_tk(canvas, canvas.cget("bg")), "formas": formas}


# O desenho do grafo num estado, com as opções de uma parte, como figura.
# tema: as cores (o PDF usa sempre o tema claro, que combina com o papel branco)
def figura_do_grafo(tela, estado, opcoes, tema=None, tamanho=TAMANHO_DA_FIGURA):
    app = tela.app
    sessao = tela.sessao
    tema = tema or app.tema
    largura, altura = tamanho
    canvas = tk.Canvas(app.raiz, width=largura, height=altura, bg=tema["canvas"], highlightthickness=0)
    try:
        desenho = DesenhoDoGrafo(canvas, app)
        desenho.tema = tema
        desenho.configurar(sessao.vertices, sessao.arestas, sessao.direcionado, sessao.posicoes)
        opcoes = dict(opcoes)
        opcoes["tamanho"] = (largura, altura)
        desenho.desenhar(estado, opcoes)
        return figura_do_canvas(canvas, largura, altura)
    finally:
        canvas.destroy()


# O que está desenhado agora na parte aberta: (estado, opções). Se a parte não tem desenho (ou ainda
# não desenhou), o grafo montado, sem as cores da busca.
def desenho_da_parte(tela):
    parte = tela.parte
    desenho = getattr(parte, "desenho", None) if parte is not None else None
    if desenho is not None and desenho.ultimo is not None and desenho.ultimo[0] is not None:
        return desenho.ultimo
    sessao = tela.sessao
    opcoes = {"arrumacao": tela.app.preferencias.get("arrumacao", "circulo"),
              "nomes": tela.app.preferencias.get("nomes_das_arestas", True),
              "pesos": tela.app.preferencias.get("pesos_das_arestas", True),
              "informacao": sessao.descricao(), "neutro": True,
              "algoritmo": sessao.algoritmo, "destino": sessao.destino_da_busca()}
    # Uma parte da busca sem desenho na tela: o momento da busca em que ela está
    if parte is not None and parte.grupo == "busca" and sessao.pode_buscar():
        try:
            indice = parte.passo_no_desenho()
        except AttributeError:
            indice = None               # a parte não chegou a montar (o linha a linha sem o rastro)
        if indice is not None:
            opcoes["neutro"] = False
            return sessao.estado_no_passo(indice), opcoes
    return sessao.estado_montado(), opcoes


def figura_da_tela(tela, tema=None):
    estado, opcoes = desenho_da_parte(tela)
    return figura_do_grafo(tela, estado, opcoes, tema)


# ----------------------------------------------------------------------
# Nomes de arquivo e diálogos
# ----------------------------------------------------------------------

def nome_sugerido(tela, complemento=""):
    nome = tela.sessao.nome
    if complemento:
        nome += " - " + complemento
    return caminhos.nome_de_arquivo(nome)


def pasta_inicial(app):
    pasta = app.preferencias.get("pasta_de_exportacao")
    if pasta and os.path.isdir(pasta):
        return pasta
    documentos = Path.home() / "Documents"
    if documentos.is_dir():
        return str(documentos)
    return str(Path.home())


def perguntar_onde_salvar(app, titulo, nome, descricao, extensao):
    caminho = filedialog.asksaveasfilename(parent=app.raiz, title=titulo, initialdir=pasta_inicial(app),
                                           initialfile=nome + extensao, defaultextension=extensao,
                                           filetypes=[(descricao, "*" + extensao), ("Todos os arquivos", "*.*")])
    if not caminho:
        return None
    app.preferencias["pasta_de_exportacao"] = str(Path(caminho).parent)
    return caminho


# ----------------------------------------------------------------------
# Exportar
# ----------------------------------------------------------------------

# tipo: "png", "svg", "pdf", "pdf_desenho", "bosco" ou "codigo" (com a linguagem).
# caminho: onde salvar (None = pergunta numa janela). Devolve o caminho salvo (ou None).
def exportar(tela, tipo, linguagem=None, caminho=None):
    app = tela.app
    if tipo == "png" and not figuras.tem_pillow():
        messagebox.showinfo(caminhos.NOME_DO_PROGRAMA,
                            "Para salvar em PNG é preciso a biblioteca Pillow (no terminal: pip install pillow).\n\n"
                            "Sem ela, use \"Imagem do desenho (SVG)\": abre em qualquer navegador e no Word, "
                            "e não perde qualidade ao ampliar.", parent=app.raiz)
        return None
    if caminho is None:
        if tipo == "codigo":
            from exportacao import codigo_fonte
            informacoes = codigo_fonte.informacoes_da_linguagem(linguagem)
            caminho = perguntar_onde_salvar(app, "Exportar o código-fonte",
                                            codigo_fonte.nome_sugerido(tela.sessao.algoritmo, tela.sessao.nome,
                                                                       linguagem),
                                            informacoes["descricao"], informacoes["extensao"])
        else:
            descricao, extensao = TIPOS[tipo]
            complemento = ""
            if tipo in ("png", "svg", "pdf_desenho") and tela.parte is not None:
                complemento = tela.parte.titulo
            elif tipo == "pdf":
                complemento = "relatório"
            caminho = perguntar_onde_salvar(app, "Exportar: " + descricao, nome_sugerido(tela, complemento),
                                            descricao, extensao)
        if caminho is None:
            return None
    app.raiz.configure(cursor="watch")
    app.raiz.update_idletasks()
    try:
        texto = salvar(tela, tipo, linguagem, caminho)
    except Exception as erro:
        traceback.print_exc()
        tela.avisar(f"Não consegui exportar: {erro}", erro=True)
        return None
    finally:
        app.raiz.configure(cursor="")
    tela.avisar(texto)
    return caminho


# Salva de fato e devolve a mensagem para a barra de baixo
def salvar(tela, tipo, linguagem, caminho):
    nome = Path(caminho).name
    if tipo == "svg":
        figuras.salvar_svg(figura_da_tela(tela), caminho)
        return f"Imagem salva: {caminho} (SVG: abre no navegador e no Word, sem perder qualidade ao ampliar)."
    if tipo == "png":
        figuras.salvar_png(figura_da_tela(tela), caminho)
        return f"Imagem salva: {caminho}"
    if tipo == "pdf_desenho":
        documento = pdf_do_desenho(tela)
        documento.salvar(caminho)
        return f"PDF salvo: {caminho}"
    if tipo == "pdf":
        from exportacao import relatorio
        from visual import conteudo_do_relatorio
        documento = relatorio.gerar(conteudo_do_relatorio.montar(tela, figura_do_grafo))
        documento.salvar(caminho)
        return f"Relatório salvo: {caminho} ({len(documento.paginas)} páginas)."
    if tipo == "bosco":
        sessao = tela.sessao
        grafo = sessao.grafo()
        grafo["limite"] = sessao.limite         # o limite fica guardado mesmo se a busca de agora não usa
        bosco.salvar(caminho, grafo, sessao.nome, estado_para_o_arquivo(tela))
        bosco.lembrar_recente(caminho)         # aparece em "Abertos recentemente" na tela do .bosco
        return f"Arquivo salvo: {nome}. Quem tem o BoscoGraph abre e vê exatamente esta tela."
    if tipo == "codigo":
        from exportacao import codigo_fonte
        if not tela.sessao.pode_buscar():
            raise ValueError("a busca não pode rodar neste grafo (" + " ".join(tela.sessao.problemas) + ")")
        texto = codigo_fonte.programa(linguagem, dados_da_sessao(tela.sessao), nome)
        temporario = str(caminho) + ".tmp"
        with open(temporario, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(texto)
        os.replace(temporario, str(caminho))
        return f"Código salvo: {caminho}. {codigo_fonte.como_rodar(linguagem, nome)}"
    raise ValueError(f"tipo de exportação desconhecido: {tipo}")


# O grafo e as opções da busca, como o gerador de código-fonte recebe
def dados_da_sessao(sessao):
    return sessao.dados_do_programa()


# O estado da tela + a aparência (tema, letras, linguagens do código, velocidade)
def estado_para_o_arquivo(tela):
    app = tela.app
    estado = tela.estado_da_tela()
    exibir = dict(estado.get("exibir", {}))
    exibir["tema"] = app.tema["nome"]
    exibir["zoom"] = app.zoom
    for chave in ("linguagem", "comparar", "comparar_1", "comparar_2", "velocidade"):
        if app.preferencias.get(chave) is not None:
            exibir[chave] = app.preferencias[chave]
    estado["exibir"] = exibir
    return estado


# Uma página A4 deitada com o título e o desenho da parte aberta
def pdf_do_desenho(tela):
    sessao = tela.sessao
    documento = pdf.DocumentoPdf(titulo=sessao.nome, autor=caminhos.NOME_DO_PROGRAMA)
    pagina = documento.nova_pagina(pdf.A4[1], pdf.A4[0])
    margem = 36
    pagina.texto(margem, margem, sessao.nome, tamanho=16, fonte="Helvetica-Bold", cor=(31, 41, 51))
    subtitulo = tela.parte.titulo if tela.parte is not None else ""
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pagina.texto(margem, margem + 22, f"{subtitulo} · {caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO} · {agora}",
                 tamanho=9, cor=(100, 110, 120))
    figura = figura_da_tela(tela, temas.CLARO)
    figuras.desenhar_no_pdf(pagina, figura, margem, margem + 44, pagina.largura - 2 * margem,
                            pagina.altura - 2 * margem - 44, borda=(210, 215, 222))
    return documento


# ----------------------------------------------------------------------
# Abrir um .bosco
# ----------------------------------------------------------------------

# A janela do sistema para escolher um .bosco (começa na pasta da última exportação). Devolve o caminho ou None.
def escolher_bosco(app):
    caminho = filedialog.askopenfilename(parent=app.raiz, title="Abrir arquivo do BoscoGraph",
                                         initialdir=pasta_inicial(app),
                                         filetypes=[("Arquivo do BoscoGraph", "*" + bosco.EXTENSAO),
                                                    ("Todos os arquivos", "*.*")])
    if not caminho:
        return None
    app.preferencias["pasta_de_exportacao"] = str(Path(caminho).parent)
    return caminho


# Abre o arquivo direto na visualização, com a tela como foi salva. Devolve True se abriu.
# Se o arquivo tiver um problema, a tela do .bosco aparece com a explicação (e o botão para escolher outro).
def abrir_bosco(app, caminho):
    try:
        grafo, nome, tela = bosco.ler(caminho)
    except ValueError as problema:
        app.mostrar_bosco(caminho, erro=str(problema))
        return False
    bosco.lembrar_recente(caminho)
    from visual.editor import configuracao_da_visualizacao
    configuracao = configuracao_da_visualizacao(grafo, nome, None)
    exibir = tela.get("exibir", {})
    if exibir.get("tema") in ("claro", "escuro") and exibir["tema"] != app.tema["nome"]:
        app.tema = temas.ESCURO if exibir["tema"] == "escuro" else temas.CLARO
        temas.aplicar_estilo(app.raiz, app.tema, app.fontes)
    if exibir.get("zoom") is not None:
        app.mudar_zoom_sem_redesenhar(exibir["zoom"])
    for chave in ("linguagem", "comparar", "comparar_1", "comparar_2", "velocidade"):
        if chave in exibir:
            app.preferencias[chave] = exibir[chave]
    if "arrumacao" in exibir:
        configuracao["arrumacao"] = exibir["arrumacao"]
    app.visualizar(configuracao, tela)
    return True
