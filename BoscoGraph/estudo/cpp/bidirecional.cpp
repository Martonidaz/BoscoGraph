// Busca bidirecional: duas buscas em largura, uma a partir da origem s (a "frente") e outra a partir
// do destino t ("trás"). Elas se revezam, cada vez expandindo UMA CAMADA INTEIRA (todos os que estão
// na fila daquele lado), até um lado achar um vértice que o outro já descobriu: o encontro.
//   cor             -> BRANCO (ninguém descobriu), CINZA (na fila de um dos lados) ou PRETO (expandido)
//   lado            -> FRENTE ou TRAS: qual das buscas descobriu o vértice (SEM_LADO = nenhuma)
//   d, d_tras       -> arestas de s até v (frente);  arestas de v até t (trás)
//   pai, pai_tras   -> de onde a frente chegou em v;  o próximo vértice de v até t (NIL = nenhum)
//   encontro        -> (u, v): u estava sendo expandido e v já era do outro lado ((NIL, NIL) = nenhum)
//   fila, fila_tras -> std::deque (fila de duas pontas): entra no fim, sai do começo, as duas em O(1)
// O lado de trás anda pelas arestas AO CONTRÁRIO: adj_tras[v] = quem chega em v.
// Devolve true (as buscas se encontraram: existe caminho) ou false.
// std::map é um dicionário (guarda as chaves em ordem); std::pair é um par (u, v).

#include <cstddef>
#include <deque>
#include <limits>
#include <map>
#include <string>
#include <utility>
#include <vector>

class BuscaBidirecional {
public:
    struct Vizinho {
        std::string v;
        double peso;                                        // a busca não usa o peso
    };
    enum Cor { BRANCO, CINZA, PRETO };
    enum Lado { SEM_LADO, FRENTE, TRAS };
    static constexpr double INFINITO = std::numeric_limits<double>::infinity();
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<Vizinho>> adj;        // adj[u] = quem sai de u, com os pesos
    std::map<std::string, std::vector<Vizinho>> adj_tras;   // adj_tras[v] = quem chega em v, com os pesos
    std::map<std::string, Cor> cor;
    std::map<std::string, Lado> lado;
    std::map<std::string, double> d;
    std::map<std::string, double> d_tras;
    std::map<std::string, std::string> pai;
    std::map<std::string, std::string> pai_tras;
    std::deque<std::string> fila;
    std::deque<std::string> fila_tras;
    std::pair<std::string, std::string> encontro = {NIL, NIL};

    BuscaBidirecional(const std::map<std::string, std::vector<Vizinho>> &adj,
                      const std::map<std::string, std::vector<Vizinho>> &adj_tras)
        : adj(adj), adj_tras(adj_tras) {}

    bool buscar(const std::string &s, const std::string &t) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            lado[v] = SEM_LADO;                                 // @sem_lado
            d[v] = INFINITO;                                    // @d_infinito
            d_tras[v] = INFINITO;                               // @d_tras_infinito
            pai[v] = NIL;                                       // @pai_nulo
            pai_tras[v] = NIL;                                  // @inicializar
        }
        cor[s] = CINZA;                                         // @origem_cinza
        lado[s] = FRENTE;                                       // @origem_lado
        d[s] = 0;                                               // @origem_d
        fila.push_back(s);                                      // @origem
        if (s == t) {                                           // @mesmo_vertice
            encontro = {s, s};                                  // @encontro_na_origem
            return true;                                        // @devolve_na_origem
        }
        cor[t] = CINZA;                                         // @destino_cinza
        lado[t] = TRAS;                                         // @destino_lado
        d_tras[t] = 0;                                          // @destino_d
        fila_tras.push_back(t);                                 // @origem_tras
        while (!fila.empty() && !fila_tras.empty()) {           // @enquanto_filas
            if (expandir(FRENTE)) {                             // @expande_frente
                return true;                                    // @achou_pela_frente
            }
            if (expandir(TRAS)) {                               // @expande_tras
                return true;                                    // @achou_por_tras
            }
        }
        return false;                                           // @sem_encontro
    }

    // Expande uma camada inteira de um lado; devolve true se encontrou o outro lado.
    // O Python dá apelidos (fila, adj, d, pai, outro) às coisas do lado que anda. Em C++, expandir
    // escolhe o lado e passa as coisas dele para expandir_camada, que faz o resto. Os parâmetros com
    // & são REFERÊNCIAS: outro nome para o mesmo objeto (nada é copiado; mexer neles mexe no original).
    bool expandir(Lado este_lado) {
        if (este_lado == FRENTE) {                              // @qual_lado
            return expandir_camada(FRENTE, fila, adj, d, pai, TRAS);     // @usa_frente
        } else {
            return expandir_camada(TRAS, fila_tras, adj_tras, d_tras, pai_tras, FRENTE);     // @usa_tras
        }
    }

    // O resto de expandir: fila_do_lado, adj_do_lado, d_do_lado e pai_do_lado são os do lado que
    // anda, e outro é o lado contrário
    bool expandir_camada(Lado este_lado, std::deque<std::string> &fila_do_lado,
                         std::map<std::string, std::vector<Vizinho>> &adj_do_lado,
                         std::map<std::string, double> &d_do_lado,
                         std::map<std::string, std::string> &pai_do_lado, Lado outro) {
        std::size_t tamanho = fila_do_lado.size();              // @nova_camada
        for (std::size_t vez = 0; vez < tamanho; vez++) {       // @cada_da_camada
            // Copia antes de tirar: front() devolve uma referência, que deixa de valer no pop_front()
            std::string u = fila_do_lado.front();               // @desenfileirar
            fila_do_lado.pop_front();                           // @desenfileirar
            for (const Vizinho &vizinho : adj_do_lado[u]) {     // @cada_vizinho
                const std::string &v = vizinho.v;               // @cada_vizinho
                if (lado[v] == outro) {                         // @se_do_outro_lado
                    encontro = {u, v};                          // @encontro
                    return true;                                // @devolve_encontro
                }
                if (cor[v] == BRANCO) {                         // @ignorar_vizinho
                    cor[v] = CINZA;                             // @pinta_cinza
                    lado[v] = este_lado;                        // @anota_lado
                    d_do_lado[v] = d_do_lado[u] + 1;            // @d_mais_um
                    pai_do_lado[v] = u;                         // @pai_v
                    fila_do_lado.push_back(v);                  // @descobrir_vizinho
                }
            }
            cor[u] = PRETO;                                     // @terminar_vertice
        }
        return false;                                           // @camada_sem_encontro
    }
};
