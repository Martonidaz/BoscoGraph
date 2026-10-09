// Algoritmo de Bellman-Ford, como BELLMAN-FORD(G, w, s) do livro do Cormen (CLRS).
// Aceita pesos negativos: em cada rodada relaxa TODAS as arestas; |V| − 1 rodadas bastam.
// Se depois disso alguma aresta ainda diminui uma distância, há um CICLO NEGATIVO alcançável.
// Devolve true (sem ciclo negativo) ou false (com ciclo negativo), como no livro.
// Melhoria: se uma rodada não muda nada, as próximas também não mudariam, e a busca para antes.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e d[v], pai[v] são vetores.
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos

#include <math.h>
#include <stdbool.h>

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

double d[MAX];
int pai[MAX];

bool bellman_ford(int s) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        d[v] = INFINITO;                                        // @d_infinito
        pai[v] = NIL;                                           // @inicializar
    }
    d[s] = 0;                                                   // @origem
    bool parou_antes = false;                                   // @parou_falso
    for (int rodada = 1; rodada < n; rodada++) {                // @rodada
        bool mudou = false;                                     // @mudou_falso
        for (int i = 0; i < m; i++) {                           // @cada_arco
            Arco arco = arcos[i];                               // @cada_arco
            if (d[arco.u] + arco.peso < d[arco.v]) {            // @relaxar_nao
                d[arco.v] = d[arco.u] + arco.peso;              // @relaxar_melhorou
                pai[arco.v] = arco.u;                           // @pai_v
                mudou = true;                                   // @mudou
            }
        }
        if (!mudou) {                                           // @se_nao_mudou
            parou_antes = true;                                 // @rodada_sem_mudanca
            break;                                              // @para
        }
    }
    if (!parou_antes) {                                         // @se_nao_parou
        for (int i = 0; i < m; i++) {                           // @verificar_ciclo
            Arco arco = arcos[i];                               // @verificar_ciclo
            if (d[arco.u] + arco.peso < d[arco.v]) {            // @ainda_diminui
                return false;                                   // @ciclo_negativo
            }
        }
    }
    return true;                                                // @sem_ciclo_negativo
}
