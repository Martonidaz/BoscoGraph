// Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25):
// o menor custo entre TODOS os pares de vértices, numa matriz.
//   d[i][j]  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
//   pi[i][j] -> o vértice que vem antes de j no melhor caminho de i até j (o π do livro; NIL = nenhum)
// Na rodada de cada vértice k, cada par (i, j) pergunta: passar por k fica mais barato?
// Os pares em que d[i][k] ou d[k][j] é infinito são pulados: passar por k é impossível.
// Aceita pesos negativos. Devolve true, ou false se algum d[i][i] ficar negativo (ciclo negativo).
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos.
//            Entre arestas paralelas, a matriz fica com a mais barata.
// Cada matriz é um std::map de std::map (um dicionário de linhas): d[i] é a linha i e d[i][j], a
// coluna j dela. d[i] = {} cria a linha i vazia, como o {} do Python.
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// números decimais exatos.

#include <limits>
#include <map>
#include <string>
#include <vector>

class FloydWarshall {
public:
    struct Arco {
        std::string u;                                      // o arco sai de u...
        std::string v;                                      // ...e chega em v
        double peso;
    };
    static constexpr double INFINITO = std::numeric_limits<double>::infinity();
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::vector<std::string> vertices;                      // os nomes dos vértices
    std::vector<Arco> arcos;
    std::map<std::string, std::map<std::string, double>> d;
    std::map<std::string, std::map<std::string, std::string>> pi;

    FloydWarshall(const std::vector<std::string> &vertices, const std::vector<Arco> &arcos)
        : vertices(vertices), arcos(arcos) {}

    bool floyd_warshall() {
        for (const std::string &i : vertices) {                 // @cada_linha
            d[i] = {};                                          // @nova_linha_d
            pi[i] = {};                                         // @nova_linha_pi
            for (const std::string &j : vertices) {             // @cada_coluna
                d[i][j] = INFINITO;                             // @d_infinito
                pi[i][j] = NIL;                                 // @pi_nulo
            }
            d[i][i] = 0;                                        // @inicializar_linha
        }
        for (const Arco &arco : arcos) {                        // @cada_arco
            if (arco.peso < d[arco.u][arco.v]) {                // @arco_nao
                d[arco.u][arco.v] = arco.peso;                  // @arco_melhorou
                pi[arco.u][arco.v] = arco.u;                    // @pi_do_arco
            }
        }
        for (const std::string &k : vertices) {                 // @rodada_k
            for (const std::string &i : vertices) {             // @cada_i
                for (const std::string &j : vertices) {         // @cada_j
                    if (d[i][k] == INFINITO || d[k][j] == INFINITO) {     // @passa_por_k
                        continue;                               // @pula_par
                    }
                    if (d[i][k] + d[k][j] < d[i][j]) {          // @par_nao
                        d[i][j] = d[i][k] + d[k][j];            // @par_melhorou
                        pi[i][j] = pi[k][j];                    // @pi_par
                    }
                }
            }
        }
        for (const std::string &i : vertices) {                 // @verifica_diagonal
            if (d[i][i] < 0) {                                  // @testa_diagonal
                return false;                                   // @diagonal_negativa
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
};
