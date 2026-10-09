# Explicação didática de cada passo: o "porquê" do que acabou de acontecer.
# A janela mostra este texto embaixo da mensagem do passo.
# Este arquivo não usa Tkinter: os testes conferem que todo passo tem explicação.

import algoritmos
from entrada import formatar_numero


def explicar(algoritmo, passo):
    tipo = passo["tipo"]
    texto = explicar_montagem(passo)
    if texto:
        return texto
    if algoritmo == algoritmos.PROFUNDIDADE:
        texto = explicar_profundidade(passo)
        if texto:
            return texto
        return explicar_tipo(passo)
    if tipo.startswith("resultado_"):
        return explicar_resultado(algoritmo, passo)
    if algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
        return explicar_limitada(passo)
    if algoritmo == algoritmos.BIDIRECIONAL:
        return explicar_bidirecional(passo)
    if algoritmo == algoritmos.FLOYD_WARSHALL:
        return explicar_floyd_warshall(passo)
    if algoritmo == algoritmos.LARGURA:
        return explicar_largura(passo)
    if algoritmo == algoritmos.BELLMAN_FORD:
        return explicar_bellman_ford(passo)
    if algoritmo == algoritmos.GULOSA:
        return explicar_gulosa(passo)
    if algoritmo == algoritmos.A_ESTRELA:
        return explicar_a_estrela(passo)
    if algoritmo == algoritmos.PRIM:
        return explicar_prim(passo)
    if algoritmo == algoritmos.KRUSKAL:
        return explicar_kruskal(passo)
    return explicar_dijkstra(passo)


# Etapas 1 a 4 (iguais em todas as buscas): vértices, arestas, listas de adjacência e ordenação
def explicar_montagem(passo):
    tipo = passo["tipo"]
    if tipo == "criar_vertice":
        return "Cada nome vira um objeto Vertice, guardado no dicionário com o nome como chave."
    if tipo == "criar_aresta":
        texto = ("O objeto Aresta liga dois objetos Vertice. Ele ainda não faz parte do grafo: "
                 "por isso a aresta aparece tracejada.")
        if passo.get("peso") is not None:
            texto += " O peso fica guardado na própria aresta (aresta.peso)."
        return texto
    if tipo == "criar_lista":
        vertice = passo["vertice"]
        return f"O Grafo cria a lista de vizinhos de {vertice}, vazia por enquanto (Adj[{vertice}] no pseudocódigo)."
    if tipo == "adicionar_vizinho" and passo.get("volta"):
        origem = passo["origem"]
        destino = passo["destino"]
        return (f"Não orientado: a aresta {destino} — {origem} é um par não ordenado e vale nos dois sentidos, "
                f"então {destino} também entra na lista de {origem}. Cada aresta aparece em duas listas.")
    if tipo == "adicionar_vizinho":
        origem = passo["origem"]
        destino = passo["destino"]
        return (f"{destino} entra no fim da lista de {origem}: a aresta {origem} -> {destino} "
                f"passa a fazer parte do grafo (a linha fica sólida).")
    if tipo == "ordenar":
        texto = "A ordem alfabética é o critério de desempate: decide qual vizinho a busca visita primeiro."
        # Se os nomes têm números, vale lembrar que a comparação é de texto, e não de número
        for nome in [passo["vertice"]] + passo["lista"]:
            for caractere in nome:
                if caractere in "0123456789":
                    return (texto + " Ela compara texto: \"10\" viria antes de \"2\" "
                                    "(por isso os números gerados têm zero à esquerda: \"02\" vem antes de \"10\").")
        return texto
    if tipo == "sem_ordenar":
        return ("Sem ordenar, a busca visita os vizinhos na ordem em que as arestas foram criadas, "
                "e o resultado pode mudar nos empates.")
    return ""


# ----------------------------------------------------------------------
# Busca em profundidade (DFS) e o tipo do grafo
# ----------------------------------------------------------------------

def explicar_profundidade(passo):
    tipo = passo["tipo"]
    if tipo == "pintar_branco":
        return "Início do DFS(G): toda cor começa Branco, que quer dizer \"ainda não descoberto\"."
    if tipo == "zerar_tempo":
        return "O relógio começa em 0. Cada descoberta e cada finalização somam 1."
    if tipo == "nova_arvore":
        return (f"{passo['vertice']} ainda está Branco no laço de fora do DFS(G): "
                f"vira a raiz de uma nova árvore da floresta de busca.")
    if tipo == "descobrir":
        vertice = passo["vertice"]
        return (f"Primeira vez que a busca chega em {vertice}: d[{vertice}] = {passo['tempo']}. "
                f"{vertice} fica Cinza e entra no topo da pilha.")
    if tipo == "finalizar":
        vertice = passo["vertice"]
        return (f"Todos os vizinhos de {vertice} foram examinados: f[{vertice}] = {passo['tempo']}. "
                f"{vertice} fica Preto e sai do topo da pilha.")
    if tipo == "examinar":
        origem = passo["origem"]
        destino = passo["destino"]
        classe = passo["classe"]
        if classe == "arvore":
            return f"{destino} ainda não foi descoberto: a busca desce para ele (recursão) e {origem} fica esperando."
        if classe == "retorno" and origem == destino:
            return f"Laço: a aresta sai de {origem} e volta para ele mesmo, que está Cinza. É um ciclo de tamanho 1."
        if classe == "retorno":
            return (f"{destino} está Cinza, ou seja, ainda está na pilha: a aresta volta para um ancestral "
                    f"e fecha um ciclo.")
        if classe == "avanco":
            return f"{destino} já terminou e foi descoberto depois de {origem}: é descendente de {origem}."
        return f"{destino} já terminou e foi descoberto antes de {origem}: está em outro ramo ou em outra árvore."
    if tipo == "revisitar":
        origem = passo["origem"]
        destino = passo["destino"]
        return (f"{destino} aparece na lista de {origem}, mas essa aresta já foi examinada a partir de {destino}. "
                f"No não orientado cada aresta está em duas listas e só conta uma vez: por isso só existem "
                f"arestas de árvore e de retorno.")
    return ""


# Explicações da etapa 6 da DFS (tipo do grafo): a teoria por trás de cada conclusão
def explicar_tipo(passo):
    tipo = passo["tipo"]
    if tipo == "tipo_orientacao":
        return ("Orientado (dígrafo): as arestas são pares ordenados, tirados de V². "
                "Não orientado: pares não ordenados, tirados de V(2).")
    if tipo == "tipo_simples":
        return "Um grafo simples não pode ter laço nem arestas paralelas (slide \"Grafos simples\")."
    if tipo == "tipo_completo":
        return ("Completo: é simples e todo par de vértices distintos está ligado (A = V(2)). "
                "Com n vértices: n(n − 1)/2 arestas no não orientado e n(n − 1) no orientado.")
    if tipo == "tipo_valorado":
        return ("Valorado (ou ponderado): as arestas têm um valor, como custo, distância ou tempo (RTT numa rede). "
                "Aqui o valor é o peso de cada aresta.")
    if tipo == "tipo_ciclo" and passo["ciclico"]:
        return ("Uma aresta de retorno chega num vértice Cinza, que ainda está na pilha: é um ancestral. "
                "O caminho da árvore até ele mais a aresta de retorno formam um ciclo.")
    if tipo == "tipo_ciclo":
        return ("Sem aresta de retorno não há ciclo: a DFS encontra um ciclo se, e somente se, "
                "encontra uma aresta de retorno.")
    if tipo == "tipo_dag" and passo["dag"]:
        return ("DAG = directed acyclic graph (grafo orientado acíclico). Modela dependências: "
                "pré-requisitos de disciplinas, etapas de uma compilação, tarefas de um pipeline de dados.")
    if tipo == "tipo_dag":
        return "Em um DAG não pode existir ciclo: seguindo as setas, nunca se volta ao ponto de partida."
    if tipo == "ordem_topologica":
        return ("Em um DAG, ordenar pelo tempo f do maior para o menor dá uma ordem topológica: "
                "arrumados em linha, todas as setas apontam para a direita. É o mesmo que pôr cada vértice "
                "no começo de uma lista no momento em que ele fica Preto.")
    if tipo == "tipo_componentes":
        return ("No não orientado, cada nova árvore da busca começa numa parte que não se liga às anteriores: "
                "cada árvore é uma componente conexa (as raízes estão marcadas). Conexo e sem ciclo = árvore.")
    if tipo == "tipo_resumo":
        return "Esta é a classificação da Parte 1 da prova, mais o que a busca em profundidade descobriu."
    return ""


# ----------------------------------------------------------------------
# Busca em largura (BFS)
# ----------------------------------------------------------------------

def explicar_largura(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("Início do BFS(G, s): todo vértice começa Branco, com d = ∞ (ainda não se sabe chegar nele) "
                "e sem pai.")
    if tipo == "origem":
        return ("A origem está a 0 arestas dela mesma. Ela entra na fila, e é a fila que decide a ordem da busca: "
                "o primeiro que entra é o primeiro que sai.")
    if tipo == "desenfileirar":
        return ("Sai sempre quem está na frente da fila, ou seja, quem foi descoberto há mais tempo. Por isso a "
                "busca anda em camadas: primeiro todos a 1 aresta da origem, depois todos a 2, e assim por diante.")
    if tipo == "descobrir_vizinho":
        origem = passo["origem"]
        destino = passo["destino"]
        return (f"{destino} é descoberto agora, a partir de {origem}: fica a d[{origem}] + 1 = {passo['distancia']} "
                f"arestas da origem. Entra no FIM da fila, atrás dos que já estavam esperando.")
    if tipo == "ignorar_vizinho":
        return (f"{passo['destino']} já foi descoberto. A BFS nunca descobre um vértice duas vezes: o primeiro "
                f"caminho que o alcançou já tem o menor número de arestas.")
    if tipo == "terminar_vertice":
        return f"Todos os vizinhos de {passo['vertice']} foram examinados: {passo['vertice']} fica Preto."
    return ""


# ----------------------------------------------------------------------
# Busca em profundidade limitada e aprofundamento iterativo
# ----------------------------------------------------------------------

def explicar_limitada(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("Branco = ainda fora do caminho. A busca limitada não guarda \"visitados\" como a DFS do Cormen: "
                "ela só lembra o caminho atual, da origem até onde está.")
    if tipo == "nova_iteracao":
        return (f"Aprofundamento iterativo: uma busca limitada nova, agora com limite {passo['limite']}. Tudo "
                f"recomeça da origem; o trabalho repetido é pequeno, porque a camada mais funda é a maior.")
    if tipo == "entrar":
        if passo["origem"] is None:
            return (f"A busca começa na origem, com profundidade 0. Ela pode descer até {passo['limite']} "
                    f"arestas; a pilha mostra o caminho atual (a pilha da recursão).")
        return (f"Descer = chamar a busca de novo no vizinho, com o limite um a menos. {passo['vertice']} entra no "
                f"topo da pilha: o caminho agora tem {passo['profundidade']} arestas.")
    if tipo == "chegou":
        return ("O teste do destino é feito assim que o vértice entra no caminho. Achou: a resposta sobe pela "
                "recursão sem examinar mais nada, e o caminho é o que está na pilha.")
    if tipo == "corte":
        return (f"Profundidade {passo['profundidade']} = o limite: os vizinhos de {passo['vertice']} não são "
                f"examinados. É o CORTE: pode haver um caminho passando por aqui, mas o limite não deixa ver.")
    if tipo == "ignorar_vizinho":
        return (f"{passo['destino']} já está no caminho atual: descer nele seria andar em círculo "
                f"({passo['destino']} ... {passo['origem']} -> {passo['destino']}). A busca pula esse vizinho.")
    if tipo == "subir":
        if passo["resultado"] == "corte":
            return (f"Todos os vizinhos de {passo['vertice']} foram examinados e algum ramo foi cortado: a resposta "
                    f"é \"corte\" (talvez com um limite maior dê). {passo['vertice']} sai do topo da pilha.")
        return (f"Todos os vizinhos de {passo['vertice']} foram examinados, sem corte e sem achar: a resposta é "
                f"\"falha\". {passo['vertice']} sai do topo da pilha (e pode entrar de novo por outro caminho).")
    return ""


# ----------------------------------------------------------------------
# Busca bidirecional
# ----------------------------------------------------------------------

def explicar_bidirecional(passo):
    tipo = passo["tipo"]
    lado = passo.get("lado")
    if tipo == "inicializar":
        return "Duas buscas em largura vão rodar: uma a partir da origem (frente) e outra a partir do destino (trás)."
    if tipo == "origem":
        return "A frente começa na origem, com d = 0, como na busca em largura."
    if tipo == "origem_tras":
        return ("Trás começa no destino. Ela anda pelas arestas ao contrário: procura quem CHEGA no destino, "
                "depois quem chega nesses, e assim por diante.")
    if tipo == "nova_camada":
        nome = "a frente" if lado == "frente" else "trás"
        return (f"Agora é a vez de {nome}: ela expande uma camada INTEIRA (todos os {passo['tamanho']} que estão na "
                f"fila agora). Os lados se revezam assim até se encontrarem.")
    if tipo == "desenfileirar":
        return "Sai quem está na frente da fila deste lado; os vizinhos dele vão ser examinados."
    if tipo == "descobrir_vizinho":
        arestas = "1 aresta" if passo["distancia"] == 1 else f"{passo['distancia']} arestas"
        if lado == "tras":
            return (f"{passo['destino']} chega em {passo['origem']} (aresta ao contrário): descoberto por trás, a "
                    f"{arestas} do destino.")
        return f"{passo['destino']} descoberto pela frente, a {arestas} da origem."
    if tipo == "ignorar_vizinho":
        return f"{passo['destino']} já foi descoberto por este mesmo lado: nada muda."
    if tipo == "terminar_vertice":
        return f"Todos os vizinhos de {passo['vertice']} foram examinados: {passo['vertice']} fica Preto."
    if tipo == "encontro":
        if passo.get("na_origem"):
            return "Origem e destino são o mesmo vértice: o caminho tem 0 arestas."
        return ("O vizinho já tinha sido descoberto pelo OUTRO lado: existe caminho da origem até ele e dele até o "
                "destino. Como as camadas são expandidas inteiras, este primeiro encontro dá o caminho com menos "
                "arestas.")
    if tipo == "sem_encontro":
        return ("Uma das filas esvaziou: aquele lado já viu tudo o que alcança, sem tocar no outro. Então não existe "
                "caminho da origem até o destino.")
    return ""


# ----------------------------------------------------------------------
# Floyd-Warshall
# ----------------------------------------------------------------------

def explicar_floyd_warshall(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar_linha":
        return (f"Antes de qualquer rodada, d[{passo['vertice']}][{passo['vertice']}] = 0 (ficar no lugar não custa "
                f"nada) e o resto da linha é ∞: ainda não se conhece caminho.")
    if tipo == "arco_inicial":
        if passo["melhorou"]:
            return (f"A aresta {passo['origem']} -> {passo['destino']} é um caminho direto: d[{passo['origem']}]"
                    f"[{passo['destino']}] = o peso dela, e π = {passo['origem']} (quem vem antes de "
                    f"{passo['destino']}).")
        return ("Uma aresta paralela mais cara (ou um laço com peso positivo) nunca faria parte de um caminho mínimo: "
                "a matriz continua com o menor valor.")
    if tipo == "rodada_k":
        return (f"Rodada de {passo['k']}: a partir de agora, os caminhos podem passar por {passo['k']} no meio. "
                f"Cada par (i, j) testa se ir de i até {passo['k']} e de {passo['k']} até j é mais barato. Os "
                f"pares em que d[i][{passo['k']}] ou d[{passo['k']}][j] é ∞ são pulados.")
    if tipo == "comparar_par":
        i = passo["i"]
        j = passo["j"]
        k = passo["k"]
        if passo["melhorou"]:
            return (f"Passar por {k} ficou mais barato: d[{i}][{j}] = {formatar_numero(passo['por_k'])} e "
                    f"π[{i}][{j}] = π[{k}][{j}] (o vértice antes de {j} agora é o do caminho de {k} até {j}). "
                    f"As arestas laranja são os caminhos {i} ⇝ {k} e {k} ⇝ {j}.")
        return (f"O caminho de agora de {i} até {j} já custa {formatar_numero(passo['antes'])}, que não é maior que "
                f"{formatar_numero(passo['por_k'])} (passando por {k}): nada muda.")
    if tipo == "diagonal_negativa":
        return (f"d[{passo['vertice']}][{passo['vertice']}] < 0: sair de {passo['vertice']} e voltar custa menos "
                f"que zero. É um ciclo negativo: dando voltas, o custo diminui sem parar.")
    if tipo == "sem_ciclo_negativo":
        return "A diagonal ficou toda em 0: não há ciclo negativo, e a matriz tem os menores custos de verdade."
    return ""


# ----------------------------------------------------------------------
# Dijkstra e o relaxamento (que o Bellman-Ford e o A* também usam)
# ----------------------------------------------------------------------

def explicar_relaxamento(passo, nome_da_distancia):
    origem = passo["origem"]
    destino = passo["destino"]
    novo = formatar_numero(passo["depois"])
    antes = formatar_numero(passo["antes"])
    if passo["melhorou"]:
        texto = (f"Relaxar = testar se passar por {origem} deixa {destino} mais barato. "
                 f"{nome_da_distancia}[{origem}] + peso = {novo} < {antes}: sim! O {nome_da_distancia} de {destino} "
                 f"diminui e o pai de {destino} passa a ser {origem} (a aresta azul é o melhor caminho conhecido).")
        if passo.get("entrou"):
            texto += f" Antes {destino} estava em ∞ (Branco)."
        return texto
    if passo["antes"] == passo["depois"] or passo["depois"] > passo["antes"]:
        texto = (f"Passar por {origem} custaria {novo}, e {destino} já tem um caminho que custa {antes}: "
                 f"não melhora, nada muda.")
        if passo.get("finalizado"):
            texto += f" {destino} já é definitivo (Preto): com pesos não negativos, ele nunca melhora."
        return texto
    return "Nada muda."


def explicar_dijkstra(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("INITIALIZE-SINGLE-SOURCE: ainda não se conhece caminho nenhum, então d = ∞ (infinito) "
                "e o pai fica vazio (NIL).")
    if tipo == "origem":
        return ("A origem custa 0 até ela mesma. A fila de prioridade guarda os vértices já alcançados, "
                "e sempre sai o de MENOR d.")
    if tipo == "extrair":
        vertice = passo["vertice"]
        return (f"{vertice} tem o menor d da fila. Como nenhum peso é negativo, nenhum outro caminho (passando "
                f"por quem ainda está na fila) pode chegar mais barato: o d de {vertice} é definitivo (Preto).")
    if tipo == "relaxar":
        return explicar_relaxamento(passo, "d")
    return ""


# ----------------------------------------------------------------------
# Bellman-Ford
# ----------------------------------------------------------------------

def explicar_bellman_ford(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return "INITIALIZE-SINGLE-SOURCE: d = ∞ (nenhum caminho conhecido) e sem pai."
    if tipo == "origem":
        return "A origem custa 0 até ela mesma. O Bellman-Ford não usa fila: ele relaxa todas as arestas, rodada a rodada."
    if tipo == "rodada":
        return ("Em cada rodada, todas as arestas são relaxadas, na ordem de criação. Depois da rodada i, estão "
                "certos todos os caminhos mínimos que usam até i arestas. Um caminho mínimo sem ciclo tem no "
                "máximo |V| − 1 arestas, então |V| − 1 rodadas bastam.")
    if tipo == "relaxar":
        texto = explicar_relaxamento(passo, "d")
        if passo["peso"] < 0:
            texto += (" Peso negativo: passar por esta aresta DIMINUI o custo. Por isso o Bellman-Ford não pode "
                      "considerar um vértice definitivo antes do fim, como o Dijkstra faz.")
        return texto
    if tipo == "rodada_sem_mudanca":
        return ("Se nenhuma distância mudou numa rodada inteira, a rodada seguinte faria exatamente as mesmas "
                "contas: nada mudaria de novo. Dá para parar antes.")
    if tipo == "verificar_ciclo":
        return ("Depois de |V| − 1 rodadas, toda distância mínima já está certa, a não ser que exista um ciclo "
                "negativo. A conferência testa cada aresta mais uma vez: se alguma ainda melhora, há ciclo negativo.")
    if tipo == "ciclo_negativo":
        return ("Um ciclo negativo é um ciclo cuja soma dos pesos é negativa. Cada volta nele fica mais barata, "
                "então não existe \"menor caminho\" para quem pode passar por ele.")
    if tipo == "sem_ciclo_negativo":
        return "Nada mais melhora: não há ciclo negativo alcançável e as distâncias são definitivas."
    return ""


# ----------------------------------------------------------------------
# Busca gulosa e A*
# ----------------------------------------------------------------------

def explicar_gulosa(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("Cada vértice tem uma estimativa h de quanto falta até o destino (por exemplo, a distância em "
                "linha reta). A gulosa só olha para h: escolhe quem parece mais perto.")
    if tipo == "origem":
        return "A origem entra na fronteira, uma fila de prioridade. Na gulosa, a prioridade é h: o menor h sai primeiro."
    if tipo == "extrair":
        return (f"{passo['vertice']} tem o menor h da fronteira: parece o mais perto do destino. A gulosa não olha "
                f"quanto já gastou para chegar nele.")
    if tipo == "chegou":
        return ("O destino saiu da fronteira: a busca acaba. O caminho é o que os pais (π) indicam, mas não é "
                "necessariamente o mais barato (veja a etapa 6).")
    if tipo == "descobrir_vizinho":
        return (f"{passo['destino']} entra na fronteira pela primeira vez, com pai {passo['origem']}. Na gulosa, "
                f"um vértice nunca troca de pai: a busca não volta atrás.")
    if tipo == "ignorar_vizinho":
        return (f"{passo['destino']} já foi visto. A gulosa não reavalia caminhos, e por isso pode perder um "
                f"caminho mais barato.")
    if tipo == "nao_chegou":
        return "A fronteira esvaziou: tudo o que dava para alcançar foi expandido, e o destino não estava lá."
    return ""


def explicar_a_estrela(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("g = custo desde a origem (∞: ainda não alcançado). h = estimativa até o destino. "
                "f = g + h estima o custo total de um caminho que passa por ali.")
    if tipo == "origem":
        return "Na origem, g = 0, então f = h. A fronteira é uma fila de prioridade por f: o menor f sai primeiro."
    if tipo == "extrair":
        return (f"{passo['vertice']} tem o menor f = g + h: é o caminho mais promissor, somando o que já gastou "
                f"e o que estima faltar.")
    if tipo == "relaxar":
        texto = explicar_relaxamento(passo, "g")
        if passo.get("melhorou"):
            texto += " Com o g novo, f = g + h também é recalculado."
        if passo.get("reabriu"):
            texto += (f" {passo['destino']} já tinha sido expandido: isso só acontece quando h não é consistente. "
                      f"Ele volta para a fronteira (é reaberto).")
        return texto
    if tipo == "chegou":
        return ("O destino saiu da fronteira com o menor f. Se h é admissível (nunca passa do custo real), nenhum "
                "caminho que ainda está na fronteira pode ser mais barato: este é o de menor custo.")
    if tipo == "nao_chegou":
        return "A fronteira esvaziou: tudo o que dava para alcançar foi expandido, e o destino não estava lá."
    return ""


# ----------------------------------------------------------------------
# Árvore geradora mínima: Prim e Kruskal
# ----------------------------------------------------------------------

def explicar_prim(passo):
    tipo = passo["tipo"]
    if tipo == "inicializar":
        return ("MST-PRIM começa com todos os vértices fora da árvore: chave = ∞ (ainda não se conhece aresta que "
                "ligue o vértice à árvore) e sem pai (NIL).")
    if tipo == "raiz" and passo["arvore"] == 1:
        return ("A raiz entra com chave 0: a árvore começa nela. A fila de prioridade guarda quem já tem uma "
                "ligação conhecida com a árvore, e sempre sai o de MENOR chave.")
    if tipo == "raiz":
        return ("A fila esvaziou, mas ainda há vértices fora: eles estão numa parte do grafo sem nenhuma aresta "
                "até a árvore anterior. Uma árvore nova começa aqui, como no laço de fora do DFS(G); no fim, o "
                "resultado é uma floresta (uma árvore por parte).")
    if tipo == "extrair" and passo["pai"] is None:
        return f"A raiz {passo['vertice']} sai da fila primeiro (chave 0) e é o primeiro vértice da árvore."
    if tipo == "extrair":
        vertice = passo["vertice"]
        pai = passo["pai"]
        return (f"{vertice} tem a menor chave da fila: a aresta {pai} — {vertice} (peso "
                f"{formatar_numero(passo['chave'])}) é a mais leve que liga a árvore a alguém de fora. Escolher a "
                f"aresta mais leve que atravessa a fronteira da árvore é sempre seguro (a propriedade do corte): "
                f"ela entra na árvore e {vertice} fica Preto.")
    if tipo == "ignorar_vizinho":
        origem = passo["origem"]
        destino = passo["destino"]
        if origem == destino:
            return "Um laço liga o vértice a ele mesmo: nunca entra numa árvore (seria um ciclo de uma aresta só)."
        return (f"{destino} já está na árvore (Preto). Ligar {origem} a {destino} de novo fecharia um ciclo, mesmo "
                f"que a aresta seja leve: por isso o Prim pula quem já entrou. (No Dijkstra essa conferência não faz "
                f"falta; aqui faz, porque a chave é o peso de UMA aresta e não uma distância.)")
    if tipo == "atualizar":
        origem = passo["origem"]
        destino = passo["destino"]
        peso = formatar_numero(passo["peso"])
        antes = formatar_numero(passo["antes"])
        if passo["melhorou"]:
            texto = (f"A aresta {origem} — {destino} (peso {peso}) é a ligação mais leve conhecida entre {destino} "
                     f"e a árvore (antes: {antes}). chave[{destino}] = {peso} e π[{destino}] = {origem}; a aresta "
                     f"fica tracejada: ainda pode aparecer uma ligação mais leve. No Dijkstra a conta seria "
                     f"d[{origem}] + peso; no Prim é só o peso da aresta.")
            if passo["entrou"]:
                texto += f" {destino} entra na fila."
            return texto
        return (f"{destino} já tem uma ligação de peso {antes} com a árvore, e esta aresta pesa {peso}: não é mais "
                f"leve, nada muda.")
    return ""


def explicar_kruskal(passo):
    tipo = passo["tipo"]
    if tipo == "criar_conjunto":
        return ("MAKE-SET: no começo, cada vértice é um conjunto sozinho (uma árvore de um vértice só). Os conjuntos "
                "guardam quem já está ligado com quem pelas arestas escolhidas.")
    if tipo == "ordenar_arestas":
        return ("O Kruskal é guloso: examina as arestas da mais leve para a mais pesada, sem olhar para vértice "
                "nenhum em especial. Arestas de mesmo peso ficam na ordem em que foram criadas.")
    if tipo == "aceitar":
        return (f"FIND-SET({passo['origem']}) ≠ FIND-SET({passo['destino']}): as pontas estão em pedaços diferentes, "
                f"que ainda não se tocam. A aresta liga os dois sem formar ciclo, e é a mais leve que sobrou: entra "
                f"na árvore.")
    if tipo == "rejeitar":
        if passo["origem"] == passo["destino"]:
            return "Um laço liga o vértice a ele mesmo: fecharia um ciclo de uma aresta só. Nunca entra."
        return (f"{passo['origem']} e {passo['destino']} já estão no mesmo conjunto: já existe um caminho entre eles "
                f"pelas arestas escolhidas. Com esta aresta, o caminho e ela formariam um ciclo, então ela fica de "
                f"fora (os vértices marcados são esse conjunto).")
    if tipo == "unir":
        return (f"UNION: os dois pedaços viram um só. Todo vértice que tinha o representante {passo['sai']} passa a ter "
                f"{passo['fica']}; a cor de cada pedaço no desenho mostra o conjunto dele.")
    return ""


# ----------------------------------------------------------------------
# Etapa 6 das buscas a partir de uma origem: o resultado
# ----------------------------------------------------------------------

def explicar_resultado(algoritmo, passo):
    tipo = passo["tipo"]
    if tipo == "resultado_distancias" and algoritmo == algoritmos.LARGURA:
        return ("d[v] = o menor número de arestas da origem até v (a BFS não olha os pesos). ∞ = não existe "
                "caminho. Os vértices não alcançados estão marcados.")
    if tipo == "resultado_distancias":
        return ("d[v] = o menor custo (soma dos pesos) da origem até v. ∞ = não existe caminho. Os vértices não "
                "alcançados estão marcados.")
    if tipo == "resultado_arvore":
        return ("As arestas pai -> filho (π) formam uma árvore: o caminho mínimo até qualquer vértice é o caminho "
                "da árvore, da origem até ele.")
    if tipo == "resultado_caminho":
        if not passo["caminho"]:
            return "Não há sequência de arestas que leve da origem ao destino."
        if algoritmo in (algoritmos.LIMITADA, algoritmos.ITERATIVA):
            return "O caminho é a pilha no momento em que o destino entrou: da origem (embaixo) até o destino (no topo)."
        if algoritmo == algoritmos.BIDIRECIONAL:
            return ("O caminho junta as duas metades: da origem até o encontro (subindo pelos pais da frente) e do "
                    "encontro até o destino (seguindo os pais de trás).")
        if algoritmo == algoritmos.FLOYD_WARSHALL:
            return ("O caminho sai da matriz π: o vértice antes do destino é π[origem][destino], o antes dele é "
                    "π[origem][esse], e assim até chegar na origem.")
        return ("O caminho é montado de trás para frente: começa no destino e sobe pelos pais (π) até a origem; "
                "depois a lista é invertida.")
    if tipo == "resultado_ciclo_negativo":
        return ("Com um ciclo negativo alcançável, \"menor caminho\" não existe: sempre dá para dar mais uma volta "
                "e gastar menos. As distâncias encontradas não valem.")
    if tipo == "resultado_comparacao" and algoritmo == algoritmos.BIDIRECIONAL:
        return ("Para comparar, a busca em largura rodou escondida: ela acha a mesma distância, mas expandindo "
                "camadas só a partir da origem, que crescem muito mais.")
    if tipo == "resultado_comparacao":
        return ("Para comparar, o Dijkstra (que não usa estimativa nenhuma) rodou escondido. Uma boa heurística "
                "faz a busca expandir menos vértices; no A* com h admissível, sem perder o caminho de menor custo.")
    if tipo == "resultado_limitada":
        if passo["resultado"] == "corte":
            return ("Corte não é \"não existe\": o limite impediu de olhar mais fundo. Aumente o limite (ou use o "
                    "aprofundamento iterativo, que aumenta sozinho).")
        return ("Sem nenhum corte, a busca viu tudo o que a origem alcança: um limite maior não mudaria nada.")
    if tipo == "resultado_iteracoes":
        return ("Cada rodada repete as de cima, mas a última camada é a maior: no total, o trabalho é parecido com o "
                "da busca em largura, guardando só um caminho na memória.")
    if tipo == "resultado_matriz":
        return ("d[i][j] = o menor custo de i até j, para todos os pares (linha i, coluna j). Para achar o caminho, "
                "siga π[i][j] de trás para frente, até chegar em i.")
    if tipo == "resultado_diagonal_negativa":
        return ("Um vértice com d[i][i] < 0 consegue voltar a si mesmo gastando menos que nada: há um ciclo "
                "negativo no caminho, e menor custo não existe para quem passa por ele.")
    if tipo == "resultado_arvore_minima":
        return ("Árvore geradora: liga todos os n vértices com n − 1 arestas e sem ciclo. Mínima: nenhuma outra "
                "árvore geradora tem a soma dos pesos menor. Num grafo com partes desligadas não existe árvore que "
                "ligue tudo: o resultado é uma floresta, com uma árvore mínima em cada parte (n − partes arestas).")
    if tipo == "resultado_mesmo_peso":
        return ("Prim e Kruskal escolhem as arestas em ordens diferentes, mas os dois sempre chegam ao peso mínimo: "
                "os dois só aceitam a aresta mais leve que atravessa algum corte (a propriedade do corte). Com pesos "
                "repetidos, as arestas podem ser outras; com todos os pesos diferentes, a árvore mínima é única.")
    if tipo == "resultado_heuristica":
        return ("Admissível: h(v) nunca passa do custo real de v até o destino; garante que o A* acha o menor "
                "custo. Consistente: h(u) ≤ peso(u, v) + h(v) em toda aresta; garante que nenhum vértice "
                "precisa ser reaberto. Consistente implica admissível.")
    return ""
