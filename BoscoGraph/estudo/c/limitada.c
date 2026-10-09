// Busca em profundidade limitada (DLS), como RECURSIVE-DLS do livro do Russell e Norvig, sem repetir
// vértices do caminho atual (senão a busca andaria em círculo).
// C não tem dicionário pronto: os vértices são NÚMEROS, de 0 a n - 1, e cor[v], prof[v]... são vetores
// comuns (a posição v guarda o valor do vértice v). O nome de cada vértice fica fora daqui.
//   cor[v]   -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
//   prof[v]  -> a profundidade com que v entrou no caminho (a última vez); SEM_PROF = nunca entrou
//   pai[v]   -> de onde v entrou no caminho (a última vez; NIL = nenhum)
//   caminho  -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão.
//               Vai de caminho[0] (a origem) até caminho[topo - 1]. Empilhar põe o vértice em
//               caminho[topo] e sobe o topo; desempilhar só desce o topo (o que fica acima não conta).
//               O caminho nunca repete vértice, então MAX posições bastam.
//   cortados -> onde o limite cortou (um vértice pode ser cortado mais de uma vez):
//               cortados[0] até cortados[quantos_cortados - 1]
// Devolve ACHOU (o caminho até o destino fica em "caminho"), CORTE (o limite cortou algum ramo)
// ou FALHA (não achou, e nenhum limite maior ajudaria). Sem destino, passe destino = NIL.
// Antes da busca, quem a chama deixa prof[v] = SEM_PROF para todo v (no Python, o dicionário prof
// começa vazio); topo e quantos_cortados já começam em 0.

#include <stdbool.h>
#include <stddef.h>

#define MAX 100                         // o maior número de vértices
#define MAX_CORTADOS 10000              // o maior número de cortes anotados
#define NIL (-1)                        // "nenhum vértice" (o NIL do livro)
#define SEM_PROF (-1)                   // "sem profundidade": o vértice ainda não entrou no caminho

enum Cor { BRANCO, CINZA, PRETO };
enum Resultado { ACHOU, CORTE, FALHA };

// Um nó da lista de adjacência (uma lista ENCADEADA: cada nó aponta o próximo)
typedef struct Vizinho {
    int v;                              // o número do vizinho
    struct Vizinho *proximo;            // o próximo nó da lista (NULL = a lista acabou)
} Vizinho;

int n;                                  // quantos vértices o grafo tem
Vizinho *adj[MAX];                      // adj[u] = o primeiro nó da lista de u

enum Cor cor[MAX];
int prof[MAX];
int pai[MAX];
int caminho[MAX];                       // a pilha: caminho[0] até caminho[topo - 1]
int topo = 0;                           // quantos vértices estão no caminho
int cortados[MAX_CORTADOS];
int quantos_cortados = 0;

// O C lê o arquivo de cima para baixo: as funções usadas antes de aparecer são anunciadas aqui
enum Resultado dls(int u, int destino, int limite, int profundidade);
bool esta_no_caminho(int v);

enum Resultado buscar(int s, int destino, int limite) {
    for (int v = 0; v < n; v++) {                               // @cada_vertice
        cor[v] = BRANCO;                                        // @pinta_branco
        pai[v] = NIL;                                           // @inicializar
    }
    return dls(s, destino, limite, 0);                          // @chama_dls
}

// Desce no máximo "limite" arestas a partir de u (profundidade = a profundidade de u)
enum Resultado dls(int u, int destino, int limite, int profundidade) {
    cor[u] = CINZA;                                             // @entrar
    prof[u] = profundidade;                                     // @anota_prof
    caminho[topo] = u;                                          // @empilha
    topo = topo + 1;                                            // @empilha
    if (u == destino) {                                         // @testa_destino
        return ACHOU;                                           // @chegou
    }
    if (limite == 0) {                                          // @testa_limite
        topo = topo - 1;                                        // @desempilha_cortado
        cor[u] = PRETO;                                         // @pinta_cortado
        cortados[quantos_cortados] = u;                         // @corte
        quantos_cortados = quantos_cortados + 1;                // @corte
        return CORTE;                                           // @devolve_corte
    }
    bool houve_corte = false;                                   // @sem_corte
    for (Vizinho *atual = adj[u]; atual != NULL; atual = atual->proximo) {     // @cada_vizinho
        int v = atual->v;                                       // @cada_vizinho
        if (esta_no_caminho(v)) {                               // @ignorar_vizinho
            continue;                                           // @pula_vizinho
        }
        pai[v] = u;                                             // @pai_v
        enum Resultado resultado = dls(v, destino, limite - 1, profundidade + 1);     // @desce
        if (resultado == ACHOU) {                               // @se_achou
            return ACHOU;                                       // @repassa_achou
        }
        if (resultado == CORTE) {                               // @se_cortou
            houve_corte = true;                                 // @houve_corte
        }
    }
    topo = topo - 1;                                            // @desempilha
    cor[u] = PRETO;                                             // @subir
    if (houve_corte) {                                          // @se_houve_corte
        return CORTE;                                           // @devolve_corte_de_baixo
    }
    return FALHA;                                               // @devolve_falha
}

// "v está no caminho?": procura v na pilha, de caminho[0] até o topo (é o que o "in" do Python faz
// numa lista: olha um por um)
bool esta_no_caminho(int v) {
    for (int i = 0; i < topo; i++) {                            // @ignorar_vizinho
        if (caminho[i] == v) {                                  // @ignorar_vizinho
            return true;                                        // @ignorar_vizinho
        }
    }
    return false;                                               // @ignorar_vizinho
}
