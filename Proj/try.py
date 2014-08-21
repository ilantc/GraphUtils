import networkx as nx
import highOrderGraph
import re

# G=nx.DiGraph()
# G.add_nodes_from(range(5))
#  
# print(G.nodes())
# print(G.edges())
# for e in nx.non_edges(G):
#     print(e)
#     G.add_edges_from([e])
# G.add_edges_from(nx.non_edges(G))
# 
# for (u,v) in G.edges():
#     print("U is " + str(u) + ", V is " + str(v))
  
# print(G.edges())
 
F = highOrderGraph.DiGraph(4,"out2.txt")
F.addWeights()
F.writeFile("out.txt")

# s = "(1,2),(3,5),4.25"
# m = re.findall("\(\d+,\d+\)",s)
# v = re.findall("\),(\d+[.\d+]*)",s)
# if m:
#     feature = []
#     for e in m:
#         t = tuple(int(v) for v in re.findall("[0-9]+", e))
#         feature.append(t)
#     print(feature)
#     val = float(v[0])
#     print(val)
# print(v)



