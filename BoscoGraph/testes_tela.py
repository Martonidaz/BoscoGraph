'''
    Conferências das telas (tela inicial, editor e a visualização por partes), com a janela escondida.
    Rode com: python testes_tela.py   (o testes.py também chama este arquivo)

    Precisa de uma tela gráfica (no Windows e no macOS sempre há; num Linux sem tela, é pulado).
    A janela fica escondida (withdraw) o tempo todo: nada pisca na frente de quem roda os testes.

    Para cada uma das dez buscas, a partir do "Ver exemplo" da tela inicial:
      12a. todas as partes abrem (as 7 do grafo e as 4 da busca) e respondem ao teclado;
      12b. passo a passo: em todos os passos, o código (pseudocódigo e Java) destaca exatamente as linhas
           do rótulo do passo;
      12c. linha a linha: o programa inteiro roda desde a linha 1 (o cabeçalho, mesmo sendo comentário); em
           todas as posições, o Python destaca a linha que vai rodar e o C as linhas do mesmo rótulo, a
           pilha mostra em cima quem está rodando, o desenho acompanha e a Saída termina igual à saída
           esperada; escolher uma linha leva à primeira, à anterior, à próxima e à última vez que ela roda
           (também clicando na linha de outra linguagem); Pular e Sair andam para a frente;
      12d. comparar: lado a lado, nos dois modos, a mesma linha destacada nas duas linguagens (o linha a
           linha também desde a linha 1);
      12e. mudanças dentro das partes (sortear e tirar pesos, orientação, ordenação) e o Ctrl+Z;
      12f. exportar: SVG, PNG, PDF (desenho e relatório), .bosco e código-fonte, a partir da tela; o .bosco
           reabre na mesma parte, no mesmo momento e com o mesmo menu Exibir;
      12g. o tema escuro recria a tela no mesmo lugar; Editar grafo e Visualizar voltam para a mesma busca;
      12h. a importação em etapas: o erro aparece na própria tela, a leitura em segundo plano (e o Cancelar),
           a conferência tira ou sorteia os pesos, o tema mantém as escolhas, "Visualizar grafo" e
           "Editar grafo" levam o grafo, e o Ctrl+Z do editor volta para o grafo de antes;
      12i. um .bosco com escolhas estragadas abre mesmo assim (as partes começam do zero);
      12j. a tela inicial: a sanfona dos tipos, o cartão que muda com a escolha, as setas e o Enter, a chave
           do tema (sol e lua), o Ctrl + roda do mouse, o Sobre, o "Começar do zero" e todos os ícones;
      12k. a tela do .bosco: os recentes, a prévia, o Abrir, o problema mostrado na tela (sem janela de erro)
           e o "Tirar da lista";
      12l. as correções da versão 7.1: o topo com os botões desenhados, sem o "Ctrl+PgDn troca de parte";
           o "até" só nas buscas com destino; Vértices sem Saem/Chegam/grau médio; Lista sem Quem sai/Quem
           chega; nada de "Como é montado" nem "Numerar"; o duplo clique (na tabela e no desenho) renomeia o
           vértice e a aresta e muda o peso e o h; a barra de edição do Tipo do grafo (vértice, aresta, laço,
           paralela, remover, orientação, Delete e Ctrl+Z) com o tipo mudando junto;
      12m. o editor em etapas (fase 2): uma etapa por tela, a trilha, o Voltar e o Próximo, a Quantidade que já
           cria e tira, os nomes A, B, C ou 1, 2, 3, a aresta editada inteira, o sorteio, a busca em três
           colunas com o que falta, o Salvar que pede o nome, o Tornar padrão, e os cartões da tela inicial.
'''

import os
import tempfile
import time
import tkinter as tk
import traceback
import xml.etree.ElementTree as arvore_xml
from pathlib import Path
from types import SimpleNamespace

import algoritmos
import importacao
from boscograph import montar_passos
from exportacao import bosco
from exportacao import figura as figuras
from visual.codigo import BOSCOGRAPH, texto_da_escolha
from visual.variaveis import nome_da_chamada

PASTA = Path(__file__).resolve().parent


# As linhas destacadas como "atual" numa caixa de código (números das linhas do arquivo).
# O Tk junta duas linhas seguidas destacadas numa faixa só ("47.0" até "49.0" = as linhas 47 e 48).
def linhas_destacadas(visao):
    faixas = visao.texto.tag_ranges("linha_atual")
    linhas = []
    for i in range(0, len(faixas), 2):
        primeira = int(str(faixas[i]).split(".")[0])
        depois_da_ultima = int(str(faixas[i + 1]).split(".")[0])
        for linha in range(primeira, depois_da_ultima):
            linhas.append(linha)
    return linhas


# Em cada caixa de código visível (menos a do BoscoGraph), as linhas destacadas:
#   - no passo a passo: as do rótulo do passo;
#   - no linha a linha: no Python, as linhas do comando que vai rodar (é ele que roda); nas outras
#     linguagens, as linhas com o rótulo desse comando
def conferir_codigo(parte):
    passos_de_linha = parte.sessao.rastro["passos_de_linha"] if parte.modo == "linha" else None
    for visao, chave in parte.painel_codigo.visoes_visiveis():
        if chave in (BOSCOGRAPH, None):
            continue
        programa = parte.codigo_de_estudo(chave)
        esperadas = []
        if parte.modo == "linha":
            if parte.posicao < len(passos_de_linha):
                passo = passos_de_linha[parte.posicao]
                if chave == "python":
                    esperadas = list(passo["linhas"])
                elif passo["rotulo"]:
                    esperadas = list(programa["linhas_do_rotulo"].get(passo["rotulo"], []))
        else:
            atual, anterior = parte.rotulos_do_momento()
            if atual is not None:
                esperadas = list(programa["linhas_do_rotulo"].get(atual, []))
        assert linhas_destacadas(visao) == esperadas, (parte.algoritmo, chave, parte.posicao, linhas_destacadas(visao),
                                                       esperadas)


def escolher_linguagens(painel, primeira, segunda):
    painel.linguagem.set(texto_da_escolha(primeira))
    painel.comparar.set(texto_da_escolha(segunda))
    painel.ao_escolher()


def abrir_exemplo(app, chave):
    app.mostrar_inicio()
    app.tela.escolher(chave)
    app.tela.ver_exemplo(chave)
    tela = app.tela
    assert tela.sessao.algoritmo == chave and tela.sessao.pode_buscar(), (chave, tela.sessao.problemas)
    return tela


# ----------------------------------------------------------------------
# Uma busca inteira
# ----------------------------------------------------------------------

def conferir_busca(app, chave, pasta, contagem):
    from visual.visualizacao import PARTES
    tela = abrir_exemplo(app, chave)
    sessao = tela.sessao

    # 12a. Todas as partes abrem, mostram e respondem às teclas
    for classe in PARTES:
        tela.escolher_parte(classe.chave)
        tela.mostrar_parte()
        for tecla in ("direita", "direita", "fim", "esquerda", "inicio"):
            tela.tecla(tecla)
    contagem["partes"] += len(PARTES)

    # 12b. Passo a passo, com o código em pseudocódigo e Java
    tela.escolher_parte("passo")
    parte = tela.parte
    # O passo a passo começa com o grafo vazio e monta um vértice por vez; Page Down pula de etapa em etapa
    assert parte.posicao == -1 and not sessao.estado_no_passo(-1).vertices_criados, chave
    assert sessao.passos[0]["tipo"] == "criar_vertice" and set(parte.botoes_da_etapa) == {1, 2, 3, 4, 5, 6}, chave
    tela.tecla("proxima_etapa")
    assert parte.posicao == sessao.primeiro_da_etapa[1] == 0, chave
    parte.ir_para_etapa(5)
    tela.tecla("proxima_etapa")
    assert parte.posicao == sessao.primeiro_da_etapa[6], chave
    parte.escolhas["mostrar"]["codigo"] = True
    parte.escolhas["mostrar"]["tabela"] = True
    parte.escolhas["mostrar"]["log"] = True
    parte.mostrar_paineis()
    escolher_linguagens(parte.painel_codigo, "pseudocodigo", "java")
    for posicao in range(parte.primeira, parte.ultima + 1):
        parte.ir_para(posicao)
        conferir_codigo(parte)
    contagem["passos"] += parte.ultima - parte.primeira

    # 12c. Linha a linha, com Python e C: o programa inteiro, desde a linha 1
    tela.escolher_parte("linha")
    parte = tela.parte
    escolher_linguagens(parte.painel_codigo, "python", "c")
    linhas = sessao.rastro["passos_de_linha"]
    python = parte.codigo_de_estudo("python")
    linguagem_c = parte.codigo_de_estudo("c")
    # O começo: o cabeçalho, linha por linha (comentários também são passos); no C, a mesma linha do cabeçalho
    for posicao in range(5):
        assert linhas[posicao]["linha"] == posicao + 1 and linhas[posicao]["tipo"] == "comentario", chave
        assert linguagem_c["linhas_do_rotulo"][linhas[posicao]["rotulo"]] == [posicao + 1], chave
    for posicao in range(parte.total + 1):
        parte.ir_para(posicao)
        conferir_codigo(parte)
        arvore = parte.painel_variaveis.arvore_da_pilha
        primeira = arvore.get_children()[0]
        if posicao < len(linhas):
            assert arvore.item(primeira, "text") == nome_da_chamada(linhas[posicao]["antes"]["pilha"][0]), chave
            assert python["linhas"][linhas[posicao]["linha"] - 1].strip() in parte.rotulo_mensagem.cget("text") or \
                linhas[posicao]["tipo"] == "branco", chave
        assert parte.passo_no_desenho() == sessao.passo_da_linha[posicao], chave
    contagem["linhas"] += parte.total
    # No fim, a Saída mostra tudo o que o programa escreveu: igual à saída esperada (a do fim do arquivo)
    saida = parte.texto_da_saida.get("1.0", "end").rstrip("\n")
    assert saida.split("\n") == python["saida"], (chave, saida, python["saida"])
    # Logo depois do primeiro print, a Saída tem a primeira linha, em destaque (é o que acabou de sair)
    primeira = min(posicao for posicao in range(len(linhas)) if linhas[posicao]["saida"] > 0)
    parte.ir_para(primeira)
    escrito = sessao.rastro["saida"][:linhas[primeira]["saida"]]
    assert parte.texto_da_saida.get("1.0", "end-1c") == escrito, (chave, escrito)
    faixa = parte.texto_da_saida.tag_ranges("nova")
    assert faixa and parte.texto_da_saida.get(faixa[0], faixa[1]) == escrito, chave
    # Escolher a linha do meio: as vezes em que ela roda
    numero = linhas[len(linhas) // 2]["linha"]
    rotulo = linhas[len(linhas) // 2]["rotulo"]
    esperadas = [posicao for posicao in range(len(linhas)) if numero in linhas[posicao]["linhas"]]
    parte.ir_para(0)
    parte.clicou_na_linha("python", numero)
    escolhida, posicoes = parte.vezes_da_escolhida()
    assert posicoes == esperadas, (chave, numero)
    parte.ir_para_vez("proxima")
    assert parte.posicao == posicoes[0] or (posicoes[0] == 0 and parte.posicao == posicoes[min(1, len(posicoes) - 1)])
    parte.ir_para_vez("primeira")
    assert parte.posicao == posicoes[0]
    parte.ir_para_vez("ultima")
    assert parte.posicao == posicoes[-1]
    if len(posicoes) > 1:
        parte.ir_para_vez("anterior")
        assert parte.posicao == posicoes[-2]
        parte.ir_para_vez("proxima")
        assert parte.posicao == posicoes[-1]
    # A mesma escolha pela linha do C (o mesmo rótulo): as vezes são as das linhas Python dos rótulos dela
    linhas_do_c = linguagem_c["linhas_do_rotulo"].get(rotulo, [])
    if linhas_do_c:
        parte.clicou_na_linha("c", linhas_do_c[0])
        do_python = set()
        for rotulo_do_c in linguagem_c["rotulos_da_linha"][linhas_do_c[0]]:
            do_python.update(python["linhas_do_rotulo"].get(rotulo_do_c, []))
        esperadas = [posicao for posicao in range(len(linhas)) if do_python & set(linhas[posicao]["linhas"])]
        assert parte.vezes_da_escolhida()[1] == esperadas, (chave, rotulo)
    parte.esquecer_linha()
    # Pular a chamada sempre anda; Sair da função também
    parte.ir_para(0)
    while parte.posicao < parte.total:
        antes = parte.posicao
        parte.pular_chamada()
        assert parte.posicao > antes, chave
    parte.ir_para(parte.total // 2)
    antes = parte.posicao
    parte.sair_da_funcao()
    assert parte.posicao > antes or antes == parte.total, chave

    # 12d. Comparar: lado a lado, nos dois modos
    tela.escolher_parte("comparar")
    parte = tela.parte
    escolher_linguagens(parte.painel_codigo, "java", "javascript")
    for modo in ("passo", "linha"):
        parte.variavel_do_modo.set(modo)
        parte.mudar_modo()
        assert parte.modo == modo
        if modo == "linha":
            # O linha a linha começa na linha 1 (o cabeçalho): as duas linguagens destacam a linha 1 delas
            parte.ir_para(0)
            for visao, linguagem in parte.painel_codigo.visoes_visiveis():
                assert linhas_destacadas(visao) == [1], (chave, linguagem, linhas_destacadas(visao))
        ultima = sessao.total_de_linhas if modo == "linha" else len(sessao.passos) - 1
        for posicao in range(0, ultima + 1, max(1, ultima // 25)):
            parte.ir_para(posicao)
            conferir_codigo(parte)
            assert len(parte.painel_codigo.visoes_visiveis()) == 2

    # 12f. Exportar a partir da tela (no meio do passo a passo) e reabrir o .bosco
    tela.escolher_parte("passo")
    parte = tela.parte
    meio = (parte.primeira + parte.ultima) // 2
    parte.ir_para(meio)
    conferir_exportacoes(app, tela, chave, pasta, contagem)
    caminho = os.path.join(pasta, chave + ".bosco")
    tela.mostrar_pesos.set(False)
    tela.mudar_rotulos()
    from visual import exportar
    assert exportar.exportar(tela, "bosco", caminho=caminho) == caminho
    tela.mostrar_pesos.set(True)
    tela.mudar_rotulos()
    app.mostrar_inicio()
    assert exportar.abrir_bosco(app, caminho)
    tela = app.tela
    assert tela.chave_da_parte == "passo" and tela.parte.posicao == meio, (chave, tela.chave_da_parte)
    assert tela.sessao.algoritmo == chave and not tela.mostrar_pesos.get(), chave
    tela.mostrar_pesos.set(True)
    tela.mudar_rotulos()

    # 12g. O tema escuro recria a tela no mesmo lugar
    app.definir_tema("escuro")
    assert app.tela.chave_da_parte == "passo" and app.tela.parte.posicao == meio, chave
    app.definir_tema("claro")
    assert app.tela.parte.posicao == meio, chave
    # Editar grafo -> editor com o grafo -> Visualizar: a mesma busca, no mesmo grafo
    vertices = list(app.tela.sessao.vertices)
    app.tela.editar_grafo()
    editor = app.tela
    assert editor.busca_escolhida()["chave"] == chave and editor.vertices == vertices, chave
    editor.visualizar()
    assert app.tela.sessao.algoritmo == chave and app.tela.sessao.vertices == vertices, chave


# Todas as exportações da tela de agora: os arquivos existem e fazem sentido
def conferir_exportacoes(app, tela, chave, pasta, contagem):
    from visual import exportar
    figura = exportar.figura_da_tela(tela)
    # A figura tem as formas do desenho: um círculo por vértice (pelo menos) e uma linha por aresta visível
    elipses = [forma for forma in figura["formas"] if forma["tipo"] == "elipse"]
    linhas = [forma for forma in figura["formas"] if forma["tipo"] == "linha"]
    assert len(elipses) >= len(tela.sessao.vertices), chave
    assert len(linhas) <= len(tela.sessao.arestas), chave
    textos = [forma["texto"] for forma in figura["formas"] if forma["tipo"] == "texto"]
    for vertice in tela.sessao.vertices:
        assert vertice in textos, (chave, vertice)

    caminho = os.path.join(pasta, chave + ".svg")
    assert exportar.exportar(tela, "svg", caminho=caminho) == caminho
    raiz = arvore_xml.parse(caminho).getroot()            # o SVG é um XML válido
    assert raiz.tag.endswith("svg")
    if figuras.tem_pillow():
        from PIL import Image
        caminho = os.path.join(pasta, chave + ".png")
        assert exportar.exportar(tela, "png", caminho=caminho) == caminho
        with Image.open(caminho) as imagem:
            assert imagem.size == (1500, 1125), imagem.size
    for tipo in ("pdf", "pdf_desenho"):
        caminho = os.path.join(pasta, f"{chave}_{tipo}.pdf")
        assert exportar.exportar(tela, tipo, caminho=caminho) == caminho
        dados = Path(caminho).read_bytes()
        assert dados.startswith(b"%PDF-1.4") and dados.rstrip().endswith(b"%%EOF")
        contagem["pdfs"] += 1
        if tipo == "pdf":
            try:
                import pymupdf
            except ImportError:
                continue
            documento = pymupdf.open(caminho)
            texto = ""
            for pagina in documento:
                texto += pagina.get_text()
            assert tela.sessao.nome in texto and "Código de estudo" in texto, chave
            assert algoritmos.algoritmo(chave)["nome"] in texto, chave
            contagem["paginas"] += documento.page_count
    for linguagem in ("python", "pseudocodigo"):
        caminho = os.path.join(pasta, f"{chave}_{linguagem}.txt")
        assert exportar.exportar(tela, "codigo", linguagem, caminho=caminho) == caminho
        assert "Saída esperada" in Path(caminho).read_text(encoding="utf-8") or linguagem == "pseudocodigo"


# ----------------------------------------------------------------------
# Mudanças dentro das partes e o Ctrl+Z
# ----------------------------------------------------------------------

def conferir_mudancas(app):
    tela = abrir_exemplo(app, algoritmos.DIJKSTRA)
    sessao = tela.sessao
    original = list(sessao.arestas)
    tela.escolher_parte("pesos")
    tela.parte.tirar_todos()
    assert all(peso is None for origem, destino, nome, peso in tela.sessao.arestas)
    assert not tela.sessao.pode_buscar()            # o Dijkstra precisa de pesos: a busca mostra o problema
    tela.escolher_parte("passo")                    # a tela do problema, com o atalho "Ir para Pesos"
    tela.escolher_parte("pesos")
    tela.parte.sortear_rapido()
    for origem, destino, nome, peso in tela.sessao.arestas:
        assert peso is not None and 1 <= peso <= 9
    assert tela.sessao.pode_buscar()
    tela.desfazer()
    tela.desfazer()
    assert tela.sessao.arestas == original
    # Orientação e ordenação
    direcionado = tela.sessao.direcionado
    tela.escolher_parte("arestas")
    tela.parte.orientacao.set(not direcionado)          # como o clique no botão "Não orientado"
    tela.parte.mudar_orientacao()
    assert tela.sessao.direcionado != direcionado
    tela.escolher_parte("lista")
    ordenar = tela.sessao.ordenar
    tela.parte.ordenar.set(not ordenar)
    tela.parte.mudar_ordenacao()
    assert tela.sessao.ordenar != ordenar
    tela.desfazer()
    tela.desfazer()
    assert tela.sessao.direcionado == direcionado and tela.sessao.ordenar == ordenar
    # A busca escolhida na barra da esquerda: trocar recalcula, o Ctrl+Z volta
    tela.variavel_da_busca.set(algoritmos.algoritmo(algoritmos.BELLMAN_FORD)["nome"])
    tela.mudar_busca()
    assert tela.sessao.algoritmo == algoritmos.BELLMAN_FORD
    tela.desfazer()
    assert tela.sessao.algoritmo == algoritmos.DIJKSTRA
    print("12e. Mudanças dentro das partes: tirar e sortear pesos, orientação, ordenação e a busca, com o Ctrl+Z "
          "desfazendo cada uma")


# ----------------------------------------------------------------------
# Importação (a conferência) e um .bosco estragado
# ----------------------------------------------------------------------

def esperar(app, condicao, limite=10.0):
    fim = time.time() + limite
    while not condicao():
        assert time.time() < fim, "a tela não chegou no estado esperado a tempo"
        app.raiz.update()
        time.sleep(0.02)


def conferir_importacao(app, pasta):
    exemplo = PASTA / "exemplos_importacao" / "estradas.csv"
    if not exemplo.exists():
        candidatos = sorted((PASTA / "exemplos_importacao").glob("*.csv"))
        exemplo = candidatos[0]
    importado = importacao.importar_arquivo(str(exemplo))
    # O editor com um grafo conhecido: a importação não pode perder esse grafo (ele fica no Ctrl+Z)
    app.mostrar_editor()
    vertices_antes = list(app.tela.vertices)
    app.mostrar_inicio()                    # fechar o editor guarda como ele estava
    app.tela.importar()
    tela = app.tela
    assert type(tela).__name__ == "TelaDeImportacao" and tela.etapa == 1
    # Um arquivo que não é um grafo: a explicação aparece na própria tela, na etapa 1
    tela.ler_arquivo(str(PASTA / "caminhos.py"), em_segundo_plano=False)
    assert tela.etapa == 1 and "Não sei importar" in tela.erro, tela.erro
    # A leitura em segundo plano, como no programa: "Lendo…" e, quando termina, a conferência
    tela.ler_arquivo(str(exemplo))
    assert tela.lendo and tela.etapa == 1
    esperar(app, lambda: not tela.lendo)
    assert tela.etapa == 2 and tela.painel is not None
    # Cancelar uma leitura: o resultado que chega depois é ignorado
    tela.voltar_para_a_escolha()
    tela.ler_arquivo(str(exemplo))
    tela.cancelar_leitura()
    fim = time.time() + 0.4
    while time.time() < fim:
        app.raiz.update()
        time.sleep(0.02)
    assert tela.etapa == 1 and not tela.lendo and tela.painel is None
    # A coleta de lixo do Python volta a funcionar quando as leituras terminam (ela fica desligada durante)
    import gc
    esperar(app, gc.isenabled)

    # A conferência: tirar e sortear os pesos, trocar a orientação
    tela.ler_arquivo(str(exemplo), em_segundo_plano=False)
    painel = tela.painel
    painel.pesos.set("tirar")
    painel.mudar_pesos()
    assert all(peso is None for origem, destino, nome, peso in painel.grafo_escolhido()["arestas"])
    painel.pesos.set("sortear")
    painel.mudar_pesos()
    grafo = painel.grafo_escolhido()
    assert all(peso is not None and 1 <= peso <= 9 for origem, destino, nome, peso in grafo["arestas"])
    painel.direcionado.set(not painel.direcionado.get())
    painel.atualizar()
    assert len(painel.grafo_escolhido()["arestas"]) == len(painel.pesos_sorteados)
    # Os segmentos respondem às setas do teclado (Pesos: de "Sortear" para "Tirar")
    painel.escolha_pesos.andar(-1)
    assert painel.pesos.get() == "tirar"
    painel.escolha_pesos.andar(1)
    assert painel.pesos.get() == "sortear"
    # O tema escuro recria a tela na mesma etapa, com as mesmas escolhas (e os mesmos pesos sorteados)
    escolhas = painel.escolhas()
    arestas = painel.grafo_escolhido()["arestas"]
    app.definir_tema("escuro")
    tela = app.tela
    assert tela.etapa == 2 and tela.painel.escolhas() == escolhas
    assert tela.painel.grafo_escolhido()["arestas"] == arestas
    app.definir_tema("claro")
    tela = app.tela
    # Visualizar grafo: direto na visualização, com a busca escolhida embaixo
    tela.variavel_da_busca.set(algoritmos.algoritmo(algoritmos.DIJKSTRA)["nome"])
    tela.atualizar_status()
    tela.visualizar()
    visualizacao = app.tela
    assert type(visualizacao).__name__ == "TelaDaVisualizacao"
    assert visualizacao.sessao.algoritmo == algoritmos.DIJKSTRA
    assert len(visualizacao.sessao.vertices) == len(importado["vertices"])
    # Editar grafo (da visualização): o editor tem o grafo importado; o Ctrl+Z volta para o de antes
    vertices_importados = list(visualizacao.sessao.vertices)
    visualizacao.editar_grafo()
    editor = app.tela
    assert editor.vertices == vertices_importados, editor.vertices
    editor.desfazer()
    assert editor.vertices == vertices_antes, editor.vertices
    # Editar grafo (da importação): vai para o editor com o grafo importado
    app.mostrar_importacao()
    app.tela.ler_arquivo(str(exemplo), em_segundo_plano=False)
    app.tela.editar()
    assert type(app.tela).__name__ == "EditorDoGrafo" and len(app.tela.vertices) == len(importado["vertices"])
    # "◀ Início" volta para a tela inicial
    app.mostrar_importacao()
    app.tela.voltar_ao_inicio()
    assert type(app.tela).__name__ == "TelaInicial"
    print(f"12h. Importação em etapas ({exemplo.name}): erro na própria tela, leitura em segundo plano e Cancelar, "
          f"pesos tirados e sorteados, tema sem perder as escolhas, Visualizar e Editar grafo, e o Ctrl+Z volta "
          f"para o grafo de antes")

    tela = abrir_exemplo(app, algoritmos.DIJKSTRA)
    # 12i. Um .bosco com escolhas estragadas (feitas à mão): abre, e as partes começam do zero
    from visual import exportar
    tela.escolher_parte("vertices")
    caminho = os.path.join(pasta, "estragado.bosco")
    exportar.exportar(tela, "bosco", caminho=caminho)
    dados = Path(caminho).read_text(encoding="utf-8")
    import json
    conteudo = json.loads(dados)
    conteudo["tela"]["parte"] = "adjacencia"
    conteudo["tela"]["partes"] = {"adjacencia": {"celula": [999, 999], "modo": "inexistente", "preenchidas": 10 ** 6,
                                                 "preenchendo": True},
                                  "passo": {"posicao": 10 ** 6, "mostrar": {"codigo": "sim"}},
                                  "linha": {"linha": -1, "escolhida": ["klingon", 7]},
                                  "vertices": {"vertice": "não existe"}, "pesos": {"arestas": [10 ** 6]},
                                  "tipo": {"passo": "abc"}, "resultado": {"passo": "999999"}}
    conteudo["tela"]["exibir"] = {"tema": "roxo", "zoom": "grande", "arrumacao": "espiral", "pesos": 3}
    Path(caminho).write_text(json.dumps(conteudo), encoding="utf-8")
    # O que a tela descartou não pode ter virado erro (nem mesmo um erro recuperado, que sai no stderr)
    import contextlib
    import io
    saida_de_erros = io.StringIO()
    with contextlib.redirect_stderr(saida_de_erros):
        assert exportar.abrir_bosco(app, caminho)
        from visual.visualizacao import PARTES
        for classe in PARTES:
            app.tela.escolher_parte(classe.chave)
            app.tela.mostrar_parte()
    assert saida_de_erros.getvalue() == "", saida_de_erros.getvalue()
    assert app.tela.app.tema["nome"] == "claro" and app.tela.app.zoom == 1.0
    print("12i. Um .bosco com escolhas estragadas abre mesmo assim (as partes descartam o que não serve)")


# Todos os textos que aparecem dentro de um componente (rótulos e os textos desenhados nos Canvas)
def textos_da_tela(componente):
    textos = []
    if isinstance(componente, tk.Canvas):
        for item in componente.find_all():
            if componente.type(item) == "text":
                textos.append(componente.itemcget(item, "text"))
    else:
        try:
            texto = componente.cget("text")
            if texto:
                textos.append(str(texto))
        except tk.TclError:
            pass
    for filho in componente.winfo_children():
        textos += textos_da_tela(filho)
    return textos


# ----------------------------------------------------------------------
# 12j. A tela inicial, o Sobre, o tema, o zoom e os componentes desenhados
# ----------------------------------------------------------------------

def conferir_tela_inicial(app):
    import caminhos
    from visual import botoes
    from visual.sobre import mostrar_sobre

    # Primeira vez (nada escolhido): as boas-vindas, com os tipos fechados
    for chave in ("busca_da_tela_inicial", "grupo_da_tela_inicial"):
        app.preferencias.pop(chave, None)
    app.mostrar_inicio()
    tela = app.tela
    assert tela.estado_do_cartao == "boas_vindas" and tela.grupo_aberto is None
    for grupo in tela.grupos:
        assert not grupo["aberto"] and not grupo["janela"].winfo_manager()
    # Clicar num tipo abre a lista dele (e o cartão explica o tipo); outro tipo fecha o primeiro; de novo, fecha
    tela.clicar_no_grupo(1)
    assert tela.grupo_aberto == 1 and tela.grupos[1]["aberto"] and tela.estado_do_cartao == ("tipo", 1)
    tela.clicar_no_grupo(2)
    assert tela.grupo_aberto == 2 and not tela.grupos[1]["aberto"] and tela.estado_do_cartao == ("tipo", 2)
    tela.clicar_no_grupo(2)
    assert tela.grupo_aberto is None and tela.estado_do_cartao == "boas_vindas"
    # A animação da sanfona (a janela fica escondida nos testes: aqui ela "finge" que está na tela)
    tela.quadro.winfo_ismapped = lambda: True
    tela.clicar_no_grupo(0)
    assert tela.animacao is not None
    esperar(app, lambda: tela.animacao is None)
    assert tela.grupos[0]["aberto"] and tela.grupos[0]["janela"].winfo_manager() == "pack"
    tela.clicar_no_grupo(0)
    esperar(app, lambda: tela.animacao is None)
    assert not tela.grupos[0]["aberto"] and not tela.grupos[0]["janela"].winfo_manager()

    # Escolher uma busca abre o tipo dela e mostra o cartão dela; as setas andam dentro do tipo
    tela.escolher(algoritmos.A_ESTRELA)
    assert tela.grupo_aberto == 2 and tela.estado_do_cartao == ("busca", algoritmos.A_ESTRELA)
    tela.andar(-1)
    assert tela.escolhida == algoritmos.GULOSA
    tela.andar(-1)                                  # já é a primeira do tipo: fica
    assert tela.escolhida == algoritmos.GULOSA
    tela.andar(1)
    tela.andar(1)
    assert tela.escolhida == algoritmos.A_ESTRELA
    # O cartão não tem mais o "Exemplo: ..." (o exemplo está na dica do botão Ver exemplo)
    for texto in textos_da_tela(tela.cartao):
        assert not texto.startswith("Exemplo:"), texto
    # Enter abre o exemplo da busca escolhida; voltar ao início encontra a mesma busca escolhida
    tela.enter()
    assert type(app.tela).__name__ == "TelaDaVisualizacao" and app.tela.sessao.algoritmo == algoritmos.A_ESTRELA
    app.mostrar_inicio()
    tela = app.tela
    assert tela.escolhida == algoritmos.A_ESTRELA and tela.estado_do_cartao == ("busca", algoritmos.A_ESTRELA)

    # A chave do tema: a bolinha desliza até a lua e o tema escurece (a tela volta igual)
    tela.cabecalho.chave_do_tema.alternar()
    esperar(app, lambda: app.tema["nome"] == "escuro")
    assert app.tela.estado_do_cartao == ("busca", algoritmos.A_ESTRELA)
    assert app.tela.cabecalho.chave_do_tema.posicao == 1.0
    app.tela.cabecalho.chave_do_tema.alternar()
    esperar(app, lambda: app.tema["nome"] == "claro")

    # Ctrl + roda do mouse: as caixas que rolam também recebem a ligação (para não rolarem junto)
    for classe in ("Text", "Treeview", "Canvas", "Listbox"):
        assert app.raiz.bind_class(classe, "<Control-MouseWheel>"), classe
        assert app.raiz.bind_class(classe, "<Control-Button-4>"), classe
    app.roda_com_ctrl(SimpleNamespace(num="??", delta=120))        # Windows: um dente para cima
    esperar(app, lambda: app.zoom == 1.1)
    assert app.aviso_de_zoom is not None and app.aviso_de_zoom.place_info()
    assert "110%" in app.aviso_de_zoom.cget("text")
    app.roda_com_ctrl(SimpleNamespace(num=5, delta=0))             # Linux: o botão 5 é para baixo
    app.roda_com_ctrl(SimpleNamespace(num=5, delta=0))
    esperar(app, lambda: app.zoom == 0.9)
    app.roda_com_ctrl(SimpleNamespace(num="??", delta=90))         # touchpad: 3/4 de dente não muda nada
    fim = time.time() + 0.15
    while time.time() < fim:
        app.raiz.update()
    assert app.zoom == 0.9
    app.roda_com_ctrl(SimpleNamespace(num="??", delta=30))         # o resto completa o dente
    esperar(app, lambda: app.zoom == 1.0)
    for vez in range(20):                                           # nunca passa de 200%
        app.roda_com_ctrl(SimpleNamespace(num=4, delta=0))
    esperar(app, lambda: app.zoom == 2.0)
    app.zoom_normal()
    assert app.zoom == 1.0

    # O Sobre: a versão, a data e todos os nomes
    mostrar_sobre(app)
    dialogo = app.dialogo
    assert type(dialogo).__name__ == "DialogoSobre"
    textos = " | ".join(textos_da_tela(dialogo.janela))
    for nome in ("Daniel Marton Barbosa", "Breno Ryan de Andrade Fernandes", "João Vitor Ferreira Azevedo Pereira",
                 "Mariana Gonçalves de Freitas Ribeiro", "Bruno Bustamante Ferreira Leonor", "Warner Brezolin"):
        assert nome in textos, nome
    # Os títulos dos grupos (o Daniel pediu "Co-criadores", não "Colegas")
    for titulo in ("Criado por", "Co-criadores", "Professores", "Disciplina"):
        assert titulo in textos, titulo
    assert "Colegas" not in textos, textos
    assert f"Versão {caminhos.VERSAO}" in textos and "29/09/2026" in textos, textos
    dialogo.fechar()
    assert app.dialogo is None

    # Os outros jeitos de começar: quatro cartões, cada um com a sua cor
    app.mostrar_editor()
    vertices_antes = list(app.tela.vertices)
    app.mostrar_inicio()
    cartoes = app.tela.cartoes_de_acao
    assert [cartao.titulo for cartao in cartoes] == ["Começar do zero", "Importar desenho", "Abrir arquivo .bosco",
                                                     "Continuar no editor"]
    assert len(set(cartao.papel for cartao in cartoes)) == 4
    # Começar do zero: o editor com um grafo vazio e a busca escolhida; o Ctrl+Z volta para o grafo de antes
    cartoes[0].acionar()
    editor = app.tela
    assert type(editor).__name__ == "EditorDoGrafo" and editor.vertices == [] and editor.arestas == []
    assert editor.busca_escolhida()["chave"] == algoritmos.A_ESTRELA
    editor.desfazer()
    assert editor.vertices == vertices_antes
    app.mostrar_inicio()
    app.tela.cartoes_de_acao[1].acionar()
    assert type(app.tela).__name__ == "TelaDeImportacao"
    app.mostrar_inicio()
    app.tela.cartoes_de_acao[2].acionar()
    assert type(app.tela).__name__ == "TelaDoBosco"
    app.mostrar_inicio()

    # Os componentes desenhados: todos os ícones em vários tamanhos, os botões de cada papel,
    # os segmentos e as etapas
    canvas = tk.Canvas(app.raiz)
    for nome in botoes.ICONES + ["nome_que_nao_existe"]:
        for lado in (12, 20, 40):
            botoes.desenhar_icone(canvas, nome, 20, 20, lado, "#000000", "#ffffff")
    canvas.destroy()
    for papel in ("principal", "sucesso", "perigo", "info", "roxo", "contorno", "suave", "neutro", "icone"):
        botao = botoes.Botao(app.raiz, app, "Teste", icone="play", papel=papel, subtitulo="subtítulo")
        botao.entrou()
        botao.apertou()
        botao.saiu()
        botao.configurar(habilitado=False)
        botao.destroy()
    # O ícone depois do texto (o "Próximo →" do editor): o ícone fica à direita do texto
    for depois in (False, True):
        botao = botoes.Botao(app.raiz, app, "Próximo", icone="seta_direita", icone_depois=depois)
        botao.desenhar()
        texto = [item for item in botao.find_all() if botao.type(item) == "text"][0]
        x_do_texto = botao.coords(texto)[0]
        x_dos_desenhos = [botao.bbox(item)[0] for item in botao.find_all()
                          if botao.type(item) not in ("text", "polygon") and botao.bbox(item)]
        assert (min(x_dos_desenhos) > x_do_texto) == depois, (depois, x_do_texto, x_dos_desenhos)
        botao.destroy()
    variavel = tk.StringVar(app.raiz, value="b")
    mudancas = []
    segmentos = botoes.Segmentos(app.raiz, app, [("a", "A", None), ("b", "B", "dado"), ("c", "C", None)], variavel,
                                 comando=lambda: mudancas.append(variavel.get()))
    segmentos.andar(1)
    segmentos.andar(1)                              # já é o último: fica
    assert variavel.get() == "c" and mudancas == ["c"]
    segmentos.destroy()
    variavel.set("a")                               # depois de destruído, mudar a variável não dá erro
    clicadas = []
    etapas = botoes.Etapas(app.raiz, app, ["Um", "Dois", "Três"], atual=2, ao_clicar=clicadas.append)
    etapas.desenhar()
    for indice in (0, 2):                           # só a etapa que já passou responde ao clique
        x = (etapas.areas[indice][0] + etapas.areas[indice][1]) / 2
        etapas.clicou(SimpleNamespace(x=x, y=5))
    assert clicadas == [0]
    etapas.destroy()
    # As etapas "livres" (o editor): dá para clicar numa etapa da frente também; o "certo" vai nas feitas
    clicadas = []
    etapas = botoes.Etapas(app.raiz, app, ["Um", "Dois", "Três"], atual=0, ao_clicar=clicadas.append, livre=True,
                           feitas=[2])
    etapas.desenhar()
    for indice in (0, 2):
        x = (etapas.areas[indice][0] + etapas.areas[indice][1]) / 2
        etapas.clicou(SimpleNamespace(x=x, y=5))
    assert clicadas == [2] and etapas.esta_feita(2) and not etapas.esta_feita(1)
    etapas.mudar_textos(["Um (8)", "Dois", "Três"])
    assert etapas.textos[0] == "Um (8)"
    etapas.destroy()

    # Os campos desenhados (visual/campos.py)
    from visual import campos
    numero = tk.StringVar(app.raiz, value="2")
    recebidos = []
    contador = campos.Contador(app.raiz, app, numero, 1, 3, ao_mudar=recebidos.append)
    contador.passo(1)
    contador.passo(1)                               # no máximo: fica
    contador.passo(-1)
    numero.set("9")
    contador.confirmar()                            # além do máximo: fica no máximo
    assert recebidos == [3, 2, 3] and numero.get() == "3"
    contador.ligar(False)
    contador.passo(-1)                              # desligado: não muda
    assert numero.get() == "3" and not contador.botao_liberado("menos")
    contador.destroy()
    ligado = tk.BooleanVar(app.raiz, value=False)
    trocas = []
    chave = campos.Interruptor(app.raiz, app, "Teste", ligado, comando=lambda: trocas.append(ligado.get()))
    chave.alternar()
    assert ligado.get() and trocas == [True] and chave.posicao == 1.0
    ligado.set(False)                               # mudou por fora (o Ctrl+Z): a chave acompanha
    assert chave.posicao == 0.0
    chave.ligar(False)
    chave.alternar()
    assert not ligado.get() and trocas == [True]
    chave.destroy()
    escolha = tk.StringVar(app.raiz, value="x")
    escolhidas = []
    seletor = campos.Seletor(app.raiz, app, escolha, ["A", "B"], comando=lambda: escolhidas.append(escolha.get()),
                             vazio="escolha")
    assert seletor.texto == "escolha" and not seletor.tem_valor()
    seletor.andar(1)
    seletor.andar(1)
    seletor.andar(1)                                # no último: fica
    assert escolha.get() == "B" and escolhidas == ["A", "B"] and seletor.texto == "B"
    seletor.mudar_opcoes([("B", "o bê"), "C"])
    assert seletor.texto == "o bê"
    seletor.montar_lista()
    assert seletor.lista.index("end") == 1
    seletor.destroy()
    texto = tk.StringVar(app.raiz, value="abc")
    campo = campos.CampoDeTexto(app.raiz, app, texto, ao_enter=lambda: recebidos.append("enter"))
    campo.marcar_erro(True)
    assert campo.com_erro
    campo.enter()
    assert recebidos[-1] == "enter"
    campo.ligar(False)
    campo.enter()                                   # desligado: o Enter não faz nada
    assert recebidos[-1] == "enter" and len(recebidos) == 4 and campo.entrada.cget("state") == "disabled"
    campo.destroy()
    selo = campos.Selo(app.raiz, app)
    assert selo.largura == 1                        # sem texto: não ocupa espaço
    selo.mudar("Salvo", app.tema["sucesso"], "check")
    assert selo.largura > 1 and selo.texto == "Salvo"
    selo.destroy()
    print(f"12j. Tela inicial: sanfona dos {len(algoritmos.ALGORITMOS)} algoritmos em {len(algoritmos.TIPOS_DE_BUSCA)} tipos (com a animação), cartão "
          f"que muda com a escolha, setas e Enter, tema sol/lua, Ctrl + roda do mouse (70% a 200%), Sobre com os "
          f"nomes, Começar do zero com o Ctrl+Z e {len(botoes.ICONES)} ícones desenhados")


# ----------------------------------------------------------------------
# 12k. A tela do .bosco
# ----------------------------------------------------------------------

def conferir_tela_do_bosco(app, pasta):
    from visual import exportar
    from visual.tela_bosco import data_brasileira
    assert data_brasileira("2026-10-01 14:30") == "01/10/2026 às 14:30" and data_brasileira("ontem") == "ontem"
    # Salvar um .bosco coloca ele nos recentes
    tela = abrir_exemplo(app, algoritmos.BELLMAN_FORD)
    tela.escolher_parte("passo")
    caminho = os.path.join(pasta, "recente.bosco")
    assert exportar.exportar(tela, "bosco", caminho=caminho) == caminho
    assert bosco.listar_recentes()[0] == os.path.abspath(caminho)
    # A tela do .bosco: o recente na lista, a prévia e o Abrir
    app.mostrar_inicio()
    app.tela.abrir_bosco()
    tela = app.tela
    assert type(tela).__name__ == "TelaDoBosco" and tela.detalhes is None
    assert os.path.basename(caminho) in textos_da_tela(tela.lista_de_recentes)
    tela.ler(caminho)
    assert tela.erro is None and tela.detalhes["grafo"]["algoritmo"] == algoritmos.BELLMAN_FORD
    textos = " | ".join(textos_da_tela(tela.cartao))
    assert "Passo a passo" in textos and "Bellman-Ford" in textos, textos
    # O tema mantém o arquivo escolhido
    app.definir_tema("escuro")
    assert app.tela.detalhes is not None and app.tela.caminho == caminho
    app.definir_tema("claro")
    app.tela.abrir()
    assert type(app.tela).__name__ == "TelaDaVisualizacao" and app.tela.chave_da_parte == "passo"
    # Um arquivo estragado: a tela do .bosco aparece com a explicação (nenhuma janela de erro)
    estragado = os.path.join(pasta, "quebrado.bosco")
    Path(estragado).write_text("{ não é json", encoding="utf-8")
    assert exportar.abrir_bosco(app, estragado) is False
    tela = app.tela
    assert type(tela).__name__ == "TelaDoBosco" and "JSON" in tela.erro and tela.caminho == estragado
    # Um recente que sumiu: o problema aparece e "Tirar da lista" tira ele dos recentes
    sumido = os.path.join(pasta, "sumiu.bosco")
    bosco.lembrar_recente(sumido)
    app.mostrar_bosco()
    app.tela.ler(sumido)
    assert app.tela.erro is not None and app.tela.esta_nos_recentes(sumido)
    app.tela.tirar_da_lista()
    assert not app.tela.esta_nos_recentes(sumido) and app.tela.erro is None
    # Duplo clique num recente abre direto
    app.tela.abrir_direto(caminho)
    assert type(app.tela).__name__ == "TelaDaVisualizacao"
    print("12k. Tela do .bosco: recentes, prévia (busca e parte), Abrir, tema sem perder o arquivo, arquivo estragado "
          "explicado na tela (sem janela de erro) e Tirar da lista")


# ----------------------------------------------------------------------
# 12l. As correções da versão 7.1 (o que o Daniel pediu depois de testar a fase 1)
# ----------------------------------------------------------------------

def todos_os_componentes(componente):
    lista = [componente]
    for filho in componente.winfo_children():
        lista += todos_os_componentes(filho)
    return lista


# Responde ao diálogo de texto aberto agora (DialogoDeTexto). Devolve o erro mostrado ("" se fechou).
def responder_dialogo(app, valor, titulo):
    dialogo = app.dialogo
    assert dialogo is not None and dialogo.janela.title() == titulo, (titulo, dialogo and dialogo.janela.title())
    dialogo.valor.set(valor)
    dialogo.confirmar()
    if app.dialogo is None:
        return ""
    return dialogo.rotulo_erro.cget("text")


# O duplo clique numa célula de uma tabela, sem depender da tabela estar na tela (a janela dos testes fica
# escondida): a tabela "responde" que o mouse está na linha e na coluna dadas
def duplo_clique_na_celula(parte, tabela, funcao, linha, coluna):
    colunas = list(tabela.cget("columns"))
    tabela.identify_row = lambda y: linha
    tabela.identify_column = lambda x: f"#{colunas.index(coluna) + 1}"
    try:
        funcao(SimpleNamespace(x=1, y=1))
    finally:
        del tabela.identify_row
        del tabela.identify_column


def linhas_em_destaque(tabela):
    return [tabela.item(iid, "values")[0] for iid in tabela.get_children() if "destaque" in tabela.item(iid, "tags")]


def conferir_correcoes(app):
    import modelos
    from decimal import Decimal
    from visual.botoes import Botao, Lembrete, Segmentos
    from visual.editor import configuracao_da_visualizacao

    # O topo: Início, Editar grafo, Exportar e Exibir são botões desenhados (Exportar e Exibir abrem menus);
    # a dica "Ctrl+PgDn / PgUp troca de parte" saiu
    tela = abrir_exemplo(app, algoritmos.PROFUNDIDADE)
    textos_dos_botoes = [componente.texto for componente in todos_os_componentes(tela.quadro)
                         if isinstance(componente, Botao)]
    for texto in ("Início", "Editar grafo", "Exportar", "Exibir"):
        assert texto in textos_dos_botoes, (texto, textos_dos_botoes)
    assert tela.botao_exportar.menu is not None and tela.botao_exibir.menu is not None
    tudo = " | ".join(textos_da_tela(tela.quadro))
    assert "troca de parte" not in tudo and "PgDn" not in tudo, tudo
    # "até": só nas buscas que usam destino (a DFS não usa); o "de" fica em todas
    assert tela.caixa_destino.grid_info() == {} and tela.rotulo_do_destino.grid_info() == {}
    assert tela.caixa_origem.grid_info() != {}
    tela.variavel_da_busca.set(algoritmos.algoritmo(algoritmos.LARGURA)["nome"])
    tela.mudar_busca()
    assert tela.caixa_destino.grid_info() != {} and tela.rotulo_do_destino.grid_info() != {}
    tela.desfazer()
    assert tela.caixa_destino.grid_info() == {}

    # As partes do grafo: sem Saem/Chegam/grau médio, Quem sai/Quem chega, Como é montado, Renomear e Numerar
    tela = abrir_exemplo(app, algoritmos.A_ESTRELA)
    for chave in ("vertices", "arestas", "pesos", "lista", "adjacencia", "incidencia", "tipo"):
        tela.escolher_parte(chave)
        tela.mostrar_parte()
        textos = " | ".join(textos_da_tela(tela.conteudo))
        for proibido in ("Como é montado", "Numerar", "Renomear", "Quem sai", "Quem chega", "Saem", "Chegam",
                         "grau médio"):
            assert proibido not in textos, (chave, proibido)
        if chave != "tipo":                         # (no Tipo, o lembrete fica na primeira linha da barra)
            assert any(isinstance(componente, Lembrete) for componente in todos_os_componentes(tela.parte.ferramentas)) \
                or chave in ("adjacencia", "incidencia"), chave
    tela.escolher_parte("vertices")
    tela.mostrar_parte()
    parte = tela.parte
    assert tuple(parte.tabela.cget("columns")) == ("numero", "nome", "h", "vizinhos"), parte.tabela.cget("columns")
    assert "soma dos graus" in parte.rotulo_resumo.cget("text")
    # O lembrete do duplo clique: aparece inteiro, ou some (nunca cortado no meio)
    lembrete = Lembrete(tela.conteudo, app, "Duplo clique renomeia")
    lembrete.place(x=0, y=0, width=lembrete.largura, height=lembrete.altura)
    app.raiz.update_idletasks()
    lembrete.desenhar()
    assert lembrete.find_all()
    lembrete.place_configure(width=lembrete.largura // 2)
    app.raiz.update_idletasks()
    lembrete.desenhar()
    assert lembrete.winfo_width() < lembrete.largura and not lembrete.find_all()
    lembrete.destroy()
    tela.escolher_parte("lista")
    assert "sentido" not in tela.parte.escolhas
    assert any(isinstance(componente, Segmentos) for componente in todos_os_componentes(tela.parte.ferramentas))

    # O duplo clique renomeia o vértice (na tabela dos Vértices e na da Lista); o Ctrl+Z desfaz
    sessao = tela.sessao
    tela.escolher_parte("vertices")
    parte = tela.parte
    antigo = sessao.vertices[1]
    duplo_clique_na_celula(parte, parte.tabela, parte.duplo_clique_na_tabela, antigo, "nome")
    assert "existe um vértice" in responder_dialogo(app, sessao.vertices[2], "Renomear vértice")   # repetido: não
    assert responder_dialogo(app, "Novo1", "Renomear vértice") == ""
    assert "Novo1" in tela.sessao.vertices and antigo not in tela.sessao.vertices
    assert tela.parte.escolhas.get("vertice") == "Novo1"
    tela.desfazer()
    assert antigo in tela.sessao.vertices
    tela.escolher_parte("lista")
    parte = tela.parte
    duplo_clique_na_celula(parte, parte.tabela, parte.duplo_clique_na_tabela, antigo, "vizinhos")
    assert responder_dialogo(app, "Novo2", "Renomear vértice") == "" and "Novo2" in tela.sessao.vertices
    tela.desfazer()

    # Arestas: duplo clique na coluna Peso muda o peso; nas outras, renomeia
    tela.escolher_parte("arestas")
    parte = tela.parte
    duplo_clique_na_celula(parte, parte.tabela, parte.duplo_clique_na_tabela, "0", "peso")
    assert responder_dialogo(app, "7,5", "Peso da aresta") == ""
    assert tela.sessao.arestas[0][3] == Decimal("7.5")
    tela.desfazer()
    parte = tela.parte
    duplo_clique_na_celula(parte, parte.tabela, parte.duplo_clique_na_tabela, "0", "ligacao")
    assert "não pode ter" in responder_dialogo(app, "a=b", "Renomear aresta")      # o "=" separa o peso
    assert responder_dialogo(app, "e1", "Renomear aresta") == "" and tela.sessao.arestas[0][2] == "e1"
    tela.desfazer()

    # Pesos: duplo clique na aresta muda o peso; na tabela h, o h (que não pode ser negativo)
    tela.escolher_parte("pesos")
    parte = tela.parte
    duplo_clique_na_celula(parte, parte.tabela, parte.duplo_clique_na_tabela, "1", "peso")
    assert responder_dialogo(app, "", "Peso da aresta") == "" and tela.sessao.arestas[1][3] is None
    tela.desfazer()
    parte = tela.parte
    vertice = tela.sessao.vertices[0]
    duplo_clique_na_celula(parte, parte.tabela_h, parte.duplo_clique_na_heuristica, vertice, "h")
    assert "negativa" in responder_dialogo(app, "-1", "Heurística h")
    assert responder_dialogo(app, "3", "Heurística h") == "" and tela.sessao.heuristica[vertice] == Decimal(3)
    tela.desfazer()

    # O duplo clique no DESENHO: no vértice renomeia, no peso escrito na aresta muda o peso, na aresta renomeia
    tela.escolher_parte("arestas")
    parte = tela.parte
    desenho = parte.desenho
    desenho.desenhar(tela.sessao.estado_montado(), parte.opcoes_do_desenho(neutro=True, tamanho=(1000, 760)))
    x, y = desenho.posicoes[vertice]
    assert desenho.item_para_editar(x, y) == ("vertice", vertice)
    # O peso mais longe de qualquer vértice (para o clique não cair num vértice)
    melhor = None
    for numero in desenho.inicio_do_peso:
        xp = desenho.inicio_do_peso[numero] + 2
        yp = desenho.pontos_dos_nomes[numero][1]
        distancia = min(((xp - xv) ** 2 + (yp - yv) ** 2) ** 0.5 for xv, yv in desenho.posicoes.values())
        if melhor is None or distancia > melhor[0]:
            melhor = (distancia, numero, xp, yp)
    distancia, numero, xp, yp = melhor
    assert desenho.item_para_editar(xp, yp) == ("peso", numero), desenho.item_para_editar(xp, yp)
    parte.duplo_clique_no_desenho(desenho.item_para_editar(xp, yp))
    assert responder_dialogo(app, "9", "Peso da aresta") == "" and tela.sessao.arestas[numero][3] == Decimal(9)
    tela.desfazer()
    tela.parte.duplo_clique_no_desenho(("aresta", numero))
    assert responder_dialogo(app, "rota", "Renomear aresta") == "" and tela.sessao.arestas[numero][2] == "rota"
    tela.desfazer()
    era_a_origem = tela.sessao.inicio == vertice
    assert era_a_origem                                             # (no exemplo do A*, o primeiro é a origem)
    tela.parte.duplo_clique_no_desenho(("vertice", vertice))
    assert responder_dialogo(app, "Comeco", "Renomear vértice") == "" and "Comeco" in tela.sessao.vertices
    assert tela.sessao.inicio == "Comeco"                           # a origem acompanha o nome novo
    tela.desfazer()
    tela.escolher_parte("pesos")                        # nos Pesos, o duplo clique na aresta muda o peso
    tela.parte.duplo_clique_no_desenho(("aresta", numero))
    assert app.dialogo is not None and app.dialogo.janela.title() == "Peso da aresta"
    app.dialogo.fechar()

    # Tipo do grafo: a barra de edição muda o grafo e o tipo muda junto (com o que mudou em destaque)
    grafo = modelos.novo_grafo(["A", "B"], [("A", "B", "", None)], True, "A", True, algoritmos.PROFUNDIDADE)
    app.visualizar(configuracao_da_visualizacao(grafo, "Teste do tipo", None))
    tela = app.tela
    tela.escolher_parte("tipo")
    tela.mostrar_parte()
    parte = tela.parte
    resumo = [parte.tabela.item(iid, "values")[1] for iid in parte.tabela.get_children()][-1]
    assert "simples" in resumo and "acíclico" in resumo and "DAG" in resumo, resumo
    assert not parte.botao_remover.habilitado                   # nada escolhido: não há o que remover
    # A aresta B -> A fecha um ciclo (e, com 2 vértices, deixa o grafo completo)
    parte.nova_origem.set("B")
    parte.novo_destino.set("A")
    parte.acrescentar_aresta()
    assert tela.sessao.arestas[-1] == ("B", "A", "", None)
    assert "Tipo agora:" in tela.aviso_atual and "cíclico (era acíclico)" in tela.aviso_atual, tela.aviso_atual
    assert "completo (era não completo)" in tela.aviso_atual, tela.aviso_atual
    tela.mostrar_parte()
    destacadas = linhas_em_destaque(tela.parte.tabela)
    assert "Cíclico?" in destacadas and "Completo?" in destacadas and "Orientação?" not in destacadas, destacadas
    # Um laço em A: deixa de ser simples (e de ser completo)
    parte = tela.parte
    parte.nova_origem.set("A")
    parte.novo_destino.set("A")
    parte.acrescentar_aresta()
    assert "é um laço" in tela.aviso_atual and "não simples (era simples)" in tela.aviso_atual, tela.aviso_atual
    # Uma paralela (A -> B de novo)
    parte = tela.parte
    parte.nova_origem.set("A")
    parte.novo_destino.set("B")
    parte.acrescentar_aresta()
    assert "paralela" in tela.aviso_atual, tela.aviso_atual
    # Escolher a aresta no desenho e remover (o botão diz qual); a tecla Delete também remove
    parte = tela.parte
    parte.clicou_no_desenho(("aresta", 3))
    assert tela.parte.botao_remover.texto == "Remover A → B" and tela.parte.botao_remover.habilitado
    tela.parte.remover()
    assert len(tela.sessao.arestas) == 3
    tela.parte.clicou_no_desenho(("aresta", 2))                 # o laço
    tela.tecla("apagar")
    assert ("A", "A", "", None) not in tela.sessao.arestas and len(tela.sessao.arestas) == 2
    # Um vértice novo (o próximo nome livre) e a orientação
    tela.parte.acrescentar_vertice()
    assert tela.sessao.vertices == ["A", "B", "C"] and tela.parte.escolhas["vertice"] == "C"
    tela.parte.orientacao.set(False)
    tela.parte.mudar_orientacao()
    assert not tela.sessao.direcionado and "não orientado (era orientado)" in tela.aviso_atual, tela.aviso_atual
    # Remover um vértice leva as arestas dele junto
    tela.parte.clicou_no_desenho(("vertice", "B"))
    assert tela.parte.botao_remover.texto == "Remover B"
    tela.parte.remover()
    assert tela.sessao.vertices == ["A", "C"] and tela.sessao.arestas == []
    # O Ctrl+Z volta tudo, e aí nada fica em destaque (o destaque é só da última mudança)
    while tela.sessao.historico:
        tela.desfazer()
    assert tela.sessao.vertices == ["A", "B"] and tela.sessao.arestas == [("A", "B", "", None)]
    assert tela.sessao.direcionado
    tela.mostrar_parte()
    assert linhas_em_destaque(tela.parte.tabela) == []
    # Sem vértices: a tabela fica vazia e a barra continua funcionando
    for vez in range(2):
        tela.parte.clicou_no_desenho(("vertice", tela.sessao.vertices[0]))
        tela.parte.remover()
    tela.mostrar_parte()
    assert tela.sessao.vertices == [] and tela.parte.tabela.get_children() == ()
    assert "vazio" in tela.parte.rotulo_explicacao.cget("text")
    tela.parte.acrescentar_aresta()                             # sem vértices: avisa, não quebra
    assert "crie os vértices" in tela.aviso_atual
    tela.parte.acrescentar_vertice()
    assert tela.sessao.vertices == ["A"]
    print("12l. Correções 7.1: botões desenhados no topo, \"até\" só com destino, partes do grafo sem Saem/Chegam/"
          "grau médio/Quem sai/Como é montado/Numerar, duplo clique (tabelas e desenho) renomeando vértice e aresta "
          "e mudando peso e h, e a barra de edição do Tipo do grafo com o tipo mudando junto")


# ----------------------------------------------------------------------
# 12m. O editor em etapas (fase 2) e os dois cartões da tela inicial
# ----------------------------------------------------------------------

# O duplo clique numa célula de uma tabela do editor (a janela dos testes fica escondida): a tabela "responde"
# que o clique foi numa célula da coluna dada (a linha é a que está escolhida na tabela)
def duplo_clique_no_editor(tabela, funcao, coluna):
    colunas = list(tabela.cget("displaycolumns"))
    tabela.identify_region = lambda x, y: "cell"
    tabela.identify_column = lambda x: f"#{colunas.index(coluna) + 1}"
    try:
        funcao(SimpleNamespace(x=1, y=1))
    finally:
        del tabela.identify_region
        del tabela.identify_column


# O botão desenhado com este texto dentro de "componente" (None se não houver)
def botao_com_texto(componente, texto):
    from visual.botoes import Botao
    for filho in todos_os_componentes(componente):
        if isinstance(filho, Botao) and filho.texto == texto:
            return filho
    return None


def conferir_editor_em_etapas(app, pasta):
    import modelos
    from decimal import Decimal
    from tkinter import ttk
    import entrada
    from visual.botoes import CartaoDeAcao
    from visual.campos import Interruptor
    from visual.dialogos import DialogoDeAresta, DialogoDeConfirmacao, DialogoDePesos

    pasta_dos_modelos = modelos.PASTA_DOS_MODELOS
    modelos.PASTA_DOS_MODELOS = Path(pasta) / "modelos_do_editor"       # os modelos de verdade não são tocados
    try:
        # A tela inicial: "Ver um exemplo pronto" (cheio) e "Montar meu grafo" (só a borda), na cor do tipo
        app.mostrar_inicio()
        tela = app.tela
        tela.escolher(algoritmos.DIJKSTRA)
        cor = app.tema[algoritmos.TIPOS_DE_BUSCA[1]["cor"]]
        assert isinstance(tela.botao_exemplo, CartaoDeAcao) and tela.botao_exemplo.cheio and tela.botao_exemplo.cor == cor
        assert isinstance(tela.botao_editor, CartaoDeAcao) and not tela.botao_editor.cheio
        assert tela.botao_editor.cor == cor and "Cormen" in tela.botao_exemplo.explicacao
        tela.escolher(algoritmos.LIMITADA)
        assert "Arad até Bucharest, limite 3" in tela.botao_exemplo.explicacao
        # "Montar meu grafo" abre o editor na primeira etapa, com a busca escolhida
        tela.botao_editor.acionar()
        editor = app.tela
        assert type(editor).__name__ == "EditorDoGrafo" and editor.etapa == 0
        assert editor.busca.get() == algoritmos.LIMITADA

        # O que saiu do editor (Desfazer, Pasta, Prefixo, Gerar, a lista de adjacência, Sortear listas) e os
        # componentes antigos do ttk (todos os botões e campos agora são desenhados)
        textos = " | ".join(textos_da_tela(editor.quadro))
        for proibido in ("Desfazer", "Pasta", "Prefixo", "Gerar", "Lista de adjacência", "Sortear listas", "Quem sai"):
            assert proibido not in textos, proibido
        antigos = (ttk.Button, ttk.Combobox, ttk.Spinbox, ttk.Checkbutton, ttk.Radiobutton, ttk.Entry, ttk.Menubutton)
        for componente in todos_os_componentes(editor.quadro):
            assert not isinstance(componente, antigos), componente
        inicio = botao_com_texto(editor.cabecalho, "Início")
        assert inicio is not None and inicio.papel == "suave"

        # Começar do zero: vazio, na etapa ①, e só essa etapa na tela
        app.mostrar_inicio()
        app.tela.comecar_do_zero()
        editor = app.tela
        etapa = editor.etapas[0]
        assert editor.vertices == [] and editor.etapa == 0 and editor.selo.texto == "Ainda não salvo"
        assert etapa.quadro.winfo_manager() == "place"
        assert editor.etapas[1].quadro.winfo_manager() == "" and editor.etapas[2].quadro.winfo_manager() == ""
        assert editor.trilha.textos == ["Vértices", "Arestas", "Busca"] and editor.etapas_feitas() == []
        assert not editor.botao_voltar.grid_info() and editor.botao_proximo.texto == "Próximo: Arestas"
        assert etapa.rotulo_vazio.place_info()                  # a tabela vazia diz o que fazer
        # (o estilo dos nomes continua o da última vez: um exemplo com 1, 2, 3 deixa "1, 2, 3…" marcado)
        etapa.segmentos_do_estilo.escolher(0)
        assert editor.estilo.get() == "letras"

        # A Quantidade já cria e tira: o +, o número digitado, o máximo (26) e o texto que não é número
        for vez in range(3):
            etapa.contador.passo(1)
        assert editor.vertices == ["A", "B", "C"] and editor.quantidade_vertices.get() == "3"
        assert not etapa.rotulo_vazio.place_info() and "criado" in editor.aviso
        editor.quantidade_vertices.set("5")
        etapa.contador.confirmar()
        assert editor.vertices == list("ABCDE")
        editor.quantidade_vertices.set("99")
        etapa.contador.confirmar()
        assert editor.vertices == list(entrada.LETRAS) and editor.quantidade_vertices.get() == "26"
        etapa.contador.passo(1)
        assert len(editor.vertices) == 26
        editor.quantidade_vertices.set("abc")
        etapa.contador.confirmar()
        assert editor.quantidade_vertices.get() == "26" and len(editor.vertices) == 26
        editor.quantidade_vertices.set("9")
        etapa.contador.confirmar()
        assert editor.vertices == list("ABCDEFGHI") and "tirados do fim" in editor.aviso
        assert editor.trilha.textos[0] == "Vértices (9)" and 0 in editor.etapas_feitas()
        # Digitado sem Enter e trocando de etapa (o clique num botão desenhado não tira o foco): vale igual
        editor.quantidade_vertices.set("10")
        editor.mostrar_etapa(1, animar=False)
        editor.mostrar_etapa(0, animar=False)
        assert len(editor.vertices) == 10
        editor.quantidade_vertices.set("9")
        etapa.contador.confirmar()

        # Os nomes 1, 2, 3...: a sequência muda junto (com as arestas); de 9 para 10 vira 01..10; o Ctrl+Z
        # desfaz cada mudança e a escolha do estilo acompanha os nomes
        editor.nova_origem.set("A")
        editor.novo_destino.set("B")
        editor.adicionar_aresta()
        editor.inicio.set("C")                                 # o início da busca acompanha o nome novo
        etapa.segmentos_do_estilo.escolher(1)
        assert editor.vertices == [str(numero) for numero in range(1, 10)] and editor.arestas[0][:2] == ("1", "2")
        assert editor.inicio.get() == "3"
        etapa.contador.passo(1)
        assert editor.vertices == [f"{numero:02d}" for numero in range(1, 11)]
        assert editor.arestas[0][:2] == ("01", "02") and "refeitos" in editor.aviso
        editor.desfazer()
        assert editor.vertices == [str(numero) for numero in range(1, 10)] and editor.estilo.get() == "numeros"
        editor.desfazer()
        assert editor.vertices == list("ABCDEFGHI") and editor.estilo.get() == "letras"
        assert editor.arestas[0][:2] == ("A", "B") and etapa.segmentos_do_estilo.indice_escolhido() == 0
        assert editor.inicio.get() == "C"
        # Tirar pela Quantidade leva junto as arestas de quem saiu (o I sai, a aresta I -> A também)
        editor.nova_origem.set("I")
        editor.novo_destino.set("A")
        editor.adicionar_aresta()
        etapa.contador.passo(-1)
        assert editor.vertices == list("ABCDEFGH") and editor.arestas == [("A", "B", "", None)]
        assert "1 aresta saiu junto" in editor.aviso
        editor.desfazer()
        editor.desfazer()
        assert editor.vertices == list("ABCDEFGHI") and editor.arestas == [("A", "B", "", None)]

        # Um de cada vez: o nome sugerido, o inválido (a caixa fica vermelha) e o repetido
        assert editor.novo_vertice.get() == "J"
        editor.novo_vertice.set("tem espaço")
        editor.adicionar_vertice()
        assert editor.aviso_de_erro and etapa.campo_nome.com_erro and len(editor.vertices) == 9
        editor.novo_vertice.set("Casa")
        editor.adicionar_vertice()
        assert editor.vertices[-1] == "Casa" and not editor.aviso_de_erro
        editor.novo_vertice.set("Casa")
        editor.adicionar_vertice()
        assert editor.aviso_de_erro and editor.vertices.count("Casa") == 1
        # Com um nome próprio, o estilo não renomeia ninguém: vale para os próximos criados pela Quantidade
        etapa.segmentos_do_estilo.escolher(1)
        assert editor.vertices[-1] == "Casa" and "nomes próprios" in editor.aviso
        etapa.contador.passo(1)
        assert editor.vertices[-2:] == ["Casa", "01"]
        etapa.contador.passo(-1)                               # tira do fim
        assert editor.vertices[-1] == "Casa"
        editor.estilo.set("letras")

        # Renomear e Remover: ligados conforme a escolha na tabela
        tabela = etapa.tabela
        tabela.selection_set(())
        etapa.atualizar_botoes()
        assert not etapa.botao_editar.habilitado and not etapa.botao_remover.habilitado
        tabela.selection_set(("0", "1"))
        etapa.atualizar_botoes()
        assert not etapa.botao_editar.habilitado and etapa.botao_remover.habilitado
        tabela.selection_set(("9",))
        etapa.atualizar_botoes()
        assert etapa.botao_editar.habilitado and etapa.botao_remover.habilitado
        etapa.botao_editar.acionar()
        assert responder_dialogo(app, "Lar", "Renomear vértice") == ""
        assert editor.vertices[9] == "Lar" and "Casa" not in editor.vertices
        tabela.selection_set(("0", "1"))                       # A e B: a aresta A -> B sai junto
        etapa.atualizar_botoes()                               # (na tela, o <<TreeviewSelect>> faz isso)
        etapa.botao_remover.acionar()
        assert "A" not in editor.vertices and "B" not in editor.vertices and editor.arestas == []
        editor.desfazer()
        assert editor.vertices[:2] == ["A", "B"] and len(editor.arestas) == 1
        # O duplo clique na coluna h muda a heurística (a coluna aparece quando a busca usa h)
        editor.escolher_busca(algoritmos.A_ESTRELA)
        assert "h" in tabela.cget("displaycolumns")
        tabela.selection_set(("2",))
        duplo_clique_no_editor(tabela, editor.duplo_clique_no_vertice, "h")
        assert responder_dialogo(app, "-1", "Heurística") != ""
        assert responder_dialogo(app, "4", "Heurística") == "" and editor.heuristica["C"] == Decimal(4)
        editor.escolher_busca(algoritmos.PROFUNDIDADE)

        # As etapas: o Próximo, o Voltar, a trilha (que leva a qualquer etapa) e a animação
        editor.proxima_etapa()
        assert editor.etapa == 1 and editor.trilha.atual == 1
        assert editor.botao_voltar.grid_info() and editor.botao_voltar.texto == "Voltar: Vértices"
        assert editor.botao_proximo.texto == "Próximo: Busca" and not editor.botao_visualizar.grid_info()
        editor.proxima_etapa()
        assert editor.etapa == 2 and editor.botao_visualizar.grid_info() and not editor.botao_proximo.grid_info()
        editor.proxima_etapa()                                 # já é a última: fica
        assert editor.etapa == 2
        editor.trilha.ao_clicar(0)
        assert editor.etapa == 0 and etapa.quadro.winfo_manager() == "place"
        assert editor.etapas[1].quadro.winfo_manager() == "" and editor.etapas[2].quadro.winfo_manager() == ""
        editor.quadro.winfo_ismapped = lambda: True            # a janela dos testes fica escondida: "finge" que aparece
        editor.mostrar_etapa(1)
        assert editor.deslize is not None
        esperar(app, lambda: editor.deslize is None)
        assert editor.etapas[1].quadro.place_info()["relx"] == "0" and editor.etapas[0].quadro.winfo_manager() == ""
        del editor.quadro.winfo_ismapped
        for tecla in ("<Alt-Right>", "<Alt-Left>", "<F5>", "<Control-z>", "<Control-s>", "<Control-o>"):
            assert app.raiz.bind(tecla), tecla

        # ② Arestas: a orientação (com o Ctrl+Z), uma de cada vez, o laço e o peso errado
        etapa = editor.etapas[1]
        etapa.segmentos_da_orientacao.escolher(1)
        assert not editor.direcionado.get() and etapa.tabela.item("0", "values")[1] == "A — B"
        editor.desfazer()
        assert editor.direcionado.get() and etapa.tabela.item("0", "values")[1] == "A → B"
        editor.nova_origem.set("B")
        editor.novo_destino.set("C")
        editor.novo_nome_da_aresta.set("e2")
        editor.novo_peso.set("2,5")
        editor.adicionar_aresta()
        assert editor.arestas[-1] == ("B", "C", "e2", Decimal("2.5")) and editor.novo_nome_da_aresta.get() == ""
        assert "peso" in etapa.tabela.cget("displaycolumns")    # com peso no grafo, a coluna aparece
        editor.novo_peso.set("x")
        editor.adicionar_aresta()
        assert editor.aviso_de_erro and etapa.campo_peso.com_erro and len(editor.arestas) == 2
        editor.novo_peso.set("")
        editor.nova_origem.set("C")
        editor.novo_destino.set("C")
        editor.adicionar_aresta()
        assert "é um laço" in editor.aviso and editor.arestas[-1][:2] == ("C", "C")
        etapa.seletor_origem.andar(1)                          # ↓ na escolha: o vértice de baixo
        assert editor.nova_origem.get() == "D"
        # Editar uma aresta inteira (de, para, nome e peso) pela janela que o duplo clique abre
        etapa.tabela.selection_set(("1",))
        duplo_clique_no_editor(etapa.tabela, editor.duplo_clique_na_aresta, "peso")
        dialogo = app.dialogo
        assert isinstance(dialogo, DialogoDeAresta) and dialogo.janela.title() == "Editar a aresta 2"
        dialogo.peso.set("abc")
        dialogo.confirmar()
        assert app.dialogo is dialogo and "Peso" in dialogo.rotulo_erro.cget("text")
        dialogo.destino.set("D")
        dialogo.peso.set("7")
        dialogo.confirmar()
        assert app.dialogo is None and editor.arestas[1] == ("B", "D", "e2", Decimal(7))
        # A posição (o Nº): a aresta 2 vai para a 1ª posição (a ordem em que os vizinhos entram nas listas)
        primeira = editor.arestas[0]
        etapa.tabela.selection_set(("1",))
        editor.editar_aresta()
        assert app.dialogo.contador_da_posicao.maximo == len(editor.arestas)
        app.dialogo.posicao.set("1")
        app.dialogo.confirmar()
        assert editor.arestas[0] == ("B", "D", "e2", Decimal(7)) and editor.arestas[1] == primeira
        assert "posição 1" in editor.aviso and etapa.tabela.selection() == ("0",)
        editor.desfazer()
        assert editor.arestas[1] == ("B", "D", "e2", Decimal(7))
        # O sorteio: no lugar das de agora, e o contador não passa do máximo (que muda com os laços)
        maximo = editor.maximo_de_arestas()
        assert etapa.contador.maximo == maximo and f"cabem até {maximo}" == etapa.rotulo_maximo.cget("text")
        for componente in todos_os_componentes(etapa.quadro):
            if isinstance(componente, Interruptor) and componente.texto == "Laços":
                componente.alternar()
        assert editor.lacos.get() and etapa.contador.maximo == entrada.maximo_de_arestas(len(editor.vertices), True,
                                                                                       False, True)
        editor.lacos.set(False)
        etapa.atualizar_maximo()
        editor.quantidade_arestas.set("7")
        botao_com_texto(etapa.quadro, "Sortear arestas").acionar()
        assert len(editor.arestas) == 7 and "no lugar das de antes" in editor.aviso
        editor.desfazer()
        assert len(editor.arestas) == 3

        # ③ Busca: uma coluna por tipo, as opções que aparecem conforme a busca e o que falta (com os botões)
        editor.mostrar_etapa(2, animar=False)
        etapa = editor.etapas[2]
        etapa.escolha.escolher(algoritmos.A_ESTRELA)
        assert editor.busca.get() == algoritmos.A_ESTRELA and etapa.seletor_destino.grid_info()
        assert not etapa.contador_do_limite.grid_info()
        textos = textos_da_tela(etapa.lista_do_que_falta)
        assert any("sem h" in texto for texto in textos) and "Dar h…" in textos, textos
        assert editor.rotulo_resumo.cget("text").startswith("Falta:") and not editor.botao_visualizar.habilitado
        botao_com_texto(etapa.lista_do_que_falta, "Dar h…").acionar()
        assert isinstance(app.dialogo, DialogoDePesos) and app.dialogo.lugar.get() == "vertices"
        app.dialogo.fechar()
        editor.visualizar()                                    # com problema: fica no editor e explica
        assert app.tela is editor and editor.aviso_de_erro
        etapa.escolha.escolher(algoritmos.PROFUNDIDADE)
        assert not etapa.seletor_destino.grid_info() and not etapa.rotulo_destino.grid_info()
        etapa.escolha.andar(1)                                 # ↓: a próxima busca (a limitada, com o limite)
        assert editor.busca.get() == algoritmos.LIMITADA and etapa.contador_do_limite.grid_info()
        assert etapa.seletor_destino.grid_info()               # na limitada, o destino é opcional ("nenhum")
        etapa.contador_do_limite.passo(1)
        assert editor.limite.get() == "4" and editor.limite_escolhido() == 4
        etapa.escolha.trocar_de_coluna(1)                      # →: a mesma linha no tipo do lado
        assert editor.busca.get() == algoritmos.BELLMAN_FORD
        etapa.escolha.escolher(algoritmos.PROFUNDIDADE)
        editor.inicio.set("A")
        etapa.seletor_inicio.andar(1)                          # ↓ na escolha do início: o vértice de baixo
        assert editor.inicio.get() == "B"
        antes = editor.ordenar.get()
        for componente in todos_os_componentes(etapa.quadro):
            if isinstance(componente, Interruptor):
                componente.alternar()
        assert editor.ordenar.get() != antes
        assert "Tudo pronto" in " ".join(textos_da_tela(etapa.lista_do_que_falta)) and editor.botao_visualizar.habilitado
        assert not editor.rotulo_resumo.cget("text").startswith("Falta:")

        # O modelo: o selo, o Salvar (pede o nome na primeira vez, depois grava direto) e o Tornar padrão
        assert editor.selo.texto == "Ainda não salvo" and not editor.botao_padrao.habilitado
        editor.salvar_modelo()
        assert responder_dialogo(app, "Prova 01", "Salvar modelo") != ""         # o da prova é protegido
        assert responder_dialogo(app, "Teste do editor", "Salvar modelo") == ""
        assert editor.modelo_aberto == "Teste do editor" and editor.selo.texto == "Sem alterações"
        assert modelos.existe_modelo("Teste do editor") and editor.botao_padrao.habilitado
        assert editor.botao_do_modelo.texto == "Teste do editor"
        editor.novo_vertice.set("Z")
        editor.adicionar_vertice()
        assert editor.selo.texto == "Alterações não salvas"
        editor.salvar_modelo()                                 # já tem nome: grava direto, sem janela
        assert app.dialogo is None and editor.selo.texto == "Sem alterações"
        editor.tornar_padrao()
        assert modelos.nome_do_padrao() == "Teste do editor" and not editor.botao_padrao.habilitado
        assert editor.botao_padrao.texto == "Modelo padrão"
        editor.montar_menu_dos_modelos()
        menu = editor.menu_dos_modelos
        rotulos = []
        for indice in range(menu.index("end") + 1):
            if menu.type(indice) == "command":
                rotulos.append(menu.entrycget(indice, "label"))
        assert any(rotulo.startswith("✓") and "Teste do editor" in rotulo and "★" in rotulo for rotulo in rotulos)
        assert "Salvar com outro nome…" in rotulos and "Grafo novo, vazio" in rotulos
        # Salvar com outro nome que já existe: pergunta antes de substituir
        editor.salvar_como()
        assert responder_dialogo(app, "Outro", "Salvar modelo") == "" and editor.modelo_aberto == "Outro"
        editor.carregar_modelo("Teste do editor")
        editor.salvar_como()
        assert responder_dialogo(app, "Outro", "Salvar modelo") == ""
        app.raiz.update()
        assert isinstance(app.dialogo, DialogoDeConfirmacao)
        app.dialogo.confirmar()
        assert app.dialogo is None and editor.modelo_aberto == "Outro"
        # Grafo novo, vazio (do menu do modelo): volta para a etapa ① e o Ctrl+Z traz o grafo de volta
        quantos = len(editor.vertices)
        editor.grafo_vazio()
        assert editor.vertices == [] and editor.etapa == 0 and editor.selo.texto == "Ainda não salvo"
        editor.desfazer()
        assert len(editor.vertices) == quantos

        # O tema e a volta para o editor mantêm a etapa
        editor.mostrar_etapa(1, animar=False)
        app.definir_tema("escuro")
        assert app.tela.etapa == 1 and len(app.tela.vertices) == quantos
        app.definir_tema("claro")
        app.mostrar_inicio()
        app.mostrar_editor()
        assert app.tela.etapa == 1
        # Visualizar (pronto): abre a visualização; o "Editar grafo" volta para a etapa Busca, de onde saiu
        app.tela.mostrar_etapa(2, animar=False)
        app.tela.visualizar()
        assert type(app.tela).__name__ == "TelaDaVisualizacao"
        app.tela.editar_grafo()
        assert type(app.tela).__name__ == "EditorDoGrafo" and app.tela.etapa == 2
    finally:
        modelos.PASTA_DOS_MODELOS = pasta_dos_modelos
    print("12m. Editor em etapas: uma etapa por tela (com a trilha, o Voltar/Próximo e a animação), a Quantidade "
          "que cria e tira na hora, os nomes A, B, C ou 1, 2, 3 com o Ctrl+Z, a aresta editada inteira, o sorteio, a "
          "escolha da busca (uma coluna por tipo) com o que falta, o Salvar que pede o nome, e os cartões da tela inicial")


def rodar():
    try:
        raiz_de_teste = tk.Tk()
        raiz_de_teste.destroy()
    except tk.TclError:
        print("12. Telas: não conferidas (sem tela gráfica)")
        return
    from visual.aplicativo import Aplicativo
    app = Aplicativo(montar_passos)
    app.raiz.withdraw()
    erros = []
    # Um erro dentro de um evento do Tkinter não para o programa (só é escrito): aqui ele é guardado
    app.raiz.report_callback_exception = lambda tipo, valor, rastro: erros.append(
        "".join(traceback.format_exception(tipo, valor, rastro)))
    contagem = {"partes": 0, "passos": 0, "linhas": 0, "pdfs": 0, "paginas": 0}
    arquivo_dos_recentes = bosco.arquivo_dos_recentes
    try:
        with tempfile.TemporaryDirectory() as pasta:
            # Os recentes do .bosco vão para a pasta temporária (a lista de verdade não é tocada)
            bosco.arquivo_dos_recentes = lambda: Path(pasta) / "recentes.txt"
            for informacoes in algoritmos.ALGORITMOS:
                conferir_busca(app, informacoes["chave"], pasta, contagem)
            print(f"12a. Todas as partes das {len(algoritmos.ALGORITMOS)} buscas abrem e respondem ao teclado "
                  f"({contagem['partes']} partes)")
            print(f"12b. Passo a passo: o código destacado conferido em {contagem['passos']} passos "
                  f"(pseudocódigo e Java)")
            print(f"12c. Linha a linha: código (Python e C), pilha e desenho conferidos em {contagem['linhas']} linhas; "
                  f"escolher uma linha leva às vezes em que ela roda")
            print("12d. Comparar códigos: lado a lado, nos dois modos, a mesma linha destacada nas duas linguagens")
            conferir_mudancas(app)
            print(f"12f. Exportações a partir da tela: SVG, PNG, {contagem['pdfs']} PDFs ({contagem['paginas']} páginas "
                  f"de relatório), .bosco reaberto no mesmo lugar e código-fonte, nas {len(algoritmos.ALGORITMOS)} buscas")
            print("12g. O tema escuro recria a tela no mesmo passo; Editar grafo e Visualizar voltam para a mesma busca")
            conferir_importacao(app, pasta)
            conferir_tela_inicial(app)
            conferir_tela_do_bosco(app, pasta)
            conferir_correcoes(app)
            conferir_editor_em_etapas(app, pasta)
            # A tela inicial: "Montar meu grafo" abre o editor com a busca escolhida, e o editor volta igual
            app.mostrar_inicio()
            app.tela.montar_grafo(algoritmos.BELLMAN_FORD)
            assert app.tela.busca_escolhida()["chave"] == algoritmos.BELLMAN_FORD
            vertices = list(app.tela.vertices)
            app.mostrar_inicio()
            app.mostrar_editor()
            assert app.tela.vertices == vertices and app.tela.busca_escolhida()["chave"] == algoritmos.BELLMAN_FORD
            app.raiz.update()
    finally:
        bosco.arquivo_dos_recentes = arquivo_dos_recentes
        app.raiz.destroy()
    assert not erros, erros[0]


if __name__ == "__main__":
    rodar()
    print("Todos os testes das telas passaram.")
