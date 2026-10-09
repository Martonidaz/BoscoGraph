// Busca A* (A estrela): sai da fronteira o vértice de menor f = g + h.
//   g -> o custo do melhor caminho conhecido;  h -> a estimativa até o destino;  f = g + h
// Com h admissível, acha o caminho de menor custo. Se h não for consistente, um vértice já
// expandido pode ganhar um caminho mais barato: aí ele é REABERTO. Devolve true se chegou.
// std::map é um dicionário (guarda as chaves em ordem).

#include <algorithm>
#include <limits>
#include <map>
#include <string>
#include <vector>

class AEstrela {
public:
    struct Vizinho {
        std::string v;
        double peso;
    };
    enum Cor { BRANCO, CINZA, PRETO };
    static constexpr double INFINITO = std::numeric_limits<double>::infinity();
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<Vizinho>> adj;        // adj[u] = os vizinhos de u, com os pesos
    std::map<std::string, double> h;
    std::map<std::string, Cor> cor;
    std::map<std::string, double> g;
    std::map<std::string, double> f;
    std::map<std::string, std::string> pai;
    std::vector<std::string> fila;                          // a fronteira

    AEstrela(const std::map<std::string, std::vector<Vizinho>> &adj, const std::map<std::string, double> &h)
        : adj(adj), h(h) {}

    bool buscar(const std::string &s, const std::string &destino) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            g[v] = INFINITO;                                    // @g_infinito
            f[v] = INFINITO;                                    // @f_infinito
            pai[v] = NIL;                                       // @inicializar
        }
        g[s] = 0;                                               // @origem_g
        f[s] = h[s];                                            // @origem_f
        cor[s] = CINZA;                                         // @origem_cinza
        fila.push_back(s);                                      // @origem
        while (!fila.empty()) {                                 // @enquanto_fila
            std::string u = extrair_minimo();                   // @chama_extrair
            cor[u] = PRETO;                                     // @extrair
            if (u == destino) {                                 // @se_destino
                return true;                                    // @chegou
            }
            for (const Vizinho &vizinho : adj[u]) {             // @cada_vizinho
                relaxar(u, vizinho.v, vizinho.peso);            // @chama_relaxar
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor f (no empate, o que entrou primeiro)
    std::string extrair_minimo() {
        std::string menor = fila[0];                            // @menor_primeiro
        for (const std::string &v : fila) {                     // @cada_da_fila
            if (f[v] < f[menor]) {                              // @compara_f
                menor = v;                                      // @novo_menor
            }
        }
        fila.erase(std::find(fila.begin(), fila.end(), menor));         // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // Como o RELAX do Dijkstra, mas a prioridade do vizinho passa a ser f = g + h
    void relaxar(const std::string &u, const std::string &v, double peso) {
        double novo = g[u] + peso;                              // @soma
        if (novo < g[v]) {                                      // @relaxar_nao
            g[v] = novo;                                        // @novo_g
            f[v] = novo + h[v];                                 // @relaxar_melhorou
            pai[v] = u;                                         // @pai_v
            if (cor[v] == BRANCO) {                             // @se_branco
                cor[v] = CINZA;                                 // @pinta_cinza
                fila.push_back(v);                              // @entra_na_fila
            } else if (cor[v] == PRETO) {                       // @se_preto
                cor[v] = CINZA;                                 // @relaxar_reabriu
                fila.push_back(v);                              // @reentra_na_fila
            }
        }
    }
};
