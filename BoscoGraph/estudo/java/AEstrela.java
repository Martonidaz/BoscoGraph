import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca A* (A estrela): sai da fronteira o vértice de menor f = g + h.
//   g -> o custo do melhor caminho conhecido;  h -> a estimativa até o destino;  f = g + h
// Com h admissível, acha o caminho de menor custo. Se h não for consistente, um vértice já
// expandido pode ganhar um caminho mais barato: aí ele é REABERTO. Devolve true se chegou.
public class AEstrela {
    record Vizinho(String v, double peso) {}
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final Map<String, List<Vizinho>> adj;
    final Map<String, Double> h;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Double> g = new HashMap<>();
    final Map<String, Double> f = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final List<String> fila = new ArrayList<>();

    public AEstrela(Map<String, List<Vizinho>> adj, Map<String, Double> h) {
        this.adj = adj;
        this.h = h;
    }

    public boolean buscar(String s, String destino) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            g.put(v, INFINITO);                                 // @g_infinito
            f.put(v, INFINITO);                                 // @f_infinito
            pai.put(v, null);                                   // @inicializar
        }
        g.put(s, 0.0);                                          // @origem_g
        f.put(s, h.get(s));                                     // @origem_f
        cor.put(s, CINZA);                                      // @origem_cinza
        fila.add(s);                                            // @origem
        while (!fila.isEmpty()) {                               // @enquanto_fila
            String u = extrairMinimo();                         // @chama_extrair
            cor.put(u, PRETO);                                  // @extrair
            if (u.equals(destino)) {                            // @se_destino
                return true;                                    // @chegou
            }
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                relaxar(u, vizinho.v(), vizinho.peso());        // @chama_relaxar
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor f (no empate, o que entrou primeiro)
    String extrairMinimo() {
        String menor = fila.get(0);                             // @menor_primeiro
        for (String v : fila) {                                 // @cada_da_fila
            if (f.get(v) < f.get(menor)) {                      // @compara_f
                menor = v;                                      // @novo_menor
            }
        }
        fila.remove(menor);                                     // @tira_da_fila
        return menor;                                           // @devolve_menor
    }

    // Como o RELAX do Dijkstra, mas a prioridade do vizinho passa a ser f = g + h
    void relaxar(String u, String v, double peso) {
        double novo = g.get(u) + peso;                          // @soma
        if (novo < g.get(v)) {                                  // @relaxar_nao
            g.put(v, novo);                                     // @novo_g
            f.put(v, novo + h.get(v));                          // @relaxar_melhorou
            pai.put(v, u);                                      // @pai_v
            if (cor.get(v).equals(BRANCO)) {                    // @se_branco
                cor.put(v, CINZA);                              // @pinta_cinza
                fila.add(v);                                    // @entra_na_fila
            } else if (cor.get(v).equals(PRETO)) {              // @se_preto
                cor.put(v, CINZA);                              // @relaxar_reabriu
                fila.add(v);                                    // @reentra_na_fila
            }
        }
    }
}
