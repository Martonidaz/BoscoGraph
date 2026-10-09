import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Busca de aprofundamento iterativo (IDDFS), como ITERATIVE-DEEPENING-SEARCH do livro do Russell e
// Norvig: a busca em profundidade limitada com limite 0, depois 1, depois 2... até não haver corte.
// Acha o destino com o menor número de arestas (como a busca em largura), guardando só o caminho atual.
//   cor -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
//   prof -> a profundidade com que o vértice entrou no caminho (a última vez, nesta rodada)
//   pai -> de onde o vértice entrou no caminho (a última vez, nesta rodada; null = nenhum)
//   caminho -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão
//   cortados -> onde o limite cortou, nesta rodada
// Devolve ACHOU (o caminho fica em "caminho") ou FALHA (o destino não é alcançável).
// O caminho é uma lista usada como pilha: add põe no topo (o fim) e remove(caminho.size() - 1)
// tira o último, que é o topo. No começo de cada rodada, clear() esvazia prof, caminho e cortados
// (o Python cria um dicionário e listas novas: dá no mesmo).
public class AprofundamentoIterativo {
    static final String BRANCO = "Branco", CINZA = "Cinza", PRETO = "Preto";
    static final String ACHOU = "achou", CORTE = "corte", FALHA = "falha";

    final Map<String, List<String>> adj;        // adj.get(u) = os vizinhos de u
    final Map<String, String> cor = new HashMap<>();
    final Map<String, Integer> prof = new HashMap<>();
    final Map<String, String> pai = new HashMap<>();
    final List<String> caminho = new ArrayList<>();
    final List<String> cortados = new ArrayList<>();

    public AprofundamentoIterativo(Map<String, List<String>> adj) {
        this.adj = adj;
    }

    public String buscar(String s, String destino) {
        int limite = 0;                                         // @limite_zero
        while (true) {                                          // @cada_rodada
            for (String v : adj.keySet()) {                     // @cada_vertice
                cor.put(v, BRANCO);                             // @pinta_branco
                pai.put(v, null);                               // @pai_nulo
            }
            prof.clear();                                       // @zera_prof
            caminho.clear();                                    // @esvazia_caminho
            cortados.clear();                                   // @nova_iteracao
            String resultado = dls(s, destino, limite, 0);      // @chama_dls
            if (!resultado.equals(CORTE)) {                     // @se_nao_cortou
                return resultado;                               // @devolve
            }
            limite = limite + 1;                                // @aumenta_limite
        }
    }

    // A mesma busca limitada: desce no máximo "limite" arestas a partir de u.
    // O parâmetro prof tem o mesmo nome do campo: this.prof é o mapa do objeto (o self.prof do
    // Python); prof sozinho é o número que esta chamada recebeu.
    String dls(String u, String destino, int limite, int prof) {
        cor.put(u, CINZA);                                      // @entrar
        this.prof.put(u, prof);                                 // @anota_prof
        caminho.add(u);                                         // @empilha
        if (u.equals(destino)) {                                // @testa_destino
            return ACHOU;                                       // @chegou
        }
        if (limite == 0) {                                      // @testa_limite
            caminho.remove(caminho.size() - 1);                 // @desempilha_cortado
            cor.put(u, PRETO);                                  // @pinta_cortado
            cortados.add(u);                                    // @corte
            return CORTE;                                       // @devolve_corte
        }
        boolean houveCorte = false;                             // @sem_corte
        for (String v : adj.get(u)) {                           // @cada_vizinho
            // contains procura v na lista inteira (como o "in" do Python)
            if (caminho.contains(v)) {                          // @ignorar_vizinho
                continue;                                       // @pula_vizinho
            }
            pai.put(v, u);                                      // @pai_v
            String resultado = dls(v, destino, limite - 1, prof + 1);   // @desce
            if (resultado.equals(ACHOU)) {                      // @se_achou
                return ACHOU;                                   // @repassa_achou
            }
            if (resultado.equals(CORTE)) {                      // @se_cortou
                houveCorte = true;                              // @houve_corte
            }
        }
        caminho.remove(caminho.size() - 1);                     // @desempilha
        cor.put(u, PRETO);                                      // @subir
        if (houveCorte) {                                       // @se_houve_corte
            return CORTE;                                       // @devolve_corte_de_baixo
        }
        return FALHA;                                           // @devolve_falha
    }
}
