import networkx as nx
from louvain_algorithm import louvain_algorithm
from visualization import visualize_graph

def main():
    G = nx.karate_club_graph()  # Загрузка или создание графа
    communities = louvain_algorithm(G)  # Выполнение алгоритма кластеризации
    visualize_graph(G, communities)  # Визуализация результатов

if __name__ == "__main__":
    main()
