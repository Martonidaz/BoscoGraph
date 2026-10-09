// Busca em profundidade (DFS), como DFS(G) e DFS-VISIT(G, u) do livro do Cormen (CLRS).
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e cor[u], d[u]... são vetores
// comuns (a posição u guarda o valor do vértice u). O nome de cada vértice fica fora daqui.
//   cor[u]     -> BRANCO (não descoberto), CINZA (em exploração) ou PRETO (terminado)
//   d[u], f[u] -> os tempos de descoberta e de término;  pai[u] -> de onde a busca chegou
//   adj[u]     -> a lista de adjacência de u: uma lista ENCADEADA (cada nó aponta o próximo)
//   tipo[u][v] -> o tipo da aresta u -> v: árvore, retorno, avanço ou cruzamento
// No grafo não orientado, voltas[u][v] conta as metades de aresta já examinadas pelo outro lado.

#include <stdbool.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro); macro sempre entre parênteses

enum Cor { BRANCO, CINZA, PRETO };

// Um nó da lista de adjacência
typedef struct Vizinho {
    int v;                              // o número do vizinho
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u
bool direcionado;

enum Cor cor[MAX];
int d[MAX];
int f[MAX];
int pai[MAX];
int tempo;
int voltas[MAX][MAX];                   // variável global começa zerada
const char *tipo[MAX][MAX];             // e ponteiro global começa NULL (ainda sem tipo)

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
void dfs_visit(int u);
const char *classificar(int u, int v);
void anotar_volta(int u, int v);

void dfs(const int ordem[]) {
    for (int u = 0; u < n; u++) {                               // @pinta_cada
        cor[u] = BRANCO;                                        // @pintar_branco
        pai[u] = NIL;                                           // @pai_nulo
    }
    tempo = 0;                                                  // @zerar_tempo
    for (int i = 0; i < n; i++) {                               // @cada_raiz
        int u = ordem[i];                                       // @cada_raiz
        if (cor[u] == BRANCO) {                                 // @raiz_branca
            dfs_visit(u);                                       // @nova_arvore
        }
    }
}

void dfs_visit(int u) {
    tempo = tempo + 1;                                          // @tempo_d
    d[u] = tempo;                                               // @anota_d
    cor[u] = CINZA;                                             // @descobrir
    for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
        int v = atual->v;                                       // @cada_vizinho
        if (voltas[u][v] > 0) {                                 // @e_volta
            voltas[u][v] = voltas[u][v] - 1;                    // @revisitar
        } else if (cor[v] == BRANCO) {                          // @vizinho_branco
            tipo[u][v] = "árvore";                              // @examinar_arvore
            anotar_volta(u, v);                                 // @volta_arvore
            pai[v] = u;                                         // @pai_v
            dfs_visit(v);                                       // @desce
        } else {
            tipo[u][v] = classificar(u, v);                     // @examinar_outra
            anotar_volta(u, v);                                 // @volta_outra
        }
    }
    cor[u] = PRETO;                                             // @pintar_preto
    tempo = tempo + 1;                                          // @tempo_f
    f[u] = tempo;                                               // @finalizar
}

// A aresta u -> v leva a um vértice já descoberto: retorno, avanço ou cruzamento
const char *classificar(int u, int v) {
    if (cor[v] == CINZA) {                                      // @se_cinza
        return "retorno";                                       // @retorno
    }
    if (d[u] < d[v]) {                                          // @se_descendente
        return "avanço";                                        // @avanco
    }
    return "cruzamento";                                        // @cruzamento
}

// Só no não orientado (e fora do laço): a outra metade da aresta, v — u, fica anotada
void anotar_volta(int u, int v) {
    if (!direcionado && u != v) {                               // @se_nao_orientado
        voltas[v][u] = voltas[v][u] + 1;                        // @anota_volta
    }
}
