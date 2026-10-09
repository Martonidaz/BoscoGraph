// Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do livro do Cormen (CLRS).
//   conjunto -> o representante do conjunto de cada vértice (MAKE-SET, FIND-SET e UNION do livro)
//   arvore   -> as arestas aceitas, na ordem em que entraram
// As arestas são examinadas da mais leve para a mais pesada: a que liga dois conjuntos diferentes entra;
// a que tem as duas pontas no mesmo conjunto fecharia um ciclo e fica de fora. std::stable_sort mantém
// as arestas de mesmo peso na ordem em que foram criadas (o std::sort não garante isso). unir percorre
// todos os vértices: O(V) por união (com a floresta de conjuntos disjuntos do livro, seria quase O(1)).

#include <algorithm>
#include <map>
#include <string>
#include <vector>

class Kruskal {
public:
    struct Aresta {
        std::string u;
        std::string v;
        double peso;
    };

    std::vector<std::string> vertices;
    std::vector<Aresta> arestas;
    std::map<std::string, std::string> conjunto;
    std::vector<Aresta> arvore;

    Kruskal(const std::vector<std::string> &vertices, const std::vector<Aresta> &arestas)
        : vertices(vertices), arestas(arestas) {}

    void kruskal() {
        for (const std::string &v : vertices) {                         // @cada_vertice
            conjunto[v] = v;                                            // @criar_conjunto
        }
        std::vector<Aresta> ordenadas = arestas;                        // @ordenar_arestas
        std::stable_sort(ordenadas.begin(), ordenadas.end(),            // @ordenar_arestas
                         [](const Aresta &a, const Aresta &b) { return a.peso < b.peso; });     // @ordenar_arestas
        for (const Aresta &aresta : ordenadas) {                        // @cada_aresta
            if (conjunto[aresta.u] == conjunto[aresta.v]) {             // @rejeitar
                continue;                                               // @pula_aresta
            }
            arvore.push_back(aresta);                                   // @aceitar
            unir(conjunto[aresta.u], conjunto[aresta.v]);               // @unir
        }
    }

    // UNION: todos os vértices do conjunto b passam para o conjunto a (a e b vêm por cópia: o conjunto
    // de b muda no meio do laço)
    void unir(std::string a, std::string b) {
        for (const std::string &x : vertices) {                         // @cada_do_conjunto
            if (conjunto[x] == b) {                                     // @mesmo_conjunto
                conjunto[x] = a;                                        // @muda_conjunto
            }
        }
    }
};
