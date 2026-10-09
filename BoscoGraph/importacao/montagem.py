'''
    Montagem do grafo a partir do que foi reconhecido num desenho (PDF ou imagem).

    O reconhecimento (importacao/pdf.py e importacao/imagem.py) entrega "primitivas":
      formas -> os vértices: {"centro": (x, y), "raio": r} (círculo/elipse)
                             ou {"centro": (x, y), "caixa": (x0, y0, x1, y1)} (retângulo)
      tracos -> as linhas: {"pontos": [(x, y), ...]} do começo ao fim da linha;
                pode trazer "seta_no_inicio" e "seta_no_fim" (True/False) se já se sabe
      pontas -> as pontas de seta (triângulos): {"centro": (x, y), "pontos": [...], "tamanho": t}
      textos -> {"texto": "A", "caixa": (x0, y0, x1, y1)}

    E a montagem decide, com as mesmas regras para o PDF e para a imagem:
      1. texto dentro de uma forma = o nome do vértice;
      2. cada linha liga as formas mais perto das suas duas pontas (laço = as duas na mesma);
         uma ponta de seta perto do fim da linha diz o sentido (e a linha vai até a ponta da seta);
      3. texto fora das formas = o rótulo da linha mais próxima (um número vira peso).
    Tudo o que não se encaixa (linha solta, texto solto) vira um aviso.
'''

from entrada import contar
from importacao import geometria


def montar(formas, tracos, pontas, textos):
    avisos = []
    tamanho_tipico = geometria.mediana([tamanho_da_forma(forma) for forma in formas]) or 20

    # 1. Os textos dentro das formas são os nomes dos vértices (na ordem de leitura: linha, depois coluna)
    nomes = []
    for forma in formas:
        nomes.append([])
    soltos = []
    for texto in textos:
        centro = centro_da_caixa(texto["caixa"])
        dono = None
        for i in range(len(formas)):
            if geometria.dentro_da_forma(centro, formas[i]):
                dono = i
                break
        if dono is None:
            soltos.append(texto)
        else:
            nomes[dono].append(texto)
    vertices = []
    sem_nome = 0
    for i in range(len(formas)):
        partes = sorted(nomes[i], key=chave_de_leitura)
        rotulo = " ".join(texto["texto"].strip() for texto in partes).strip()
        if rotulo == "":
            sem_nome += 1
        vertices.append({"id": f"forma{i + 1}", "rotulo": rotulo, "sem_nome": rotulo == "",
                         "posicao": formas[i]["centro"]})
    if sem_nome:
        avisos.append(contar(sem_nome, "vértice sem nome no desenho ganhou", "vértices sem nome no desenho ganharam")
                      + " um nome automático (A, B, C...): renomeie no editor se precisar.")

    # 2. As linhas: cada ponta encaixa na forma mais próxima.
    # Tolerância: a linha costuma parar um pouco antes da borda (ou depois dela, por dentro)
    def tolerancia(forma):
        return max(4.0, 0.45 * tamanho_da_forma(forma) / 2)

    setas = associar_pontas_de_seta(tracos, pontas)
    arestas = []
    linhas_das_arestas = []
    soltas = 0
    for i in range(len(tracos)):
        traco = tracos[i]
        pontos = list(traco["pontos"])
        if len(pontos) < 2:
            continue
        seta_no_inicio = traco.get("seta_no_inicio")
        seta_no_fim = traco.get("seta_no_fim")
        if seta_no_inicio is None:
            seta_no_inicio = (i, 0) in setas
            if seta_no_inicio and setas[(i, 0)] is not None:
                pontos.insert(0, setas[(i, 0)])        # a linha "continua" até a ponta da seta
        if seta_no_fim is None:
            seta_no_fim = (i, -1) in setas
            if seta_no_fim and setas[(i, -1)] is not None:
                pontos.append(setas[(i, -1)])
        inicio = geometria.forma_mais_proxima(pontos[0], formas, tolerancia)
        fim = geometria.forma_mais_proxima(pontos[-1], formas, tolerancia)
        if inicio is None or fim is None:
            if inicio is not None or fim is not None:
                soltas += 1                     # uma ponta presa e a outra solta: não dá para saber
            continue
        if inicio == fim and not sai_da_forma(pontos, formas[inicio]):
            continue                            # um risco dentro do próprio vértice (sublinhado, enfeite)
        if seta_no_inicio and seta_no_fim:
            seta = "ambas"
        elif seta_no_fim:
            seta = "fim"
        elif seta_no_inicio:
            seta = "inicio"
        else:
            seta = "nenhuma"
        arestas.append({"origem": f"forma{inicio + 1}", "destino": f"forma{fim + 1}", "rotulo": "", "peso": None,
                        "seta": seta})
        linhas_das_arestas.append(pontos)
    if soltas:
        avisos.append(contar(soltas, "linha com uma ponta solta (sem vértice perto) foi ignorada",
                             "linhas com uma ponta solta (sem vértice perto) foram ignoradas") + ".")

    # 3. Os textos de fora são rótulos das arestas. Os programas de desenho põem o rótulo junto do
    # MEIO da aresta; por isso a medida é a distância ao ponto do meio da linha (e o texto também
    # precisa estar perto da linha). Primeiro cada aresta recebe no máximo um rótulo, dos pares mais
    # próximos para os mais distantes; os textos que sobrarem vão para a aresta mais próxima.
    meios = []
    for linha in linhas_das_arestas:
        meios.append(geometria.ponto_do_meio(linha))
    candidatos = []
    for j in range(len(soltos)):
        caixa = soltos[j]["caixa"]
        centro = centro_da_caixa(caixa)
        limite = max(2.5 * (caixa[3] - caixa[1]), 0.9 * tamanho_tipico)
        for i in range(len(linhas_das_arestas)):
            if geometria.distancia_a_linha(centro, linhas_das_arestas[i]) <= limite:
                candidatos.append((geometria.distancia(centro, meios[i]), j, i))
    candidatos.sort(key=lambda candidato: candidato[0])
    dono_do_texto = {}
    com_rotulo = []
    for distancia, j, i in candidatos:
        if j not in dono_do_texto and i not in com_rotulo:
            dono_do_texto[j] = i
            com_rotulo.append(i)
    for distancia, j, i in candidatos:
        if j not in dono_do_texto:
            dono_do_texto[j] = i
    rotulos = []
    for aresta in arestas:
        rotulos.append([])
    ignorados = []
    for j in range(len(soltos)):
        if j in dono_do_texto:
            rotulos[dono_do_texto[j]].append(soltos[j])
        else:
            ignorados.append(soltos[j]["texto"].strip())
    for i in range(len(arestas)):
        partes = sorted(rotulos[i], key=chave_de_leitura)
        arestas[i]["rotulo"] = " ".join(texto["texto"].strip() for texto in partes).strip()
    if ignorados:
        avisos.append("Textos soltos ignorados (longe dos vértices e das linhas): " + ", ".join(ignorados[:5]) + ".")

    # O que foi reconhecido, para a conferência desenhar por cima da imagem
    marcas = {"vertices": [], "arestas": []}
    for i in range(len(formas)):
        marcas["vertices"].append((f"forma{i + 1}", formas[i]["centro"], tamanho_da_forma(formas[i]) / 2))
    for i in range(len(arestas)):
        primeiro = linhas_das_arestas[i][0]
        ultimo = linhas_das_arestas[i][-1]
        marcas["arestas"].append((primeiro, ultimo, arestas[i]["seta"]))
    return {"vertices": vertices, "arestas": arestas, "direcionado": None, "avisos": avisos,
            "conferir": True, "marcas_originais": marcas}


def tamanho_da_forma(forma):
    if "raio" in forma:
        return 2 * forma["raio"]
    x0, y0, x1, y1 = forma["caixa"]
    return min(x1 - x0, y1 - y0)


def centro_da_caixa(caixa):
    return ((caixa[0] + caixa[2]) / 2, (caixa[1] + caixa[3]) / 2)


# Ordem de leitura: de cima para baixo e, na mesma linha, da esquerda para a direita
def chave_de_leitura(texto):
    return (round(texto["caixa"][1] / 4), texto["caixa"][0])


# A linha sai da forma? (para separar um laço de verdade de um risco dentro do vértice)
def sai_da_forma(pontos, forma):
    for ponto in pontos:
        if geometria.distancia_a_borda(ponto, forma) > tamanho_da_forma(forma) * 0.25 \
                and not geometria.dentro_da_forma(ponto, forma):
            return True
    return False


# Qual ponta de seta pertence a qual fim de linha.
# Uma ponta de seta pertence a um fim de linha se estiver ALINHADA com a direção da linha ali
# (pouco desvio para o lado) e perto do fim (um pouco depois dele, ou por cima do último trecho).
# Só a distância não basta: a seta de outra aresta, chegando no mesmo vértice, pode estar tão perto
# quanto. Os pares são escolhidos dos mais próximos para os mais distantes, cada seta uma vez só.
# Devolve {(número do traço, 0 ou -1): ponto até onde a linha continua, ou None}
def associar_pontas_de_seta(tracos, pontas):
    candidatos = []
    for i in range(len(tracos)):
        pontos = tracos[i]["pontos"]
        if len(pontos) < 2 or tracos[i].get("seta_no_inicio") is not None:
            continue
        for extremo in (0, -1):
            ponto = pontos[extremo]
            anterior = ponto_anterior(pontos, extremo)
            direcao = (ponto[0] - anterior[0], ponto[1] - anterior[1])
            comprimento = geometria.distancia(ponto, anterior)
            if comprimento == 0:
                continue
            direcao = (direcao[0] / comprimento, direcao[1] / comprimento)
            for j in range(len(pontas)):
                centro = pontas[j]["centro"]
                tamanho = pontas[j]["tamanho"]
                vetor = (centro[0] - ponto[0], centro[1] - ponto[1])
                adiante = vetor[0] * direcao[0] + vetor[1] * direcao[1]          # ao longo da linha
                de_lado = abs(vetor[0] * direcao[1] - vetor[1] * direcao[0])   # para o lado
                if de_lado <= 0.5 * tamanho and -1.5 * tamanho <= adiante <= 1.5 * tamanho:
                    candidatos.append((geometria.distancia(ponto, centro), i, extremo, j, adiante > 0))
    candidatos.sort(key=lambda candidato: candidato[0])
    setas = {}
    usadas = []
    for distancia, i, extremo, j, adiante in candidatos:
        if (i, extremo) in setas or j in usadas:
            continue
        usadas.append(j)
        continuacao = None
        if adiante:
            # A seta fica depois do fim da linha: a ponta de verdade é o canto mais longe da linha
            anterior = ponto_anterior(tracos[i]["pontos"], extremo)
            maior = None
            for canto in pontas[j]["pontos"]:
                d = geometria.distancia(canto, anterior)
                if maior is None or d > maior:
                    continuacao = canto
                    maior = d
        setas[(i, extremo)] = continuacao
    return setas


# Um ponto da linha a pelo menos 3 unidades do extremo (para a direção não depender de um
# pedacinho minúsculo do fim da curva)
def ponto_anterior(pontos, extremo):
    ponto = pontos[extremo]
    if extremo == 0:
        sequencia = pontos[1:]
    else:
        sequencia = list(reversed(pontos[:-1]))
    for outro in sequencia:
        if geometria.distancia(ponto, outro) >= 3:
            return outro
    return sequencia[-1]
