// Só para os testes (testes_estudo.py): lê grafos da entrada padrão, roda a busca de estudo pedida
// e escreve o estado final, no formato que o teste compara com o do Python. O formato da entrada
// está em testes_estudo.py (entrada_das_traducoes).

const fs = require("fs");
const path = require("path");

const { BuscaEmProfundidade } = require(path.join(__dirname, "profundidade.js"));
const { BuscaEmLargura } = require(path.join(__dirname, "largura.js"));
const { Dijkstra } = require(path.join(__dirname, "dijkstra.js"));
const { BellmanFord } = require(path.join(__dirname, "bellman_ford.js"));
const { BuscaGulosa } = require(path.join(__dirname, "gulosa.js"));
const { AEstrela } = require(path.join(__dirname, "a_estrela.js"));
const { ProfundidadeLimitada } = require(path.join(__dirname, "limitada.js"));
const { AprofundamentoIterativo } = require(path.join(__dirname, "iterativa.js"));
const { BuscaBidirecional } = require(path.join(__dirname, "bidirecional.js"));
const { FloydWarshall } = require(path.join(__dirname, "floyd_warshall.js"));
const { Prim } = require(path.join(__dirname, "prim.js"));
const { Kruskal } = require(path.join(__dirname, "kruskal.js"));

const fichas = fs.readFileSync(0, "utf8").split(/\s+/).filter((ficha) => ficha.length > 0);
let posicao = 0;
const ler = () => fichas[posicao++];
const lerNumero = () => Number(ler());
const linhas = [];

// Os números como o teste espera: "inf" para o infinito e inteiros sem casas decimais
function numero(x) {
    if (x === Infinity) {
        return "inf";
    }
    if (x === -Infinity) {
        return "-inf";
    }
    return String(x);
}

const nomeOuNil = (nome) => (nome === null ? "NIL" : nome);

while (posicao < fichas.length) {
    const algoritmo = ler();
    const n = lerNumero();
    const nomes = [];
    for (let i = 0; i < n; i++) {
        nomes.push(ler());
    }
    const direcionado = lerNumero() === 1;
    const origem = nomes[lerNumero()];
    const numeroDoDestino = lerNumero();
    const destino = numeroDoDestino >= 0 ? nomes[numeroDoDestino] : null;
    const h = new Map();
    for (let i = 0; i < n; i++) {
        h.set(nomes[i], lerNumero());
    }
    const vizinhos = new Map();
    const comPesos = new Map();
    for (let u = 0; u < n; u++) {
        const k = lerNumero();
        vizinhos.set(nomes[u], []);
        comPesos.set(nomes[u], []);
        for (let j = 0; j < k; j++) {
            const v = nomes[lerNumero()];
            const peso = lerNumero();
            vizinhos.get(nomes[u]).push(v);
            comPesos.get(nomes[u]).push([v, peso]);
        }
    }
    const arcos = [];
    const quantosArcos = lerNumero();
    for (let j = 0; j < quantosArcos; j++) {
        const u = nomes[lerNumero()];
        const v = nomes[lerNumero()];
        arcos.push([u, v, lerNumero()]);
    }
    const ordem = [];
    for (let i = 0; i < n; i++) {
        ordem.push(nomes[lerNumero()]);
    }
    // Versão 6 (vêm em TODAS as buscas): o limite da busca limitada (-1 = nenhum) e, para cada
    // vértice v, quem CHEGA em v (a lista ao contrário da busca bidirecional)
    const limite = lerNumero();
    const comPesosTras = new Map();
    for (let v = 0; v < n; v++) {
        const k = lerNumero();
        comPesosTras.set(nomes[v], []);
        for (let j = 0; j < k; j++) {
            const u = nomes[lerNumero()];
            const peso = lerNumero();
            comPesosTras.get(nomes[v]).push([u, peso]);
        }
    }
    // Versão 7.3: as arestas uma vez cada, na ordem de criação (só o Kruskal usa)
    const arestas = [];
    const quantasArestas = lerNumero();
    for (let j = 0; j < quantasArestas; j++) {
        const u = nomes[lerNumero()];
        const v = nomes[lerNumero()];
        arestas.push([u, v, lerNumero()]);
    }

    if (algoritmo === "profundidade") {
        const busca = new BuscaEmProfundidade(vizinhos, direcionado);
        busca.dfs(ordem);
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`d ${v} ${busca.d.get(v)}`);
            linhas.push(`f ${v} ${busca.f.get(v)}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
        for (const [chave, tipo] of busca.tipo) {
            const [u, v] = JSON.parse(chave);
            linhas.push(`tipo ${u} ${v} ${tipo}`);
        }
    } else if (algoritmo === "largura" || algoritmo === "dijkstra") {
        const busca = algoritmo === "largura" ? new BuscaEmLargura(comPesos) : new Dijkstra(comPesos);
        if (algoritmo === "largura") {
            busca.bfs(origem);
        } else {
            busca.dijkstra(origem);
        }
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`d ${v} ${numero(busca.d.get(v))}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
    } else if (algoritmo === "bellman_ford") {
        const busca = new BellmanFord(nomes, arcos);
        const resposta = busca.bellmanFord(origem);
        for (const v of nomes) {
            linhas.push(`d ${v} ${numero(busca.d.get(v))}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "gulosa") {
        const busca = new BuscaGulosa(comPesos, h);
        const resposta = busca.buscar(origem, destino);
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "a_estrela") {
        const busca = new AEstrela(comPesos, h);
        const resposta = busca.buscar(origem, destino);
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`g ${v} ${numero(busca.g.get(v))}`);
            linhas.push(`f ${v} ${numero(busca.f.get(v))}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "limitada" || algoritmo === "iterativa") {
        let busca;
        let resposta;
        if (algoritmo === "limitada") {
            busca = new ProfundidadeLimitada(vizinhos);
            resposta = busca.buscar(origem, destino, limite);
        } else {
            busca = new AprofundamentoIterativo(vizinhos);
            resposta = busca.buscar(origem, destino);
        }
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
            if (busca.prof.has(v)) {
                linhas.push(`prof ${v} ${busca.prof.get(v)}`);
            }
        }
        linhas.push(["caminho", ...busca.caminho].join(" "));
        linhas.push(["cortados", ...busca.cortados].join(" "));
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "bidirecional") {
        const busca = new BuscaBidirecional(comPesos, comPesosTras);
        const resposta = busca.buscar(origem, destino);
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`lado ${v} ${nomeOuNil(busca.lado.get(v))}`);
            linhas.push(`d ${v} ${numero(busca.d.get(v))}`);
            linhas.push(`d_tras ${v} ${numero(busca.dTras.get(v))}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
            linhas.push(`pai_tras ${v} ${nomeOuNil(busca.paiTras.get(v))}`);
        }
        if (busca.encontro !== null) {
            linhas.push(`encontro ${busca.encontro[0]} ${busca.encontro[1]}`);
        }
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "floyd_warshall") {
        const busca = new FloydWarshall(nomes, arcos);
        const resposta = busca.floydWarshall();
        for (const i of nomes) {
            for (const j of nomes) {
                linhas.push(`d ${i} ${j} ${numero(busca.d.get(i).get(j))}`);
                linhas.push(`pi ${i} ${j} ${nomeOuNil(busca.pi.get(i).get(j))}`);
            }
        }
        linhas.push(`resposta ${resposta}`);
    } else if (algoritmo === "prim") {
        const busca = new Prim(comPesos);
        busca.prim(ordem);
        for (const v of nomes) {
            linhas.push(`cor ${v} ${busca.cor.get(v)}`);
            linhas.push(`chave ${v} ${numero(busca.chave.get(v))}`);
            linhas.push(`pai ${v} ${nomeOuNil(busca.pai.get(v))}`);
        }
    } else if (algoritmo === "kruskal") {
        const busca = new Kruskal(nomes, arestas);
        busca.kruskal();
        for (const v of nomes) {
            linhas.push(`conjunto ${v} ${busca.conjunto.get(v)}`);
        }
        busca.arvore.forEach(([u, v, peso], i) => linhas.push(`arvore ${i} ${u} ${v} ${numero(peso)}`));
    } else {
        throw new Error(`busca desconhecida: ${algoritmo}`);
    }
    linhas.push("fim");
}

process.stdout.write(linhas.join("\n") + "\n");
