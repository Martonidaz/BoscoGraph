# A sessão da visualização: o grafo, as opções da busca e tudo o que é calculado a partir deles
# (os passos, o rastro do linha a linha, o estado da tela em cada passo), num lugar só.
#
# A tela por partes (visual/visualizacao.py) tem várias partes que olham o MESMO grafo: Vértices,
# Arestas, Pesos, Lista, Matrizes, Tipo, Passo a passo, Linha a linha... Em vez de cada parte calcular
# as coisas de novo, todas perguntam para a sessão. Quando o grafo muda (um peso, a orientação, um
# nome), a sessão recalcula tudo e as partes se redesenham.
#
# Este arquivo não usa Tkinter: os testes conferem a sessão sem abrir janela.

import copy
import datetime

import algoritmos
import entrada
import modelos
from estudo import estrutura, rastreador
from exportacao import codigo_fonte
from visual import perfis
from visual.estado import EstadoVisual

# Em que etapa está cada passo: 1 vértices, 2 arestas, 3 listas, 4 ordenação, 5 a busca, 6 o resultado
ETAPAS_DA_MONTAGEM = {"criar_vertice": 1, "criar_aresta": 2, "criar_lista": 3, "adicionar_vizinho": 3,
                      "ordenar": 4, "sem_ordenar": 4}


def etapa_do_passo(passo):
    tipo = passo["tipo"]
    if tipo in ETAPAS_DA_MONTAGEM:
        return ETAPAS_DA_MONTAGEM[tipo]
    if tipo.startswith("tipo_") or tipo.startswith("resultado_") or tipo == "ordem_topologica":
        return 6
    return 5


# A cada tantos passos, o estado da tela fica guardado (uma "foto"): para mostrar o passo 1530,
# a sessão parte da foto do passo 1500 em vez de aplicar os 1530 passos desde o começo
INTERVALO_DAS_FOTOS = 100
TAMANHO_DO_HISTORICO = 50           # quantas mudanças no grafo o Desfazer lembra


class Sessao:
    # configuracao: o dicionário que o editor (ou a tela inicial, ou um arquivo .bosco) monta;
    # montar_passos: a função do boscograph.py
    def __init__(self, configuracao, montar_passos):
        self.montar_passos = montar_passos
        self.configuracao = configuracao
        self.titulo = configuracao.get("titulo", "Grafo")
        self.nome = configuracao.get("nome", self.titulo)
        self.vertices = list(configuracao["vertices"])
        self.arestas = list(configuracao["arestas"])
        self.direcionado = configuracao["direcionado"]
        self.heuristica = dict(configuracao.get("heuristica") or {})
        self.posicoes = dict(configuracao.get("posicoes") or {})
        self.ordenar = configuracao.get("ordenar", True)
        self.algoritmo = configuracao.get("algoritmo", algoritmos.PROFUNDIDADE)
        self.inicio = configuracao.get("inicio")
        self.destino = configuracao.get("destino")
        self.limite = configuracao.get("limite")
        if self.limite is None:
            self.limite = 3                 # o limite sugerido para a busca limitada
        self.historico = []
        self.recalcular()

    # ------------------------------------------------------------------
    # O grafo e as opções
    # ------------------------------------------------------------------

    def informacoes_da_busca(self):
        return algoritmos.algoritmo(self.algoritmo)

    # A origem que a busca usa de fato (sem escolha: a primeira em ordem alfabética)
    def origem(self):
        if self.inicio in self.vertices:
            return self.inicio
        if self.vertices:
            return sorted(self.vertices)[0]
        return None

    # O destino que vale para a busca escolhida (as buscas sem destino ignoram o escolhido)
    def destino_da_busca(self):
        if self.informacoes_da_busca()["destino"] == "nao":
            return None
        if self.destino in self.vertices:
            return self.destino
        return None

    def limite_da_busca(self):
        if self.informacoes_da_busca()["usa_limite"]:
            return self.limite
        return None

    # O grafo com as opções, no formato de modelos.novo_grafo (para o editor, os modelos e o .bosco)
    def grafo(self):
        arrumacao = self.configuracao.get("arrumacao")
        return modelos.novo_grafo(self.vertices, self.arestas, self.ordenar, self.inicio, self.direcionado,
                                  self.algoritmo, self.destino, self.heuristica, self.posicoes, arrumacao,
                                  self.limite if self.informacoes_da_busca()["usa_limite"] else None)

    def tem_pesos(self):
        return entrada.tem_pesos(self.arestas)

    def tem_nomes_de_aresta(self):
        for origem, destino, nome, peso in self.arestas:
            if nome != "":
                return True
        return False

    # "Prova 01 · orientado · 16 vértices, 24 arestas"
    def descricao(self):
        orientacao = "orientado" if self.direcionado else "não orientado"
        return f"{self.titulo} · {orientacao} · {entrada.resumo(self.vertices, self.arestas, self.direcionado)}"

    # ------------------------------------------------------------------
    # Mudanças (cada uma guarda o estado anterior, para o Desfazer)
    # ------------------------------------------------------------------

    def foto(self):
        return {"vertices": list(self.vertices), "arestas": list(self.arestas), "direcionado": self.direcionado,
                "heuristica": dict(self.heuristica), "posicoes": dict(self.posicoes), "ordenar": self.ordenar,
                "algoritmo": self.algoritmo, "inicio": self.inicio, "destino": self.destino, "limite": self.limite}

    def restaurar(self, foto):
        self.vertices = list(foto["vertices"])
        self.arestas = list(foto["arestas"])
        self.direcionado = foto["direcionado"]
        self.heuristica = dict(foto["heuristica"])
        self.posicoes = dict(foto["posicoes"])
        self.ordenar = foto["ordenar"]
        self.algoritmo = foto["algoritmo"]
        self.inicio = foto["inicio"]
        self.destino = foto["destino"]
        self.limite = foto["limite"]

    # Muda o que vier (as chaves de foto()) e recalcula tudo. Devolve True se algo mudou.
    def mudar(self, **mudancas):
        antes = self.foto()
        depois = dict(antes)
        for chave in mudancas:
            depois[chave] = mudancas[chave]
        # A heurística e as posições acompanham os vértices (quem saiu do grafo é esquecido)
        depois["heuristica"] = entrada.manter_chaves(depois["heuristica"], depois["vertices"])
        depois["posicoes"] = entrada.manter_chaves(depois["posicoes"], depois["vertices"])
        if depois == antes:
            return False
        self.historico.append(antes)
        if len(self.historico) > TAMANHO_DO_HISTORICO:
            self.historico.pop(0)
        self.restaurar(depois)
        self.recalcular()
        return True

    def desfazer(self):
        if not self.historico:
            return False
        self.restaurar(self.historico.pop())
        self.recalcular()
        return True

    # ------------------------------------------------------------------
    # Os passos
    # ------------------------------------------------------------------

    # Recalcula tudo depois de uma mudança:
    #   passos_do_grafo -> os passos da DFS (sempre rodam): as etapas 1 a 4 (montar o grafo) servem para
    #                      as partes do grafo, e a etapa 6 da DFS é a parte "Tipo do grafo";
    #   passos          -> os passos da busca escolhida (None se ela não pode rodar: veja problemas)
    def recalcular(self):
        self.fotos = {}
        self.fotos_do_grafo = {}
        self.rastro = None
        self.rastro_calculado = False
        self.problema_da_linha = None
        self.programas_prontos = None
        self.problemas, self.avisos = algoritmos.conferir(self.algoritmo, self.vertices, self.arestas,
                                                          self.direcionado, self.inicio, self.destino_da_busca(),
                                                          self.heuristica, self.limite_da_busca(), self.ordenar)
        if self.vertices:
            self.passos_do_grafo = self.montar_passos(self.vertices, self.arestas, self.ordenar, self.inicio,
                                                      self.direcionado)
        else:
            self.passos_do_grafo = []
        self.passos = None
        if not self.problemas:
            if self.algoritmo == algoritmos.PROFUNDIDADE:
                self.passos = self.passos_do_grafo
            else:
                self.passos = self.montar_passos(self.vertices, self.arestas, self.ordenar, self.inicio,
                                                 self.direcionado, self.algoritmo, self.destino_da_busca(),
                                                 self.heuristica, self.limite_da_busca())
        self.etapas = {}
        self.primeiro_da_etapa = {}
        if self.passos is not None:
            for indice in range(len(self.passos)):
                etapa = etapa_do_passo(self.passos[indice])
                self.etapas[indice] = etapa
                if etapa not in self.primeiro_da_etapa:
                    self.primeiro_da_etapa[etapa] = indice
        # A montagem (etapas 1 a 4): o último passo dela e os passos de cada etapa
        self.ultimo_da_montagem = -1
        self.passos_da_etapa = {1: [], 2: [], 3: [], 4: []}
        for indice in range(len(self.passos_do_grafo)):
            etapa = etapa_do_passo(self.passos_do_grafo[indice])
            if etapa <= 4:
                self.ultimo_da_montagem = indice
                self.passos_da_etapa[etapa].append(indice)

    def pode_buscar(self):
        return self.passos is not None

    # Os índices dos passos da busca (etapa 5) e do resultado (etapa 6)
    def indices_da_busca(self):
        if self.passos is None:
            return []
        lista = []
        for indice in range(len(self.passos)):
            if self.etapas[indice] >= 5:
                lista.append(indice)
        return lista

    def indices_do_resultado(self):
        if self.passos is None:
            return []
        lista = []
        for indice in range(len(self.passos)):
            if self.etapas[indice] == 6:
                lista.append(indice)
        return lista

    # O estado da tela depois do passo "indice" da busca (-1 = antes de qualquer passo).
    # Parte da foto guardada mais próxima, para não aplicar tudo desde o começo.
    def estado_no_passo(self, indice):
        return self.estado_em(self.passos, self.fotos, self.algoritmo, indice)

    # O mesmo, nos passos da DFS (montagem e tipo do grafo)
    def estado_do_grafo(self, indice):
        return self.estado_em(self.passos_do_grafo, self.fotos_do_grafo, algoritmos.PROFUNDIDADE, indice)

    # O grafo montado (depois das etapas 1 a 4), sem nada da busca
    def estado_montado(self):
        return self.estado_do_grafo(self.ultimo_da_montagem)

    def estado_em(self, passos, fotos, algoritmo, indice):
        indice = max(-1, min(indice, len(passos) - 1))
        comeco = -1
        estado = None
        for guardado in fotos:
            if comeco < guardado <= indice:
                comeco = guardado
        if comeco >= 0:
            estado = copy.deepcopy(fotos[comeco])
        else:
            estado = EstadoVisual(self.arestas, self.direcionado, algoritmo)
        for i in range(comeco + 1, indice + 1):
            estado.aplicar(passos[i])
            if (i + 1) % INTERVALO_DAS_FOTOS == 0 and i not in fotos:
                fotos[i] = copy.deepcopy(estado)
        return estado

    # ------------------------------------------------------------------
    # O programa inteiro em cada linguagem e o linha a linha (o Python rodando de verdade)
    # ------------------------------------------------------------------

    # O grafo e as opções da busca, como o gerador de código-fonte recebe (exportacao/codigo_fonte.py)
    def dados_do_programa(self):
        return {"nome": self.nome, "vertices": list(self.vertices), "arestas": list(self.arestas),
                "ordenar": self.ordenar, "inicio": self.origem(), "direcionado": self.direcionado,
                "algoritmo": self.algoritmo, "destino": self.destino_da_busca(),
                "heuristica": dict(self.heuristica), "limite": self.limite_da_busca()}

    # O programa da busca, com o grafo dentro, nas seis linguagens: o mesmo arquivo que "Exportar >
    # Código-fonte" grava, com os rótulos de cada linha (veja estudo/estrutura.py). Calculado uma vez
    # (até o grafo mudar). Devolve {linguagem: programa}; cada programa tem "linhas", "nome",
    # "rotulo_da_linha", "rotulos_da_linha" e "linhas_do_rotulo".
    def programas(self):
        if self.programas_prontos is None:
            nome = codigo_fonte.nome_sugerido(self.algoritmo, self.nome, "python")
            agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            programas = codigo_fonte.programas_com_rotulos(self.dados_do_programa(), nome, agora)
            for programa in programas.values():
                estrutura.completar(programa)
            self.programas_prontos = programas
        return self.programas_prontos

    # Calculado só quando alguma parte precisa (rodar o rastro custa mais que montar os passos).
    # Depois disso:
    #   rastro          -> o resultado de rastreador.rastrear_programa (None = sem linha a linha, o motivo em
    #                      problema_da_linha)
    #   casamento       -> {índice do passo: índice da linha}
    #   passo_da_linha  -> para cada posição j (0 até o total): o último passo da busca já feito
    #   execucoes       -> {número da linha no programa em Python: [posições em que ela roda]}
    def preparar_linha_a_linha(self):
        if self.rastro_calculado:
            return self.rastro is not None
        self.rastro_calculado = True
        if self.passos is None:
            self.problema_da_linha = self.problemas[0] if self.problemas else "A busca não pode rodar."
            return False
        try:
            python = self.programas()["python"]
            rastro = rastreador.rastrear_programa(python, self.algoritmo)
            casamento = rastreador.sincronizar(self.passos, rastro["passos_de_linha"], python["rotulo_da_linha"],
                                               perfis.chave_do_trecho)
        except rastreador.RastroGrandeDemais as problema:
            self.problema_da_linha = str(problema) + " Use o passo a passo."
            return False
        except Exception as problema:
            self.problema_da_linha = f"O linha a linha não ficou disponível para este grafo ({problema})."
            return False
        self.rastro = rastro
        self.casamento = casamento
        self.total_de_linhas = len(rastro["passos_de_linha"])
        ultimo_da_montagem = -1
        for indice in range(len(self.passos)):
            if self.etapas[indice] <= 4:
                ultimo_da_montagem = indice
        pares = sorted(casamento.items())
        self.passo_da_linha = []
        indice_do_passo = ultimo_da_montagem
        proximo = 0
        for posicao in range(self.total_de_linhas + 1):
            while proximo < len(pares) and pares[proximo][1] < posicao:
                indice_do_passo = pares[proximo][0]
                proximo += 1
            self.passo_da_linha.append(indice_do_passo)
        # Cada linha de um comando (o dicionário adj tem várias) leva às vezes em que o comando roda
        self.execucoes = {}
        for posicao in range(self.total_de_linhas):
            for numero in rastro["passos_de_linha"][posicao]["linhas"]:
                self.execucoes.setdefault(numero, []).append(posicao)
        return True

    # A posição do linha a linha que mostra o mesmo desenho do passo
    def linha_do_passo(self, indice):
        if indice < 0 or self.etapas.get(indice, 5) <= 4:
            return 0
        if indice in self.casamento:
            return self.casamento[indice] + 1
        if self.etapas.get(indice) == 6:
            return self.total_de_linhas
        # Um passo da busca sem linha própria: a linha do último passo antes dele que tem
        anterior = 0
        for passo, linha in sorted(self.casamento.items()):
            if passo <= indice:
                anterior = linha + 1
        return anterior

    # As linhas do programa em Python que têm o mesmo rótulo de uma linha de outra linguagem
    def linhas_python_do_rotulo(self, rotulo):
        return self.programas()["python"]["linhas_do_rotulo"].get(rotulo, [])

    # As posições em que uma linha do Python roda (a lista de execuções), [] se ela nunca roda
    def posicoes_da_linha(self, numero):
        if not self.preparar_linha_a_linha():
            return []
        return self.execucoes.get(numero, [])
