// Busca bidirecional: duas buscas em largura, uma a partir da origem s (a "frente") e outra a partir
// do destino t ("trás"). Elas se revezam, cada vez expandindo UMA CAMADA INTEIRA (todos os que estão
// na fila daquele lado), até um lado achar um vértice que o outro já descobriu: o encontro.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e cor[v], d[v]... são vetores
// comuns (a posição v guarda o valor do vértice v). O nome de cada vértice fica fora daqui.
//   cor[v]      -> BRANCO (ninguém descobriu), CINZA (na fila de um dos lados) ou PRETO (expandido)
//   lado[v]     -> FRENTE ou TRAS: qual das buscas descobriu v (SEM_LADO = nenhuma)
//   d[v]        -> arestas de s até v (frente);  d_tras[v] -> arestas de v até t (trás)
//   pai[v]      -> de onde a frente chegou em v;  pai_tras[v] -> o próximo vértice de v até t
//   encontro    -> (u, v): u estava sendo expandido e v já era do outro lado (NIL = ainda não houve)
//   fila, fila_tras -> as filas dos dois lados (veja a struct Fila)
// O lado de trás anda pelas arestas AO CONTRÁRIO: adj_tras[v] = quem chega em v.
// Devolve true (as buscas se encontraram: existe caminho) ou false.

#include <math.h>
#include <stdbool.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define INFINITO INFINITY               // o infinito do ponto flutuante (de math.h)

enum Cor { BRANCO, CINZA, PRETO };
enum Lado { SEM_LADO, FRENTE, TRAS };   // SEM_LADO = nenhuma das buscas descobriu o vértice

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    double peso;                        // o peso da aresta (a busca não usa)
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

// Uma fila: itens[inicio] até itens[fim - 1]. Entra no fim, sai do início, as duas pontas em O(1).
// Cada vértice entra uma vez só (numa das duas filas), então MAX posições bastam.
typedef struct Fila {
    int itens[MAX];
    int inicio;
    int fim;
} Fila;

// Onde as duas buscas se tocaram: u estava sendo expandido e v, vizinho dele, já era do outro lado
typedef struct Encontro {
    int u;
    int v;
} Encontro;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = quem sai de u (o primeiro nó da lista)
Vizinho *adj_tras[MAX];                 // adj_tras[v] = quem chega em v (o primeiro nó da lista)

enum Cor cor[MAX];
enum Lado lado[MAX];
double d[MAX];
double d_tras[MAX];
int pai[MAX];
int pai_tras[MAX];
Fila fila;                              // variável global começa zerada: inicio = fim = 0 (vazia)
Fila fila_tras;
Encontro encontro = {NIL, NIL};

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
bool expandir(enum Lado este_lado);
bool expandir_camada(enum Lado este_lado, Fila *fila_do_lado, Vizinho *adj_do_lado[],
                     double d_do_lado[], int pai_do_lado[], enum Lado outro);

bool buscar(int s, int t) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        lado[v] = SEM_LADO;                                     // @sem_lado
        d[v] = INFINITO;                                        // @d_infinito
        d_tras[v] = INFINITO;                                   // @d_tras_infinito
        pai[v] = NIL;                                           // @pai_nulo
        pai_tras[v] = NIL;                                      // @inicializar
    }
    cor[s] = CINZA;                                             // @origem_cinza
    lado[s] = FRENTE;                                           // @origem_lado
    d[s] = 0;                                                   // @origem_d
    fila.itens[fila.fim] = s;                                   // @origem
    fila.fim = fila.fim + 1;                                    // @origem
    if (s == t) {                                               // @mesmo_vertice
        encontro.u = s;                                         // @encontro_na_origem
        encontro.v = s;                                         // @encontro_na_origem
        return true;                                            // @devolve_na_origem
    }
    cor[t] = CINZA;                                             // @destino_cinza
    lado[t] = TRAS;                                             // @destino_lado
    d_tras[t] = 0;                                              // @destino_d
    fila_tras.itens[fila_tras.fim] = t;                         // @origem_tras
    fila_tras.fim = fila_tras.fim + 1;                          // @origem_tras
    // Uma fila está vazia quando inicio == fim
    while (fila.inicio < fila.fim && fila_tras.inicio < fila_tras.fim) {     // @enquanto_filas
        if (expandir(FRENTE)) {                                 // @expande_frente
            return true;                                        // @achou_pela_frente
        }
        if (expandir(TRAS)) {                                   // @expande_tras
            return true;                                        // @achou_por_tras
        }
    }
    return false;                                               // @sem_encontro
}

// Expande uma camada inteira de um lado; devolve true se encontrou o outro lado.
// O Python dá apelidos (fila, adj, d, pai, outro) às coisas do lado que anda. Em C, expandir escolhe
// o lado e passa as coisas dele para expandir_camada, que faz o resto. Um vetor passado para uma
// função não é copiado: ela recebe o endereço e mexe no vetor original. A fila vai pelo endereço
// (&fila) pelo mesmo motivo: expandir_camada tira e põe vértices na fila de verdade.
bool expandir(enum Lado este_lado) {
    if (este_lado == FRENTE) {                                  // @qual_lado
        return expandir_camada(FRENTE, &fila, adj, d, pai, TRAS);       // @usa_frente
    } else {
        return expandir_camada(TRAS, &fila_tras, adj_tras, d_tras, pai_tras, FRENTE);     // @usa_tras
    }
}

// O resto de expandir: fila_do_lado, adj_do_lado, d_do_lado e pai_do_lado são os do lado que anda, e
// outro é o lado contrário. fila_do_lado aponta para uma Fila: fila_do_lado->fim é o campo fim dela.
bool expandir_camada(enum Lado este_lado, Fila *fila_do_lado, Vizinho *adj_do_lado[],
                     double d_do_lado[], int pai_do_lado[], enum Lado outro) {
    int tamanho = fila_do_lado->fim - fila_do_lado->inicio;     // @nova_camada
    for (int vez = 0; vez < tamanho; vez++) {                   // @cada_da_camada
        int u = fila_do_lado->itens[fila_do_lado->inicio];      // @desenfileirar
        fila_do_lado->inicio = fila_do_lado->inicio + 1;        // @desenfileirar
        for (Vizinho *atual = adj_do_lado[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
            int v = atual->v;                                   // @cada_vizinho
            if (lado[v] == outro) {                             // @se_do_outro_lado
                encontro.u = u;                                 // @encontro
                encontro.v = v;                                 // @encontro
                return true;                                    // @devolve_encontro
            }
            if (cor[v] == BRANCO) {                             // @ignorar_vizinho
                cor[v] = CINZA;                                 // @pinta_cinza
                lado[v] = este_lado;                            // @anota_lado
                d_do_lado[v] = d_do_lado[u] + 1;                // @d_mais_um
                pai_do_lado[v] = u;                             // @pai_v
                fila_do_lado->itens[fila_do_lado->fim] = v;     // @descobrir_vizinho
                fila_do_lado->fim = fila_do_lado->fim + 1;      // @descobrir_vizinho
            }
        }
        cor[u] = PRETO;                                         // @terminar_vertice
    }
    return false;                                               // @camada_sem_encontro
}
