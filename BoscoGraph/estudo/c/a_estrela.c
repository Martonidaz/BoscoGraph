// Busca A* (A estrela): sai da fronteira o vértice de menor f = g + h.
//   g[v]    -> o custo do melhor caminho conhecido de s até v (como o d do Dijkstra)
//   h[v]    -> a estimativa de quanto falta de v até o destino
//   f[v]    -> g[v] + h[v]: a estimativa do custo total de um caminho que passa por v
// Com h admissível (nunca maior que o custo real), o A* acha o caminho de menor custo.
// Se h não for consistente, um vértice já expandido pode ganhar um caminho mais barato:
// aí ele é REABERTO (volta para a fronteira). Devolve true se chegou ao destino.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e g[v], f[v]... são vetores.

#include <math.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define INFINITO INFINITY               // o infinito do ponto flutuante (de math.h)

enum Cor { BRANCO, CINZA, PRETO };

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    double peso;                        // o peso da aresta u -> v
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u
double h[MAX];

enum Cor cor[MAX];
double g[MAX];
double f[MAX];
int pai[MAX];
int fila[MAX];                          // a fronteira: fila[0] até fila[tamanho - 1]
int tamanho = 0;

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
int extrair_minimo(void);
void relaxar(int u, int v, double peso);

bool buscar(int s, int destino) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        g[v] = INFINITO;                                        // @g_infinito
        f[v] = INFINITO;                                        // @f_infinito
        pai[v] = NIL;                                           // @inicializar
    }
    g[s] = 0;                                                   // @origem_g
    f[s] = h[s];                                                // @origem_f
    cor[s] = CINZA;                                             // @origem_cinza
    fila[tamanho] = s;                                          // @origem
    tamanho = tamanho + 1;                                      // @origem
    while (tamanho > 0) {                                       // @enquanto_fila
        int u = extrair_minimo();                               // @chama_extrair
        cor[u] = PRETO;                                         // @extrair
        if (u == destino) {                                     // @se_destino
            return true;                                        // @chegou
        }
        for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
            relaxar(u, atual->v, atual->peso);                  // @chama_relaxar
        }
    }
    return false;                                               // @nao_chegou
}

// O vértice da fronteira com o menor f (no empate, o que entrou primeiro)
int extrair_minimo(void) {
    int menor = fila[0];                                        // @menor_primeiro
    int posicao = 0;                                            // @menor_primeiro
    for (int i = 0; i < tamanho; i++) {                         // @cada_da_fila
        if (f[fila[i]] < f[menor]) {                            // @compara_f
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

// Como o RELAX do Dijkstra, mas a prioridade do vizinho passa a ser f = g + h
void relaxar(int u, int v, double peso) {
    double novo = g[u] + peso;                                  // @soma
    if (novo < g[v]) {                                          // @relaxar_nao
        g[v] = novo;                                            // @novo_g
        f[v] = novo + h[v];                                     // @relaxar_melhorou
        pai[v] = u;                                             // @pai_v
        if (cor[v] == BRANCO) {                                 // @se_branco
            cor[v] = CINZA;                                     // @pinta_cinza
            fila[tamanho] = v;                                  // @entra_na_fila
            tamanho = tamanho + 1;                              // @entra_na_fila
        } else if (cor[v] == PRETO) {                           // @se_preto
            cor[v] = CINZA;                                     // @relaxar_reabriu
            fila[tamanho] = v;                                  // @reentra_na_fila
            tamanho = tamanho + 1;                              // @reentra_na_fila
        }
    }
}
