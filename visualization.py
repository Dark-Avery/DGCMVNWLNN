import matplotlib.pyplot as plt
import networkx as nx

def visualize_graph(G, communities, title="Graph Visualization"):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_nodes(G, pos, node_color=list(communities.values()), cmap=plt.cm.tab20, node_size=100)
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_labels(G, pos)
    plt.title(title)
    plt.show()
