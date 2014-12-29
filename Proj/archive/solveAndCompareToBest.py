# import networkx as nx
import highOrderGraph
import xlsxwriter as xw
import math
from os import listdir
from os.path import isfile, join
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
proj = False
allfiles = [ f for f in listdir(".") if isfile(join(".",f)) ]
print("num files = " + str(len(allfiles)));
allfiles = ["output_0.txt"]
    
def solveInstance(filename,proj):
    filesToSkip = ["_av.txt","gurobi.log","model1.lp","stat.txt"];
    if (filesToSkip.count(filename) > 0):
        return;
    G = highOrderGraph.DiGraph(None,filename)
    G.addWeights()
     
    lpm = highOrderGraph.LPMaker(G,'highOrder','output_0.lp')
    lpm.createLP(proj)
    lpm.solveLP()
    bestTree = {};
    
    for (u,v) in lpm.g.graph.edges():
        if lpm.LPVars[((u,v),)].x > 0:
            bestTree[(u,v)] = 1;

    lpm2 = highOrderGraph.LPMaker(G,'reductionLp','reduction.lp')
    
    lpm2.createWeightReductionLPWithSetGraph(proj, bestTree)
    lpm2.solveWeightReductionLPWithSetGraph()
#     lpm2.createWeightReductionLP(proj)
#     lpm2.solveWeightReductionLP()
#     workbook = xw.Workbook('%s_out.xlsx'%(filename))
#     worksheet = workbook.add_worksheet()
#     row = 0
#     col = 0
    tempOutFile = open("_av.txt", "w")
    statFile = open("stat.txt", "w")
    for (u,v) in lpm.g.graph.edges():
#         newW = lpm.newWeights[(u,v)]
        allW = filter(lambda x: (u,v) in x,lpm.g.allWeights)
        allW.sort(highOrderGraph.cmpFeatures)
        sumAllW = 0
        currW = 0
        for w in allW:
            if (w == ((u,v),)):
                currW = lpm.g.allWeights[w]
            else:
                sumAllW += lpm.g.allWeights[w]*lpm.g.allWeights[w]
        try:
            tempOutFile.write('(%s,%s),%s\n' % (u,v,currW + (math.sqrt(sumAllW)/(len(allW)-1)) ))
        except ZeroDivisionError:
            print ("u =",u,"v =", v);
            exit
#         worksheet.write_column(0,col, [str((u,v))] + [str(w) for w in allW])
#         col += 1
#         worksheet.write_column(0,col, [newW] + [lpm.g.allWeights[w] for w in allW])
#         col += 1
#     workbook.close()
    tempOutFile.close()
    
    G2 = highOrderGraph.DiGraph(G.n,"_av.txt")
    G2.addWeights()
    lpm3 = highOrderGraph.LPMaker(G2,'afterReduction','afterReduction.lp')
    lpm3.createLP(proj)
    lpm3.solveLP()
    
    avTree = {}
    for (u,v) in lpm3.g.graph.edges():
        if lpm3.LPVars[((u,v),)].x > 0:
            avTree[(u,v)] = 1;
    
    intersection = filter(lambda x: x in bestTree.keys(),avTree.keys())
    print('amount correct = %s / %s' % (len(intersection),G.n))
    statFile.write('%s: %s / %s : %s percent' % (filename, len(intersection),G.n, len(intersection)/G.n ) )
    statFile.close

for f in allfiles:
    solveInstance(f,proj);

