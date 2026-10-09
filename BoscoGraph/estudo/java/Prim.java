import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Algoritmo de Prim (árvore geradora mínima), como MST-PRIM(G, w, r) do livro do Cormen (CLRS), na mesma
// forma do Dijkstra daqui: a fila de prioridade só guarda os vértices já alcançados.
//   chave -> o peso da aresta mais leve que liga o vértice à árvore;  pai -> a outra ponta dela
//   cor   -> BRANCO (fora, sem ligação), CINZA (na fila) ou PRETO (já está na árvore)
// Como no DFS(G), uma árvore nova começa em cada parte desligada: é a floresta geradora mínima.
// A fila é uma lista: extrairMinimo percorre todos, O(V). Com um heap (PriorityQueue) seria O(log V).
// Atenção: double tem erro de arredondamento (0.1 + 0.2 dá 0.30000000000000004); o BoscoGraph usa
// decimais exatos (BigDecimal faria o mesmo em Java).
public class Prim {
    record Vizinho(String v, double peso) {}
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final Map<String, List<Vizinho>> adj;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Double> chave = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final List<String> fila = new ArrayList<>();

    public Prim(Map<String, List<Vizinho>> adj) {
        this.adj = adj;
    }

    public void prim(List<String> raizes) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            chave.put(v, INFINITO);                             // @chave_infinito
            pai.put(v, null);                                   // @inicializar
        }
        for (String r : raizes) {                               // @cada_raiz
            if (cor.get(r).equals(BRANCO)) {                    // @raiz_branca
                crescer(r);                                     // @chama_crescer
            }
        }
    }

    // A árvore que começa em r cresce até a fila esvaziar (até todos da parte de r entrarem)
    void crescer(String r) {
        chave.put(r, 0.0);                                      // @raiz_chave
        cor.put(r, CINZA);                                      // @raiz_cinza
        fila.add(r);                                            // @raiz
        while (!fila.isEmpty()) {                               // @enquanto_fila
            String u = extrairMinimo();                         // @chama_extrair
            cor.put(u, PRETO);                                  // @extrair
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                String v = vizinho.v();                         // @cada_vizinho
                if (cor.get(v).equals(PRETO)) {                 // @ignorar_vizinho
                    continue;                                   // @pula_vizinho
                }
                if (vizinho.peso() < chave.get(v)) {            // @atualizar_nao
                    chave.put(v, vizinho.peso());               // @atualizar_melhorou
                    pai.put(v, u);                              // @pai_v
                    if (cor.get(v).equals(BRANCO)) {            // @se_branco
                        cor.put(v, CINZA);                      // @pinta_cinza
                        fila.add(v);                            // @entra_na_fila
                    }
                }
            }
        }
    }

    // EXTRACT-MIN: o vértice da fila com a menor chave (no empate, o que entrou primeiro)
    String extrairMinimo() {
        String menor = fila.get(0);                             // @menor_primeiro
        for (String v : fila) {                                 // @cada_da_fila
            if (chave.get(v) < chave.get(menor)) {              // @compara_chave
                menor = v;                                      // @novo_menor
            }
        }
        fila.remove(menor);                                     // @tira_da_fila
        return menor;                                           // @devolve_menor
    }
}
