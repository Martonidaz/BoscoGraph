'''
    O relatório completo em PDF: recebe uma lista de "blocos" (títulos, parágrafos, tabelas, matrizes,
    desenhos, código) e vai colocando um embaixo do outro nas páginas A4, como um editor de texto faz:
    quando um bloco não cabe no resto da página, ele passa para a próxima (as tabelas compridas
    continuam na página seguinte, repetindo o cabeçalho).

    Quem monta os blocos é a tela (visual/conteudo_do_relatorio.py), que sabe o que o grafo e a busca
    têm; este arquivo só sabe ARRUMAR na página. Os blocos são dicionários com "tipo":
        capa       -> titulo, subtitulo, fatos [(rótulo, valor)], figura (opcional)
        secao      -> titulo, cor (r, g, b), descricao (opcional)     (um título grande, com uma faixa colorida)
        subtitulo  -> texto
        paragrafo  -> texto, estilo ("normal", "suave" ou "aviso")
        tabela     -> colunas [títulos], linhas [[células]], alinhamentos (opcional), tons (cor de fundo
                      de cada linha, opcional)
        grade      -> matriz {"linhas", "colunas", "celulas": {(i, j): texto}}, legenda (opcional)
        figura     -> figura (exportacao/figura.py), altura_maxima, legenda (opcional)
        numerada   -> itens [textos]: uma lista 1., 2., 3....
        codigo     -> linhas [textos], com o número de cada linha
        quebra     -> começa uma página nova
    Este arquivo não usa Tkinter.
'''

import caminhos
from exportacao import figura as figuras
from exportacao.pdf import A4, DocumentoPdf, largura_do_texto, quebrar_texto

MARGEM_ESQUERDA = 50
MARGEM_DIREITA = 50
MARGEM_DE_CIMA = 54
MARGEM_DE_BAIXO = 62                # o rodapé fica aqui embaixo

TEXTO = (31, 41, 51)
SUAVE = (100, 110, 122)
BORDA = (208, 214, 222)
FUNDO_DO_CABECALHO = (236, 240, 245)
AVISO = (180, 60, 40)


class Relatorio:
    def __init__(self, titulo):
        self.titulo = titulo
        self.documento = DocumentoPdf(titulo=titulo, autor=caminhos.NOME_DO_PROGRAMA)
        self.largura, self.altura = A4
        self.util = self.largura - MARGEM_ESQUERDA - MARGEM_DIREITA
        self.fim = self.altura - MARGEM_DE_BAIXO
        self.pagina = None
        self.y = 0
        self.nova_pagina()

    # ------------------------------------------------------------------
    # Páginas e espaço
    # ------------------------------------------------------------------

    def nova_pagina(self):
        self.pagina = self.documento.nova_pagina()
        self.y = MARGEM_DE_CIMA

    # Se não couber "altura" no resto da página, vai para a próxima. Devolve True se pulou.
    def garantir(self, altura):
        if self.y + altura > self.fim and self.y > MARGEM_DE_CIMA + 1:
            self.nova_pagina()
            return True
        return False

    def espaco(self, altura):
        self.y += altura

    # ------------------------------------------------------------------
    # Os blocos
    # ------------------------------------------------------------------

    def capa(self, bloco):
        self.pagina.texto(MARGEM_ESQUERDA, self.y, bloco["titulo"], tamanho=22, fonte="Helvetica-Bold", cor=TEXTO)
        self.y += 30
        if bloco.get("subtitulo"):
            self.pagina.texto(MARGEM_ESQUERDA, self.y, bloco["subtitulo"], tamanho=10, cor=SUAVE)
            self.y += 20
        self.pagina.linha([(MARGEM_ESQUERDA, self.y), (MARGEM_ESQUERDA + self.util, self.y)], cor=BORDA, espessura=1)
        self.y += 12
        fatos = bloco.get("fatos", [])
        if fatos:
            largura_do_rotulo = 0
            for rotulo, valor in fatos:
                largura_do_rotulo = max(largura_do_rotulo, largura_do_texto(rotulo, 9.5, "Helvetica-Bold"))
            largura_do_rotulo += 12
            for rotulo, valor in fatos:
                linhas = quebrar_texto(str(valor), self.util - largura_do_rotulo, 9.5)
                self.garantir(len(linhas) * 12.5 + 2)
                self.pagina.texto(MARGEM_ESQUERDA, self.y, rotulo, tamanho=9.5, fonte="Helvetica-Bold", cor=SUAVE)
                for linha in linhas:
                    self.pagina.texto(MARGEM_ESQUERDA + largura_do_rotulo, self.y, linha, tamanho=9.5, cor=TEXTO)
                    self.y += 12.5
                self.y += 2
            self.y += 10
        if bloco.get("figura") is not None:
            self.figura({"figura": bloco["figura"], "altura_maxima": bloco.get("altura_maxima", 380),
                         "legenda": bloco.get("legenda")})

    def secao(self, bloco):
        # Uma seção nunca começa no pé da página: precisa de espaço para o título e um pouco do conteúdo
        self.garantir(90)
        if self.y > MARGEM_DE_CIMA + 1:
            self.y += 8
        cor = bloco.get("cor") or (42, 111, 219)
        self.pagina.retangulo(MARGEM_ESQUERDA, self.y, MARGEM_ESQUERDA + 4, self.y + 20, preenchimento=cor, contorno=None)
        self.pagina.texto(MARGEM_ESQUERDA + 12, self.y + 2, bloco["titulo"], tamanho=15, fonte="Helvetica-Bold", cor=cor)
        self.y += 26
        if bloco.get("descricao"):
            self.paragrafo({"texto": bloco["descricao"], "estilo": "suave"})
        self.y += 4

    def subtitulo(self, bloco):
        self.garantir(60)
        self.y += 6
        self.pagina.texto(MARGEM_ESQUERDA, self.y, bloco["texto"], tamanho=11.5, fonte="Helvetica-Bold", cor=TEXTO)
        self.y += 18

    def paragrafo(self, bloco):
        estilo = bloco.get("estilo", "normal")
        tamanho = 9.5 if estilo == "suave" else 10
        cor = {"suave": SUAVE, "aviso": AVISO}.get(estilo, TEXTO)
        fonte = "Helvetica-Oblique" if estilo == "suave" else "Helvetica"
        entrelinha = tamanho * 1.35
        for linha in quebrar_texto(bloco["texto"], self.util, tamanho, fonte):
            self.garantir(entrelinha)
            self.pagina.texto(MARGEM_ESQUERDA, self.y, linha, tamanho=tamanho, fonte=fonte, cor=cor)
            self.y += entrelinha
        self.y += 6

    def numerada(self, bloco):
        tamanho = 8.5
        entrelinha = tamanho * 1.3
        itens = bloco["itens"]
        inicio = bloco.get("inicio", 1)
        largura_do_numero = largura_do_texto(f"{inicio + len(itens) - 1}.", tamanho, "Helvetica-Bold") + 6
        for posicao in range(len(itens)):
            linhas = quebrar_texto(itens[posicao], self.util - largura_do_numero, tamanho)
            self.garantir(len(linhas) * entrelinha if len(linhas) <= 6 else entrelinha)
            self.pagina.texto(MARGEM_ESQUERDA + largura_do_numero - 4, self.y, f"{inicio + posicao}.", tamanho=tamanho,
                              fonte="Helvetica-Bold", cor=SUAVE, ancora="ne")
            for linha in linhas:
                self.garantir(entrelinha)
                self.pagina.texto(MARGEM_ESQUERDA + largura_do_numero, self.y, linha, tamanho=tamanho, cor=TEXTO)
                self.y += entrelinha
            self.y += 1.5
        self.y += 6

    def figura(self, bloco):
        figura = figuras.recortar(bloco["figura"])
        altura_maxima = bloco.get("altura_maxima", 360)
        legenda = bloco.get("legenda")
        extra = (16 if legenda else 0) + 6
        # Se não couber no resto da página mas sobrar bastante espaço, o desenho encolhe para caber
        # (em vez de pular de página e deixar meia página em branco)
        sobra = self.fim - self.y - extra
        if sobra < altura_maxima and sobra >= 0.6 * altura_maxima:
            altura_maxima = sobra
        escala = min(self.util / figura["largura"], altura_maxima / figura["altura"])
        altura = figura["altura"] * escala
        self.garantir(altura + extra)
        figuras.desenhar_no_pdf(self.pagina, figura, MARGEM_ESQUERDA, self.y, self.util, altura, borda=BORDA)
        self.y += altura + 4
        if legenda:
            self.pagina.texto(MARGEM_ESQUERDA + self.util / 2, self.y, legenda, tamanho=8.5, fonte="Helvetica-Oblique",
                              cor=SUAVE, ancora="n")
            self.y += 14
        self.y += 8

    # Uma tabela com cabeçalho. As colunas têm a largura do conteúdo; se não couber na página, as
    # colunas de texto comprido encolhem e o texto quebra em várias linhas dentro da célula.
    def tabela(self, bloco):
        colunas = bloco["colunas"]
        linhas = bloco["linhas"]
        tamanho = bloco.get("tamanho", 8.5)
        alinhamentos = bloco.get("alinhamentos") or ["esquerda"] * len(colunas)
        tons = bloco.get("tons") or [None] * len(linhas)
        folga = 4                           # o espaço entre o texto e a borda da célula
        entrelinha = tamanho * 1.25
        larguras = self.larguras_das_colunas(colunas, linhas, tamanho, folga)

        def desenhar_cabecalho():
            textos = [quebrar_texto(str(colunas[c]), larguras[c] - 2 * folga, tamanho, "Helvetica-Bold")
                      for c in range(len(colunas))]
            altura = max(len(texto) for texto in textos) * entrelinha + 2 * folga
            self.garantir(altura + entrelinha + 2 * folga)
            self.desenhar_linha_da_tabela(textos, larguras, altura, alinhamentos, tamanho, "Helvetica-Bold",
                                          FUNDO_DO_CABECALHO, folga, entrelinha)

        desenhar_cabecalho()
        for posicao in range(len(linhas)):
            textos = [quebrar_texto(str(linhas[posicao][c]), larguras[c] - 2 * folga, tamanho)
                      for c in range(len(colunas))]
            altura = max(len(texto) for texto in textos) * entrelinha + 2 * folga
            if self.y + altura > self.fim:
                self.nova_pagina()
                desenhar_cabecalho()
            self.desenhar_linha_da_tabela(textos, larguras, altura, alinhamentos, tamanho, "Helvetica", tons[posicao],
                                          folga, entrelinha)
        self.y += 10

    def larguras_das_colunas(self, colunas, linhas, tamanho, folga):
        naturais = []
        for c in range(len(colunas)):
            maior = largura_do_texto(str(colunas[c]), tamanho, "Helvetica-Bold")
            for linha in linhas:
                for pedaco in str(linha[c]).split("\n"):
                    maior = max(maior, largura_do_texto(pedaco, tamanho))
            naturais.append(maior + 2 * folga + 1)
        if sum(naturais) <= self.util:
            return naturais
        # Não cabe: as colunas estreitas ficam como estão; as largas dividem o que sobra
        justa = self.util / len(colunas)
        estreitas = 0
        soma_das_largas = 0
        for largura in naturais:
            if largura <= justa:
                estreitas += largura
            else:
                soma_das_largas += largura
        sobra = self.util - estreitas
        larguras = []
        for largura in naturais:
            if largura <= justa:
                larguras.append(largura)
            else:
                larguras.append(max(36, sobra * largura / soma_das_largas))
        return larguras

    def desenhar_linha_da_tabela(self, textos, larguras, altura, alinhamentos, tamanho, fonte, fundo, folga,
                                 entrelinha):
        x = MARGEM_ESQUERDA
        for c in range(len(textos)):
            self.pagina.retangulo(x, self.y, x + larguras[c], self.y + altura, preenchimento=fundo, contorno=BORDA,
                                  espessura=0.6)
            for indice in range(len(textos[c])):
                topo = self.y + folga + indice * entrelinha
                alinhamento = alinhamentos[c]
                if alinhamento == "centro":
                    self.pagina.texto(x + larguras[c] / 2, topo, textos[c][indice], tamanho=tamanho, fonte=fonte,
                                      cor=TEXTO, ancora="n")
                elif alinhamento == "direita":
                    self.pagina.texto(x + larguras[c] - folga, topo, textos[c][indice], tamanho=tamanho, fonte=fonte,
                                      cor=TEXTO, ancora="ne")
                else:
                    self.pagina.texto(x + folga, topo, textos[c][indice], tamanho=tamanho, fonte=fonte, cor=TEXTO)
            x += larguras[c]
        self.y += altura

    # Uma matriz: os nomes das linhas à esquerda, os das colunas em cima. Se for larga demais para a
    # página, sai em pedaços (colunas 1 a 12, 13 a 24...), cada um com os nomes das linhas.
    def grade(self, bloco):
        matriz = bloco["matriz"]
        nomes_das_linhas = matriz["linhas"]
        nomes_das_colunas = matriz["colunas"]
        celulas = matriz["celulas"]
        tamanho = 8.5 if len(nomes_das_colunas) <= 16 else 7.5
        folga = 3
        altura = tamanho * 1.25 + 2 * folga
        largura_dos_nomes = 0
        for nome in nomes_das_linhas:
            largura_dos_nomes = max(largura_dos_nomes, largura_do_texto(nome, tamanho, "Helvetica-Bold"))
        largura_dos_nomes += 2 * folga + 2
        largura_da_coluna = 18
        for j in range(len(nomes_das_colunas)):
            largura_da_coluna = max(largura_da_coluna, largura_do_texto(nomes_das_colunas[j], tamanho, "Helvetica-Bold"))
            for i in range(len(nomes_das_linhas)):
                largura_da_coluna = max(largura_da_coluna, largura_do_texto(celulas.get((i, j), ""), tamanho))
        largura_da_coluna = min(largura_da_coluna + 2 * folga, 90)
        por_pedaco = max(1, int((self.util - largura_dos_nomes) // largura_da_coluna))
        if bloco.get("legenda"):
            self.paragrafo({"texto": bloco["legenda"], "estilo": "suave"})
        comeco = 0
        while comeco < len(nomes_das_colunas) or comeco == 0:
            fim = min(len(nomes_das_colunas), comeco + por_pedaco)
            if len(nomes_das_colunas) > por_pedaco:
                self.garantir(altura * 3)
                self.pagina.texto(MARGEM_ESQUERDA, self.y, f"colunas {comeco + 1} a {fim} de {len(nomes_das_colunas)}",
                                  tamanho=8, fonte="Helvetica-Oblique", cor=SUAVE)
                self.y += 12
            self.desenhar_pedaco_da_grade(nomes_das_linhas, nomes_das_colunas, celulas, comeco, fim, largura_dos_nomes,
                                          largura_da_coluna, altura, tamanho, folga, bloco.get("destaques") or {})
            self.y += 8
            comeco = fim
            if fim >= len(nomes_das_colunas):
                break
        self.y += 4

    def desenhar_pedaco_da_grade(self, nomes_das_linhas, nomes_das_colunas, celulas, comeco, fim, largura_dos_nomes,
                                 largura_da_coluna, altura, tamanho, folga, destaques):
        def cabecalho():
            self.garantir(altura * 2)
            x = MARGEM_ESQUERDA + largura_dos_nomes
            for j in range(comeco, fim):
                self.pagina.retangulo(x, self.y, x + largura_da_coluna, self.y + altura,
                                      preenchimento=FUNDO_DO_CABECALHO, contorno=BORDA, espessura=0.6)
                self.pagina.texto(x + largura_da_coluna / 2, self.y + folga, nomes_das_colunas[j], tamanho=tamanho,
                                  fonte="Helvetica-Bold", cor=TEXTO, ancora="n")
                x += largura_da_coluna
            self.y += altura

        cabecalho()
        for i in range(len(nomes_das_linhas)):
            if self.y + altura > self.fim:
                self.nova_pagina()
                cabecalho()
            self.pagina.retangulo(MARGEM_ESQUERDA, self.y, MARGEM_ESQUERDA + largura_dos_nomes, self.y + altura,
                                  preenchimento=FUNDO_DO_CABECALHO, contorno=BORDA, espessura=0.6)
            self.pagina.texto(MARGEM_ESQUERDA + folga + 1, self.y + folga, nomes_das_linhas[i], tamanho=tamanho,
                              fonte="Helvetica-Bold", cor=TEXTO)
            x = MARGEM_ESQUERDA + largura_dos_nomes
            for j in range(comeco, fim):
                texto = celulas.get((i, j), "")
                self.pagina.retangulo(x, self.y, x + largura_da_coluna, self.y + altura,
                                      preenchimento=destaques.get((i, j)), contorno=BORDA, espessura=0.6)
                cor = SUAVE if texto in ("0", "") else TEXTO
                # Um texto maior que a célula é encurtado (as células são números: quase nunca acontece)
                while len(texto) > 1 and largura_do_texto(texto, tamanho) > largura_da_coluna - 2:
                    texto = texto[:-2] + "…"
                self.pagina.texto(x + largura_da_coluna / 2, self.y + folga, texto, tamanho=tamanho, cor=cor, ancora="n")
                x += largura_da_coluna
            self.y += altura

    def codigo(self, bloco):
        tamanho = 7.6
        entrelinha = tamanho * 1.3
        linhas = bloco["linhas"]
        largura_do_numero = largura_do_texto(str(len(linhas)), tamanho, "Courier") + 8
        largura_do_texto_do_codigo = self.util - largura_do_numero
        if bloco.get("titulo"):
            self.subtitulo({"texto": bloco["titulo"]})
        # Na Courier toda letra tem a mesma largura (600 milésimos): cabem tantas letras por linha
        por_linha = max(20, int(largura_do_texto_do_codigo // (0.6 * tamanho)))
        for numero in range(len(linhas)):
            # Linha comprida demais: continua embaixo, um pouco para dentro. (Aqui não dá para quebrar
            # nos espaços como num parágrafo: os espaços do começo são a indentação do código.)
            linha = linhas[numero].replace("\t", "    ")
            pedacos = []
            while len(linha) > por_linha:
                pedacos.append(linha[:por_linha])
                linha = linha[por_linha:]
            pedacos.append(linha)
            for indice in range(len(pedacos)):
                self.garantir(entrelinha)
                if indice == 0:
                    self.pagina.texto(MARGEM_ESQUERDA + largura_do_numero - 6, self.y, str(numero + 1), tamanho=tamanho,
                                      fonte="Courier", cor=SUAVE, ancora="ne")
                    texto = pedacos[indice]
                else:
                    texto = "  " + pedacos[indice]
                self.pagina.texto(MARGEM_ESQUERDA + largura_do_numero, self.y, texto, tamanho=tamanho, fonte="Courier",
                                  cor=TEXTO)
                self.y += entrelinha
        self.y += 8

    # ------------------------------------------------------------------
    # O rodapé (no fim, quando já se sabe quantas páginas são)
    # ------------------------------------------------------------------

    def rodapes(self):
        total = len(self.documento.paginas)
        for numero in range(total):
            pagina = self.documento.paginas[numero]
            base = self.altura - MARGEM_DE_BAIXO + 22
            pagina.linha([(MARGEM_ESQUERDA, base - 8), (MARGEM_ESQUERDA + self.util, base - 8)], cor=BORDA,
                         espessura=0.6)
            titulo = self.titulo if len(self.titulo) <= 70 else self.titulo[:69] + "…"
            pagina.texto(MARGEM_ESQUERDA, base, f"{caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO} · {titulo}",
                         tamanho=8, cor=SUAVE)
            pagina.texto(MARGEM_ESQUERDA + self.util, base, f"página {numero + 1} de {total}", tamanho=8, cor=SUAVE,
                         ancora="ne")


# Monta o PDF a partir dos blocos. Devolve o DocumentoPdf (quem chama salva com .salvar(caminho)).
def gerar(conteudo):
    relatorio = Relatorio(conteudo["titulo"])
    for bloco in conteudo["blocos"]:
        tipo = bloco["tipo"]
        if tipo == "quebra":
            if relatorio.y > MARGEM_DE_CIMA + 1:
                relatorio.nova_pagina()
            continue
        getattr(relatorio, tipo)(bloco)
    relatorio.rodapes()
    return relatorio.documento
