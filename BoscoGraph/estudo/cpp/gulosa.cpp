// Busca gulosa pela melhor escolha (greedy best-first): sai da fronteira o vértice de menor h,
// a ESTIMATIVA de quanto falta até o destino. Rápida, mas não garante o caminho de menor custo.
//   h   -> a heurística;  cor -> BRANCO (não visto), CINZA (na fronteira), PRETO (expandido)
//   pai -> de onde a busca chegou (NIL = nenhum)
// Devolve true se chegou ao destino. std::map é um dicionário (guarda as chaves em ordem).

#include <algorithm>
#include <map>
#include <string>
#include <vector>

class BuscaGulosa {
public:
    struct Vizinho {
        std::string v;
        double peso;                                        // a gulosa não usa o peso
    };
    enum Cor { BRANCO, CINZA, PRETO };
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<Vizinho>> adj;        // adj[u] = os vizinhos de u, com os pesos
    std::map<std::string, double> h;
    std::map<std::string, Cor> cor;
    std::map<std::string, std::string> pai;
    std::vector<std::string> fila;                          // a fronteira

    BuscaGulosa(const std::map<std::string, std::vector<Vizinho>> &adj, const std::map<std::string, double> &h)
        : adj(adj), h(h) {}

    bool buscar(const std::string &s, const std::string &destino) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            pai[v] = NIL;                                       // @inicializar
        }
        cor[s] = CINZA;                                         // @origem_cinza
        fila.push_back(s);                                      // @origem
        while (!fila.empty()) {                                 // @enquanto_fila
            std::string u = extrair_minimo();                   // @chama_extrair
            cor[u] = PRETO;                                     // @extrair
            if (u == destino) {                                 // @se_destino
                return true;                                    // @chegou
            }
            for (const Vizinho &vizinho : adj[u]) {             // @cada_vizinho
                const std::string &v = vizinho.v;               // @cada_vizinho
                if (cor[v] == BRANCO) {                         // @ignorar_vizinho
                    cor[v] = CINZA;                             // @pinta_cinza
                    pai[v] = u;                                 // @pai_v
                    fila.push_back(v);                          // @descobrir_vizinho
                }
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor h (no empate, o que entrou primeiro)
    std::string extrair_minimo() {
        std::string menor = fila[0];                            // @menor_primeiro
        for (const std::string &v : fila) {                     // @cada_da_fila
            if (h[v] < h[menor]) {                              // @compara_h
                menor = v;                                      // @novo_menor
            }
        }
        fila.erase(std::find(fila.begin(), fila.end(), menor));         // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
};
