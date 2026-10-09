// Algoritmo de Dijkstra, como DIJKSTRA(G, w, s) do livro do Cormen (CLRS), na versão em que a fila
// de prioridade só guarda os vértices já alcançados ("busca de custo uniforme").
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e d[v], pai[v]... são vetores.
//   d[v]    -> o menor custo conhecido de s até v (INFINITO = ainda não alcançado)
//   pai[v]  -> o vértice anterior no melhor caminho conhecido (NIL = nenhum)
//   cor[v]  -> BRANCO (não alcançado), CINZA (na fila) ou PRETO (d definitivo)
//   fila    -> fila[0] até fila[tamanho - 1], na ordem em que entraram
// extrair_minimo percorre a fila toda: O(V). Com um heap seria O(log V).
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
    double peso;                        // o peso da aresta u -> v
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u

enum Cor cor[MAX];
double d[MAX];
int pai[MAX];
int fila[MAX];
int tamanho = 0;                        // quantos vértices estão na fila

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
int extrair_minimo(void);
void relaxar(int u, int v, double peso);

void dijkstra(int s) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        d[v] = INFINITO;                                        // @d_infinito
        pai[v] = NIL;                                           // @inicializar
    }
    d[s] = 0;                                                   // @origem_d
    cor[s] = CINZA;                                             // @origem_cinza
    fila[tamanho] = s;                                          // @origem
    tamanho = tamanho + 1;                                      // @origem
    while (tamanho > 0) {                                       // @enquanto_fila
        int u = extrair_minimo();                               // @chama_extrair
        cor[u] = PRETO;                                         // @extrair
        for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
            relaxar(u, atual->v, atual->peso);                  // @chama_relaxar
        }
    }
}

// EXTRACT-MIN: o vértice da fila com o menor d (no empate, o que entrou primeiro)
int extrair_minimo(void) {
    int menor = fila[0];                                        // @menor_primeiro
    int posicao = 0;                                            // @menor_primeiro
    for (int i = 0; i < tamanho; i++) {                         // @cada_da_fila
        if (d[fila[i]] < d[menor]) {                            // @compara_d
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

// RELAX(u, v, w): passar por u deixa o caminho até v mais barato?
void relaxar(int u, int v, double peso) {
    double novo = d[u] + peso;                                  // @soma
    if (novo < d[v]) {                                          // @relaxar_nao
        d[v] = novo;                                            // @relaxar_melhorou
        pai[v] = u;                                             // @pai_v
        if (cor[v] == BRANCO) {                                 // @se_branco
            cor[v] = CINZA;                                     // @pinta_cinza
            fila[tamanho] = v;                                  // @entra_na_fila
            tamanho = tamanho + 1;                              // @entra_na_fila
        }
    }
}
