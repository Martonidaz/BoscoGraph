// Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25):
// o menor custo entre TODOS os pares de vértices, numa matriz.
//   d.get(i).get(j)  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
//   pi.get(i).get(j) -> o vértice que vem antes de j no melhor caminho de i até j (o π do livro;
//                       null = nenhum)
// A matriz é um Map de Maps: d.get(i) é a linha de i, e d.get(i).get(j) é a casa da coluna j.
// Na rodada de cada vértice k, cada par (i, j) pergunta: passar por k fica mais barato?
// Os pares em que d[i][k] ou d[k][j] é infinito são pulados: passar por k é impossível.
// Aceita pesos negativos. Devolve true, ou false se algum d[i][i] ficar negativo (ciclo negativo).
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos.
//            Entre arestas paralelas, a matriz fica com a mais barata.
// Atenção: os números do JavaScript são double: 0.1 + 0.2 dá 0.30000000000000004. O BoscoGraph
// usa números decimais exatos.

const INFINITO = Infinity;

class FloydWarshall {
    constructor(vertices, arcos) {
        this.vertices = vertices;       // os nomes dos vértices
        this.arcos = arcos;             // [[u, v, peso], ...]
        this.d = new Map();
        this.pi = new Map();
    }

    floydWarshall() {
        for (const i of this.vertices) {                        // @cada_linha
            this.d.set(i, new Map());                           // @nova_linha_d
            this.pi.set(i, new Map());                          // @nova_linha_pi
            for (const j of this.vertices) {                    // @cada_coluna
                this.d.get(i).set(j, INFINITO);                 // @d_infinito
                this.pi.get(i).set(j, null);                    // @pi_nulo
            }
            this.d.get(i).set(i, 0);                            // @inicializar_linha
        }
        for (const [u, v, peso] of this.arcos) {                // @cada_arco
            if (peso < this.d.get(u).get(v)) {                  // @arco_nao
                this.d.get(u).set(v, peso);                     // @arco_melhorou
                this.pi.get(u).set(v, u);                       // @pi_do_arco
            }
        }
        for (const k of this.vertices) {                        // @rodada_k
            for (const i of this.vertices) {                    // @cada_i
                for (const j of this.vertices) {                // @cada_j
                    if (this.d.get(i).get(k) === INFINITO || this.d.get(k).get(j) === INFINITO) {   // @passa_por_k
                        continue;                               // @pula_par
                    }
                    if (this.d.get(i).get(k) + this.d.get(k).get(j) < this.d.get(i).get(j)) {       // @par_nao
                        this.d.get(i).set(j, this.d.get(i).get(k) + this.d.get(k).get(j));          // @par_melhorou
                        this.pi.get(i).set(j, this.pi.get(k).get(j));                               // @pi_par
                    }
                }
            }
        }
        for (const i of this.vertices) {                        // @verifica_diagonal
            if (this.d.get(i).get(i) < 0) {                     // @testa_diagonal
                return false;                                   // @diagonal_negativa
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
}

module.exports = { FloydWarshall };
