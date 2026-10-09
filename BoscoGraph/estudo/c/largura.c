// Busca em largura (BFS), como BFS(G, s) do livro do Cormen (CLRS).
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e cor[v], d[v]... são vetores
// comuns (a posição v guarda o valor do vértice v). O nome de cada vértice fica fora daqui.
//   cor[v]  -> BRANCO (não descoberto), CINZA (descoberto, na fila) ou PRETO (terminado)
//   d[v]    -> o menor número de arestas de s até v (INFINITO = não alcançado)
//   pai[v]  -> de qual vértice a busca chegou em v (NIL = nenhum)
//   fila    -> fila[inicio] até fila[fim - 1]: entra no fim, sai do início, as duas pontas em O(1).
//              Cada vértice entra uma vez só, então MAX posições bastam.

#include <math.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define INFINITO INFINITY               // o infinito do ponto flutuante (de math.h)

enum Cor { BRANCO, CINZA, PRETO };

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    double peso;                        // o peso da aresta (a BFS não usa)
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u

enum Cor cor[MAX];
double d[MAX];
int pai[MAX];
int fila[MAX];
int inicio = 0;
int fim = 0;

void bfs(int s) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        d[v] = INFINITO;                                        // @d_infinito
        pai[v] = NIL;                                           // @inicializar
    }
    cor[s] = CINZA;                                             // @origem_cinza
    d[s] = 0;                                                   // @origem_d
    fila[fim] = s;                                              // @origem
    fim = fim + 1;                                              // @origem
    while (inicio < fim) {                                      // @enquanto_fila
        int u = fila[inicio];                                   // @desenfileirar
        inicio = inicio + 1;                                    // @desenfileirar
        for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
            int v = atual->v;                                   // @cada_vizinho
            if (cor[v] == BRANCO) {                             // @ignorar_vizinho
                cor[v] = CINZA;                                 // @pinta_cinza
                d[v] = d[u] + 1;                                // @d_mais_um
                pai[v] = u;                                     // @pai_v
                fila[fim] = v;                                  // @descobrir_vizinho
                fim = fim + 1;                                  // @descobrir_vizinho
            }
        }
        cor[u] = PRETO;                                         // @terminar_vertice
    }
}
