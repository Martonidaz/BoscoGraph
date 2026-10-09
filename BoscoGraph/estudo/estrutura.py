'''
    Os rótulos da ESTRUTURA do programa: as linhas que não são passos da busca, mas que todo programa
    tem (importar, constantes, a classe, o construtor, os campos do objeto, as funções).

    O código de estudo só rotula as linhas da busca ("@descobrir", "@relaxar_melhorou"...). No modo
    linha a linha, o Python roda o programa INTEIRO, desde a primeira linha: quando ele estiver em
    "class Dijkstra:" ou em "self.cor = {}", as outras linguagens também precisam saber qual linha
    destacar. Aqui cada linha dessas ganha um rótulo automático, achado pelo jeito da linha:

        estrutura_importar         from decimal import Decimal | import java.util.Map; | #include <math.h>
        estrutura_constante_<nome> BRANCO = "Branco" | static final String BRANCO = ... | enum Cor { BRANCO, ... }
        estrutura_classe           class Dijkstra: | public class Dijkstra { | class Dijkstra {
        estrutura_construtor       def __init__(self, adj): | public Dijkstra(...) { | constructor(adj) {
        estrutura_campo_<nome>     self.cor = {} | final Map<String, String> cor = ...; | enum Cor cor[MAX];
        estrutura_def_<nome>       def relaxar(self, u, v, peso): | void relaxar(...) { | RELAXAR(u, v, w)
        estrutura_registro         record Vizinho(...) | typedef struct Vizinho { ... } (o Python usa tuplas)
        estrutura_prototipo        void relaxar(int u, int v, double peso);   (só o C anuncia as funções)

    O <nome> é "normalizado": minúsculas, sem _ nem - nem acento. Assim extrair_minimo (Python),
    extrairMinimo (Java) e EXTRAIR-MÍNIMO (pseudocódigo) viram todos "extrairminimo"; d_tras (Python) e
    dTras (Java) viram "dtras".
    Uma linha pode ter mais de um rótulo: a do Java "static final String BRANCO = ..., CINZA = ..., PRETO = ..."
    tem três (é a linha das três constantes do Python).
    Este arquivo não usa Tkinter.
'''

import re
import unicodedata

LINGUAGENS_COM_CHAVES = ("java", "c", "cpp", "javascript")      # as que usam { } nos blocos
PALAVRAS_DE_CONTROLE = ("if", "for", "while", "switch", "return", "catch", "else")


# minúsculas, sem _, - e acentos: "extrair_minimo", "extrairMinimo" e "EXTRAIR-MÍNIMO" -> "extrairminimo"
def normalizar(nome):
    sem_acento = ""
    for letra in unicodedata.normalize("NFD", nome):
        if unicodedata.category(letra) != "Mn":        # Mn = os acentos, que o NFD separou da letra
            sem_acento += letra
    return sem_acento.lower().replace("_", "").replace("-", "")


# A linha sem o comentário do fim (fora de aspas) e sem os espaços das pontas
def sem_comentario(linha, marcador):
    dentro = None
    i = 0
    while i < len(linha):
        caractere = linha[i]
        if dentro is not None:
            if caractere == "\\":
                i += 2
                continue
            if caractere == dentro:
                dentro = None
        elif caractere in "\"'`":
            dentro = caractere
        elif marcador and linha.startswith(marcador, i):
            return linha[:i].strip()
        i += 1
    return linha.strip()


# Em quantas chaves { } cada linha está, contando do começo dela (as chaves dentro de aspas e de
# comentários não contam). Ex.: no Java, os campos e os métodos da classe estão na profundidade 1.
def profundidades(linhas):
    resultado = []
    profundidade = 0
    for linha in linhas:
        resultado.append(profundidade)
        dentro = None
        i = 0
        while i < len(linha):
            caractere = linha[i]
            if dentro is not None:
                if caractere == "\\":
                    i += 2
                    continue
                if caractere == dentro:
                    dentro = None
            elif linha.startswith("//", i):
                break
            elif caractere in "\"'`":
                dentro = caractere
            elif caractere == "{":
                profundidade += 1
            elif caractere == "}":
                profundidade -= 1
            i += 1
    return resultado


# O nome declarado numa linha como "final Map<String, String> cor = new HashMap<>();" ou
# "Vizinho *adj[MAX];" (cor, adj), ou None se a linha não é uma declaração
def nome_declarado(codigo):
    if not codigo.endswith(";"):
        return None
    corpo = codigo[:-1]
    if "=" in corpo:
        corpo = corpo.split("=", 1)[0]
    corpo = corpo.strip()
    if "(" in corpo or corpo.startswith("return") or corpo.startswith("this."):
        return None
    corpo = re.sub(r"(\[[^\]]*\])+$", "", corpo).strip()          # tira os colchetes do fim: adj[MAX]
    achado = re.search(r"([A-Za-z_]\w*)$", corpo)
    if achado is None or achado.group(1) == corpo:
        return None                                                 # só um nome, sem o tipo antes
    return achado.group(1)


# As constantes de uma linha: BRANCO, CINZA... (os nomes em maiúsculas seguidos de "=")
def constantes_da_linha(codigo):
    return re.findall(r"\b([A-Z][A-Z0-9_]*)\s*=(?!=)", codigo)


def rotulo_de_constante(nome):
    return "estrutura_constante_" + normalizar(nome)


def rotulo_de_campo(nome):
    return "estrutura_campo_" + normalizar(nome)


def rotulo_de_funcao(nome):
    return "estrutura_def_" + normalizar(nome)


# ----------------------------------------------------------------------
# Cada linguagem
# ----------------------------------------------------------------------

def estrutura_do_python(linhas, rotulados):
    extras = {}
    dentro_do_init = False
    for numero in range(1, len(linhas) + 1):
        linha = linhas[numero - 1]
        codigo = sem_comentario(linha, "#")
        recuo = len(linha) - len(linha.lstrip())
        if re.match(r"\s*def\s", linha):
            dentro_do_init = re.match(r"\s*def\s+__init__\s*\(", linha) is not None
        elif codigo and recuo == 0:
            dentro_do_init = False
        if numero in rotulados or not codigo:
            continue
        rotulos = []
        if re.match(r"(from\s+\S+\s+)?import\s", codigo):
            rotulos.append("estrutura_importar")
        elif recuo == 0 and re.match(r"[A-Z][A-Z0-9_]*\s*=", codigo):
            rotulos.append(rotulo_de_constante(codigo.split("=")[0].strip()))
        elif re.match(r"class\s+\w+", codigo):
            rotulos.append("estrutura_classe")
        elif re.match(r"def\s+__init__\s*\(", codigo):
            rotulos.append("estrutura_construtor")
        elif re.match(r"def\s+(\w+)\s*\(", codigo):
            rotulos.append(rotulo_de_funcao(re.match(r"def\s+(\w+)", codigo).group(1)))
        elif dentro_do_init and re.match(r"self\.(\w+)\s*=", codigo):
            rotulos.append(rotulo_de_campo(re.match(r"self\.(\w+)", codigo).group(1)))
        if rotulos:
            extras[numero] = rotulos
    return extras


# Java, C++ e JavaScript: classe, construtor, campos e métodos (os membros ficam na profundidade 1)
def estrutura_com_classes(linhas, rotulados, linguagem):
    extras = {}
    profundidade = profundidades(linhas)
    classe = None                       # o nome da classe de agora
    no_construtor = False               # entre o construtor e o fim dele (os "this.x = ..." são campos)
    no_registro = None                  # a profundidade em que começou um struct (o corpo dele também é registro)
    construtor_aberto = False           # o construtor do C++ que continua na linha de baixo ": adj(adj) {}"
    for numero in range(1, len(linhas) + 1):
        linha = linhas[numero - 1]
        codigo = sem_comentario(linha, "//")
        nivel = profundidade[numero - 1]
        rotulos = []
        if no_construtor and nivel <= 1 and not codigo.startswith("}"):
            no_construtor = False
        if no_registro is not None:
            if nivel > no_registro or codigo.startswith("}"):
                rotulos.append("estrutura_registro")
            if codigo.startswith("}") and nivel == no_registro + 1:
                no_registro = None
        elif not codigo:
            pass
        elif re.match(r"(import\s|#include|using\s)", codigo) or re.search(r"=\s*require\(", codigo):
            rotulos.append("estrutura_importar")
        elif nivel == 0 and re.match(r"(public\s+|final\s+|abstract\s+)*class\s+(\w+)", codigo):
            classe = re.match(r"(public\s+|final\s+|abstract\s+)*class\s+(\w+)", codigo).group(2)
            rotulos.append("estrutura_classe")
        elif nivel == 0 and linguagem == "javascript" and re.match(r"const\s+[A-Z][A-Z0-9_]*\s*=", codigo):
            rotulos += [rotulo_de_constante(nome) for nome in constantes_da_linha(codigo)]
        elif nivel == 0 and linguagem == "javascript" and re.match(r"function\s+(\w+)\s*\(", codigo):
            rotulos.append(rotulo_de_funcao(re.match(r"function\s+(\w+)", codigo).group(1)))
        elif nivel == 1 and classe is not None:
            if construtor_aberto and codigo.startswith(":"):
                # A continuação do construtor do C++: ": adj(adj), direcionado(direcionado) {}"
                rotulos.append("estrutura_construtor")
                construtor_aberto = False
            else:
                rotulos += membro_da_classe(codigo, classe, linguagem)
                if "estrutura_construtor" in rotulos:
                    no_construtor = True
                    construtor_aberto = not codigo.endswith("{") and not codigo.endswith("}")
                if "estrutura_registro" in rotulos and codigo.endswith("{"):
                    no_registro = nivel
        elif no_construtor and re.match(r"this\.(\w+)\s*=", codigo):
            rotulos.append(rotulo_de_campo(re.match(r"this\.(\w+)", codigo).group(1)))
        if rotulos and numero not in rotulados:
            extras[numero] = rotulos
    return extras


# Um membro da classe (Java, C++, JavaScript): construtor, método, campo, constante ou registro
def membro_da_classe(codigo, classe, linguagem):
    if codigo in ("public:", "private:", "protected:") or codigo.startswith("}"):
        return []
    if re.match(r"(static\s+)?(record|struct)\s+\w+", codigo):
        return ["estrutura_registro"]
    enumeracao = re.match(r"enum\s+\w+\s*\{([^}]*)\}", codigo)
    if enumeracao is not None:
        return [rotulo_de_constante(nome.strip()) for nome in enumeracao.group(1).split(",") if nome.strip()]
    chamada = re.search(r"([A-Za-z_]\w*)\s*\(", codigo)
    eh_constante = re.search(r"\b(static\s+final|final\s+static|constexpr|static\s+const)\b", codigo) is not None
    if chamada is not None and not eh_constante and "=" not in codigo.split("(")[0]:
        nome = chamada.group(1)
        if nome in PALAVRAS_DE_CONTROLE:
            return []
        if nome == classe or nome == "constructor":
            return ["estrutura_construtor"]
        return [rotulo_de_funcao(nome)]
    if eh_constante:
        return [rotulo_de_constante(nome) for nome in constantes_da_linha(codigo)]
    nome = nome_declarado(codigo)
    if nome is not None:
        if nome.isupper():
            return [rotulo_de_constante(nome)]
        return [rotulo_de_campo(nome)]
    return []


def estrutura_do_c(linhas, rotulados):
    extras = {}
    profundidade = profundidades(linhas)
    no_registro = False
    for numero in range(1, len(linhas) + 1):
        codigo = sem_comentario(linhas[numero - 1], "//")
        nivel = profundidade[numero - 1]
        rotulos = []
        if no_registro:
            rotulos.append("estrutura_registro")
            if nivel == 1 and codigo.startswith("}"):
                no_registro = False
        elif not codigo or nivel > 0:
            pass
        elif codigo.startswith("#include"):
            rotulos.append("estrutura_importar")
        elif re.match(r"#define\s+([A-Z][A-Z0-9_]*)", codigo):
            rotulos.append(rotulo_de_constante(re.match(r"#define\s+(\w+)", codigo).group(1)))
        elif re.match(r"enum\s+\w+\s*\{([^}]*)\}", codigo):
            nomes = re.match(r"enum\s+\w+\s*\{([^}]*)\}", codigo).group(1).split(",")
            rotulos += [rotulo_de_constante(nome.strip()) for nome in nomes if nome.strip()]
        elif re.match(r"(typedef\s+)?struct\s+\w+\s*\{", codigo):
            rotulos.append("estrutura_registro")
            no_registro = True
        elif "(" in codigo and codigo.endswith(");") and "=" not in codigo:
            rotulos.append("estrutura_prototipo")
        elif "(" in codigo and codigo.endswith("{") and "=" not in codigo.split("(")[0]:
            rotulos.append(rotulo_de_funcao(re.search(r"([A-Za-z_]\w*)\s*\(", codigo).group(1)))
        else:
            nome = nome_declarado(codigo)
            if nome is not None:
                rotulos.append(rotulo_de_constante(nome) if nome.isupper() else rotulo_de_campo(nome))
        if rotulos and numero not in rotulados:
            extras[numero] = rotulos
    return extras


def estrutura_do_pseudocodigo(linhas, rotulados):
    extras = {}
    for numero in range(1, len(linhas) + 1):
        linha = linhas[numero - 1]
        if numero in rotulados:
            continue
        # O começo de um procedimento, sem recuo: DIJKSTRA(G, w, s), DFS-VISIT(G, u), EXTRAIR-MÍNIMO(Q)
        achado = re.match(r"([A-ZÀ-Ý][A-ZÀ-Ý0-9_\-]*)\(.*\)\s*$", linha)
        if achado is not None:
            extras[numero] = [rotulo_de_funcao(achado.group(1))]
    return extras


# Os rótulos automáticos das linhas que ainda não têm rótulo: {número da linha: [rótulos]}
def rotulos_da_estrutura(linhas, rotulos, linguagem):
    rotulados = set(rotulos)
    if linguagem == "python":
        return estrutura_do_python(linhas, rotulados)
    if linguagem == "c":
        return estrutura_do_c(linhas, rotulados)
    if linguagem in ("java", "cpp", "javascript"):
        return estrutura_com_classes(linhas, rotulados, linguagem)
    return estrutura_do_pseudocodigo(linhas, rotulados)


# Os comentários também ganham rótulo, para as linguagens andarem juntas neles:
#   - o primeiro bloco de comentários sem rótulo (o que explica a busca, no começo do código de estudo)
#     ganha "comentario_do_estudo";
#   - o bloco de comentários logo em cima de uma classe ou de uma função ganha o rótulo dela
#     ("# RELAX(u, v, w): ..." em cima de "def relaxar" fica com estrutura_def_relaxar).
def rotular_comentarios(linhas, rotulos_da_linha, linguagem):
    marcador = "#" if linguagem == "python" else "//"

    def comentario(numero):
        return linhas[numero - 1].strip().startswith(marcador)

    numero = 1
    while numero <= len(linhas) and not (comentario(numero) and numero not in rotulos_da_linha):
        numero += 1
    while numero <= len(linhas) and comentario(numero) and numero not in rotulos_da_linha:
        rotulos_da_linha[numero] = ["comentario_do_estudo"]
        numero += 1
    for numero in range(1, len(linhas) + 1):
        rotulo = None
        for candidato in rotulos_da_linha.get(numero, []):
            if candidato.startswith("estrutura_def_") or candidato in ("estrutura_construtor", "estrutura_classe"):
                rotulo = candidato
                break
        if rotulo is None or (numero > 1 and rotulo in rotulos_da_linha.get(numero - 1, [])):
            continue
        acima = numero - 1
        while acima >= 1 and comentario(acima) and acima not in rotulos_da_linha:
            rotulos_da_linha[acima] = [rotulo]
            acima -= 1


# Completa um programa de exportacao/codigo_fonte.programas_com_rotulos com os rótulos da estrutura e
# os dicionários que a tela usa:
#   "rotulos_da_linha" -> {número da linha: [rótulos]}  (a maioria tem um só)
#   "rotulo_da_linha"  -> {número da linha: o primeiro rótulo}
#   "linhas_do_rotulo" -> {rótulo: [números das linhas, em ordem]}
def completar(programa):
    linguagem = programa["linguagem"]
    rotulos_da_linha = {}
    for numero, rotulo in programa["rotulos"].items():
        rotulos_da_linha[numero] = [rotulo]
    for numero, rotulos in rotulos_da_estrutura(programa["linhas"], programa["rotulos"], linguagem).items():
        rotulos_da_linha[numero] = list(rotulos)
    rotular_comentarios(programa["linhas"], rotulos_da_linha, linguagem)
    linhas_do_rotulo = {}
    rotulo_da_linha = {}
    for numero in sorted(rotulos_da_linha):
        rotulo_da_linha[numero] = rotulos_da_linha[numero][0]
        for rotulo in rotulos_da_linha[numero]:
            linhas_do_rotulo.setdefault(rotulo, []).append(numero)
    programa["rotulos_da_linha"] = rotulos_da_linha
    programa["rotulo_da_linha"] = rotulo_da_linha
    programa["linhas_do_rotulo"] = linhas_do_rotulo
    return programa
