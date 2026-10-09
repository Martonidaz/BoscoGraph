// Busca A* (A estrela): sai da fronteira o vértice de menor f = g + h.
//   g -> o custo do melhor caminho conhecido;  h -> a estimativa até o destino;  f = g + h
// Com h admissível, acha o caminho de menor custo. Se h não for consistente, um vértice já
// expandido pode ganhar um caminho mais barato: aí ele é REABERTO. Devolve true se chegou.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const INFINITO = Infinity;

class AEstrela {
    constructor(adj, h) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...]
        this.h = h;
        this.cor = new Map();
        this.g = new Map();
        this.f = new Map();
        this.pai = new Map();
        this.fila = [];
    }

    buscar(s, destino) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.g.set(v, INFINITO);                            // @g_infinito
            this.f.set(v, INFINITO);                            // @f_infinito
            this.pai.set(v, null);                              // @inicializar
        }
        this.g.set(s, 0);                                       // @origem_g
        this.f.set(s, this.h.get(s));                           // @origem_f
        this.cor.set(s, CINZA);                                 // @origem_cinza
        this.fila.push(s);                                      // @origem
        while (this.fila.length > 0) {                          // @enquanto_fila
            const u = this.extrairMinimo();                     // @chama_extrair
            this.cor.set(u, PRETO);                             // @extrair
            if (u === destino) {                                // @se_destino
                return true;                                    // @chegou
            }
            for (const [v, peso] of this.adj.get(u)) {          // @cada_vizinho
                this.relaxar(u, v, peso);                       // @chama_relaxar
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor f (no empate, o que entrou primeiro)
    extrairMinimo() {
        let menor = this.fila[0];                               // @menor_primeiro
        for (const v of this.fila) {                            // @cada_da_fila
            if (this.f.get(v) < this.f.get(menor)) {            // @compara_f
                menor = v;                                      // @novo_menor
            }
        }
        this.fila.splice(this.fila.indexOf(menor), 1);          // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // Como o RELAX do Dijkstra, mas a prioridade do vizinho passa a ser f = g + h
    relaxar(u, v, peso) {
        const novo = this.g.get(u) + peso;                      // @soma
        if (novo < this.g.get(v)) {                             // @relaxar_nao
            this.g.set(v, novo);                                // @novo_g
            this.f.set(v, novo + this.h.get(v));                // @relaxar_melhorou
            this.pai.set(v, u);                                 // @pai_v
            if (this.cor.get(v) === BRANCO) {                   // @se_branco
                this.cor.set(v, CINZA);                         // @pinta_cinza
                this.fila.push(v);                              // @entra_na_fila
            } else if (this.cor.get(v) === PRETO) {             // @se_preto
                this.cor.set(v, CINZA);                         // @relaxar_reabriu
                this.fila.push(v);                              // @reentra_na_fila
            }
        }
    }
}

module.exports = { AEstrela };
