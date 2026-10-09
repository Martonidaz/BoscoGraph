# Depois da busca: a classificação do grafo, como pede a Parte 1 da prova
# ("responda se o grafo é simples, completo ou valorado"), mais o que a DFS revela:
#
#   orientado ou não  -> escolhido no editor (pares ordenados ou não ordenados)
#   simples           -> sem laço e sem arestas paralelas (slide "Grafos simples")
#   completo          -> simples e com todos os pares de vértices distintos ligados
#   valorado          -> as arestas têm peso (um valor: custo, distância, tempo...)
#   cíclico           -> tem ciclo se, e somente se, a DFS achou alguma aresta de retorno
#   DAG               -> orientado e acíclico; a ordem topológica é a ordem decrescente de f
#   componentes       -> no não orientado, cada árvore da DFS é uma componente conexa
#
# Cada conclusão vira um passo, e a janela mostra esses passos na etapa 6 ("Tipo").

class TipoDoGrafo:

    def __init__(self, grafo, busca, passos):
        self.grafo = grafo
        self.busca = busca
        self.passos = passos
        self.direcionado = grafo.direcionado
        self.nomes = list(grafo.grafo)          # os nomes dos vértices, na ordem de criação
        self.arestas = []                       # (origem, destino, nome, peso), na ordem de criação
        for aresta in grafo.arestas:
            self.arestas.append((aresta.vertice_origem.nome, aresta.vertice_destino.nome, aresta.nome,
                                 aresta.peso))
        self.resultado = {}                     # as conclusões, para quem quiser usar (o editor mostra um resumo)

    # Faz todas as análises, na ordem em que aparecem na tela
    def concluir(self):
        self.anotar_orientacao()
        self.anotar_simples()
        self.anotar_completo()
        self.anotar_valorado()
        self.anotar_ciclos()
        if self.direcionado:
            self.anotar_dag()
        else:
            self.anotar_componentes()
        self.anotar_resumo()

    # Acrescenta um passo com as informações dadas (tipo, mensagem e o que mais vier)
    def anotar(self, tipo, mensagem, dados):
        passo = {"tipo": tipo, "mensagem": mensagem}
        for chave in dados:
            passo[chave] = dados[chave]
        self.passos.append(passo)

    # A chave de um par: ordenado no orientado; no não orientado, A — B e B — A viram a mesma chave
    def chave_do_par(self, origem, destino):
        if self.direcionado or origem <= destino:
            return (origem, destino)
        return (destino, origem)

    def ligacao(self, origem, destino):
        if self.direcionado:
            return f"{origem} -> {destino}"
        return f"{origem} — {destino}"

    # ------------------------------------------------------------------
    # Classificação (Parte 1 da prova)
    # ------------------------------------------------------------------

    def anotar_orientacao(self):
        if self.direcionado:
            mensagem = "Orientado (dígrafo): cada aresta é um par ordenado, então A -> B é diferente de B -> A"
            # Simétrico: toda aresta A -> B tem a volta B -> A (dava para desenhar sem setas)
            pares = []
            for origem, destino, nome, peso in self.arestas:
                if origem != destino:
                    pares.append((origem, destino))
            simetrico = len(pares) > 0
            for origem, destino in pares:
                if (destino, origem) not in pares:
                    simetrico = False
            if simetrico:
                mensagem += ". Toda aresta tem a volta: daria para tratar como não orientado"
        else:
            simetrico = True
            mensagem = "Não orientado: cada aresta é um par não ordenado, então A — B é a mesma aresta que B — A"
        self.resultado["orientado"] = self.direcionado
        self.anotar("tipo_orientacao", mensagem, {"simetrico": simetrico})

    def anotar_simples(self):
        quantidade_do_par = {}
        for origem, destino, nome, peso in self.arestas:
            chave = self.chave_do_par(origem, destino)
            quantidade_do_par[chave] = quantidade_do_par.get(chave, 0) + 1

        lacos = []          # vértices que têm laço
        paralelas = []      # pares que aparecem mais de uma vez
        for origem, destino, nome, peso in self.arestas:
            if origem == destino and origem not in lacos:
                lacos.append(origem)
            chave = self.chave_do_par(origem, destino)
            if quantidade_do_par[chave] > 1 and chave not in paralelas:
                paralelas.append(chave)

        simples = not lacos and not paralelas
        if simples:
            mensagem = "Simples: sim, não tem laço nem arestas paralelas"
        else:
            motivos = []
            if lacos:
                motivos.append("laço em " + ", ".join(lacos))
            if paralelas:
                textos = []
                for origem, destino in paralelas:
                    textos.append(self.ligacao(origem, destino))
                motivos.append("arestas paralelas " + ", ".join(textos))
            mensagem = "Simples: não, tem " + " e ".join(motivos)
        self.resultado["simples"] = simples
        self.anotar("tipo_simples", mensagem, {"simples": simples})

    def anotar_completo(self):
        n = len(self.nomes)
        # Pares de vértices distintos que estão ligados (sem contar repetições)
        ligados = []
        for origem, destino, nome, peso in self.arestas:
            chave = self.chave_do_par(origem, destino)
            if origem != destino and chave not in ligados:
                ligados.append(chave)
        possiveis = n * (n - 1)             # orientado: A -> B e B -> A são pares diferentes
        if not self.direcionado:
            possiveis = possiveis // 2      # não orientado: A — B é um par só (a quantidade de pares de V(2))

        completo = self.resultado["simples"] and len(ligados) == possiveis
        if completo:
            mensagem = f"Completo: sim, todos os {possiveis} pares de vértices estão ligados"
        elif len(ligados) == possiveis:
            mensagem = "Completo: não, todos os pares estão ligados, mas o grafo não é simples"
        else:
            mensagem = f"Completo: não, só {len(ligados)} dos {possiveis} pares de vértices estão ligados"
        if len(self.arestas) == 0:
            mensagem += ". É um grafo vazio (A = {})"
        self.resultado["completo"] = completo
        self.anotar("tipo_completo", mensagem, {"completo": completo, "ligados": len(ligados),
                                                "possiveis": possiveis})

    def anotar_valorado(self):
        com_peso = 0
        for origem, destino, nome, peso in self.arestas:
            if peso is not None:
                com_peso += 1
        total = len(self.arestas)
        if total > 0 and com_peso == total:
            valorado = "sim"
            mensagem = "Valorado: sim, todas as arestas têm peso"
        elif com_peso == 0:
            valorado = "não"
            mensagem = "Valorado: não, as arestas não têm peso"
        else:
            valorado = "em parte"
            mensagem = f"Valorado: em parte, {com_peso} das {total} arestas têm peso"
        self.resultado["valorado"] = valorado
        self.anotar("tipo_valorado", mensagem, {"valorado": valorado})

    # ------------------------------------------------------------------
    # O que a busca revela
    # ------------------------------------------------------------------

    def anotar_ciclos(self):
        retornos = self.busca.arestas_de_retorno
        if not retornos:
            self.resultado["ciclico"] = False
            self.anotar("tipo_ciclo", "Acíclico: a busca não encontrou nenhuma aresta de retorno",
                        {"ciclico": False, "ciclo": [], "retorno": None})
            return

        # Para o exemplo, a primeira aresta de retorno que não é laço (o laço é um ciclo de 1 vértice só)
        escolhida = retornos[0]
        for origem, destino in retornos:
            if origem != destino:
                escolhida = (origem, destino)
                break
        ciclo = self.montar_ciclo(escolhida[0], escolhida[1])

        textos = []
        for origem, destino in retornos:
            textos.append(self.ligacao(origem, destino))
        separador = " -> "
        if not self.direcionado:
            separador = " — "
        quantidade = "1 aresta de retorno"
        if len(retornos) > 1:
            quantidade = f"{len(retornos)} arestas de retorno"
        mensagem = f"Cíclico: {quantidade} ({', '.join(textos)}). Exemplo de ciclo: {separador.join(ciclo)}"
        self.resultado["ciclico"] = True
        self.anotar("tipo_ciclo", mensagem, {"ciclico": True, "ciclo": ciclo, "retorno": escolhida})

    # Monta o ciclo fechado pela aresta de retorno origem -> destino.
    # O destino é um ancestral da origem (estava Cinza, na pilha), então subindo pelos pais
    # a partir da origem chegamos nele. Caminho da árvore + aresta de retorno = ciclo.
    def montar_ciclo(self, origem, destino):
        caminho = [origem]
        atual = origem
        while atual != destino:
            atual = self.busca.pai[atual]
            caminho.append(atual)
        caminho.reverse()           # agora o caminho vai do destino (o ancestral) até a origem
        caminho.append(destino)     # e a aresta de retorno volta para o começo
        return caminho

    # O tempo de finalização de um vértice (usado para ordenar: key=... diz "ordene por isto")
    def tempo_de_finalizacao(self, nome):
        return self.busca.f[nome]

    def anotar_dag(self):
        if self.resultado["ciclico"]:
            self.resultado["dag"] = False
            self.anotar("tipo_dag", "Não é DAG: é orientado, mas tem ciclo", {"dag": False})
            return
        self.resultado["dag"] = True
        self.anotar("tipo_dag", "É um DAG (grafo orientado acíclico)", {"dag": True})

        # Ordem topológica: do maior f para o menor (reverse=True inverte a ordem crescente)
        ordem = list(self.nomes)
        ordem.sort(key=self.tempo_de_finalizacao, reverse=True)
        self.resultado["ordem_topologica"] = ordem
        self.anotar("ordem_topologica", "Ordem topológica (f do maior para o menor): " + ", ".join(ordem),
                    {"ordem": ordem})

    def anotar_componentes(self):
        # Cada vértice pertence à árvore da raiz que se alcança subindo pelos pais
        componentes = []
        for raiz in self.busca.raizes:
            componentes.append([])
        for nome in self.nomes:
            atual = nome
            while self.busca.pai[atual] is not None:
                atual = self.busca.pai[atual]
            componentes[self.busca.raizes.index(atual)].append(nome)

        quantidade = len(componentes)
        if not self.resultado["ciclico"] and quantidade == 1:
            forma = "árvore"
            mensagem = "É uma árvore: conexo (1 componente) e sem ciclo"
        elif not self.resultado["ciclico"]:
            forma = "floresta"
            mensagem = f"É uma floresta: {quantidade} árvores (componentes conexas), sem ciclo"
        elif quantidade == 1:
            forma = "conexo"
            mensagem = "Conexo: 1 componente (todos os vértices se alcançam)"
        else:
            forma = f"{quantidade} componentes"
            mensagem = f"Não é conexo: {quantidade} componentes conexas"
        partes = []
        for componente in componentes:
            partes.append("{" + ", ".join(componente) + "}")
        mensagem += ": " + " ".join(partes)
        self.resultado["componentes"] = componentes
        self.resultado["forma"] = forma
        self.anotar("tipo_componentes", mensagem, {"componentes": componentes, "raizes": list(self.busca.raizes)})

    def anotar_resumo(self):
        partes = []
        if self.direcionado:
            partes.append("orientado")
        else:
            partes.append("não orientado")
        if self.resultado["simples"]:
            partes.append("simples")
        else:
            partes.append("não simples")
        if self.resultado["completo"]:
            partes.append("completo")
        else:
            partes.append("não completo")
        if self.resultado["valorado"] == "sim":
            partes.append("valorado")
        elif self.resultado["valorado"] == "não":
            partes.append("não valorado")
        else:
            partes.append("valorado em parte")
        if self.resultado["ciclico"]:
            partes.append("cíclico")
        else:
            partes.append("acíclico")
        if self.direcionado and self.resultado["dag"]:
            partes.append("DAG")
        elif self.direcionado:
            partes.append("não é DAG")
        else:
            partes.append(self.resultado["forma"])
        self.resultado["resumo"] = " · ".join(partes)

        # Versão curta, para o editor: só o que mais muda de um grafo para outro
        curtas = [partes[0], partes[1]]
        if self.resultado["completo"]:
            curtas.append("completo")
        if self.resultado["valorado"] == "sim":
            curtas.append("valorado")
        curtas.append(partes[4])        # cíclico ou acíclico
        curtas.append(partes[5])        # DAG, não é DAG, árvore, floresta...
        self.resultado["resumo_curto"] = " · ".join(curtas)

        self.anotar("tipo_resumo", "Resumo: " + self.resultado["resumo"],
                    {"resumo": self.resultado["resumo"], "resumo_curto": self.resultado["resumo_curto"]})
