// Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25):
// o menor custo entre TODOS os pares de vértices, numa matriz.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e d[i][j], pi[i][j] são matrizes
// (a linha i, coluna j guarda o valor do par i -> j).
//   d[i][j]  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
//   pi[i][j] -> o vértice que vem antes de j no melhor caminho de i até j (o π do livro; NIL = nenhum)
// Na rodada de cada vértice k, cada par (i, j) pergunta: passar por k fica mais barato?
// Os pares em que d[i][k] ou d[k][j] é infinito são pulados: passar por k é impossível.
// Aceita pesos negativos. Devolve true, ou false se algum d[i][i] ficar negativo (ciclo negativo).
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos.
//            Entre arestas paralelas, a matriz fica com a mais barata.
// Cada linha das matrizes é criada com malloc, como o Python cria um dicionário para cada linha:
// d[i] guarda o endereço da linha i, e d[i][j] é a posição j dessa linha. Quem chamou a busca
// devolve a memória com free(d[i]) e free(pi[i]) quando não precisar mais das matrizes.
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// números decimais exatos.

#include <math.h>
#include <stdbool.h>
#include <stdlib.h>

#define MAX 100                         // o maior número de vértices
#define MAX_ARCOS 1000                  // o maior número de arcos
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define INFINITO INFINITY               // o infinito do ponto flutuante (de math.h)

typedef struct Arco {
    int u;                              // o arco sai de u...
    int v;                              // ...e chega em v
    double peso;
} Arco;

int n;                                  // quantos vértices o grafo tem
Arco arcos[MAX_ARCOS];
int m;                                  // quantos arcos

double *d[MAX];                         // d[i] = o endereço da linha i da matriz d
int *pi[MAX];                           // pi[i] = o endereço da linha i da matriz pi

bool floyd_warshall(void) {
    for (int i = 0; i < n; i++) {                               // @cada_linha
        d[i] = malloc(n * sizeof(double));                      // @nova_linha_d
        pi[i] = malloc(n * sizeof(int));                        // @nova_linha_pi
        for (int j = 0; j < n; j++) {                           // @cada_coluna
            d[i][j] = INFINITO;                                 // @d_infinito
            pi[i][j] = NIL;                                     // @pi_nulo
        }
        d[i][i] = 0;                                            // @inicializar_linha
    }
    for (int a = 0; a < m; a++) {                               // @cada_arco
        Arco arco = arcos[a];                                   // @cada_arco
        if (arco.peso < d[arco.u][arco.v]) {                    // @arco_nao
            d[arco.u][arco.v] = arco.peso;                      // @arco_melhorou
            pi[arco.u][arco.v] = arco.u;                        // @pi_do_arco
        }
    }
    for (int k = 0; k < n; k++) {                               // @rodada_k
        for (int i = 0; i < n; i++) {                           // @cada_i
            for (int j = 0; j < n; j++) {                       // @cada_j
                if (d[i][k] == INFINITO || d[k][j] == INFINITO) {       // @passa_por_k
                    continue;                                   // @pula_par
                }
                if (d[i][k] + d[k][j] < d[i][j]) {              // @par_nao
                    d[i][j] = d[i][k] + d[k][j];                // @par_melhorou
                    pi[i][j] = pi[k][j];                        // @pi_par
                }
            }
        }
    }
    for (int i = 0; i < n; i++) {                               // @verifica_diagonal
        if (d[i][i] < 0) {                                      // @testa_diagonal
            return false;                                       // @diagonal_negativa
        }
    }
    return true;                                                // @sem_ciclo_negativo
}
