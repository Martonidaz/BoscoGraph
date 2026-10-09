import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca gulosa pela melhor escolha (greedy best-first): sai da fronteira o vértice de menor h,
// a ESTIMATIVA de quanto falta até o destino. Rápida, mas não garante o caminho de menor custo.
//   h -> a heurística;  cor -> BRANCO (não visto), CINZA (na fronteira), PRETO (expandido)
// Devolve true se chegou ao destino.
public class BuscaGulosa {
    record Vizinho(String v, double peso) {}            // a gulosa não precisa do peso
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";

    final Map<String, List<Vizinho>> adj;
    final Map<String, Double> h;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final List<String> fila = new ArrayList<>();

    public BuscaGulosa(Map<String, List<Vizinho>> adj, Map<String, Double> h) {
        this.adj = adj;
        this.h = h;
    }

    public boolean buscar(String s, String destino) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            pai.put(v, null);                                   // @inicializar
        }
        cor.put(s, CINZA);                                      // @origem_cinza
        fila.add(s);                                            // @origem
        while (!fila.isEmpty()) {                               // @enquanto_fila
            String u = extrairMinimo();                         // @chama_extrair
            cor.put(u, PRETO);                                  // @extrair
            if (u.equals(destino)) {                            // @se_destino
                return true;                                    // @chegou
            }
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                String v = vizinho.v();
                if (cor.get(v).equals(BRANCO)) {                // @ignorar_vizinho
                    cor.put(v, CINZA);                          // @pinta_cinza
                    pai.put(v, u);                              // @pai_v
                    fila.add(v);                                // @descobrir_vizinho
                }
            }
        }
        return false;                                           // @nao_chegou
    }

    // O vértice da fronteira com o menor h (no empate, o que entrou primeiro)
    String extrairMinimo() {
        String menor = fila.get(0);                             // @menor_primeiro
        for (String v : fila) {                                 // @cada_da_fila
            if (h.get(v) < h.get(menor)) {                      // @compara_h
                menor = v;                                      // @novo_menor
            }
        }
        fila.remove(menor);                                     // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
}
