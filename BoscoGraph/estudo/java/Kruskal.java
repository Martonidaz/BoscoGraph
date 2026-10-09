import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Algoritmo de Kruskal (árvore geradora mínima), como MST-KRUSKAL(G, w) do livro do Cormen (CLRS).
//   conjunto -> o representante do conjunto de cada vértice (MAKE-SET, FIND-SET e UNION do livro)
//   arvore   -> as arestas aceitas, na ordem em que entraram
// As arestas são examinadas da mais leve para a mais pesada: a que liga dois conjuntos diferentes entra;
// a que tem as duas pontas no mesmo conjunto fecharia um ciclo e fica de fora. O sort das listas do Java é
// estável: as arestas de mesmo peso ficam na ordem em que foram criadas. unir percorre todos os vértices:
// O(V) por união (com a floresta de conjuntos disjuntos do livro, seria quase O(1)).
public class Kruskal {
    record Aresta(String u, String v, double peso) {}

    final List<String> vertices;
    final List<Aresta> arestas;
    final Map<String, String> conjunto = new HashMap<>();
    final List<Aresta> arvore = new ArrayList<>();

    public Kruskal(List<String> vertices, List<Aresta> arestas) {
        this.vertices = vertices;
        this.arestas = arestas;
    }

    public void kruskal() {
        for (String v : vertices) {                                     // @cada_vertice
            conjunto.put(v, v);                                         // @criar_conjunto
        }
        List<Aresta> ordenadas = new ArrayList<>(arestas);              // @ordenar_arestas
        ordenadas.sort(Comparator.comparingDouble(Aresta::peso));       // @ordenar_arestas
        for (Aresta aresta : ordenadas) {                               // @cada_aresta
            String u = aresta.u();                                      // @cada_aresta
            String v = aresta.v();                                      // @cada_aresta
            if (conjunto.get(u).equals(conjunto.get(v))) {              // @rejeitar
                continue;                                               // @pula_aresta
            }
            arvore.add(aresta);                                         // @aceitar
            unir(conjunto.get(u), conjunto.get(v));                     // @unir
        }
    }

    // UNION: todos os vértices do conjunto b passam para o conjunto a
    void unir(String a, String b) {
        for (String x : vertices) {                                     // @cada_do_conjunto
            if (conjunto.get(x).equals(b)) {                            // @mesmo_conjunto
                conjunto.put(x, a);                                     // @muda_conjunto
            }
        }
    }
}
