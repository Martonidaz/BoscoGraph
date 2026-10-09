import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca bidirecional: duas buscas em largura, uma a partir da origem s (a "frente") e outra a partir
// do destino t ("trás"). Elas se revezam, cada vez expandindo UMA CAMADA INTEIRA (todos os que estão
// na fila daquele lado), até um lado achar um vértice que o outro já descobriu: o encontro.
//   cor -> BRANCO (ninguém descobriu), CINZA (na fila de um dos lados) ou PRETO (expandido)
//   lado -> FRENTE ou TRAS: qual das buscas descobriu o vértice (null = nenhuma)
//   d -> arestas de s até o vértice (frente);  dTras -> arestas do vértice até t (trás)
//   pai -> de onde a frente chegou;  paiTras -> o próximo vértice no caminho até t
//   encontro -> o par List.of(u, v): u estava sendo expandido e v já era do outro lado (null = nenhum)
// O lado de trás anda pelas arestas AO CONTRÁRIO: adjTras.get(v) = quem chega em v.
// As filas são ArrayDeque: entra no fim, sai do começo (as duas pontas custam O(1)).
// Devolve true (as buscas se encontraram: existe caminho) ou false.
public class BuscaBidirecional {
    record Vizinho(String v, double peso) {}            // a busca não usa o peso
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final String FRENTE = "frente", TRAS = "tras";
    static final double INFINITO = Double.POSITIVE_INFINITY;

    final Map<String, List<Vizinho>> adj;       // adj.get(u) = quem sai de u
    final Map<String, List<Vizinho>> adjTras;   // adjTras.get(v) = quem chega em v
    final Map<String, String> cor = new HashMap<>();
    final Map<String, String> lado = new HashMap<>();
    final Map<String, Double> d = new HashMap<>();
    final Map<String, Double> dTras = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final Map<String, String> paiTras = new HashMap<>();
    final ArrayDeque<String> fila = new ArrayDeque<>();
    final ArrayDeque<String> filaTras = new ArrayDeque<>();
    List<String> encontro = null;

    public BuscaBidirecional(Map<String, List<Vizinho>> adj, Map<String, List<Vizinho>> adjTras) {
        this.adj = adj;
        this.adjTras = adjTras;
    }

    public boolean buscar(String s, String t) {
        for (String v : adj.keySet()) {                         // @cada_vertice
            cor.put(v, BRANCO);                                 // @pinta_branco
            lado.put(v, null);                                  // @sem_lado
            d.put(v, INFINITO);                                 // @d_infinito
            dTras.put(v, INFINITO);                             // @d_tras_infinito
            pai.put(v, null);                                   // @pai_nulo
            paiTras.put(v, null);                               // @inicializar
        }
        cor.put(s, CINZA);                                      // @origem_cinza
        lado.put(s, FRENTE);                                    // @origem_lado
        d.put(s, 0.0);                                          // @origem_d
        fila.addLast(s);                                        // @origem
        if (s.equals(t)) {                                      // @mesmo_vertice
            encontro = List.of(s, s);                           // @encontro_na_origem
            return true;                                        // @devolve_na_origem
        }
        cor.put(t, CINZA);                                      // @destino_cinza
        lado.put(t, TRAS);                                      // @destino_lado
        dTras.put(t, 0.0);                                      // @destino_d
        filaTras.addLast(t);                                    // @origem_tras
        while (!fila.isEmpty() && !filaTras.isEmpty()) {        // @enquanto_filas
            if (expandir(FRENTE)) {                             // @expande_frente
                return true;                                    // @achou_pela_frente
            }
            if (expandir(TRAS)) {                               // @expande_tras
                return true;                                    // @achou_por_tras
            }
        }
        return false;                                           // @sem_encontro
    }

    // Expande uma camada inteira de um lado; devolve true se encontrou o outro lado.
    // Aqui dentro, fila, adj, d, pai e lado SEM this são as variáveis deste método (as do lado que
    // está andando); COM this (this.fila, this.lado...) são os campos do objeto, como o self do Python.
    boolean expandir(String lado) {
        ArrayDeque<String> fila;
        Map<String, List<Vizinho>> adj;
        Map<String, Double> d;
        Map<String, String> pai;
        String outro;
        if (lado.equals(FRENTE)) {                              // @qual_lado
            fila = this.fila;                                   // @usa_frente
            adj = this.adj;                                     // @usa_frente
            d = this.d;                                         // @usa_frente
            pai = this.pai;                                     // @usa_frente
            outro = TRAS;                                       // @usa_frente
        } else {
            fila = this.filaTras;                               // @usa_tras
            adj = this.adjTras;                                 // @usa_tras
            d = this.dTras;                                     // @usa_tras
            pai = this.paiTras;                                 // @usa_tras
            outro = FRENTE;                                     // @usa_tras
        }
        // fila, d e pai apontam para os MESMOS objetos dos campos: mexer neles muda os campos
        int tamanho = fila.size();                              // @nova_camada
        for (int vez = 0; vez < tamanho; vez++) {               // @cada_da_camada
            String u = fila.pollFirst();                        // @desenfileirar
            for (Vizinho vizinho : adj.get(u)) {                // @cada_vizinho
                String v = vizinho.v();
                // this.lado.get(v) pode ser null (ninguém descobriu v); outro nunca é null,
                // por isso o equals é chamado em outro
                if (outro.equals(this.lado.get(v))) {           // @se_do_outro_lado
                    this.encontro = List.of(u, v);              // @encontro
                    return true;                                // @devolve_encontro
                }
                if (this.cor.get(v).equals(BRANCO)) {           // @ignorar_vizinho
                    this.cor.put(v, CINZA);                     // @pinta_cinza
                    this.lado.put(v, lado);                     // @anota_lado
                    d.put(v, d.get(u) + 1);                     // @d_mais_um
                    pai.put(v, u);                              // @pai_v
                    fila.addLast(v);                            // @descobrir_vizinho
                }
            }
            this.cor.put(u, PRETO);                             // @terminar_vertice
        }
        return false;                                           // @camada_sem_encontro
    }
}
