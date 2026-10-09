// Algoritmo de Dijkstra, como DIJKSTRA(G, w, s) do livro do Cormen (CLRS), na versão em que a fila
// de prioridade só guarda os vértices já alcançados ("busca de custo uniforme").
//   d   -> o menor custo conhecido;  pai -> o vértice anterior no melhor caminho (NIL = nenhum)
//   cor -> BRANCO (não alcançado), CINZA (na fila) ou PRETO (d definitivo)
// A fila é um vector: extrair_minimo percorre todos, O(V). Com std::priority_queue (um heap) seria
// O(log V). Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o
// BoscoGraph usa números decimais exatos.

#include <algorithm>
#include <limits>
#include <map>
#include <string>
#include <vector>

class Dijkstra {
public:
    struct Vizinho {
        std::string v;
        double peso;
    };
    enum Cor { BRANCO, CINZA, PRETO };
    static constexpr double INFINITO = std::numeric_limits<double>::infinity();
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<Vizinho>> adj;        // adj[u] = os vizinhos de u, com os pesos
    std::map<std::string, Cor> cor;
    std::map<std::string, double> d;
    std::map<std::string, std::string> pai;
    std::vector<std::string> fila;

    explicit Dijkstra(const std::map<std::string, std::vector<Vizinho>> &adj) : adj(adj) {}

    void dijkstra(const std::string &s) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            d[v] = INFINITO;                                    // @d_infinito
            pai[v] = NIL;                                       // @inicializar
        }
        d[s] = 0;                                               // @origem_d
        cor[s] = CINZA;                                         // @origem_cinza
        fila.push_back(s);                                      // @origem
        while (!fila.empty()) {                                 // @enquanto_fila
            std::string u = extrair_minimo();                   // @chama_extrair
            cor[u] = PRETO;                                     // @extrair
            for (const Vizinho &vizinho : adj[u]) {             // @cada_vizinho
                relaxar(u, vizinho.v, vizinho.peso);            // @chama_relaxar
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com o menor d (no empate, o que entrou primeiro)
    std::string extrair_minimo() {
        std::string menor = fila[0];                            // @menor_primeiro
        for (const std::string &v : fila) {                     // @cada_da_fila
            if (d[v] < d[menor]) {                              // @compara_d
                menor = v;                                      // @novo_menor
            }
        }
        fila.erase(std::find(fila.begin(), fila.end(), menor));         // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // RELAX(u, v, w): passar por u deixa o caminho até v mais barato?
    void relaxar(const std::string &u, const std::string &v, double peso) {
        double novo = d[u] + peso;                              // @soma
        if (novo < d[v]) {                                      // @relaxar_nao
            d[v] = novo;                                        // @relaxar_melhorou
            pai[v] = u;                                         // @pai_v
            if (cor[v] == BRANCO) {                             // @se_branco
                cor[v] = CINZA;                                 // @pinta_cinza
                fila.push_back(v);                              // @entra_na_fila
            }
        }
    }
};
