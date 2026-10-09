'''
    Código de estudo: cada busca escrita do jeito do livro (CLRS), em seis linguagens, para ler,
    seguir linha a linha e comparar.

    Por que existe, se o programa já mostra o código dele? O código do BoscoGraph (classes/) faz a busca
    E anota cada passo para a tela; as anotações atrapalham quem quer só entender o algoritmo. O código
    de estudo é o algoritmo sozinho. O Python de estudo também RODA: no modo "linha a linha", ele é
    executado de verdade, linha por linha (veja estudo/rastreador.py). As outras linguagens são
    traduções fiéis dele, conferidas pelos testes (compilam e dão o mesmo resultado).

    Os RÓTULOS de linha. Cada linha que faz alguma coisa termina com um comentário-rótulo:
        self.cor[u] = CINZA                             # @descobrir        (Python)
        cor.put(u, CINZA);                              // @descobrir       (Java, C, C++, JavaScript...)
    O mesmo rótulo marca a linha que faz a mesma coisa em todas as linguagens. Assim, quando o Python
    está na linha "@descobrir", a tela destaca a linha "@descobrir" do Java, do C... Alguns rótulos têm
    o nome de um passo da busca ("descobrir", "relaxar_melhorou"...): é a linha que o passo destaca.
    Na tela, os rótulos não aparecem (são tirados ao carregar o arquivo).

    Este arquivo não usa Tkinter.
'''

import re

import algoritmos
import caminhos

PASTA_DO_ESTUDO = caminhos.pasta_dos_recursos() / "estudo"

# As linguagens, na ordem dos botões. "comentario" = o que começa um comentário (e o rótulo);
# "palavras" = as palavras reservadas (para colorir); "aspas" = os delimitadores de texto.
LINGUAGENS = [
    {"chave": "pseudocodigo", "nome": "Pseudocódigo", "comentario": "//",
     "palavras": ["para", "cada", "em", "se", "senão", "enquanto", "devolva", "faça", "até", "e", "ou",
                  "não", "NIL", "VERDADEIRO", "FALSO", "de"],
     "aspas": '"'},
    {"chave": "python", "nome": "Python", "comentario": "#",
     "palavras": ["def", "class", "for", "in", "if", "elif", "else", "return", "import", "from", "while",
                  "and", "or", "not", "None", "True", "False", "break", "continue", "self"],
     "aspas": "\"'"},
    {"chave": "java", "nome": "Java", "comentario": "//",
     "palavras": ["class", "public", "private", "static", "final", "void", "int", "double", "boolean",
                  "String", "new", "for", "while", "if", "else", "return", "break", "continue", "null",
                  "true", "false", "this", "import"],
     "aspas": "\"'"},
    {"chave": "c", "nome": "C", "comentario": "//",
     "palavras": ["int", "double", "char", "void", "for", "while", "if", "else", "return", "break",
                  "continue", "const", "static", "struct", "#include", "#define", "bool", "true", "false"],
     "aspas": "\"'"},
    {"chave": "cpp", "nome": "C++", "comentario": "//",
     "palavras": ["class", "public", "private", "struct", "const", "auto", "int", "double", "bool", "void",
                  "string", "for", "while", "if", "else", "return", "break", "continue", "true", "false",
                  "this", "#include", "using", "namespace", "std"],
     "aspas": "\"'"},
    {"chave": "javascript", "nome": "JavaScript", "comentario": "//",
     "palavras": ["class", "constructor", "const", "let", "new", "for", "of", "while", "if", "else",
                  "return", "break", "continue", "null", "true", "false", "this", "function"],
     "aspas": "\"'`"},
]

# O arquivo de cada busca em cada linguagem (dentro de estudo/<linguagem>/)
ARQUIVOS = {
    algoritmos.PROFUNDIDADE: {"pseudocodigo": "profundidade.txt", "python": "profundidade.py",
                              "java": "BuscaEmProfundidade.java", "c": "profundidade.c",
                              "cpp": "profundidade.cpp", "javascript": "profundidade.js"},
    algoritmos.LARGURA: {"pseudocodigo": "largura.txt", "python": "largura.py",
                         "java": "BuscaEmLargura.java", "c": "largura.c",
                         "cpp": "largura.cpp", "javascript": "largura.js"},
    algoritmos.DIJKSTRA: {"pseudocodigo": "dijkstra.txt", "python": "dijkstra.py",
                          "java": "Dijkstra.java", "c": "dijkstra.c",
                          "cpp": "dijkstra.cpp", "javascript": "dijkstra.js"},
    algoritmos.BELLMAN_FORD: {"pseudocodigo": "bellman_ford.txt", "python": "bellman_ford.py",
                              "java": "BellmanFord.java", "c": "bellman_ford.c",
                              "cpp": "bellman_ford.cpp", "javascript": "bellman_ford.js"},
    algoritmos.GULOSA: {"pseudocodigo": "gulosa.txt", "python": "gulosa.py",
                        "java": "BuscaGulosa.java", "c": "gulosa.c",
                        "cpp": "gulosa.cpp", "javascript": "gulosa.js"},
    algoritmos.A_ESTRELA: {"pseudocodigo": "a_estrela.txt", "python": "a_estrela.py",
                           "java": "AEstrela.java", "c": "a_estrela.c",
                           "cpp": "a_estrela.cpp", "javascript": "a_estrela.js"},
    algoritmos.LIMITADA: {"pseudocodigo": "limitada.txt", "python": "limitada.py",
                          "java": "ProfundidadeLimitada.java", "c": "limitada.c",
                          "cpp": "limitada.cpp", "javascript": "limitada.js"},
    algoritmos.ITERATIVA: {"pseudocodigo": "iterativa.txt", "python": "iterativa.py",
                           "java": "AprofundamentoIterativo.java", "c": "iterativa.c",
                           "cpp": "iterativa.cpp", "javascript": "iterativa.js"},
    algoritmos.BIDIRECIONAL: {"pseudocodigo": "bidirecional.txt", "python": "bidirecional.py",
                              "java": "BuscaBidirecional.java", "c": "bidirecional.c",
                              "cpp": "bidirecional.cpp", "javascript": "bidirecional.js"},
    algoritmos.FLOYD_WARSHALL: {"pseudocodigo": "floyd_warshall.txt", "python": "floyd_warshall.py",
                                "java": "FloydWarshall.java", "c": "floyd_warshall.c",
                                "cpp": "floyd_warshall.cpp", "javascript": "floyd_warshall.js"},
    algoritmos.PRIM: {"pseudocodigo": "prim.txt", "python": "prim.py", "java": "Prim.java", "c": "prim.c",
                      "cpp": "prim.cpp", "javascript": "prim.js"},
    algoritmos.KRUSKAL: {"pseudocodigo": "kruskal.txt", "python": "kruskal.py", "java": "Kruskal.java",
                         "c": "kruskal.c", "cpp": "kruskal.cpp", "javascript": "kruskal.js"},
}


def linguagem(chave):
    for informacoes in LINGUAGENS:
        if informacoes["chave"] == chave:
            return informacoes
    raise ValueError(f"Linguagem desconhecida: {chave}")


def caminho_do_arquivo(algoritmo, chave_da_linguagem):
    return PASTA_DO_ESTUDO / chave_da_linguagem / ARQUIVOS[algoritmo][chave_da_linguagem]


# O rótulo no fim de uma linha: o comentário, um @ e o nome (letras minúsculas, algarismos e _),
# e mais nada até o fim da linha. Devolve (a linha sem o rótulo, o rótulo) ou (a linha, None).
def separar_rotulo(linha, comentario):
    achado = re.search(r"\s*" + re.escape(comentario) + r"\s*@([a-z0-9_]+)\s*$", linha)
    if achado is None:
        return linha.rstrip(), None
    return linha[:achado.start()].rstrip(), achado.group(1)


# Lê o arquivo de estudo de uma busca numa linguagem. Devolve:
#   "linhas"          -> as linhas como aparecem na tela (sem os rótulos)
#   "texto_original"  -> o arquivo como está no disco (é o que o Python executa)
#   "rotulo_da_linha" -> {número da linha (a 1ª é 1): rótulo}
#   "linhas_do_rotulo"-> {rótulo: [números das linhas]}
def carregar(algoritmo, chave_da_linguagem):
    caminho = caminho_do_arquivo(algoritmo, chave_da_linguagem)
    texto = caminho.read_text(encoding="utf-8")
    comentario = linguagem(chave_da_linguagem)["comentario"]
    linhas = []
    rotulo_da_linha = {}
    linhas_do_rotulo = {}
    numero = 0
    for linha in texto.split("\n"):
        numero += 1
        limpa, rotulo = separar_rotulo(linha, comentario)
        linhas.append(limpa)
        if rotulo is not None:
            rotulo_da_linha[numero] = rotulo
            linhas_do_rotulo.setdefault(rotulo, []).append(numero)
    while linhas and linhas[-1] == "":          # sem linhas vazias sobrando no fim
        linhas.pop()
    return {"caminho": caminho, "linhas": linhas, "texto_original": texto, "rotulo_da_linha": rotulo_da_linha,
            "linhas_do_rotulo": linhas_do_rotulo}
