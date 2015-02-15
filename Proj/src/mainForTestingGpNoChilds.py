from graph import DiGraph
from graph import LPMaker
import csv
import gurobipy as gp
import os
import sys
import stats

def main(fileIndex,writeCsvFile,verbose):
    fileIndex = str(fileIndex)
#     inputFile = "./data/output_" + fileIndex + ".txt"
#     inputFile = "./2ndOrder/output_" + fileIndex + ".txt"
    inputFile = "./output_" + fileIndex + ".txt"
    outputFileName = "./output/file_" + fileIndex + ".csv"
    g = DiGraph(inputFile)
    lpm = LPMaker(g, "try_input_" + fileIndex, "input_" + fileIndex + ".lp")
    
    bestTree = [];
#     print "n =",g.n
    for i in range(0,g.n):
        v = i + 1
        u = int(g.optHeads[i])
        bestTree.append((u,v))
        if verbose: 
            print "best tree added (" + str(u) + "," + str(v) + ")"
    edges = lpm.createAndSolveOriginalLP(True)
    nCorrect = 0
    for (u,v) in edges:
        if (u,v) in bestTree:
            nCorrect += 1
    allParts = lpm.g.partsManager.getAllParts()
    nGpPartNoGrandChild = filter(lambda part: part.type == 'grandParantNoGrandChild', allParts)
    return {'ncorrect': nCorrect, 'n':g.n, 'nParts': len(allParts), 'nGPnoGC': len(nGpPartNoGrandChild)}
    
    
if __name__ == '__main__':

    writeCsvFile = False
    verbose = False
    currentDir = os.getcwd()
    os.chdir('../../../../shared/')
    allFileData  = []
    nFiles = 39832
#     nFiles = 100
    fileIdsToSkip = [629,1192,1759]
    fileIdsToSkip = []
    fileIds = range(0,nFiles)
#     fileIds = [1007]
    totalAccuracy = 0.0
    totalGpPer = 0.0
    for fileId in fileIds:
        if (fileId in fileIdsToSkip):
            nFiles -= 1
            continue
        fileData = main(fileId,writeCsvFile,verbose)
        totalAccuracy += (float(fileData['ncorrect'])/float(fileData['n']))
        totalGpPer += (float(fileData['nGPnoGC'])/float(fileData['nParts']))
#         print (float(fileData['ncorrect'])/float(fileData['n']))
        if (fileId % 250) == 0:
#             print fileData
            print "after iter",fileId + 1,"average correct =",totalAccuracy/(fileId + 1),"average Gp rate =",totalGpPer/(fileId + 1)
        allFileData.append(fileData)
    
    
    os.chdir(currentDir)
    outputFileName = "ResGpTrain" + str(nFiles) + '.csv'

    
    csvfile = open(outputFileName, 'wb')
    fieldnames = ['fileIndex','ncorrect','n','nParts','nGPnoGC'] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    fIndex = 0
    for fileData in allFileData:
        line = fileData
        line['fileIndex'] = fIndex
        fIndex += 1
        writer.writerow(line)
    
    csvfile.close
    
