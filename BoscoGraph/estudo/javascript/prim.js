// Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do livro do Cormen (CLRS), na mesma
// forma do Dijkstra daqui: a fila de prioridade só guarda os vértices já alcançados.
//   chave -> o peso da aresta mais leve que liga o vértice à árvore;  pai -> a outra ponta (null = nenhum)
//   cor   -> BRANCO (fora, sem ligação), CINZA (na fila) ou PRETO (já está na árvore)
// Como no DFS(G), uma árvore nova começa em cada parte desligada: é a floresta geradora mínima.
// A fila é um array: extrairMinimo percorre todos, O(V). Com um heap seria O(log V).
// Atenção: os números do JavaScript são double: 0.1 + 0.2 dá 0.30000000000000004. O BoscoGraph
// usa números decimais exatos.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const INFINITO = Infinity;

class Prim {
    constructor(adj) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...]
        this.cor = new Map();
        this.chave = new Map();
        this.pai = new Map();
        this.fila = [];
    }

    prim(raizes) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.chave.set(v, INFINITO);                        // @chave_infinito
            this.pai.set(v, null);                              // @inicializar
        }
        for (const r of raizes) {                               // @cada_raiz
            if (this.cor.get(r) === BRANCO) {                   // @raiz_branca
                this.crescer(r);                                // @chama_crescer
            }
        }
    }

    // A árvore que começa em r cresce até a fila esvaziar (até todos da parte de r entrarem)
    crescer(r) {
        this.chave.set(r, 0);                                   // @raiz_chave
        this.cor.set(r, CINZA);                                 // @raiz_cinza
        this.fila.push(r);                                      // @raiz
        while (this.fila.length > 0) {                          // @enquanto_fila
            const u = this.extrairMinimo();                     // @chama_extrair
            this.cor.set(u, PRETO);                             // @extrair
            for (const [v, peso] of this.adj.get(u)) {          // @cada_vizinho
                if (this.cor.get(v) === PRETO) {                // @ignorar_vizinho
                    continue;                                   // @pula_vizinho
                }
                if (peso < this.chave.get(v)) {                 // @atualizar_nao
                    this.chave.set(v, peso);                    // @atualizar_melhorou
                    this.pai.set(v, u);                         // @pai_v
                    if (this.cor.get(v) === BRANCO) {           // @se_branco
                        this.cor.set(v, CINZA);                 // @pinta_cinza
                        this.fila.push(v);                      // @entra_na_fila
                    }
                }
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com a menor chave (no empate, o que entrou primeiro)
    extrairMinimo() {
        let menor = this.fila[0];                               // @menor_primeiro
        for (const v of this.fila) {                            // @cada_da_fila
            if (this.chave.get(v) < this.chave.get(menor)) {    // @compara_chave
                menor = v;                                      // @novo_menor
            }
        }
        this.fila.splice(this.fila.indexOf(menor), 1);          // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
}

module.exports = { Prim };
