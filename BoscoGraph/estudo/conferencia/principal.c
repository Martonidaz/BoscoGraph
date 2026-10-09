// Só para os testes (testes_estudo.py): lê grafos da entrada padrão, roda a busca de estudo pedida
// e escreve o estado final, no formato que o teste compara com o do Python. O formato da entrada
// está em testes_estudo.py (entrada_das_traducoes).
// Compilado uma vez para cada busca (gcc -DPROFUNDIDADE ...): as buscas têm variáveis globais com o
// mesmo nome, como cor e pai, e não cabem juntas num programa só.

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(PROFUNDIDADE)
#include "profundidade.c"
#elif defined(LARGURA)
#include "largura.c"
#elif defined(DIJKSTRA)
#include "dijkstra.c"
#elif defined(BELLMAN_FORD)
#include "bellman_ford.c"
#elif defined(GULOSA)
#include "gulosa.c"
#elif defined(A_ESTRELA)
#include "a_estrela.c"
#elif defined(LIMITADA)
#include "limitada.c"
#elif defined(ITERATIVA)
#include "iterativa.c"
#elif defined(BIDIRECIONAL)
#include "bidirecional.c"
#elif defined(FLOYD_WARSHALL)
#include "floyd_warshall.c"
#elif defined(PRIM)
#include "prim.c"
#elif defined(KRUSKAL)
#include "kruskal.c"
#else
#error "Diga qual busca: -DPROFUNDIDADE, -DLARGURA, -DDIJKSTRA, -DBELLMAN_FORD, -DGULOSA, -DA_ESTRELA, -DLIMITADA, -DITERATIVA, -DBIDIRECIONAL, -DFLOYD_WARSHALL, -DPRIM ou -DKRUSKAL"
#endif

// As buscas com lista de adjacência (o Bellman-Ford e o Floyd-Warshall usam a lista de arcos; o Kruskal, as arestas)
#if !defined(BELLMAN_FORD) && !defined(FLOYD_WARSHALL) && !defined(KRUSKAL)
#define COM_LISTAS
#endif

static char nomes[MAX][64];

static int ler_inteiro(void) {
    int x;
    if (scanf("%d", &x) != 1) {
        exit(2);
    }
    return x;
}

static double ler_numero(void) {
    double x;
    if (scanf("%lf", &x) != 1) {
        exit(2);
    }
    return x;
}

#if !defined(PROFUNDIDADE) && !defined(GULOSA) && !defined(LIMITADA) && !defined(ITERATIVA)
// Os números como o teste espera: "inf" para o infinito e inteiros sem casas decimais
static void escrever_numero(double x) {
    if (isinf(x)) {
        fputs(x > 0 ? "inf" : "-inf", stdout);
    } else if (x == floor(x)) {
        printf("%.0f", x);
    } else {
        printf("%.17g", x);
    }
}
#endif

#if !defined(BELLMAN_FORD) && !defined(FLOYD_WARSHALL) && !defined(KRUSKAL)
static const char *NOMES_DAS_CORES[] = {"Branco", "Cinza", "Preto"};
#endif

#if defined(LIMITADA) || defined(ITERATIVA)
static const char *NOMES_DOS_RESULTADOS[] = {"achou", "corte", "falha"};
#endif

#if defined(BIDIRECIONAL)
static const char *NOMES_DOS_LADOS[] = {"NIL", "frente", "tras"};
#endif

static const char *nome_ou_nil(int v) {
    return v == NIL ? "NIL" : nomes[v];
}

#if defined(COM_LISTAS)
// Lê uma lista de adjacência (k, depois k pares "vizinho peso"), na ordem da entrada: cada nó novo
// entra no FIM da lista. Devolve o primeiro nó (NULL = lista vazia).
static Vizinho *ler_lista(void) {
    Vizinho *primeiro = NULL;
    Vizinho *ultimo = NULL;
    int k = ler_inteiro();
    for (int j = 0; j < k; j++) {
        Vizinho *novo = malloc(sizeof *novo);
        novo->v = ler_inteiro();
#if defined(PROFUNDIDADE) || defined(LIMITADA) || defined(ITERATIVA)
        ler_numero();                   // a DFS, a limitada e a iterativa de estudo não guardam o peso
#else
        novo->peso = ler_numero();
#endif
        novo->proximo = NULL;
        if (ultimo == NULL) {
            primeiro = novo;
        } else {
            ultimo->proximo = novo;
        }
        ultimo = novo;
    }
    return primeiro;
}

// Devolve a memória de uma lista (o sistema devolveria no fim, mas o certo é cada malloc ter um free)
static void liberar_lista(Vizinho *atual) {
    while (atual != NULL) {
        Vizinho *proximo = atual->proximo;
        free(atual);
        atual = proximo;
    }
}
#endif

#if !defined(BIDIRECIONAL)
// Lê uma lista que esta busca não usa, e joga fora
static void pular_lista(void) {
    int k = ler_inteiro();
    for (int j = 0; j < k; j++) {
        ler_inteiro();
        ler_numero();
    }
}
#endif

int main(void) {
    char algoritmo[64];
    while (scanf("%63s", algoritmo) == 1) {
        n = ler_inteiro();
        for (int i = 0; i < n; i++) {
            if (scanf("%63s", nomes[i]) != 1) {
                return 2;
            }
        }
        int orientado = ler_inteiro();
        int origem = ler_inteiro();
        int destino = ler_inteiro();
        double heuristica[MAX];
        for (int i = 0; i < n; i++) {
            heuristica[i] = ler_numero();
        }
        // As listas de adjacência, na ordem da entrada
        for (int u = 0; u < n; u++) {
#if defined(COM_LISTAS)
            adj[u] = ler_lista();
#else
            pular_lista();
#endif
        }
        int quantos_arcos = ler_inteiro();
        for (int j = 0; j < quantos_arcos; j++) {
#if defined(BELLMAN_FORD) || defined(FLOYD_WARSHALL)
            arcos[j].u = ler_inteiro();
            arcos[j].v = ler_inteiro();
            arcos[j].peso = ler_numero();
#else
            ler_inteiro();
            ler_inteiro();
            ler_numero();
#endif
        }
        int ordem[MAX];
        for (int i = 0; i < n; i++) {
            ordem[i] = ler_inteiro();
        }
        int limite = ler_inteiro();                 // -1 = nenhum (só a busca limitada usa)
        // As listas ao contrário (quem CHEGA em cada vértice): só a bidirecional usa
        for (int v = 0; v < n; v++) {
#if defined(BIDIRECIONAL)
            adj_tras[v] = ler_lista();
#else
            pular_lista();
#endif
        }
        // Versão 7.3: as arestas uma vez cada, na ordem de criação (só o Kruskal usa)
        int quantas_arestas = ler_inteiro();
        for (int j = 0; j < quantas_arestas; j++) {
#if defined(KRUSKAL)
            arestas[j].u = ler_inteiro();
            arestas[j].v = ler_inteiro();
            arestas[j].peso = ler_numero();
#else
            ler_inteiro();
            ler_inteiro();
            ler_numero();
#endif
        }

#if defined(PROFUNDIDADE)
        (void) origem;
        (void) destino;
        (void) heuristica;
        (void) limite;
        direcionado = orientado == 1;
        memset(voltas, 0, sizeof voltas);
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                tipo[u][v] = NULL;
            }
        }
        dfs(ordem);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("d %s %d\n", nomes[v], d[v]);
            printf("f %s %d\n", nomes[v], f[v]);
            printf("pai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
        for (int u = 0; u < n; u++) {
            for (int v = 0; v < n; v++) {
                if (tipo[u][v] != NULL) {
                    printf("tipo %s %s %s\n", nomes[u], nomes[v], tipo[u][v]);
                }
            }
        }
#elif defined(LARGURA)
        (void) orientado;
        (void) destino;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        inicio = 0;
        fim = 0;
        bfs(origem);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("d %s ", nomes[v]);
            escrever_numero(d[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
#elif defined(DIJKSTRA)
        (void) orientado;
        (void) destino;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        tamanho = 0;
        dijkstra(origem);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("d %s ", nomes[v]);
            escrever_numero(d[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
#elif defined(BELLMAN_FORD)
        (void) orientado;
        (void) destino;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        m = quantos_arcos;
        bool resposta = bellman_ford(origem);
        for (int v = 0; v < n; v++) {
            printf("d %s ", nomes[v]);
            escrever_numero(d[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
        printf("resposta %s\n", resposta ? "true" : "false");
#elif defined(GULOSA)
        (void) orientado;
        (void) ordem;
        (void) limite;
        for (int v = 0; v < n; v++) {
            h[v] = heuristica[v];
        }
        tamanho = 0;
        bool resposta = buscar(origem, destino);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("pai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
        printf("resposta %s\n", resposta ? "true" : "false");
#elif defined(A_ESTRELA)
        (void) orientado;
        (void) ordem;
        (void) limite;
        for (int v = 0; v < n; v++) {
            h[v] = heuristica[v];
        }
        tamanho = 0;
        bool resposta = buscar(origem, destino);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("g %s ", nomes[v]);
            escrever_numero(g[v]);
            printf("\nf %s ", nomes[v]);
            escrever_numero(f[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
        printf("resposta %s\n", resposta ? "true" : "false");
#elif defined(LIMITADA) || defined(ITERATIVA)
        (void) orientado;
        (void) heuristica;
        (void) ordem;
        // Como o objeto novo do Python: prof vazio (SEM_PROF em todos), caminho e cortados vazios
        for (int v = 0; v < n; v++) {
            prof[v] = SEM_PROF;
        }
        topo = 0;
        quantos_cortados = 0;
#if defined(LIMITADA)
        enum Resultado resposta = buscar(origem, destino, limite);
#else
        (void) limite;
        enum Resultado resposta = buscar(origem, destino);
#endif
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("pai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
            if (prof[v] != SEM_PROF) {
                printf("prof %s %d\n", nomes[v], prof[v]);
            }
        }
        printf("caminho");
        for (int i = 0; i < topo; i++) {
            printf(" %s", nomes[caminho[i]]);
        }
        printf("\ncortados");
        for (int i = 0; i < quantos_cortados; i++) {
            printf(" %s", nomes[cortados[i]]);
        }
        printf("\nresposta %s\n", NOMES_DOS_RESULTADOS[resposta]);
#elif defined(BIDIRECIONAL)
        (void) orientado;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        fila.inicio = 0;
        fila.fim = 0;
        fila_tras.inicio = 0;
        fila_tras.fim = 0;
        encontro.u = NIL;
        encontro.v = NIL;
        bool resposta = buscar(origem, destino);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("lado %s %s\n", nomes[v], NOMES_DOS_LADOS[lado[v]]);
            printf("d %s ", nomes[v]);
            escrever_numero(d[v]);
            printf("\nd_tras %s ", nomes[v]);
            escrever_numero(d_tras[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
            printf("pai_tras %s %s\n", nomes[v], nome_ou_nil(pai_tras[v]));
        }
        if (encontro.u != NIL) {
            printf("encontro %s %s\n", nomes[encontro.u], nomes[encontro.v]);
        }
        printf("resposta %s\n", resposta ? "true" : "false");
#elif defined(PRIM)
        (void) orientado;
        (void) origem;
        (void) destino;
        (void) heuristica;
        (void) limite;
        tamanho = 0;
        prim(ordem);
        for (int v = 0; v < n; v++) {
            printf("cor %s %s\n", nomes[v], NOMES_DAS_CORES[cor[v]]);
            printf("chave %s ", nomes[v]);
            escrever_numero(chave[v]);
            printf("\npai %s %s\n", nomes[v], nome_ou_nil(pai[v]));
        }
#elif defined(KRUSKAL)
        (void) orientado;
        (void) origem;
        (void) destino;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        m = quantas_arestas;
        quantas_na_arvore = 0;
        kruskal();
        for (int v = 0; v < n; v++) {
            printf("conjunto %s %s\n", nomes[v], nome_ou_nil(conjunto[v]));
        }
        for (int i = 0; i < quantas_na_arvore; i++) {
            printf("arvore %d %s %s ", i, nomes[arvore[i].u], nomes[arvore[i].v]);
            escrever_numero(arvore[i].peso);
            printf("\n");
        }
#elif defined(FLOYD_WARSHALL)
        (void) orientado;
        (void) origem;
        (void) destino;
        (void) heuristica;
        (void) ordem;
        (void) limite;
        m = quantos_arcos;
        bool resposta = floyd_warshall();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                printf("d %s %s ", nomes[i], nomes[j]);
                escrever_numero(d[i][j]);
                printf("\npi %s %s %s\n", nomes[i], nomes[j], nome_ou_nil(pi[i][j]));
            }
        }
        printf("resposta %s\n", resposta ? "true" : "false");
        // Devolve a memória das linhas que a busca criou com malloc
        for (int i = 0; i < n; i++) {
            free(d[i]);
            free(pi[i]);
            d[i] = NULL;
            pi[i] = NULL;
        }
#endif
        printf("fim\n");

#if defined(COM_LISTAS)
        // Devolve a memória das listas (o sistema devolveria no fim, mas o certo é cada malloc ter um free)
        for (int u = 0; u < n; u++) {
            liberar_lista(adj[u]);
            adj[u] = NULL;
        }
#endif
#if defined(BIDIRECIONAL)
        for (int v = 0; v < n; v++) {
            liberar_lista(adj_tras[v]);
            adj_tras[v] = NULL;
        }
#endif
    }
    return 0;
}
