// Busca em profundidade (DFS), como DFS(G) e DFS-VISIT(G, u) do livro do Cormen (CLRS).
//   cor  -> BRANCO (não descoberto), CINZA (em exploração) ou PRETO (terminado)
//   d, f -> os tempos de descoberta e de término;  pai -> de onde a busca chegou (NIL = nenhum)
//   tipo -> o tipo de cada aresta examinada (u, v): árvore, retorno, avanço ou cruzamento
// No grafo não orientado, "voltas" anota a outra metade de cada aresta já examinada.
// std::map é um dicionário (guarda as chaves em ordem); um std::pair (u, v) serve de chave de um par.
// Atenção: mapa[chave] CRIA a chave (com valor 0, "" ...) quando ela ainda não existe.

#include <map>
#include <string>
#include <utility>
#include <vector>

class BuscaEmProfundidade {
public:
    enum Cor { BRANCO, CINZA, PRETO };
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<std::string>> adj;    // adj[u] = os vizinhos de u
    bool direcionado;
    std::map<std::string, Cor> cor;
    std::map<std::string, int> d;
    std::map<std::string, int> f;
    std::map<std::string, std::string> pai;
    int tempo = 0;
    std::map<std::pair<std::string, std::string>, int> voltas;
    std::map<std::pair<std::string, std::string>, std::string> tipo;

    BuscaEmProfundidade(const std::map<std::string, std::vector<std::string>> &adj, bool direcionado)
        : adj(adj), direcionado(direcionado) {}

    void dfs(const std::vector<std::string> &ordem) {
        for (const auto &[u, vizinhos] : adj) {                 // @pinta_cada
            cor[u] = BRANCO;                                    // @pintar_branco
            pai[u] = NIL;                                       // @pai_nulo
        }
        tempo = 0;                                              // @zerar_tempo
        for (const std::string &u : ordem) {                    // @cada_raiz
            if (cor[u] == BRANCO) {                             // @raiz_branca
                dfs_visit(u);                                   // @nova_arvore
            }
        }
    }

    void dfs_visit(const std::string &u) {
        tempo = tempo + 1;                                      // @tempo_d
        d[u] = tempo;                                           // @anota_d
        cor[u] = CINZA;                                         // @descobrir
        for (const std::string &v : adj[u]) {                   // @cada_vizinho
            if (voltas[{u, v}] > 0) {                           // @e_volta
                voltas[{u, v}] = voltas[{u, v}] - 1;            // @revisitar
            } else if (cor[v] == BRANCO) {                      // @vizinho_branco
                tipo[{u, v}] = "árvore";                        // @examinar_arvore
                anotar_volta(u, v);                             // @volta_arvore
                pai[v] = u;                                     // @pai_v
                dfs_visit(v);                                   // @desce
            } else {
                tipo[{u, v}] = classificar(u, v);               // @examinar_outra
                anotar_volta(u, v);                             // @volta_outra
            }
        }
        cor[u] = PRETO;                                         // @pintar_preto
        tempo = tempo + 1;                                      // @tempo_f
        f[u] = tempo;                                           // @finalizar
    }

    // A aresta u -> v leva a um vértice já descoberto: retorno, avanço ou cruzamento
    std::string classificar(const std::string &u, const std::string &v) {
        if (cor[v] == CINZA) {                                  // @se_cinza
            return "retorno";                                   // @retorno
        }
        if (d[u] < d[v]) {                                      // @se_descendente
            return "avanço";                                    // @avanco
        }
        return "cruzamento";                                    // @cruzamento
    }

    // Só no não orientado (e fora do laço): a outra metade da aresta, v — u, fica anotada
    void anotar_volta(const std::string &u, const std::string &v) {
        if (!direcionado && u != v) {                           // @se_nao_orientado
            voltas[{v, u}] = voltas[{v, u}] + 1;                // @anota_volta
        }
    }
};
