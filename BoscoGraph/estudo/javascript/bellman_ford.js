// Algoritmo de Bellman-Ford, como BELLMAN-FORD(G, w, s) do livro do Cormen (CLRS).
// Aceita pesos negativos: em cada rodada relaxa TODAS as arestas; |V| − 1 rodadas bastam.
// Se depois disso alguma aresta ainda diminui uma distância, há um ciclo negativo: devolve false.
// Melhoria: se uma rodada não muda nada, as próximas também não mudariam, e a busca para antes.
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos

const INFINITO = Infinity;

class BellmanFord {
    constructor(vertices, arcos) {
        this.vertices = vertices;       // os nomes dos vértices
        this.arcos = arcos;             // [[u, v, peso], ...]
        this.d = new Map();
        this.pai = new Map();
    }

    bellmanFord(s) {
        for (const v of this.vertices) {                        // @cada_vertice
            this.d.set(v, INFINITO);                            // @d_infinito
            this.pai.set(v, null);                              // @inicializar
        }
        this.d.set(s, 0);                                       // @origem
        let parouAntes = false;                                 // @parou_falso
        for (let rodada = 1; rodada < this.vertices.length; rodada++) {     // @rodada
            let mudou = false;                                  // @mudou_falso
            for (const [u, v, peso] of this.arcos) {            // @cada_arco
                if (this.d.get(u) + peso < this.d.get(v)) {     // @relaxar_nao
                    this.d.set(v, this.d.get(u) + peso);        // @relaxar_melhorou
                    this.pai.set(v, u);                         // @pai_v
                    mudou = true;                               // @mudou
                }
            }
            if (!mudou) {                                       // @se_nao_mudou
                parouAntes = true;                              // @rodada_sem_mudanca
                break;                                          // @para
            }
        }
        if (!parouAntes) {                                      // @se_nao_parou
            for (const [u, v, peso] of this.arcos) {            // @verificar_ciclo
                if (this.d.get(u) + peso < this.d.get(v)) {     // @ainda_diminui
                    return false;                               // @ciclo_negativo
                }
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
}

module.exports = { BellmanFord };
