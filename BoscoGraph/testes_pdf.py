'''
    Conferências do escritor de PDF (exportacao/pdf.py), sem abrir janela.
    Rode com: python testes_pdf.py   (o testes.py também chama este arquivo)

    Duas partes:
      - 13a a 13d: só com a biblioteca padrão. O arquivo é desmontado de novo aqui (a tabela xref aponta
        para o começo de cada objeto? os conteúdos descomprimem?), as larguras batem com números
        conhecidos das tabelas da Adobe, a quebra de linhas não perde nada e a geração é rápida.
      - 13e a 13h: se o PyMuPDF estiver instalado (pip install pymupdf), um leitor de PDF de verdade abre o
        arquivo e devolve o texto, a posição de cada texto e os desenhos, que conferimos um por um.
        Sem o PyMuPDF, essa parte é pulada (o programa não precisa dele: só o teste usa).
'''

import random
import re
import time
import zlib

from exportacao import pdf


# ----------------------------------------------------------------------
# Funções de apoio
# ----------------------------------------------------------------------

# Desmonta o arquivo: confere o cabeçalho, o fim, a tabela xref e devolve {número: bytes do objeto}
def desmontar(dados):
    assert dados.startswith(b"%PDF-1.4\n")
    assert dados.rstrip().endswith(b"%%EOF")
    procura = re.search(rb"startxref\n(\d+)\n%%EOF", dados)
    assert procura is not None
    inicio_da_tabela = int(procura.group(1))
    assert dados[inicio_da_tabela:inicio_da_tabela + 5] == b"xref\n"
    linhas = dados[inicio_da_tabela:].split(b"\n")
    primeiro, quantidade = linhas[1].split()
    assert primeiro == b"0"
    objetos = {}
    for numero in range(1, int(quantidade)):
        entrada = linhas[2 + numero]
        assert len(entrada) == 19, entrada        # cada linha da xref tem 20 bytes (com o "\n")
        deslocamento = int(entrada[:10])
        if entrada.endswith(b"f "):
            continue
        # O deslocamento tem que cair EXATAMENTE no começo de "N 0 obj"
        cabecalho = f"{numero} 0 obj\n".encode("latin-1")
        assert dados[deslocamento:deslocamento + len(cabecalho)] == cabecalho, (numero, deslocamento)
        fim = dados.index(b"\nendobj\n", deslocamento)
        objetos[numero] = dados[deslocamento + len(cabecalho):fim]
    assert re.search(rb"/Root 1 0 R", dados[inicio_da_tabela:])
    return objetos


# O conteúdo (descomprimido) de cada página, na ordem
def conteudos_das_paginas(objetos):
    lista = re.search(rb"/Kids \[([^\]]*)\]", objetos[2]).group(1).split(b" 0 R")
    conteudos = []
    for item in lista:
        if item.strip() == b"":
            continue
        pagina = objetos[int(item)]
        numero_do_conteudo = int(re.search(rb"/Contents (\d+) 0 R", pagina).group(1))
        objeto = objetos[numero_do_conteudo]
        comprimento = int(re.search(rb"/Length (\d+)", objeto).group(1))
        comeco = objeto.index(b"stream\n") + len(b"stream\n")
        stream = objeto[comeco:comeco + comprimento]
        assert objeto[comeco + comprimento:] == b"\nendstream"
        conteudos.append(zlib.decompress(stream).decode("latin-1"))
    return conteudos


def documento_de_exemplo():
    documento = pdf.DocumentoPdf(titulo="Relatório de teste — π", autor="BoscoGraph")
    for numero in range(3):
        pagina = documento.nova_pagina()
        pagina.texto(50, 50, f"Página {numero + 1}: Ação, coração — π ≤ ∞ → fim", tamanho=12)
        pagina.linha([(50, 100), (300, 100)], cor="#2a6fdb", espessura=2)
        pagina.elipse(100, 200, 160, 240, preenchimento=(255, 200, 0))
    return documento


# Texto com acentos, sorteado
def texto_sorteado(sorteio):
    letras = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 áéíóúâêôãõçÁÉÍÓÚÇàü.,;:-()[]{}/%$#@!?"
    quantidade = sorteio.randint(1, 40)
    texto = ""
    for vez in range(quantidade):
        texto += sorteio.choice(letras)
    return texto


# ----------------------------------------------------------------------
# 13a a 13d: sem bibliotecas de fora
# ----------------------------------------------------------------------

def conferir_estrutura():
    documento = documento_de_exemplo()
    dados = documento.para_bytes()
    objetos = desmontar(dados)
    assert b"/Count 3" in objetos[2]
    assert b"/FlateDecode" in objetos[11]
    conteudos = conteudos_das_paginas(objetos)
    assert len(conteudos) == 3
    for conteudo in conteudos:
        assert conteudo.startswith("0 J 1 j")            # pontas retas e junções redondas, como no Tkinter
        assert " Tj" in conteudo and " c" in conteudo    # um texto e as curvas da elipse
        assert "/F6 " in conteudo                         # a fonte Symbol (para o π, o ≤, o ∞ e a →)
    # Um documento vazio também é um PDF válido (com uma página em branco)
    vazio = desmontar(pdf.DocumentoPdf().para_bytes())
    assert b"/Count 1" in vazio[2]
    print("13a. PDF: estrutura conferida (xref aponta para cada objeto, conteúdos descomprimem, 3 páginas; "
          "documento vazio = 1 página)")


def conferir_textos_e_larguras():
    # Larguras conhecidas das tabelas da Adobe (em milésimos): A = 667, espaço = 278, travessão — = 1000,
    # aspas “ = 333 (500 no negrito), • = 350, … = 1000, € = 556; Courier = 600 em tudo; ∞ = 713 e π = 549
    # (fonte Symbol)
    assert abs(pdf.largura_do_texto("A", 1000) - 667) < 1e-9
    assert abs(pdf.largura_do_texto("A A", 10) - (667 + 278 + 667) / 100) < 1e-9
    assert abs(pdf.largura_do_texto("“—•…€", 1000) - (333 + 1000 + 350 + 1000 + 556)) < 1e-9
    assert abs(pdf.largura_do_texto("“", 1000, "Helvetica-Bold") - 500) < 1e-9
    assert abs(pdf.largura_do_texto("ação", 1000, "Courier") - 2400) < 1e-9
    assert abs(pdf.largura_do_texto("∞π", 1000) - (713 + 549)) < 1e-9

    # A troca de fonte no meio do texto: "a ≤ b" = Helvetica "a ", Symbol "≤", Helvetica " b"
    pedacos = pdf.pedacos_do_texto("a ≤ b", "Helvetica")
    assert [pedaco[0] for pedaco in pedacos] == ["Helvetica", "Symbol", "Helvetica"]
    assert pedacos[1][1] == bytes([0xA3])
    # Os substitutos: "▶ ✓" -> "> v"; um caractere que ninguém tem -> "?"
    assert pdf.pedacos_do_texto("▶ ✓", "Helvetica")[0][1] == b"> v"
    assert pdf.pedacos_do_texto("中", "Helvetica")[0][1] == b"?"
    # Parênteses e barra invertida precisam de barra antes; o resto fora do ASCII vai em octal
    assert pdf.string_do_pdf(b"(a\\b)") == "(\\(a\\\\b\\))"
    assert pdf.string_do_pdf("é".encode("cp1252")) == "(\\351)"

    # As âncoras: a caixa devolvida tem a largura do texto e fica do lado certo do ponto
    pagina = pdf.Pagina(*pdf.A4)
    largura = pdf.largura_do_texto("Teste", 20)
    for ancora in ("nw", "n", "ne", "w", "center", "e", "sw", "s", "se"):
        x0, y0, x1, y1 = pagina.texto(300, 400, "Teste", tamanho=20, ancora=ancora)
        assert abs((x1 - x0) - largura) < 1e-9
        if "w" in ancora:
            assert abs(x0 - 300) < 1e-9
        elif "e" in ancora:
            assert abs(x1 - 300) < 1e-9
        else:
            assert abs((x0 + x1) / 2 - 300) < 1e-9
        if "n" in ancora:
            assert abs(y0 - 400) < 1e-9
        elif "s" in ancora:
            assert abs(y1 - 400) < 1e-9
        else:
            assert abs((y0 + y1) / 2 - 400) < 1e-9
    print("13b. PDF: larguras das letras (Helvetica, negrito, Courier, Symbol), troca de fonte no meio do texto, "
          "substitutos, escape das strings e as 9 âncoras conferidos")


def conferir_quebra_de_linhas(quantidade):
    sorteio = random.Random(13)
    for vez in range(quantidade):
        palavras = []
        for indice in range(sorteio.randint(1, 30)):
            tamanho_da_palavra = sorteio.choice([1, 2, 3, 5, 8, 13, 40])
            palavra = ""
            for letra in range(tamanho_da_palavra):
                palavra += sorteio.choice("abcdeéçãmwMW→")
            palavras.append(palavra)
        texto = " ".join(palavras)
        largura_maxima = sorteio.choice([30, 60, 120, 300])
        tamanho = sorteio.choice([8, 10, 12])
        linhas = pdf.quebrar_texto(texto, largura_maxima, tamanho)
        for linha in linhas:
            # Nenhuma linha passa da largura (a não ser uma letra sozinha, que não tem como partir)
            assert pdf.largura_do_texto(linha, tamanho) <= largura_maxima + 1e-9 or len(linha) == 1, linha
        # Nada se perde: sem os espaços, as linhas juntas são o texto sem os espaços
        assert "".join(linhas).replace(" ", "") == texto.replace(" ", "")
        # Quando não precisou partir palavra, juntar com espaço devolve o texto
        if all(pdf.largura_do_texto(palavra, tamanho) <= largura_maxima for palavra in palavras):
            assert " ".join(linhas) == texto
    # As quebras que já existem são respeitadas (e linha vazia continua vazia)
    assert pdf.quebrar_texto("um\n\ndois", 500, 10) == ["um", "", "dois"]
    print(f"13c. PDF: quebra de linhas conferida em {quantidade} textos sorteados (nada passa da largura, nada se "
          f"perde, respeita as quebras)")


def conferir_rapidez():
    inicio = time.perf_counter()
    documento = pdf.DocumentoPdf(titulo="Rapidez")
    pagina = documento.nova_pagina()
    for numero in range(2000):
        pagina.texto(20 + numero % 50 * 10, 20 + numero // 50 * 18, f"Texto {numero} → π", tamanho=8)
        pagina.linha([(10, numero % 800), (500, (numero * 7) % 800), (580, 30)], suave=numero % 2 == 0,
                     ponta="fim" if numero % 3 == 0 else None)
    dados = documento.para_bytes()
    tempo = time.perf_counter() - inicio
    assert tempo < 2, tempo
    desmontar(dados)
    print(f"13d. PDF: 2000 textos e 2000 linhas em {tempo:.2f} s ({len(dados) // 1024} KB)")


# ----------------------------------------------------------------------
# 13e a 13h: um leitor de PDF de verdade (PyMuPDF), se estiver instalado
# ----------------------------------------------------------------------

def abrir(documento):
    import pymupdf
    return pymupdf.open(stream=documento.para_bytes(), filetype="pdf")


# Os textos de uma página: [(texto, caixa, origem da linha de base), ...]
def textos_da_pagina(pagina):
    textos = []
    for bloco in pagina.get_text("dict")["blocks"]:
        for linha in bloco.get("lines", []):
            texto = ""
            caixa = None
            origem = None
            for trecho in linha["spans"]:
                texto += trecho["text"]
                if caixa is None:
                    caixa = list(trecho["bbox"])
                    origem = trecho["origin"]
                else:
                    caixa[2] = trecho["bbox"][2]
            textos.append((texto, caixa, origem))
    return textos


def conferir_com_o_leitor_documento_e_texto(pymupdf):
    documento = documento_de_exemplo()
    lido = abrir(documento)
    assert lido.page_count == 3
    assert lido.metadata["title"] == "Relatório de teste — π"     # os metadados vão em UTF-16
    assert lido.metadata["producer"] == "BoscoGraph"
    texto = lido[1].get_text()
    assert "Página 2: Ação, coração — π ≤ ∞ → fim" in texto, texto

    # Substitutos e símbolos
    teste = pdf.DocumentoPdf()
    pagina = teste.nova_pagina()
    pagina.texto(40, 40, "▶ ✓ d(v) = ∞, π[v] = —, Σ ≥ 0, ∅")
    texto = abrir(teste)[0].get_text().strip()
    assert texto == "> v d(v) = ∞, π[v] = —, Σ ≥ 0, ∅", texto
    print("13e. PDF aberto pelo PyMuPDF: 3 páginas, metadados, acentos e símbolos (π ≤ ∞ → Σ ≥ ∅) voltam iguais "
          "na extração do texto")


def conferir_com_o_leitor_larguras_e_ancoras(pymupdf):
    # As larguras batem com as do leitor (nas letras do Latin-1, onde o PyMuPDF usa a tabela certa)
    sorteio = random.Random(7)
    nomes = {"Helvetica": "helv", "Helvetica-Bold": "hebo", "Courier": "cour"}
    for vez in range(200):
        texto = texto_sorteado(sorteio)
        for fonte in nomes:
            nosso = pdf.largura_do_texto(texto, 10, fonte)
            # Letra por letra: medindo o texto inteiro, o PyMuPDF 1.28 pula a letra que vem logo depois de
            # um acento (ele anda 2 bytes do UTF-8 em vez de 1 letra) e erra a soma
            dele = 0
            for letra in texto:
                dele += pymupdf.get_text_length(letra, fontname=nomes[fonte], fontsize=10)
            assert abs(nosso - dele) < 0.01, (texto, fonte, nosso, dele)

    # Âncoras: a caixa que o texto() devolve bate com a que o leitor encontra
    documento = pdf.DocumentoPdf()
    pagina = documento.nova_pagina()
    caixas = {}
    ancoras = ("nw", "n", "ne", "w", "center", "e", "sw", "s", "se")
    for indice in range(len(ancoras)):
        ancora = ancoras[indice]
        x = 100 + (indice % 3) * 200           # longe uns dos outros (o leitor junta textos vizinhos)
        y = 150 + (indice // 3) * 150
        caixas[ancora + " Ação π"] = pagina.texto(x, y, ancora + " Ação π", tamanho=14, ancora=ancora)
    lido = abrir(documento)[0]
    encontrados = textos_da_pagina(lido)
    assert len(encontrados) == len(ancoras)
    for texto, caixa, origem in encontrados:
        nossa = caixas[texto]
        assert abs(caixa[0] - nossa[0]) < 1.5 and abs(caixa[2] - nossa[2]) < 1.5, (texto, caixa, nossa)
        # A linha de base: nossa caixa começa no topo das letras (ascendente 718/1000 do tamanho)
        base = nossa[1] + 718 * 14 / 1000
        assert abs(origem[1] - base) < 0.05, (texto, origem, base)
        # E a caixa do leitor fica em volta da linha de base, como a nossa
        assert caixa[1] < base < caixa[3]
    print("13f. PDF: larguras iguais às do PyMuPDF em 200 textos × 3 fontes; as 9 âncoras no lugar certo "
          "(posição horizontal e linha de base)")


def conferir_com_o_leitor_desenhos(pymupdf):
    documento = pdf.DocumentoPdf()
    pagina = documento.nova_pagina()
    pagina.linha([(50, 60), (250, 60)], cor=(255, 0, 0), espessura=3)
    pagina.linha([(50, 100), (250, 100)], cor="#00ff00", tracejado=(5, 4))
    pagina.retangulo(300, 50, 400, 120, preenchimento="#0000ff", contorno=None)
    pagina.elipse(300, 200, 400, 260, contorno=(0, 0, 0), espessura=2)
    pagina.poligono([(50, 300), (150, 300), (100, 380)], preenchimento=(255, 255, 0))
    pagina.linha([(100, 500), (200, 700), (300, 500)], cor=(0, 0, 255), suave=True)
    pagina.linha([(50, 780), (250, 780)], espessura=2, ponta="fim", forma_da_ponta=(8, 10, 3))
    desenhos = abrir(documento)[0].get_drawings()

    # 1. A linha vermelha de espessura 3
    vermelha = [d for d in desenhos if d.get("color") == (1.0, 0.0, 0.0)]
    assert len(vermelha) == 1 and abs(vermelha[0]["width"] - 3) < 1e-6
    assert vermelha[0]["items"][0][0] == "l"
    # 2. O tracejado
    verde = [d for d in desenhos if d.get("color") == (0.0, 1.0, 0.0)]
    assert len(verde) == 1 and verde[0]["dashes"].replace(".0", "").split() == ["[", "5", "4", "]", "0"]
    # 3. O retângulo azul preenchido
    azul = [d for d in desenhos if d.get("fill") == (0.0, 0.0, 1.0)]
    assert len(azul) == 1
    caixa = azul[0]["rect"]
    assert abs(caixa.x0 - 300) < 0.01 and abs(caixa.y0 - 50) < 0.01 and abs(caixa.x1 - 400) < 0.01
    # 4. A elipse: quatro curvas dentro da caixa (a espessura 2 sai um pouco para fora)
    curvas = [d for d in desenhos if len(d["items"]) == 4 and all(item[0] == "c" for item in d["items"])]
    assert len(curvas) == 1
    caixa = curvas[0]["rect"]
    assert abs(caixa.x0 - 300) < 0.5 and abs(caixa.x1 - 400) < 0.5 and abs(caixa.y0 - 200) < 0.5
    # 5. O triângulo amarelo
    amarelo = [d for d in desenhos if d.get("fill") == (1.0, 1.0, 0.0)]
    assert len(amarelo) == 1 and len(amarelo[0]["items"]) == 3
    # 6. A curva suave de 3 pontos é a quadrática P0-(P1)-P2: começa em P0, termina em P2 e, no meio
    #    (t = 0,5), passa por P0/4 + P1/2 + P2/4 = (200, 600)
    suave = [d for d in desenhos if d.get("color") == (0.0, 0.0, 1.0)]
    assert len(suave) == 1 and len(suave[0]["items"]) == 1 and suave[0]["items"][0][0] == "c"
    p0, c1, c2, p3 = suave[0]["items"][0][1:]
    assert abs(p0.x - 100) < 0.01 and abs(p0.y - 500) < 0.01 and abs(p3.x - 300) < 0.01 and abs(p3.y - 500) < 0.01
    meio_x = (p0.x + 3 * c1.x + 3 * c2.x + p3.x) / 8          # a cúbica em t = 0,5
    meio_y = (p0.y + 3 * c1.y + 3 * c2.y + p3.y) / 8
    assert abs(meio_x - 200) < 0.01 and abs(meio_y - 600) < 0.01, (meio_x, meio_y)
    # 7. A seta: um polígono preenchido com a ponta em (250, 780) e a linha terminando ANTES da ponta
    pretas = [d for d in desenhos if d.get("fill") == (0.0, 0.0, 0.0)]
    assert len(pretas) == 1
    pontos_da_ponta = [item[1] for item in pretas[0]["items"]]
    assert any(abs(ponto.x - 250) < 0.01 and abs(ponto.y - 780) < 0.01 for ponto in pontos_da_ponta)
    linha_da_seta = [d for d in desenhos if d.get("color") == (0.0, 0.0, 0.0) and d["items"][0][0] == "l"
                     and abs(d["items"][0][1].y - 780) < 0.01]
    assert len(linha_da_seta) == 1
    fim_da_linha = linha_da_seta[0]["items"][-1][2]
    assert 240 < fim_da_linha.x < 250, fim_da_linha
    print("13g. PDF: desenhos lidos pelo PyMuPDF (cor e espessura, tracejado, retângulo, elipse, polígono, curva "
          "suave igual à do Tkinter e ponta de seta)")


def conferir_com_o_leitor_pixels(pymupdf):
    # Rasteriza a página e confere a cor de alguns pontos (a elipse preenchida e o fundo branco)
    documento = pdf.DocumentoPdf()
    pagina = documento.nova_pagina()
    pagina.elipse(100, 100, 200, 160, preenchimento=(200, 30, 30), contorno=None)
    imagem = abrir(documento)[0].get_pixmap()
    # (com 1 de folga: a cor vai para o PDF com 3 casas, 200/255 = 0,784, e volta como 199,9)
    cor = imagem.pixel(150, 130)[:3]
    assert abs(cor[0] - 200) <= 1 and abs(cor[1] - 30) <= 1 and abs(cor[2] - 30) <= 1, cor
    assert imagem.pixel(102, 102)[:3] == (255, 255, 255)        # o canto da caixa fica fora da elipse
    print("13h. PDF: a página rasterizada tem a cor certa dentro e fora da elipse")


def rodar():
    conferir_estrutura()
    conferir_textos_e_larguras()
    conferir_quebra_de_linhas(400)
    conferir_rapidez()
    try:
        import pymupdf
    except ImportError:
        print("13e a 13h. Pulados: o PyMuPDF não está instalado (só os testes usam; o programa não precisa dele)")
        return
    conferir_com_o_leitor_documento_e_texto(pymupdf)
    conferir_com_o_leitor_larguras_e_ancoras(pymupdf)
    conferir_com_o_leitor_desenhos(pymupdf)
    conferir_com_o_leitor_pixels(pymupdf)


if __name__ == "__main__":
    rodar()
    print("Todos os testes do PDF passaram.")
