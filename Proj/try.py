import networkx as nx
import highOrderGraph
# import re
# from gurobipy import *
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
 
F = highOrderGraph.DiGraph(8)
F.addWeights()
F.writeFile("out3.txt")
 
lpm = highOrderGraph.LPMaker(F,'try')
# lpm.createLP()
# lpm.solveLP()
lpm.createWeightReductionLP()
lpm.solveWeightReductionLP()

# edges = F.graph.edges()
# print(edges)
# 
# l = gurobipy.tuplelist(edges)
# print(l.select(0,'*'))
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

# def allNonEmptySubsets(feature):
#     if len(feature) == 0:
#         return
#     out = [[]]
#     for e in feature:
#         out += [x+[e] for x in out]
#     out.remove([])
#     out2 = []
#     for e in out:
#         out2.append( tuple(e) )
#     return out2
# 
# f = ((1,3),(3,4),(5,6))
# print(allNonEmptySubsets(f))