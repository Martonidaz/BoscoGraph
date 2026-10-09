import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca em profundidade (DFS), como DFS(G) e DFS-VISIT(G, u) do livro do Cormen (CLRS).
//   cor -> BRANCO (não descoberto), CINZA (em exploração) ou PRETO (terminado)
//   d, f -> os tempos de descoberta e de término;  pai -> de onde a busca chegou (o π do livro)
//   tipo -> o tipo de cada aresta examinada (u, v): árvore, retorno, avanço ou cruzamento
// No grafo não orientado, "voltas" anota a outra metade de cada aresta já examinada.
// List.of(u, v) serve de chave de um par: duas listas com os mesmos itens são iguais (equals e hashCode).
public class BuscaEmProfundidade {
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";

    final Map<String, List<String>> adj;        // adj.get(u) = os vizinhos de u
    final boolean direcionado;
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Integer> d = new HashMap<>();
    final Map<String, Integer> f = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    int tempo = 0;
    final Map<List<String>, Integer> voltas = new HashMap<>();
    final Map<List<String>, String> tipo = new HashMap<>();

    public BuscaEmProfundidade(Map<String, List<String>> adj, boolean direcionado) {
        this.adj = adj;
        this.direcionado = direcionado;
    }

    public void dfs(List<String> ordem) {
        for (String u : adj.keySet()) {                         // @pinta_cada
            cor.put(u, BRANCO);                                 // @pintar_branco
            pai.put(u, null);                                   // @pai_nulo
        }
        tempo = 0;                                              // @zerar_tempo
        for (String u : ordem) {                                // @cada_raiz
            if (cor.get(u).equals(BRANCO)) {                    // @raiz_branca
                dfsVisit(u);                                    // @nova_arvore
            }
        }
    }

    void dfsVisit(String u) {
        tempo = tempo + 1;                                      // @tempo_d
        d.put(u, tempo);                                        // @anota_d
        cor.put(u, CINZA);                                      // @descobrir
        for (String v : adj.get(u)) {                           // @cada_vizinho
            if (voltas.getOrDefault(List.of(u, v), 0) > 0) {    // @e_volta
                voltas.put(List.of(u, v), voltas.get(List.of(u, v)) - 1);   // @revisitar
            } else if (cor.get(v).equals(BRANCO)) {             // @vizinho_branco
                tipo.put(List.of(u, v), "árvore");              // @examinar_arvore
                anotarVolta(u, v);                              // @volta_arvore
                pai.put(v, u);                                  // @pai_v
                dfsVisit(v);                                    // @desce
            } else {
                tipo.put(List.of(u, v), classificar(u, v));     // @examinar_outra
                anotarVolta(u, v);                              // @volta_outra
            }
        }
        cor.put(u, PRETO);                                      // @pintar_preto
        tempo = tempo + 1;                                      // @tempo_f
        f.put(u, tempo);                                        // @finalizar
    }

    // A aresta u -> v leva a um vértice já descoberto: retorno, avanço ou cruzamento
    String classificar(String u, String v) {
        if (cor.get(v).equals(CINZA)) {                         // @se_cinza
            return "retorno";                                   // @retorno
        }
        if (d.get(u) < d.get(v)) {                              // @se_descendente
            return "avanço";                                    // @avanco
        }
        return "cruzamento";                                    // @cruzamento
    }

    // Só no não orientado (e fora do laço): a outra metade da aresta, v — u, fica anotada
    void anotarVolta(String u, String v) {
        if (!direcionado && !u.equals(v)) {                     // @se_nao_orientado
            voltas.put(List.of(v, u), voltas.getOrDefault(List.of(v, u), 0) + 1);   // @anota_volta
        }
    }
}
