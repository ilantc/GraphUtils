from graph import DiGraph
from graph import LPMaker
import csv
import gurobipy as gp
import os

def main(fileIndex,writeCsvFile,verbose,applyPositiveSlacks):
    fileIndex = str(fileIndex)
#     inputFile = "./data/output_" + fileIndex + ".txt"
    inputFile = "./output_" + fileIndex + ".txt"
    outputFileName = "./output/file_" + fileIndex + ".csv"
    g = DiGraph(inputFile)
    lpm = LPMaker(g, "try_input_" + fileIndex, "input_" + fileIndex + ".lp")
    
    bestTree = [];
    print "n =",g.n
    for i in range(0,g.n):
        v = i + 1
        u = int(g.optHeads[i])
        bestTree.append((u,v))
        if verbose: 
            print "best tree added (" + str(u) + "," + str(v) + ")"
    lpm.createLP(True, bestTree,applyPositiveSlacks)
    lpm.lpFile = None
    lpm.solve(verbose)
    if lpm.model.status != gp.GRB.status.OPTIMAL:
        lpm.model.computeIIS()
        for c in lpm.model.getConstrs():
            if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
                print c.getAttr(gp.GRB.Attr.ConstrName),c.getAttr(gp.GRB.Attr.Sense),c.getAttr(gp.GRB.Attr.RHS)
        return 

    w = {}
    for (u,v) in lpm.newWeights.keys():
        w[u,v] = lpm.newWeights[u,v]
    
    optG = lpm.chuLiuEdmondsWrapper(g.n, w)
    
    if writeCsvFile:
        csvfile = open(outputFileName, 'wb')
        fieldnames = ["childIndex","goldHead","optHead","LP Head"] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    vals = {}
    optEdges = optG.edges()
    edgesFromLp = lpm.optEdges
    nOptCorrect = 0
    nLPCorrect = 0
    nLP_OPTCorrect = 0
    for i in range(0,g.n):
        v = i + 1
        goldu = int(g.optHeads[i])
        optEdge = filter(lambda (u_j,v_j): v_j == v, optEdges)
        optU = optEdge[0][0]
        edgeFromLp = filter(lambda (u_j,v_j): v_j == v, edgesFromLp)
        LPU = edgeFromLp[0][0]
        line = {"childIndex": v,"goldHead": goldu,"optHead": optU,"LP Head": LPU}
#         print line
        if writeCsvFile:
            writer.writerow(line)
        if optU == goldu:
            nOptCorrect += 1 
        if LPU == goldu:
            nLPCorrect += 1
        if LPU == optU:
            nLP_OPTCorrect += 1
    if writeCsvFile:
        csvfile.close
#     print nOptCorrect,nLPCorrect,nLP_OPTCorrect
    return {'nopt': float(nOptCorrect)/float(g.n), 'nLP': float(nLPCorrect)/float(g.n), 'n_LP_OPT': float(nLP_OPTCorrect)/float(g.n)}
#     print bestTree, optG.edges()
#     nCorrect = 0;
#     for (u,v) in optG.edges():
#         print (u,v)
#         if (u,v) in bestTree:
#             nCorrect += 1
#     print "nCorrect =", nCorrect, "out of", g.n 
        
# names = lpm.getConflictingConstrsNames(lpm.model, lpm.edges, lpm.g.partsManager)
# for name in names:
#     lpm.model.remove(lpm.model.getConstrByName(name))
# 
# lpm.solve("input_" + fileIndex + ".out")
# numRemoved = 0
# while lpm.model.status != gp.GRB.status.OPTIMAL:
#     lpm.model.computeIIS()
#     for c in lpm.model.getConstrs():
#         if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
#             print c.getAttr(gp.GRB.Attr.ConstrName),c.getAttr(gp.GRB.Attr.Sense),c.getAttr(gp.GRB.Attr.RHS) 
#             lpm.model.remove(c)
#             numRemoved += 1
#     lpm.model.update()
#     lpm.solve()
# 
#     
# print "removed", len(names),"+",numRemoved, "constrs"


# for c in lpm.model.getConstrs():
#     if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
#         print c.getAttr(gp.GRB.Attr.ConstrName)
        


if __name__ == '__main__':
    writeCsvFile = False
    verbose = False
    applyPositiveSlacks = False
    currentDir = os.getcwd()
    os.chdir('C:\\Users\\ilantc\\shared')
    allFileData  = []
    nFiles = 1858
    fileIds = range(0,nFiles)
    fileIdsToSkip = [629,1192,1759]
    nFiles -= len(fileIdsToSkip)
    print "writeCsv =", writeCsvFile, "verbose =", verbose, "applyPositiveSlacks =", applyPositiveSlacks, "nFiles =", nFiles
    for fileId in fileIds:
        if (fileId in fileIdsToSkip):
            continue
        fileData = main(fileId,writeCsvFile,verbose,applyPositiveSlacks)
        print fileData
        allFileData.append(fileData)
    nopt = 0.0
    nLP = 0.0
    LP_OPT = 0.0
    for fileData in allFileData:
        nopt += fileData['nopt']
        nLP += fileData['nLP']
        LP_OPT += fileData['n_LP_OPT']
    os.chdir(currentDir)
    print 'positive slacks =', applyPositiveSlacks
    print 'average opt vs gold =', nopt/nFiles
    print 'average lp output vs gold =', nLP/nFiles
    print 'average opt vs lp output =', LP_OPT/nFiles
