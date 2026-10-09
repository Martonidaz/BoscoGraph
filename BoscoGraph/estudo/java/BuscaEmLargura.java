import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca em largura (BFS), como BFS(G, s) do livro do Cormen (CLRS).
//   cor -> BRANCO (não descoberto), CINZA (na fila) ou PRETO (terminado)
//   d -> o menor número de arestas de s até cada vértice;  pai -> de onde a busca chegou
//   fila -> entra no fim, sai do começo (ArrayDeque: as duas pontas custam O(1))
public class BuscaEmLargura {
    record Vizinho(String v, double peso) {}            // a BFS não usa o peso
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final Map<String, List<Vizinho>> adj;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Double> d = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final ArrayDeque<String> fila = new ArrayDeque<>();

    public BuscaEmLargura(Map<String, List<Vizinho>> adj) {
        this.adj = adj;
    }

    public void bfs(String s) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            d.put(v, INFINITO);                                 // @d_infinito
            pai.put(v, null);                                   // @inicializar
        }
        cor.put(s, CINZA);                                      // @origem_cinza
        d.put(s, 0.0);                                          // @origem_d
        fila.addLast(s);                                        // @origem
        while (!fila.isEmpty()) {                               // @enquanto_fila
            String u = fila.pollFirst();                        // @desenfileirar
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                String v = vizinho.v();
                if (cor.get(v).equals(BRANCO)) {                // @ignorar_vizinho
                    cor.put(v, CINZA);                          // @pinta_cinza
                    d.put(v, d.get(u) + 1);                     // @d_mais_um
                    pai.put(v, u);                              // @pai_v
                    fila.addLast(v);                            // @descobrir_vizinho
                }
            }
            cor.put(u, PRETO);                                  // @terminar_vertice
        }
    }
}
