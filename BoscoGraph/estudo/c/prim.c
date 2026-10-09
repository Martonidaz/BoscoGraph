// Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do livro do Cormen (CLRS), na mesma
// forma do Dijkstra daqui: a fila de prioridade só guarda os vértices já alcançados.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e chave[v], pai[v]... são vetores.
//   chave[v] -> o peso da aresta mais leve conhecida que liga v à árvore (INFINITO = nenhuma ainda)
//   pai[v]   -> a outra ponta dessa aresta, que já está na árvore (NIL = nenhum)
//   cor[v]   -> BRANCO (fora, sem ligação), CINZA (na fila) ou PRETO (já está na árvore)
//   fila     -> fila[0] até fila[tamanho - 1], na ordem em que entraram
// Como no DFS(G), uma árvore nova começa em cada parte desligada (raizes: a escolhida primeiro, depois os
// outros vértices): é a floresta geradora mínima. extrair_minimo percorre a fila toda: O(V).
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// números decimais exatos.

#include <math.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define INFINITO INFINITY               // o infinito do ponto flutuante (de math.h)

enum Cor { BRANCO, CINZA, PRETO };

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    double peso;                        // o peso da aresta u — v
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u

enum Cor cor[MAX];
double chave[MAX];
int pai[MAX];
int fila[MAX];
int tamanho = 0;                        // quantos vértices estão na fila

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
void crescer(int r);
int extrair_minimo(void);

void prim(const int raizes[]) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        chave[v] = INFINITO;                                    // @chave_infinito
        pai[v] = NIL;                                           // @inicializar
    }
    for (int i = 0; i < n; i++) {                               // @cada_raiz
        int r = raizes[i];                                      // @cada_raiz
        if (cor[r] == BRANCO) {                                 // @raiz_branca
            crescer(r);                                         // @chama_crescer
        }
    }
}

// A árvore que começa em r cresce até a fila esvaziar (até todos da parte de r entrarem)
void crescer(int r) {
    chave[r] = 0;                                               // @raiz_chave
    cor[r] = CINZA;                                             // @raiz_cinza
    fila[tamanho] = r;                                          // @raiz
    tamanho = tamanho + 1;                                      // @raiz
    while (tamanho > 0) {                                       // @enquanto_fila
        int u = extrair_minimo();                               // @chama_extrair
        cor[u] = PRETO;                                         // @extrair
        for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
            int v = atual->v;                                   // @cada_vizinho
            if (cor[v] == PRETO) {                              // @ignorar_vizinho
                continue;                                       // @pula_vizinho
            }
            if (atual->peso < chave[v]) {                       // @atualizar_nao
                chave[v] = atual->peso;                         // @atualizar_melhorou
                pai[v] = u;                                     // @pai_v
                if (cor[v] == BRANCO) {                         // @se_branco
                    cor[v] = CINZA;                             // @pinta_cinza
                    fila[tamanho] = v;                          // @entra_na_fila
                    tamanho = tamanho + 1;                      // @entra_na_fila
                }
            }
        }
    }
}

// EXTRACT-MIN: o vértice da fila com a menor chave (no empate, o que entrou primeiro)
int extrair_minimo(void) {
    int menor = fila[0];                                        // @menor_primeiro
    int posicao = 0;                                            // @menor_primeiro
    for (int i = 0; i < tamanho; i++) {                         // @cada_da_fila
        if (chave[fila[i]] < chave[menor]) {                    // @compara_chave
            menor = fila[i];                                    // @novo_menor
            posicao = i;                                        // @novo_menor
        }
    }
    // Tira da fila: os que vêm depois dele andam uma posição para a esquerda (a ordem fica igual)
    for (int i = posicao; i < tamanho - 1; i++) {               // @tira_da_fila
        fila[i] = fila[i + 1];                                  // @tira_da_fila
    }
    tamanho = tamanho - 1;                                      // @tira_da_fila
    return menor;                                               // @devolve_menor
}
