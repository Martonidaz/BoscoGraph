// Busca em profundidade limitada (DLS), como RECURSIVE-DLS do livro do Russell e Norvig, sem repetir
// vértices do caminho atual (senão a busca andaria em círculo).
//   cor      -> BRANCO (fora do caminho), CINZA (no caminho atual) ou PRETO (já saiu do caminho)
//   prof     -> a profundidade com que cada vértice entrou no caminho (a última vez)
//   pai      -> de onde cada vértice entrou no caminho (a última vez; NIL = nenhum)
//   caminho  -> o caminho atual, da origem até o vértice de agora: é a pilha da recursão
//               (push_back empilha no fim do vector; pop_back desempilha do fim)
//   cortados -> onde o limite cortou (um vértice pode ser cortado mais de uma vez)
// Devolve ACHOU (o caminho até o destino fica em "caminho"), CORTE (o limite cortou algum ramo)
// ou FALHA (não achou, e nenhum limite maior ajudaria). Sem destino, passe destino = NIL.
// std::map é um dicionário (guarda as chaves em ordem).

#include <algorithm>
#include <map>
#include <string>
#include <vector>

class ProfundidadeLimitada {
public:
    enum Cor { BRANCO, CINZA, PRETO };
    enum Resultado { ACHOU, CORTE, FALHA };
    inline static const std::string NIL = "";               // "nenhum vértice" (o NIL do livro)

    std::map<std::string, std::vector<std::string>> adj;    // adj[u] = os vizinhos de u
    std::map<std::string, Cor> cor;
    std::map<std::string, int> prof;
    std::map<std::string, std::string> pai;
    std::vector<std::string> caminho;
    std::vector<std::string> cortados;

    explicit ProfundidadeLimitada(const std::map<std::string, std::vector<std::string>> &adj) : adj(adj) {}

    Resultado buscar(const std::string &s, const std::string &destino, int limite) {
        for (const auto &[v, vizinhos] : adj) {                 // @cada_vertice
            cor[v] = BRANCO;                                    // @pinta_branco
            pai[v] = NIL;                                       // @inicializar
        }
        return dls(s, destino, limite, 0);                      // @chama_dls
    }

    // Desce no máximo "limite" arestas a partir de u (profundidade = a profundidade de u)
    Resultado dls(const std::string &u, const std::string &destino, int limite, int profundidade) {
        cor[u] = CINZA;                                         // @entrar
        prof[u] = profundidade;                                 // @anota_prof
        caminho.push_back(u);                                   // @empilha
        if (u == destino) {                                     // @testa_destino
            return ACHOU;                                       // @chegou
        }
        if (limite == 0) {                                      // @testa_limite
            caminho.pop_back();                                 // @desempilha_cortado
            cor[u] = PRETO;                                     // @pinta_cortado
            cortados.push_back(u);                              // @corte
            return CORTE;                                       // @devolve_corte
        }
        bool houve_corte = false;                               // @sem_corte
        for (const std::string &v : adj[u]) {                   // @cada_vizinho
            // std::find procura v no caminho, um por um (como o "in" do Python); se não achar,
            // devolve caminho.end()
            if (std::find(caminho.begin(), caminho.end(), v) != caminho.end()) {     // @ignorar_vizinho
                continue;                                       // @pula_vizinho
            }
            pai[v] = u;                                         // @pai_v
            Resultado resultado = dls(v, destino, limite - 1, profundidade + 1);     // @desce
            if (resultado == ACHOU) {                           // @se_achou
                return ACHOU;                                   // @repassa_achou
            }
            if (resultado == CORTE) {                           // @se_cortou
                houve_corte = true;                             // @houve_corte
            }
        }
        caminho.pop_back();                                     // @desempilha
        cor[u] = PRETO;                                         // @subir
        if (houve_corte) {                                      // @se_houve_corte
            return CORTE;                                       // @devolve_corte_de_baixo
        }
        return FALHA;                                           // @devolve_falha
    }
};
