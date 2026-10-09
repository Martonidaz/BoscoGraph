import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

// Só para os testes (testes_estudo.py): lê grafos da entrada padrão, roda a busca de estudo pedida
// e escreve o estado final, no formato que o teste compara com o do Python. O formato da entrada
// está em testes_estudo.py (entrada_das_traducoes).
public class Principal {
    static String[] fichas;
    static int posicao = 0;
    static PrintStream saida;

    static String ler() {
        return fichas[posicao++];
    }

    static int lerInteiro() {
        return Integer.parseInt(ler());
    }

    static double lerNumero() {
        return Double.parseDouble(ler());
    }

    // Os números como o teste espera: "inf" para o infinito e inteiros sem ".0"
    static String numero(double x) {
        if (Double.isInfinite(x)) {
            return x > 0 ? "inf" : "-inf";
        }
        if (x == Math.rint(x)) {
            return String.valueOf((long) x);
        }
        return String.valueOf(x);
    }

    static String nomeOuNil(String nome) {
        return nome == null ? "NIL" : nome;
    }

    public static void main(String[] argumentos) throws IOException {
        saida = new PrintStream(new FileOutputStream(FileDescriptor.out), true, StandardCharsets.UTF_8);
        String texto = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        fichas = texto.isEmpty() ? new String[0] : texto.split("\\s+");
        while (posicao < fichas.length) {
            String algoritmo = ler();
            int n = lerInteiro();
            String[] nomes = new String[n];
            for (int i = 0; i < n; i++) {
                nomes[i] = ler();
            }
            boolean direcionado = lerInteiro() == 1;
            String origem = nomes[lerInteiro()];
            int numeroDoDestino = lerInteiro();
            String destino = numeroDoDestino >= 0 ? nomes[numeroDoDestino] : null;
            Map<String, Double> h = new LinkedHashMap<>();
            for (int i = 0; i < n; i++) {
                h.put(nomes[i], lerNumero());
            }
            List<List<String>> vizinhos = new ArrayList<>();
            List<List<Double>> pesos = new ArrayList<>();
            for (int u = 0; u < n; u++) {
                int k = lerInteiro();
                vizinhos.add(new ArrayList<>());
                pesos.add(new ArrayList<>());
                for (int j = 0; j < k; j++) {
                    vizinhos.get(u).add(nomes[lerInteiro()]);
                    pesos.get(u).add(lerNumero());
                }
            }
            List<BellmanFord.Arco> arcos = new ArrayList<>();
            int quantosArcos = lerInteiro();
            for (int j = 0; j < quantosArcos; j++) {
                String u = nomes[lerInteiro()];
                String v = nomes[lerInteiro()];
                arcos.add(new BellmanFord.Arco(u, v, lerNumero()));
            }
            List<String> ordem = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                ordem.add(nomes[lerInteiro()]);
            }
            // Versão 6 (vêm em TODAS as buscas): o limite da busca limitada (-1 = nenhum) e, para cada
            // vértice v, quem CHEGA em v (a lista ao contrário da busca bidirecional)
            int limite = lerInteiro();
            List<List<String>> vizinhosTras = new ArrayList<>();
            List<List<Double>> pesosTras = new ArrayList<>();
            for (int v = 0; v < n; v++) {
                int k = lerInteiro();
                vizinhosTras.add(new ArrayList<>());
                pesosTras.add(new ArrayList<>());
                for (int j = 0; j < k; j++) {
                    vizinhosTras.get(v).add(nomes[lerInteiro()]);
                    pesosTras.get(v).add(lerNumero());
                }
            }
            // Versão 7.3: as arestas uma vez cada, na ordem de criação (só o Kruskal usa)
            List<Kruskal.Aresta> arestas = new ArrayList<>();
            int quantasArestas = lerInteiro();
            for (int j = 0; j < quantasArestas; j++) {
                String u = nomes[lerInteiro()];
                String v = nomes[lerInteiro()];
                arestas.add(new Kruskal.Aresta(u, v, lerNumero()));
            }
            rodar(algoritmo, nomes, direcionado, origem, destino, h, vizinhos, pesos, arcos, ordem, limite,
                  vizinhosTras, pesosTras, arestas);
            saida.println("fim");
        }
    }

    // A busca limitada e o aprofundamento iterativo escrevem as mesmas informações
    static void escreverCaminho(String[] nomes, Map<String, String> cor, Map<String, String> pai,
                                Map<String, Integer> prof, List<String> caminho, List<String> cortados,
                                String resposta) {
        for (String v : nomes) {
            saida.println("cor " + v + " " + cor.get(v));
            saida.println("pai " + v + " " + nomeOuNil(pai.get(v)));
            if (prof.containsKey(v)) {
                saida.println("prof " + v + " " + prof.get(v));
            }
        }
        saida.println(caminho.isEmpty() ? "caminho" : "caminho " + String.join(" ", caminho));
        saida.println(cortados.isEmpty() ? "cortados" : "cortados " + String.join(" ", cortados));
        saida.println("resposta " + resposta);
    }

    static void rodar(String algoritmo, String[] nomes, boolean direcionado, String origem, String destino,
                      Map<String, Double> h, List<List<String>> vizinhos, List<List<Double>> pesos,
                      List<BellmanFord.Arco> arcos, List<String> ordem, int limite,
                      List<List<String>> vizinhosTras, List<List<Double>> pesosTras, List<Kruskal.Aresta> arestas) {
        int n = nomes.length;
        switch (algoritmo) {
            case "profundidade" -> {
                Map<String, List<String>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    adj.put(nomes[u], vizinhos.get(u));
                }
                BuscaEmProfundidade busca = new BuscaEmProfundidade(adj, direcionado);
                busca.dfs(ordem);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("d " + v + " " + busca.d.get(v));
                    saida.println("f " + v + " " + busca.f.get(v));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
                for (Map.Entry<List<String>, String> item : busca.tipo.entrySet()) {
                    saida.println("tipo " + item.getKey().get(0) + " " + item.getKey().get(1) + " " + item.getValue());
                }
            }
            case "largura" -> {
                Map<String, List<BuscaEmLargura.Vizinho>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<BuscaEmLargura.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new BuscaEmLargura.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                }
                BuscaEmLargura busca = new BuscaEmLargura(adj);
                busca.bfs(origem);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("d " + v + " " + numero(busca.d.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
            }
            case "dijkstra" -> {
                Map<String, List<Dijkstra.Vizinho>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<Dijkstra.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new Dijkstra.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                }
                Dijkstra busca = new Dijkstra(adj);
                busca.dijkstra(origem);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("d " + v + " " + numero(busca.d.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
            }
            case "bellman_ford" -> {
                BellmanFord busca = new BellmanFord(List.of(nomes), arcos);
                boolean resposta = busca.bellmanFord(origem);
                for (String v : nomes) {
                    saida.println("d " + v + " " + numero(busca.d.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
                saida.println("resposta " + resposta);
            }
            case "gulosa" -> {
                Map<String, List<BuscaGulosa.Vizinho>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<BuscaGulosa.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new BuscaGulosa.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                }
                BuscaGulosa busca = new BuscaGulosa(adj, h);
                boolean resposta = busca.buscar(origem, destino);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
                saida.println("resposta " + resposta);
            }
            case "a_estrela" -> {
                Map<String, List<AEstrela.Vizinho>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<AEstrela.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new AEstrela.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                }
                AEstrela busca = new AEstrela(adj, h);
                boolean resposta = busca.buscar(origem, destino);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("g " + v + " " + numero(busca.g.get(v)));
                    saida.println("f " + v + " " + numero(busca.f.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
                saida.println("resposta " + resposta);
            }
            case "limitada" -> {
                Map<String, List<String>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    adj.put(nomes[u], vizinhos.get(u));
                }
                ProfundidadeLimitada busca = new ProfundidadeLimitada(adj);
                String resposta = busca.buscar(origem, destino, limite);
                escreverCaminho(nomes, busca.cor, busca.pai, busca.prof, busca.caminho, busca.cortados, resposta);
            }
            case "iterativa" -> {
                Map<String, List<String>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    adj.put(nomes[u], vizinhos.get(u));
                }
                AprofundamentoIterativo busca = new AprofundamentoIterativo(adj);
                String resposta = busca.buscar(origem, destino);
                escreverCaminho(nomes, busca.cor, busca.pai, busca.prof, busca.caminho, busca.cortados, resposta);
            }
            case "bidirecional" -> {
                Map<String, List<BuscaBidirecional.Vizinho>> adj = new LinkedHashMap<>();
                Map<String, List<BuscaBidirecional.Vizinho>> adjTras = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<BuscaBidirecional.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new BuscaBidirecional.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                    List<BuscaBidirecional.Vizinho> listaTras = new ArrayList<>();
                    for (int j = 0; j < vizinhosTras.get(u).size(); j++) {
                        listaTras.add(new BuscaBidirecional.Vizinho(vizinhosTras.get(u).get(j),
                                                                    pesosTras.get(u).get(j)));
                    }
                    adjTras.put(nomes[u], listaTras);
                }
                BuscaBidirecional busca = new BuscaBidirecional(adj, adjTras);
                boolean resposta = busca.buscar(origem, destino);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("lado " + v + " " + nomeOuNil(busca.lado.get(v)));
                    saida.println("d " + v + " " + numero(busca.d.get(v)));
                    saida.println("d_tras " + v + " " + numero(busca.dTras.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                    saida.println("pai_tras " + v + " " + nomeOuNil(busca.paiTras.get(v)));
                }
                if (busca.encontro != null) {
                    saida.println("encontro " + busca.encontro.get(0) + " " + busca.encontro.get(1));
                }
                saida.println("resposta " + resposta);
            }
            case "floyd_warshall" -> {
                // Os mesmos arcos do Bellman-Ford, no tipo Arco do Floyd-Warshall
                List<FloydWarshall.Arco> arcosDoFloyd = new ArrayList<>();
                for (BellmanFord.Arco arco : arcos) {
                    arcosDoFloyd.add(new FloydWarshall.Arco(arco.u(), arco.v(), arco.peso()));
                }
                FloydWarshall busca = new FloydWarshall(List.of(nomes), arcosDoFloyd);
                boolean resposta = busca.floydWarshall();
                for (String i : nomes) {
                    for (String j : nomes) {
                        saida.println("d " + i + " " + j + " " + numero(busca.d.get(i).get(j)));
                        saida.println("pi " + i + " " + j + " " + nomeOuNil(busca.pi.get(i).get(j)));
                    }
                }
                saida.println("resposta " + resposta);
            }
            case "prim" -> {
                Map<String, List<Prim.Vizinho>> adj = new LinkedHashMap<>();
                for (int u = 0; u < n; u++) {
                    List<Prim.Vizinho> lista = new ArrayList<>();
                    for (int j = 0; j < vizinhos.get(u).size(); j++) {
                        lista.add(new Prim.Vizinho(vizinhos.get(u).get(j), pesos.get(u).get(j)));
                    }
                    adj.put(nomes[u], lista);
                }
                Prim busca = new Prim(adj);
                busca.prim(ordem);
                for (String v : nomes) {
                    saida.println("cor " + v + " " + busca.cor.get(v));
                    saida.println("chave " + v + " " + numero(busca.chave.get(v)));
                    saida.println("pai " + v + " " + nomeOuNil(busca.pai.get(v)));
                }
            }
            case "kruskal" -> {
                Kruskal busca = new Kruskal(List.of(nomes), arestas);
                busca.kruskal();
                for (String v : nomes) {
                    saida.println("conjunto " + v + " " + busca.conjunto.get(v));
                }
                for (int i = 0; i < busca.arvore.size(); i++) {
                    Kruskal.Aresta aresta = busca.arvore.get(i);
                    saida.println("arvore " + i + " " + aresta.u() + " " + aresta.v() + " " + numero(aresta.peso()));
                }
            }
            default -> throw new IllegalArgumentException("busca desconhecida: " + algoritmo);
        }
    }
}
