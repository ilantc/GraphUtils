import csv
import gurobipy as gp
import os
import sys
from graph import DiGraph
from graph import LPMaker
from inference import inference
import getopt
from test.sortperf import flush

def main(fileIndex,writeCsvFile,verbose,applyPositiveSlacks,order,useGoldHeads,useTestData,getTrees,alpha,proj):
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
#     if g.n > 15:
#         return
    for i in range(0,g.n):
        v = i + 1
        u = int(gHeads[i])
        bestTree.append((u,v))
        if verbose: 
            print "best tree added (" + str(u) + "," + str(v) + ")"
    lpm.createLP(proj, bestTree,applyPositiveSlacks,alpha)
    lpm.lpFile = None
    lpm.solve(verbose)
    if lpm.model.status != gp.GRB.status.OPTIMAL:
        print "\n\nINFEASIBLE: file ID =", fileIndex
        lpm.model.computeIIS()
        for c in lpm.model.getConstrs():
            if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
                print c.getAttr(gp.GRB.Attr.ConstrName),c.getAttr(gp.GRB.Attr.Sense),c.getAttr(gp.GRB.Attr.RHS)
        return 

    w = {}
    for (u,v) in lpm.newWeights.keys():
        w[u,v] = lpm.newWeights[u,v]
    
    inf = inference(w,g.n);
    optGProj            = inf.eisnerProjective()
    optGNonProj         = inf.chuLiuEdmondsWrapper()
    optGgreedyMinLoss   = inf.greedyMinLoss() 
    
    goldHeads = map(lambda u: int(u), g.goldHeads)
    origOptHeads = map(lambda u: int(u), g.optHeads)
    outHeads = {'projInference':[],'nonProj': [], 'minLoss': []}
    if writeCsvFile:
        csvfile = open(outputFileName, 'wb')
        fieldnames = ["childIndex","goldHead","highOrderOptHead","optHead","LP Head"] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    out = {}
    for (optG, keyName) in [(optGProj,'projInference'), (optGNonProj,'nonProj'), (optGgreedyMinLoss,'minLoss')]: 
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
            goldu = goldHeads[i]
            origOptu = origOptHeads[i]
            optEdge = filter(lambda (u_j,v_j): v_j == v, optEdges)
            optU = optEdge[0][0]
            outHeads[keyName].append(optU)
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
#         normalizationFactor = float(g.n)
        out[keyName] = {'noptGold': nOptGoldCorrect, 'nLPGold': nLPGoldCorrect, 'n_LP_OPT': nLP_OPTCorrect, \
               'norigOptGold': nOrigOptGoldCorrect, 'nOptOrigOpt': nOptOrigOptCorrect, 'nLpOrigOpt': nLP_OrigOptCorrect, 'n': g.n}
        if getTrees:
            out['goldHeads'] = goldHeads
            out['highOrderOptHeads'] = origOptHeads
            out['projOptHeads'] = outHeads['projInference']
            out['nonProjOptHeads'] = outHeads['nonProj']
    
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
    
    print "option <type> [default]: description"
    print "-s <bool> [t]: apply positive slacks"
    print "-g <bool> [t]: use gold heads"
    print "-t <bool> [f]: use test data"
    print "-o <int>  [2]: model order (1, 2 or 3)"
    print "-p <bool> [f]: print out all tres to output csv file" 
    print "-a <float>[1]: alpha parameter for d in the objective function"
    print "-i <bool> [t]: use projective ILP formulation"
    print "-n <int>     : num sentences (override defaults for train/dev sets)"
    
    
    
if __name__ == '__main__':
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "s:g:t:o:p:a:i:n:h", \
                                       ["applyPositiveSlacks", "useGoldenHeads","useTestData", "order", \
                                        "getTrees","alpha","projectiveILPConstraints"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    trueVals            = ["1","true","True", "t", "T"]
    falseVals           = ["0", "false", "False", "F", "f"]
    
    writeCsvFile        = False
    verbose             = False
    applyPositiveSlacks = True
    useGoldHeads        = True
    projective          = True
    useTestData         = False
    getTrees            = False
    nSentences          = None
    order               = 2
    alpha               = 1.0
    
    print "opts =", opts, "\nargs =", args
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit(0)
        if o == "-n":
            nSentences = int(a)
        elif o in ["-s", "--applyPositiveSlacks"]:
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
        elif o in ("-p", "--getTrees"):
            if a in trueVals:
                getTrees = True
            elif a in falseVals:
                getTrees = False
            else:
                assert False, "bad arg for parameter " + o
        elif o in ("-i", "--projectiveILPConstraints"):
            if a in trueVals:
                projective = True
            elif a in falseVals:
                projective = False
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
        elif o in ("-a", "--alpha"):
            alpha = float(a)
        else:
            assert False, "unhandled option : " + o

    currentDir = os.getcwd()
    os.chdir('data')
    allFileData  = []
    nFiles = 2415 if useTestData else 1699
    if nSentences:
        nFiles = nSentences
#     nFiles = 100
    fileIdsToSkip = []
    fileIds = range(0,nFiles)
#     fileIds = [1007]
    
    os.chdir(currentDir)
    outputFileName = "res_"
    outputFileName += "allSlk_" if applyPositiveSlacks else "negSlk_"
    outputFileName += "nFiles_" + str(nFiles) + "_"
    if order == 3:
        outputFileName += "3rd"
    elif order == 2:
        outputFileName += "2nd"
    else:
        outputFileName += "1st"
    outputFileName += "OrderModel_"
    if useGoldHeads:
        outputFileName += "goldHeads_"
    else:
        outputFileName += "optHeads_"
    outputFileName += "alpha_" + str(alpha)
    if useTestData:
        outputFileName += "_testData"
    outputFileName += ".csv"

    print "writeCsv            =", writeCsvFile
    print "verbose             =", verbose 
    print "applyPositiveSlacks =", applyPositiveSlacks 
    print "nFiles              =", nFiles
    print "modelOrder          =", order
    print "alpha               =", alpha
    print "projective ILP form =", projective
    print "useTestData         =", useTestData
    print "outputFileName      =", outputFileName
    print "printTrees          =", getTrees
    
    for fileId in fileIds:
        if (fileId in fileIdsToSkip):
            continue
#         fileId = 21
        fileData = main(fileId,writeCsvFile,verbose,applyPositiveSlacks,order,useGoldHeads,\
                        useTestData,getTrees,alpha,projective)
        if (fileId % 1) == 0:
            print "fileID =", fileId 
#         print fileData
        allFileData.append(fileData)
    
    csvfile = open(outputFileName, 'wb')
    fieldnames = ["opt / gold","opt / lp output","lp output / gold", \
                  "highOrderOutput / gold","opt / highOrderOutput", "lpOutput / highOrderOutput","projective inference","allSlk",\
                  "alpha","trained on gold or higher order opt", "projective ILP formulation"] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for inferenceType in ['nonProj','projInference','minLoss']:
        noptGold    = 0.0
        nLPGold     = 0.0
        LP_OPT      = 0.0
        origOptGold = 0.0
        optOrigOpt  = 0.0
        LpOrigOpt   = 0.0
        n           = 0.0
        for fileData in allFileData:
            noptGold    += float(fileData[inferenceType]['noptGold'])
            nLPGold     += float(fileData[inferenceType]['nLPGold'])
            LP_OPT      += float(fileData[inferenceType]['n_LP_OPT'])
            origOptGold += float(fileData[inferenceType]['norigOptGold'])
            optOrigOpt  += float(fileData[inferenceType]['nOptOrigOpt'])
            LpOrigOpt   += float(fileData[inferenceType]['nLpOrigOpt'])
            n           += float(fileData[inferenceType]['n'])
        line = {"projective inference"                  : inferenceType                             ,\
                "allSlk"                                : applyPositiveSlacks                       ,\
                "trained on gold or higher order opt"   : "gold" if useGoldHeads else "highOrderOpt",\
                "alpha"                                 : alpha                                     ,\
                "projective ILP formulation"            : projective                                ,\
                "opt / gold"                            : noptGold/n                                ,\
                "opt / lp output"                       : LP_OPT/n                                  ,\
                "lp output / gold"                      : nLPGold/n                                 ,\
                "highOrderOutput / gold"                : origOptGold/n                             ,\
                "opt / highOrderOutput"                 : optOrigOpt/n                              ,\
                "lpOutput / highOrderOutput"            : LpOrigOpt/n}
        print "\n"
        headsStr = 'used gold heads' if useGoldHeads else 'used high order opt heads' 
        print headsStr
        print 'modelOrder                =', order
        print 'alpha                     =', alpha
        print "proj ILP formulation      =", projective
        print 'positive slacks           =', applyPositiveSlacks
        print 'isProjectiveInference     =', inferenceType, "\n"
        print 'average opt vs gold       =', noptGold/n
        print 'average lp output vs gold =', nLPGold/n
        print 'average opt vs lp output  =', LP_OPT/n
        print 'average origOpt vs gold   =', origOptGold/n
        print 'average opt vs origOpt    =', optOrigOpt/n
        print 'average lpOpt vs origOpt  =', LpOrigOpt/n
        writer.writerow(line)
    csvfile.close
    
    if getTrees:
        csvfile2 = open("allTrees.csv", 'wb')
        flush()
        for fileData in allFileData:
            goldStr         = "gold,"           + ",".join(map(lambda t: str(t),fileData['goldHeads'])) + "\n"
            highOrderOptStr = "highOrderOpt,"   + ",".join(map(lambda t: str(t),fileData['highOrderOptHeads'])) + "\n"
            projOptStr      = "projOpt,"        + ",".join(map(lambda t: str(t),fileData['projOptHeads'])) + "\n"
            nonProjStr      = "nonProjOpt,"     + ",".join(map(lambda t: str(t),fileData['nonProjOptHeads'])) + "\n"
            emptyStr        = "\n"
            csvfile2.writelines([goldStr,highOrderOptStr,projOptStr,nonProjStr,emptyStr])
        csvfile2.close()
    
