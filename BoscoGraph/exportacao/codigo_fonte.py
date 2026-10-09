'''
    O código-fonte da busca, COM O GRAFO DENTRO, na linguagem escolhida: um programa completo, num arquivo
    só, que roda sozinho (python arquivo.py, java Arquivo.java, gcc arquivo.c...) e escreve o resultado.

    O arquivo tem três partes:
      1. o código de estudo da busca (o mesmo do modo linha a linha e da comparação), sem os rótulos @;
      2. o grafo escrito na linguagem (a lista de adjacência na ordem em que a busca visita, os pesos, a
         origem, o destino...) e a chamada da busca;
      3. no fim, num comentário, a SAÍDA ESPERADA: o que o programa tem que escrever, calculado pelo
         BoscoGraph na hora de exportar. Assim dá para conferir na mão.

    A saída é igual em todas as linguagens (os testes rodam as cinco e comparam). Os números: "inf" para
    o infinito e inteiros sem casas decimais. Cuidado com pesos decimais: o Java, o C, o C++ e o JavaScript
    usam double, que tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o Python de estudo
    usa Decimal, exato como o BoscoGraph.

    O "pseudocódigo" sai como um texto (.txt): o pseudocódigo, o grafo e o resultado esperado.

    Os RÓTULOS. O modo linha a linha da tela mostra este mesmo programa (o arquivo inteiro, da primeira à
    última linha) e o Python roda de verdade. Para destacar nas outras linguagens a linha que faz o mesmo,
    cada linha do programa ganha um rótulo, como as do código de estudo (veja estudo/__init__.py): as do
    cabeçalho são "cabecalho_1", "cabecalho_2"...; as do grafo, "principal_grafo"; a chamada da busca,
    "principal_buscar"; e assim por diante. Enquanto o programa é montado, o rótulo vai grudado no fim
    da linha, depois de um caractere invisível (MARCA); no fim, programa() separa os dois. O arquivo
    exportado sai sem os rótulos.
    Este arquivo não usa Tkinter.
'''

import datetime
import json
from decimal import Decimal

import algoritmos
import caminhos
import entrada as entrada_do_grafo
import estudo
from estudo import rastreador

LINGUAGENS = {
    "python": {"extensao": ".py", "descricao": "Programa em Python", "comentario": "#"},
    "java": {"extensao": ".java", "descricao": "Programa em Java", "comentario": "//"},
    "c": {"extensao": ".c", "descricao": "Programa em C", "comentario": "//"},
    "cpp": {"extensao": ".cpp", "descricao": "Programa em C++", "comentario": "//"},
    "javascript": {"extensao": ".js", "descricao": "Programa em JavaScript (Node.js)", "comentario": "//"},
    "pseudocodigo": {"extensao": ".txt", "descricao": "Texto", "comentario": ""},
}

# O que a "resposta" da busca quer dizer (vai num comentário perto da linha que a escreve)
SIGNIFICADO_DA_RESPOSTA = {
    algoritmos.BELLMAN_FORD: "VERDADEIRO = nenhum ciclo negativo alcançável a partir da origem",
    algoritmos.FLOYD_WARSHALL: "VERDADEIRO = nenhum ciclo negativo (nenhum d[i][i] ficou negativo)",
    algoritmos.GULOSA: "VERDADEIRO = chegou ao destino",
    algoritmos.A_ESTRELA: "VERDADEIRO = chegou ao destino",
    algoritmos.BIDIRECIONAL: "VERDADEIRO = os dois lados se encontraram (existe caminho)",
    algoritmos.LIMITADA: "achou = chegou ao destino; corte = o limite cortou algum caminho; falha = não há caminho",
    algoritmos.ITERATIVA: "achou = chegou ao destino; falha = não há caminho",
}


def informacoes_da_linguagem(chave):
    return LINGUAGENS[chave]


# "Dijkstra - Prova 01" (sem a extensão)
def nome_sugerido(algoritmo, nome_do_grafo, linguagem):
    return caminhos.nome_de_arquivo(algoritmos.algoritmo(algoritmo)["nome_curto"] + " - " + nome_do_grafo)


def como_rodar(linguagem, nome_do_arquivo):
    if linguagem == "python":
        return f"Para rodar: python \"{nome_do_arquivo}\""
    if linguagem == "java":
        return (f"Para rodar (Java 16 ou mais novo): java \"{nome_do_arquivo}\"  "
                f"(ou: javac -encoding UTF-8 \"{nome_do_arquivo}\" e depois java Programa)")
    if linguagem == "c":
        return (f"Para compilar: gcc -std=c11 \"{nome_do_arquivo}\" -o busca -lm   e rodar: ./busca "
                f"(no Windows: busca.exe)")
    if linguagem == "cpp":
        return (f"Para compilar: g++ -std=c++17 \"{nome_do_arquivo}\" -o busca   e rodar: ./busca "
                f"(no Windows: busca.exe)")
    if linguagem == "javascript":
        return f"Para rodar: node \"{nome_do_arquivo}\""
    return "Abra no Bloco de Notas (ou em qualquer editor de texto)."


# ----------------------------------------------------------------------
# A entrada da busca e o resultado esperado (rodando o Python de estudo)
# ----------------------------------------------------------------------

# dados: {"nome", "vertices", "arestas", "ordenar", "inicio", "direcionado", "algoritmo", "destino",
#         "heuristica", "limite"} (visual/exportar.py monta a partir da sessão)
def preparar(dados):
    entrada = rastreador.preparar_entrada(dados["vertices"], dados["arestas"], dados["ordenar"], dados["inicio"],
                                          dados["direcionado"])
    entrada["nomes"] = list(dados["vertices"])
    return entrada


def rodar_o_python(dados, entrada):
    arquivo, busca, executar = rastreador.criar_busca(dados["algoritmo"], entrada, dados["direcionado"],
                                                      dados["destino"], dados["heuristica"], dados["limite"])
    resposta = executar()
    return busca, resposta


# O número como os programas escrevem: inf, -inf, inteiros sem casas, e o decimal sem zeros no fim
def numero(valor):
    valor = Decimal(valor)
    if valor.is_infinite():
        return "inf" if valor > 0 else "-inf"
    if valor == valor.to_integral_value():
        return str(int(valor))
    return format(valor.normalize(), "f")


def nome_ou_nil(valor):
    return "NIL" if valor is None else valor


def verdadeiro_ou_falso(resposta):
    return "VERDADEIRO" if resposta else "FALSO"


# As linhas que o programa escreve, a partir do estado final do Python de estudo
def saida_esperada(algoritmo, nomes, busca, resposta):
    linhas = []
    if algoritmo == algoritmos.PROFUNDIDADE:
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, d = {busca.d[v]}, f = {busca.f[v]}, pai = {nome_ou_nil(busca.pai[v])}")
        for u in nomes:
            for v in nomes:
                if (u, v) in busca.tipo:
                    linhas.append(f"aresta ({u}, {v}): {busca.tipo[(u, v)]}")
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, d = {numero(busca.d[v])}, pai = {nome_ou_nil(busca.pai[v])}")
    elif algoritmo == algoritmos.BELLMAN_FORD:
        for v in nomes:
            linhas.append(f"{v}: d = {numero(busca.d[v])}, pai = {nome_ou_nil(busca.pai[v])}")
        linhas.append("resposta: " + verdadeiro_ou_falso(resposta))
    elif algoritmo == algoritmos.GULOSA:
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, pai = {nome_ou_nil(busca.pai[v])}")
        linhas.append("resposta: " + verdadeiro_ou_falso(resposta))
    elif algoritmo == algoritmos.A_ESTRELA:
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, g = {numero(busca.g[v])}, f = {numero(busca.f[v])}, "
                          f"pai = {nome_ou_nil(busca.pai[v])}")
        linhas.append("resposta: " + verdadeiro_ou_falso(resposta))
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        for v in nomes:
            prof = busca.prof[v] if v in busca.prof else "-"
            linhas.append(f"{v}: cor = {busca.cor[v]}, pai = {nome_ou_nil(busca.pai[v])}, prof = {prof}")
        linhas.append("caminho: " + (" ".join(busca.caminho) if busca.caminho else "(vazio)"))
        linhas.append("cortados: " + (" ".join(busca.cortados) if busca.cortados else "(nenhum)"))
        linhas.append("resposta: " + resposta)
    elif algoritmo == algoritmos.PRIM:
        total = 0
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, chave = {numero(busca.chave[v])}, pai = {nome_ou_nil(busca.pai[v])}")
            total += busca.chave[v]
        linhas.append("peso total: " + numero(total))
    elif algoritmo == algoritmos.KRUSKAL:
        for v in nomes:
            linhas.append(f"{v}: conjunto = {busca.conjunto[v]}")
        total = 0
        for u, v, peso in busca.arvore:
            linhas.append(f"aresta da árvore: {u} - {v} (peso {numero(peso)})")
            total += peso
        linhas.append("peso total: " + numero(total))
    elif algoritmo == algoritmos.BIDIRECIONAL:
        for v in nomes:
            linhas.append(f"{v}: cor = {busca.cor[v]}, lado = {nome_ou_nil(busca.lado[v])}, d = {numero(busca.d[v])}, "
                          f"d' = {numero(busca.d_tras[v])}, pai = {nome_ou_nil(busca.pai[v])}, "
                          f"pai' = {nome_ou_nil(busca.pai_tras[v])}")
        if busca.encontro is not None:
            linhas.append(f"encontro: {busca.encontro[0]} {busca.encontro[1]}")
        linhas.append("resposta: " + verdadeiro_ou_falso(resposta))
    else:
        for i in nomes:
            for j in nomes:
                linhas.append(f"d({i}, {j}) = {numero(busca.d[i][j])}, pi({i}, {j}) = {nome_ou_nil(busca.pi[i][j])}")
        linhas.append("resposta: " + verdadeiro_ou_falso(resposta))
    return linhas


# ----------------------------------------------------------------------
# Ajudantes de texto
# ----------------------------------------------------------------------

# Um texto entre aspas, válido em Python, Java, C, C++ e JavaScript (o JSON escreve igual)
def aspas(texto):
    return json.dumps(texto, ensure_ascii=False)


# O peso no código: 4, 2.5 (um peso que falta vira 0: as buscas que deixam faltar não usam o peso)
def peso_comum(peso):
    if peso is None:
        return "0"
    return numero(peso)


def peso_python(peso):
    if peso is None:
        return "None"
    if Decimal(peso) == Decimal(peso).to_integral_value():
        return str(int(peso))
    return f"Decimal(\"{numero(peso)}\")"


def peso_java(peso):
    texto = peso_comum(peso)
    if "." not in texto:
        texto += ".0"               # double no Java: 4.0 (o 4 sozinho é int, e o Map<String, Double> não aceita)
    return texto


def comentar(linhas, comentario):
    resultado = []
    for linha in linhas:
        resultado.append((comentario + " " + linha).rstrip() if comentario else linha)
    return resultado


# ----------------------------------------------------------------------
# Os rótulos (veja a explicação no começo do arquivo)
# ----------------------------------------------------------------------

MARCA = "\x01"


def rotular(linha, rotulo):
    return linha + MARCA + rotulo


def rotular_todas(linhas, rotulo):
    resultado = []
    for linha in linhas:
        resultado.append(rotular(linha, rotulo))
    return resultado


# Separa cada linha do seu rótulo: devolve (as linhas limpas, {número da linha: rótulo}); a 1ª linha é 1
def separar_rotulos(linhas):
    limpas = []
    rotulos = {}
    for numero in range(1, len(linhas) + 1):
        linha = linhas[numero - 1]
        if MARCA in linha:
            linha, rotulo = linha.split(MARCA, 1)
            rotulos[numero] = rotulo
        limpas.append(linha)
    return limpas, rotulos


# O cabeçalho comentado, cada linha com o seu rótulo: cabecalho_1, cabecalho_2... (é o mesmo texto em
# todas as linguagens: a linha 3 de um é a linha 3 do outro)
def cabecalho_comentado(topo, comentario):
    linhas = comentar(topo, comentario)
    resultado = []
    for indice in range(len(linhas)):
        resultado.append(rotular(linhas[indice], f"cabecalho_{indice + 1}"))
    return resultado


# A faixa que separa o código de estudo do resto ("===", o título, "==="), com um rótulo só
def faixa(comentario, titulo, rotulo="principal_titulo"):
    return rotular_todas([comentario + " " + "=" * 70, comentario + " " + titulo, comentario + " " + "=" * 70],
                         rotulo)


# agora: a data e a hora do cabeçalho ("02/10/2026 15:30"); None = agora mesmo
def cabecalho(linguagem, dados, nome_do_arquivo, agora=None):
    informacoes = algoritmos.algoritmo(dados["algoritmo"])
    if agora is None:
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    orientacao = "orientado" if dados["direcionado"] else "não orientado"
    linhas = [f"{informacoes['nome']} no grafo \"{dados['nome']}\"",
              f"Gerado pelo {caminhos.NOME_DO_PROGRAMA} {caminhos.VERSAO} em {agora}.",
              f"O grafo: {orientacao} · {entrada_do_grafo.resumo(dados['vertices'], dados['arestas'], dados['direcionado'])}."]
    opcoes = []
    if dados["algoritmo"] == algoritmos.PRIM:
        opcoes.append(f"raiz {dados['inicio']}")
    elif dados["algoritmo"] not in (algoritmos.FLOYD_WARSHALL, algoritmos.KRUSKAL):
        opcoes.append(f"origem {dados['inicio']}")
    if dados.get("destino") is not None:
        opcoes.append(f"destino {dados['destino']}")
    if dados.get("limite") is not None:
        opcoes.append(f"limite {dados['limite']}")
    if opcoes:
        linhas.append("A busca: " + ", ".join(opcoes) + ".")
    linhas.append("")
    linhas.append(como_rodar(linguagem, nome_do_arquivo) if linguagem != "pseudocodigo" else
                  "O pseudocódigo é o do livro do Cormen (CLRS), como o BoscoGraph mostra.")
    linhas.append("O algoritmo é o código de estudo do BoscoGraph (o mesmo do modo linha a linha).")
    linhas.append("No fim do arquivo está a saída esperada, para conferir.")
    if linguagem in ("java", "c", "cpp", "javascript"):
        linhas.append("Pesos decimais: double tem erro de arredondamento (0.1 + 0.2 = 0.30000000000000004).")
    return linhas


# O código de estudo da busca na linguagem, com os rótulos dele grudados (MARCA) nas linhas que têm
def codigo_de_estudo(algoritmo, linguagem):
    carregado = estudo.carregar(algoritmo, linguagem)
    linhas = []
    for numero in range(1, len(carregado["linhas"]) + 1):
        linha = carregado["linhas"][numero - 1]
        rotulo = carregado["rotulo_da_linha"].get(numero)
        if rotulo is None:
            linhas.append(linha)
        else:
            linhas.append(rotular(linha, rotulo))
    return linhas


# ----------------------------------------------------------------------
# O programa
# ----------------------------------------------------------------------

GERADORES = {}          # preenchido no fim do arquivo: linguagem -> a função que escreve o programa


# linguagem: a chave (python, java...); nome_do_arquivo: o nome com que vai ser salvo (vai no cabeçalho).
# Devolve o texto do arquivo.
def programa(linguagem, dados, nome_do_arquivo):
    entrada = preparar(dados)
    busca, resposta = rodar_o_python(dados, entrada)
    saida = saida_esperada(dados["algoritmo"], entrada["nomes"], busca, resposta)
    return montar_programa(linguagem, dados, entrada, saida, nome_do_arquivo)["texto"]


# Os programas nas seis linguagens de uma vez (a busca roda uma vez só), para o modo linha a linha.
# nome: o nome do arquivo sem a extensão; agora: a data e a hora do cabeçalho (a mesma nos seis).
# Devolve {linguagem: o programa}, cada um como em montar_programa.
def programas_com_rotulos(dados, nome, agora=None):
    entrada = preparar(dados)
    busca, resposta = rodar_o_python(dados, entrada)
    saida = saida_esperada(dados["algoritmo"], entrada["nomes"], busca, resposta)
    if agora is None:
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    programas = {}
    for linguagem in LINGUAGENS:
        programas[linguagem] = montar_programa(linguagem, dados, entrada, saida, nome, agora)
    return programas


# Monta o programa. Devolve {"linguagem", "nome" (o nome do arquivo, com a extensão), "texto" (o arquivo),
# "linhas" (as linhas, sem os rótulos), "rotulos" ({número da linha: rótulo}), "saida" (a saída esperada)}
def montar_programa(linguagem, dados, entrada, saida, nome_do_arquivo, agora=None):
    if not nome_do_arquivo.endswith(LINGUAGENS[linguagem]["extensao"]):
        nome_do_arquivo += LINGUAGENS[linguagem]["extensao"]
    topo = cabecalho(linguagem, dados, nome_do_arquivo, agora)
    linhas = GERADORES[linguagem](dados, entrada, topo)
    comentario = LINGUAGENS[linguagem]["comentario"]
    linhas.append("")
    if linguagem == "pseudocodigo":
        linhas.append(rotular("O RESULTADO (calculado pelo BoscoGraph)", "saida_esperada"))
        linhas += rotular_todas(saida, "saida_esperada")
    else:
        linhas += rotular_todas(comentar(["Saída esperada (calculada pelo BoscoGraph ao exportar):"], comentario),
                                "saida_esperada")
        linhas += rotular_todas(comentar(["    " + linha for linha in saida], comentario), "saida_esperada")
    limpas, rotulos = separar_rotulos(linhas)
    return {"linguagem": linguagem, "nome": nome_do_arquivo, "texto": "\n".join(limpas) + "\n", "linhas": limpas,
            "rotulos": rotulos, "saida": list(saida)}


# ----------------------------------------------------------------------
# Python
# ----------------------------------------------------------------------

def programa_python(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    nomes = entrada["nomes"]
    linhas = cabecalho_comentado(topo, "#") + [""]
    linhas += codigo_de_estudo(algoritmo, "python")
    linhas += ["", ""] + faixa("#", "O grafo exportado pelo BoscoGraph e a chamada da busca")
    linhas += [rotular("from decimal import Decimal", "estrutura_importar"), "", ""]
    linhas += rotular_todas(["# O número como o BoscoGraph escreve: inf para o infinito e inteiros sem casas decimais",
                             "def numero(x):",
                             "    x = Decimal(x)",
                             "    if x.is_infinite():",
                             "        return \"inf\" if x > 0 else \"-inf\"",
                             "    if x == x.to_integral_value():",
                             "        return str(int(x))",
                             "    return format(x.normalize(), \"f\")"], "aux_numero")
    linhas += ["", ""]
    linhas += rotular_todas(["def nome(v):",
                             "    return \"NIL\" if v is None else v"], "aux_nome")
    linhas += ["", ""]
    linhas += rotular_todas(["def verdadeiro_ou_falso(resposta):",
                             "    return \"VERDADEIRO\" if resposta else \"FALSO\""], "aux_verdadeiro")
    linhas += ["", ""]
    linhas.append(rotular("nomes = [" + ", ".join(aspas(v) for v in nomes) + "]      # os vértices, na ordem em que "
                          "foram criados", "principal_nomes"))
    sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
    if algoritmo == algoritmos.KRUSKAL:
        grafo = ["# As arestas (u, v, peso), uma vez cada, na ordem em que foram criadas", "arestas = ["]
        for u, v, peso in entrada["arestas"]:
            grafo.append(f"    ({aspas(u)}, {aspas(v)}, {peso_python(peso)}),")
        grafo.append("]")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL):
        grafo = ["# Os arcos (u, v, peso), na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)"), "arcos = ["]
        for u, v, peso in entrada["arcos"]:
            grafo.append(f"    ({aspas(u)}, {aspas(v)}, {peso_python(peso)}),")
        grafo.append("]")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        grafo = ["# adj[u] = os vizinhos de u, na ordem em que a busca visita"
                 + ("" if sem_pesos else " (com o peso de cada aresta)")]
        grafo += dicionario_python("adj", nomes, entrada["vizinhos"] if sem_pesos else entrada["com_pesos"], sem_pesos)
        linhas += rotular_todas(grafo, "principal_grafo")
        if algoritmo == algoritmos.BIDIRECIONAL:
            tras = ["# adj_tras[v] = quem CHEGA em v (o lado de trás anda pelas arestas ao contrário)"]
            tras += dicionario_python("adj_tras", nomes, entrada["com_pesos_tras"], False)
            linhas += rotular_todas(tras, "principal_grafo_tras")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        linhas.append(rotular("h = {" + ", ".join(f"{aspas(v)}: {peso_python(dados['heuristica'].get(v, 0))}"
                                                  for v in nomes)
                              + "}      # a heurística: a estimativa de cada vértice até o destino", "principal_h"))
    origem = aspas(entrada["origem"])
    destino = aspas(dados["destino"]) if dados.get("destino") is not None else "None"
    linhas.append("")
    criar = "principal_criar"
    buscar = "principal_buscar"
    cada = "principal_cada_vertice"
    escreve = "principal_escreve_vertice"
    resposta = "principal_escreve_resposta"
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas += rotular_todas(["# As raízes: a origem primeiro, depois os outros vértices em ordem alfabética",
                                 "ordem = [" + ", ".join(aspas(v) for v in entrada["ordem"]) + "]"], "principal_ordem")
        linhas += [rotular(f"busca = BuscaEmProfundidade(adj, {dados['direcionado']})", criar),
                   rotular("busca.dfs(ordem)", buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, d = {busca.d[v]}, f = {busca.f[v]}, pai = "
                           "{nome(busca.pai[v])}\")", escreve),
                   rotular("for u in nomes:", "principal_cada_par"),
                   rotular("    for v in nomes:", "principal_cada_par"),
                   rotular("        if (u, v) in busca.tipo:", "principal_escreve_par"),
                   rotular("            print(f\"aresta ({u}, {v}): {busca.tipo[(u, v)]}\")", "principal_escreve_par")]
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        classe, metodo = ("BuscaEmLargura", "bfs") if algoritmo == algoritmos.LARGURA else ("Dijkstra", "dijkstra")
        linhas += [rotular(f"busca = {classe}(adj)", criar),
                   rotular(f"busca.{metodo}({origem})", buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, d = {numero(busca.d[v])}, pai = "
                           "{nome(busca.pai[v])}\")", escreve)]
    elif algoritmo == algoritmos.BELLMAN_FORD:
        linhas += [rotular("busca = BellmanFord(nomes, arcos)", criar),
                   rotular(f"resposta = busca.bellman_ford({origem})      # {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: d = {numero(busca.d[v])}, pai = {nome(busca.pai[v])}\")", escreve),
                   rotular("print(\"resposta: \" + verdadeiro_ou_falso(resposta))", resposta)]
    elif algoritmo == algoritmos.GULOSA:
        linhas += [rotular("busca = BuscaGulosa(adj, h)", criar),
                   rotular(f"resposta = busca.buscar({origem}, {destino})      # {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, pai = {nome(busca.pai[v])}\")", escreve),
                   rotular("print(\"resposta: \" + verdadeiro_ou_falso(resposta))", resposta)]
    elif algoritmo == algoritmos.A_ESTRELA:
        linhas += [rotular("busca = AEstrela(adj, h)", criar),
                   rotular(f"resposta = busca.buscar({origem}, {destino})      # {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, g = {numero(busca.g[v])}, f = {numero(busca.f[v])}, "
                           "pai = {nome(busca.pai[v])}\")", escreve),
                   rotular("print(\"resposta: \" + verdadeiro_ou_falso(resposta))", resposta)]
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        if algoritmo == algoritmos.LIMITADA:
            linhas += [rotular("busca = ProfundidadeLimitada(adj)", criar),
                       rotular(f"resposta = busca.buscar({origem}, {destino}, {dados['limite']})      "
                               f"# {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        else:
            linhas += [rotular("busca = AprofundamentoIterativo(adj)", criar),
                       rotular(f"resposta = busca.buscar({origem}, {destino})      "
                               f"# {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        linhas += [rotular("for v in nomes:", cada),
                   rotular("    prof = busca.prof[v] if v in busca.prof else \"-\"      # \"-\" = nunca entrou no "
                           "caminho", escreve),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, pai = {nome(busca.pai[v])}, prof = {prof}\")",
                           escreve),
                   rotular("print(\"caminho: \" + (\" \".join(busca.caminho) if busca.caminho else \"(vazio)\"))",
                           "principal_escreve_caminho"),
                   rotular("print(\"cortados: \" + (\" \".join(busca.cortados) if busca.cortados else \"(nenhum)\"))",
                           "principal_escreve_cortados"),
                   rotular("print(\"resposta: \" + resposta)", resposta)]
    elif algoritmo == algoritmos.PRIM:
        linhas += rotular_todas(["# As raízes: a escolhida primeiro, depois os outros vértices em ordem alfabética",
                                 "raizes = [" + ", ".join(aspas(v) for v in entrada["ordem"]) + "]"],
                                "principal_raizes")
        linhas += [rotular("busca = Prim(adj)", criar),
                   rotular("busca.prim(raizes)", buscar),
                   rotular("total = 0", "principal_total"),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, chave = {numero(busca.chave[v])}, pai = "
                           "{nome(busca.pai[v])}\")", escreve),
                   rotular("    total = total + busca.chave[v]      # a chave é o peso da aresta por onde v entrou",
                           "principal_soma"),
                   rotular("print(\"peso total: \" + numero(total))", "principal_escreve_total")]
    elif algoritmo == algoritmos.KRUSKAL:
        linhas += [rotular("busca = Kruskal(nomes, arestas)", criar),
                   rotular("busca.kruskal()", buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: conjunto = {nome(busca.conjunto[v])}\")", escreve),
                   rotular("total = 0", "principal_total"),
                   rotular("for u, v, peso in busca.arvore:", "principal_cada_aresta"),
                   rotular("    print(f\"aresta da árvore: {u} - {v} (peso {numero(peso)})\")",
                           "principal_escreve_aresta"),
                   rotular("    total = total + peso", "principal_soma"),
                   rotular("print(\"peso total: \" + numero(total))", "principal_escreve_total")]
    elif algoritmo == algoritmos.BIDIRECIONAL:
        linhas += [rotular("busca = BuscaBidirecional(adj, adj_tras)", criar),
                   rotular(f"resposta = busca.buscar({origem}, {destino})      # {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for v in nomes:", cada),
                   rotular("    print(f\"{v}: cor = {busca.cor[v]}, lado = {nome(busca.lado[v])}, d = "
                           "{numero(busca.d[v])}, \"", escreve),
                   rotular("          f\"d' = {numero(busca.d_tras[v])}, pai = {nome(busca.pai[v])}, pai' = "
                           "{nome(busca.pai_tras[v])}\")", escreve),
                   rotular("if busca.encontro is not None:", "principal_escreve_encontro"),
                   rotular("    print(f\"encontro: {busca.encontro[0]} {busca.encontro[1]}\")",
                           "principal_escreve_encontro"),
                   rotular("print(\"resposta: \" + verdadeiro_ou_falso(resposta))", resposta)]
    else:
        linhas += [rotular("busca = FloydWarshall(nomes, arcos)", criar),
                   rotular(f"resposta = busca.floyd_warshall()      # {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar),
                   rotular("for i in nomes:", "principal_cada_par"),
                   rotular("    for j in nomes:", "principal_cada_par"),
                   rotular("        print(f\"d({i}, {j}) = {numero(busca.d[i][j])}, pi({i}, {j}) = "
                           "{nome(busca.pi[i][j])}\")", "principal_escreve_par"),
                   rotular("print(\"resposta: \" + verdadeiro_ou_falso(resposta))", resposta)]
    return linhas


def dicionario_python(nome, nomes, listas, sem_pesos):
    linhas = [nome + " = {"]
    for u in nomes:
        if sem_pesos:
            itens = ", ".join(aspas(v) for v in listas[u])
        else:
            itens = ", ".join(f"({aspas(v)}, {peso_python(peso)})" for v, peso in listas[u])
        linhas.append(f"    {aspas(u)}: [{itens}],")
    linhas.append("}")
    return linhas


# ----------------------------------------------------------------------
# Java
# ----------------------------------------------------------------------

CLASSES_DO_JAVA = {
    algoritmos.PROFUNDIDADE: "BuscaEmProfundidade", algoritmos.LARGURA: "BuscaEmLargura",
    algoritmos.DIJKSTRA: "Dijkstra", algoritmos.BELLMAN_FORD: "BellmanFord", algoritmos.GULOSA: "BuscaGulosa",
    algoritmos.A_ESTRELA: "AEstrela", algoritmos.LIMITADA: "ProfundidadeLimitada",
    algoritmos.ITERATIVA: "AprofundamentoIterativo", algoritmos.BIDIRECIONAL: "BuscaBidirecional",
    algoritmos.FLOYD_WARSHALL: "FloydWarshall", algoritmos.PRIM: "Prim", algoritmos.KRUSKAL: "Kruskal",
}


def programa_java(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    classe = CLASSES_DO_JAVA[algoritmo]
    nomes = entrada["nomes"]
    estudo_java = codigo_de_estudo(algoritmo, "java")
    # Os "import" ficam no começo do arquivo; a classe da busca deixa de ser "public" (num arquivo
    # com várias classes, só uma pode ser public, e com o nome do arquivo: assim o nome fica livre)
    importacoes = ["import java.math.BigDecimal;", "import java.util.LinkedHashMap;", "import java.util.List;",
                   "import java.util.Map;"]
    corpo = []
    for linha in estudo_java:
        if linha.startswith("import "):
            if linha not in importacoes:
                importacoes.append(linha)
        elif linha.startswith("public class "):
            corpo.append(linha[len("public "):])
        else:
            corpo.append(linha)
    while corpo and corpo[0] == "":
        corpo.pop(0)
    importacoes.sort()
    linhas = cabecalho_comentado(topo, "//") + [""] + rotular_todas(importacoes, "estrutura_importar") + [""]
    linhas += faixa("//", "O grafo exportado pelo BoscoGraph e a chamada da busca")
    linhas.append(rotular("class Programa {", "principal_programa"))
    linhas += rotular_todas(["    // O número como o BoscoGraph escreve: inf para o infinito e inteiros sem casas decimais",
                             "    static String numero(double x) {",
                             "        if (Double.isInfinite(x)) {",
                             "            return x > 0 ? \"inf\" : \"-inf\";",
                             "        }",
                             "        if (x == Math.rint(x)) {",
                             "            return String.valueOf((long) x);",
                             "        }",
                             "        return BigDecimal.valueOf(x).stripTrailingZeros().toPlainString();",
                             "    }"], "aux_numero")
    linhas.append("")
    linhas += rotular_todas(["    static String nome(String v) {",
                             "        return v == null ? \"NIL\" : v;",
                             "    }"], "aux_nome")
    linhas.append("")
    linhas += rotular_todas(["    static String verdadeiroOuFalso(boolean resposta) {",
                             "        return resposta ? \"VERDADEIRO\" : \"FALSO\";",
                             "    }"], "aux_verdadeiro")
    linhas.append("")
    linhas.append(rotular("    public static void main(String[] argumentos) {", "principal_main"))
    linhas += rotular_todas(["        // Os vértices, na ordem em que foram criados",
                             "        List<String> nomes = List.of(" + ", ".join(aspas(v) for v in nomes) + ");"],
                            "principal_nomes")
    sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
    if algoritmo == algoritmos.KRUSKAL:
        grafo = ["        // As arestas (u, v, peso), uma vez cada, na ordem em que foram criadas",
                 "        List<Kruskal.Aresta> arestas = List.of("]
        itens = [f"            new Kruskal.Aresta({aspas(u)}, {aspas(v)}, {peso_java(peso)})"
                 for u, v, peso in entrada["arestas"]]
        grafo += juntar_com_virgulas(itens)
        grafo.append("        );")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL):
        grafo = ["        // Os arcos (u, v, peso), na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)"),
                 f"        List<{classe}.Arco> arcos = List.of("]
        itens = [f"            new {classe}.Arco({aspas(u)}, {aspas(v)}, {peso_java(peso)})" for u, v, peso in entrada["arcos"]]
        grafo += juntar_com_virgulas(itens)
        grafo.append("        );")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        grafo = ["        // adj.get(u) = os vizinhos de u, na ordem em que a busca visita"
                 + ("" if sem_pesos else " (com o peso de cada aresta)")]
        grafo += mapa_java("adj", classe, nomes, entrada["vizinhos"] if sem_pesos else entrada["com_pesos"], sem_pesos)
        linhas += rotular_todas(grafo, "principal_grafo")
        if algoritmo == algoritmos.BIDIRECIONAL:
            tras = ["        // adjTras.get(v) = quem CHEGA em v (o lado de trás anda pelas arestas ao contrário)"]
            tras += mapa_java("adjTras", classe, nomes, entrada["com_pesos_tras"], False)
            linhas += rotular_todas(tras, "principal_grafo_tras")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        heuristica = ["        // A heurística: a estimativa de cada vértice até o destino",
                      "        Map<String, Double> h = new LinkedHashMap<>();"]
        for v in nomes:
            heuristica.append(f"        h.put({aspas(v)}, {peso_java(dados['heuristica'].get(v, 0))});")
        linhas += rotular_todas(heuristica, "principal_h")
    origem = aspas(entrada["origem"])
    destino = aspas(dados["destino"]) if dados.get("destino") is not None else "null"
    linhas.append("")
    pa = "        "
    criar = "principal_criar"
    buscar = "principal_buscar"
    cada = "principal_cada_vertice"
    escreve = "principal_escreve_vertice"
    resposta = "principal_escreve_resposta"
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas += rotular_todas([pa + "// As raízes: a origem primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "List<String> ordem = List.of(" + ", ".join(aspas(v) for v in entrada["ordem"]) + ");"],
                                "principal_ordem")
        linhas += [rotular(pa + f"BuscaEmProfundidade busca = new BuscaEmProfundidade(adj, "
                                f"{str(dados['direcionado']).lower()});", criar),
                   rotular(pa + "busca.dfs(ordem);", buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", d = \" + busca.d.get(v) + \", f = \"",
                                 pa + "                       + busca.f.get(v) + \", pai = \" + nome(busca.pai.get(v)));",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "for (String u : nomes) {",
                                 pa + "    for (String v : nomes) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        String tipo = busca.tipo.get(List.of(u, v));",
                                 pa + "        if (tipo != null) {",
                                 pa + "            System.out.println(\"aresta (\" + u + \", \" + v + \"): \" + tipo);",
                                 pa + "        }"], "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        metodo = "bfs" if algoritmo == algoritmos.LARGURA else "dijkstra"
        linhas += [rotular(pa + f"{classe} busca = new {classe}(adj);", criar),
                   rotular(pa + f"busca.{metodo}({origem});", buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", d = \" + numero(busca.d.get(v))",
                                 pa + "                       + \", pai = \" + nome(busca.pai.get(v)));",
                                 pa + "}"], escreve)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        linhas += [rotular(pa + "BellmanFord busca = new BellmanFord(nomes, arcos);", criar),
                   rotular(pa + f"boolean resposta = busca.bellmanFord({origem});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": d = \" + numero(busca.d.get(v)) + \", pai = \" + nome(busca.pai.get(v)));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "System.out.println(\"resposta: \" + verdadeiroOuFalso(resposta));", resposta))
    elif algoritmo == algoritmos.GULOSA:
        linhas += [rotular(pa + "BuscaGulosa busca = new BuscaGulosa(adj, h);", criar),
                   rotular(pa + f"boolean resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", pai = \" + nome(busca.pai.get(v)));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "System.out.println(\"resposta: \" + verdadeiroOuFalso(resposta));", resposta))
    elif algoritmo == algoritmos.A_ESTRELA:
        linhas += [rotular(pa + "AEstrela busca = new AEstrela(adj, h);", criar),
                   rotular(pa + f"boolean resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", g = \" + numero(busca.g.get(v))",
                                 pa + "                       + \", f = \" + numero(busca.f.get(v)) + \", pai = \" + nome(busca.pai.get(v)));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "System.out.println(\"resposta: \" + verdadeiroOuFalso(resposta));", resposta))
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        if algoritmo == algoritmos.LIMITADA:
            linhas += [rotular(pa + "ProfundidadeLimitada busca = new ProfundidadeLimitada(adj);", criar),
                       rotular(pa + f"String resposta = busca.buscar({origem}, {destino}, {dados['limite']});      "
                                    f"// {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        else:
            linhas += [rotular(pa + "AprofundamentoIterativo busca = new AprofundamentoIterativo(adj);", criar),
                       rotular(pa + f"String resposta = busca.buscar({origem}, {destino});      "
                                    f"// {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        linhas.append(rotular(pa + "for (String v : nomes) {", cada))
        linhas += rotular_todas([pa + "    // \"-\" = nunca entrou no caminho",
                                 pa + "    String prof = busca.prof.containsKey(v) ? String.valueOf(busca.prof.get(v)) : \"-\";",
                                 pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", pai = \" + nome(busca.pai.get(v))",
                                 pa + "                       + \", prof = \" + prof);",
                                 pa + "}"], escreve)
        linhas += [rotular(pa + "System.out.println(\"caminho: \" + (busca.caminho.isEmpty() ? \"(vazio)\" : String.join(\" \", busca.caminho)));",
                           "principal_escreve_caminho"),
                   rotular(pa + "System.out.println(\"cortados: \" + (busca.cortados.isEmpty() ? \"(nenhum)\" : String.join(\" \", busca.cortados)));",
                           "principal_escreve_cortados"),
                   rotular(pa + "System.out.println(\"resposta: \" + resposta);", resposta)]
    elif algoritmo == algoritmos.PRIM:
        linhas += rotular_todas([pa + "// As raízes: a escolhida primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "List<String> raizes = List.of(" + ", ".join(aspas(v) for v in entrada["ordem"])
                                 + ");"], "principal_raizes")
        linhas += [rotular(pa + "Prim busca = new Prim(adj);", criar),
                   rotular(pa + "busca.prim(raizes);", buscar),
                   rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", chave = \" + numero(busca.chave.get(v))",
                                 pa + "                       + \", pai = \" + nome(busca.pai.get(v)));"], escreve)
        linhas += [rotular(pa + "    total = total + busca.chave.get(v);      // a chave é o peso da aresta por onde v entrou",
                           "principal_soma"),
                   rotular(pa + "}", cada),
                   rotular(pa + "System.out.println(\"peso total: \" + numero(total));", "principal_escreve_total")]
    elif algoritmo == algoritmos.KRUSKAL:
        linhas += [rotular(pa + "Kruskal busca = new Kruskal(nomes, arestas);", criar),
                   rotular(pa + "busca.kruskal();", buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": conjunto = \" + nome(busca.conjunto.get(v)));",
                                 pa + "}"], escreve)
        linhas += [rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (Kruskal.Aresta aresta : busca.arvore) {", "principal_cada_aresta")]
        linhas += rotular_todas([pa + "    System.out.println(\"aresta da árvore: \" + aresta.u() + \" - \" + aresta.v() + \" (peso \"",
                                 pa + "                       + numero(aresta.peso()) + \")\");"], "principal_escreve_aresta")
        linhas += [rotular(pa + "    total = total + aresta.peso();", "principal_soma"),
                   rotular(pa + "}", "principal_cada_aresta"),
                   rotular(pa + "System.out.println(\"peso total: \" + numero(total));", "principal_escreve_total")]
    elif algoritmo == algoritmos.BIDIRECIONAL:
        linhas += [rotular(pa + "BuscaBidirecional busca = new BuscaBidirecional(adj, adjTras);", criar),
                   rotular(pa + f"boolean resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (String v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    System.out.println(v + \": cor = \" + busca.cor.get(v) + \", lado = \" + nome(busca.lado.get(v))",
                                 pa + "                       + \", d = \" + numero(busca.d.get(v)) + \", d' = \" + numero(busca.dTras.get(v))",
                                 pa + "                       + \", pai = \" + nome(busca.pai.get(v)) + \", pai' = \" + nome(busca.paiTras.get(v)));",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "if (busca.encontro != null) {",
                                 pa + "    System.out.println(\"encontro: \" + busca.encontro.get(0) + \" \" + busca.encontro.get(1));",
                                 pa + "}"], "principal_escreve_encontro")
        linhas.append(rotular(pa + "System.out.println(\"resposta: \" + verdadeiroOuFalso(resposta));", resposta))
    else:
        linhas += [rotular(pa + "FloydWarshall busca = new FloydWarshall(nomes, arcos);", criar),
                   rotular(pa + f"boolean resposta = busca.floydWarshall();      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar)]
        linhas += rotular_todas([pa + "for (String i : nomes) {",
                                 pa + "    for (String j : nomes) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        System.out.println(\"d(\" + i + \", \" + j + \") = \" + numero(busca.d.get(i).get(j))",
                                 pa + "                           + \", pi(\" + i + \", \" + j + \") = \" + nome(busca.pi.get(i).get(j)));"],
                                "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
        linhas.append(rotular(pa + "System.out.println(\"resposta: \" + verdadeiroOuFalso(resposta));", resposta))
    linhas += rotular_todas(["    }", "}"], "principal_fim")
    linhas += [""] + faixa("//", "A busca (o código de estudo do BoscoGraph)", "principal_titulo_do_estudo")
    linhas += corpo
    return linhas


def juntar_com_virgulas(itens):
    linhas = []
    for posicao in range(len(itens)):
        linhas.append(itens[posicao] + ("," if posicao < len(itens) - 1 else ""))
    return linhas


def mapa_java(nome, classe, nomes, listas, sem_pesos):
    tipo = "List<String>" if sem_pesos else f"List<{classe}.Vizinho>"
    linhas = [f"        Map<String, {tipo}> {nome} = new LinkedHashMap<>();"]
    for u in nomes:
        if sem_pesos:
            itens = ", ".join(aspas(v) for v in listas[u])
        else:
            itens = ", ".join(f"new {classe}.Vizinho({aspas(v)}, {peso_java(peso)})" for v, peso in listas[u])
        linhas.append(f"        {nome}.put({aspas(u)}, List.of({itens}));")
    return linhas


# ----------------------------------------------------------------------
# C
# ----------------------------------------------------------------------

def programa_c(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    nomes = entrada["nomes"]
    numero_de = {}
    for indice in range(len(nomes)):
        numero_de[nomes[indice]] = indice
    linhas = cabecalho_comentado(topo, "//") + [""] + codigo_de_estudo(algoritmo, "c")
    sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
    com_arcos = algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL)
    com_arestas = algoritmo == algoritmos.KRUSKAL           # as arestas uma vez cada, sem listas de vizinhos
    usa_numero = algoritmo not in (algoritmos.PROFUNDIDADE, algoritmos.GULOSA, algoritmos.LIMITADA,
                                   algoritmos.ITERATIVA)
    linhas += ["", ""] + faixa("//", "O grafo exportado pelo BoscoGraph e a chamada da busca")
    linhas += rotular_todas(["#include <math.h>", "#include <stdbool.h>", "#include <stdio.h>", "#include <stdlib.h>"],
                            "estrutura_importar") + [""]
    linhas += rotular_todas(["// Os vértices viram números (a posição na lista): "
                             + ", ".join(f"{indice} = {nomes[indice]}" for indice in range(len(nomes))),
                             "static const char *nomes[] = {" + ", ".join(aspas(v) for v in nomes) + "};"],
                            "principal_nomes")
    linhas.append("")
    linhas += rotular_todas(["static const char *nome(int v) {",
                             "    return v == NIL ? \"NIL\" : nomes[v];",
                             "}"], "aux_nome")
    linhas.append("")
    if usa_numero:
        linhas += rotular_todas(["// O número como o BoscoGraph escreve: inf para o infinito, inteiros sem casas decimais e, nos",
                                 "// outros, o menor número de casas que volta exatamente ao mesmo double",
                                 "static void escrever_numero(double x) {",
                                 "    if (isinf(x)) {",
                                 "        printf(\"%s\", x > 0 ? \"inf\" : \"-inf\");",
                                 "    } else if (x == floor(x)) {",
                                 "        printf(\"%.0f\", x);",
                                 "    } else {",
                                 "        char texto[40];",
                                 "        for (int casas = 1; casas <= 17; casas++) {",
                                 "            snprintf(texto, sizeof texto, \"%.*g\", casas, x);",
                                 "            if (strtod(texto, NULL) == x) {",
                                 "                break;",
                                 "            }",
                                 "        }",
                                 "        printf(\"%s\", texto);",
                                 "    }",
                                 "}"], "aux_numero")
        linhas.append("")
    if algoritmo not in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL, algoritmos.KRUSKAL):
        linhas += [rotular("static const char *NOMES_DAS_CORES[] = {\"Branco\", \"Cinza\", \"Preto\"};", "aux_cores"), ""]
    if algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.GULOSA, algoritmos.A_ESTRELA, algoritmos.BIDIRECIONAL,
                     algoritmos.FLOYD_WARSHALL):
        linhas += rotular_todas(["static const char *verdadeiro_ou_falso(bool resposta) {",
                                 "    return resposta ? \"VERDADEIRO\" : \"FALSO\";",
                                 "}"], "aux_verdadeiro")
        linhas.append("")
    # As funções só entram se forem usadas (o compilador avisa função que não é usada): num grafo sem
    # arestas, não há nada para ligar
    tem_ligacoes = False
    for u in nomes:
        if entrada["vizinhos"][u]:
            tem_ligacoes = True
    if com_arestas:
        if entrada["arestas"]:
            linhas += rotular_todas(["// Acrescenta uma aresta no fim da lista de arestas",
                                     "static void aresta(int u, int v, double peso) {",
                                     "    arestas[m].u = u;",
                                     "    arestas[m].v = v;",
                                     "    arestas[m].peso = peso;",
                                     "    m = m + 1;",
                                     "}"], "aux_aresta")
            linhas.append("")
    elif not com_arcos:
        parametro = "" if sem_pesos else ", double peso"
        if tem_ligacoes:
            ligar = ["// Põe v no FIM da lista de u (a ordem das listas é a ordem em que a busca visita)",
                     f"static void ligar(Vizinho *listas[], int u, int v{parametro}) {{",
                     "    Vizinho *novo = malloc(sizeof *novo);",
                     "    novo->v = v;"]
            if not sem_pesos:
                ligar.append("    novo->peso = peso;")
            ligar += ["    novo->proximo = NULL;",
                      "    if (listas[u] == NULL) {",
                      "        listas[u] = novo;                   // a lista estava vazia: o novo é o primeiro",
                      "    } else {",
                      "        Vizinho *ultimo = listas[u];",
                      "        while (ultimo->proximo != NULL) {   // anda até o último nó",
                      "            ultimo = ultimo->proximo;",
                      "        }",
                      "        ultimo->proximo = novo;",
                      "    }",
                      "}"]
            linhas += rotular_todas(ligar, "aux_ligar") + [""]
        linhas += rotular_todas(["// Devolve a memória de uma lista (cada malloc com o seu free)",
                                 "static void liberar(Vizinho *atual) {",
                                 "    while (atual != NULL) {",
                                 "        Vizinho *proximo = atual->proximo;",
                                 "        free(atual);",
                                 "        atual = proximo;",
                                 "    }",
                                 "}"], "aux_liberar")
        linhas.append("")
    elif entrada["arcos"]:
        linhas += rotular_todas(["// Acrescenta um arco no fim da lista de arcos",
                                 "static void arco(int u, int v, double peso) {",
                                 "    arcos[m].u = u;",
                                 "    arcos[m].v = v;",
                                 "    arcos[m].peso = peso;",
                                 "    m = m + 1;",
                                 "}"], "aux_arco")
        linhas.append("")
    linhas += [rotular("int main(void) {", "principal_main"), rotular(f"    n = {len(nomes)};", "principal_nomes")]
    pa = "    "
    if com_arestas:
        grafo = [pa + "// As arestas (u, v, peso), uma vez cada, na ordem em que foram criadas"]
        for u, v, peso in entrada["arestas"]:
            grafo.append(pa + f"aresta({numero_de[u]}, {numero_de[v]}, {peso_comum(peso)});".ljust(30) + f"// {u} - {v}")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif com_arcos:
        grafo = [pa + "// Os arcos (u, v, peso), na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)")]
        for u, v, peso in entrada["arcos"]:
            grafo.append(pa + f"arco({numero_de[u]}, {numero_de[v]}, {peso_comum(peso)});".ljust(30) + f"// {u} -> {v}")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        grafo = [pa + "// As listas de adjacência, na ordem em que a busca visita"]
        grafo += ligacoes_c("adj", nomes, numero_de, entrada["vizinhos"] if sem_pesos else entrada["com_pesos"], sem_pesos)
        linhas += rotular_todas(grafo, "principal_grafo")
        if algoritmo == algoritmos.BIDIRECIONAL:
            tras = [pa + "// adj_tras[v] = quem CHEGA em v (o lado de trás anda pelas arestas ao contrário)"]
            tras += ligacoes_c("adj_tras", nomes, numero_de, entrada["com_pesos_tras"], False)
            linhas += rotular_todas(tras, "principal_grafo_tras")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        heuristica = [pa + "// A heurística: a estimativa de cada vértice até o destino"]
        for v in nomes:
            heuristica.append(pa + f"h[{numero_de[v]}] = {peso_comum(dados['heuristica'].get(v, 0))};".ljust(26) + f"// {v}")
        linhas += rotular_todas(heuristica, "principal_h")
    origem = numero_de[entrada["origem"]]
    destino = numero_de[dados["destino"]] if dados.get("destino") is not None else "NIL"
    comentario_da_origem = f"      // {entrada['origem']}" + (f" até {dados['destino']}" if dados.get("destino") else "")
    linhas.append("")
    buscar = "principal_buscar"
    cada = "principal_cada_vertice"
    escreve = "principal_escreve_vertice"
    resposta = "principal_escreve_resposta"
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas.append(rotular(pa + f"direcionado = {str(dados['direcionado']).lower()};", "principal_criar"))
        linhas += rotular_todas([pa + "// As raízes: a origem primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "int ordem[] = {" + ", ".join(str(numero_de[v]) for v in entrada["ordem"]) + "};"],
                                "principal_ordem")
        linhas += [rotular(pa + "dfs(ordem);", buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, d = %d, f = %d, pai = %s\\n\", nomes[v], NOMES_DAS_CORES[cor[v]], d[v], f[v],",
                                 pa + "           nome(pai[v]));",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "for (int u = 0; u < n; u++) {",
                                 pa + "    for (int v = 0; v < n; v++) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        if (tipo[u][v] != NULL) {",
                                 pa + "            printf(\"aresta (%s, %s): %s\\n\", nomes[u], nomes[v], tipo[u][v]);",
                                 pa + "        }"], "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        metodo = "bfs" if algoritmo == algoritmos.LARGURA else "dijkstra"
        linhas += [rotular(pa + f"{metodo}({origem});" + comentario_da_origem, buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, d = \", nomes[v], NOMES_DAS_CORES[cor[v]]);",
                                 pa + "    escrever_numero(d[v]);",
                                 pa + "    printf(\", pai = %s\\n\", nome(pai[v]));",
                                 pa + "}"], escreve)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        linhas += [rotular(pa + f"bool resposta = bellman_ford({origem});" + comentario_da_origem, buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: d = \", nomes[v]);",
                                 pa + "    escrever_numero(d[v]);",
                                 pa + "    printf(\", pai = %s\\n\", nome(pai[v]));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + f"printf(\"resposta: %s\\n\", verdadeiro_ou_falso(resposta));      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
    elif algoritmo == algoritmos.GULOSA:
        linhas += [rotular(pa + f"bool resposta = buscar({origem}, {destino});" + comentario_da_origem, buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, pai = %s\\n\", nomes[v], NOMES_DAS_CORES[cor[v]], nome(pai[v]));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + f"printf(\"resposta: %s\\n\", verdadeiro_ou_falso(resposta));      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
    elif algoritmo == algoritmos.A_ESTRELA:
        linhas += [rotular(pa + f"bool resposta = buscar({origem}, {destino});" + comentario_da_origem, buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, g = \", nomes[v], NOMES_DAS_CORES[cor[v]]);",
                                 pa + "    escrever_numero(g[v]);",
                                 pa + "    printf(\", f = \");",
                                 pa + "    escrever_numero(f[v]);",
                                 pa + "    printf(\", pai = %s\\n\", nome(pai[v]));",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + f"printf(\"resposta: %s\\n\", verdadeiro_ou_falso(resposta));      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        chamada = f"buscar({origem}, {destino}, {dados['limite']})" if algoritmo == algoritmos.LIMITADA else \
            f"buscar({origem}, {destino})"
        linhas += rotular_todas([pa + "for (int v = 0; v < n; v++) {",
                                 pa + "    prof[v] = SEM_PROF;                     // ninguém entrou no caminho ainda",
                                 pa + "}"], "principal_criar")
        linhas += [rotular(pa + f"enum Resultado resposta = {chamada};" + comentario_da_origem, buscar),
                   rotular(pa + "const char *NOMES_DOS_RESULTADOS[] = {\"achou\", \"corte\", \"falha\"};",
                           "principal_nomes_dos_resultados"),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, pai = %s, prof = \", nomes[v], NOMES_DAS_CORES[cor[v]], nome(pai[v]));",
                                 pa + "    if (prof[v] == SEM_PROF) {",
                                 pa + "        printf(\"-\\n\");                       // nunca entrou no caminho",
                                 pa + "    } else {",
                                 pa + "        printf(\"%d\\n\", prof[v]);",
                                 pa + "    }",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "printf(\"caminho:\");",
                                 pa + "if (topo == 0) {",
                                 pa + "    printf(\" (vazio)\");",
                                 pa + "}",
                                 pa + "for (int i = 0; i < topo; i++) {",
                                 pa + "    printf(\" %s\", nomes[caminho[i]]);",
                                 pa + "}"], "principal_escreve_caminho")
        linhas += rotular_todas([pa + "printf(\"\\ncortados:\");",
                                 pa + "if (quantos_cortados == 0) {",
                                 pa + "    printf(\" (nenhum)\");",
                                 pa + "}",
                                 pa + "for (int i = 0; i < quantos_cortados; i++) {",
                                 pa + "    printf(\" %s\", nomes[cortados[i]]);",
                                 pa + "}"], "principal_escreve_cortados")
        linhas.append(rotular(pa + f"printf(\"\\nresposta: %s\\n\", NOMES_DOS_RESULTADOS[resposta]);      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
    elif algoritmo == algoritmos.PRIM:
        linhas += rotular_todas([pa + "// As raízes: a escolhida primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "int raizes[] = {" + ", ".join(str(numero_de[v]) for v in entrada["ordem"]) + "};"],
                                "principal_raizes")
        linhas += [rotular(pa + "prim(raizes);", buscar),
                   rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, chave = \", nomes[v], NOMES_DAS_CORES[cor[v]]);",
                                 pa + "    escrever_numero(chave[v]);",
                                 pa + "    printf(\", pai = %s\\n\", nome(pai[v]));"], escreve)
        linhas += [rotular(pa + "    total = total + chave[v];          // a chave é o peso da aresta por onde v entrou",
                           "principal_soma"),
                   rotular(pa + "}", cada)]
        linhas += rotular_todas([pa + "printf(\"peso total: \");",
                                 pa + "escrever_numero(total);",
                                 pa + "printf(\"\\n\");"], "principal_escreve_total")
    elif algoritmo == algoritmos.KRUSKAL:
        linhas += [rotular(pa + "kruskal();", buscar),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: conjunto = %s\\n\", nomes[v], nome(conjunto[v]));",
                                 pa + "}"], escreve)
        linhas += [rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (int i = 0; i < quantas_na_arvore; i++) {", "principal_cada_aresta")]
        linhas += rotular_todas([pa + "    printf(\"aresta da árvore: %s - %s (peso \", nomes[arvore[i].u], nomes[arvore[i].v]);",
                                 pa + "    escrever_numero(arvore[i].peso);",
                                 pa + "    printf(\")\\n\");"], "principal_escreve_aresta")
        linhas += [rotular(pa + "    total = total + arvore[i].peso;", "principal_soma"),
                   rotular(pa + "}", "principal_cada_aresta")]
        linhas += rotular_todas([pa + "printf(\"peso total: \");",
                                 pa + "escrever_numero(total);",
                                 pa + "printf(\"\\n\");"], "principal_escreve_total")
    elif algoritmo == algoritmos.BIDIRECIONAL:
        linhas += [rotular(pa + f"bool resposta = buscar({origem}, {destino});" + comentario_da_origem, buscar),
                   rotular(pa + "const char *NOMES_DOS_LADOS[] = {\"NIL\", \"frente\", \"tras\"};",
                           "principal_nomes_dos_lados"),
                   rotular(pa + "for (int v = 0; v < n; v++) {", cada)]
        linhas += rotular_todas([pa + "    printf(\"%s: cor = %s, lado = %s, d = \", nomes[v], NOMES_DAS_CORES[cor[v]], NOMES_DOS_LADOS[lado[v]]);",
                                 pa + "    escrever_numero(d[v]);",
                                 pa + "    printf(\", d' = \");",
                                 pa + "    escrever_numero(d_tras[v]);",
                                 pa + "    printf(\", pai = %s, pai' = %s\\n\", nome(pai[v]), nome(pai_tras[v]));",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "if (encontro.u != NIL) {",
                                 pa + "    printf(\"encontro: %s %s\\n\", nomes[encontro.u], nomes[encontro.v]);",
                                 pa + "}"], "principal_escreve_encontro")
        linhas.append(rotular(pa + f"printf(\"resposta: %s\\n\", verdadeiro_ou_falso(resposta));      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
    else:
        linhas.append(rotular(pa + "bool resposta = floyd_warshall();", buscar))
        linhas += rotular_todas([pa + "for (int i = 0; i < n; i++) {",
                                 pa + "    for (int j = 0; j < n; j++) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        printf(\"d(%s, %s) = \", nomes[i], nomes[j]);",
                                 pa + "        escrever_numero(d[i][j]);",
                                 pa + "        printf(\", pi(%s, %s) = %s\\n\", nomes[i], nomes[j], nome(pi[i][j]));"],
                                "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
        linhas.append(rotular(pa + f"printf(\"resposta: %s\\n\", verdadeiro_ou_falso(resposta));      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                              resposta))
        linhas += rotular_todas([pa + "for (int i = 0; i < n; i++) {        // devolve a memória das linhas das matrizes",
                                 pa + "    free(d[i]);",
                                 pa + "    free(pi[i]);",
                                 pa + "}"], "principal_liberar")
    if not com_arcos and not com_arestas:
        liberar = [pa + "for (int u = 0; u < n; u++) {        // devolve a memória das listas",
                   pa + "    liberar(adj[u]);"]
        if algoritmo == algoritmos.BIDIRECIONAL:
            liberar.append(pa + "    liberar(adj_tras[u]);")
        liberar.append(pa + "}")
        linhas += rotular_todas(liberar, "principal_liberar")
    linhas += rotular_todas([pa + "return 0;", "}"], "principal_fim")
    return linhas


def ligacoes_c(nome, nomes, numero_de, listas, sem_pesos):
    linhas = []
    for u in nomes:
        for item in listas[u]:
            if sem_pesos:
                v = item
                chamada = f"ligar({nome}, {numero_de[u]}, {numero_de[v]});"
            else:
                v, peso = item
                chamada = f"ligar({nome}, {numero_de[u]}, {numero_de[v]}, {peso_comum(peso)});"
            linhas.append("    " + chamada.ljust(34) + f"// {u} -> {v}")
    return linhas


# ----------------------------------------------------------------------
# C++
# ----------------------------------------------------------------------

def programa_cpp(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    classe = CLASSES_DO_JAVA[algoritmo]             # as classes têm o mesmo nome no C++
    nomes = entrada["nomes"]
    linhas = cabecalho_comentado(topo, "//") + [""] + codigo_de_estudo(algoritmo, "cpp")
    sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
    linhas += ["", ""] + faixa("//", "O grafo exportado pelo BoscoGraph e a chamada da busca")
    linhas += rotular_todas(["#include <cmath>", "#include <cstdio>", "#include <cstdlib>", "#include <iostream>"],
                            "estrutura_importar") + [""]
    if algoritmo not in (algoritmos.PROFUNDIDADE, algoritmos.GULOSA, algoritmos.LIMITADA, algoritmos.ITERATIVA):
        linhas += rotular_todas(["// O número como o BoscoGraph escreve: inf para o infinito, inteiros sem casas decimais e, nos",
                                 "// outros, o menor número de casas que volta exatamente ao mesmo double",
                                 "static std::string numero(double x) {",
                                 "    if (std::isinf(x)) {",
                                 "        return x > 0 ? \"inf\" : \"-inf\";",
                                 "    }",
                                 "    char texto[40];",
                                 "    if (x == std::floor(x)) {",
                                 "        std::snprintf(texto, sizeof texto, \"%.0f\", x);",
                                 "        return texto;",
                                 "    }",
                                 "    for (int casas = 1; casas <= 17; casas++) {",
                                 "        std::snprintf(texto, sizeof texto, \"%.*g\", casas, x);",
                                 "        if (std::strtod(texto, nullptr) == x) {",
                                 "            break;",
                                 "        }",
                                 "    }",
                                 "    return texto;",
                                 "}"], "aux_numero")
        linhas.append("")
    linhas += rotular_todas(["static std::string nome(const std::string &v) {",
                             "    return v.empty() ? \"NIL\" : v;                  // NIL é o texto vazio",
                             "}"], "aux_nome")
    linhas.append("")
    if algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.GULOSA, algoritmos.A_ESTRELA, algoritmos.BIDIRECIONAL,
                     algoritmos.FLOYD_WARSHALL):
        linhas += rotular_todas(["static std::string verdadeiro_ou_falso(bool resposta) {",
                                 "    return resposta ? \"VERDADEIRO\" : \"FALSO\";",
                                 "}"], "aux_verdadeiro")
        linhas.append("")
    if algoritmo not in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL, algoritmos.KRUSKAL):
        linhas += [rotular("static const char *NOMES_DAS_CORES[] = {\"Branco\", \"Cinza\", \"Preto\"};", "aux_cores"), ""]
    linhas.append(rotular("int main() {", "principal_main"))
    linhas += rotular_todas(["    // Os vértices, na ordem em que foram criados",
                             "    std::vector<std::string> nomes = {" + ", ".join(aspas(v) for v in nomes) + "};"],
                            "principal_nomes")
    pa = "    "
    if algoritmo == algoritmos.KRUSKAL:
        grafo = [pa + "// As arestas (u, v, peso), uma vez cada, na ordem em que foram criadas",
                 pa + "std::vector<Kruskal::Aresta> arestas = {"]
        itens = [pa + f"    {{{aspas(u)}, {aspas(v)}, {peso_comum(peso)}}}" for u, v, peso in entrada["arestas"]]
        grafo += juntar_com_virgulas(itens)
        grafo.append(pa + "};")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL):
        grafo = [pa + "// Os arcos (u, v, peso), na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)"),
                 pa + f"std::vector<{classe}::Arco> arcos = {{"]
        itens = [pa + f"    {{{aspas(u)}, {aspas(v)}, {peso_comum(peso)}}}" for u, v, peso in entrada["arcos"]]
        grafo += juntar_com_virgulas(itens)
        grafo.append(pa + "};")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        grafo = [pa + "// adj[u] = os vizinhos de u, na ordem em que a busca visita"
                 + ("" if sem_pesos else " (com o peso de cada aresta)")]
        grafo += mapa_cpp("adj", classe, nomes, entrada["vizinhos"] if sem_pesos else entrada["com_pesos"], sem_pesos)
        linhas += rotular_todas(grafo, "principal_grafo")
        if algoritmo == algoritmos.BIDIRECIONAL:
            tras = [pa + "// adj_tras[v] = quem CHEGA em v (o lado de trás anda pelas arestas ao contrário)"]
            tras += mapa_cpp("adj_tras", classe, nomes, entrada["com_pesos_tras"], False)
            linhas += rotular_todas(tras, "principal_grafo_tras")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        linhas += rotular_todas([pa + "// A heurística: a estimativa de cada vértice até o destino",
                                 pa + "std::map<std::string, double> h = {"
                                 + ", ".join(f"{{{aspas(v)}, {peso_comum(dados['heuristica'].get(v, 0))}}}" for v in nomes)
                                 + "};"], "principal_h")
    origem = aspas(entrada["origem"])
    destino = aspas(dados["destino"]) if dados.get("destino") is not None else f"{classe}::NIL"
    linhas.append("")
    criar = "principal_criar"
    buscar = "principal_buscar"
    cada = "principal_cada_vertice"
    escreve = "principal_escreve_vertice"
    resposta = "principal_escreve_resposta"
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas += rotular_todas([pa + "// As raízes: a origem primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "std::vector<std::string> ordem = {" + ", ".join(aspas(v) for v in entrada["ordem"]) + "};"],
                                "principal_ordem")
        linhas += [rotular(pa + f"BuscaEmProfundidade busca(adj, {str(dados['direcionado']).lower()});", criar),
                   rotular(pa + "busca.dfs(ordem);", buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", d = \" << busca.d[v]",
                                 pa + "              << \", f = \" << busca.f[v] << \", pai = \" << nome(busca.pai[v]) << \"\\n\";",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "for (const std::string &u : nomes) {",
                                 pa + "    for (const std::string &v : nomes) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        if (busca.tipo.count({u, v}) > 0) {",
                                 pa + "            std::cout << \"aresta (\" << u << \", \" << v << \"): \" << busca.tipo[{u, v}] << \"\\n\";",
                                 pa + "        }"], "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        metodo = "bfs" if algoritmo == algoritmos.LARGURA else "dijkstra"
        linhas += [rotular(pa + f"{classe} busca(adj);", criar),
                   rotular(pa + f"busca.{metodo}({origem});", buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", d = \" << numero(busca.d[v])",
                                 pa + "              << \", pai = \" << nome(busca.pai[v]) << \"\\n\";",
                                 pa + "}"], escreve)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        linhas += [rotular(pa + "BellmanFord busca(nomes, arcos);", criar),
                   rotular(pa + f"bool resposta = busca.bellman_ford({origem});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": d = \" << numero(busca.d[v]) << \", pai = \" << nome(busca.pai[v]) << \"\\n\";",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "std::cout << \"resposta: \" << verdadeiro_ou_falso(resposta) << \"\\n\";", resposta))
    elif algoritmo == algoritmos.GULOSA:
        linhas += [rotular(pa + "BuscaGulosa busca(adj, h);", criar),
                   rotular(pa + f"bool resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", pai = \" << nome(busca.pai[v])",
                                 pa + "              << \"\\n\";",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "std::cout << \"resposta: \" << verdadeiro_ou_falso(resposta) << \"\\n\";", resposta))
    elif algoritmo == algoritmos.A_ESTRELA:
        linhas += [rotular(pa + "AEstrela busca(adj, h);", criar),
                   rotular(pa + f"bool resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", g = \" << numero(busca.g[v])",
                                 pa + "              << \", f = \" << numero(busca.f[v]) << \", pai = \" << nome(busca.pai[v]) << \"\\n\";",
                                 pa + "}"], escreve)
        linhas.append(rotular(pa + "std::cout << \"resposta: \" << verdadeiro_ou_falso(resposta) << \"\\n\";", resposta))
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        if algoritmo == algoritmos.LIMITADA:
            linhas += [rotular(pa + "ProfundidadeLimitada busca(adj);", criar),
                       rotular(pa + f"int resposta = busca.buscar({origem}, {destino}, {dados['limite']});      "
                                    f"// {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        else:
            linhas += [rotular(pa + "AprofundamentoIterativo busca(adj);", criar),
                       rotular(pa + f"int resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                               buscar)]
        linhas += [rotular(pa + "const char *NOMES_DOS_RESULTADOS[] = {\"achou\", \"corte\", \"falha\"};",
                           "principal_nomes_dos_resultados"),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    // \"-\" = nunca entrou no caminho",
                                 pa + "    std::string prof = busca.prof.count(v) > 0 ? std::to_string(busca.prof[v]) : \"-\";",
                                 pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", pai = \" << nome(busca.pai[v])",
                                 pa + "              << \", prof = \" << prof << \"\\n\";",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "std::cout << \"caminho:\" << (busca.caminho.empty() ? \" (vazio)\" : \"\");",
                                 pa + "for (const std::string &v : busca.caminho) {",
                                 pa + "    std::cout << \" \" << v;",
                                 pa + "}"], "principal_escreve_caminho")
        linhas += rotular_todas([pa + "std::cout << \"\\ncortados:\" << (busca.cortados.empty() ? \" (nenhum)\" : \"\");",
                                 pa + "for (const std::string &v : busca.cortados) {",
                                 pa + "    std::cout << \" \" << v;",
                                 pa + "}"], "principal_escreve_cortados")
        linhas.append(rotular(pa + "std::cout << \"\\nresposta: \" << NOMES_DOS_RESULTADOS[resposta] << \"\\n\";", resposta))
    elif algoritmo == algoritmos.PRIM:
        linhas += rotular_todas([pa + "// As raízes: a escolhida primeiro, depois os outros vértices em ordem alfabética",
                                 pa + "std::vector<std::string> raizes = {" + ", ".join(aspas(v) for v in entrada["ordem"])
                                 + "};"], "principal_raizes")
        linhas += [rotular(pa + "Prim busca(adj);", criar),
                   rotular(pa + "busca.prim(raizes);", buscar),
                   rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", chave = \" << numero(busca.chave[v])",
                                 pa + "              << \", pai = \" << nome(busca.pai[v]) << \"\\n\";"], escreve)
        linhas += [rotular(pa + "    total = total + busca.chave[v];      // a chave é o peso da aresta por onde v entrou",
                           "principal_soma"),
                   rotular(pa + "}", cada),
                   rotular(pa + "std::cout << \"peso total: \" << numero(total) << \"\\n\";", "principal_escreve_total")]
    elif algoritmo == algoritmos.KRUSKAL:
        linhas += [rotular(pa + "Kruskal busca(nomes, arestas);", criar),
                   rotular(pa + "busca.kruskal();", buscar),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": conjunto = \" << nome(busca.conjunto[v]) << \"\\n\";",
                                 pa + "}"], escreve)
        linhas += [rotular(pa + "double total = 0;", "principal_total"),
                   rotular(pa + "for (const Kruskal::Aresta &aresta : busca.arvore) {", "principal_cada_aresta")]
        linhas += rotular_todas([pa + "    std::cout << \"aresta da árvore: \" << aresta.u << \" - \" << aresta.v << \" (peso \"",
                                 pa + "              << numero(aresta.peso) << \")\\n\";"], "principal_escreve_aresta")
        linhas += [rotular(pa + "    total = total + aresta.peso;", "principal_soma"),
                   rotular(pa + "}", "principal_cada_aresta"),
                   rotular(pa + "std::cout << \"peso total: \" << numero(total) << \"\\n\";", "principal_escreve_total")]
    elif algoritmo == algoritmos.BIDIRECIONAL:
        linhas += [rotular(pa + "BuscaBidirecional busca(adj, adj_tras);", criar),
                   rotular(pa + f"bool resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular(pa + "const char *NOMES_DOS_LADOS[] = {\"NIL\", \"frente\", \"tras\"};",
                           "principal_nomes_dos_lados"),
                   rotular(pa + "for (const std::string &v : nomes) {", cada)]
        linhas += rotular_todas([pa + "    std::cout << v << \": cor = \" << NOMES_DAS_CORES[busca.cor[v]] << \", lado = \" << NOMES_DOS_LADOS[busca.lado[v]]",
                                 pa + "              << \", d = \" << numero(busca.d[v]) << \", d' = \" << numero(busca.d_tras[v])",
                                 pa + "              << \", pai = \" << nome(busca.pai[v]) << \", pai' = \" << nome(busca.pai_tras[v]) << \"\\n\";",
                                 pa + "}"], escreve)
        linhas += rotular_todas([pa + "if (!busca.encontro.first.empty()) {",
                                 pa + "    std::cout << \"encontro: \" << busca.encontro.first << \" \" << busca.encontro.second << \"\\n\";",
                                 pa + "}"], "principal_escreve_encontro")
        linhas.append(rotular(pa + "std::cout << \"resposta: \" << verdadeiro_ou_falso(resposta) << \"\\n\";", resposta))
    else:
        linhas += [rotular(pa + "FloydWarshall busca(nomes, arcos);", criar),
                   rotular(pa + f"bool resposta = busca.floyd_warshall();      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar)]
        linhas += rotular_todas([pa + "for (const std::string &i : nomes) {",
                                 pa + "    for (const std::string &j : nomes) {"], "principal_cada_par")
        linhas += rotular_todas([pa + "        std::cout << \"d(\" << i << \", \" << j << \") = \" << numero(busca.d[i][j]) << \", pi(\" << i",
                                 pa + "                  << \", \" << j << \") = \" << nome(busca.pi[i][j]) << \"\\n\";"],
                                "principal_escreve_par")
        linhas += rotular_todas([pa + "    }",
                                 pa + "}"], "principal_cada_par")
        linhas.append(rotular(pa + "std::cout << \"resposta: \" << verdadeiro_ou_falso(resposta) << \"\\n\";", resposta))
    linhas += rotular_todas([pa + "return 0;", "}"], "principal_fim")
    return linhas


def mapa_cpp(nome, classe, nomes, listas, sem_pesos):
    if sem_pesos:
        linhas = [f"    std::map<std::string, std::vector<std::string>> {nome};"]
    else:
        linhas = [f"    std::map<std::string, std::vector<{classe}::Vizinho>> {nome};"]
    for u in nomes:
        if sem_pesos:
            itens = ", ".join(aspas(v) for v in listas[u])
        else:
            itens = ", ".join(f"{{{aspas(v)}, {peso_comum(peso)}}}" for v, peso in listas[u])
        linhas.append(f"    {nome}[{aspas(u)}] = {{{itens}}};")
    return linhas


# ----------------------------------------------------------------------
# JavaScript
# ----------------------------------------------------------------------

def programa_javascript(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    classe = CLASSES_DO_JAVA[algoritmo]
    nomes = entrada["nomes"]
    estudo_js = []
    for linha in codigo_de_estudo(algoritmo, "javascript"):
        if not linha.startswith("module.exports"):      # num arquivo só, não precisa exportar a classe
            estudo_js.append(linha)
    while estudo_js and estudo_js[-1] == "":
        estudo_js.pop()
    linhas = cabecalho_comentado(topo, "//") + [""] + estudo_js
    sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
    linhas += [""] + faixa("//", "O grafo exportado pelo BoscoGraph e a chamada da busca") + [""]
    linhas += rotular_todas(["// O número como o BoscoGraph escreve: inf para o infinito e inteiros sem casas decimais",
                             "function numero(x) {",
                             "    if (x === Infinity) {",
                             "        return \"inf\";",
                             "    }",
                             "    if (x === -Infinity) {",
                             "        return \"-inf\";",
                             "    }",
                             "    return String(x);",
                             "}"], "aux_numero")
    linhas.append("")
    linhas += [rotular("const nome = (v) => (v === null || v === undefined ? \"NIL\" : v);", "aux_nome"),
               rotular("const verdadeiroOuFalso = (resposta) => (resposta ? \"VERDADEIRO\" : \"FALSO\");",
                       "aux_verdadeiro"),
               ""]
    linhas += rotular_todas(["// Os vértices, na ordem em que foram criados",
                             "const nomes = [" + ", ".join(aspas(v) for v in nomes) + "];"], "principal_nomes")
    if algoritmo == algoritmos.KRUSKAL:
        grafo = ["// As arestas [u, v, peso], uma vez cada, na ordem em que foram criadas", "const arestas = ["]
        for u, v, peso in entrada["arestas"]:
            grafo.append(f"    [{aspas(u)}, {aspas(v)}, {peso_comum(peso)}],")
        grafo.append("];")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL):
        grafo = ["// Os arcos [u, v, peso], na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)"),
                 "const arcos = ["]
        for u, v, peso in entrada["arcos"]:
            grafo.append(f"    [{aspas(u)}, {aspas(v)}, {peso_comum(peso)}],")
        grafo.append("];")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        grafo = ["// adj.get(u) = os vizinhos de u, na ordem em que a busca visita"
                 + ("" if sem_pesos else " (cada um com o peso da aresta: [vizinho, peso])")]
        grafo += mapa_javascript("adj", nomes, entrada["vizinhos"] if sem_pesos else entrada["com_pesos"], sem_pesos)
        linhas += rotular_todas(grafo, "principal_grafo")
        if algoritmo == algoritmos.BIDIRECIONAL:
            tras = ["// adjTras.get(v) = quem CHEGA em v (o lado de trás anda pelas arestas ao contrário)"]
            tras += mapa_javascript("adjTras", nomes, entrada["com_pesos_tras"], False)
            linhas += rotular_todas(tras, "principal_grafo_tras")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        linhas += rotular_todas(["// A heurística: a estimativa de cada vértice até o destino",
                                 "const h = new Map([" + ", ".join(f"[{aspas(v)}, {peso_comum(dados['heuristica'].get(v, 0))}]"
                                                                  for v in nomes) + "]);"], "principal_h")
    origem = aspas(entrada["origem"])
    destino = aspas(dados["destino"]) if dados.get("destino") is not None else "null"
    linhas.append("")
    criar = "principal_criar"
    buscar = "principal_buscar"
    cada = "principal_cada_vertice"
    escreve = "principal_escreve_vertice"
    resposta = "principal_escreve_resposta"
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas += rotular_todas(["// As raízes: a origem primeiro, depois os outros vértices em ordem alfabética",
                                 "const ordem = [" + ", ".join(aspas(v) for v in entrada["ordem"]) + "];"],
                                "principal_ordem")
        linhas += [rotular(f"const busca = new BuscaEmProfundidade(adj, {str(dados['direcionado']).lower()});", criar),
                   rotular("busca.dfs(ordem);", buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: cor = ${busca.cor.get(v)}, d = ${busca.d.get(v)}, f = ${busca.f.get(v)}, "
                                 "pai = ${nome(busca.pai.get(v))}`);",
                                 "}"], escreve)
        linhas += rotular_todas(["for (const u of nomes) {",
                                 "    for (const v of nomes) {"], "principal_cada_par")
        linhas += rotular_todas(["        const tipo = busca.tipo.get(JSON.stringify([u, v]));      // a chave do par é o texto [u, v]",
                                 "        if (tipo !== undefined) {",
                                 "            console.log(`aresta (${u}, ${v}): ${tipo}`);",
                                 "        }"], "principal_escreve_par")
        linhas += rotular_todas(["    }",
                                 "}"], "principal_cada_par")
    elif algoritmo in (algoritmos.LARGURA, algoritmos.DIJKSTRA):
        metodo = "bfs" if algoritmo == algoritmos.LARGURA else "dijkstra"
        linhas += [rotular(f"const busca = new {classe}(adj);", criar),
                   rotular(f"busca.{metodo}({origem});", buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: cor = ${busca.cor.get(v)}, d = ${numero(busca.d.get(v))}, pai = ${nome(busca.pai.get(v))}`);",
                                 "}"], escreve)
    elif algoritmo == algoritmos.BELLMAN_FORD:
        linhas += [rotular("const busca = new BellmanFord(nomes, arcos);", criar),
                   rotular(f"const resposta = busca.bellmanFord({origem});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: d = ${numero(busca.d.get(v))}, pai = ${nome(busca.pai.get(v))}`);",
                                 "}"], escreve)
        linhas.append(rotular("console.log(`resposta: ${verdadeiroOuFalso(resposta)}`);", resposta))
    elif algoritmo == algoritmos.GULOSA:
        linhas += [rotular("const busca = new BuscaGulosa(adj, h);", criar),
                   rotular(f"const resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: cor = ${busca.cor.get(v)}, pai = ${nome(busca.pai.get(v))}`);",
                                 "}"], escreve)
        linhas.append(rotular("console.log(`resposta: ${verdadeiroOuFalso(resposta)}`);", resposta))
    elif algoritmo == algoritmos.A_ESTRELA:
        linhas += [rotular("const busca = new AEstrela(adj, h);", criar),
                   rotular(f"const resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: cor = ${busca.cor.get(v)}, g = ${numero(busca.g.get(v))}, f = ${numero(busca.f.get(v))}, "
                                 "pai = ${nome(busca.pai.get(v))}`);",
                                 "}"], escreve)
        linhas.append(rotular("console.log(`resposta: ${verdadeiroOuFalso(resposta)}`);", resposta))
    elif algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        if algoritmo == algoritmos.LIMITADA:
            linhas += [rotular("const busca = new ProfundidadeLimitada(adj);", criar),
                       rotular(f"const resposta = busca.buscar({origem}, {destino}, {dados['limite']});      "
                               f"// {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        else:
            linhas += [rotular("const busca = new AprofundamentoIterativo(adj);", criar),
                       rotular(f"const resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                               buscar)]
        linhas.append(rotular("for (const v of nomes) {", cada))
        linhas += rotular_todas(["    const prof = busca.prof.has(v) ? busca.prof.get(v) : \"-\";      // \"-\" = nunca entrou no caminho",
                                 "    console.log(`${v}: cor = ${busca.cor.get(v)}, pai = ${nome(busca.pai.get(v))}, prof = ${prof}`);",
                                 "}"], escreve)
        linhas += [rotular("console.log(`caminho: ${busca.caminho.length > 0 ? busca.caminho.join(\" \") : \"(vazio)\"}`);",
                           "principal_escreve_caminho"),
                   rotular("console.log(`cortados: ${busca.cortados.length > 0 ? busca.cortados.join(\" \") : \"(nenhum)\"}`);",
                           "principal_escreve_cortados"),
                   rotular("console.log(`resposta: ${resposta}`);", resposta)]
    elif algoritmo == algoritmos.PRIM:
        linhas += rotular_todas(["// As raízes: a escolhida primeiro, depois os outros vértices em ordem alfabética",
                                 "const raizes = [" + ", ".join(aspas(v) for v in entrada["ordem"]) + "];"],
                                "principal_raizes")
        linhas += [rotular("const busca = new Prim(adj);", criar),
                   rotular("busca.prim(raizes);", buscar),
                   rotular("let total = 0;", "principal_total"),
                   rotular("for (const v of nomes) {", cada),
                   rotular("    console.log(`${v}: cor = ${busca.cor.get(v)}, chave = ${numero(busca.chave.get(v))}, "
                           "pai = ${nome(busca.pai.get(v))}`);", escreve),
                   rotular("    total = total + busca.chave.get(v);      // a chave é o peso da aresta por onde v entrou",
                           "principal_soma"),
                   rotular("}", cada),
                   rotular("console.log(`peso total: ${numero(total)}`);", "principal_escreve_total")]
    elif algoritmo == algoritmos.KRUSKAL:
        linhas += [rotular("const busca = new Kruskal(nomes, arestas);", criar),
                   rotular("busca.kruskal();", buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: conjunto = ${nome(busca.conjunto.get(v))}`);",
                                 "}"], escreve)
        linhas += [rotular("let total = 0;", "principal_total"),
                   rotular("for (const [u, v, peso] of busca.arvore) {", "principal_cada_aresta"),
                   rotular("    console.log(`aresta da árvore: ${u} - ${v} (peso ${numero(peso)})`);",
                           "principal_escreve_aresta"),
                   rotular("    total = total + peso;", "principal_soma"),
                   rotular("}", "principal_cada_aresta"),
                   rotular("console.log(`peso total: ${numero(total)}`);", "principal_escreve_total")]
    elif algoritmo == algoritmos.BIDIRECIONAL:
        linhas += [rotular("const busca = new BuscaBidirecional(adj, adjTras);", criar),
                   rotular(f"const resposta = busca.buscar({origem}, {destino});      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}",
                           buscar),
                   rotular("for (const v of nomes) {", cada)]
        linhas += rotular_todas(["    console.log(`${v}: cor = ${busca.cor.get(v)}, lado = ${nome(busca.lado.get(v))}, d = ${numero(busca.d.get(v))}, `",
                                 "        + `d' = ${numero(busca.dTras.get(v))}, pai = ${nome(busca.pai.get(v))}, pai' = ${nome(busca.paiTras.get(v))}`);",
                                 "}"], escreve)
        linhas += rotular_todas(["if (busca.encontro !== null) {",
                                 "    console.log(`encontro: ${busca.encontro[0]} ${busca.encontro[1]}`);",
                                 "}"], "principal_escreve_encontro")
        linhas.append(rotular("console.log(`resposta: ${verdadeiroOuFalso(resposta)}`);", resposta))
    else:
        linhas += [rotular("const busca = new FloydWarshall(nomes, arcos);", criar),
                   rotular(f"const resposta = busca.floydWarshall();      // {SIGNIFICADO_DA_RESPOSTA[algoritmo]}", buscar)]
        linhas += rotular_todas(["for (const i of nomes) {",
                                 "    for (const j of nomes) {"], "principal_cada_par")
        linhas.append(rotular("        console.log(`d(${i}, ${j}) = ${numero(busca.d.get(i).get(j))}, pi(${i}, ${j}) = ${nome(busca.pi.get(i).get(j))}`);",
                              "principal_escreve_par"))
        linhas += rotular_todas(["    }",
                                 "}"], "principal_cada_par")
        linhas.append(rotular("console.log(`resposta: ${verdadeiroOuFalso(resposta)}`);", resposta))
    return linhas


def mapa_javascript(nome, nomes, listas, sem_pesos):
    linhas = [f"const {nome} = new Map(["]
    for u in nomes:
        if sem_pesos:
            itens = ", ".join(aspas(v) for v in listas[u])
        else:
            itens = ", ".join(f"[{aspas(v)}, {peso_comum(peso)}]" for v, peso in listas[u])
        linhas.append(f"    [{aspas(u)}, [{itens}]],")
    linhas.append("]);")
    return linhas


# ----------------------------------------------------------------------
# Pseudocódigo (texto)
# ----------------------------------------------------------------------

def texto_do_pseudocodigo(dados, entrada, topo):
    algoritmo = dados["algoritmo"]
    nomes = entrada["nomes"]
    linhas = cabecalho_comentado(topo, "") + ["", rotular("PSEUDOCÓDIGO", "principal_titulo_do_estudo"), ""]
    linhas += codigo_de_estudo(algoritmo, "pseudocodigo")
    linhas += ["", rotular("O GRAFO", "principal_titulo"), "", rotular("Vértices: " + ", ".join(nomes), "principal_nomes")]
    if algoritmo == algoritmos.KRUSKAL:
        grafo = ["Arestas (u, v, w), uma vez cada, na ordem em que foram criadas:"]
        for u, v, peso in entrada["arestas"]:
            grafo.append(f"    ({u}, {v}, {peso_comum(peso)})")
        if not entrada["arestas"]:
            grafo.append("    (nenhuma)")
        linhas += rotular_todas(grafo, "principal_grafo")
    elif algoritmo in (algoritmos.BELLMAN_FORD, algoritmos.FLOYD_WARSHALL):
        grafo = ["Arcos (u, v, w), na ordem em que as arestas foram criadas"
                 + ("" if dados["direcionado"] else " (não orientado: cada aresta nos dois sentidos)") + ":"]
        for u, v, peso in entrada["arcos"]:
            grafo.append(f"    ({u}, {v}, {peso_comum(peso)})")
        if not entrada["arcos"]:
            grafo.append("    (nenhum)")
        linhas += rotular_todas(grafo, "principal_grafo")
    else:
        sem_pesos = algoritmo in (algoritmos.PROFUNDIDADE, algoritmos.LIMITADA, algoritmos.ITERATIVA)
        grafo = ["Listas de adjacência, na ordem em que a busca visita:"]
        for u in nomes:
            if sem_pesos:
                itens = ", ".join(entrada["vizinhos"][u])
            else:
                itens = ", ".join(f"{v} ({peso_comum(peso)})" if peso is not None else v
                                  for v, peso in entrada["com_pesos"][u])
            grafo.append(f"    Adj[{u}] = {itens or '(vazia)'}")
        linhas += rotular_todas(grafo, "principal_grafo")
    if algoritmo in (algoritmos.GULOSA, algoritmos.A_ESTRELA):
        linhas.append(rotular("Heurística: " + ", ".join(f"h({v}) = {peso_comum(dados['heuristica'].get(v, 0))}"
                                                         for v in nomes), "principal_h"))
    if algoritmo == algoritmos.PROFUNDIDADE:
        linhas.append(rotular("Raízes, nesta ordem: " + ", ".join(entrada["ordem"]), "principal_ordem"))
    if algoritmo == algoritmos.PRIM:
        linhas.append(rotular("Raízes, nesta ordem (uma árvore nova só começa em quem ainda estiver fora): "
                              + ", ".join(entrada["ordem"]), "principal_raizes"))
    if algoritmo in SIGNIFICADO_DA_RESPOSTA:
        linhas.append(rotular("A resposta: " + SIGNIFICADO_DA_RESPOSTA[algoritmo] + ".", "principal_escreve_resposta"))
    return linhas


GERADORES.update({"python": programa_python, "java": programa_java, "c": programa_c, "cpp": programa_cpp,
                  "javascript": programa_javascript, "pseudocodigo": texto_do_pseudocodigo})
