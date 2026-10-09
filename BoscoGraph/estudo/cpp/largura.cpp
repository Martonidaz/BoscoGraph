// Busca em largura (BFS), como BFS(G, s) do livro do Cormen (CLRS).
//   cor  -> BRANCO (não descoberto), CINZA (descoberto, na fila) ou PRETO (terminado)
//   d    -> o menor número de arestas de s até cada vértice (INFINITO = não alcançado)
//   pai  -> de qual vértice a busca chegou (NIL = nenhum)
//   fila -> std::deque (fila de duas pontas): entra no fim, sai do começo, as duas em O(1)
// std::map é um dicionário (guarda as chaves em ordem).

#include <deque>
#include <limits>
#include <map>
#include <string>
#include <vector>

class BuscaEmLargura {
public:
    struct Vizinho {
        std::string v;
        double peso;                                        // a BFS não usa o peso
    };
    enum Cor { BRANCO, CINZA, PRETO };
    static constexpr double INFINITO = std::numeric_limits<double>::infinity();
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<Vizinho>> adj;        // adj[u] = os vizinhos de u, com os pesos
    std::map<std::string, Cor> cor;
    std::map<std::string, double> d;
    std::map<std::string, std::string> pai;
    std::deque<std::string> fila;

    explicit BuscaEmLargura(const std::map<std::string, std::vector<Vizinho>> &adj) : adj(adj) {}

    void bfs(const std::string &s) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            d[v] = INFINITO;                                    // @d_infinito
            pai[v] = NIL;                                       // @inicializar
        }
        cor[s] = CINZA;                                         // @origem_cinza
        d[s] = 0;                                               // @origem_d
        fila.push_back(s);                                      // @origem
        while (!fila.empty()) {                                 // @enquanto_fila
            // Copia antes de tirar: front() devolve uma referência, que deixa de valer no pop_front()
            std::string u = fila.front();                       // @desenfileirar
            fila.pop_front();                                   // @desenfileirar
            for (const Vizinho &vizinho : adj[u]) {             // @cada_vizinho
                const std::string &v = vizinho.v;               // @cada_vizinho
                if (cor[v] == BRANCO) {                         // @ignorar_vizinho
                    cor[v] = CINZA;                             // @pinta_cinza
                    d[v] = d[u] + 1;                            // @d_mais_um
                    pai[v] = u;                                 // @pai_v
                    fila.push_back(v);                          // @descobrir_vizinho
                }
            }
            cor[u] = PRETO;                                     // @terminar_vertice
        }
    }
};
