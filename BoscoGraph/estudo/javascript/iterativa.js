// Busca de aprofundamento iterativo (IDDFS), como ITERATIVE-DEEPENING-SEARCH do livro do Russell e
// Norvig: a busca em profundidade limitada com limite 0, depois 1, depois 2... até não haver corte.
// Acha o destino com o menor número de arestas (como a busca em largura), guardando só o caminho atual.
//   cor      -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
//   prof     -> a profundidade com que o vértice entrou no caminho (a última vez, nesta rodada)
//   pai      -> de onde o vértice entrou no caminho (a última vez, nesta rodada; null = nenhum)
//   caminho  -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão
//   cortados -> onde o limite cortou, nesta rodada
// Devolve ACHOU (o caminho fica em "caminho") ou FALHA (o destino não é alcançável).
// Os dicionários são Map: get(chave) lê, set(chave, valor) grava. O caminho é um array usado como
// pilha: push põe no topo (o fim) e pop tira do topo.

const BRANCO = "Branco";
const CINZA = "Cinza";
const PRETO = "Preto";
const ACHOU = "achou";
const CORTE = "corte";
const FALHA = "falha";

class AprofundamentoIterativo {
    constructor(adj) {
        this.adj = adj;                 // adj.get(u) = [v1, v2, ...]
        this.cor = new Map();
        this.prof = new Map();
        this.pai = new Map();
        this.caminho = [];
        this.cortados = [];
    }

    buscar(s, destino) {
        let limite = 0;                                         // @limite_zero
        while (true) {                                          // @cada_rodada
            for (const v of this.adj.keys()) {                  // @cada_vertice
                this.cor.set(v, BRANCO);                        // @pinta_branco
                this.pai.set(v, null);                          // @pai_nulo
            }
            this.prof = new Map();                              // @zera_prof
            this.caminho = [];                                  // @esvazia_caminho
            this.cortados = [];                                 // @nova_iteracao
            const resultado = this.dls(s, destino, limite, 0);  // @chama_dls
            if (resultado !== CORTE) {                          // @se_nao_cortou
                return resultado;                               // @devolve
            }
            limite = limite + 1;                                // @aumenta_limite
        }
    }

    // A mesma busca limitada: desce no máximo "limite" arestas a partir de u
    dls(u, destino, limite, prof) {
        this.cor.set(u, CINZA);                                 // @entrar
        this.prof.set(u, prof);                                 // @anota_prof
        this.caminho.push(u);                                   // @empilha
        if (u === destino) {                                    // @testa_destino
            return ACHOU;                                       // @chegou
        }
        if (limite === 0) {                                     // @testa_limite
            this.caminho.pop();                                 // @desempilha_cortado
            this.cor.set(u, PRETO);                             // @pinta_cortado
            this.cortados.push(u);                              // @corte
            return CORTE;                                       // @devolve_corte
        }
        let houveCorte = false;                                 // @sem_corte
        for (const v of this.adj.get(u)) {                      // @cada_vizinho
            // includes procura v no array inteiro (como o "in" do Python)
            if (this.caminho.includes(v)) {                     // @ignorar_vizinho
                continue;                                       // @pula_vizinho
            }
            this.pai.set(v, u);                                 // @pai_v
            const resultado = this.dls(v, destino, limite - 1, prof + 1);   // @desce
            if (resultado === ACHOU) {                          // @se_achou
                return ACHOU;                                   // @repassa_achou
            }
            if (resultado === CORTE) {                          // @se_cortou
                houveCorte = true;                              // @houve_corte
            }
        }
        this.caminho.pop();                                     // @desempilha
        this.cor.set(u, PRETO);                                 // @subir
        if (houveCorte) {                                       // @se_houve_corte
            return CORTE;                                       // @devolve_corte_de_baixo
        }
        return FALHA;                                           // @devolve_falha
    }
}

module.exports = { AprofundamentoIterativo };
