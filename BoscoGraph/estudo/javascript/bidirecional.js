// Busca bidirecional: duas buscas em largura, uma a partir da origem s (a "frente") e outra a partir
// do destino t ("trás"). Elas se revezam, cada vez expandindo UMA CAMADA INTEIRA (todos os que estão
// na fila daquele lado), até um lado achar um vértice que o outro já descobriu: o encontro.
//   cor      -> BRANCO (ninguém descobriu), CINZA (na fila de um dos lados) ou PRETO (expandido)
//   lado     -> FRENTE ou TRAS: qual das buscas descobriu o vértice (null = nenhuma)
//   d        -> arestas de s até o vértice (frente);  dTras -> arestas do vértice até t (trás)
//   pai      -> de onde a frente chegou;  paiTras -> o próximo vértice no caminho até t
//   encontro -> [u, v]: u estava sendo expandido e v já era do outro lado (null = nenhum)
// O lado de trás anda pelas arestas AO CONTRÁRIO: adjTras.get(v) = quem chega em v.
// As filas são arrays: push põe no fim, shift tira do começo (o shift arrasta os outros uma
// posição, O(n); veja largura.js). Devolve true (as buscas se encontraram: existe caminho) ou false.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const FRENTE = "frente";
const TRAS = "tras";
const INFINITO = Infinity;

class BuscaBidirecional {
    constructor(adj, adjTras) {
        this.adj = adj;                 // adj.get(u) = [[v, peso], ...]: quem sai de u (a busca não usa o peso)
        this.adjTras = adjTras;         // adjTras.get(v) = [[u, peso], ...]: quem chega em v
        this.cor = new Map();
        this.lado = new Map();
        this.d = new Map();
        this.dTras = new Map();
        this.pai = new Map();
        this.paiTras = new Map();
        this.fila = [];
        this.filaTras = [];
        this.encontro = null;
    }

    buscar(s, t) {
        for (const v of this.adj.keys()) {                      // @cada_vertice
            this.cor.set(v, BRANCO);                            // @pinta_branco
            this.lado.set(v, null);                             // @sem_lado
            this.d.set(v, INFINITO);                            // @d_infinito
            this.dTras.set(v, INFINITO);                        // @d_tras_infinito
            this.pai.set(v, null);                              // @pai_nulo
            this.paiTras.set(v, null);                          // @inicializar
        }
        this.cor.set(s, CINZA);                                 // @origem_cinza
        this.lado.set(s, FRENTE);                               // @origem_lado
        this.d.set(s, 0);                                       // @origem_d
        this.fila.push(s);                                      // @origem
        if (s === t) {                                          // @mesmo_vertice
            this.encontro = [s, s];                             // @encontro_na_origem
            return true;                                        // @devolve_na_origem
        }
        this.cor.set(t, CINZA);                                 // @destino_cinza
        this.lado.set(t, TRAS);                                 // @destino_lado
        this.dTras.set(t, 0);                                   // @destino_d
        this.filaTras.push(t);                                  // @origem_tras
        while (this.fila.length > 0 && this.filaTras.length > 0) {      // @enquanto_filas
            if (this.expandir(FRENTE)) {                        // @expande_frente
                return true;                                    // @achou_pela_frente
            }
            if (this.expandir(TRAS)) {                          // @expande_tras
                return true;                                    // @achou_por_tras
            }
        }
        return false;                                           // @sem_encontro
    }

    // Expande uma camada inteira de um lado; devolve true se encontrou o outro lado.
    // fila, adj, d e pai (sem this) são as variáveis do lado que está andando; this.fila, this.d...
    // são os campos do objeto. [a, b] = [x, y] faz a = x e b = y numa linha só (como no Python).
    // As variáveis apontam para os MESMOS Map e arrays dos campos: mexer nelas muda os campos.
    expandir(lado) {
        let fila, adj, d, pai, outro;
        if (lado === FRENTE) {                                  // @qual_lado
            [fila, adj, d, pai, outro] = [this.fila, this.adj, this.d, this.pai, TRAS];         // @usa_frente
        } else {
            [fila, adj, d, pai, outro] = [this.filaTras, this.adjTras, this.dTras, this.paiTras, FRENTE];   // @usa_tras
        }
        const tamanho = fila.length;                            // @nova_camada
        for (let vez = 0; vez < tamanho; vez++) {               // @cada_da_camada
            const u = fila.shift();                             // @desenfileirar
            for (const [v, peso] of adj.get(u)) {               // @cada_vizinho
                if (this.lado.get(v) === outro) {               // @se_do_outro_lado
                    this.encontro = [u, v];                     // @encontro
                    return true;                                // @devolve_encontro
                }
                if (this.cor.get(v) === BRANCO) {               // @ignorar_vizinho
                    this.cor.set(v, CINZA);                     // @pinta_cinza
                    this.lado.set(v, lado);                     // @anota_lado
                    d.set(v, d.get(u) + 1);                     // @d_mais_um
                    pai.set(v, u);                              // @pai_v
                    fila.push(v);                               // @descobrir_vizinho
                }
            }
            this.cor.set(u, PRETO);                             // @terminar_vertice
        }
        return false;                                           // @camada_sem_encontro
    }
}

module.exports = { BuscaBidirecional };
