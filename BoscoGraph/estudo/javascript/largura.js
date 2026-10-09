// Busca em largura (BFS), como BFS(G, s) do livro do Cormen (CLRS).
//   cor  -> BRANCO (não descoberto), CINZA (descoberto, na fila) ou PRETO (terminado)
//   d    -> o menor número de arestas de s até cada vértice (INFINITO = não alcançado)
//   pai  -> de qual vértice a busca chegou (o π do livro; null = nenhum)
//   fila -> um array: push põe no fim, shift tira do começo. O shift arrasta todos os outros uma
//           posição, O(n), como o lista.pop(0) do Python; numa fila grande, guarde o índice do início.
// Os dicionários são Map: get(chave) lê, set(chave, valor) grava.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const INFINITO = Infinity;

class BuscaEmLargura {
    constructor(adj) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...] (a BFS não usa o peso)
        this.cor = new Map();
        this.d = new Map();
        this.pai = new Map();
        this.fila = [];
    }

    bfs(s) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.d.set(v, INFINITO);                            // @d_infinito
            this.pai.set(v, null);                              // @inicializar
        }
        this.cor.set(s, CINZA);                                 // @origem_cinza
        this.d.set(s, 0);                                       // @origem_d
        this.fila.push(s);                                      // @origem
        while (this.fila.length > 0) {                          // @enquanto_fila
            const u = this.fila.shift();                        // @desenfileirar
            for (const [v, peso] of this.adj.get(u)) {          // @cada_vizinho
                if (this.cor.get(v) === BRANCO) {               // @ignorar_vizinho
                    this.cor.set(v, CINZA);                     // @pinta_cinza
                    this.d.set(v, this.d.get(u) + 1);           // @d_mais_um
                    this.pai.set(v, u);                         // @pai_v
                    this.fila.push(v);                          // @descobrir_vizinho
                }
            }
            this.cor.set(u, PRETO);                             // @terminar_vertice
        }
    }
}

module.exports = { BuscaEmLargura };
