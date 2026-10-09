// Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do livro do Cormen (CLRS).
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e conjunto[v] é um vetor.
//   conjunto[v] -> o representante do conjunto de v (MAKE-SET, FIND-SET e UNION do livro)
//   arestas     -> arestas[0] até arestas[m - 1], uma vez cada, na ordem em que foram criadas
//   arvore      -> as arestas aceitas: arvore[0] até arvore[quantas_na_arvore - 1]
// O C não tem uma ordenação estável pronta (o qsort não garante a ordem dos empates): ordenar_por_peso é a
// ordenação por inserção, que é estável (as arestas de mesmo peso ficam na ordem em que foram criadas).
// unir percorre todos os vértices: O(V) por união (com a floresta de conjuntos do livro, quase O(1)).
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// números decimais exatos.

#define MAX 100                         // o maior número de vértices
#define MAX_ARESTAS 1000                // o maior número de arestas
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)

typedef struct Aresta {
    int u;                              // as duas pontas da aresta u — v
    int v;
    double peso;
} Aresta;

int n;                                  // quantos vértices o grafo tem
Aresta arestas[MAX_ARESTAS];
int m;                                  // quantas arestas
int conjunto[MAX];
Aresta arvore[MAX];
int quantas_na_arvore = 0;

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
void ordenar_por_peso(Aresta lista[], int quantas);
void unir(int a, int b);

void kruskal(void) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        conjunto[v] = v;                                        // @criar_conjunto
    }
    Aresta ordenadas[MAX_ARESTAS];                              // @ordenar_arestas
    for (int i = 0; i < m; i++) {                               // @ordenar_arestas
        ordenadas[i] = arestas[i];                              // @ordenar_arestas
    }
    ordenar_por_peso(ordenadas, m);                             // @ordenar_arestas
    for (int i = 0; i < m; i++) {                               // @cada_aresta
        int u = ordenadas[i].u;                                 // @cada_aresta
        int v = ordenadas[i].v;                                 // @cada_aresta
        if (conjunto[u] == conjunto[v]) {                       // @rejeitar
            continue;                                           // @pula_aresta
        }
        arvore[quantas_na_arvore] = ordenadas[i];               // @aceitar
        quantas_na_arvore = quantas_na_arvore + 1;              // @aceitar
        unir(conjunto[u], conjunto[v]);                         // @unir
    }
}

// UNION: todos os vértices do conjunto b passam para o conjunto a
void unir(int a, int b) {
    for (int x = 0; x < n; x++) {                               // @cada_do_conjunto
        if (conjunto[x] == b) {                                 // @mesmo_conjunto
            conjunto[x] = a;                                    // @muda_conjunto
        }
    }
}

// Ordenação por inserção: cada aresta anda para a esquerda enquanto a de lá for mais PESADA (só mais
// pesada: a de mesmo peso não é ultrapassada, por isso os empates ficam na ordem em que foram criados)
void ordenar_por_peso(Aresta lista[], int quantas) {
    for (int i = 1; i < quantas; i++) {                         // @ordenar_arestas
        Aresta atual = lista[i];                                // @ordenar_arestas
        int j = i - 1;                                          // @ordenar_arestas
        while (j >= 0 && lista[j].peso > atual.peso) {          // @ordenar_arestas
            lista[j + 1] = lista[j];                            // @ordenar_arestas
            j = j - 1;                                          // @ordenar_arestas
        }
        lista[j + 1] = atual;                                   // @ordenar_arestas
    }
}
