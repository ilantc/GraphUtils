# import networkx as nx
import highOrderGraph
import xlsxwriter as xw
import math
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
vals = []
n=20
proj = False
numIter = 1
for i in range(numIter):
    F = highOrderGraph.DiGraph(n)
    F.addWeights()
    filename = "out%s" %(n)
    F.writeFile(filename + ".txt")
     
    lpm = highOrderGraph.LPMaker(F,'try')
    # lpm.createLP()
    # lpm.solveLP()
    lpm.createWeightReductionLP(proj)
    lpm.solveWeightReductionLP()
    
    workbook = xw.Workbook('W_model_%s.xlsx'%(n))
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    outFile = open(filename + "_av.txt", "w")
    correctTree = []
    for (u,v) in lpm.g.graph.edges():
        newW = lpm.newWeights[(u,v)]
        allW = filter(lambda x: (u,v) in x,lpm.g.allWeights)
        allW.sort(highOrderGraph.cmpFeatures)
        if lpm.LPVars[((u,v),)].x > 0:
            correctTree.append(((u,v),))
        sumAllW = 0
        currW = 0
        for w in allW:
            if (w == ((u,v),)):
                currW = lpm.g.allWeights[w]
            else:
                sumAllW += lpm.g.allWeights[w]*lpm.g.allWeights[w]
        outFile.write('(%s,%s),%s\n' % (u,v,currW + (math.sqrt(sumAllW)/(len(allW)-1)) ))
        worksheet.write_column(0,col, [str((u,v))] + [str(w) for w in allW])
        col += 1
        worksheet.write_column(0,col, [newW] + [lpm.g.allWeights[w] for w in allW])
        col += 1
    workbook.close()
    outFile.close()
    
    G = highOrderGraph.DiGraph(n,filename + "_av.txt")
    G.addWeights()
    lpm = highOrderGraph.LPMaker(G,'try')
    lpm.createLP(proj)
    lpm.solveLP()
    
    avTree = []
    for (u,v) in lpm.g.graph.edges():
        if lpm.LPVars[((u,v),)].x > 0:
            avTree.append(((u,v),))
    
    amountCorrect = 0
    intersection = filter(lambda x: x in correctTree,avTree)
    print('amount correct = %s / %s' % (len(intersection),n))
    vals.append(len(intersection))


Fname = 'averageRes_%s_nodes_%s_tries' % (n,numIter)
if proj:
    Fname += '_proj'
else:
    Fname += '_nonproj'
Fname += '.csv'
outFile = open(Fname,"w")
for v in vals:
    outFile.write(str(v) + "\n")
outFile.close()

#     print('(%s,%s)\t%s' % (u,v,newW))
#     print('===')
#     for w in allW:
#         text = ''
#         text += str(w) + '\t'
#         text += str(lpm.g.allWeights[w])
#         print(text)


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