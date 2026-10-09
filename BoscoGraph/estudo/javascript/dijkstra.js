// Algoritmo de Dijkstra, como DIJKSTRA(G, w, s) do livro do Cormen (CLRS), na versão em que a fila
// de prioridade só guarda os vértices já alcançados ("busca de custo uniforme").
//   d   -> o menor custo conhecido;  pai -> o vértice anterior no melhor caminho (null = nenhum)
//   cor -> BRANCO (não alcançado), CINZA (na fila) ou PRETO (d definitivo)
// A fila é um array: extrairMinimo percorre todos, O(V). Com um heap seria O(log V).
// Atenção: os números do JavaScript são double: 0.1 + 0.2 dá 0.30000000000000004. O BoscoGraph
// usa números decimais exatos.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const INFINITO = Infinity;

class Dijkstra {
    constructor(adj) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...]
        this.cor = new Map();
        this.d = new Map();
        this.pai = new Map();
        this.fila = [];
    }

    dijkstra(s) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.d.set(v, INFINITO);                            // @d_infinito
            this.pai.set(v, null);                              // @inicializar
        }
        this.d.set(s, 0);                                       // @origem_d
        this.cor.set(s, CINZA);                                 // @origem_cinza
        this.fila.push(s);                                      // @origem
        while (this.fila.length > 0) {                          // @enquanto_fila
            const u = this.extrairMinimo();                     // @chama_extrair
            this.cor.set(u, PRETO);                             // @extrair
            for (const [v, peso] of this.adj.get(u)) {          // @cada_vizinho
                this.relaxar(u, v, peso);                       // @chama_relaxar
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com o menor d (no empate, o que entrou primeiro)
    extrairMinimo() {
        let menor = this.fila[0];                               // @menor_primeiro
        for (const v of this.fila) {                            // @cada_da_fila
            if (this.d.get(v) < this.d.get(menor)) {            // @compara_d
                menor = v;                                      // @novo_menor
            }
        }
        this.fila.splice(this.fila.indexOf(menor), 1);          // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // RELAX(u, v, w): passar por u deixa o caminho até v mais barato?
    relaxar(u, v, peso) {
        const novo = this.d.get(u) + peso;                      // @soma
        if (novo < this.d.get(v)) {                             // @relaxar_nao
            this.d.set(v, novo);                                // @relaxar_melhorou
            this.pai.set(v, u);                                 // @pai_v
            if (this.cor.get(v) === BRANCO) {                   // @se_branco
                this.cor.set(v, CINZA);                         // @pinta_cinza
                this.fila.push(v);                              // @entra_na_fila
            }
        }
    }
}

module.exports = { Dijkstra };
