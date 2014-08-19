import networkx as nx
G=nx.DiGraph()
G.add_node("spam")
G.add_edge(1,2)
print(G.nodes())
print(G.edges())
# for e in nx.non_edges(G):
#     print(e)
#     G.add_edges_from([e])
G.add_edges_from(nx.non_edges(G))
# while i.has_next():
#     e = i.next()
#     print(e)
#     G.add_edge(e)

print(G.edges())
