from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets
from pyvis.network import Network
import networkx as nx
import json
import sys
import os
import mod_community_louvain
from collections import defaultdict

class GraphVisualization(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graph Visualization with Clustering")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.graph_button = QtWidgets.QPushButton("Select Graph File")
        self.graph_button.clicked.connect(self.select_graph_file)
        self.layout.addWidget(self.graph_button)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(1)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_graph)
        self.layout.addWidget(self.slider)

        self.label = QtWidgets.QLabel("Clustering Level: 1")
        self.layout.addWidget(self.label)

        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.web_view)

        self.graph_file_path = None
        self.clusters = None
        self.html_file_path = os.path.abspath("graph.html")

    def select_graph_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Graph File", "", 
                                                             "All Supported Files (*.adjlist *.multiadjlist *.dot *.edgelist *.gexf *.gml *.graphml *.json *.leda *.sg6 *.pajek *.mtx);;All Files (*)", 
                                                             options=options)
        if file_name:
            self.graph_file_path = file_name
            self.load_graph()
            # self.perform_clustering()
            self.update_graph()

    def load_graph(self):
        if self.graph_file_path:
            ext = os.path.splitext(self.graph_file_path)[1].lower()
            if ext == '.adjlist':
                self.G = nx.read_adjlist(self.graph_file_path, encoding='utf-8')
            elif ext == '.multiadjlist':
                self.G = nx.read_multiline_adjlist(self.graph_file_path, encoding='utf-8')
            elif ext == '.dot':
                self.G = nx.nx_pydot.read_dot(self.graph_file_path)
            elif ext == '.edgelist':
                self.G = nx.read_edgelist(self.graph_file_path, encoding='utf-8')
            elif ext == '.gexf':
                self.G = nx.read_gexf(self.graph_file_path)
            elif ext == '.gml':
                self.G = nx.read_gml(self.graph_file_path, encoding='utf-8')
            elif ext == '.graphml':
                self.G = nx.read_graphml(self.graph_file_path)
            elif ext == '.json':
                with open(self.graph_file_path, encoding='utf-8') as f:
                    self.G = nx.readwrite.json_graph.node_link_graph(json.load(f))
            elif ext == '.leda':
                self.G = nx.read_leda(self.graph_file_path, encoding='utf-8')
            elif ext == '.sg6':
                self.G = nx.read_sparse6(self.graph_file_path, encoding='utf-8')
            elif ext == '.pajek':
                self.G = nx.read_pajek(self.graph_file_path, encoding='utf-8')
            elif ext == '.mtx':
                self.G = nx.read_matrix_market(self.graph_file_path)
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
            self.G = nx.Graph(self.G)
            # print("Graph loaded successfully.")

    def update_graph(self):
        if self.G:
            level = self.slider.value()
            self.label.setText(f"Clustering Level: {level}")

            net = Network(notebook=True, cdn_resources='in_line')
            
            # for node in self.G.nodes():
            #     self.G.nodes[node]['group'] = self.clusters[node] % level

            net.set_options("""
            var options = {
            "nodes": {
                "font": {
                "size": 12
                }
            },
            "edges": {
                "color": {
                "inherit": true
                },
                "smooth": false
            },
            "physics": {
                "forceAtlas2Based": {
                "gravitationalConstant": -26,
                "centralGravity": 0.005,
                "springLength": 230,
                "springConstant": 0.18
                },
                "maxVelocity": 146,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {
                "enabled": true,
                "iterations": 1000,
                "updateInterval": 25,
                "onlyDynamicEdges": false,
                "fit": true
                }
            }
            }
            """)

            partition = mod_community_louvain.best_partition(self.G, level=level)

            community_map = defaultdict(list)
            for node, community_id in partition.items():
                community_map[community_id].append(node)

            # Добавляем узлы в pyvis сеть
            for community_id, nodes in community_map.items():
                net.add_node(f"Community {community_id + 1}",
                            title=f"Community {community_id + 1} (Size: {len(nodes)})", 
                            size=20)  # Фиксированный размер узлов
                
            max_weight = 1
            edge_attributes = defaultdict(lambda: {'weight': 0, 'latency': 0, 'bandwidth': float("inf"), 'reliability': 1})
            for com1, nodes1 in community_map.items():
                for com2, nodes2 in community_map.items():
                    if com1 < com2:
                        for u in nodes1:
                            for v in nodes2:
                                if self.G.has_edge(u, v):
                                    edge_data = self.G[u][v]
                                    latency = (edge_attributes[(com1, com2)]['latency'] + edge_data['latency']) / 2
                                    bandwidth = min(edge_attributes[(com1, com2)]['bandwidth'], edge_data['bandwidth'])
                                    reliability = edge_attributes[(com1, com2)]['reliability'] * edge_data['reliability']
                                    edge_attributes[(com1, com2)]['weight'] = (latency + 1 / bandwidth) * (1 - reliability)
                                    edge_attributes[(com1, com2)]['latency'] = latency
                                    edge_attributes[(com1, com2)]['bandwidth'] = bandwidth
                                    edge_attributes[(com1, com2)]['reliability'] = reliability
                                    if edge_attributes[(com1, com2)]['weight'] > max_weight:
                                        max_weight = edge_attributes[(com1, com2)]['weight']

            for (com1, com2), attrs in edge_attributes.items():
                net.add_edge(f"Community {com1 + 1}", f"Community {com2 + 1}", value=attrs['weight'],
                            title=f"Weight: {attrs['weight']}, Latency: {attrs['latency']}, bandwidth: {attrs['bandwidth']}, reliability: {attrs['reliability']}")
            
            self.save_graph(net)

            self.web_view.setUrl(QtCore.QUrl.fromLocalFile(self.html_file_path))

    def save_graph(self, net):
        html_content = net.generate_html()
        with open(self.html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GraphVisualization()
    window.show()
    sys.exit(app.exec_())
