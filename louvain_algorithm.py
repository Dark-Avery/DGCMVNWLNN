import networkx as nx
from collections import defaultdict

def initialize_communities(G):
    communities = {node: f"n_{node}" for node in G.nodes()}
    edge_communities = {edge: f"e_{edge[0]}_{edge[1]}" for edge in G.edges()}
    return communities, edge_communities

def calculate_modularity(G, communities):
    m = G.size(weight='weight')
    degrees = dict(G.degree(weight='weight'))
    modularity_score = 0
    community_dict = defaultdict(list)
    for node, comm in communities.items():
        community_dict[comm].append(node)
    for comm, nodes in community_dict.items():
        intra_edges = G.subgraph(nodes).size(weight='weight')
        total_degree = sum(degrees[n] for n in nodes)
        modularity_score += intra_edges / m - (total_degree / (2 * m))**2
    return modularity_score

def louvain_algorithm(G):
    # Инициализация сообществ и предварительные расчеты
    communities, edge_communities = initialize_communities(G)
    total_links = G.size(weight='weight')
    current_modularity = calculate_modularity(G, communities)
    print(f"Initial modularity: {current_modularity}")
    
    improved = True
    while improved:
        improved = False
        for node in G.nodes():
            best_gain = 0
            best_community = None
            
            # Рассматриваем слияние с сообществами ребер
            for edge in G.edges(node):
                if edge[0] != node and edge[1] != node:  # Убедимся, что рассматриваем ребро, не включающее сам узел
                    mod_gain = calculate_edge_modularity_gain(G, node, edge, communities, total_links, G.degree(weight='weight'))
                    if mod_gain > best_gain:
                        best_gain = mod_gain
                        best_community = edge_communities[edge]
            
            # Рассматриваем слияние с сообществами узлов
            for neighbor in G.neighbors(node):
                mod_gain = calculate_edge_modularity_gain(G, node, (node, neighbor), communities, total_links, G.degree(weight='weight'))
                if mod_gain > best_gain:
                    best_gain = mod_gain
                    best_community = communities[neighbor]
            
            if best_community and best_gain > 0:
                communities[node] = best_community
                improved = True
                current_modularity += best_gain
        
        print(f"Updated modularity: {current_modularity}")
    
    return communities
