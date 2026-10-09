import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Algoritmo de Bellman-Ford, como BELLMAN-FORD(G, w, s) do livro do Cormen (CLRS).
// Aceita pesos negativos: em cada rodada relaxa TODAS as arestas; |V| − 1 rodadas bastam.
// Se depois disso alguma aresta ainda diminui uma distância, há um ciclo negativo: devolve false.
// Melhoria: se uma rodada não muda nada, as próximas também não mudariam, e a busca para antes.
//   arcos -> as arestas na ordem de criação; no não orientado, cada uma nos dois sentidos
public class BellmanFord {
    record Arco(String u, String v, double peso) {}
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final List<String> vertices;
    final List<Arco> arcos;
    final Map<String, Double> d = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();

    public BellmanFord(List<String> vertices, List<Arco> arcos) {
        this.vertices = vertices;
        this.arcos = arcos;
    }

    public boolean bellmanFord(String s) {
        for (String v : vertices) {                             // @cada_vertice
            d.put(v, INFINITO);                                 // @d_infinito
            pai.put(v, null);                                   // @inicializar
        }
        d.put(s, 0.0);                                          // @origem
        boolean parouAntes = false;                             // @parou_falso
        for (int rodada = 1; rodada < vertices.size(); rodada++) {         // @rodada
            boolean mudou = false;                              // @mudou_falso
            for (Arco arco : arcos) {                           // @cada_arco
                if (d.get(arco.u()) + arco.peso() < d.get(arco.v())) {      // @relaxar_nao
                    d.put(arco.v(), d.get(arco.u()) + arco.peso());          // @relaxar_melhorou
                    pai.put(arco.v(), arco.u());                // @pai_v
                    mudou = true;                               // @mudou
                }
            }
            if (!mudou) {                                       // @se_nao_mudou
                parouAntes = true;                              // @rodada_sem_mudanca
                break;                                          // @para
            }
        }
        if (!parouAntes) {                                      // @se_nao_parou
            for (Arco arco : arcos) {                           // @verificar_ciclo
                if (d.get(arco.u()) + arco.peso() < d.get(arco.v())) {      // @ainda_diminui
                    return false;                               // @ciclo_negativo
                }
            }
        }
        return true;                                            // @sem_ciclo_negativo
    }
}
