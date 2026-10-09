class Aresta:
    # Guarda os dois objetos Vertice, e não só os nomes
    # Exemplo: aresta.vertice_origem.nome -> "A" e aresta.vertice_destino.nome -> "B"
    # O nome da aresta é opcional (por exemplo "e1" ou "link SP-RJ"); vazio = sem nome
    # O peso também é opcional (por exemplo 5 ou 2,5: custo, distância, tempo); None = sem peso
    def __init__(self, vertice_origem, vertice_destino, nome="", peso=None):
        self.vertice_origem = vertice_origem
        self.vertice_destino = vertice_destino
        self.nome = nome
        self.peso = peso
