// Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do livro do Cormen (CLRS).
//   conjunto -> o representante do conjunto de cada vértice (MAKE-SET, FIND-SET e UNION do livro)
//   arvore   -> as arestas aceitas [u, v, peso], na ordem em que entraram
// As arestas são examinadas da mais leve para a mais pesada: a que liga dois conjuntos diferentes entra;
// a que tem as duas pontas no mesmo conjunto fecharia um ciclo e fica de fora. O sort do JavaScript é
// estável: as arestas de mesmo peso ficam na ordem em que foram criadas. unir percorre todos os vértices:
// O(V) por união (com a floresta de conjuntos disjuntos do livro, seria quase O(1)).

class Kruskal {
    constructor(vertices, arestas) {
        this.vertices = vertices;       // os nomes dos vértices
        this.arestas = arestas;         // [u, v, peso], uma vez cada, na ordem em que foram criadas
        this.conjunto = new Map();
        this.arvore = [];
    }

    kruskal() {
        for (const v of this.vertices) {                                // @cada_vertice
            this.conjunto.set(v, v);                                    // @criar_conjunto
        }
        const ordenadas = [...this.arestas].sort((a, b) => a[2] - b[2]);       // @ordenar_arestas
        for (const [u, v, peso] of ordenadas) {                         // @cada_aresta
            if (this.conjunto.get(u) === this.conjunto.get(v)) {        // @rejeitar
                continue;                                               // @pula_aresta
            }
            this.arvore.push([u, v, peso]);                             // @aceitar
            this.unir(this.conjunto.get(u), this.conjunto.get(v));      // @unir
        }
    }

    // UNION: todos os vértices do conjunto b passam para o conjunto a
    unir(a, b) {
        for (const x of this.vertices) {                                // @cada_do_conjunto
            if (this.conjunto.get(x) === b) {                           // @mesmo_conjunto
                this.conjunto.set(x, a);                                // @muda_conjunto
            }
        }
    }
}

module.exports = { Kruskal };
