import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Algoritmo de Floyd-Warshall, como FLOYD-WARSHALL(W) do livro do Cormen (CLRS, capítulo 25):
// o menor custo entre TODOS os pares de vértices, numa matriz.
//   d.get(i).get(j)  -> o menor custo conhecido de i até j (INFINITO = ainda sem caminho)
//   pi.get(i).get(j) -> o vértice que vem antes de j no melhor caminho de i até j (o π do livro)
// A matriz é um mapa de mapas: d.get(i) é a linha de i, e d.get(i).get(j) é a casa da coluna j.
// Na rodada de cada vértice k, cada par (i, j) pergunta: passar por k fica mais barato?
// Os pares em que d[i][k] ou d[k][j] é infinito são pulados: passar por k é impossível.
// Aceita pesos negativos. Devolve true, ou false se algum d[i][i] ficar negativo (ciclo negativo).
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos.
//            Entre arestas paralelas, a matriz fica com a mais barata.
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// decimais exatos (BigDecimal faria o mesmo em Java).
public class FloydWarshall {
    record Arco(String u, String v, double peso) {}
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final List<String> vertices;
    final List<Arco> arcos;
    final Map<String, Map<String, Double>> d = new HashMap<>();
    final Map<String, Map<String, String>> pi = new HashMap<>();

    public FloydWarshall(List<String> vertices, List<Arco> arcos) {
        this.vertices = vertices;
        this.arcos = arcos;
    }

    public boolean floydWarshall() {
        for (String i : vertices) {                             // @cada_linha
            d.put(i, new HashMap<>());                          // @nova_linha_d
            pi.put(i, new HashMap<>());                         // @nova_linha_pi
            for (String j : vertices) {                         // @cada_coluna
                d.get(i).put(j, INFINITO);                      // @d_infinito
                pi.get(i).put(j, null);                         // @pi_nulo
            }
            d.get(i).put(i, 0.0);                               // @inicializar_linha
        }
        for (Arco arco : arcos) {                               // @cada_arco
            if (arco.peso() < d.get(arco.u()).get(arco.v())) {  // @arco_nao
                d.get(arco.u()).put(arco.v(), arco.peso());     // @arco_melhorou
                pi.get(arco.u()).put(arco.v(), arco.u());       // @pi_do_arco
            }
        }
        for (String k : vertices) {                             // @rodada_k
            for (String i : vertices) {                         // @cada_i
                for (String j : vertices) {                     // @cada_j
                    // INFINITO é um double (um número), então o == compara os valores
                    if (d.get(i).get(k) == INFINITO || d.get(k).get(j) == INFINITO) {   // @passa_por_k
                        continue;                               // @pula_par
                    }
                    if (d.get(i).get(k) + d.get(k).get(j) < d.get(i).get(j)) {          // @par_nao
                        d.get(i).put(j, d.get(i).get(k) + d.get(k).get(j));             // @par_melhorou
                        pi.get(i).put(j, pi.get(k).get(j));                             // @pi_par
                    }
                }
            }
        }
        for (String i : vertices) {                             // @verifica_diagonal
            if (d.get(i).get(i) < 0) {                          // @testa_diagonal
                return false;                                   // @diagonal_negativa
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
}
