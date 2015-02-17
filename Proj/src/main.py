from graph import DiGraph
from graph import LPMaker
import csv
import gurobipy as gp
import os
import sys
import stats
import getopt

def main(fileIndex,writeCsvFile,verbose,applyPositiveSlacks,order,useGoldHeads,useTestData):
    fileIndex = str(fileIndex)
#     inputFile = "./data/output_" + fileIndex + ".txt"
    inputFile = "./data/"
    if order == 3:
        inputFile += "3rdOrder/"
    elif order == 2:
        inputFile += "2ndOrder/"
    elif order == 1:
        inputFile += "1stOrder/"
    else:
        assert False, "wrong model order, should be 1,2 or 3 - given: '" + str(order) + "'"
    if useTestData:
        inputFile += "test/"
    else:
        inputFile += "dev/"
        
    inputFile += "output_" + fileIndex + ".txt"
    outputFileName = "./output/file_" + fileIndex + ".csv"
    g = DiGraph(inputFile)
    lpm = LPMaker(g, "try_input_" + fileIndex, "input_" + fileIndex + ".lp")
    
    bestTree = [];
#     print "n =",g.n
    gHeads = g.optHeads
    if useGoldHeads:
        gHeads = g.goldHeads
    for i in range(0,g.n):
        v = i + 1
        u = int(gHeads[i])
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
    
    optGProj = lpm.eisnerProjective(g.n, w)
    optGNonProj = lpm.chuLiuEdmondsWrapper(g.n, w)
    
    if writeCsvFile:
        csvfile = open(outputFileName, 'wb')
        fieldnames = ["childIndex","goldHead","highOrderOptHead","optHead","LP Head"] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    out = {}
    for (optG, keyName) in [(optGProj,'proj'), (optGNonProj,'nonProj')]: 
        optEdges = optG.edges()
        edgesFromLp = lpm.optEdges
        nOptGoldCorrect = 0
        nOptOrigOptCorrect = 0
        nLPGoldCorrect = 0
        nLP_OPTCorrect = 0
        nLP_OrigOptCorrect = 0
        nOrigOptGoldCorrect = 0
        for i in range(0,g.n):
            v = i + 1
            goldu = int(g.goldHeads[i])
            origOptu = int(g.optHeads[i])
            optEdge = filter(lambda (u_j,v_j): v_j == v, optEdges)
            optU = optEdge[0][0]
            edgeFromLp = filter(lambda (u_j,v_j): v_j == v, edgesFromLp)
            LPU = edgeFromLp[0][0]
            line = {"childIndex": v,"goldHead": goldu,"highOrderOptHead": origOptu, "optHead": optU,"LP Head": LPU}
    #         print line
            if writeCsvFile:
                writer.writerow(line)
            if optU == goldu:
                nOptGoldCorrect += 1 
            if optU == origOptu:
                nOptOrigOptCorrect += 1
            if LPU == goldu:
                nLPGoldCorrect += 1
            if LPU == optU:
                nLP_OPTCorrect += 1
            if LPU == origOptu:
                nLP_OrigOptCorrect += 1
            if origOptu == goldu:
                nOrigOptGoldCorrect += 1
            
        if writeCsvFile:
            csvfile.close
    #     print nOptCorrect,nLPCorrect,nLP_OPTCorrect
        normalizationFactor = float(g.n)
        out[keyName] = {'noptGold': float(nOptGoldCorrect), 'nLPGold': float(nLPGoldCorrect), 'n_LP_OPT': float(nLP_OPTCorrect), \
               'norigOptGold': float(nOrigOptGoldCorrect), 'nOptOrigOpt': float(nOptOrigOptCorrect), 'nLpOrigOpt': nLP_OrigOptCorrect}
        for k in out[keyName].keys():
            out[keyName][k] = out[keyName][k]/normalizationFactor
     
    return out
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

def usage():
    
    print "-p <bool>: apply positive slacks"
    print "-g <bool>: use gold heads"
    print "-t <bool>: use test data"
    print "-o <int>: model order (1, 2 or 3)"
    
    
if __name__ == '__main__':
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "p:g:t:o:h", ["applyPositiveSlacks", "useGoldenHeads","useTestData", "order"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    trueVals = ["1","true","True", "t", "T"]
    falseVals = ["0", "false", "False", "F", "f"]
    applyPositiveSlacks = False
    useGoldHeads = False
    useTestData = False
    order = 2
    print "opts =", opts, "\nargs =", args
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit(0)
        if o in ["-p", "--applyPositiveSlacks"]:
            if a in trueVals:
                applyPositiveSlacks = True 
            elif a in falseVals:
                applyPositiveSlacks = False
            else:
                assert False, "bad arg for parameter " + o + " : " + a
        elif o in ("-g", "--useGoldenHeads"):
            if a in trueVals:
                useGoldHeads = True
            elif a in falseVals:
                useGoldHeads = False
            else:
                assert False, "bad arg for parameter " + o
        elif o in ("-t", "--useTestData"):
            if a in trueVals:
                useTestData = True
            elif a in falseVals:
                useTestData = False
            else:
                assert False, "bad arg for parameter " + o
        elif o in ("-o", "--order"):
            if a == "1":
                order = 1
            elif a == "2":
                order = 2
            elif a == "3":
                order = 3
            else:
                assert False, "bad arg for parameter " + o
        else:
            assert False, "unhandled option : " + o

    writeCsvFile = False
    verbose = False

    currentDir = os.getcwd()
    os.chdir('data')
    allFileData  = []
    nFiles = 2415 if useTestData else 1699
#     nFiles = 100
    fileIdsToSkip = [629,1192,1759]
    fileIdsToSkip = []
    fileIds = range(0,nFiles)
#     fileIds = [1007]
    
    os.chdir(currentDir)
    outputFileName = "res_"
    outputFileName += "allSlk_" if applyPositiveSlacks else "negSlk_"
    outputFileName += "nFiles_" + str(nFiles) + "_"
    if order == 3:
        outputFileName += "3rdOrderModel_"
    elif order == 2:
        outputFileName += "2ndOrderModel_"
    else:
        outputFileName += "1stOrderModel_"
    if useGoldHeads:
        outputFileName += "goldHeads_noNegW"
    else:
        outputFileName += "optHeads_noNegW"
    if useTestData:
        outputFileName += "_testData"
    outputFileName += ".csv"

    print "writeCsv =", writeCsvFile, "verbose =", verbose, "applyPositiveSlacks =", applyPositiveSlacks, "nFiles =", nFiles, " modelOrder  =",order, \
          "use test data =",useTestData, "outputFileName =", outputFileName
    for fileId in fileIds:
        if (fileId in fileIdsToSkip):
            continue
        fileData = main(fileId,writeCsvFile,verbose,applyPositiveSlacks,order,useGoldHeads,useTestData)
        if (fileId % 50) == 0:
            print "fileID =", fileId 
#         print fileData
        allFileData.append(fileData)
    
    csvfile = open(outputFileName, 'wb')
    fieldnames = ["proj inference","allSlk","opt / gold","opt / lp_output","lp_output / gold", \
                  "highOrderOutput / gold","opt / highOrderOutput", "lpOutput / highOrderOutput"] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for proj in ['nonProj','proj']:
        noptGold    = 0.0
        nLPGold     = 0.0
        LP_OPT      = 0.0
        origOptGold = 0.0
        optOrigOpt  = 0.0
        LpOrigOpt   = 0.0
        for fileData in allFileData:
            noptGold    += fileData[proj]['noptGold']
            nLPGold     += fileData[proj]['nLPGold']
            LP_OPT      += fileData[proj]['n_LP_OPT']
            origOptGold += fileData[proj]['norigOptGold']
            optOrigOpt  += fileData[proj]['nOptOrigOpt']
            LpOrigOpt   += fileData[proj]['nLpOrigOpt']
        line = {"proj inference"            : proj               ,\
                "allSlk"                    : applyPositiveSlacks,\
                "opt / gold"                : noptGold/nFiles    ,\
                "opt / lp_output"           : LP_OPT/nFiles      ,\
                "lp_output / gold"          : nLPGold/nFiles     ,\
                "highOrderOutput / gold"    : origOptGold/nFiles ,\
                "opt / highOrderOutput"     : optOrigOpt/nFiles  ,\
                "lpOutput / highOrderOutput": LpOrigOpt/nFiles}
        print "\n"
        headsStr = 'used gold heads' if useGoldHeads else 'used high order opt heads' 
        print headsStr
        print 'modelOrder                =', order
        print 'positive slacks           =', applyPositiveSlacks
        print 'isProjective              =', proj, "\n"
        print 'average opt vs gold       =', noptGold/nFiles
        print 'average lp output vs gold =', nLPGold/nFiles
        print 'average opt vs lp output  =', LP_OPT/nFiles
        print 'average origOpt vs gold   =', origOptGold/nFiles
        print 'average opt vs origOpt    =', optOrigOpt/nFiles
        print 'average lpOpt vs origOpt  =', LpOrigOpt/nFiles
        writer.writerow(line)
    csvfile.close
    
