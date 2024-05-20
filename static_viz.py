import networkx as nx
import json
import sys
import os
import mod_community_louvain
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict


def load_graph(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext == '.adjlist':
        G = nx.read_adjlist(path, encoding='utf-8')
    elif ext == '.multiadjlist':
        G = nx.read_multiline_adjlist(path, encoding='utf-8')
    elif ext == '.dot':
        G = nx.nx_pydot.read_dot(path)
    elif ext == '.edgelist':
        G = nx.read_edgelist(path, encoding='utf-8')
    elif ext == '.gexf':
        G = nx.read_gexf(path)
    elif ext == '.gml':
        G = nx.read_gml(path, encoding='utf-8')
    elif ext == '.graphml':
        G = nx.read_graphml(path)
    elif ext == '.json':
        with open(path, encoding='utf-8') as f:
            G = nx.readwrite.json_graph.node_link_graph(json.load(f))
    elif ext == '.leda':
        G = nx.read_leda(path, encoding='utf-8')
    elif ext == '.sg6':
        G = nx.read_sparse6(path, encoding='utf-8')
    elif ext == '.pajek':
        G = nx.read_pajek(path, encoding='utf-8')
    elif ext == '.mtx':
        G = nx.read_matrix_market(path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    G = nx.Graph(G)
    return G

def vizualize_graph(G, level):
    partition = mod_community_louvain.best_partition(G, level=level)

    cluster_graph = nx.Graph()
    cluster_map = defaultdict(list)

    for node, cluster in partition.items():
        cluster_map[cluster].append(node)

    # Create a node for each cluster
    for cluster_id, nodes in cluster_map.items():
        cluster_graph.add_node(cluster_id, size=len(nodes))

    # Create edges between clusters
    for cluster_id, nodes in cluster_map.items():
        for node in nodes:
            for neighbor in G.neighbors(node):
                neighbor_cluster = partition[neighbor]
                if cluster_id != neighbor_cluster:
                    if cluster_graph.has_edge(cluster_id, neighbor_cluster):
                        cluster_graph[cluster_id][neighbor_cluster]['weight'] += 0.005
                    else:
                        cluster_graph.add_edge(cluster_id, neighbor_cluster, weight=1)

    pos = nx.spring_layout(cluster_graph)

    plt.figure(figsize=(12, 8))

    # Draw nodes with sizes proportional to the number of original nodes in each cluster
    sizes = [cluster_graph.nodes[cluster]['size'] * 1.1 for cluster in cluster_graph.nodes]
    nx.draw_networkx_nodes(cluster_graph, pos, node_size=sizes, node_color='lightblue')

    # Draw edges with widths proportional to their weights
    edges = cluster_graph.edges(data=True)
    weights = [edge[2]['weight'] for edge in edges]
    nx.draw_networkx_edges(cluster_graph, pos, edgelist=cluster_graph.edges(), width=weights)

    nx.draw_networkx_labels(cluster_graph, pos, font_size=12)

    plt.title(f"Graph Visualization with Clustering Level: {level}")
    plt.savefig('clustered_graph.png')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python static_viz.py <graph_file> <clustering_level>")
        sys.exit(1)
    G = load_graph(sys.argv[1])
    vizualize_graph(G, int(sys.argv[2]))
    
