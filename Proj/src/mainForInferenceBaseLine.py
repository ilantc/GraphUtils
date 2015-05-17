import csv
import os
import sys
from graph import DiGraph
from inference import inference
import getopt
import time
from test.sortperf import flush

english     = "english"
arabic      = "arabic"
basque      = "basque"
catalan     = "catalan"
chinese     = "chinese" 
czech       = "czech"
hungarian   = "hungarian"
turkish     = "turkish"
languages = [english,arabic,basque,catalan,chinese,czech,hungarian,turkish]

def main(fileIndex,useTestData,getTrees,order = 1,language = english):
    fileIndex = str(fileIndex)
    inputFile = ""
    if language == english:
        if order == 1:
            inputFile += "./data/1stOrder/"
        elif order == 2:
            inputFile += "./data/2ndOrder/"
        if useTestData:
            inputFile += "test/"
        else:
            inputFile += "dev/"
    else:
        inputFile += "./data/" + language + str(order) + "/"
        
    inputFile += "output_" + fileIndex + ".txt"
    g = DiGraph(inputFile)
    
#     print "iter Num =", fileIndex, "n =", g.n
    
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
    if fileIndex == '42':
        print "0,2"
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
        noptGoldCorrect     = 0
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
            if optu == goldu:
                noptGoldCorrect += 1
           
        out[keyName] = {'ninfGold': nInfGoldCorrect, 'ninfOpt': nInfOptCorrect, 'noptGold': noptGoldCorrect, \
                        'n': g.n, 'inferenceTime': t}
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
    
    nFiles = dict.fromkeys(languages,1000)
    nFiles[english] = 2415 if useTestData else 1699
    if nSentences:
        for language in languages:
            nFiles[language] = min(nSentences,1000)
        nFiles[english] = nSentences
        
#     nFiles = 100
    orders    = [1,2]
    languages = [english]
    orders    = [2] 
    summary = ""
    for order in orders:
        for language in languages:
            allFileData  = []
            fileIdsToSkip = []
            fileIds = range(0,nFiles[language])
        #     fileIds = [1007]
        #     Ids = [85,89,99,173,244, 287]
        #     fileIdsToSkip += Ids
            # 244 
            os.chdir(currentDir)
            outputFileName = "inferenceBaseLine_"
            outputFileName += "nFiles_" + str(nFiles[language]) + "_" + str(order) + "OrderModel_" + language
            if useTestData:
                outputFileName += "_testData"
            outputFileName += ".csv"
            
            print "language            =", language
            print "order               =", order
            print "nFiles              =", nFiles[language]
            print "useTestData         =", useTestData
            print "outputFileName      =", outputFileName
            print "printTrees          =", getTrees
            
            for fileId in fileIds:
                if (fileId in fileIdsToSkip):
                    continue
#                 fileId = 589
                try:
#                     (fileId,language,order) = (266,english,2)
                    fileData = main(fileId,useTestData,getTrees,order,language)
#                     sys.exit()
                except Exception:
                    print "\t\t## file ID =", fileId
                    raise
                if (fileId % 30) == 0:
                    print "fileID =", fileId 
                if fileData['minLoss'] == None:
                    print "## ", fileId
                allFileData.append(fileData)
            
            csvfile = open(outputFileName, 'wb')
            fieldnames = ["inferenceType","num inference / gold","num inference / opt", "num opt / gold", "average time"] 
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # fileData.keys() = ['nonProj','projInference','minLoss']
            inferenceTypes = ['projInference','nonProj', 'minLoss','2SidedMinLoss']
            inferenceTypes = ['minLoss']
            for inferenceType in inferenceTypes:
                ninfGold  = 0.0
                ninfOpt   = 0.0
                noptGold  = 0.0
                n         = 0.0
                totalTime = 0.0
                nFailed   = 0
                if not fileData.has_key(inferenceType):
                    continue
                for fileData in allFileData:
                    if fileData[inferenceType] is None:
                        nFailed += 1
                        continue
                    ninfGold    += float(fileData[inferenceType]['ninfGold'])
                    ninfOpt     += float(fileData[inferenceType]['ninfOpt'])
                    noptGold    += float(fileData[inferenceType]['noptGold'])
                    n           += float(fileData[inferenceType]['n'])
                    totalTime   += float(fileData[inferenceType]['inferenceTime'])
                line = {"inferenceType"         : inferenceType ,\
                        "num inference / gold"  : ninfGold/n    ,\
                        "num inference / opt"   : ninfOpt/n     ,\
                        "num opt / gold"        : noptGold/n    ,\
                        "average time"          : totalTime/n}
                currSummary = "\n" + 'language                  = ' + language           + "\n" \
                                   + 'order                     = ' + str(order)         + "\n" \
                                   + 'inferenceType             = ' + inferenceType      + "\n" \
                                   + 'average inference vs gold = ' + str(ninfGold/n)    + "\n" \
                                   + 'average inference vs opt  = ' + str(ninfOpt/n)     + "\n" \
                                   + 'average opt vs gold       = ' + str(noptGold/n)    + "\n" \
                                   + 'average inference time    = ' + str(totalTime/n)   + "\n" \
                                   + 'number failed             = ' + str(nFailed)       + "\n"
                print currSummary
                summary += currSummary
                writer.writerow(line)
                
                if getTrees:
                    treeFileName = "allTrees_" + language + "_order" + str(order) + ".csv"
                    csvfile2 = open(treeFileName, 'wb')
                    flush()
                    for fileData in allFileData:
                        if not fileData.has_key('goldHeads'):
                            continue

                        goldStr         = "gold,"           + ",".join(map(lambda t: str(t),fileData['goldHeads'])) + "\n"
                        highOrderOptStr = "highOrderOpt,"   + ",".join(map(lambda t: str(t),fileData['optHeads'])) + "\n"
                        minLossStr      = "minLoss,"        + ",".join(map(lambda t: str(t),fileData['greedyOptHeads'])) + "\n"
    #                     projOptStr      = "projOpt,"        + ",".join(map(lambda t: str(t),fileData['projOptHeads'])) + "\n"
    #                     nonProjStr      = "nonProjOpt,"     + ",".join(map(lambda t: str(t),fileData['nonProjOptHeads'])) + "\n"
                        emptyStr        = "\n"
    #                     lines           = [goldStr,highOrderOptStr,projOptStr,nonProjStr,emptyStr]
                        lines           = [goldStr,highOrderOptStr,minLossStr,emptyStr]
                        csvfile2.writelines(lines)
                    csvfile2.close()
                
            csvfile.close
            
    print summary
