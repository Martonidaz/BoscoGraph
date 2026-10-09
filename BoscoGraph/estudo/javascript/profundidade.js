// Busca em profundidade (DFS), como DFS(G) e DFS-VISIT(G, u) do livro do Cormen (CLRS).
//   cor  -> BRANCO (não descoberto), CINZA (em exploração) ou PRETO (terminado)
//   d, f -> os tempos de descoberta e de término;  pai -> de onde a busca chegou (o π do livro)
//   tipo -> o tipo de cada aresta examinada (u, v): árvore, retorno, avanço ou cruzamento
// No grafo não orientado, "voltas" anota a outra metade de cada aresta já examinada.
// Os dicionários são Map. Cuidado: o Map compara chaves que são listas pela REFERÊNCIA (o endereço
// na memória), não pelo conteúdo: ["A", "B"] !== ["A", "B"]. Por isso o par (u, v) vira um texto.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";

// A chave de um par (u, v): JSON.stringify(["A", "B"]) dá '["A","B"]' (sem confundir nomes)
function par(u, v) {
    return JSON.stringify([u, v]);
}

class BuscaEmProfundidade {
    constructor(adj, direcionado) {
        this.adj = adj;                 // adj.get(u) = [v1, v2, ...]
        this.direcionado = direcionado;
        this.cor = new Map();
        this.d = new Map();
        this.f = new Map();
        this.pai = new Map();
        this.tempo = 0;
        this.voltas = new Map();
        this.tipo = new Map();
    }

    dfs(ordem) {
        for (const u of this.adj.keys()) {                      // @pinta_cada
            this.cor.set(u, BRANCO);                            // @pintar_branco
            this.pai.set(u, null);                              // @pai_nulo
        }
        this.tempo = 0;                                         // @zerar_tempo
        for (const u of ordem) {                                // @cada_raiz
            if (this.cor.get(u) === BRANCO) {                   // @raiz_branca
                this.dfsVisit(u);                               // @nova_arvore
            }
        }
    }

    dfsVisit(u) {
        this.tempo = this.tempo + 1;                            // @tempo_d
        this.d.set(u, this.tempo);                              // @anota_d
        this.cor.set(u, CINZA);                                 // @descobrir
        for (const v of this.adj.get(u)) {                      // @cada_vizinho
            // a ?? 0: se o Map não tem a chave (undefined), vale 0
            if ((this.voltas.get(par(u, v)) ?? 0) > 0) {        // @e_volta
                this.voltas.set(par(u, v), this.voltas.get(par(u, v)) - 1);    // @revisitar
            } else if (this.cor.get(v) === BRANCO) {            // @vizinho_branco
                this.tipo.set(par(u, v), "árvore");             // @examinar_arvore
                this.anotarVolta(u, v);                         // @volta_arvore
                this.pai.set(v, u);                             // @pai_v
                this.dfsVisit(v);                               // @desce
            } else {
                this.tipo.set(par(u, v), this.classificar(u, v));               // @examinar_outra
                this.anotarVolta(u, v);                         // @volta_outra
            }
        }
        this.cor.set(u, PRETO);                                 // @pintar_preto
        this.tempo = this.tempo + 1;                            // @tempo_f
        this.f.set(u, this.tempo);                              // @finalizar
    }

    // A aresta u -> v leva a um vértice já descoberto: retorno, avanço ou cruzamento
    classificar(u, v) {
        if (this.cor.get(v) === CINZA) {                        // @se_cinza
            return "retorno";                                   // @retorno
        }
        if (this.d.get(u) < this.d.get(v)) {                    // @se_descendente
            return "avanço";                                    // @avanco
        }
        return "cruzamento";                                    // @cruzamento
    }

    // Só no não orientado (e fora do laço): a outra metade da aresta, v — u, fica anotada
    anotarVolta(u, v) {
        if (!this.direcionado && u !== v) {                     // @se_nao_orientado
            this.voltas.set(par(v, u), (this.voltas.get(par(v, u)) ?? 0) + 1);  // @anota_volta
        }
    }
}

module.exports = { BuscaEmProfundidade };
