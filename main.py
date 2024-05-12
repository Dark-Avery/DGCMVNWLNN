#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This package implements community detection.

Package name is community but refer to python-louvain on pypi
"""

import networkx as nx
import numpy
import unittest
import random
from community_louvain import (
    partition_at_level,
    modularity,
    best_partition,
    generate_dendrogram,
    induced_graph,
    load_binary,
)

for _ in range(10):
    graph = nx.erdos_renyi_graph(50, 0.1)
    part = dict([])
    for node in graph:
        part[node] = 0
    print(modularity(part, graph))
    assert modularity(part, graph) == 0

for _ in range(10):
        size_clique = random.randint(5, 20)
        num_clique = random.randint(5, 20)
        graph = nx.Graph()
        for i in range(num_clique):
            clique_i = nx.complete_graph(size_clique)
            graph = nx.union(graph, clique_i, rename=("", str(i) + "_"))
            if i > 0:
                graph.add_edge(str(i) + "_0", str(i - 1) + "_1")
        graph.add_edge("0_0", str(num_clique - 1) + "_1")
        part = best_partition(graph)

        for clique in range(num_clique):
            part_name = part[str(clique) + "_0"]
            for node in range(size_clique):
                expected = part[str(clique) + "_" + str(node)]
                
                print(part_name, expected)

# __version__ = "0.16"
# __author__ = """Thomas Aynaud (thomas.aynaud@lip6.fr)"""
#    Copyright (C) 2009 by
#    Thomas Aynaud <thomas.aynaud@lip6.fr>
#    All rights reserved.
#    BSD license.
