import csv
import os
import sys
from graph import DiGraph
from inference import inference
import getopt
import time
from test.sortperf import flush

def main(fileIndex,useTestData,getTrees,order = 1):
    fileIndex = str(fileIndex)
    inputFile = ""
    if order == 1:
        inputFile += "./data/1stOrder/"
    elif order == 2:
        inputFile += "./data/2ndOrder/"
    if useTestData:
        inputFile += "test/"
    else:
        inputFile += "dev/"
        
    inputFile += "output_" + fileIndex + ".txt"
    g = DiGraph(inputFile)
    
    print "iter Num =", fileIndex, "n =", g.n
    
    optTree = [];
    goldTree = [];
    optHeads = g.optHeads
    goldHeads = g.goldHeads
    
    for i in range(0,g.n):
        v = i + 1
        goldu = int(goldHeads[i])
        optu  = int(optHeads[i])
        goldTree.append((goldu,v))
        optTree.append((optu,v))

    w = {}
    for arc in g.partsManager.getArcs():
        w[arc.u,arc.v] = arc.val
    
    inf                 = inference(w,g.n,g.partsManager);
#     t1                  = time.clock()
#     optGProj            = inf.eisnerProjective()
#     t2                  = time.clock()
#     optGNonProj         = inf.chuLiuEdmondsWrapper()
    t3                  = time.clock()
#     optGgreedyMinLoss   = inf.greedyMinLoss()
    order = 2
    optGgreedyMinLoss   = inf.greedyMinLossTake2(order)
    t4                  = time.clock()
#     optGtwoSidedMinLoss = inf.twoSidedMinLoss()
#     t5                  = time.clock()
    
    goldHeads           = map(lambda u: int(u), goldHeads)
    optHeads            = map(lambda u: int(u), optHeads)
    outHeads = {'projInference':[],'nonProj': [], 'minLoss': [],'2SidedMinLoss': []}
    out = {}
#     inferenceTypes = [(optGProj,'projInference',t2 - t1), (optGNonProj,'nonProj',t3 - t2), (optGgreedyMinLoss,'minLoss', t4 - t3)\
#                       , (optGtwoSidedMinLoss,'2SidedMinLoss',t5 - t4)]
    inferenceTypes = [(optGgreedyMinLoss,'minLoss', t4 - t3)]
    for (optG, keyName,t) in inferenceTypes: 
        if optG is None:
            out[keyName] = None
            continue
        optEdges            = optG.edges()
        nInfGoldCorrect     = 0
        nInfOptCorrect      = 0
        for i in range(0,g.n):
            v           = i + 1
            goldu       = goldHeads[i]
            optu        = optHeads[i]
            optEdge     = filter(lambda (u_j,v_j): v_j == v, optEdges)
            infu        = optEdge[0][0]
            outHeads[keyName].append(infu)

            if infu == goldu:
                nInfGoldCorrect += 1 
            if infu == optu:
                nInfOptCorrect += 1
           
        out[keyName] = {'ninfGold': nInfGoldCorrect, 'ninfOpt': nInfOptCorrect, 'n': g.n, 'inferenceTime': t}
        if getTrees:
            out['goldHeads']        = goldHeads
            out['optHeads']         = optHeads
            out['projOptHeads']     = outHeads['projInference']
            out['nonProjOptHeads']  = outHeads['nonProj']
            out['greedyOptHeads']   = outHeads['minLoss']
    
    return out

def usage():
    
    print "option <type> [default]: description"
    print "-t <bool> [f]: use test data"
    print "-p <bool> [f]: print out all tres to output csv file" 
    print "-n <int>     : num sentences (override defaults for train/dev sets)"
    
    
    
if __name__ == '__main__':
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "t:p:n:h",["useTestData","getTrees"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        
    trueVals            = ["1","true","True", "t", "T"]
    falseVals           = ["0", "false", "False", "F", "f"]
    
    useTestData         = False
    getTrees            = False
    nSentences          = None
    
    print "opts =", opts, "\nargs =", args
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit(0)
        if o == "-n":
            nSentences = int(a)
        elif o in ("-p", "--getTrees"):
            if a in trueVals:
                getTrees = True
            elif a in falseVals:
                getTrees = False
            else:
                assert False, "bad arg for parameter " + o
        elif o in ("-t", "--useTestData"):
            if a in trueVals:
                useTestData = True
            elif a in falseVals:
                useTestData = False
            else:
                assert False, "bad arg for parameter " + o
        else:
            assert False, "unhandled option : " + o

    currentDir = os.getcwd()
    os.chdir('data')
    allFileData  = []
    nFiles = 2415 if useTestData else 1699
    if nSentences:
        nFiles = nSentences
#     nFiles = 100
    fileIdsToSkip = [85,287,360]
    fileIds = range(0,nFiles)
#     fileIds = [1007]
#     Ids = [85,89,99,173,244, 287]
#     fileIdsToSkip += Ids
    # 244 
    os.chdir(currentDir)
    outputFileName = "1stOrderInferenceBaseLine_"
    outputFileName += "nFiles_" + str(nFiles) + "_1stOrderModel_"
    if useTestData:
        outputFileName += "_testData"
    outputFileName += ".csv"
 
    print "nFiles              =", nFiles
    print "useTestData         =", useTestData
    print "outputFileName      =", outputFileName
    print "printTrees          =", getTrees
    
    for fileId in fileIds:
        if (fileId in fileIdsToSkip):
            continue
#         fileId = 16
        try:
            order = 2
            fileData = main(fileId,useTestData,getTrees,order)
        except Exception:
            print "\t\t## file ID =", fileId
            raise
        if (fileId % 10000) == 0:
            print "fileID =", fileId 
        allFileData.append(fileData)
    
    csvfile = open(outputFileName, 'wb')
    fieldnames = ["inferenceType","num inference / gold","num inference / opt", "average time"] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # fileData.keys() = ['nonProj','projInference','minLoss']
    for inferenceType in fileData.keys():
        ninfGold  = 0.0
        ninfOpt   = 0.0
        n         = 0.0
        totalTime = 0.0
        nFailed   = 0
        for fileData in allFileData:
            if fileData[inferenceType] is None:
                nFailed += 1
                continue
            ninfGold    += float(fileData[inferenceType]['ninfGold'])
            ninfOpt     += float(fileData[inferenceType]['ninfOpt'])
            n           += float(fileData[inferenceType]['n'])
            totalTime   += float(fileData[inferenceType]['inferenceTime'])
        line = {"inferenceType"         : inferenceType ,\
                "num inference / gold"  : ninfGold/n    ,\
                "num inference / opt"   : ninfOpt/n     ,\
                "average time"          : totalTime/n}
        print "\n"
        print 'inferenceType             =', inferenceType
        print 'average inference vs gold =', ninfGold/n
        print 'average inference vs opt  =', ninfOpt/n
        print 'average inference time    =', totalTime/n
        print 'number failed             =', nFailed
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
    
