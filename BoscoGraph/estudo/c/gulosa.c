// Busca gulosa pela melhor escolha (greedy best-first): sai da fronteira sempre o vértice de
// menor h, a ESTIMATIVA de quanto falta até o destino. Não olha quanto já gastou: costuma chegar
// rápido, mas não garante o caminho de menor custo.
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e h[v], cor[v]... são vetores.
//   h[v]    -> a heurística (estimativa até o destino)
//   cor[v]  -> BRANCO (não visto), CINZA (na fronteira) ou PRETO (já expandido)
//   pai[v]  -> de onde a busca chegou em v (NIL = nenhum)
// Devolve true se chegou ao destino.

#include <stdbool.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)

enum Cor { BRANCO, CINZA, PRETO };

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    double peso;                        // o peso da aresta (a gulosa não usa)
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u
double h[MAX];

enum Cor cor[MAX];
int pai[MAX];
int fila[MAX];                          // a fronteira: fila[0] até fila[tamanho - 1]
int tamanho = 0;

// O C lê o arquivo de cima para baixo: a função usada antes de aparecer é anunciada aqui
int extrair_minimo(void);

bool buscar(int s, int destino) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        pai[v] = NIL;                                           // @inicializar
    }
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
            int v = atual->v;                                   // @cada_vizinho
            if (cor[v] == BRANCO) {                             // @ignorar_vizinho
                cor[v] = CINZA;                                 // @pinta_cinza
                pai[v] = u;                                     // @pai_v
                fila[tamanho] = v;                              // @descobrir_vizinho
                tamanho = tamanho + 1;                          // @descobrir_vizinho
            }
        }
    }
    return false;                                               // @nao_chegou
}

// O vértice da fronteira com o menor h (no empate, o que entrou primeiro)
int extrair_minimo(void) {
    int menor = fila[0];                                        // @menor_primeiro
    int posicao = 0;                                            // @menor_primeiro
    for (int i = 0; i < tamanho; i++) {                         // @cada_da_fila
        if (h[fila[i]] < h[menor]) {                            // @compara_h
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
