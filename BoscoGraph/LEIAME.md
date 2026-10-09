# BoscoGraph — buscas em grafos por partes, passo a passo e linha a linha (versão 7.3)

Mostra como um grafo é montado (vértices, arestas, lista de adjacência, matrizes) e como a **busca
escolhida** anda por ele, com o código correspondente destacado. São **doze algoritmos**: dez buscas
(profundidade (DFS), profundidade limitada, aprofundamento iterativo, largura (BFS), bidirecional,
Dijkstra, Bellman-Ford, Floyd-Warshall, gulosa e A\*) e os dois da **árvore geradora mínima** (Prim e
Kruskal).

A visualização é **por partes**: em vez de mostrar tudo ao mesmo tempo, ela mostra uma coisa de cada vez
(os vértices, as arestas, os pesos, a lista, a matriz de adjacência, a matriz de incidência, o tipo do
grafo, o passo a passo, o linha a linha, a comparação de códigos, o resultado), e você escolhe qual na
trilha da esquerda. Cada parte tem a sua cor, e o que você escolhe nela fica destacado nessa cor.

Dois jeitos de acompanhar a busca:

- **passo a passo**: um passo da busca por clique;
- **linha a linha**: o programa da busca **roda de verdade**, desde a **primeira linha** do arquivo
  (o cabeçalho, os comentários, a classe, o grafo, a chamada da busca e os `print` do fim), uma linha
  por clique, como num depurador, com as variáveis do programa, o que ele escreveu (a **Saída**) e uma
  explicação de cada linha já com os números. O programa aparece em **Pseudocódigo, Python, Java, C,
  C++ e JavaScript**, e dá para **comparar duas linguagens lado a lado** com a mesma linha destacada.
  Clicando numa linha, você escolhe **de onde partir**.

Tudo pode ser **exportado**: o desenho como imagem (PNG ou SVG), um **relatório completo em PDF**, um
arquivo **.bosco** (que abre o BoscoGraph exatamente como estava) e o **código-fonte** da busca, com o
grafo dentro, na linguagem que você escolher.

O grafo é montado no **editor**, em três etapas, uma tela de cada vez (**vértices**, **arestas** e
**busca**: orientado ou não orientado, com pesos e heurística, sorteios e modelos salvos), ou
**importado** de outros programas (draw.io, yEd, Gephi, Graphviz, planilha, PDF e até foto).
O grafo da Prova 01 vem salvo como o modelo padrão.

Em todas as telas: o **tamanho das letras** muda com **Ctrl + roda do mouse** (como no navegador; também
Ctrl + e Ctrl −, e Ctrl 0 volta a 100%) e o **tema** muda na chave do canto de cima, com o **sol**
(claro) e a **lua** (escuro). As cores de base são as da paleta da universidade. Os botões têm cores e
ícones diferentes conforme o que fazem: azul-marinho (salmão, no tema escuro) para a ação principal,
verde para criar, vermelho para remover, verde-azulado para editar e importar, roxo para os arquivos
.bosco.

## O que mudou na versão 7.3

- **Árvore geradora mínima: Prim e Kruskal**, um tipo novo na tela inicial (o quarto), com o exemplo do
  livro do Cormen (figura 23.1, peso mínimo 37). Veja [As buscas](#as-buscas).
  - **Prim**: a árvore cresce a partir da **raiz**, sempre pela aresta mais leve que sai dela. A fila de
    prioridade é pela **chave** (o peso da ligação mais leve conhecida); a melhor ligação de cada vértice
    da fila aparece **tracejada** no desenho até ele entrar na árvore.
  - **Kruskal**: as arestas da mais leve para a mais pesada; aceita a que liga dois conjuntos diferentes
    e recusa a que fecharia um ciclo. Os **conjuntos disjuntos** aparecem com uma cor cada um (no desenho,
    na tabela e na estrutura, que mostra a lista ordenada com ✓ e ✗).
  - O **resultado** mostra as arestas da árvore e o peso total com a conta (1 + 2 + 2 + …), e compara
    com o outro algoritmo, rodando escondido: o peso é sempre o mesmo (com os pesos todos diferentes, as
    arestas também). Grafo desligado: uma **floresta**, uma árvore por parte.
  - Os dois são para grafos **não orientados**: no orientado, o "Antes de visualizar" do editor e a
    visualização mostram o botão **Tornar não orientado**. No Prim, a origem se chama **raiz**; o
    Kruskal não parte de um vértice (o "de" some e o editor explica por quê).
  - O código de estudo nas **seis linguagens**, o **linha a linha** e a exportação do **código-fonte**
    também têm os dois.
- **Passo a passo monta o grafo de novo, vértice por vértice**: ele começa com o grafo **vazio** e cada
  clique mostra um passo da montagem (etapas **1. Vértices**, **2. Arestas**, **3. Listas** e
  **4. Ordenação**) antes da busca (etapa 5) e do resultado (etapa 6), como antes da versão 5. Os botões
  das seis etapas ficam em cima; **Page Down / Page Up** vão para a próxima etapa / a anterior; para ir
  direto à busca, a etapa 5.
- **Correções**: a escolha da busca do editor ganhou a quarta coluna (com o nome curto quando o nome
  inteiro não cabe); um número digitado na **Quantidade** ou no **Limite** sem o Enter agora vale ao
  clicar em Próximo ou Visualizar; aumentar a Quantidade num desenho importado avisa que os vértices
  novos não têm posição (o desenho volta a ser em círculo); e a **chave do tema** só recria a tela
  depois de terminar a animação dela (antes, às vezes, o Tkinter apagava um comando de um componente
  novo e a tela seguinte quebrava).
- **As cores da universidade**: as cores de base (fundo, textos, bordas, o botão principal, a seleção, o
  destaque e o logo) vêm da paleta da logo da universidade: azul-marinho `#03296a` e `#053e75`,
  azul-acinzentado `#6880a1`, cinza-azulado `#d7dce4` e os vermelhos `#fd2016`, `#fd4943`, `#fe7874` e
  `#febbb9` (no tema escuro, o botão principal fica salmão, porque o azul-marinho sumiria no fundo). As
  cores que ajudam a entender a tela continuam as mesmas: Branco, Cinza e Preto nos vértices, as cores das
  arestas e de cada parte, os lados da bidirecional, os conjuntos do Kruskal, o amarelo da linha em
  destaque, o verde de "certo" e o vermelho de "erro". O detalhe está no começo de `visual/tema.py`.
- **Instalador mais simples**: três telas, e quem instala só clica em **Avançar**, **Eu aceito o
  acordo** + **Avançar** e **Concluir**: as boas-vindas (o agradecimento, por que o BoscoGraph foi feito,
  quem criou, os co-criadores e os entusiastas, os professores), os termos de uso e o fim, já com "Abrir o
  BoscoGraph agora". Instala só para quem está usando o computador, sem pedir senha de administrador.
  Veja [Executável e instalador](#executável-e-instalador-windows).
- **Sobre**: o nome completo do professor Bruno Bustamante Ferreira Leonor.

## O que mudou na versão 7.2

- **Editor em etapas**: ① Vértices, ② Arestas e ③ Busca, **uma tela de cada vez**, com a trilha em cima
  (clicar numa etapa leva até ela) e **Voltar / Próximo** embaixo; a tela desliza na troca de etapa.
  A **lista de adjacência saiu do editor** (ela continua na visualização). Veja
  [Editor do grafo](#editor-do-grafo).
- **Campos e botões novos**, desenhados como o resto do programa: a caixa de texto com cantos
  arredondados (fica azul com o cursor e vermelha quando o texto tem problema), o contador **[ − 8 + ]**,
  a **chave liga/desliga** (laços, paralelas, ordenar as listas), a caixa de escolha dos vértices e a
  escolha da busca em **três colunas**, uma por tipo, como na tela inicial.
- **Vértices**: a **Quantidade já cria (ou tira) os vértices** na hora, com os nomes **A, B, C…** ou
  **1, 2, 3…** (trocar o estilo renomeia os vértices da sequência); saíram o **Prefixo** e o **Gerar**.
  **Adicionar** (verde), **Renomear** (verde-azulado) e **Remover** (vermelho) com cores diferentes.
- **Arestas**: **De → Para** (no não orientado, **De — Para**), nome e peso opcionais; **Editar** abre
  a aresta inteira (de onde sai, para onde vai, o nome, o peso e a **posição**, que é a ordem nas listas);
  sortear com as chaves **Laços** e **Paralelas**; saiu o **Sortear listas**.
- **Busca**: as opções aparecem conforme a busca (o destino só nas que usam; o limite só na limitada) e
  o quadro **Antes de visualizar** lista o que falta, com um botão que resolve ("Dar pesos…", "Dar h…",
  "Ir para Vértices").
- **Modelo**: o nome do modelo virou um botão com a lista dos modelos (o aberto com ✓, o padrão com ★,
  "Salvar com outro nome…" e "Grafo novo, vazio"); o **Desfazer** saiu (o **Ctrl+Z** continua) e no
  lugar dele fica o aviso **Alterações não salvas**; o **Salvar** pede o nome na primeira vez; saiu o
  **Pasta…** (a dica do Salvar mostra onde os modelos ficam).
- **Janelas** (renomear, editar a aresta, pesos, editar como texto, salvar): os mesmos campos e botões
  novos (OK e Cancelar desenhados).
- **Tela inicial**: **Ver um exemplo pronto** e **Montar meu grafo** viraram **cartões grandes na cor do
  tipo de busca**, cada um dizendo o que vai abrir. O **Início** de todas as telas ganhou o fundo azul
  clarinho.

## O que mudou na versão 7.1

- **Linha a linha e Comparar códigos como um depurador de verdade**: o programa inteiro roda desde a
  linha 1 (veja [Linha a linha](#linha-a-linha)); comentários e linhas em branco do caminho também são
  passos; ao entrar numa função, o passo para na linha do `def`; o painel **Saída** mostra o que o
  `print` já escreveu.
- **Duplo clique para editar**, na tabela ou no desenho: no vértice renomeia, na aresta renomeia, em
  cima do peso muda o peso (e, na tabela h, muda o h). Saíram os botões Renomear e **Numerar e1, e2…**.
- **Tipo do grafo com edição**: uma barra para criar vértices e arestas (laço e paralela também),
  remover o que foi escolhido no desenho e trocar a orientação; o tipo é refeito na hora e a mensagem
  diz o que mudou ("Tipo agora: cíclico (era acíclico)"), com as linhas que mudaram em destaque.
- **Telas mais limpas**: Vértices sem Saem/Chegam/grau médio (o editor também), Lista de adjacência
  sem Quem sai/Quem chega (o relatório também), sem o "Como é montado"; o "até" só aparece nas buscas
  que usam destino; saiu a dica "Ctrl+PgDn / PgUp troca de parte" (o atalho continua, na lista de
  atalhos do Exibir).
- **Botões novos no topo** da visualização: Início, Editar grafo, Exportar e Exibir (os dois abrem um
  menu) e a chave do tema; os botões das partes do grafo também (segmentos e botões com ícone).
- **Sobre**: "Co-criadores" no lugar de "Colegas".

## Como rodar

Precisa só do Python (3.10 ou mais novo) com o Tkinter, que já vem na instalação do Windows.

```
python boscograph.py                 abre a tela inicial (a escolha da busca)
python boscograph.py grafo.bosco     abre direto um arquivo .bosco, do jeito que foi salvo
python testes.py                     confere tudo (as telas, com a janela escondida)
python boscograph.py --verificar     autoteste: arquivos, código de estudo, buscas e exportações
```

Bibliotecas extras (o resto funciona sem elas):

```
pip install -r requirements.txt      PyMuPDF (importar PDF), OpenCV e NumPy (importar imagem),
                                     pytesseract (texto na imagem) e Pillow (exportar PNG)
```

Sem a Pillow, o PNG avisa e sugere o SVG ou o PDF (que não precisam de nada). Para ler os **nomes**
numa imagem, também é preciso o programa **Tesseract** (veja
[Imagem ou foto](#imagem-ou-foto-fase-3)). Quem instala pelo instalador do BoscoGraph pode marcar o
componente que já traz o Tesseract.

## Tela inicial

À esquerda ficam só os **tipos de busca**, numa sanfona: **sem pesos** (profundidade, limitada,
aprofundamento iterativo, largura e bidirecional), **menor custo** (Dijkstra, Bellman-Ford e
Floyd-Warshall), **com heurística** (gulosa e A\*) e **árvore geradora mínima** (Prim e Kruskal). Clicar
num tipo **abre a lista dos algoritmos dele** (e fecha o tipo que estava aberto); clicar de novo fecha. À
direita, um cartão que acompanha a escolha:

- nada escolhido: as **boas-vindas**, com um desenho da DFS no meio do caminho e "como começar";
- um tipo aberto: o que as buscas desse tipo têm em comum e um atalho para cada algoritmo;
- um algoritmo: o que ele faz, a estrutura que usa, um desenho pequeno dele no meio do caminho e dois
  botões:
  - **Ver um exemplo pronto** (o cartão cheio, na cor do tipo; ou duplo clique no algoritmo, ou Enter):
    abre a visualização direto, num grafo que combina com a busca (o da prova na DFS e na BFS; os do
    livro no Dijkstra, no Bellman-Ford, no Floyd-Warshall, no Prim e no Kruskal; o mapa da Romênia, de
    Arad a Bucharest, na limitada, na iterativa, na bidirecional, na gulosa e no A\*). O cartão diz qual
    é o exemplo;
  - **Montar meu grafo** (o cartão só com a borda): abre o editor na etapa dos vértices, com a busca já
    escolhida.

As setas **↑ / ↓** andam pelos algoritmos do tipo aberto. Embaixo, **outros jeitos de começar**, cada um
com a sua cor e o seu ícone:

| Cartão | O que faz |
|---|---|
| **Começar do zero** (verde) | o editor com um grafo vazio e a busca escolhida; o grafo que estava no editor fica no **Ctrl+Z** |
| **Importar desenho** (verde-azulado, Ctrl+O) | a tela de importação, em etapas (veja [Importar um grafo](#importar-um-grafo)) |
| **Abrir arquivo .bosco** (roxo) | a tela do .bosco: os abertos recentemente e a prévia antes de abrir |
| **Continuar no editor** (cinza) | o editor como você deixou (na primeira vez, **Abrir o editor**, com o modelo padrão) |

No alto, à direita: **Sobre** (o que é o BoscoGraph, a versão, a data de criação, 29/09/2026, quem fez e
os professores) e a chave do tema. O botão **Início** das outras telas volta para cá sem perder nada: a
tela inicial lembra o tipo aberto e o algoritmo escolhido.

Ver um exemplo, importar ou abrir um .bosco **não apaga o que estava no editor**: o grafo novo entra no
editor com o grafo de antes no Ctrl+Z (que volta para ele).

## As buscas

| Busca | Estrutura | Pesos | Destino | Heurística h | O que mostra no fim |
|---|---|---|---|---|---|
| **Profundidade (DFS)** | pilha | ignora | — | — | tempos d/f, tipo de cada aresta, ciclos, DAG e ordem topológica |
| **Profundidade limitada** | pilha (o caminho) | ignora | opcional | — | achou, **corte** (o limite cortou algum caminho) ou falha; os vértices cortados |
| **Aprofundamento iterativo** | pilha, uma rodada por limite | ignora | obrigatório | — | a rodada em que achou (limite 0, 1, 2…), o caminho com menos arestas e quantos nós cada rodada visitou |
| **Largura (BFS)** | fila | ignora | opcional | — | camadas, árvore de busca e menor número de arestas até cada vértice |
| **Bidirecional** | duas filas (da origem e do destino) | ignora | obrigatório | — | o encontro dos dois lados, o caminho e quantos vértices cada lado expandiu |
| **Dijkstra** (custo uniforme) | fila de prioridade | obrigatórios, ≥ 0 | opcional | — | distâncias, árvore de caminhos mínimos e o caminho até o destino |
| **Bellman-Ford** | rodadas (\|V\| − 1) | obrigatórios, aceita negativos | opcional | — | distâncias ou o **ciclo negativo** encontrado |
| **Floyd-Warshall** (todos os pares) | matriz | obrigatórios, aceita negativos | opcional | — | as matrizes d e π de todos os pares; com origem e destino, o caminho entre os dois |
| **Gulosa** (melhor primeiro) | fila de prioridade por h | opcionais | obrigatório | obrigatória | o caminho achado e a comparação com o de menor custo |
| **A\*** (A estrela) | fila de prioridade por f = g + h | obrigatórios, ≥ 0 | obrigatório | obrigatória | o caminho, se h é admissível/consistente e a comparação com o ótimo |
| **Prim** (árvore mínima) | fila de prioridade pela chave | obrigatórios, aceita negativos | — | — | a árvore (ou a floresta) geradora mínima, o peso total e a comparação com o Kruskal |
| **Kruskal** (árvore mínima) | arestas em ordem de peso e conjuntos disjuntos | obrigatórios, aceita negativos | — | — | a árvore (ou a floresta) geradora mínima, o peso total e a comparação com o Prim |

- **Profundidade limitada**: a DFS que não desce além do **limite** (escolhido na barra da busca ou no
  editor). Como no livro do Russell e Norvig, um vértice que já está no caminho atual não é visitado de
  novo (evita ciclo), mas pode ser visitado por outro caminho. O resultado tem três respostas: **achou**,
  **corte** (não achou, mas o limite cortou algum caminho: com um limite maior, talvez ache) ou
  **falha** (não há caminho).
- **Aprofundamento iterativo**: repete a limitada com limite 0, 1, 2… até achar. Acha o caminho com
  **menos arestas**, como a BFS, gastando só a memória da DFS.
- **Bidirecional**: uma BFS da origem (**frente**, em azul) e outra do destino andando pelas arestas
  **ao contrário** (**trás**, em laranja), uma camada de cada vez, até um lado achar um vértice que o
  outro já descobriu. Em geral expande bem menos vértices que a BFS sozinha (os testes contam).
- **Floyd-Warshall**: na rodada de cada vértice k, cada par (i, j) pergunta se passar por k fica mais
  barato. Os pares em que d[i][k] ou d[k][j] é ∞ são pulados. Um d[i][i] negativo no fim é um **ciclo
  negativo**. Até 12 vértices (a matriz precisa caber na tela).
- **Prim e Kruskal** (árvore geradora mínima): não procuram um caminho; escolhem as n − 1 arestas que
  ligam todos os vértices sem formar ciclo, com a menor soma de pesos. Só no grafo **não orientado**.
  O **Prim** tem a forma do Dijkstra, com outra prioridade (o peso da aresta, e não a distância desde a
  origem), e pula o vizinho que já está na árvore (a aresta fecharia um ciclo). O **Kruskal** guarda o
  representante do conjunto de cada vértice (`conjunto[v]`: o MAKE-SET, o FIND-SET e o UNION do livro);
  aqui a união percorre todos os vértices, O(V) por união, enquanto o livro usa a floresta de conjuntos,
  quase O(1). Peso negativo pode: a árvore não soma caminhos, então não existe o problema do Dijkstra.
  Grafo desligado: uma árvore por parte (no Prim, um vértice que sobra fora vira a raiz de uma árvore
  nova, como no laço de fora do DFS). Empates: no Prim, sai da fila quem entrou primeiro; no Kruskal,
  as arestas de mesmo peso ficam na ordem em que foram criadas. Por isso, no exemplo do livro, o Prim
  tira o h antes do c (os dois com chave 8); o livro tira o c e avisa que tanto faz: o peso é 37 nos dois.
- A barra da esquerda (e o editor) conferem os requisitos **enquanto você edita**: falta de peso, peso
  negativo no Dijkstra, destino ou heurística faltando, limite, grafo orientado no Prim e no Kruskal. O
  aviso diz o que falta e leva à parte que resolve (por exemplo, **Ir para Pesos** ou **Tornar não
  orientado**).
- Empates na fila de prioridade: sai quem entrou primeiro (como numa fila comum). Assim, o passo a passo
  é sempre o mesmo para o mesmo grafo.
- Os modelos de exemplo trazem um grafo para cada caso: **Dijkstra (CLRS 24.6)**, **Bellman-Ford
  (CLRS 24.4)**, com peso negativo, **Floyd-Warshall (CLRS 25.1)**, **A estrela (Romênia)**, com a
  heurística da distância em linha reta, e **Árvore geradora mínima (CLRS 23.1)**.

## Pesos e heurística

- **Peso** fica na aresta; **heurística h** fica no vértice (a estimativa do custo até o destino).
- Os pesos são números decimais **exatos** (o tipo `Decimal` do Python): `0,1 + 0,2` dá `0,3`, e não
  `0,30000000000000004` como com `float`. Até 3 casas decimais, entre −1.000.000 e 1.000.000. Vírgula
  ou ponto, tanto faz.
- Na visualização, a parte **Pesos** põe, tira e sorteia pesos (de 1 a 9, ou na faixa que você quiser
  no **Pesos…**), edita um peso com duplo clique e mostra as **estatísticas**: quantas arestas têm peso,
  menor, maior, soma, média, mediana e desvio padrão. O botão **Heurística h…** faz o mesmo nos vértices.
- O botão **Pesos…** (no editor e na parte Pesos) abre a janela "Pesos e heurística":
  - **Aplicar em**: arestas (peso) ou vértices (heurística h);
  - **Quais**: todas, as selecionadas na tabela ou só as que ainda estão sem valor;
  - **Valor**: o mesmo valor para todas, inteiros sorteados numa faixa, tirar o valor e, para a
    heurística, o **custo real até o destino** (h perfeita) ou uma **admissível sorteada** (entre 0 e o
    custo real), calculadas pelo próprio programa;
  - uma prévia diz o que vai acontecer antes de aplicar. Ctrl+Z desfaz.
- No **Editar como texto…** do editor, o peso vem depois de `=`:

```
A -> B: e1 = 2,5
A -> C = 4
B D
```

## Editor do grafo

O grafo é montado em **três etapas, uma tela de cada vez**. Em cima fica a trilha
**① Vértices ── ② Arestas ── ③ Busca** (com quantos vértices e arestas já existem, e o ✓ verde nas
etapas prontas): clicar numa etapa leva até ela. Embaixo, **Voltar** e **Próximo** (Alt+← e Alt+→); na
última etapa, o Próximo vira o **Visualizar** (F5). No meio do rodapé, o resumo do grafo e o **tipo**
(`orientado · não simples · cíclico · não é DAG`), calculados a cada mudança; na etapa Busca, se algo
impede a busca, aparece ali o que falta, em vermelho.

| Parte | O que dá para fazer |
|---|---|
| **Topo** | **Início** (a tela inicial), **Importar desenho** (Ctrl+O; leva à tela de importação) e a chave do tema (sol e lua) |
| **Modelo** | o botão com o nome do modelo abre a lista dos modelos salvos (o aberto com ✓, o padrão com ★), **Salvar com outro nome…** e **Grafo novo, vazio**; o aviso **Alterações não salvas** (ou **Sem alterações**); **Salvar** (Ctrl+S; pede o nome na primeira vez) e **Tornar padrão** (o modelo que abre primeiro) |
| **① Vértices** | **Um de cada vez**: o nome (o próximo já vem sugerido) e **Adicionar** (ou Enter). **Vários de uma vez**: a **Quantidade [ − n + ]** já cria ou tira os vértices (os do fim da lista), os nomes **A, B, C…** ou **1, 2, 3…** e **Sortear quantidade** (de 4 a 12). A tabela: **Renomear** (ou duplo clique; na coluna h, muda a heurística) e **Remover** (ou Delete) |
| **② Arestas** | **Orientado / Não orientado**. **Uma de cada vez**: **De → Para**, nome e peso (os dois opcionais) e **Adicionar aresta** (De = Para cria um laço; o mesmo par de novo, uma paralela). **Várias de uma vez**: a quantidade, as chaves **Laços** e **Paralelas** e **Sortear arestas** (no lugar das de agora). **Editar como texto…** e **Pesos…**. A tabela: **Editar** (ou duplo clique: de onde sai, para onde vai, o nome, o peso e a posição) e **Remover** (ou Delete) |
| **③ Busca** | a busca, em quatro colunas (sem pesos, menor custo, com heurística, árvore geradora mínima; ↑ ↓ ← → também escolhem), o que ela usa e a ideia dela; **Começar por** (no Prim, **Raiz**; o Kruskal não tem opções, e uma frase diz por quê), o **Destino** (só nas buscas que usam; "nenhum" quando é opcional), o **Limite** (só na profundidade limitada) e a chave **Ordenar as listas**; e o quadro **Antes de visualizar**: o que falta, com um botão que resolve quando dá ("Dar pesos…", "Dar h…", "Ir para Vértices", "Tornar não orientado"), ou "Tudo pronto" |

- **Ctrl+Z** volta qualquer mudança, inclusive a quantidade, os nomes 1, 2, 3, um sorteio, os pesos, um
  modelo carregado, uma importação, um exemplo ou o "Começar do zero" (o grafo que estava no editor
  antes deles). O botão Desfazer saiu: no lugar dele, o aviso de alterações não salvas.
- A **Quantidade** aproveita os vértices que já existem. Com os nomes na sequência (A, B, C… ou
  1, 2, 3…), a sequência é refeita com a quantidade nova; com nomes próprios (Arad, Sibiu…), os novos
  entram no fim, com o próximo nome livre do estilo. Trocar **A, B, C… / 1, 2, 3…** renomeia os vértices
  da sequência (as arestas acompanham); com nomes próprios, o estilo vale para os próximos.
- A ordem das arestas (o **Nº** da tabela) é a ordem em que os vizinhos entram nas listas de adjacência;
  o **Editar** muda a posição.
- Passar o mouse por cima de um botão ou campo mostra uma dica do que ele faz.
- Nome de vértice: até 10 caracteres, só letras, números e `_` (por exemplo `SP`, `R1`, `São_Paulo`).
- Nome de aresta: opcional, até 16 caracteres, sem `,` `;` `:` `=`.
- Limites: 26 vértices e 60 arestas (acima disso o desenho fica ilegível).
- A ordenação é alfabética, ou seja, compara **texto**: `"10"` vem antes de `"2"`. Por isso, com 10 ou
  mais vértices, os números ganham zero à esquerda (`01, 02, … 12`): de 9 para 10 vértices, `1..9`
  viram `01..09`, com as arestas junto.
- O modelo **Prova 01** é protegido: para mudar o grafo da prova, salve com outro nome.
- A tela funciona a partir de 960 × 600 pixels (a coluna dos controles rola quando não cabe).

### Orientado ou não orientado

| | Orientado (dígrafo) | Não orientado |
|---|---|---|
| Aresta | par ordenado: `A -> B` é diferente de `B -> A` | par não ordenado: `A — B` é o mesmo que `B — A` |
| Lista de adjacência | `B` entra só na lista de `A` | `B` entra na lista de `A` **e** `A` na lista de `B` (o laço entra uma vez) |
| Paralelas | duas `A -> B` | duas `A — B` (também `A — B` com `B — A`) |
| Grau | saem / chegam | grau (o laço conta 2) |
| DFS | árvore, retorno, avanço e cruzamento | só árvore e retorno |

### Modelos

Cada modelo é um arquivo `.json` (dá para copiar, mandar para alguém ou apagar). O arquivo
`padrao.txt` guarda o nome do modelo que abre primeiro. Onde ficam:

- rodando pelo código-fonte: na pasta `modelos/` do projeto;
- no programa instalado: em `%APPDATA%\BoscoGraph\modelos` (no Windows, a pasta do perfil do usuário).
  Instalado em "Arquivos de Programas", um programa comum **não pode gravar na própria pasta**; por
  isso os dados do usuário vão para o perfil dele. Na primeira vez, os exemplos são copiados para lá;
- a variável de ambiente `BOSCOGRAPH_DADOS` escolhe outra pasta (por exemplo, num pen drive).

## Importar um grafo

**Importar desenho** (na tela inicial ou no editor, ou Ctrl+O) abre uma tela própria, **uma etapa de
cada vez**, com a trilha das etapas em cima (as que já passaram ficam verdes; clicar na primeira volta
para ela):

1. **Escolher o arquivo**: o botão **Escolher arquivo…** (ou Ctrl+O) abre a janela do sistema; embaixo,
   os formatos que o BoscoGraph entende. Enquanto o arquivo é lido aparece **"Lendo…"** com a barra
   andando (PDF e imagem podem levar alguns segundos; a janela continua respondendo e dá para
   **Cancelar**). Se o arquivo tiver um problema, a explicação aparece **na própria tela**, em vermelho.
2. **Conferir o que foi lido**:
   - à esquerda, a prévia: o grafo desenhado (no PDF e na imagem, o que foi reconhecido aparece **por
     cima** do desenho original, para comparar);
   - à direita, o que foi encontrado, a **orientação** (Orientado `A → B` ou Não orientado `A — B`, com
     o motivo: "lido do arquivo", "pelas setas do desenho" ou "o arquivo não diz"; dá para trocar), os
     **pesos** (**manter** os do arquivo, **tirar** todos ou **sortear** de 1 a 9; cada clique em Sortear
     sorteia de novo), o **desenho** (como no arquivo ou em círculo, quando o arquivo tem as posições) e
     os avisos.
3. **Editar ou visualizar**: escolha a **busca** e um dos dois botões:
   - **Editar grafo**: abre o editor com o grafo importado;
   - **Visualizar grafo**: vai direto para a visualização por partes (se a busca ainda não pode rodar,
     por exemplo um Dijkstra sem pesos, o rodapé avisa e a visualização explica e leva à parte que
     resolve).

O grafo que estava no editor não se perde: ele fica no **Ctrl+Z** do editor. **Início** volta para a tela
inicial sem importar nada. Um arquivo **.bosco** escolhido
aqui vai para a tela do .bosco.

| Fase | Fonte | Extensões | Resultado |
|---|---|---|---|
| 1 | draw.io / diagrams.net | `.drawio`, `.xml` (também o formato compactado) | exato |
| 1 | GraphML (yEd, Gephi, NetworkX) | `.graphml` | exato |
| 1 | DOT (Graphviz) | `.dot`, `.gv` | exato |
| 1 | Planilha | `.csv`, `.tsv`, `.txt` (lista de arestas ou matriz de adjacência) | exato |
| 2 | PDF exportado (draw.io, Graphviz, PowerPoint...) | `.pdf` | quase sempre exato; passa pela conferência com o desenho por baixo |
| 3 | Imagem ou foto | `.png`, `.jpg`, `.bmp`, `.tif`, `.webp`... | pode errar; passa pela conferência com o desenho por baixo |

Regras que valem para todas as fontes:

- **Orientação**: a do arquivo (`digraph`, `edgedefault`); senão, as setas desenhadas (nenhuma seta =
  não orientado); senão (CSV), orientado, com aviso. Num grafo orientado, uma ligação sem seta vira
  ida e volta. Os laços não decidem a orientação (a seta de um laço não diz nada).
- **Nomes**: os nomes do arquivo viram nomes válidos no editor (`Centro de Distribuição` →
  `Centro_d_D`, sem repetir); vértice sem nome ganha A, B, C...
- **Pesos**: um rótulo que é número (`5`, `2,5`, `-3`) vira peso; um rótulo de texto vira o nome da aresta.
- Arquivo com defeito (cortado, embaralhado, vazio) vira uma mensagem, nunca um travamento. Entidades
  de XML (o ataque "billion laughs") são recusadas.

### PDF (fase 2)

Lido com a biblioteca **PyMuPDF**: os desenhos do PDF são classificados em círculos e caixas (vértices),
linhas (arestas) e triângulos pequenos (pontas de seta), e os textos vêm com a posição. O texto dentro
de uma forma é o nome; o texto perto do **meio** de uma linha é o rótulo dela. Funciona para PDF
**desenhado** (exportado de um programa); PDF escaneado é uma imagem: exporte a página e importe a imagem.

### Imagem ou foto (fase 3)

Lida com o **OpenCV** (as formas) e o **Tesseract** (os textos). É a fase que mais erra: uma imagem não
tem objetos, só pixels. O caminho, explicado no próprio código (`importacao/imagem.py`):

1. separar a "tinta" do fundo comparando cada pixel com a vizinhança (funciona com luz desigual);
2. vértices: os buracos redondos ou retangulares da tinta (os buracos das letras são descartados pelo
   tamanho e pela grossura do anel em volta);
3. arestas: com os vértices apagados, cada mancha de tinta que encosta em dois vértices; linhas que se
   cruzam são separadas pelo caminho mais reto;
4. setas: perto de uma ponta com seta, a tinta fica bem mais larga do que no resto da linha;
5. textos: o nome dentro de cada vértice e os rótulos perto das linhas, com correções que usam o resto
   do desenho (maiúsculas, `R1` lido como `Ri`, `l` no lugar de `1`), sempre avisadas.

**Quanto acerta** (medido pelos testes em grafos sorteados desenhados pelo Graphviz, que o teste
compara com a resposta certa):

| | Vértices | Nomes | Ligações e sentidos* | Pesos* |
|---|---|---|---|---|
| Imagem limpa (captura de tela, exportação) | 100% | 100% | 90% | 92% |
| Foto sintética (inclinada, luz desigual, ruído, borrada, JPEG) | 98% | 72% | 90% | 86% |
| Tema escuro com grade de fundo (como o draw.io escuro) | 92% | 85% | 85% | 76% |

\* entre os grafos com os nomes certos. Os erros se concentram em fotos pequenas e borradas (letras com
menos de uns 15 pixels de altura) e em desenhos apertados, com linhas encostando em outros vértices.
Por isso a conferência mostra o que foi reconhecido **por cima** da imagem.

Dicas para a foto acertar mais: de frente, bem iluminada, com os vértices como círculos fechados, letras
grandes e linhas sem encostar umas nas outras.

**Instalar o Tesseract** (só para ler os textos; sem ele, os vértices ganham nomes automáticos):

- Windows: o instalador do BoscoGraph pode trazer junto (componente "Leitor de texto"). Para usar com o
  Python, instale o Tesseract do projeto UB Mannheim (github.com/UB-Mannheim/tesseract) com o idioma
  português. O BoscoGraph procura em `C:\Program Files\Tesseract-OCR`, no PATH ou na variável
  `BOSCOGRAPH_TESSERACT` (o caminho do `tesseract.exe`).
- Linux: `sudo apt install tesseract-ocr tesseract-ocr-por`.

## A visualização por partes

Em cima, os botões desenhados (cada um com a sua cor e o seu ícone): **Início**, **Editar grafo** (volta
ao editor com o grafo como está agora, inclusive as mudanças feitas aqui), o nome do grafo, **Exportar** e
**Exibir** (os dois abrem um menu) e a chave do tema (sol e lua).

À esquerda, a **trilha**: as partes, cada uma com a sua cor, e as opções da busca (qual busca, **de**
onde, **até** onde e o limite). O "até" só aparece nas buscas que usam destino (a busca em profundidade
não usa) e o limite só na profundidade limitada; no Prim, o "de" vira **raiz**, e no Kruskal ele some
(o Kruskal não parte de um vértice); parando o mouse em cima, a dica diz para que cada um
serve naquela busca. Mudar qualquer opção recalcula tudo na hora (Ctrl+Z desfaz). Quando a busca ainda
não pode rodar, o motivo aparece ali mesmo.

| Grupo | Parte | O que mostra | O que dá para fazer |
|---|---|---|---|
| O GRAFO | **Vértices** | cada vértice e com quem se liga; embaixo, o maior grau e a soma dos graus (= 2 × arestas) | **duplo clique** renomeia (na tabela ou no desenho) |
| | **Arestas** | cada aresta: de onde sai, aonde chega, nome, peso, laço, paralela; a densidade | **Orientado / Não orientado**; **duplo clique** renomeia, e em cima do peso (ou na coluna Peso) muda o peso |
| | **Pesos** | os pesos (e a heurística h, nas buscas que usam) e as estatísticas | **Sortear de 1 a 9**, **Pesos…**, **Tirar todos**, **Heurística h…**; **duplo clique** muda o peso (e, na tabela h, o h) |
| | **Lista de adjacência** | Adj[u] de cada vértice, na ordem em que a busca visita (no orientado, para onde as arestas saem) | **Ordenada / Ordem de criação**; **duplo clique** renomeia o vértice |
| | **Matriz de adjacência** | n × n; clicar numa célula mostra no desenho as arestas dela | os modos dos slides: **Contagem** (não orientado, laço = 1), **0 e 1** e **−1 e +1** (orientado), **Pesos**; **▶ Preencher aresta por aresta** |
| | **Matriz de incidência** | n × m, uma coluna por aresta | **1 e −1** (o laço vale 2 no não orientado, ±1 no orientado) e **Pesos**; **▶ Preencher aresta por aresta** |
| | **Tipo do grafo** | simples, completo, valorado, cíclico, DAG, ordem topológica, componentes | a **barra de edição**: **Orientado / Não orientado**, **+ Vértice**, **Nova aresta de … → …** (a mesma ponta nos dois lados = laço; um par que já existe = paralela) e **Remover** (o vértice, com as arestas dele, ou a aresta escolhida com um clique no desenho; a tecla Delete também); o tipo é refeito na hora e o que mudou fica em destaque; escolher uma linha mostra no desenho o que ela aponta (o ciclo, os laços, a ordem…) |
| A BUSCA | **Passo a passo** | cada clique, um passo: o grafo sendo montado do zero (etapas 1 a 4: vértices, arestas, listas e ordenação), a busca (etapa 5) e, no fim, o resultado (etapa 6); os botões das seis etapas, em cima, pulam para o começo de cada uma | **Mostrar**: a estrutura (pilha, fila, duas filas, fila de prioridade, rodadas, a matriz d ou, no Kruskal, as arestas em ordem de peso e os conjuntos), a tabela (cor, d, π…), o código, a explicação e o log |
| | **Linha a linha** | o programa inteiro em Python rodando de verdade, desde a linha 1 | **Mostrar**: variáveis, saída, desenho e explicação; **Pular a chamada** (F10), **Sair da função** (Shift+F11); **escolher uma linha** (veja abaixo) |
| | **Comparar códigos** | duas linguagens **lado a lado**, com a mesma linha destacada | nos dois modos (passo a passo e linha a linha, este desde a linha 1); o desenho começa minimizado |
| | **Resultado** | as conclusões do fim, uma de cada vez, e a tabela final (no Floyd-Warshall, a matriz d final) | escolher uma conclusão mostra no desenho o que ela aponta |

Para a tela não ficar poluída:

- o **desenho** e o **código** ficam em painéis com o botão **–**: minimizado, o painel vira uma faixa
  fina com o nome (um clique traz de volta);
- os botões **Mostrar** ligam e desligam os painéis aos poucos (a tela começa simples);
- o **Exibir** tem o que se usa pouco: pesos e nomes das arestas no desenho, desenho em círculo ou
  **como no arquivo**, tamanho das letras, tela cheia e a lista dos atalhos (o tema fica na chave ao
  lado);
- uma dica discreta, com um lápis, lembra o que o duplo clique faz em cada parte (ela some sozinha
  quando a janela fica estreita demais para ela).

O grafo pode **mudar dentro das partes** (pesos, orientação, nomes, ordenação, e vértices e arestas na
parte Tipo do grafo), inclusive o grafo que acabou de ser importado; cada mudança recalcula tudo e o
**Ctrl+Z** desfaz. Cada parte lembra o que foi
escolhido nela (o passo, a célula, a linha, os painéis): sair e voltar mantém tudo, e o arquivo
**.bosco** guarda tudo isso.

| Tecla | Ação |
|---|---|
| Ctrl + Page Down / Ctrl + Page Up | próxima parte / parte anterior |
| → / ← | próximo / anterior (passo, linha ou aresta, conforme a parte) |
| Espaço | Play / Pausar |
| Home / End | início / fim |
| Page Down / Page Up | passo a passo: próxima etapa / etapa anterior |
| ↑ / ↓ | mais rápido / mais devagar |
| F10 / Shift + F11 | linha a linha: pula a chamada / sai da função |
| Ctrl + Z | desfaz a última mudança no grafo |
| Duplo clique | num vértice, numa aresta ou num peso (na tabela ou no desenho): renomeia ou muda o peso |
| Delete | Tipo do grafo: remove o vértice ou a aresta escolhida no desenho |
| Ctrl + S | exporta o arquivo .bosco |
| Ctrl + roda do mouse, Ctrl + / Ctrl − / Ctrl 0 | letras maiores / menores / normais (de 70% a 200%) |
| F11 / Esc | tela cheia / sair da tela cheia |

- **Velocidade do Play:** botões `0,5×` `1×` `2×` `4×` `8×`, em que `2×` = 2 passos (ou linhas) por
  segundo.
- Também dá para arrastar a linha do tempo e os divisores entre os painéis.

## Linha a linha

O **programa inteiro** da busca em Python (o mesmo arquivo que **Exportar > Código-fonte** grava, com o
grafo dentro) **roda de verdade**, com o `sys.settrace` do Python registrando cada linha (é assim que os
depuradores funcionam), **desde a primeira linha do arquivo**:

1. o **cabeçalho** (comentários: o nome da busca, o grafo, como rodar);
2. o código de estudo: os `import`, as constantes, a `class` e os `def` (que só são **definidos**: o
   corpo roda depois, quando a função é chamada);
3. as funções de ajuda (`numero`, `nome`...), a lista `nomes` e o grafo (`adj` ou `arcos`);
4. `busca = Dijkstra(adj)` (o construtor `__init__` roda e cria os campos do objeto) e a chamada da busca,
   que roda o algoritmo;
5. os `print` do resultado, um vértice por vez, e no fim a **saída esperada**, comentada.

Comentários e linhas em branco **também são passos** (o Python não os executa, mas quem lê passa por
eles): os que ficam logo antes do próximo comando, no mesmo trecho. Um comando de várias linhas (o
dicionário `adj`, por exemplo) é **um** passo, com todas as linhas dele destacadas. Ao entrar numa
função, o passo para na linha do `def`, mostrando o que os parâmetros receberam; quando a função
termina no meio de um comando (um `print` que chamou `numero()`), o passo seguinte é a **volta** para
aquela linha. Em cada clique:

- a linha em **amarelo, com ▶,** é a **próxima a rodar**, como num depurador; a que acabou de rodar
  fica em verde-claro;
- a mensagem de cima explica a linha **com os números do momento**: `novo = d[s] + peso = 0 + 10 = 10`,
  `novo = 10 < d[t] = ∞? Sim: passar por s é mais barato.`; embaixo, a pilha de chamadas
  (`em relaxar() ← dijkstra()`; numa recursão funda da DFS, as de cima e quantas são);
- o painel **Variáveis** mostra a memória do programa: a pilha de chamadas (a função que está rodando
  em cima e, no fundo, o **programa**, o nível de fora das funções, com `nomes`, `adj`, `busca`...) e os
  campos do objeto da busca; o que acabou de mudar fica em amarelo;
- o painel **Saída** mostra o que o programa já escreveu (o `print`), como no terminal; o que a última
  linha escreveu fica em destaque. No fim, ele é igual à saída esperada do fim do arquivo;
- o desenho acompanha: cada passo da busca aparece quando a linha que o faz já rodou.

Para não passar por tudo: **Pular a chamada** (F10) roda de uma vez a função chamada na linha (na
linha `busca.dijkstra("s")`, pula a busca inteira e vai para os `print`); **Sair da função**
(Shift+F11) roda até a função de agora terminar.

**Escolher de onde partir:** clique numa linha do código (em qualquer linguagem). Aparece quantas vezes
ela roda neste grafo e quantas já rodaram, com os botões **|◀ primeira**, **◀ anterior**,
**próxima ▶** e **última ▶|**: por exemplo, para ver a terceira vez que um vértice é relaxado no
Dijkstra, clique na linha do relaxamento e em próxima ▶ três vezes. Clicando na linha de outra
linguagem (Java, C...), valem as vezes da linha que faz o mesmo no Python.

Observação honesta: um passo do desenho às vezes corresponde a duas ou três linhas. No Dijkstra, por
exemplo, o passo "relaxar" muda d **e** o pai de uma vez, e o código faz isso em duas linhas seguidas:
o desenho já mostra o pai novo enquanto a linha `pai[v] = u` ainda é a próxima. O painel Variáveis
mostra sempre o valor exato de cada linha.

## O código em seis linguagens

O painel de código tem duas caixas de escolha:

- **Linguagem**: o **Código do BoscoGraph** (os arquivos do próprio programa, que fazem a busca e
  anotam cada passo para a tela) ou o **programa da busca** em **Pseudocódigo, Python, Java, C, C++ e
  JavaScript**: o arquivo inteiro, o mesmo que a exportação grava (o cabeçalho, o código de estudo da
  pasta `estudo/`, a busca escrita como no livro do Cormen, o grafo e a chamada);
- **Comparar com**: uma segunda linguagem, com a mesma linha destacada (na parte Comparar códigos, as
  duas ficam lado a lado).

Como a mesma linha é achada em todas as linguagens: cada linha tem um **rótulo**, o mesmo em todas as
linguagens. Os rótulos não aparecem na tela. São de três tipos:

- os do **código de estudo**: cada linha da busca termina com um (`// @relaxar_melhorou`,
  `# @relaxar_melhorou` no Python);
- os do **resto do programa**, que o gerador de código põe em cada linha que escreve: `cabecalho_1`,
  `cabecalho_2`... (a linha 3 do cabeçalho é a linha 3 em todas), `principal_grafo` (o `adj` do Python,
  os `ligar(...)` do C), `principal_buscar` (a chamada da busca), `aux_numero` (a função que escreve os
  números) e assim por diante;
- os da **estrutura**, achados automaticamente pelo jeito da linha (`estudo/estrutura.py`): `import`
  e `#include`, as constantes (`BRANCO = "Branco"` no Python e `static final String BRANCO = ...` no
  Java), a classe, o construtor (`__init__`, `constructor`, `Dijkstra(...)`), os campos (`self.cor = {}`
  no Python, `final Map<...> cor` no Java, `enum Cor cor[MAX];` no C) e as funções (`extrair_minimo`,
  `extrairMinimo` e `EXTRAIR-MÍNIMO` são a mesma); o comentário logo em cima de uma função vai junto
  com ela.

No passo a passo, a linha destacada é a que faz o passo; no linha a linha, a próxima que o Python vai
rodar (nas outras linguagens, a que tem o mesmo rótulo; quando a linha do Python não tem par na outra
linguagem, como o `__init__` no C, nada fica destacado lá).

Cada linguagem do seu jeito (os comentários de cada arquivo explicam):

| Linguagem | Dicionários | Fila | Infinito | Observação |
|---|---|---|---|---|
| Pseudocódigo | atributos (`v.d`, `v.π`) | `INSERIR`, `EXTRAIR-MÍNIMO` | ∞ | o estilo do livro, em português |
| Python | `dict` | `deque` (BFS) e lista | `Decimal("Infinity")` | o que roda no linha a linha; números decimais exatos |
| Java | `HashMap` | `ArrayDeque` (BFS) e `ArrayList` | `Double.POSITIVE_INFINITY` | `record` para o vizinho; `List.of(u, v)` como chave de par |
| C | vetores indexados pelo número do vértice | vetor | `INFINITY` | vértices numerados de 0 a n − 1; lista de adjacência encadeada |
| C++ | `std::map` | `std::deque` (BFS) e `std::vector` | `numeric_limits<double>::infinity()` | `std::pair` como chave de par |
| JavaScript | `Map` | `Array` | `Infinity` | o par (u, v) vira texto com `JSON.stringify` (o `Map` compara listas pela referência) |

Java, C, C++ e JavaScript usam `double`: com pesos decimais, `0.1 + 0.2` dá `0.30000000000000004`.
Os testes conferem as traduções com pesos inteiros, em que o `double` é exato.

O Kruskal ordena as arestas com uma ordenação **estável** em todas as linguagens (`sorted` no Python,
`List.sort` no Java, `std::stable_sort` no C++, `sort` no JavaScript e, no C, a ordenação por inserção):
as arestas de mesmo peso ficam na ordem em que foram criadas, então os empates saem iguais nas seis.

## Exportar

O menu **Exportar** da visualização:

| Opção | O que sai |
|---|---|
| **Imagem do desenho (PNG)** | o desenho **como está na parte aberta** (o passo, as cores, o que foi escolhido), 1500 × 1125 pixels, com as bordas suaves. Precisa da biblioteca Pillow |
| **Imagem do desenho (SVG, vetorial)** | o mesmo desenho em SVG: abre no navegador e no Word e não perde qualidade ao ampliar (bom para slides e relatórios) |
| **PDF só com o desenho** | uma página A4 deitada com o título e o desenho |
| **Relatório completo em PDF** | várias páginas: capa (o resumo e o desenho), vértices e arestas, lista de adjacência, as matrizes de adjacência e de incidência (nos modos dos slides), as estatísticas dos pesos e a heurística, o tipo do grafo, o passo a passo da busca, o resultado (as conclusões, o desenho do fim e a tabela final ou as matrizes d e π), o pseudocódigo e o Python de estudo. Cada seção tem a cor da parte da tela |
| **Arquivo do BoscoGraph (.bosco)** (Ctrl+S) | o grafo, a busca e **a tela como está**: a parte aberta, o passo, a linha escolhida, os painéis ligados e minimizados, o menu Exibir, o tema e o tamanho das letras |
| **Código-fonte da busca, com este grafo** | um programa completo, num arquivo só, em **Python, Java, C, C++, JavaScript** ou o **pseudocódigo** (texto) |

Detalhes:

- **Como o desenho vira imagem**: o Tkinter não sabe salvar um Canvas como imagem. Então o BoscoGraph
  desenha o grafo de novo num Canvas que nem aparece na tela, lê cada item que o Tkinter criou (linhas,
  círculos, textos, com cores, espessuras e posições) e monta uma lista de formas, que o SVG, o PNG e o
  PDF sabem desenhar. A curva das arestas e a ponta da seta são calculadas com as mesmas contas do
  Tkinter (`exportacao/geometria.py`), para sair igual à tela.
- **O PDF** é escrito por um escritor próprio (`exportacao/pdf.py`), só com a biblioteca padrão do
  Python: as fontes padrão de todo leitor de PDF (Helvetica e Courier, com os acentos do português) e a
  fonte Symbol para ∞, π, → e ≤. O próprio arquivo explica como um PDF é por dentro.
- **O .bosco** é um texto JSON (dá para abrir no Bloco de Notas). Quem tem o BoscoGraph instalado abre
  com **duplo clique** (o instalador associa a extensão), pela tela inicial (**Abrir arquivo .bosco**)
  ou pela linha de comando (`python boscograph.py grafo.bosco`). A tela do .bosco mostra os **abertos
  recentemente** (os que você abriu ou salvou por último, o mais novo em cima) e, antes de abrir, uma
  **prévia**: o nome, a busca, quantos vértices e arestas, quando foi salvo, em que parte a visualização
  vai abrir e o desenho do grafo. Tudo é conferido ao abrir: um arquivo estragado (ou que sumiu) mostra
  a explicação **na própria tela**, com o que pode ter acontecido, **Escolher outro arquivo** e **Tirar
  da lista**; o que não serve mais (uma célula fora da matriz, uma linguagem desconhecida) é esquecido:
  a parte abre do começo.
- **O código-fonte** tem três partes: o código de estudo da busca (o mesmo do linha a linha, sem os
  rótulos), o grafo escrito na linguagem com a chamada da busca e, no fim, num comentário, a **saída
  esperada**, calculada pelo BoscoGraph na hora de exportar, para conferir. A saída é igual nas cinco
  linguagens. O cabeçalho do arquivo diz como rodar:

  | Linguagem | Como rodar |
  |---|---|
  | Python | `python busca.py` |
  | Java (16 ou mais novo) | `java Busca.java` (ou `javac -encoding UTF-8 Busca.java` e `java Programa`) |
  | C | `gcc -std=c11 busca.c -o busca -lm` e `./busca` (no Windows, `busca.exe`) |
  | C++ | `g++ -std=c++17 busca.cpp -o busca` e `./busca` |
  | JavaScript | `node busca.js` |

  Com pesos decimais, o Java, o C, o C++ e o JavaScript usam `double` e podem mostrar o erro de
  arredondamento (`0.30000000000000004`); o Python usa `Decimal`, exato como o BoscoGraph.

## Executável e instalador (Windows)

```
pip install -r requirements-construcao.txt
python construir.py
```

O `construir.py` faz, em ordem, parando no primeiro erro:

1. roda os **testes**;
2. gera o **ícone** do Windows (`instalador/boscograph.ico`, com os tamanhos de 16 a 256 pixels) e as
   **imagens das telas do instalador** (`instalador/assistente_*.bmp`, nas cores da paleta);
3. gera o **executável** com o PyInstaller (receita `BoscoGraph.spec`): a pasta `dist\BoscoGraph`, com o
   `BoscoGraph.exe` (programa de janela, sem terminal). Os arquivos `.py` que o painel de código mostra
   e o código de estudo das seis linguagens vão junto como **dados**, porque o executável guarda o
   código só compilado (e o linha a linha e a exportação do código-fonte leem esses arquivos);
4. roda o **autoteste** no executável recém-gerado (`BoscoGraph.exe --verificar`), com uma pasta de
   dados temporária: se faltou algum arquivo no pacote, o erro aparece aqui, e não na mão do usuário;
5. gera o **instalador** com o Inno Setup 6 (receita `instalador\BoscoGraph.iss`), se ele estiver
   instalado: `instalador\saida\BoscoGraph-7.3-instalador.exe`.

O instalador tem três telas, e quem instala só clica em **Avançar**, **Eu aceito o acordo** +
**Avançar** e **Concluir**:

1. **boas-vindas**: o agradecimento, por que o BoscoGraph foi feito e quem fez (criador, co-criadores e
   entusiastas, os professores);
2. **termos de uso** (`instalador/termos_de_uso.txt`, um texto simples que dá para mudar);
3. **fim**: o agradecimento de novo, com "Abrir o BoscoGraph agora" já marcado.

O resto não pergunta nada:

- instala **só para quem está usando o computador**, em `%LOCALAPPDATA%\Programs\BoscoGraph`, **sem
  pedir senha de administrador** (nem a janela do Controle de Conta de Usuário): funciona também num
  computador de laboratório;
- cria os atalhos no menu Iniciar e na área de trabalho;
- **associa os arquivos .bosco** ao BoscoGraph: duplo clique num .bosco abre o programa direto na
  visualização;
- leva o **leitor de texto (Tesseract)** se a pasta `instalador\tesseract` existir na hora de compilar
  (copie para lá a pasta do Tesseract instalado, com `tesseract.exe` e `tessdata` com `por.traineddata`);
- **não apaga** `%APPDATA%\BoscoGraph` ao desinstalar: os modelos salvos são do usuário.

Observações honestas:

- O executável tem uns 300 MB (o OpenCV e a PyMuPDF são a maior parte); o instalador comprime para bem
  menos. Quem não precisa importar PDF e imagem pode gerar sem essas bibliotecas instaladas: o
  executável fica pequeno e a importação desses formatos mostra como instalar.
- Sem assinatura digital (um certificado pago), o Windows pode desconfiar de um programa novo:
  - "O Windows protegeu o computador" (SmartScreen, num instalador baixado da internet): **Mais
    informações → Executar assim mesmo**;
  - "O Controle Inteligente de Aplicativos bloqueou..." ou "Uma política de Controle de Aplicativo bloqueou
    este arquivo" (Windows 11): esse não deixa passar programa sem assinatura, nem o BoscoGraph.exe que o
    `construir.py` acabou de gerar (o autoteste da etapa 4 para aí). Só um instalador assinado resolve, ou
    desligar o controle em Segurança do Windows → Controle de aplicativos e navegador → Configurações do
    Controle Inteligente de Aplicativos (desde a atualização de abril de 2026, dá para religar depois
    sem reinstalar o Windows). Assinar custa: certificado OV, uns US$ 150–300 por ano (com token); o
    Azure Artifact Signing ainda não aceita pessoa física fora dos EUA e do Canadá; a SignPath Foundation
    assina de graça projetos de código aberto;
  - "Ameaça encontrada" (Segurança do Windows): um falso positivo do antivírus; dá para mandar o arquivo
    para a Microsoft conferir (https://www.microsoft.com/wdsi/filesubmission).
- O PyInstaller gera o executável **para o sistema em que roda**: para o `.exe`, rode o `construir.py`
  no Windows.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `boscograph.py` | monta o grafo, roda a busca e anota cada passo (`montar_passos`); abre o programa (e um .bosco) |
| `algoritmos.py` | os doze algoritmos: nomes, requisitos e a conferência antes de rodar (heurística admissível e consistente, limite, tamanho da árvore de busca, grafo não orientado e partes desligadas na árvore mínima) |
| `entrada.py` | nomes, números (`Decimal`), validações, sorteios, arestas em texto e resumo |
| `representacoes.py` | as matrizes de adjacência e de incidência (nas convenções dos slides), as listas de saída e de entrada e as estatísticas dos pesos (sem Tkinter) |
| `pesos.py` | o que a janela "Pesos e heurística" faz (sem Tkinter) |
| `modelos.py` e `modelos/` | salvar e carregar modelos; os modelos de exemplo |
| `caminhos.py` | onde estão os recursos (no executável, `sys._MEIPASS`), onde gravar os dados (`%APPDATA%`), a versão e nomes de arquivo válidos |
| `classes/` | `Vertice`, `Aresta`, `Grafo`, as buscas (`BuscaEmProfundidade`, `BuscaEmProfundidadeLimitada`, `AprofundamentoIterativo`, `BuscaEmLargura`, `BuscaBidirecional`, `Dijkstra`, `BellmanFord`, `FloydWarshall`, `BuscaGulosa`, `AEstrela`), a árvore geradora mínima (`Prim`, `Kruskal`), `TipoDoGrafo` e `ResultadoDaBusca` |
| `importacao/` | a importação: `arquivos.py` (fase 1), `pdf.py` (fase 2), `imagem.py` (fase 3), `montagem.py` e `geometria.py` (o que PDF e imagem têm em comum) |
| `exportacao/` | as exportações, sem Tkinter: `pdf.py` (o escritor de PDF), `geometria.py` (curvas, setas e tracejado como no Tk), `figura.py` (SVG, PNG e o desenho no PDF), `relatorio.py` (arruma o relatório nas páginas), `bosco.py` (o arquivo .bosco) e `codigo_fonte.py` (o programa em cada linguagem) |
| `visual/` | as telas: `aplicativo.py`, `inicio.py` (a tela inicial), `tela_importar.py` (a importação em etapas), `tela_bosco.py` (abrir um .bosco), `sobre.py` (a janela Sobre), `editor.py` e `etapas_do_editor.py` (o editor em três etapas), `visualizacao.py` (a tela por partes), `sessao.py` (o grafo e tudo o que é calculado dele, sem Tkinter), `parte.py`, `partes_do_grafo.py` e `partes_da_busca.py` (as onze partes), `componentes.py` (painel minimizável, tocador e botões "Mostrar"), `grafo_na_tela.py` (o desenho), `estruturas.py` (pilha, filas, rodadas, conjuntos), `matrizes.py` (a grade das matrizes), `codigo.py` (o painel de código), `variaveis.py` (o painel Variáveis), `exportar.py` e `conteudo_do_relatorio.py` (o menu Exportar), `importacao.py` (a conferência), `dialogos.py`, `perfis.py` e `explicacoes.py` (o que cada busca mostra e explica), `estado.py`, `desenho.py`, `tema.py`, `dica.py`, `logo.py`; os componentes desenhados: `botoes.py` (os botões com ícone e cor por papel, os cartões, a chave do tema, os segmentos e as etapas), `campos.py` (a caixa de texto, o contador, a chave liga/desliga, a caixa de escolha, o selo e a escolha da busca, uma coluna por tipo), `cabecalho.py` (o topo das telas), `rolagem.py` (o quadro que rola) e `previa.py` (o desenho pequeno de um grafo) |
| `estudo/` | o código de estudo dos doze algoritmos em seis linguagens (`pseudocodigo/`, `python/`, `java/`, `c/`, `cpp/`, `javascript/`); `rastreador.py` (roda o Python linha a linha: só a busca, ou o programa inteiro desde a linha 1); `estrutura.py` (os rótulos automáticos da estrutura do programa em cada linguagem); `explicacoes.py` (a explicação de cada linha, com os valores); `conferencia/` (os programas que os testes usam para rodar as traduções) |
| `verificacao.py` | o autoteste (`--verificar`) |
| `construir.py`, `BoscoGraph.spec`, `instalador/` | executável e instalador |
| `testes*.py` | conferências automáticas (veja abaixo) |
| `exemplos_importacao/` | arquivos de exemplo de cada formato (usados nos testes) |

## O que os testes conferem

`python testes.py` (uns 8 minutos; a imagem é a parte mais demorada) confere, sem mostrar janela:

- **DFS**: o grafo da prova dá exatamente os tempos d/f da prova; em 400 grafos sorteados, orientados e
  não orientados: teorema dos parênteses, classificação das arestas, ciclos (conferidos com o algoritmo
  de Kahn), componentes (conferidas com união-busca), DAG e ordem topológica.
- **Outras buscas**, sempre comparadas com um algoritmo independente: BFS, Dijkstra e Bellman-Ford com
  o Floyd-Warshall (300 a 400 grafos cada; quase metade dos do Bellman-Ford com ciclo negativo), A\* e
  gulosa (250, com h zero, exata e admissível) e os exemplos do livro (CLRS 24.4 e 24.6).
- **Buscas novas** (`testes_novas_buscas.py`): a profundidade limitada com a **força bruta** (todos os
  caminhos simples, 400 grafos: achou ⇔ existe caminho até o limite, cortes certos); o aprofundamento
  iterativo e a bidirecional com a BFS (o caminho com menos arestas; a bidirecional expandindo menos);
  o Floyd-Warshall com o Bellman-Ford rodado de cada vértice (250 grafos, com ciclos negativos) e a
  matriz D(5) inteira do exemplo CLRS 25.1.
- **Árvore geradora mínima** (`testes_arvore_minima.py`): o Prim e o Kruskal com a **força bruta** (400
  grafos com pesos repetidos, fracionados e negativos, laços, paralelas e partes desligadas: todas as
  escolhas de n − partes arestas sem ciclo; a resposta tem que ser uma floresta que liga cada parte, com
  o menor peso possível); um com o outro (o mesmo peso e, com os pesos todos diferentes, as mesmas
  arestas, e a frase "a árvore mínima é única" só quando é verdade); e os exemplos do livro (CLRS 23.4
  e 23.5: as arestas do Kruskal na ordem do livro, peso 37).
- **Tela** (`testes.py`, `testes_novas_buscas.py` e `testes_arvore_minima.py`): em 800 buscas, cada
  passo é reproduzido e conferido (pilha, filas, matriz, árvore, a aresta tracejada de cada vértice da
  fila do Prim, os conjuntos do Kruskal, código destacado e explicações).
- **Importação**: os exemplos de cada formato dão o grafo exato; 200 grafos sorteados escritos em DOT,
  GraphML, draw.io e CSV e lidos de volta; 600 arquivos com defeito viram mensagem; 150 PDFs sorteados
  do Graphviz (estrutura 100%, rótulos 97,6%); e as imagens: os exemplos exatos e as taxas da tabela
  acima, em 40 imagens limpas e 40 fotos sintéticas (o teste falha se alguma taxa cair abaixo do mínimo).
- **Autoteste** (`--verificar`): passa pelo código-fonte.
- **Código de estudo** (`testes_estudo.py`): o Python de estudo faz **a mesma busca** que o BoscoGraph
  em 150 grafos sorteados de cada um dos doze algoritmos (e em mais 75 em que o A\* **reabre** vértices);
  cada passo casa com a linha certa e o estado final é igual; **todas as linhas** do código de estudo
  rodam em algum grafo; os rótulos batem nas seis linguagens; **Java, C, C++ e JavaScript compilam sem
  nenhum aviso** (`-Werror`) e dão o mesmo estado final que o Python em 60 grafos de cada busca; e o
  **programa inteiro** (o linha a linha), em 40 grafos de cada busca: começa na linha 1 do cabeçalho,
  passa por todas as linhas do nível de fora até a última, toda linha executada tem rótulo e
  explicação, a busca casa com os passos do BoscoGraph, o `print` escreve exatamente a saída esperada,
  as outras linguagens têm os mesmos rótulos e o texto é o mesmo que a exportação grava.
- **Telas** (`testes_tela.py`, com a janela escondida), a partir do "Ver exemplo" de cada busca: as onze
  partes abrem e respondem ao teclado; o passo a passo começa com o grafo vazio, com as seis etapas e o
  Page Down / Page Up; no passo a passo e no linha a linha, **todos os passos e todas as linhas**,
  conferindo a linha destacada no código (em quatro linguagens), a pilha de chamadas e o desenho;
  escolher uma linha leva às vezes certas; a comparação lado a lado; as mudanças dentro das partes com o
  Ctrl+Z; todas as exportações a partir da tela, com o .bosco reaberto no mesmo passo; o tema e a volta
  ao editor; a **importação em etapas** (o erro na própria tela, a leitura em segundo plano e o Cancelar,
  a conferência, o tema sem perder as escolhas, Visualizar e Editar grafo, e o Ctrl+Z voltando para o
  grafo de antes); um .bosco estragado de propósito abrindo sem erro; a **tela inicial** (a sanfona, com
  a animação, o cartão que muda com a escolha, as setas e o Enter, a chave do tema, o Ctrl + roda do
  mouse de 70% a 200%, o Sobre com os nomes, o Começar do zero e todos os ícones desenhados); a **tela do
  .bosco** (recentes, prévia, Abrir, arquivo estragado explicado na tela e Tirar da lista); e as
  **correções da 7.1** (os botões do topo, o "até" só com destino, as partes do grafo sem o que saiu, o
  duplo clique renomeando e mudando peso e h na tabela e no desenho, e a barra de edição do Tipo do
  grafo, com o tipo mudando junto e o Ctrl+Z voltando tudo); e o **editor em etapas** (uma etapa por
  tela, a trilha, o Voltar e o Próximo, a animação, a Quantidade criando e tirando (também sem o Enter),
  os nomes 1, 2, 3 com o Ctrl+Z, a aresta editada inteira com a posição, o sorteio, a escolha da busca
  (uma coluna por tipo) com o que falta e os botões que resolvem, o Salvar pedindo o nome, o Tornar
  padrão, o tema mantendo a etapa, nenhum componente antigo do ttk na tela) e os **cartões da tela
  inicial**.
- **PDF** (`testes_pdf.py`): o arquivo é desmontado de novo (a tabela xref aponta para cada objeto), as
  larguras das letras batem com as tabelas da Adobe, e um leitor de PDF de verdade (PyMuPDF) devolve os
  textos com acentos e símbolos, as posições e os desenhos (a curva igual à do Tkinter, a ponta de seta).
- **Exportações** (`testes_exportacao.py`): 150 arquivos .bosco salvos e lidos iguais (pesos decimais
  exatos) e 10 estragados virando mensagem; a prévia (data e programa que salvou) e a lista dos abertos
  recentemente (o mais novo em cima, sem repetir, no máximo 6, sem erro com arquivo faltando ou sem
  permissão); **282 programas de código-fonte** (os doze algoritmos, nas cinco
  linguagens, com pesos inteiros, com quartos como 2,75 e um caminho com distâncias acima de 10
  milhões) compilam sem avisos e escrevem exatamente a saída esperada; as figuras (SVG válido, PNG com
  as cores no lugar certo); e o relatório (tabelas que continuam na página seguinte com o cabeçalho,
  matrizes largas em pedaços, a indentação do código e o rodapé em todas as páginas).

Os próprios testes das exportações foram conferidos com **12 defeitos colocados de propósito** (a seta
saindo do lado errado, o tracejado sem traços, o cabeçalho da tabela sem repetir, o Java escrevendo
`1.0999991E7`, o .bosco esquecendo as posições...): pegaram os 12. Os da versão 7.3, com **22 defeitos**
(o Prim sem pular quem já está na árvore ou tirando o último no empate, o Kruskal sem ordenar as
arestas ou com a união pela metade, a aresta antiga do Prim continuando tracejada, o C ordenando sem
estabilidade, o Passo a passo começando com o grafo pronto, a chave do tema recriando a tela dentro da
própria animação...): pegaram os 22.

Alguns testes só rodam se a biblioteca ou o programa estiver instalado (PyMuPDF, OpenCV, Tesseract,
Pillow, Graphviz, java, gcc, g++, node, uma tela gráfica); senão, aparecem como pulados.
