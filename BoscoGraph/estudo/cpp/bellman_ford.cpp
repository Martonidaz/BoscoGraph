// Algoritmo de Bellman-Ford, como BELLMAN-FORD(G, w, s) do livro do Cormen (CLRS).
// Aceita pesos negativos: em cada rodada relaxa TODAS as arestas; |V| − 1 rodadas bastam.
// Se depois disso alguma aresta ainda diminui uma distância, há um ciclo negativo: devolve false.
// Melhoria: se uma rodada não muda nada, as próximas também não mudariam, e a busca para antes.
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos
// std::map é um dicionário (guarda as chaves em ordem).

#include <cstddef>
#include <limits>
#include <map>
#include <string>
#include <vector>

class BellmanFord {
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
    std::map<std::string, double> d;
    std::map<std::string, std::string> pai;

    BellmanFord(const std::vector<std::string> &vertices, const std::vector<Arco> &arcos)
        : vertices(vertices), arcos(arcos) {}

    bool bellman_ford(const std::string &s) {
        for (const std::string &v : vertices) {                 // @cada_vertice
            d[v] = INFINITO;                                    // @d_infinito
            pai[v] = NIL;                                       // @inicializar
        }
        d[s] = 0;                                               // @origem
        bool parou_antes = false;                               // @parou_falso
        for (std::size_t rodada = 1; rodada < vertices.size(); rodada++) {     // @rodada
            bool mudou = false;                                 // @mudou_falso
            for (const Arco &arco : arcos) {                    // @cada_arco
                if (d[arco.u] + arco.peso < d[arco.v]) {        // @relaxar_nao
                    d[arco.v] = d[arco.u] + arco.peso;          // @relaxar_melhorou
                    pai[arco.v] = arco.u;                       // @pai_v
                    mudou = true;                               // @mudou
                }
            }
            if (!mudou) {                                       // @se_nao_mudou
                parou_antes = true;                             // @rodada_sem_mudanca
                break;                                          // @para
            }
        }
        if (!parou_antes) {                                     // @se_nao_parou
            for (const Arco &arco : arcos) {                    // @verificar_ciclo
                if (d[arco.u] + arco.peso < d[arco.v]) {        // @ainda_diminui
                    return false;                               // @ciclo_negativo
                }
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
};
