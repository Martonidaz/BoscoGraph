// Busca gulosa pela melhor escolha (greedy best-first): sai da fronteira o vértice de menor h,
// a ESTIMATIVA de quanto falta até o destino. Rápida, mas não garante o caminho de menor custo.
//   h   -> a heurística;  cor -> BRANCO (não visto), CINZA (na fronteira), PRETO (expandido)
//   pai -> de onde a busca chegou (null = nenhum)
// Devolve true se chegou ao destino.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";

class BuscaGulosa {
    constructor(adj, h) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...] (a gulosa não usa o peso)
        this.h = h;
        this.cor = new Map();
        this.pai = new Map();
        this.fila = [];
    }

    buscar(s, destino) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.pai.set(v, null);                              // @inicializar
        }
        this.cor.set(s, CINZA);                                 // @origem_cinza
        this.fila.push(s);                                      // @origem
        while (this.fila.length > 0) {                          // @enquanto_fila
            const u = this.extrairMinimo();                     // @chama_extrair
            this.cor.set(u, PRETO);                             // @extrair
            if (u === destino) {                                // @se_destino
                return true;                                    // @chegou
            }
            for (const [v, peso] of this.adj.get(u)) {          // @cada_vizinho
                if (this.cor.get(v) === BRANCO) {               // @ignorar_vizinho
                    this.cor.set(v, CINZA);                     // @pinta_cinza
                    this.pai.set(v, u);                         // @pai_v
                    this.fila.push(v);                          // @descobrir_vizinho
                }
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor h (no empate, o que entrou primeiro)
    extrairMinimo() {
        let menor = this.fila[0];                               // @menor_primeiro
        for (const v of this.fila) {                            // @cada_da_fila
            if (this.h.get(v) < this.h.get(menor)) {            // @compara_h
                menor = v;                                      // @novo_menor
            }
        }
        this.fila.splice(this.fila.indexOf(menor), 1);          // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
}

module.exports = { BuscaGulosa };
