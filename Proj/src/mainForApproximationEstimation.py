import csv
from graph import DiGraph
from inference import inference
import os, os.path
import sys



def getTrees(inputFile):
    
    g = DiGraph(inputFile)
    
    cleTree         = [0] * g.n;
    solverHeads     = map(lambda v: int(v),g.optHeads)
    goldHeads       = map(lambda v: int(v),g.goldHeads)
    inferenceHeads  = [0] * g.n
    
    w = {}
    for arc in g.partsManager.getArcs():
        w[arc.u,arc.v] = arc.val
    
    inf                 = inference(w,g.n,g.partsManager);
    
    cle                 = inf.chuLiuEdmondsWrapper()
    optGgreedyMinLoss   = inf.greedyMinLossTake2(1)
    
    outHeads = {'gold'      : {'tree' : goldHeads,      'val' : 0}, \
                'solver'    : {'tree' : solverHeads,    'val' : 0}, \
                'inference' : {'tree' : [],             'val' : 0}, \
                'cle'       : {'tree' : [],             'val' : 0}}

    cleEdges = cle.edges()
    infEdges = optGgreedyMinLoss.edges()
    for (u,v) in cleEdges:
        cleTree[v - 1] = u
    
    for (u,v) in infEdges:
        inferenceHeads[v - 1] = u
    
    outHeads['cle']['tree']         = cleTree
    outHeads['inference']['tree']   = inferenceHeads
    
    for treeType in outHeads:
        treeVal = 0
        for v in range(1,g.n + 1):
            u = outHeads[treeType]['tree'][v - 1]
            treeVal += w[u,v]
        outHeads[treeType]['val'] = treeVal
    
    return outHeads

def countMatches(v1,v2):
    count = 0
    for (u1,u2) in zip(v1,v2):
        count += (u1 == u2)
    return count

def analyzeData(trees):
    allData = []
    for tree in trees:
        data = {}
        data['n'] = len(tree['gold']['tree'])
        data['infCLEAccuracy'] = countMatches(tree['cle']['tree'], tree['inference']['tree'])
        data['optVal'] = tree['cle']['val']
        data['infVal'] = tree['inference']['val']
        if countMatches(tree['cle']['tree'], tree['solver']['tree']) != data['n']:
            print "tree", trees.index(tree), "different CLE and solver trees"
        apx = 0.5
        if (float(data['infVal']) / float(data['optVal'])) < apx:
            print "tree", trees.index(tree), "appx val of less than",apx
        allData.append(data)
    return allData

def loadFromFile(fileName):
    f = open(fileName)
    allData = []
    currTree = {}
    for line in f:
        line = line.strip().split(",")
        if len(line) == 1:
            allData.append(currTree)
            currTree = {}
        else:
            currTree[line[0]] = {}
            currTree[line[0]]['val'] = line[1]
            currTree[line[0]]['tree'] = line[2:]
    f.close()
    return allData
    
if __name__ == '__main__':

    
    english     = "english"
    arabic      = "arabic"
    basque      = "basque"
    catalan     = "catalan"
    chinese     = "chinese" 
    czech       = "czech"
    hungarian   = "hungarian"
    turkish     = "turkish"
    languages   = [english,arabic,basque,catalan,chinese,czech,hungarian,turkish]
    if len(sys.argv) > 1:
        languageId = int(sys.argv[1])
        print "language ID =", languageId
        if languageId < 0 or languageId > (len(languages) - 1):
            raise Exception('bad language id' + sys.argv[1])
        languages = [languages[languageId]]
    languages   = [english,chinese]
    baseDir     = "./data/1stOrderUnPruned/"# + language + "/output_" + str(fileIndex) + ".txt"
    for language in languages:
        languageDir = baseDir + language + "/"
        nFiles = len([name for name in os.listdir(languageDir) if os.path.isfile(os.path.join(languageDir, name))])
        readFile = False
        
        outputFileName = "inferenceApx_nFiles_" + str(nFiles) + "_1stOrderModel_" + language + ".csv"
    
        print "outputFileName      =", outputFileName
        
        if readFile:
            allTrees = loadFromFile(outputFileName)
        else: 
            allTrees = []
            for fileId in range(nFiles):
#                 (languageDir, fileId) = (baseDir + chinese + "/", 533)
                try:
                    trees = getTrees(languageDir + "output_" + str(fileId) + ".txt")
                    allTrees.append(trees)
                except Exception:
                    print "\t\t## file ID =", fileId
                    raise
                if (fileId % 30) == 0:
                    print "fileID =", fileId 
            
            csvfile = open(outputFileName, 'wb')
        #     fieldnames = ["cle","goldHeads","solverHeads", "inference"] 
            writer = csv.writer(csvfile)
            
            inferenceTypes = ['gold','solver', 'inference','cle']
            for tree in allTrees:
                for inferenceType in inferenceTypes:
                    line = [inferenceType] + [tree[inferenceType]['val']] + tree[inferenceType]['tree']
                    writer.writerow(line)
                writer.writerow("")
            csvfile.close
        
        summaryFileName = "inferenceApx_nFiles_" + str(nFiles) + "_1stOrderModel_" + language + "_summary.csv"
#         summaryFileName = "delME.csv"
        allData = analyzeData(allTrees)
        csvfile = open(summaryFileName, 'wb')
        fieldnames = ["n","infCLEAccuracy","optVal", "infVal"] 
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in allData:
            writer.writerow(data)
        csvfile.close()
        
            