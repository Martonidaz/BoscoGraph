# As partes "O GRAFO" da tela por partes: Vértices, Arestas, Pesos, Lista de adjacência, Matriz de
# adjacência, Matriz de incidência e Tipo do grafo.
#
# Todas têm o mesmo jeito: à esquerda o desenho (que pode ser minimizado) e à direita a tabela (ou a
# matriz) daquela parte. Clicar numa linha da tabela, numa célula da matriz ou no desenho escolhe um
# vértice ou uma aresta, e o escolhido fica na COR DA PARTE nos dois lugares.
#
# O DUPLO CLIQUE edita, na tabela ou no desenho: no vértice renomeia, na aresta renomeia e no peso muda
# o peso. Os botões de cada parte mudam o resto: a orientação, os pesos, a ordem das listas e, na parte
# Tipo do grafo, acrescentam e removem vértices e arestas. Toda mudança tem Ctrl+Z para desfazer.

import random
import tkinter as tk
from tkinter import ttk

import algoritmos
import entrada
import pesos as regras_dos_pesos
import representacoes
from visual import explicacoes
from visual.botoes import Botao, Lembrete, Segmentos
from visual.componentes import BarraDoTocador
from visual.dialogos import DialogoDePesos, DialogoDeTexto
from visual.matrizes import GradeDeMatriz
from visual.parte import Parte, coluna_em, limpar_tabela

# As duas orientações, como aparecem na barra de segmentos: (valor, texto, ícone)
ORIENTACOES = [(True, "Orientado", "aresta_orientada"), (False, "Não orientado", "aresta_simples")]
DICA_DA_ORIENTACAO = ("Orientado: cada aresta tem sentido (A → B). Não orientado: a aresta vale nos dois "
                      "sentidos (A — B). Ctrl+Z desfaz.")


# Uma parte do grafo com o desenho à esquerda e o painel da parte à direita.
# As partes de baixo preenchem montar_painel e mostrar_painel.
class ParteDoGrafo(Parte):
    grupo = "grafo"

    def montar(self, pai):
        self.pai = pai
        pai.columnconfigure(0, weight=1)
        pai.rowconfigure(2, weight=1)
        cabecalho = ttk.Frame(pai)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.columnconfigure(0, weight=1)
        self.criar_titulo(cabecalho).grid(row=0, column=0, sticky="w")
        self.ferramentas = ttk.Frame(pai)
        self.ferramentas.grid(row=1, column=0, sticky="ew", pady=(6, 6))
        self.divisao = ttk.PanedWindow(pai, orient="horizontal")
        self.divisao.grid(row=2, column=0, sticky="nsew")
        self.painel_do_grafo = self.criar_painel_do_grafo(self.divisao, ao_clicar=self.clicou_no_desenho,
                                                          ao_clicar_duas_vezes=self.duplo_clique_no_desenho)
        self.painel_do_grafo.colocar()
        self.direita = ttk.Frame(self.divisao)
        self.direita.columnconfigure(0, weight=1)
        self.direita.rowconfigure(0, weight=1)
        self.divisao.add(self.direita, weight=2)
        self.montar_painel(self.direita)
        if self.escolhas.get("recolhidos", {}).get("grafo"):
            self.painel_do_grafo.recolher()
        else:
            self.posicionar_divisao(self.divisao, 0.5)

    def recolhidos(self):
        return {"grafo": self.painel_do_grafo.recolhido}

    def mostrar(self):
        self.mostrar_painel()
        if self.desenho is not None:
            estado = self.sessao.estado_montado()
            self.desenho.desenhar(estado, self.opcoes_do_desenho(neutro=True, selecao=self.selecao(),
                                                                 **self.opcoes_extras()))

    def opcoes_extras(self):
        return {}

    def selecao(self):
        return None

    def clicou_no_desenho(self, item):
        pass

    # A seleção de uma tabela ligada à escolha: o identificador da linha escolhida vai para escolhas[chave]
    def ligar_selecao(self, tabela, chave):
        def ao_escolher(evento=None):
            selecionados = tabela.selection()
            novo = selecionados[0] if selecionados else None
            if novo != self.escolhas.get(chave):
                self.escolhas[chave] = novo
                self.mostrar()
        tabela.bind("<<TreeviewSelect>>", ao_escolher)

    def selecionar_na_tabela(self, tabela, iid):
        if iid is not None and tabela.exists(iid):
            if tuple(tabela.selection()) != (iid,):
                tabela.selection_set(iid)
            tabela.see(iid)
        elif tabela.selection():
            tabela.selection_remove(tabela.selection())

    # Uma dica que fica sempre à vista na barra de ferramentas, com o lápis: "Duplo clique ... renomeia".
    # Fica à direita (depois dos botões da parte) ou, se a barra não tiver mais nada, à esquerda.
    # Se não couber inteira (janela estreita), ela some sozinha (veja Lembrete.desenhar).
    def criar_lembrete(self, texto, lado="right", pai=None):
        lembrete = Lembrete(pai or self.ferramentas, self.app, texto)
        lembrete.pack(side=lado, padx=(12, 0) if lado == "right" else (0, 0))
        return lembrete

    # O resumo embaixo da tabela, em letra suave, quebrando a linha na largura do painel
    def criar_resumo(self, pai, linha):
        rotulo = ttk.Label(pai, style="Suave.TLabel", justify="left")
        rotulo.grid(row=linha, column=0, sticky="w", pady=(6, 0))
        pai.bind("<Configure>", lambda evento: rotulo.configure(wraplength=max(200, evento.width - 10)), add="+")
        return rotulo

    # "A → B" no orientado, "A — B" no não orientado
    def ligacao(self, origem, destino):
        if self.sessao.direcionado:
            return f"{origem} → {destino}"
        return f"{origem} — {destino}"

    # ------------------------------------------------------------------
    # O duplo clique: renomear vértice, renomear aresta e mudar o peso
    # ------------------------------------------------------------------

    # No desenho: item = ("vertice", nome), ("aresta", número), ("peso", número) ou None (veja
    # DesenhoDoGrafo.item_para_editar: o "peso" é o duplo clique em cima do peso escrito na aresta)
    def duplo_clique_no_desenho(self, item):
        if item is None:
            return
        tipo, qual = item
        if tipo == "vertice":
            self.renomear_vertice(qual)
        elif tipo == "peso":
            self.editar_peso(qual)
        else:
            self.renomear_aresta(qual)

    def renomear_vertice(self, antigo):
        if antigo not in self.sessao.vertices or self.app.dialogo is not None:
            return

        def aplicar(novo):
            if novo == antigo:
                return ""
            outros = [vertice for vertice in self.sessao.vertices if vertice != antigo]
            problema = entrada.validar_nome_de_vertice(novo, outros)
            if problema:
                return problema
            vertices, arestas = entrada.renomear_vertice(self.sessao.vertices, self.sessao.arestas, antigo, novo)
            mudancas = {"vertices": vertices, "arestas": arestas,
                        "heuristica": entrada.renomear_chave(self.sessao.heuristica, antigo, novo),
                        "posicoes": entrada.renomear_chave(self.sessao.posicoes, antigo, novo)}
            if self.sessao.inicio == antigo:
                mudancas["inicio"] = novo
            if self.sessao.destino == antigo:
                mudancas["destino"] = novo
            # O que a parte tinha escolhido com o nome antigo continua escolhido com o nome novo, e o
            # vértice renomeado fica escolhido (nas partes que escolhem vértices)
            for chave in ("vertice", "nova_origem", "novo_destino"):
                if self.escolhas.get(chave) == antigo:
                    self.escolhas[chave] = novo
            if "vertice" in self.escolhas_iniciais:
                self.escolhas["vertice"] = novo
            self.mudar_grafo(f"Vértice {antigo} renomeado para {novo}. Ctrl+Z desfaz.", **mudancas)
            return ""

        DialogoDeTexto(self.app, "Renomear vértice", f"Novo nome para o vértice {antigo}:", antigo, aplicar)

    def renomear_aresta(self, numero):
        if not 0 <= numero < len(self.sessao.arestas) or self.app.dialogo is not None:
            return
        origem, destino, antigo, peso = self.sessao.arestas[numero]

        def aplicar(novo):
            problema = entrada.validar_nome_de_aresta(novo)
            if problema:
                return problema
            if novo == antigo:
                return ""
            arestas = list(self.sessao.arestas)
            arestas[numero] = (origem, destino, novo, peso)
            aviso = f"Aresta {self.ligacao(origem, destino)} agora se chama {novo}. Ctrl+Z desfaz."
            if novo == "":
                aviso = f"Aresta {self.ligacao(origem, destino)} ficou sem nome. Ctrl+Z desfaz."
            self.mudar_grafo(aviso, arestas=arestas)
            return ""

        DialogoDeTexto(self.app, "Renomear aresta",
                       f"Nome da aresta {self.ligacao(origem, destino)} (vazio = sem nome):", antigo, aplicar)

    def editar_peso(self, numero):
        if not 0 <= numero < len(self.sessao.arestas) or self.app.dialogo is not None:
            return
        origem, destino, nome, antigo = self.sessao.arestas[numero]

        def aplicar(texto):
            peso, problema = entrada.ler_numero(texto)
            if problema:
                return problema
            if peso == antigo:
                return ""
            if peso is None:
                aviso = f"Aresta {self.ligacao(origem, destino)} ficou sem peso. Ctrl+Z desfaz."
            else:
                aviso = (f"Aresta {self.ligacao(origem, destino)} agora tem peso {entrada.formatar_numero(peso)}. "
                         f"Ctrl+Z desfaz.")
            self.mudar_grafo(aviso, arestas=entrada.trocar_pesos(self.sessao.arestas, [numero], [peso]))
            return ""

        DialogoDeTexto(self.app, "Peso da aresta",
                       f"Peso da aresta {self.ligacao(origem, destino)} (vazio = sem peso; vírgula ou ponto nos "
                       f"decimais):", entrada.formatar_numero(antigo), aplicar)

    # Toda mudança no grafo passa por aqui (a parte Tipo do grafo acrescenta o que mudou no tipo)
    def mudar_grafo(self, aviso, **mudancas):
        self.tela.mudar_grafo(aviso, **mudancas)


# ----------------------------------------------------------------------
# Vértices
# ----------------------------------------------------------------------

class ParteDosVertices(ParteDoGrafo):
    chave = "vertices"
    titulo = "Vértices"
    descricao = "Os pontos do grafo e com quem cada um se liga."
    escolhas_iniciais = {"vertice": None}

    def montar_painel(self, pai):
        self.criar_lembrete("Duplo clique num vértice (na tabela ou no desenho) renomeia", lado="left")
        colunas = [("numero", "nº", 40, False), ("nome", "Vértice", 90, False)]
        if self.sessao.heuristica or self.sessao.informacoes_da_busca()["usa_heuristica"]:
            colunas.append(("h", "h", 60, False))
        colunas.append(("vizinhos", "Liga-se a", 180, True))
        quadro, self.tabela = self.criar_tabela(pai, colunas, altura=12)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.ligar_selecao(self.tabela, "vertice")
        self.tabela.bind("<Double-1>", self.duplo_clique_na_tabela)
        self.rotulo_resumo = self.criar_resumo(pai, 2)

    def mostrar_painel(self):
        sessao = self.sessao
        limpar_tabela(self.tabela)
        # O grau (quantas pontas de aresta tocam o vértice; o laço conta 2) só entra no resumo de baixo
        grau = entrada.graus_nao_orientados(sessao.vertices, sessao.arestas)
        vizinhos = representacoes.lista_de_saida(sessao.vertices, sessao.arestas, sessao.direcionado)
        colunas = self.tabela.cget("columns")
        maior = None
        for indice in range(len(sessao.vertices)):
            nome = sessao.vertices[indice]
            valores = {"numero": indice + 1, "nome": nome,
                       "h": entrada.formatar_numero(sessao.heuristica.get(nome)) or "—"}
            nomes = []
            for vizinho, peso, numero in vizinhos[nome]:
                if vizinho not in nomes:
                    nomes.append(vizinho)
            valores["vizinhos"] = ", ".join(nomes) or "—"
            linha = []
            for coluna in colunas:
                linha.append(valores[coluna])
            marcas = ("escolhida",) if nome == self.escolhas.get("vertice") else ()
            self.tabela.insert("", "end", iid=nome, values=linha, tags=marcas)
            if maior is None or grau[nome] > maior[1]:
                maior = (nome, grau[nome])
        self.selecionar_na_tabela(self.tabela, self.escolhas.get("vertice"))
        texto = entrada.contar(len(sessao.vertices), "vértice", "vértices")
        if sessao.vertices:
            soma = sum(grau.values())
            texto += f" · maior grau: {maior[0]} ({maior[1]})"
            texto += f" · soma dos graus = {soma} = 2 × {len(sessao.arestas)} arestas"
        self.rotulo_resumo.configure(text=texto)

    def selecao(self):
        nome = self.escolhas.get("vertice")
        if nome not in self.sessao.vertices:
            return None
        arestas = []
        for numero in range(len(self.sessao.arestas)):
            origem, destino, rotulo, peso = self.sessao.arestas[numero]
            if nome in (origem, destino):
                arestas.append(numero)
        return {"vertices": [nome], "arestas": arestas, "cor": self.cor}

    def clicou_no_desenho(self, item):
        if item and item[0] == "vertice":
            self.escolhas["vertice"] = item[1]
            self.mostrar()

    def duplo_clique_na_tabela(self, evento):
        nome = self.tabela.identify_row(evento.y)
        if nome in self.sessao.vertices:
            self.renomear_vertice(nome)
        return "break"


# ----------------------------------------------------------------------
# Arestas
# ----------------------------------------------------------------------

class ParteDasArestas(ParteDoGrafo):
    chave = "arestas"
    titulo = "Arestas"
    descricao = "As ligações: de onde saem, aonde chegam, nome, peso, laços e paralelas."
    escolhas_iniciais = {"aresta": None}

    def montar_painel(self, pai):
        self.orientacao = tk.BooleanVar(value=self.sessao.direcionado)
        Segmentos(self.ferramentas, self.app, ORIENTACOES, self.orientacao, comando=self.mudar_orientacao,
                  dica=DICA_DA_ORIENTACAO).pack(side="left")
        self.criar_lembrete("Duplo clique numa aresta renomeia; em cima do peso, muda o peso")
        colunas = [("numero", "nº", 40, False), ("ligacao", "Aresta", 110, True), ("nome", "Nome", 70, False),
                   ("peso", "Peso", 60, False), ("obs", "Observação", 110, True)]
        quadro, self.tabela = self.criar_tabela(pai, colunas, altura=12)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.ligar_selecao(self.tabela, "aresta")
        self.tabela.bind("<Double-1>", self.duplo_clique_na_tabela)
        self.rotulo_resumo = self.criar_resumo(pai, 2)

    def mostrar_painel(self):
        sessao = self.sessao
        limpar_tabela(self.tabela)
        observacoes = entrada.observacoes(sessao.arestas, sessao.direcionado)
        for numero in range(len(sessao.arestas)):
            origem, destino, nome, peso = sessao.arestas[numero]
            marcas = ("escolhida",) if str(numero) == self.escolhas.get("aresta") else ()
            self.tabela.insert("", "end", iid=str(numero),
                               values=(numero + 1, self.ligacao(origem, destino), nome or "—",
                                       entrada.formatar_numero(peso) or "—", observacoes[numero] or "—"),
                               tags=marcas)
        self.selecionar_na_tabela(self.tabela, self.escolhas.get("aresta"))
        texto = entrada.resumo(sessao.vertices, sessao.arestas, sessao.direcionado)
        densidade = representacoes.densidade(len(sessao.vertices), len(sessao.arestas), sessao.direcionado)
        if densidade is not None:
            maximo = "n(n−1)" if sessao.direcionado else "n(n−1)/2"
            texto += f" · densidade {entrada.formatar_numero(entrada.Decimal(str(round(densidade, 3))))} " \
                     f"(arestas ÷ {maximo})"
        self.rotulo_resumo.configure(text=texto)

    def selecao(self):
        escolhida = self.escolhas.get("aresta")
        if escolhida is None or not escolhida.isdigit() or int(escolhida) >= len(self.sessao.arestas):
            return None
        numero = int(escolhida)
        origem, destino, nome, peso = self.sessao.arestas[numero]
        return {"vertices": [origem, destino], "arestas": [numero], "cor": self.cor}

    def clicou_no_desenho(self, item):
        if item and item[0] == "aresta":
            self.escolhas["aresta"] = str(item[1])
            self.mostrar()

    # Na tabela: na coluna Peso muda o peso; nas outras, renomeia (como no editor)
    def duplo_clique_na_tabela(self, evento):
        linha = self.tabela.identify_row(evento.y)
        if not linha.isdigit():
            return "break"
        if coluna_em(self.tabela, evento.x) == "peso":
            self.editar_peso(int(linha))
        else:
            self.renomear_aresta(int(linha))
        return "break"

    def mudar_orientacao(self):
        novo = self.orientacao.get()
        if novo == self.sessao.direcionado:
            return
        if novo:
            aviso = "Agora o grafo é orientado: cada aresta tem sentido (A → B). Ctrl+Z desfaz."
        else:
            aviso = "Agora o grafo é não orientado: cada aresta vale nos dois sentidos (A — B). Ctrl+Z desfaz."
        self.mudar_grafo(aviso, direcionado=novo)


# ----------------------------------------------------------------------
# Pesos (e a heurística h)
# ----------------------------------------------------------------------

class ParteDosPesos(ParteDoGrafo):
    chave = "pesos"
    titulo = "Pesos"
    descricao = "O custo de cada aresta: pôr, tirar, sortear (e a heurística h dos vértices)."
    escolhas_iniciais = {"aresta": None}

    def montar_painel(self, pai):
        barra = self.ferramentas
        Botao(barra, self.app, "Sortear de 1 a 9", icone="dado", papel="info", comando=self.sortear_rapido,
              dica="Um peso inteiro sorteado de 1 a 9 em cada aresta (para outro intervalo, use Pesos…)").pack(
            side="left")
        Botao(barra, self.app, "Pesos…", icone="etiqueta", papel="neutro", comando=lambda: self.abrir_dialogo("arestas"),
              dica="Mesmo valor, sorteio num intervalo ou tirar, em todas, nas escolhidas ou nas sem peso").pack(
            side="left", padx=(6, 0))
        Botao(barra, self.app, "Tirar todos", icone="lixeira", papel="perigo", comando=self.tirar_todos,
              dica="Tira o peso de todas as arestas (Ctrl+Z desfaz)").pack(side="left", padx=(6, 0))
        self.usa_h = bool(self.sessao.heuristica) or self.sessao.informacoes_da_busca()["usa_heuristica"]
        if self.usa_h:
            Botao(barra, self.app, "Heurística h…", icone="estrela", papel="roxo",
                  comando=lambda: self.abrir_dialogo("vertices"),
                  dica="A estimativa h de cada vértice até o destino (gulosa e A*): valor, sorteio, custo real "
                       "ou admissível").pack(side="left", padx=(14, 0))
        self.criar_lembrete("Duplo clique numa aresta muda o peso" +
                            ("; na tabela h, muda o h" if self.usa_h else ""))
        colunas = [("numero", "nº", 40, False), ("ligacao", "Aresta", 120, True), ("peso", "Peso", 90, False)]
        quadro, self.tabela = self.criar_tabela(pai, colunas, selecao="extended", altura=10)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", self.ao_escolher)
        self.tabela.bind("<Double-1>", self.duplo_clique_na_tabela)
        linha = 2
        if self.usa_h:
            ttk.Label(pai, text="Heurística h (estimativa até o destino)", style="Negrito.TLabel").grid(
                row=1, column=0, sticky="w", pady=(10, 2))
            colunas = [("vertice", "Vértice", 90, True), ("h", "h", 60, False), ("real", "Custo real", 80, False),
                       ("ok", "h ≤ real?", 70, False)]
            quadro, self.tabela_h = self.criar_tabela(pai, colunas, altura=6)
            quadro.grid(row=2, column=0, sticky="nsew")
            self.tabela_h.bind("<Double-1>", self.duplo_clique_na_heuristica)
            pai.rowconfigure(2, weight=1)
            linha = 3
        self.rotulo_resumo = self.criar_resumo(pai, linha)

    def indices_escolhidos(self):
        indices = []
        for iid in self.tabela.selection():
            indices.append(int(iid))
        return indices

    def ao_escolher(self, evento=None):
        escolhidos = self.indices_escolhidos()
        self.escolhas["aresta"] = str(escolhidos[0]) if escolhidos else None
        self.escolhas["arestas"] = escolhidos
        self.desenhar_so()

    def desenhar_so(self):
        if self.desenho is not None:
            estado = self.sessao.estado_montado()
            self.desenho.desenhar(estado, self.opcoes_do_desenho(neutro=True, selecao=self.selecao(),
                                                                 **self.opcoes_extras()))

    def opcoes_extras(self):
        rotulos = {}
        if self.usa_h:
            for vertice in self.sessao.vertices:
                if vertice in self.sessao.heuristica:
                    rotulos[vertice] = "h=" + entrada.formatar_numero(self.sessao.heuristica[vertice])
        return {"pesos": True, "pesos_em_destaque": True, "rotulos": rotulos}

    def mostrar_painel(self):
        sessao = self.sessao
        escolhidos = self.escolhas.get("arestas") or []
        limpar_tabela(self.tabela)
        for numero in range(len(sessao.arestas)):
            origem, destino, nome, peso = sessao.arestas[numero]
            texto = self.ligacao(origem, destino)
            if nome:
                texto += f"  ({nome})"
            marcas = ("suave",) if peso is None else ()
            self.tabela.insert("", "end", iid=str(numero),
                               values=(numero + 1, texto, entrada.formatar_numero(peso) or "sem peso"), tags=marcas)
        presentes = [str(i) for i in escolhidos if i < len(sessao.arestas)]
        if presentes:
            self.tabela.selection_set(presentes)
        estatisticas = representacoes.estatisticas_dos_pesos(sessao.arestas)
        if estatisticas is None:
            texto = "Nenhuma aresta tem peso. O Dijkstra, o Bellman-Ford, o Floyd-Warshall e o A* precisam de pesos."
        else:
            texto = (f"{estatisticas['quantidade']} de {len(sessao.arestas)} arestas com peso · menor "
                     f"{entrada.formatar_numero(estatisticas['menor'])} · maior "
                     f"{entrada.formatar_numero(estatisticas['maior'])} · soma "
                     f"{entrada.formatar_numero(estatisticas['soma'])} · média "
                     f"{representacoes.arredondado(estatisticas['media'])} · mediana "
                     f"{representacoes.arredondado(estatisticas['mediana'])} · desvio padrão "
                     f"{representacoes.arredondado(estatisticas['desvio'])}")
            if estatisticas["negativos"]:
                texto += f" · {entrada.contar(estatisticas['negativos'], 'negativo', 'negativos')}"
        self.rotulo_resumo.configure(text=texto)
        if self.usa_h:
            self.mostrar_heuristica()

    def mostrar_heuristica(self):
        sessao = self.sessao
        limpar_tabela(self.tabela_h)
        destino = sessao.destino
        custo = None
        if destino in sessao.vertices:
            custo = algoritmos.custos_ate_o_destino(sessao.vertices, sessao.arestas, destino, sessao.direcionado)
        for vertice in sessao.vertices:
            h = sessao.heuristica.get(vertice)
            real = "—"
            ok = "—"
            if custo is not None:
                real = entrada.formatar_numero(custo[vertice])
                if h is not None:
                    ok = "sim" if h <= custo[vertice] else "NÃO"
            self.tabela_h.insert("", "end", iid=vertice, values=(vertice, entrada.formatar_numero(h) or "—", real, ok),
                                 tags=("destaque",) if ok == "NÃO" else ())

    def selecao(self):
        escolhidos = self.escolhas.get("arestas") or []
        arestas = [numero for numero in escolhidos if numero < len(self.sessao.arestas)]
        if not arestas:
            return None
        vertices = []
        for numero in arestas:
            origem, destino, nome, peso = self.sessao.arestas[numero]
            vertices += [origem, destino]
        return {"vertices": vertices, "arestas": arestas, "cor": self.cor}

    def clicou_no_desenho(self, item):
        if item and item[0] == "aresta":
            self.escolhas["arestas"] = [item[1]]
            self.tabela.selection_set([str(item[1])])
            self.tabela.see(str(item[1]))

    # Nesta parte, o duplo clique numa aresta (na linha, no nome ou no peso) muda o peso
    def duplo_clique_no_desenho(self, item):
        if item is not None and item[0] in ("aresta", "peso"):
            self.editar_peso(item[1])
        else:
            ParteDoGrafo.duplo_clique_no_desenho(self, item)

    def duplo_clique_na_tabela(self, evento):
        linha = self.tabela.identify_row(evento.y)
        if linha.isdigit():
            self.editar_peso(int(linha))
        return "break"

    def duplo_clique_na_heuristica(self, evento):
        vertice = self.tabela_h.identify_row(evento.y)
        if vertice in self.sessao.vertices:
            self.editar_heuristica(vertice)
        return "break"

    # O h de um vértice: a estimativa de quanto custa ir dele até o destino (não pode ser negativa)
    def editar_heuristica(self, vertice):
        if self.app.dialogo is not None:
            return
        antigo = self.sessao.heuristica.get(vertice)

        def aplicar(texto):
            valor, problema = entrada.ler_numero(texto)
            if problema:
                return problema
            if valor is not None and valor < 0:
                return "A heurística não pode ser negativa: ela estima quanto falta até o destino."
            if valor == antigo:
                return ""
            heuristica = entrada.trocar_heuristicas(self.sessao.heuristica, [vertice], [valor])
            if valor is None:
                aviso = f"O vértice {vertice} ficou sem h. Ctrl+Z desfaz."
            else:
                aviso = f"O vértice {vertice} agora tem h = {entrada.formatar_numero(valor)}. Ctrl+Z desfaz."
            self.mudar_grafo(aviso, heuristica=heuristica)
            return ""

        DialogoDeTexto(self.app, "Heurística h",
                       f"h do vértice {vertice}, a estimativa do custo até o destino (vazio = sem h):",
                       entrada.formatar_numero(antigo), aplicar)

    def sortear_rapido(self):
        if not self.sessao.arestas:
            self.tela.avisar("O grafo não tem arestas.", erro=True)
            return
        pesos = entrada.sortear_numeros(len(self.sessao.arestas), 1, 9, random.randint(0, 10 ** 6))
        arestas = entrada.trocar_pesos(self.sessao.arestas, list(range(len(self.sessao.arestas))), pesos)
        self.mudar_grafo("Pesos sorteados de 1 a 9 em todas as arestas. Ctrl+Z desfaz.", arestas=arestas)

    def tirar_todos(self):
        arestas = entrada.trocar_pesos(self.sessao.arestas, list(range(len(self.sessao.arestas))),
                                       [None] * len(self.sessao.arestas))
        self.mudar_grafo("Pesos tirados de todas as arestas. Ctrl+Z desfaz.", arestas=arestas)

    # O diálogo Pesos… do editor, aqui dentro: "arestas" (o peso) ou "vertices" (a heurística)
    def abrir_dialogo(self, lugar):
        sessao = self.sessao
        escolhidos = self.indices_escolhidos()
        sem_h = 0
        for vertice in sessao.vertices:
            if vertice not in sessao.heuristica:
                sem_h += 1
        destino = sessao.destino if sessao.destino in sessao.vertices else None
        contexto = {
            "arestas": len(sessao.arestas),
            "arestas_selecionadas": len(escolhidos),
            "arestas_sem_peso": len(entrada.indices_sem_peso(sessao.arestas)),
            "vertices": len(sessao.vertices),
            "vertices_selecionados": 0,
            "vertices_sem_h": sem_h,
            "custo_real": regras_dos_pesos.motivo_sem_custo_real(sessao.vertices, sessao.arestas, destino,
                                                                 sessao.direcionado),
            "destino": destino,
            "lugar": lugar,
        }

        def aplicar(escolha):
            arestas, heuristica, aviso, problema = regras_dos_pesos.aplicar_escolha(
                escolha, sessao.vertices, sessao.arestas, sessao.heuristica, sessao.direcionado, destino,
                escolhidos, [])
            if problema:
                return problema
            self.mudar_grafo(aviso, arestas=arestas, heuristica=heuristica)
            return ""

        DialogoDePesos(self.app, contexto, aplicar)


# ----------------------------------------------------------------------
# Lista de adjacência
# ----------------------------------------------------------------------

class ParteDaLista(ParteDoGrafo):
    chave = "lista"
    titulo = "Lista de adjacência"
    descricao = "Para cada vértice, a lista de vizinhos: é o que as buscas percorrem."
    escolhas_iniciais = {"vertice": None}

    def montar_painel(self, pai):
        self.ordenar = tk.BooleanVar(value=self.sessao.ordenar)
        Segmentos(self.ferramentas, self.app, [(True, "Ordenada", "lista"), (False, "Ordem de criação", None)],
                  self.ordenar, comando=self.mudar_ordenacao,
                  dica="Ordenada: os vizinhos em ordem alfabética (a busca visita primeiro o menor nome). Ordem de "
                       "criação: na ordem em que as arestas foram criadas").pack(side="left")
        self.criar_lembrete("Duplo clique num vértice renomeia")
        colunas = [("vertice", "Vértice", 90, False), ("vizinhos", "Vizinhos", 240, True),
                   ("quantos", "Quantos", 64, False)]
        quadro, self.tabela = self.criar_tabela(pai, colunas, altura=12)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.ligar_selecao(self.tabela, "vertice")
        self.tabela.bind("<Double-1>", self.duplo_clique_na_tabela)
        self.rotulo_resumo = self.criar_resumo(pai, 2)

    # A lista de cada vértice: no orientado, os vizinhos para onde as arestas SAEM dele
    def lista(self):
        sessao = self.sessao
        return representacoes.lista_de_saida(sessao.vertices, sessao.arestas, sessao.direcionado, sessao.ordenar)

    def mostrar_painel(self):
        limpar_tabela(self.tabela)
        lista = self.lista()
        for vertice in self.sessao.vertices:
            partes = []
            for vizinho, peso, numero in lista[vertice]:
                texto = vizinho
                if peso is not None:
                    texto += f" ({entrada.formatar_numero(peso)})"
                partes.append(texto)
            marcas = ("escolhida",) if vertice == self.escolhas.get("vertice") else ()
            self.tabela.insert("", "end", iid=vertice, values=(vertice, " → ".join(partes) or "—", len(partes)),
                               tags=marcas)
        self.selecionar_na_tabela(self.tabela, self.escolhas.get("vertice"))
        if self.sessao.ordenar:
            texto = "Listas em ordem alfabética: é o critério de desempate (a busca visita primeiro o menor nome)."
        else:
            texto = "Listas na ordem de criação das arestas."
        if not self.sessao.direcionado:
            texto += " Não orientado: cada aresta aparece nas duas listas (o laço, uma vez)."
        self.rotulo_resumo.configure(text=texto)

    def selecao(self):
        nome = self.escolhas.get("vertice")
        if nome not in self.sessao.vertices:
            return None
        arestas = []
        vertices = [nome]
        for vizinho, peso, numero in self.lista()[nome]:
            arestas.append(numero)
            vertices.append(vizinho)
        return {"vertices": vertices, "arestas": arestas, "cor": self.cor}

    def clicou_no_desenho(self, item):
        if item and item[0] == "vertice":
            self.escolhas["vertice"] = item[1]
            self.mostrar()

    def duplo_clique_na_tabela(self, evento):
        vertice = self.tabela.identify_row(evento.y)
        if vertice in self.sessao.vertices:
            self.renomear_vertice(vertice)
        return "break"

    def mudar_ordenacao(self):
        novo = self.ordenar.get()
        if novo == self.sessao.ordenar:
            return
        aviso = "Listas ordenadas em ordem alfabética. Ctrl+Z desfaz." if novo else \
            "Listas na ordem de criação das arestas. Ctrl+Z desfaz."
        self.mudar_grafo(aviso, ordenar=novo)


# ----------------------------------------------------------------------
# Matriz de adjacência e matriz de incidência
# ----------------------------------------------------------------------

class ParteDaMatriz(ParteDoGrafo):
    escolhas_iniciais = {"celula": None, "modo": None, "preenchendo": False, "preenchidas": None}

    def montar_painel(self, pai):
        self.modo = tk.StringVar(value=self.modo_inicial())
        opcoes = []
        for valor, texto in self.modos():
            opcoes.append((valor, texto, None))
        Segmentos(self.ferramentas, self.app, opcoes, self.modo, comando=self.mudar_modo).pack(side="left")
        self.botao_preencher = Botao(self.ferramentas, self.app, "Preencher aresta por aresta", icone="play",
                                     papel="info", comando=self.alternar_preenchimento,
                                     dica="Monta a matriz do zero, uma aresta de cada vez (as setas ← → andam)")
        self.botao_preencher.pack(side="right")
        self.grade = GradeDeMatriz(pai, self.app, self.clicou_na_grade)
        self.grade.quadro.grid(row=0, column=0, sticky="nsew")
        self.rotulo_nota = ttk.Label(pai, style="Suave.TLabel", justify="left")
        self.rotulo_nota.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.rotulo_passo = ttk.Label(pai, style="Mensagem.TLabel", justify="left")
        self.rotulo_passo.grid(row=2, column=0, sticky="w")
        self.barra = None
        pai.bind("<Configure>", self.quebrar_linhas, add="+")
        if self.escolhas.get("preenchendo"):
            self.escolhas["preenchendo"] = False
            self.alternar_preenchimento()

    def quebrar_linhas(self, evento):
        self.rotulo_nota.configure(wraplength=max(200, evento.width - 10))
        self.rotulo_passo.configure(wraplength=max(200, evento.width - 10))

    def modo_inicial(self):
        modos = [valor for valor, texto in self.modos()]
        escolhido = self.escolhas.get("modo")
        if escolhido in modos:
            return escolhido
        if self.sessao.tem_pesos() and "pesos" in modos and not entrada.indices_sem_peso(self.sessao.arestas):
            return "pesos"
        return modos[0]

    def mudar_modo(self):
        self.escolhas["modo"] = self.modo.get()
        self.mostrar()

    # Preencher aresta por aresta: a matriz começa vazia e cada passo acrescenta uma aresta
    def alternar_preenchimento(self):
        if self.barra is not None:
            self.barra.destruir()
            self.barra.quadro.destroy()
            self.barra = None
            self.escolhas["preenchendo"] = False
            self.escolhas["preenchidas"] = None
            self.botao_preencher.configurar(texto="Preencher aresta por aresta", icone="play", papel="info")
            self.rotulo_passo.configure(text="")
            self.mostrar()
            return
        self.escolhas["preenchendo"] = True
        self.botao_preencher.configurar(texto="Ver a matriz completa", icone="matriz", papel="neutro")
        self.barra = BarraDoTocador(self.direita, self.app, self.ir_para, unidade="aresta")
        self.barra.quadro.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        total = len(self.sessao.arestas)
        preenchidas = self.escolhas.get("preenchidas")
        if preenchidas is None:
            preenchidas = 0
        self.barra.configurar(0, total, preenchidas)
        self.ir_para(preenchidas)

    def ir_para(self, posicao):
        self.escolhas["preenchidas"] = max(0, min(posicao, len(self.sessao.arestas)))
        self.mostrar()

    def tecla(self, nome):
        if self.barra is None:
            return False
        acoes = {"direita": self.barra.avancar, "esquerda": self.barra.voltar, "espaco": self.barra.play_pausa,
                 "inicio": self.barra.inicio, "fim": self.barra.fim}
        if nome in acoes:
            acoes[nome]()
            return True
        return False

    def destruir(self):
        if self.barra is not None:
            self.barra.destruir()
        ParteDoGrafo.destruir(self)

    # As arestas que entram na matriz agora (todas, ou só as primeiras no preenchimento)
    def arestas_da_matriz(self):
        preenchidas = self.escolhas.get("preenchidas")
        if self.barra is None or preenchidas is None:
            return self.sessao.arestas
        return self.sessao.arestas[:preenchidas]

    def mostrar_painel(self):
        matriz = self.calcular(self.arestas_da_matriz())
        self.matriz = matriz
        destaques = {"linhas": {}, "colunas": {}, "celulas": {}, "contorno": {}}
        celula = self.escolhas.get("celula")
        if celula is not None:
            i, j = celula
            if i is not None:
                destaques["linhas"][i] = self.tinta
            if j is not None:
                destaques["colunas"][j] = self.tinta
            if i is not None and j is not None:
                destaques["celulas"][(i, j)] = self.cor_clara()
                destaques["contorno"][(i, j)] = self.cor
        preenchidas = self.escolhas.get("preenchidas")
        if self.barra is not None and preenchidas:
            ultima = preenchidas - 1
            for (i, j), numeros in matriz["arestas"].items():
                if ultima in numeros:
                    destaques["celulas"][(i, j)] = self.tema["fundo_destaque"]
                    destaques["contorno"][(i, j)] = self.tema["destaque"]
            self.rotulo_passo.configure(text=self.texto_do_passo(ultima))
            self.barra.atualizar(preenchidas, f"{preenchidas} de {len(self.sessao.arestas)} arestas")
        elif self.barra is not None:
            self.rotulo_passo.configure(text="A matriz começa toda vazia (zero). Use ▶ para acrescentar as arestas.")
            self.barra.atualizar(0, f"0 de {len(self.sessao.arestas)} arestas")
        self.grade.mostrar(matriz, destaques)
        self.rotulo_nota.configure(text=self.nota())

    def cor_clara(self):
        from visual.tema import misturar
        return misturar(self.tema["superficie"], self.cor, 0.45)

    def clicou_na_grade(self, linha, coluna):
        self.escolhas["celula"] = (linha, coluna)
        self.mostrar()

    def mostrar(self):
        self.mostrar_painel()
        if self.desenho is None:
            return
        estado = self.sessao.estado_montado()
        selecao = self.selecao()
        preenchidas = self.escolhas.get("preenchidas")
        if self.barra is not None and preenchidas:
            numero = preenchidas - 1
            origem, destino, nome, peso = self.sessao.arestas[numero]
            selecao = {"vertices": [origem, destino], "arestas": [numero], "cor": self.tema["destaque"]}
        self.desenho.desenhar(estado, self.opcoes_do_desenho(neutro=True, selecao=selecao))


class ParteDaMatrizDeAdjacencia(ParteDaMatriz):
    chave = "adjacencia"
    titulo = "Matriz de adjacência"
    descricao = "Uma linha e uma coluna por vértice: M[i][j] diz se (e quanto) i se liga a j."

    def modos(self):
        return representacoes.modos_da_adjacencia(self.sessao.direcionado)

    def calcular(self, arestas):
        return representacoes.matriz_de_adjacencia(self.sessao.vertices, arestas, self.sessao.direcionado,
                                                   self.modo.get())

    def selecao(self):
        celula = self.escolhas.get("celula")
        if celula is None or self.matriz is None:
            return None
        i, j = celula
        vertices = []
        arestas = []
        nomes = self.sessao.vertices
        if i is not None and j is not None:
            vertices = [nomes[i], nomes[j]]
            arestas = list(self.matriz["arestas"].get((i, j), []))
        elif i is not None:
            vertices = [nomes[i]]
            for coluna in range(len(nomes)):
                arestas += self.matriz["arestas"].get((i, coluna), [])
        elif j is not None:
            vertices = [nomes[j]]
            for linha in range(len(nomes)):
                arestas += self.matriz["arestas"].get((linha, j), [])
        return {"vertices": vertices, "arestas": arestas, "cor": self.cor}

    def clicou_no_desenho(self, item):
        if not item:
            return
        nomes = self.sessao.vertices
        if item[0] == "vertice":
            self.escolhas["celula"] = (nomes.index(item[1]), None)
        else:
            origem, destino, nome, peso = self.sessao.arestas[item[1]]
            self.escolhas["celula"] = (nomes.index(origem), nomes.index(destino))
        self.mostrar()
        i, j = self.escolhas["celula"]
        self.grade.mostrar_celula(i, j)

    def texto_do_passo(self, numero):
        origem, destino, nome, peso = self.sessao.arestas[numero]
        modo = self.modo.get()
        if modo == "sinais":
            return (f"Aresta {origem} → {destino}: M[{origem}][{destino}] recebe −1 (sai de {origem}) e "
                    f"M[{destino}][{origem}] recebe +1 (chega em {destino}).")
        if modo == "pesos":
            return f"Aresta {origem} → {destino}: o peso {entrada.formatar_numero(peso) or '?'} vai para M[{origem}][{destino}]."
        if self.sessao.direcionado:
            return f"Aresta {origem} → {destino}: M[{origem}][{destino}] aumenta 1 (linha = de onde sai)."
        if origem == destino:
            return f"Laço em {origem}: M[{origem}][{origem}] aumenta 1 (na diagonal)."
        return (f"Aresta {origem} — {destino}: M[{origem}][{destino}] e M[{destino}][{origem}] aumentam 1 "
                f"(vale nos dois sentidos: a matriz fica simétrica).")

    def nota(self):
        modo = self.modo.get()
        n = len(self.sessao.vertices)
        if modo == "sinais":
            texto = "−1 = a aresta sai deste vértice (linha) para o da coluna; +1 = chega vinda dele (slide 9)."
        elif modo == "pesos":
            texto = "O peso no lugar do 1; vazio = sem aresta (slide 13)."
            for numeros in self.matriz["arestas"].values():
                if len(numeros) > 1:
                    texto += (" Arestas paralelas com peso não cabem numa matriz padrão (slide 14): aqui aparecem "
                              "os pesos separados por |.")
                    break
        elif self.sessao.direcionado:
            texto = "Linha = de onde a aresta sai, coluna = aonde chega (slide 10). Paralelas somam."
        else:
            texto = "Não orientado: simétrica (M[i][j] = M[j][i]). Laço = 1 na diagonal (slide 11); paralelas somam " \
                    "(slide 12)."
        texto += f" Tamanho: {n} × {n} = {n * n} posições, mesmo com poucas arestas."
        return texto


class ParteDaMatrizDeIncidencia(ParteDaMatriz):
    chave = "incidencia"
    titulo = "Matriz de incidência"
    descricao = "Uma linha por vértice e uma coluna por aresta: quem a aresta toca."

    def modos(self):
        return representacoes.MODOS_DA_INCIDENCIA

    def calcular(self, arestas):
        return representacoes.matriz_de_incidencia(self.sessao.vertices, arestas, self.sessao.direcionado,
                                                   self.modo.get())

    def selecao(self):
        celula = self.escolhas.get("celula")
        if celula is None or self.matriz is None:
            return None
        i, j = celula
        if j is not None and j < len(self.sessao.arestas):
            origem, destino, nome, peso = self.sessao.arestas[j]
            return {"vertices": [origem, destino], "arestas": [j], "cor": self.cor}
        if i is not None:
            nome = self.sessao.vertices[i]
            arestas = []
            for numero in range(len(self.sessao.arestas)):
                if nome in self.sessao.arestas[numero][:2]:
                    arestas.append(numero)
            return {"vertices": [nome], "arestas": arestas, "cor": self.cor}
        return None

    def clicou_no_desenho(self, item):
        if not item:
            return
        if item[0] == "vertice":
            self.escolhas["celula"] = (self.sessao.vertices.index(item[1]), None)
        else:
            self.escolhas["celula"] = (None, item[1])
        self.mostrar()
        i, j = self.escolhas["celula"]
        self.grade.mostrar_celula(i, j)

    def texto_do_passo(self, numero):
        origem, destino, nome, peso = self.sessao.arestas[numero]
        coluna = representacoes.nome_da_coluna(self.sessao.arestas, numero)
        if origem == destino:
            if self.sessao.direcionado:
                return f"Coluna {coluna}: laço em {origem}, sai e chega nele mesmo (±1)."
            return f"Coluna {coluna}: laço em {origem}, que toca o vértice duas vezes (2)."
        if self.sessao.direcionado:
            return f"Coluna {coluna}: a aresta sai de {origem} (−1) e chega em {destino} (+1); o resto da coluna é 0."
        return f"Coluna {coluna}: a aresta toca {origem} e {destino} (1 nos dois); o resto da coluna é 0."

    def nota(self):
        n = len(self.sessao.vertices)
        m = len(self.sessao.arestas)
        if self.sessao.direcionado:
            texto = "Orientado: −1 onde a aresta sai e +1 onde chega (slide 17); laço = ±1. Paralelas = colunas iguais."
        else:
            texto = "Não orientado: 1 nas duas pontas (slide 16); laço = 2 (slide 18). Paralelas = colunas iguais."
        if self.modo.get() == "pesos":
            texto += " Com pesos: o peso no lugar do 1 (slide 20)."
        texto += f" Tamanho: {n} × {m} (vértices × arestas). Cada coluna soma 0 no orientado e 2 no não orientado."
        return texto


# ----------------------------------------------------------------------
# Tipo do grafo (a análise que a DFS faz na etapa 6), com a barra de edição
# ----------------------------------------------------------------------

NOMES_DOS_TIPOS = {
    "tipo_orientacao": "Orientação",
    "tipo_simples": "Simples?",
    "tipo_completo": "Completo?",
    "tipo_valorado": "Valorado?",
    "tipo_ciclo": "Cíclico?",
    "tipo_dag": "DAG?",
    "ordem_topologica": "Ordem topológica",
    "tipo_componentes": "Componentes",
    "tipo_resumo": "Resumo",
}


# As conclusões da análise de agora: {tipo do passo: mensagem}, por exemplo {"tipo_simples": "Simples: sim, ..."}
def conclusoes_do_tipo(sessao):
    conclusoes = {}
    for passo in sessao.passos_do_grafo:
        if passo["tipo"] in NOMES_DOS_TIPOS:
            conclusoes[passo["tipo"]] = passo["mensagem"]
    return conclusoes


# O resumo da análise em partes: ["orientado", "simples", "não completo", "não valorado", "acíclico", "DAG"]
def resumo_do_tipo(sessao):
    for passo in sessao.passos_do_grafo:
        if passo["tipo"] == "tipo_resumo":
            return passo["resumo"].split(" · ")
    return []


# O que mudou no tipo, em texto: "não simples (era simples), cíclico (era acíclico)". "" = nada mudou.
# As partes do resumo estão sempre na mesma ordem (orientação, simples, completo, valorado, ciclo e a
# última: DAG no orientado, árvore/floresta/componentes no não orientado).
def mudancas_no_tipo(antes, depois):
    if not depois:
        return ""
    if not antes or len(antes) != len(depois):
        return " · ".join(depois)
    mudou = []
    for indice in range(len(depois)):
        if antes[indice] != depois[indice]:
            mudou.append(f"{depois[indice]} (era {antes[indice]})")
    return ", ".join(mudou)


class ParteDoTipo(ParteDoGrafo):
    chave = "tipo"
    titulo = "Tipo do grafo"
    descricao = "Simples, completo, valorado, cíclico, DAG: mude o grafo pela barra e veja o tipo mudar junto."
    # passo: a linha escolhida na tabela; vertice/aresta: o escolhido no desenho (para remover);
    # nova_origem/novo_destino: a última aresta criada pela barra; antes/depois: as conclusões de antes e
    # de depois da última mudança (as linhas que mudaram ficam em destaque)
    escolhas_iniciais = {"passo": None, "vertice": None, "aresta": None, "nova_origem": None, "novo_destino": None,
                         "antes": None, "depois": None}

    # A barra de edição tem duas linhas (numa só ela não cabe em janelas menores):
    #   [Orientado | Não orientado]  [+ Vértice]  [Remover ...]          ✎ clique escolhe · duplo clique renomeia
    #   Nova aresta: de [A] → [B]  [+ Aresta]
    def montar_painel(self, pai):
        sessao = self.sessao
        primeira = ttk.Frame(self.ferramentas)
        primeira.pack(side="top", fill="x")
        segunda = ttk.Frame(self.ferramentas)
        segunda.pack(side="top", fill="x", pady=(6, 0))

        self.orientacao = tk.BooleanVar(value=sessao.direcionado)
        Segmentos(primeira, self.app, ORIENTACOES, self.orientacao, comando=self.mudar_orientacao,
                  dica=DICA_DA_ORIENTACAO).pack(side="left")
        Botao(primeira, self.app, "Vértice", icone="mais", papel="sucesso", comando=self.acrescentar_vertice,
              dica=self.texto_do_vertice_novo).pack(side="left", padx=(14, 0))
        self.botao_remover = Botao(primeira, self.app, "Remover", icone="lixeira", papel="perigo",
                                   comando=self.remover,
                                   dica="Remove o vértice (com as arestas dele) ou a aresta escolhida no desenho "
                                        "(a tecla Delete também)")
        self.botao_remover.pack(side="left", padx=(6, 0))
        self.criar_lembrete("Clique no desenho escolhe · duplo clique renomeia", pai=primeira)

        # A aresta nova: de [origem] → [destino] + Aresta (a mesma ponta nos dois = laço; um par que já
        # existe = aresta paralela)
        ttk.Label(segunda, text="Nova aresta:  de").pack(side="left", padx=(0, 6))
        self.nova_origem = tk.StringVar(value=self.vertice_ou_padrao(self.escolhas.get("nova_origem"), 0))
        self.novo_destino = tk.StringVar(value=self.vertice_ou_padrao(self.escolhas.get("novo_destino"), 1))
        # A largura das caixas: a do maior nome de vértice (de 4 a 10 letras)
        largura = 4
        for vertice in sessao.vertices:
            largura = max(largura, min(len(vertice), entrada.TAMANHO_MAXIMO_DO_VERTICE))
        for variavel, seta in ((self.nova_origem, "→" if sessao.direcionado else "—"), (self.novo_destino, None)):
            caixa = ttk.Combobox(segunda, textvariable=variavel, values=sessao.vertices, state="readonly",
                                 width=largura + 1, font=self.fontes["texto"])
            caixa.pack(side="left")
            if seta:
                ttk.Label(segunda, text=seta).pack(side="left", padx=6)
        Botao(segunda, self.app, "Aresta", icone="mais", papel="sucesso", comando=self.acrescentar_aresta,
              dica="Cria a aresta escolhida. A mesma ponta nos dois lados faz um laço; um par que já existe faz "
                   "uma aresta paralela").pack(side="left", padx=(8, 0))

        colunas = [("propriedade", "Propriedade", 130, False), ("resposta", "O que a análise diz", 420, True)]
        quadro, self.tabela = self.criar_tabela(pai, colunas, altura=10)
        quadro.grid(row=0, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", self.escolheu_na_tabela)
        self.rotulo_explicacao = ttk.Label(pai, style="Explicacao.TLabel", justify="left")
        self.rotulo_explicacao.grid(row=2, column=0, sticky="w", pady=(6, 0))
        pai.bind("<Configure>", lambda evento: self.rotulo_explicacao.configure(
            wraplength=max(200, evento.width - 10)), add="+")

    # Um vértice que existe: o escolhido, ou o da posição "indice" (o último, se não houver tantos)
    def vertice_ou_padrao(self, escolhido, indice):
        vertices = self.sessao.vertices
        if escolhido in vertices:
            return escolhido
        if not vertices:
            return ""
        return vertices[min(indice, len(vertices) - 1)]

    def texto_do_vertice_novo(self):
        nome = entrada.proximo_nome_livre(self.sessao.vertices)
        return f"Cria o vértice {nome}, ainda sem arestas" if nome else "Não há nome livre para outro vértice"

    def indices(self):
        lista = []
        for indice in range(len(self.sessao.passos_do_grafo)):
            if self.sessao.passos_do_grafo[indice]["tipo"] in NOMES_DOS_TIPOS:
                lista.append(indice)
        return lista

    # As conclusões de antes da última mudança feita aqui, ou None se o grafo mudou de novo depois dela
    # (em outra parte, ou com o Ctrl+Z): aí não há o que destacar
    def conclusoes_de_antes(self):
        antes = self.escolhas.get("antes")
        depois = self.escolhas.get("depois")
        if not isinstance(antes, dict) or depois != conclusoes_do_tipo(self.sessao):
            return None
        return antes

    def mostrar_painel(self):
        limpar_tabela(self.tabela)
        antes = self.conclusoes_de_antes()
        for indice in self.indices():
            passo = self.sessao.passos_do_grafo[indice]
            # As linhas que a última mudança alterou ficam em destaque
            marcas = ()
            if antes is not None and antes.get(passo["tipo"]) != passo["mensagem"]:
                marcas = ("destaque",)
            self.tabela.insert("", "end", iid=str(indice), values=(NOMES_DOS_TIPOS[passo["tipo"]], passo["mensagem"]),
                               tags=marcas)
        escolhido = self.escolhas.get("passo")
        self.selecionar_na_tabela(self.tabela, escolhido)
        if self.passo_escolhido() is not None:
            passo = self.sessao.passos_do_grafo[self.passo_escolhido()]
            self.rotulo_explicacao.configure(text=explicacoes.explicar(algoritmos.PROFUNDIDADE, passo))
        elif not self.sessao.vertices:
            self.rotulo_explicacao.configure(text="O grafo está vazio: use + Vértice para começar.")
        else:
            texto = ("Escolha uma linha para ver no desenho o que ela aponta (o ciclo, os laços e as paralelas, a "
                     "ordem topológica, as componentes...).")
            if antes is not None:
                texto = "Em destaque: o que mudou com a última mudança no grafo. " + texto
            self.rotulo_explicacao.configure(text=texto)
        self.atualizar_remover()

    def passo_escolhido(self):
        escolhido = self.escolhas.get("passo")
        if isinstance(escolhido, str) and escolhido.isdigit() and int(escolhido) < len(self.sessao.passos_do_grafo):
            return int(escolhido)
        return None

    def aresta_escolhida(self):
        escolhida = self.escolhas.get("aresta")
        if isinstance(escolhida, str) and escolhida.isdigit() and int(escolhida) < len(self.sessao.arestas):
            return int(escolhida)
        return None

    # O botão Remover diz o que vai remover ("Remover B", "Remover A → B") e fica apagado sem escolha
    def atualizar_remover(self):
        vertice = self.escolhas.get("vertice")
        numero = self.aresta_escolhida()
        if vertice in self.sessao.vertices:
            self.botao_remover.configurar(texto=f"Remover {vertice}", habilitado=True)
        elif numero is not None:
            origem, destino, nome, peso = self.sessao.arestas[numero]
            self.botao_remover.configurar(texto=f"Remover {self.ligacao(origem, destino)}", habilitado=True)
        else:
            self.botao_remover.configurar(texto="Remover", habilitado=False)

    def selecao(self):
        vertice = self.escolhas.get("vertice")
        if vertice in self.sessao.vertices:
            # O vértice e as arestas dele (o Remover leva tudo junto)
            arestas = []
            for numero in range(len(self.sessao.arestas)):
                if vertice in self.sessao.arestas[numero][:2]:
                    arestas.append(numero)
            return {"vertices": [vertice], "arestas": arestas, "cor": self.cor}
        numero = self.aresta_escolhida()
        if numero is not None:
            origem, destino, nome, peso = self.sessao.arestas[numero]
            return {"vertices": [origem, destino], "arestas": [numero], "cor": self.cor}
        return None

    def mostrar(self):
        self.mostrar_painel()
        if self.desenho is None:
            return
        indice = self.passo_escolhido()
        if indice is not None:
            estado = self.sessao.estado_do_grafo(indice)
            selecao = {"vertices": list(estado.vertices_marcados), "arestas": list(estado.arestas_marcadas),
                       "cor": self.cor}
            self.desenho.desenhar(estado, self.opcoes_do_desenho(neutro=True, selecao=selecao))
        else:
            self.desenho.desenhar(self.sessao.estado_montado(), self.opcoes_do_desenho(neutro=True,
                                                                                      selecao=self.selecao()))

    # Escolher uma linha da tabela tira a escolha do desenho (e o contrário): uma coisa de cada vez
    def escolheu_na_tabela(self, evento=None):
        selecionados = self.tabela.selection()
        novo = selecionados[0] if selecionados else None
        if novo != self.escolhas.get("passo"):
            self.escolhas["passo"] = novo
            if novo is not None:
                self.escolhas["vertice"] = None
                self.escolhas["aresta"] = None
            self.mostrar()

    def clicou_no_desenho(self, item):
        self.escolhas["passo"] = None
        self.escolhas["vertice"] = None
        self.escolhas["aresta"] = None
        if item is not None and item[0] == "vertice":
            self.escolhas["vertice"] = item[1]
        elif item is not None:
            self.escolhas["aresta"] = str(item[1])
        self.mostrar()

    def tecla(self, nome):
        if nome == "apagar":
            self.remover()
            return True
        return False

    # ------------------------------------------------------------------
    # As mudanças pela barra (cada uma diz também o que mudou no tipo)
    # ------------------------------------------------------------------

    def mudar_grafo(self, aviso, **mudancas):
        sessao = self.sessao
        tela = self.tela
        antes = resumo_do_tipo(sessao)
        self.escolhas["antes"] = conclusoes_do_tipo(sessao)
        self.escolhas["depois"] = None
        tela.mudar_grafo(aviso, **mudancas)
        # Aqui a parte já foi montada de novo (tela.parte é a parte nova), com o grafo novo
        if isinstance(tela.parte, ParteDoTipo):
            tela.parte.escolhas["depois"] = conclusoes_do_tipo(sessao)
        mudou = mudancas_no_tipo(antes, resumo_do_tipo(sessao))
        if mudou and tela.aviso_atual == aviso:
            tela.avisar(f"{aviso} Tipo agora: {mudou}.")

    def mudar_orientacao(self):
        novo = self.orientacao.get()
        if novo == self.sessao.direcionado:
            return
        if novo:
            aviso = "Agora o grafo é orientado: cada aresta tem sentido (A → B). Ctrl+Z desfaz."
        else:
            aviso = "Agora o grafo é não orientado: cada aresta vale nos dois sentidos (A — B). Ctrl+Z desfaz."
        self.mudar_grafo(aviso, direcionado=novo)

    def acrescentar_vertice(self):
        vertices = self.sessao.vertices
        if len(vertices) >= entrada.MAXIMO_DE_VERTICES:
            self.tela.avisar(f"O grafo já tem {entrada.MAXIMO_DE_VERTICES} vértices, o máximo que cabe no desenho.",
                             erro=True)
            return
        nome = entrada.proximo_nome_livre(vertices)
        if nome == "":
            self.tela.avisar("Não há um nome livre para o vértice novo: renomeie algum (duplo clique).", erro=True)
            return
        self.escolhas.update({"vertice": nome, "aresta": None, "passo": None})
        self.mudar_grafo(f"Vértice {nome} criado, ainda sem arestas. Ctrl+Z desfaz.", vertices=vertices + [nome])

    def acrescentar_aresta(self):
        sessao = self.sessao
        origem = self.nova_origem.get()
        destino = self.novo_destino.get()
        if origem not in sessao.vertices or destino not in sessao.vertices:
            self.tela.avisar("Escolha de onde a aresta sai e aonde ela chega (crie os vértices antes).", erro=True)
            return
        if len(sessao.arestas) >= entrada.LIMITE_DE_ARESTAS:
            self.tela.avisar(f"O limite é de {entrada.LIMITE_DE_ARESTAS} arestas.", erro=True)
            return
        detalhes = []
        if origem == destino:
            detalhes.append("é um laço")
        for outra_origem, outro_destino, nome, peso in sessao.arestas:
            if entrada.chave_do_par(outra_origem, outro_destino, sessao.direcionado) == \
                    entrada.chave_do_par(origem, destino, sessao.direcionado):
                detalhes.append("é paralela a outra")
                break
        aviso = f"Aresta {self.ligacao(origem, destino)} criada"
        if detalhes:
            aviso += " (" + " e ".join(detalhes) + ")"
        aviso += ". Ctrl+Z desfaz."
        if sessao.tem_pesos():
            aviso += " Ela está sem peso: duplo clique na aresta para dar um."
        self.escolhas.update({"aresta": str(len(sessao.arestas)), "vertice": None, "passo": None,
                              "nova_origem": origem, "novo_destino": destino})
        self.mudar_grafo(aviso, arestas=sessao.arestas + [(origem, destino, "", None)])

    def remover(self):
        sessao = self.sessao
        vertice = self.escolhas.get("vertice")
        numero = self.aresta_escolhida()
        if vertice in sessao.vertices:
            vertices, arestas = entrada.remover_vertice(sessao.vertices, sessao.arestas, vertice)
            mudancas = {"vertices": vertices, "arestas": arestas}
            if sessao.inicio == vertice:
                mudancas["inicio"] = None
            if sessao.destino == vertice:
                mudancas["destino"] = None
            saem = len(sessao.arestas) - len(arestas)
            aviso = f"Vértice {vertice} removido"
            if saem:
                aviso += " com " + entrada.contar(saem, "aresta", "arestas")
            self.escolhas.update({"vertice": None, "aresta": None, "passo": None})
            self.mudar_grafo(aviso + ". Ctrl+Z desfaz.", **mudancas)
        elif numero is not None:
            origem, destino, nome, peso = sessao.arestas[numero]
            arestas = list(sessao.arestas)
            del arestas[numero]
            self.escolhas.update({"vertice": None, "aresta": None, "passo": None})
            self.mudar_grafo(f"Aresta {self.ligacao(origem, destino)} removida. Ctrl+Z desfaz.", arestas=arestas)
        else:
            self.tela.avisar("Clique num vértice ou numa aresta do desenho para escolher o que remover.", erro=True)


PARTES_DO_GRAFO = [ParteDosVertices, ParteDasArestas, ParteDosPesos, ParteDaLista, ParteDaMatrizDeAdjacencia,
                   ParteDaMatrizDeIncidencia, ParteDoTipo]
