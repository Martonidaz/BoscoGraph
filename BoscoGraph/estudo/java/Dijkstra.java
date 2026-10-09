import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Algoritmo de Dijkstra, como DIJKSTRA(G, w, s) do livro do Cormen (CLRS), na versão em que a fila
// de prioridade só guarda os vértices já alcançados ("busca de custo uniforme").
//   d -> o menor custo conhecido;  pai -> o vértice anterior no melhor caminho;  cor -> BRANCO/CINZA/PRETO
// A fila é uma lista: extrairMinimo percorre todos, O(V). Com um heap (PriorityQueue) seria O(log V).
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// decimais exatos (BigDecimal faria o mesmo em Java).
public class Dijkstra {
    record Vizinho(String v, double peso) {}
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final Map<String, List<Vizinho>> adj;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Double> d = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final List<String> fila = new ArrayList<>();

    public Dijkstra(Map<String, List<Vizinho>> adj) {
        this.adj = adj;
    }

    public void dijkstra(String s) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            d.put(v, INFINITO);                                 // @d_infinito
            pai.put(v, null);                                   // @inicializar
        }
        d.put(s, 0.0);                                          // @origem_d
        cor.put(s, CINZA);                                      // @origem_cinza
        fila.add(s);                                            // @origem
        while (!fila.isEmpty()) {                               // @enquanto_fila
            String u = extrairMinimo();                         // @chama_extrair
            cor.put(u, PRETO);                                  // @extrair
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                relaxar(u, vizinho.v(), vizinho.peso());        // @chama_relaxar
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com o menor d (no empate, o que entrou primeiro)
    String extrairMinimo() {
        String menor = fila.get(0);                             // @menor_primeiro
        for (String v : fila) {                                 // @cada_da_fila
            if (d.get(v) < d.get(menor)) {                      // @compara_d
                menor = v;                                      // @novo_menor
            }
        }
        fila.remove(menor);                                     // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // RELAX(u, v, w): passar por u deixa o caminho até v mais barato?
    void relaxar(String u, String v, double peso) {
        double novo = d.get(u) + peso;                          // @soma
        if (novo < d.get(v)) {                                  // @relaxar_nao
            d.put(v, novo);                                     // @relaxar_melhorou
            pai.put(v, u);                                      // @pai_v
            if (cor.get(v).equals(BRANCO)) {                    // @se_branco
                cor.put(v, CINZA);                              // @pinta_cinza
                fila.add(v);                                    // @entra_na_fila
            }
        }
    }
}
