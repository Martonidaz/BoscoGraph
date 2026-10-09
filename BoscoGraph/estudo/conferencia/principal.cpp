// Só para os testes (testes_estudo.py): lê grafos da entrada padrão, roda a busca de estudo pedida
// e escreve o estado final, no formato que o teste compara com o do Python. O formato da entrada
// está em testes_estudo.py (entrada_das_traducoes).

#include <cmath>
#include <cstdio>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "a_estrela.cpp"
#include "bellman_ford.cpp"
#include "bidirecional.cpp"
#include "dijkstra.cpp"
#include "floyd_warshall.cpp"
#include "gulosa.cpp"
#include "iterativa.cpp"
#include "kruskal.cpp"
#include "largura.cpp"
#include "limitada.cpp"
#include "prim.cpp"
#include "profundidade.cpp"

// Os números como o teste espera: "inf" para o infinito e inteiros sem casas decimais
static std::string numero(double x) {
    if (std::isinf(x)) {
        return x > 0 ? "inf" : "-inf";
    }
    char texto[64];
    if (x == std::floor(x)) {
        std::snprintf(texto, sizeof texto, "%.0f", x);
    } else {
        std::snprintf(texto, sizeof texto, "%.17g", x);
    }
    return texto;
}

static std::string nome_ou_nil(const std::string &nome) {
    return nome.empty() ? "NIL" : nome;
}

static const char *nome_da_cor(int cor) {
    static const char *NOMES[] = {"Branco", "Cinza", "Preto"};
    return NOMES[cor];
}

// A resposta da busca limitada e do aprofundamento iterativo, como o Python escreve
static const char *nome_do_resultado(int resultado) {
    static const char *NOMES[] = {"achou", "corte", "falha"};
    return NOMES[resultado];
}

static const char *nome_do_lado(int lado) {
    static const char *NOMES[] = {"NIL", "frente", "tras"};
    return NOMES[lado];
}

// Uma lista de nomes numa linha: "caminho A B C" (ou só "caminho" se estiver vazia)
static void escrever_lista(const char *titulo, const std::vector<std::string> &lista) {
    std::cout << titulo;
    for (const std::string &nome : lista) {
        std::cout << " " << nome;
    }
    std::cout << "\n";
}

// O estado final da busca limitada e do aprofundamento iterativo (as duas classes têm os mesmos campos)
template <typename Busca>
static void escrever_limitada(const std::vector<std::string> &nomes, Busca &busca, int resultado) {
    for (const std::string &v : nomes) {
        std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
        std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
        if (busca.prof.count(v) > 0) {
            std::cout << "prof " << v << " " << busca.prof[v] << "\n";
        }
    }
    escrever_lista("caminho", busca.caminho);
    escrever_lista("cortados", busca.cortados);
    std::cout << "resposta " << nome_do_resultado(resultado) << "\n";
}

// As listas com pesos no formato de cada busca (cada classe tem o seu próprio Vizinho)
template <typename Vizinho>
static std::map<std::string, std::vector<Vizinho>> listas(const std::vector<std::string> &nomes,
                                                         const std::vector<std::vector<std::string>> &vizinhos,
                                                         const std::vector<std::vector<double>> &pesos) {
    std::map<std::string, std::vector<Vizinho>> adj;
    for (std::size_t u = 0; u < nomes.size(); u++) {
        std::vector<Vizinho> lista;
        for (std::size_t j = 0; j < vizinhos[u].size(); j++) {
            lista.push_back(Vizinho{vizinhos[u][j], pesos[u][j]});
        }
        adj[nomes[u]] = lista;
    }
    return adj;
}

int main() {
    std::string algoritmo;
    while (std::cin >> algoritmo) {
        int n;
        std::cin >> n;
        std::vector<std::string> nomes(n);
        for (int i = 0; i < n; i++) {
            std::cin >> nomes[i];
        }
        int orientado, numero_da_origem, numero_do_destino;
        std::cin >> orientado >> numero_da_origem >> numero_do_destino;
        std::string origem = nomes[numero_da_origem];
        std::string destino = numero_do_destino >= 0 ? nomes[numero_do_destino] : "";
        std::map<std::string, double> h;
        for (int i = 0; i < n; i++) {
            std::cin >> h[nomes[i]];
        }
        std::vector<std::vector<std::string>> vizinhos(n);
        std::vector<std::vector<double>> pesos(n);
        for (int u = 0; u < n; u++) {
            int k;
            std::cin >> k;
            for (int j = 0; j < k; j++) {
                int v;
                double peso;
                std::cin >> v >> peso;
                vizinhos[u].push_back(nomes[v]);
                pesos[u].push_back(peso);
            }
        }
        int quantos_arcos;
        std::cin >> quantos_arcos;
        std::vector<BellmanFord::Arco> arcos;
        for (int j = 0; j < quantos_arcos; j++) {
            int u, v;
            double peso;
            std::cin >> u >> v >> peso;
            arcos.push_back(BellmanFord::Arco{nomes[u], nomes[v], peso});
        }
        std::vector<std::string> ordem(n);
        for (int i = 0; i < n; i++) {
            int v;
            std::cin >> v;
            ordem[i] = nomes[v];
        }
        // Versão 6: o limite da busca limitada (-1 = nenhum) e, para cada vértice, quem CHEGA nele
        int limite;
        std::cin >> limite;
        std::vector<std::vector<std::string>> vizinhos_tras(n);
        std::vector<std::vector<double>> pesos_tras(n);
        for (int u = 0; u < n; u++) {
            int k;
            std::cin >> k;
            for (int j = 0; j < k; j++) {
                int v;
                double peso;
                std::cin >> v >> peso;
                vizinhos_tras[u].push_back(nomes[v]);
                pesos_tras[u].push_back(peso);
            }
        }
        // Versão 7.3: as arestas uma vez cada, na ordem de criação (só o Kruskal usa)
        int quantas_arestas;
        std::cin >> quantas_arestas;
        std::vector<Kruskal::Aresta> arestas;
        for (int j = 0; j < quantas_arestas; j++) {
            int u, v;
            double peso;
            std::cin >> u >> v >> peso;
            arestas.push_back(Kruskal::Aresta{nomes[u], nomes[v], peso});
        }
        // As listas só com os nomes (a busca limitada e a iterativa não usam os pesos)
        std::map<std::string, std::vector<std::string>> sem_pesos;
        for (int u = 0; u < n; u++) {
            sem_pesos[nomes[u]] = vizinhos[u];
        }

        if (algoritmo == "profundidade") {
            std::map<std::string, std::vector<std::string>> adj;
            for (int u = 0; u < n; u++) {
                adj[nomes[u]] = vizinhos[u];
            }
            BuscaEmProfundidade busca(adj, orientado == 1);
            busca.dfs(ordem);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "d " << v << " " << busca.d[v] << "\n";
                std::cout << "f " << v << " " << busca.f[v] << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
            for (const auto &[aresta, tipo] : busca.tipo) {
                std::cout << "tipo " << aresta.first << " " << aresta.second << " " << tipo << "\n";
            }
        } else if (algoritmo == "largura") {
            BuscaEmLargura busca(listas<BuscaEmLargura::Vizinho>(nomes, vizinhos, pesos));
            busca.bfs(origem);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "d " << v << " " << numero(busca.d[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
        } else if (algoritmo == "dijkstra") {
            Dijkstra busca(listas<Dijkstra::Vizinho>(nomes, vizinhos, pesos));
            busca.dijkstra(origem);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "d " << v << " " << numero(busca.d[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
        } else if (algoritmo == "bellman_ford") {
            BellmanFord busca(nomes, arcos);
            bool resposta = busca.bellman_ford(origem);
            for (const std::string &v : nomes) {
                std::cout << "d " << v << " " << numero(busca.d[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
            std::cout << "resposta " << (resposta ? "true" : "false") << "\n";
        } else if (algoritmo == "gulosa") {
            BuscaGulosa busca(listas<BuscaGulosa::Vizinho>(nomes, vizinhos, pesos), h);
            bool resposta = busca.buscar(origem, destino);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
            std::cout << "resposta " << (resposta ? "true" : "false") << "\n";
        } else if (algoritmo == "a_estrela") {
            AEstrela busca(listas<AEstrela::Vizinho>(nomes, vizinhos, pesos), h);
            bool resposta = busca.buscar(origem, destino);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "g " << v << " " << numero(busca.g[v]) << "\n";
                std::cout << "f " << v << " " << numero(busca.f[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
            std::cout << "resposta " << (resposta ? "true" : "false") << "\n";
        } else if (algoritmo == "limitada") {
            ProfundidadeLimitada busca(sem_pesos);
            int resultado = busca.buscar(origem, destino, limite);
            escrever_limitada(nomes, busca, resultado);
        } else if (algoritmo == "iterativa") {
            AprofundamentoIterativo busca(sem_pesos);
            int resultado = busca.buscar(origem, destino);
            escrever_limitada(nomes, busca, resultado);
        } else if (algoritmo == "bidirecional") {
            BuscaBidirecional busca(listas<BuscaBidirecional::Vizinho>(nomes, vizinhos, pesos),
                                    listas<BuscaBidirecional::Vizinho>(nomes, vizinhos_tras, pesos_tras));
            bool resposta = busca.buscar(origem, destino);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "lado " << v << " " << nome_do_lado(busca.lado[v]) << "\n";
                std::cout << "d " << v << " " << numero(busca.d[v]) << "\n";
                std::cout << "d_tras " << v << " " << numero(busca.d_tras[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
                std::cout << "pai_tras " << v << " " << nome_ou_nil(busca.pai_tras[v]) << "\n";
            }
            if (!busca.encontro.first.empty()) {
                std::cout << "encontro " << busca.encontro.first << " " << busca.encontro.second << "\n";
            }
            std::cout << "resposta " << (resposta ? "true" : "false") << "\n";
        } else if (algoritmo == "floyd_warshall") {
            std::vector<FloydWarshall::Arco> arcos_do_floyd;
            for (const BellmanFord::Arco &arco : arcos) {
                arcos_do_floyd.push_back(FloydWarshall::Arco{arco.u, arco.v, arco.peso});
            }
            FloydWarshall busca(nomes, arcos_do_floyd);
            bool resposta = busca.floyd_warshall();
            for (const std::string &i : nomes) {
                for (const std::string &j : nomes) {
                    std::cout << "d " << i << " " << j << " " << numero(busca.d[i][j]) << "\n";
                    std::cout << "pi " << i << " " << j << " " << nome_ou_nil(busca.pi[i][j]) << "\n";
                }
            }
            std::cout << "resposta " << (resposta ? "true" : "false") << "\n";
        } else if (algoritmo == "prim") {
            Prim busca(listas<Prim::Vizinho>(nomes, vizinhos, pesos));
            busca.prim(ordem);
            for (const std::string &v : nomes) {
                std::cout << "cor " << v << " " << nome_da_cor(busca.cor[v]) << "\n";
                std::cout << "chave " << v << " " << numero(busca.chave[v]) << "\n";
                std::cout << "pai " << v << " " << nome_ou_nil(busca.pai[v]) << "\n";
            }
        } else if (algoritmo == "kruskal") {
            Kruskal busca(nomes, arestas);
            busca.kruskal();
            for (const std::string &v : nomes) {
                std::cout << "conjunto " << v << " " << busca.conjunto[v] << "\n";
            }
            for (std::size_t i = 0; i < busca.arvore.size(); i++) {
                const Kruskal::Aresta &aresta = busca.arvore[i];
                std::cout << "arvore " << i << " " << aresta.u << " " << aresta.v << " " << numero(aresta.peso) << "\n";
            }
        } else {
            throw std::invalid_argument("busca desconhecida: " + algoritmo);
        }
        std::cout << "fim\n";
    }
    return 0;
}
