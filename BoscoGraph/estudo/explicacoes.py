'''
    A explicação de cada linha do código de estudo, com os valores daquele momento.

    No modo linha a linha, a linha em destaque é a PRÓXIMA a rodar (como num depurador). A explicação
    diz o que ela vai fazer, já com os números: "novo = d[y] + peso = 5 + 3 = 8", "d[x] = ∞ < d[t] = 8?
    Não". Cada rótulo de linha (veja estudo/__init__.py) tem uma função que monta esse texto.

    As funções recebem um "contexto" c, em que c.u, c.d, c.fila... são as variáveis do momento:
    primeiro as variáveis locais da função (u, v, peso, novo, menor...) e, se não houver, os campos do
    objeto da busca (self.d, self.cor, self.fila...). Elas rodam ANTES de a linha rodar: por isso, numa
    linha como "d[v] = novo", c.d[c.v] ainda é o valor antigo.

    Este arquivo não usa Tkinter.
'''

from decimal import Decimal
from operator import itemgetter

import algoritmos
from entrada import formatar_numero


# Um número como aparece na tela: 2,5 e ∞
def n(valor):
    return formatar_numero(valor)


# Uma lista de nomes: "B, C, D" (ou "vazia")
def nomes(lista):
    if len(lista) == 0:
        return "vazia"
    return ", ".join(str(item) for item in lista)


# Os vizinhos de u, como estão na lista de adjacência (com ou sem peso)
def vizinhos(c, u):
    lista = []
    for item in c.adj[u]:
        if isinstance(item, tuple):
            lista.append(item[0])
        else:
            lista.append(item)
    return nomes(lista)


def sim_ou_nao(condicao, se_sim, se_nao):
    if condicao:
        return "Sim: " + se_sim
    return "Não: " + se_nao


class Contexto:
    def __init__(self, locais, objeto):
        self.locais = locais
        self.objeto = objeto

    # c.u procura u nas variáveis locais e, se não achar, nos campos do objeto (self.u)
    def __getattr__(self, nome):
        if nome in self.locais:
            return self.locais[nome]
        return getattr(self.objeto, nome)

    # O lado de um vértice na busca bidirecional (o campo self.lado; "lado" sozinho é o parâmetro)
    def lado_do(self, vertice):
        return self.objeto.lado[vertice]

    # O infinito do código de estudo (o mesmo Decimal("Infinity") de todas as buscas)
    @property
    def INFINITO_DO_ESTUDO(self):
        return Decimal("Infinity")


# ----------------------------------------------------------------------
# As linhas que várias buscas têm (o mesmo rótulo faz a mesma coisa)
# ----------------------------------------------------------------------

COMUNS = {
    "cada_vertice": lambda c: "Pega o próximo vértice v do grafo (o laço termina quando acabarem).",
    "pinta_branco": lambda c: f"cor[{c.v}] = Branco: {c.v} ainda não foi visto pela busca.",
    "d_infinito": lambda c: f"d[{c.v}] = ∞: ainda não há caminho conhecido até {c.v}.",
    "inicializar": lambda c: f"pai[{c.v}] = None: {c.v} ainda não tem de onde veio.",
    "origem_cinza": lambda c: f"cor[{c.s}] = Cinza: a origem {c.s} já é conhecida e vai para a fila.",
    "enquanto_fila": lambda c: (f"A fila tem {len(c.fila)}: {nomes(list(c.fila))}. Continua."
                                if len(c.fila) > 0 else "A fila está vazia: o laço termina."),
    "cada_vizinho": lambda c: f"Pega o próximo vizinho v de {c.u} na lista de adjacência ({vizinhos(c, c.u)}).",
    "pai_v": lambda c: f"pai[{c.v}] = {c.u}: o caminho até {c.v} passa a vir de {c.u}.",
    "pinta_cinza": lambda c: f"cor[{c.v}] = Cinza: {c.v} acaba de ser visto e vai para a fila.",
    "menor_primeiro": lambda c: f"Começa supondo que o menor é o primeiro da fila: menor = {c.fila[0]}.",
    "cada_da_fila": lambda c: f"Pega o próximo vértice v da fila ({nomes(list(c.fila))}) para comparar.",
    "novo_menor": lambda c: f"menor = {c.v}.",
    "tira_da_fila": lambda c: f"Tira {c.menor} da fila (no empate, fica o que entrou primeiro).",
    "devolve_menor": lambda c: f"Devolve {c.menor} para quem chamou.",
    "chama_extrair": lambda c: "Chama extrair_minimo(): tira da fila o vértice de menor prioridade.",
}


# ----------------------------------------------------------------------
# Busca em profundidade
# ----------------------------------------------------------------------

def tipo_da_aresta(c):
    if c.cor[c.v] == "Cinza":
        return "retorno"
    if c.d[c.u] < c.d[c.v]:
        return "avanço"
    return "cruzamento"


PROFUNDIDADE = {
    "pinta_cada": lambda c: "Pega o próximo vértice u do grafo (o laço termina quando acabarem).",
    "pintar_branco": lambda c: f"cor[{c.u}] = Branco: {c.u} ainda não foi descoberto.",
    "pai_nulo": lambda c: f"pai[{c.u}] = None: {c.u} ainda não tem pai.",
    "zerar_tempo": lambda c: "tempo = 0: o relógio da busca começa do zero.",
    "cada_raiz": lambda c: f"Pega o próximo vértice u da ordem das raízes ({nomes(c.ordem)}).",
    "raiz_branca": lambda c: f"cor[{c.u}] é Branco? " + sim_ou_nao(
        c.cor[c.u] == "Branco", f"{c.u} começa uma árvore nova.", f"{c.u} está {c.cor[c.u]}, já foi visitado."),
    "nova_arvore": lambda c: f"Chama dfs_visit({c.u}): uma árvore nova, com raiz {c.u}.",
    "tempo_d": lambda c: f"tempo = {c.tempo} + 1 = {c.tempo + 1}: o relógio anda na descoberta.",
    "anota_d": lambda c: f"d[{c.u}] = {c.tempo}: o tempo em que {c.u} foi descoberto.",
    "descobrir": lambda c: f"cor[{c.u}] = Cinza: {c.u} foi descoberto e está em exploração.",
    "cada_vizinho": lambda c: f"Pega o próximo vizinho v de {c.u} na lista de adjacência ({vizinhos(c, c.u)}).",
    "e_volta": lambda c: f"voltas[({c.u}, {c.v})] = {c.voltas.get((c.u, c.v), 0)} > 0? " + sim_ou_nao(
        c.voltas.get((c.u, c.v), 0) > 0, f"é a mesma aresta {c.v} — {c.u}, já examinada pelo outro lado.",
        "a aresta ainda não foi examinada."),
    "revisitar": lambda c: (f"voltas[({c.u}, {c.v})] = {c.voltas[(c.u, c.v)] - 1}: desconta a volta e "
                            f"não examina de novo."),
    "vizinho_branco": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.u} -> {c.v} vai entrar na árvore.", f"{c.v} está {c.cor[c.v]}."),
    "examinar_arvore": lambda c: f"tipo[({c.u}, {c.v})] = árvore: a busca vai descer por esta aresta.",
    "volta_arvore": lambda c: "Chama anotar_volta(): no não orientado, a outra metade da aresta fica anotada.",
    "pai_v": lambda c: f"pai[{c.v}] = {c.u}: {c.v} foi descoberto a partir de {c.u}.",
    "desce": lambda c: f"Chama dfs_visit({c.v}): a busca desce para {c.v}; {c.u} espera na pilha de chamadas.",
    "examinar_outra": lambda c: (f"{c.v} já foi descoberto ({c.cor[c.v]}): chama classificar(), que diz o "
                                 f"tipo da aresta {c.u} -> {c.v}."),
    "volta_outra": lambda c: "Chama anotar_volta(): no não orientado, a outra metade da aresta fica anotada.",
    "pintar_preto": lambda c: f"cor[{c.u}] = Preto: todos os vizinhos de {c.u} foram examinados.",
    "tempo_f": lambda c: f"tempo = {c.tempo} + 1 = {c.tempo + 1}: o relógio anda no término.",
    "finalizar": lambda c: (f"f[{c.u}] = {c.tempo}: o tempo em que {c.u} terminou. Depois, dfs_visit({c.u}) "
                            f"volta para quem chamou."),
    "se_cinza": lambda c: f"cor[{c.v}] é Cinza? " + sim_ou_nao(
        c.cor[c.v] == "Cinza", f"{c.v} ainda está em exploração: é um ancestral de {c.u}.",
        f"{c.v} está {c.cor[c.v]} (já terminou)."),
    "retorno": lambda c: f"Devolve \"retorno\": {c.u} -> {c.v} volta para um ancestral e fecha um ciclo.",
    "se_descendente": lambda c: f"d[{c.u}] = {c.d[c.u]} < d[{c.v}] = {c.d[c.v]}? " + sim_ou_nao(
        c.d[c.u] < c.d[c.v], f"{c.v} foi descoberto depois de {c.u}, é um descendente.",
        f"{c.v} foi descoberto antes, em outro ramo."),
    "avanco": lambda c: f"Devolve \"avanço\": {c.u} -> {c.v} vai para um descendente que já terminou.",
    "cruzamento": lambda c: f"Devolve \"cruzamento\": {c.u} -> {c.v} vai para outro ramo, já terminado.",
    "se_nao_orientado": lambda c: "Grafo não orientado e não é laço? " + sim_ou_nao(
        not c.direcionado and c.u != c.v, f"a aresta também está na lista de {c.v}.", "não há outra metade."),
    "anota_volta": lambda c: (f"voltas[({c.v}, {c.u})] = {c.voltas.get((c.v, c.u), 0) + 1}: na lista de "
                              f"{c.v}, a aresta até {c.u} não vai contar de novo."),
}


# ----------------------------------------------------------------------
# Busca em largura
# ----------------------------------------------------------------------

LARGURA = {
    "origem_d": lambda c: f"d[{c.s}] = 0: a origem está a 0 arestas dela mesma.",
    "origem": lambda c: f"{c.s} entra no fim da fila.",
    "desenfileirar": lambda c: f"Tira {c.fila[0]} do começo da fila: é o vértice que vai ser explorado.",
    "ignorar_vizinho": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} vai ser descoberto agora.", f"{c.v} já foi descoberto ({c.cor[c.v]})."),
    "d_mais_um": lambda c: f"d[{c.v}] = d[{c.u}] + 1 = {n(c.d[c.u])} + 1 = {n(c.d[c.u] + 1)}: uma aresta a mais.",
    "descobrir_vizinho": lambda c: f"{c.v} entra no fim da fila.",
    "terminar_vertice": lambda c: f"cor[{c.u}] = Preto: todos os vizinhos de {c.u} já foram vistos.",
}


# ----------------------------------------------------------------------
# Dijkstra, gulosa e A*: a fila de prioridade e o relaxamento
# ----------------------------------------------------------------------

def comparar(c, chave):
    valores = getattr(c, chave)
    return f"{chave}[{c.v}] = {n(valores[c.v])} < {chave}[{c.menor}] = {n(valores[c.menor])}? " + sim_ou_nao(
        valores[c.v] < valores[c.menor], f"{c.v} passa a ser o menor.", f"o menor continua {c.menor}.")


DIJKSTRA = {
    "origem_d": lambda c: f"d[{c.s}] = 0: chegar na origem não custa nada.",
    "origem": lambda c: f"{c.s} entra na fila de prioridade.",
    "chama_extrair": lambda c: "Chama extrair_minimo(): tira da fila o vértice de menor d.",
    "extrair": lambda c: f"cor[{c.u}] = Preto: d[{c.u}] = {n(c.d[c.u])} é definitivo (ninguém chega mais barato).",
    "chama_relaxar": lambda c: f"Chama relaxar({c.u}, {c.v}, {n(c.peso)}): a aresta {c.u} -> {c.v} melhora d[{c.v}]?",
    "compara_d": lambda c: comparar(c, "d"),
    "soma": lambda c: (f"novo = d[{c.u}] + peso = {n(c.d[c.u])} + {n(c.peso)} = {n(c.d[c.u] + c.peso)}: "
                       f"o custo de chegar em {c.v} passando por {c.u}."),
    "relaxar_nao": lambda c: f"novo = {n(c.novo)} < d[{c.v}] = {n(c.d[c.v])}? " + sim_ou_nao(
        c.novo < c.d[c.v], f"passar por {c.u} é mais barato.", f"o caminho que {c.v} já tem é tão bom ou melhor."),
    "relaxar_melhorou": lambda c: f"d[{c.v}] = {n(c.novo)} (era {n(c.d[c.v])}).",
    "se_branco": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} ainda não está na fila.",
        f"{c.v} já está na fila: só a prioridade dele mudou."),
    "entra_na_fila": lambda c: f"{c.v} entra na fila de prioridade, com d = {n(c.d[c.v])}.",
}

GULOSA = {
    "origem": lambda c: f"{c.s} entra na fronteira.",
    "chama_extrair": lambda c: "Chama extrair_minimo(): tira da fronteira o vértice de menor h.",
    "extrair": lambda c: f"cor[{c.u}] = Preto: {c.u} vai ser expandido (h = {n(c.h[c.u])}).",
    "se_destino": lambda c: f"{c.u} é o destino {c.destino}? " + sim_ou_nao(
        c.u == c.destino, "chegou!", "continua."),
    "chegou": lambda c: "Devolve True: a busca chegou ao destino.",
    "ignorar_vizinho": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} ainda não foi visto.", f"{c.v} já foi visto ({c.cor[c.v]})."),
    "descobrir_vizinho": lambda c: f"{c.v} entra na fronteira, com h = {n(c.h[c.v])}.",
    "nao_chegou": lambda c: "A fronteira esvaziou sem chegar ao destino: devolve False.",
    "compara_h": lambda c: comparar(c, "h"),
}

A_ESTRELA = {
    "g_infinito": lambda c: f"g[{c.v}] = ∞: ainda não há caminho conhecido até {c.v}.",
    "f_infinito": lambda c: f"f[{c.v}] = ∞.",
    "origem_g": lambda c: f"g[{c.s}] = 0: chegar na origem não custa nada.",
    "origem_f": lambda c: f"f[{c.s}] = h[{c.s}] = {n(c.h[c.s])}: g + h, com g = 0.",
    "origem": lambda c: f"{c.s} entra na fronteira.",
    "chama_extrair": lambda c: "Chama extrair_minimo(): tira da fronteira o vértice de menor f = g + h.",
    "extrair": lambda c: f"cor[{c.u}] = Preto: {c.u} vai ser expandido (f = {n(c.f[c.u])}).",
    "se_destino": lambda c: f"{c.u} é o destino {c.destino}? " + sim_ou_nao(
        c.u == c.destino, f"chegou, com custo g = {n(c.g[c.u])}.", "continua."),
    "chegou": lambda c: "Devolve True: a busca chegou ao destino.",
    "chama_relaxar": lambda c: f"Chama relaxar({c.u}, {c.v}, {n(c.peso)}): a aresta {c.u} -> {c.v} melhora g[{c.v}]?",
    "nao_chegou": lambda c: "A fronteira esvaziou sem chegar ao destino: devolve False.",
    "compara_f": lambda c: comparar(c, "f"),
    "soma": lambda c: (f"novo = g[{c.u}] + peso = {n(c.g[c.u])} + {n(c.peso)} = {n(c.g[c.u] + c.peso)}: "
                       f"o custo de chegar em {c.v} passando por {c.u}."),
    "relaxar_nao": lambda c: f"novo = {n(c.novo)} < g[{c.v}] = {n(c.g[c.v])}? " + sim_ou_nao(
        c.novo < c.g[c.v], f"passar por {c.u} é mais barato.", f"o caminho que {c.v} já tem é tão bom ou melhor."),
    "novo_g": lambda c: f"g[{c.v}] = {n(c.novo)} (era {n(c.g[c.v])}).",
    "relaxar_melhorou": lambda c: (f"f[{c.v}] = novo + h[{c.v}] = {n(c.novo)} + {n(c.h[c.v])} = "
                                   f"{n(c.novo + c.h[c.v])}: a nova prioridade de {c.v}."),
    "se_branco": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} ainda não está na fronteira.", f"{c.v} está {c.cor[c.v]}."),
    "entra_na_fila": lambda c: f"{c.v} entra na fronteira, com f = {n(c.f[c.v])}.",
    "se_preto": lambda c: f"cor[{c.v}] é Preto? " + sim_ou_nao(
        c.cor[c.v] == "Preto", f"{c.v} já tinha sido expandido, mas achou um caminho mais barato.",
        f"{c.v} já está na fronteira (Cinza): só a prioridade mudou."),
    "relaxar_reabriu": lambda c: (f"cor[{c.v}] = Cinza: {c.v} é REABERTO. Isso só acontece quando a heurística "
                                  f"não é consistente."),
    "reentra_na_fila": lambda c: f"{c.v} volta para a fronteira, com f = {n(c.f[c.v])}.",
}


# ----------------------------------------------------------------------
# Bellman-Ford
# ----------------------------------------------------------------------

def soma_do_arco(c):
    return c.d[c.u] + c.peso


BELLMAN_FORD = {
    "origem": lambda c: f"d[{c.s}] = 0: chegar na origem não custa nada.",
    "parou_falso": lambda c: "parou_antes = False: a busca ainda não parou antes da hora.",
    "rodada": lambda c: (f"Começa a próxima rodada (no máximo |V| − 1 = {len(c.vertices) - 1}); se já fez todas, "
                         f"o laço termina."),
    "mudou_falso": lambda c: "mudou = False: nenhuma distância mudou nesta rodada, por enquanto.",
    "cada_arco": lambda c: f"Pega o próximo arco (u, v, peso) da lista ({len(c.arcos)} arcos).",
    "relaxar_nao": lambda c: (f"d[{c.u}] + peso = {n(c.d[c.u])} + {n(c.peso)} = {n(soma_do_arco(c))} < "
                              f"d[{c.v}] = {n(c.d[c.v])}? ") + sim_ou_nao(
        soma_do_arco(c) < c.d[c.v], f"passar por {c.u} é mais barato.", "não melhora."),
    "relaxar_melhorou": lambda c: f"d[{c.v}] = {n(soma_do_arco(c))} (era {n(c.d[c.v])}).",
    "mudou": lambda c: "mudou = True: esta rodada mudou alguma distância.",
    "se_nao_mudou": lambda c: "A rodada não mudou nada? " + sim_ou_nao(
        not c.mudou, "as próximas também não mudariam.", "vem mais uma rodada."),
    "rodada_sem_mudanca": lambda c: "parou_antes = True: as distâncias já são as finais.",
    "para": lambda c: "break: sai do laço das rodadas antes da hora.",
    "se_nao_parou": lambda c: "Fez todas as rodadas sem parar antes? " + sim_ou_nao(
        not c.parou_antes, "confere se ainda há algo que diminua (ciclo negativo).",
        "parou antes, então não há ciclo negativo."),
    "verificar_ciclo": lambda c: "Pega o próximo arco para conferir se ele ainda diminui alguma distância.",
    "ainda_diminui": lambda c: (f"d[{c.u}] + peso = {n(soma_do_arco(c))} < d[{c.v}] = {n(c.d[c.v])}? ") + sim_ou_nao(
        soma_do_arco(c) < c.d[c.v], "depois de |V| − 1 rodadas, só um ciclo negativo faz isso.", "tudo certo."),
    "ciclo_negativo": lambda c: "Devolve False: há um ciclo negativo alcançável a partir da origem.",
    "sem_ciclo_negativo": lambda c: "Devolve True: sem ciclo negativo, as distâncias são as menores possíveis.",
}


# ----------------------------------------------------------------------
# Busca em profundidade limitada e aprofundamento iterativo
# ----------------------------------------------------------------------

def caminho_atual(c):
    if len(c.caminho) == 0:
        return "vazio"
    return " -> ".join(str(v) for v in c.caminho)


LIMITADA = {
    "chama_dls": lambda c: (f"Chama dls({c.s}, destino = {c.destino}, limite = {c.limite}, prof = 0): a busca começa "
                            f"na origem e pode descer até {c.limite} arestas."),
    "entrar": lambda c: f"cor[{c.u}] = Cinza: {c.u} entra no caminho (profundidade {c.prof}).",
    "anota_prof": lambda c: f"prof[{c.u}] = {c.prof}: {c.u} está a {c.prof} arestas da origem neste caminho.",
    "empilha": lambda c: f"{c.u} entra no topo do caminho (antes: {caminho_atual(c)}).",
    "testa_destino": lambda c: f"{c.u} é o destino {c.destino}? " + sim_ou_nao(
        c.u == c.destino, "achou!", "continua."),
    "chegou": lambda c: "Devolve ACHOU: o caminho até o destino é o que está na pilha.",
    "testa_limite": lambda c: "O limite que sobra é 0? " + sim_ou_nao(
        c.limite == 0, f"{c.u} está na profundidade máxima: corte, os vizinhos dele não são examinados.",
        f"ainda dá para descer {c.limite} aresta(s)."),
    "desempilha_cortado": lambda c: f"{c.u} sai do caminho (o corte não deixa ir além dele).",
    "pinta_cortado": lambda c: f"cor[{c.u}] = Preto: {c.u} já saiu do caminho.",
    "corte": lambda c: f"{c.u} entra na lista dos cortados.",
    "devolve_corte": lambda c: "Devolve CORTE: talvez houvesse caminho depois daqui, mas o limite não deixa ver.",
    "sem_corte": lambda c: "houve_corte = False: nenhum ramo abaixo de " + str(c.u) + " foi cortado, por enquanto.",
    "ignorar_vizinho": lambda c: f"{c.v} já está no caminho ({caminho_atual(c)})? " + sim_ou_nao(
        c.v in c.caminho, "descer nele seria andar em círculo: pula.", f"pode descer em {c.v}."),
    "pula_vizinho": lambda c: "continue: vai para o próximo vizinho.",
    "desce": lambda c: (f"Chama dls({c.v}, limite = {c.limite} − 1 = {c.limite - 1}, prof = {c.prof + 1}): a busca "
                        f"desce para {c.v}; {c.u} espera na pilha de chamadas."),
    "se_achou": lambda c: f"A chamada devolveu {c.resultado.upper()}. É ACHOU? " + sim_ou_nao(
        c.resultado == "achou", "repassa a resposta para cima.", "continua com os outros vizinhos."),
    "repassa_achou": lambda c: "Devolve ACHOU para quem chamou (o caminho fica como está).",
    "se_cortou": lambda c: f"A chamada devolveu {c.resultado.upper()}. É CORTE? " + sim_ou_nao(
        c.resultado == "corte", "anota que houve corte.", "nada a anotar."),
    "houve_corte": lambda c: "houve_corte = True: algum ramo abaixo foi cortado pelo limite.",
    "desempilha": lambda c: f"{c.u} sai do topo do caminho: todos os vizinhos dele já foram examinados.",
    "subir": lambda c: f"cor[{c.u}] = Preto: {c.u} já saiu do caminho (pode entrar de novo por outro caminho).",
    "se_houve_corte": lambda c: "Houve corte abaixo? " + sim_ou_nao(
        c.houve_corte, "devolve CORTE.", "devolve FALHA."),
    "devolve_corte_de_baixo": lambda c: "Devolve CORTE: com um limite maior, talvez ache.",
    "devolve_falha": lambda c: "Devolve FALHA: nada abaixo daqui chega ao destino, com nenhum limite.",
}

ITERATIVA = dict(LIMITADA)
ITERATIVA.update({
    "limite_zero": lambda c: "limite = 0: a primeira rodada só olha a própria origem.",
    "cada_rodada": lambda c: f"Começa a rodada com limite {c.limite} (o laço só para pelo return).",
    "pinta_branco": lambda c: f"cor[{c.v}] = Branco: na rodada nova, ninguém está no caminho.",
    "pai_nulo": lambda c: f"pai[{c.v}] = None.",
    "zera_prof": lambda c: "prof = {}: as profundidades da rodada anterior são esquecidas.",
    "esvazia_caminho": lambda c: "caminho = []: a rodada começa com o caminho vazio.",
    "nova_iteracao": lambda c: "cortados = []: nenhum corte nesta rodada, por enquanto.",
    "chama_dls": lambda c: (f"Chama dls({c.s}, destino = {c.destino}, limite = {c.limite}, prof = 0): a busca "
                            f"limitada inteira, agora com limite {c.limite}."),
    "se_nao_cortou": lambda c: f"A rodada devolveu {c.resultado.upper()}. É diferente de CORTE? " + sim_ou_nao(
        c.resultado != "corte", "achou ou não existe caminho: um limite maior não mudaria nada.",
        "houve corte: vale tentar com um limite maior."),
    "devolve": lambda c: f"Devolve {c.resultado.upper()}.",
    "aumenta_limite": lambda c: f"limite = {c.limite} + 1 = {c.limite + 1}: a próxima rodada desce mais um nível.",
})


# ----------------------------------------------------------------------
# Busca bidirecional
# ----------------------------------------------------------------------

def nome_do_lado(lado):
    if lado == "frente":
        return "a frente"
    return "trás"


BIDIRECIONAL = {
    "pinta_branco": lambda c: f"cor[{c.v}] = Branco: nenhuma das duas buscas viu {c.v}.",
    "sem_lado": lambda c: f"lado[{c.v}] = None: {c.v} ainda não é de nenhum lado.",
    "d_tras_infinito": lambda c: f"d_tras[{c.v}] = ∞: ainda não se sabe chegar de {c.v} até o destino.",
    "pai_nulo": lambda c: f"pai[{c.v}] = None.",
    "inicializar": lambda c: f"pai_tras[{c.v}] = None.",
    "origem_lado": lambda c: f"lado[{c.s}] = frente: a origem é da busca da frente.",
    "origem_d": lambda c: f"d[{c.s}] = 0: a origem está a 0 arestas dela mesma.",
    "origem": lambda c: f"{c.s} entra na fila da frente.",
    "mesmo_vertice": lambda c: f"A origem {c.s} é o destino {c.t}? " + sim_ou_nao(
        c.s == c.t, "não há nada para buscar.", "as duas buscas vão começar."),
    "encontro_na_origem": lambda c: f"encontro = ({c.s}, {c.s}): o caminho é só {c.s}.",
    "devolve_na_origem": lambda c: "Devolve True.",
    "destino_cinza": lambda c: f"cor[{c.t}] = Cinza: o destino {c.t} vai para a fila de trás.",
    "destino_lado": lambda c: f"lado[{c.t}] = trás: o destino é da busca de trás.",
    "destino_d": lambda c: f"d_tras[{c.t}] = 0: o destino está a 0 arestas dele mesmo.",
    "origem_tras": lambda c: f"{c.t} entra na fila de trás.",
    "enquanto_filas": lambda c: (f"Fila da frente: {nomes(list(c.fila))}; fila de trás: {nomes(list(c.fila_tras))}. "
                                 + ("As duas têm alguém: continua." if len(c.fila) > 0 and len(c.fila_tras) > 0
                                    else "Uma delas está vazia: o laço termina.")),
    "expande_frente": lambda c: "Chama expandir(frente): a frente expande uma camada inteira.",
    "achou_pela_frente": lambda c: "A frente encontrou trás: devolve True.",
    "expande_tras": lambda c: "Chama expandir(trás): trás expande uma camada inteira.",
    "achou_por_tras": lambda c: "Trás encontrou a frente: devolve True.",
    "sem_encontro": lambda c: "Uma fila esvaziou sem as buscas se encontrarem: devolve False (não há caminho).",
    "qual_lado": lambda c: f"lado = {c.lado}. É a frente? " + sim_ou_nao(
        c.lado == "frente", "usa a fila, a lista e os campos da frente.", "usa os de trás (arestas ao contrário)."),
    "usa_frente": lambda c: "fila, adj, d, pai = os da frente; o outro lado é trás.",
    "usa_tras": lambda c: "fila, adj, d, pai = os de trás (adj_tras: quem chega em cada vértice); o outro lado é a frente.",
    "nova_camada": lambda c: (f"tamanho = {len(c.fila)}: a camada de {nome_do_lado(c.lado)} são os que estão na fila "
                              f"agora ({nomes(list(c.fila))}); quem entrar depois espera a próxima vez."),
    "cada_da_camada": lambda c: f"Pega o próximo da camada (são {c.tamanho} no total).",
    "desenfileirar": lambda c: f"Tira {c.fila[0]} do começo da fila de {nome_do_lado(c.lado)}.",
    "se_do_outro_lado": lambda c: f"{c.v} é do outro lado ({c.outro})? " + sim_ou_nao(
        c.lado_do(c.v) == c.outro, "as buscas se encontraram!",
        "não; " + (f"{c.v} ainda não foi visto." if c.lado_do(c.v) is None else f"{c.v} é deste mesmo lado.")),
    "encontro": lambda c: f"encontro = ({c.u}, {c.v}): o caminho passa pela aresta entre {c.u} e {c.v}.",
    "devolve_encontro": lambda c: "Devolve True.",
    "ignorar_vizinho": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} vai ser descoberto por {nome_do_lado(c.lado)}.",
        f"{c.v} já foi descoberto por este lado ({c.cor[c.v]})."),
    "anota_lado": lambda c: f"lado[{c.v}] = {c.lado}.",
    "d_mais_um": lambda c: f"d[{c.v}] = d[{c.u}] + 1 = {n(c.d[c.u])} + 1 = {n(c.d[c.u] + 1)} (deste lado).",
    "descobrir_vizinho": lambda c: f"{c.v} entra no fim da fila de {nome_do_lado(c.lado)}.",
    "terminar_vertice": lambda c: f"cor[{c.u}] = Preto: todos os vizinhos de {c.u} já foram vistos.",
    "camada_sem_encontro": lambda c: "A camada inteira foi expandida sem encontro: devolve False (é a vez do outro lado).",
}


# ----------------------------------------------------------------------
# Floyd-Warshall
# ----------------------------------------------------------------------

FLOYD_WARSHALL = {
    "cada_linha": lambda c: "Pega o próximo vértice i: a linha i da matriz.",
    "nova_linha_d": lambda c: f"Cria a linha d[{c.i}].",
    "nova_linha_pi": lambda c: f"Cria a linha pi[{c.i}].",
    "cada_coluna": lambda c: f"Pega a próxima coluna j da linha {c.i}.",
    "d_infinito": lambda c: f"d[{c.i}][{c.j}] = ∞: ainda não se conhece caminho de {c.i} até {c.j}.",
    "pi_nulo": lambda c: f"pi[{c.i}][{c.j}] = None.",
    "inicializar_linha": lambda c: f"d[{c.i}][{c.i}] = 0: ficar no lugar não custa nada.",
    "cada_arco": lambda c: f"Pega a próxima aresta (u, v, peso) da lista ({len(c.arcos)} no total).",
    "arco_nao": lambda c: f"peso = {n(c.peso)} < d[{c.u}][{c.v}] = {n(c.d[c.u][c.v])}? " + sim_ou_nao(
        c.peso < c.d[c.u][c.v], "é o caminho direto mais barato até agora.",
        "uma aresta paralela mais barata (ou o 0 da diagonal) já está lá."),
    "arco_melhorou": lambda c: f"d[{c.u}][{c.v}] = {n(c.peso)}: o caminho direto pela aresta.",
    "pi_do_arco": lambda c: f"pi[{c.u}][{c.v}] = {c.u}: no caminho direto, quem vem antes de {c.v} é {c.u}.",
    "rodada_k": lambda c: "Começa a rodada do próximo vértice k (depois do último, o laço termina).",
    "cada_i": lambda c: f"Pega a próxima linha i (rodada de k = {c.k}).",
    "cada_j": lambda c: f"Pega a próxima coluna j (par ({c.i}, j), rodada de k = {c.k}).",
    "passa_por_k": lambda c: (f"d[{c.i}][{c.k}] = {n(c.d[c.i][c.k])} ou d[{c.k}][{c.j}] = {n(c.d[c.k][c.j])} é ∞? ")
    + sim_ou_nao(c.d[c.i][c.k] == c.INFINITO_DO_ESTUDO or c.d[c.k][c.j] == c.INFINITO_DO_ESTUDO,
                 f"não dá para passar por {c.k}: pula o par.", f"dá para ir de {c.i} até {c.j} passando por {c.k}."),
    "pula_par": lambda c: "continue: vai para o próximo par.",
    "par_nao": lambda c: (f"d[{c.i}][{c.k}] + d[{c.k}][{c.j}] = {n(c.d[c.i][c.k])} + {n(c.d[c.k][c.j])} = "
                          f"{n(c.d[c.i][c.k] + c.d[c.k][c.j])} < d[{c.i}][{c.j}] = {n(c.d[c.i][c.j])}? ") + sim_ou_nao(
        c.d[c.i][c.k] + c.d[c.k][c.j] < c.d[c.i][c.j], f"passar por {c.k} é mais barato.", "não melhora."),
    "par_melhorou": lambda c: (f"d[{c.i}][{c.j}] = {n(c.d[c.i][c.k] + c.d[c.k][c.j])} (era {n(c.d[c.i][c.j])}): "
                               f"o caminho agora passa por {c.k}."),
    "pi_par": lambda c: (f"pi[{c.i}][{c.j}] = pi[{c.k}][{c.j}] = {c.pi[c.k][c.j]}: quem vem antes de {c.j} é o mesmo "
                         f"do caminho de {c.k} até {c.j}."),
    "verifica_diagonal": lambda c: "Pega o próximo vértice i para conferir a diagonal d[i][i].",
    "testa_diagonal": lambda c: f"d[{c.i}][{c.i}] = {n(c.d[c.i][c.i])} < 0? " + sim_ou_nao(
        c.d[c.i][c.i] < 0, f"sair de {c.i} e voltar custa menos que nada: ciclo negativo.", "tudo certo."),
    "diagonal_negativa": lambda c: "Devolve False: existe ciclo negativo.",
    "sem_ciclo_negativo": lambda c: "Devolve True: sem ciclo negativo, a matriz tem os menores custos.",
}


# ----------------------------------------------------------------------
# Árvore geradora mínima: Prim e Kruskal
# ----------------------------------------------------------------------

def texto_da_entrada_na_arvore(c):
    if c.pai[c.u] is None:
        return f"cor[{c.u}] = Preto: {c.u} entra na árvore como raiz (chave 0)."
    return (f"cor[{c.u}] = Preto: {c.u} entra na árvore pela aresta {c.pai[c.u]} — {c.u} (peso "
            f"{n(c.chave[c.u])}), a mais leve que liga a árvore a alguém de fora.")


PRIM = {
    "pinta_branco": lambda c: f"cor[{c.v}] = Branco: {c.v} começa fora da árvore.",
    "chave_infinito": lambda c: f"chave[{c.v}] = ∞: ainda não se conhece aresta que ligue {c.v} à árvore.",
    "inicializar": lambda c: f"pai[{c.v}] = None: {c.v} ainda não tem ligação com a árvore.",
    "cada_raiz": lambda c: (f"Pega a próxima raiz r da lista ({nomes(c.raizes)}): a escolhida primeiro, depois os "
                            f"outros vértices (o laço termina quando acabarem)."),
    "raiz_branca": lambda c: f"cor[{c.r}] é Branco? " + sim_ou_nao(
        c.cor[c.r] == "Branco", f"{c.r} ainda está fora de qualquer árvore: começa uma árvore nova nele.",
        f"{c.r} já entrou numa árvore ({c.cor[c.r]}): pula."),
    "chama_crescer": lambda c: f"Chama crescer({c.r}): a árvore cresce a partir de {c.r} até a fila esvaziar.",
    "raiz_chave": lambda c: f"chave[{c.r}] = 0: a raiz entra na árvore sem precisar de aresta nenhuma.",
    "raiz_cinza": lambda c: f"cor[{c.r}] = Cinza: a raiz {c.r} vai para a fila.",
    "raiz": lambda c: f"{c.r} entra na fila de prioridade.",
    "chama_extrair": lambda c: "Chama extrair_minimo(): tira da fila o vértice de menor chave (o mais barato de ligar).",
    "extrair": texto_da_entrada_na_arvore,
    "ignorar_vizinho": lambda c: f"cor[{c.v}] é Preto? " + sim_ou_nao(
        c.cor[c.v] == "Preto", f"{c.v} já está na árvore: a aresta {c.u} — {c.v} fecharia um ciclo.",
        f"{c.v} ainda está fora da árvore ({c.cor[c.v]})."),
    "pula_vizinho": lambda c: "continue: vai para o próximo vizinho.",
    "atualizar_nao": lambda c: f"peso = {n(c.peso)} < chave[{c.v}] = {n(c.chave[c.v])}? " + sim_ou_nao(
        c.peso < c.chave[c.v], f"{c.u} — {c.v} é a ligação mais leve conhecida entre {c.v} e a árvore.",
        f"{c.v} já tem uma ligação tão leve ou mais leve."),
    "atualizar_melhorou": lambda c: (f"chave[{c.v}] = {n(c.peso)} (era {n(c.chave[c.v])}): só o peso da aresta, sem "
                                     f"somar nada (no Dijkstra seria d[{c.u}] + peso)."),
    "pai_v": lambda c: f"pai[{c.v}] = {c.u}: a ligação de {c.v} com a árvore passa a ser a aresta {c.u} — {c.v}.",
    "se_branco": lambda c: f"cor[{c.v}] é Branco? " + sim_ou_nao(
        c.cor[c.v] == "Branco", f"{c.v} ainda não está na fila.", f"{c.v} já está na fila: só a chave dele mudou."),
    "entra_na_fila": lambda c: f"{c.v} entra na fila de prioridade, com chave = {n(c.chave[c.v])}.",
    "compara_chave": lambda c: comparar(c, "chave"),
}


# As arestas em ordem de peso, como o sorted vai deixar: "h — g (1), i — c (2)..." (as 12 primeiras)
def arestas_em_ordem(c):
    ordenadas = sorted(c.arestas, key=itemgetter(2))
    partes = []
    for u, v, peso in ordenadas[:12]:
        partes.append(f"{u} — {v} ({n(peso)})")
    if len(ordenadas) > 12:
        partes.append(f"… e mais {len(ordenadas) - 12}")
    if not partes:
        return "Ordena as arestas pelo peso: não há nenhuma."
    return ("Ordena as arestas pelo peso (itemgetter(2) é o peso de cada tupla), da mais leve para a mais pesada: "
            + ", ".join(partes) + ".")


KRUSKAL = {
    "criar_conjunto": lambda c: (f"conjunto[{c.v}] = {c.v}: MAKE-SET, {c.v} começa sozinho, num conjunto só dele "
                                 f"(ele mesmo é o representante)."),
    "ordenar_arestas": arestas_em_ordem,
    "cada_aresta": lambda c: (f"Pega a próxima aresta (u, v, peso) da lista ordenada ({len(c.ordenadas)} no total; o "
                              f"laço termina quando acabarem)."),
    "rejeitar": lambda c: (f"conjunto[{c.u}] = {c.conjunto[c.u]} e conjunto[{c.v}] = {c.conjunto[c.v]}: são iguais? "
                           + sim_ou_nao(c.conjunto[c.u] == c.conjunto[c.v],
                                        f"{c.u} e {c.v} já estão ligados; a aresta fecharia um ciclo e fica de fora.",
                                        "estão em conjuntos diferentes, a aresta liga os dois.")),
    "pula_aresta": lambda c: "continue: vai para a próxima aresta.",
    "aceitar": lambda c: f"A aresta {c.u} — {c.v} (peso {n(c.peso)}) entra na árvore.",
    "unir": lambda c: (f"Chama unir({c.conjunto[c.u]}, {c.conjunto[c.v]}): quem está no conjunto de {c.v} passa para o "
                       f"conjunto de {c.u}."),
    "cada_do_conjunto": lambda c: "Pega o próximo vértice x do grafo (para ver se ele está no conjunto b).",
    "mesmo_conjunto": lambda c: f"conjunto[{c.x}] = {c.conjunto[c.x]} é o conjunto {c.b}? " + sim_ou_nao(
        c.conjunto[c.x] == c.b, f"{c.x} muda de conjunto.", f"{c.x} fica onde está."),
    "muda_conjunto": lambda c: f"conjunto[{c.x}] = {c.a}: {c.x} passa para o conjunto de {c.a}.",
}


EXPLICACOES = {
    algoritmos.PROFUNDIDADE: PROFUNDIDADE,
    algoritmos.LIMITADA: LIMITADA,
    algoritmos.ITERATIVA: ITERATIVA,
    algoritmos.BIDIRECIONAL: BIDIRECIONAL,
    algoritmos.FLOYD_WARSHALL: FLOYD_WARSHALL,
    algoritmos.LARGURA: LARGURA,
    algoritmos.DIJKSTRA: DIJKSTRA,
    algoritmos.BELLMAN_FORD: BELLMAN_FORD,
    algoritmos.GULOSA: GULOSA,
    algoritmos.A_ESTRELA: A_ESTRELA,
    algoritmos.PRIM: PRIM,
    algoritmos.KRUSKAL: KRUSKAL,
}


# A função que explica um rótulo numa busca: a da própria busca ou, se não houver, a comum
def funcao_da_explicacao(algoritmo, rotulo):
    if rotulo in EXPLICACOES[algoritmo]:
        return EXPLICACOES[algoritmo][rotulo]
    return COMUNS.get(rotulo)


# O texto da linha com o rótulo dado, com as variáveis do momento.
# estrito=False (na tela): se der algum erro, a explicação fica vazia em vez de travar a busca.
# Os testes usam estrito=True: toda explicação de toda linha tem que funcionar.
def explicar_linha(algoritmo, rotulo, locais, objeto, estrito=False):
    funcao = funcao_da_explicacao(algoritmo, rotulo)
    if funcao is None:
        if estrito:
            raise KeyError(f"Sem explicação para a linha '{rotulo}' em {algoritmo}")
        return ""
    try:
        return funcao(Contexto(locais, objeto))
    except Exception:
        if estrito:
            raise
        return ""


# ----------------------------------------------------------------------
# O resto do programa: no modo linha a linha, o Python roda o arquivo INTEIRO (o mesmo que a
# exportação do código-fonte grava), desde a primeira linha. As linhas que não são da busca (o
# cabeçalho, os import, a classe, os def, o grafo, a chamada da busca, os print...) têm os rótulos de
# exportacao/codigo_fonte.py e de estudo/estrutura.py; as explicações delas ficam aqui.
# ----------------------------------------------------------------------

# Os rótulos que não são da busca começam com um destes (os da busca são os do código de estudo)
PREFIXOS_DO_PROGRAMA = ("cabecalho_", "principal_", "aux_", "estrutura_", "saida_esperada")


def rotulo_do_programa(rotulo):
    return rotulo is not None and rotulo.startswith(PREFIXOS_DO_PROGRAMA)


# Uma linha que o Python não executa: comentário ou linha em branco
def explicar_comentario(rotulo, linha):
    if linha.strip() == "":
        return "Linha em branco: só separa as partes do código (o Python pula)."
    if rotulo is not None and rotulo.startswith("cabecalho_"):
        return ("Cabeçalho: comentários dizendo o que é este programa e como rodar. O Python ignora tudo o que "
                "vem depois do #.")
    if rotulo == "saida_esperada":
        return ("A saída esperada, num comentário: compare com o painel Saída, que mostra o que o programa "
                "escreveu de verdade.")
    if rotulo == "principal_titulo":
        return "Um comentário que separa as partes do arquivo: daqui para baixo vêm o grafo e a chamada da busca."
    return "Comentário: uma explicação para quem lê o código. O Python ignora (tudo depois do # é comentário)."


# A entrada numa função (o passo na linha do def). parametros: [(nome, valor já em texto), ...]
def explicar_chamada(funcao, parametros):
    lista = ", ".join(f"{nome} = {valor}" for nome, valor in parametros)
    if funcao == "__init__":
        texto = "Entra no construtor __init__, que prepara o objeto novo (o self) e os campos dele"
    else:
        texto = f"Entra na função {funcao}: o Python anota onde parou (a pilha de chamadas cresce) e começa o corpo dela"
    if lista:
        texto += f". Os parâmetros recebem: {lista}"
    return texto + "."


# A volta de uma chamada para o meio de um comando de várias linhas (o print que chamou numero(), por exemplo)
def explicar_volta(codigo):
    return "Voltou da chamada para esta linha, que ainda não terminou: o Python continua de onde parou."


def nome_definido(codigo, palavra):
    achado = codigo.split(palavra, 1)[1].strip()
    return achado.split("(")[0].split(":")[0].strip()


def parametros_do_def(codigo):
    dentro = codigo[codigo.index("(") + 1:codigo.rindex(")")]
    nomes_dos_parametros = [parte.strip() for parte in dentro.split(",") if parte.strip() and parte.strip() != "self"]
    return ", ".join(nomes_dos_parametros)


# Uma linha executada do resto do programa. codigo = o texto da linha (sem os espaços da frente);
# locais = as variáveis do momento (da função, ou as do programa); em_classe = a linha é um def dentro
# de uma classe (um método)
def explicar_linha_do_programa(rotulo, codigo, locais, em_classe=False):
    c = Contexto(locais, None)
    sem_comentario = codigo.split("  #")[0].strip()
    if rotulo == "estrutura_importar":
        if "Decimal" in codigo:
            return ("Importa Decimal: números decimais exatos (0,1 + 0,2 dá exatamente 0,3, sem o erro de "
                    "arredondamento do float).")
        return f"Importa o que o programa vai usar: {sem_comentario}."
    if rotulo.startswith("estrutura_constante_"):
        nome, valor = [parte.strip() for parte in sem_comentario.split("=", 1)]
        return f"Cria a constante {nome} = {valor}: o nome em MAIÚSCULAS avisa que o valor não muda."
    if rotulo == "estrutura_classe":
        return (f"Cria a classe {nome_definido(codigo, 'class')}: o molde do objeto da busca. Os métodos de "
                f"dentro (def) são definidos agora, mas só rodam quando forem chamados.")
    if rotulo == "estrutura_construtor":
        return ("Define o construtor __init__: ele roda sozinho quando o objeto for criado (a linha "
                "\"busca = ...\" lá embaixo).")
    if rotulo.startswith("estrutura_def_") or (rotulo.startswith("aux_") and codigo.startswith("def ")):
        tipo = "o método" if em_classe else "a função"
        return (f"Define {tipo} {nome_definido(codigo, 'def')}({parametros_do_def(codigo)}): só guarda o código; "
                f"o corpo roda quando for chamado.")
    if rotulo.startswith("estrutura_campo_"):
        campo, valor = [parte.strip() for parte in sem_comentario.split("=", 1)]
        return f"{campo} = {valor}: cria o campo {campo[5:]} do objeto (ele continua existindo depois do __init__)."
    if rotulo.startswith("aux_"):
        return explicar_ajudante(sem_comentario, c)
    explicacao = PRINCIPAL.get(rotulo)
    if explicacao is not None:
        return explicacao(c, sem_comentario)
    return "Roda esta linha."


# As funções de ajuda do fim do programa (numero, nome, verdadeiro_ou_falso), linha por linha
def explicar_ajudante(codigo, c):
    if codigo == "x = Decimal(x)":
        return f"x = Decimal({n(c.x)}): o número vira Decimal (decimal exato)."
    if codigo == "if x.is_infinite():":
        return f"x = {n(c.x)} é infinito? " + sim_ou_nao(c.x.is_infinite(), "devolve inf.", "continua.")
    if codigo.startswith("return \"inf\""):
        return "Devolve \"inf\" (ou \"-inf\", se for negativo)."
    if codigo == "if x == x.to_integral_value():":
        return f"x = {n(c.x)} é inteiro? " + sim_ou_nao(c.x == c.x.to_integral_value(), "escreve sem casas decimais.",
                                                         "escreve com as casas decimais.")
    if codigo == "return str(int(x))":
        return f"Devolve \"{int(c.x)}\": o número sem casas decimais."
    if codigo.startswith("return format("):
        return "Devolve o número com as casas decimais, sem os zeros que sobram no fim."
    if codigo.startswith("return \"NIL\""):
        if c.v is None:
            return "v = None: não há vértice, devolve \"NIL\" (como o NIL do livro)."
        return f"v = '{c.v}': devolve o nome \"{c.v}\"."
    if codigo.startswith("return \"VERDADEIRO\""):
        return f"resposta = {c.resposta}: devolve \"{'VERDADEIRO' if c.resposta else 'FALSO'}\"."
    return "Roda esta linha."


def explicar_grafo(c, codigo):
    if codigo.startswith("arcos"):
        return ("arcos = as arestas (u, v, peso), na ordem em que foram criadas: o algoritmo percorre esta lista "
                "inteira.")
    if codigo.startswith("arestas"):
        return ("arestas = as arestas (u, v, peso), uma vez cada, na ordem em que foram criadas: o Kruskal vai "
                "ordenar esta lista pelo peso.")
    return ("adj = a lista de adjacência: para cada vértice, os vizinhos na ordem em que a busca visita (com o peso "
            "de cada aresta, quando a busca usa).")


def explicar_par(c, codigo):
    if codigo.startswith("if (u, v) in busca.tipo"):
        return f"A aresta ({c.u}, {c.v}) foi examinada (tem tipo)? " + sim_ou_nao(
            (c.u, c.v) in c.busca.tipo, "escreve o tipo dela.", "pula.")
    if "for i" in codigo or "for j" in codigo:
        return "Pega o próximo vértice do par (i, j): a matriz é escrita linha por linha."
    return "Pega o próximo vértice do par (u, v): passa por todos os pares de vértices."


# Prim e Kruskal: a soma dos pesos da árvore, no fim do programa
def explicar_soma(c, codigo):
    if "chave" in codigo:
        chave = c.busca.chave[c.v]
        return (f"total = {n(c.total)} + chave[{c.v}] = {n(c.total + chave)}: no fim, a chave de cada vértice é o peso "
                f"da aresta por onde ele entrou na árvore (a raiz tem 0), então somar as chaves dá o peso da árvore.")
    return f"total = {n(c.total)} + {n(c.peso)} = {n(c.total + c.peso)}: soma o peso de mais uma aresta da árvore."


def explicar_encontro(c, codigo):
    if codigo.startswith("if"):
        return "As duas buscas se encontraram? " + sim_ou_nao(c.busca.encontro is not None, "escreve onde.",
                                                              "não há caminho.")
    return "Escreve a aresta onde as duas buscas se encontraram."


# As linhas do programa principal (rótulo -> função(c, código) que explica)
PRINCIPAL = {
    "principal_nomes": lambda c, codigo: ("nomes = os vértices, na ordem em que foram criados (o resultado sai "
                                          "nessa ordem)."),
    "principal_grafo": explicar_grafo,
    "principal_grafo_tras": lambda c, codigo: ("adj_tras = o grafo ao contrário: para cada vértice, quem chega nele "
                                               "(o lado de trás da busca bidirecional anda por aqui)."),
    "principal_h": lambda c, codigo: "h = a heurística: a estimativa do custo de cada vértice até o destino.",
    "principal_ordem": lambda c, codigo: ("ordem = as raízes da DFS, nesta ordem: a origem primeiro, depois os "
                                          "outros vértices em ordem alfabética."),
    "principal_criar": lambda c, codigo: (f"Cria o objeto da busca: {codigo}. O Python chama o construtor __init__ "
                                          f"agora."),
    "principal_buscar": lambda c, codigo: (f"Chama a busca: {codigo.split('#')[0].strip()}. Daqui em diante roda o "
                                           f"algoritmo, linha por linha."),
    "principal_cada_vertice": lambda c, codigo: "Pega o próximo vértice v da lista nomes (o laço termina quando acabarem).",
    "principal_cada_par": explicar_par,
    "principal_escreve_par": explicar_par,
    "principal_escreve_vertice": lambda c, codigo: (
        f"prof = a profundidade de {c.v} no caminho (\"-\" se {c.v} nunca entrou nele)."
        if codigo.startswith("prof =") else "Escreve uma linha do resultado."),
    "principal_escreve_encontro": explicar_encontro,
    "principal_raizes": lambda c, codigo: ("raizes = as raízes do Prim, nesta ordem: a escolhida primeiro, depois os "
                                           "outros vértices em ordem alfabética (uma árvore nova só começa em quem "
                                           "ainda estiver fora)."),
    "principal_total": lambda c, codigo: "total = 0: a soma dos pesos da árvore começa em zero.",
    "principal_soma": explicar_soma,
    "principal_cada_aresta": lambda c, codigo: ("Pega a próxima aresta (u, v, peso) da árvore, na ordem em que ela "
                                                "entrou (o laço termina quando acabarem)."),
}
