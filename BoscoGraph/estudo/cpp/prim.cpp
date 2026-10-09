// Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do livro do Cormen (CLRS), na mesma
// forma do Dijkstra daqui: a fila de prioridade só guarda os vértices já alcançados.
//   chave -> o peso da aresta mais leve que liga o vértice à árvore;  pai -> a outra ponta (NIL = nenhum)
//   cor   -> BRANCO (fora, sem ligação), CINZA (na fila) ou PRETO (já está na árvore)
// Como no DFS(G), uma árvore nova começa em cada parte desligada: é a floresta geradora mínima.
// A fila é um vector: extrair_minimo percorre todos, O(V). Com std::priority_queue (um heap) seria
// O(log V). Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o
// BoscoGraph usa números decimais exatos.

#include <algorithm>
#include <limits>
#include <map>
#include <string>
#include <vector>

class Prim {
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
    std::map<std::string, double> chave;
    std::map<std::string, std::string> pai;
    std::vector<std::string> fila;

    explicit Prim(const std::map<std::string, std::vector<Vizinho>> &adj) : adj(adj) {}

    void prim(const std::vector<std::string> &raizes) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            chave[v] = INFINITO;                                // @chave_infinito
            pai[v] = NIL;                                       // @inicializar
        }
        for (const std::string &r : raizes) {                   // @cada_raiz
            if (cor[r] == BRANCO) {                             // @raiz_branca
                crescer(r);                                     // @chama_crescer
            }
        }
    }

    // A árvore que começa em r cresce até a fila esvaziar (até todos da parte de r entrarem)
    void crescer(const std::string &r) {
        chave[r] = 0;                                           // @raiz_chave
        cor[r] = CINZA;                                         // @raiz_cinza
        fila.push_back(r);                                      // @raiz
        while (!fila.empty()) {                                 // @enquanto_fila
            std::string u = extrair_minimo();                   // @chama_extrair
            cor[u] = PRETO;                                     // @extrair
            for (const Vizinho &vizinho : adj[u]) {             // @cada_vizinho
                const std::string &v = vizinho.v;               // @cada_vizinho
                if (cor[v] == PRETO) {                          // @ignorar_vizinho
                    continue;                                   // @pula_vizinho
                }
                if (vizinho.peso < chave[v]) {                  // @atualizar_nao
                    chave[v] = vizinho.peso;                    // @atualizar_melhorou
                    pai[v] = u;                                 // @pai_v
                    if (cor[v] == BRANCO) {                     // @se_branco
                        cor[v] = CINZA;                         // @pinta_cinza
                        fila.push_back(v);                      // @entra_na_fila
                    }
                }
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com a menor chave (no empate, o que entrou primeiro)
    std::string extrair_minimo() {
        std::string menor = fila[0];                            // @menor_primeiro
        for (const std::string &v : fila) {                     // @cada_da_fila
            if (chave[v] < chave[menor]) {                      // @compara_chave
                menor = v;                                      // @novo_menor
            }
        }
        fila.erase(std::find(fila.begin(), fila.end(), menor));         // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
};
