import os
import sys
from graph import DiGraph

if __name__ == '__main__':
    
    if len(sys.argv) > 9:
        print "usage:",sys.argv[0],"dirname" 
    
    d = sys.argv[1]
    t = sys.argv[2]
    lang = sys.argv[3]
    order = sys.argv[4]
    decodeMethod = sys.argv[5]
    alpha = sys.argv[6]
    beta = sys.argv[7]
    parserResDir = ""
    if len(sys.argv) == 9:
        parserResDir = sys.argv[8]

    if (d == "."):
        d = os.getcwd()
    
    allFileData  = []
    fileIdsToSkip = []
    allFiles = []
    
    nCorrect            = 0
    total               = 0
    nFiles              = 0
    nUnionCorrect       = 0
    nUndirectedCorrect  = 0
    for f in os.listdir(d):
        if not f.endswith(".txt"):
            continue
        if f.endswith("log.txt"):
            continue
        nFiles += 1
        g = DiGraph(d + "/" + f,True)
        optHeads = g.optHeads
        goldHeads = g.goldHeads
        if (parserResDir != ""):
            parser_g = DiGraph(parserResDir + "/" + f,True)
            parserHeads = parser_g.optHeads
        for i in range(0,g.n):
            v           = i + 1
            goldu       = goldHeads[i]
            optu        = optHeads[i]
            if optu == "_":
                optu = '0'
            if optu == goldu:
                nCorrect            += 1
                nUnionCorrect       += 1
                nUndirectedCorrect  += 1  
            elif ((parserResDir != "") and (parserHeads[i] == goldu)):
                nUnionCorrect += 1
            if ((int(optu) > 0) and ( int(goldHeads[int(optu) - 1]) == (i + 1) )):
                nUndirectedCorrect += 1
            total += 1
    strToPrint = order + "," + lang + "," + str(nFiles) + "," + str(total) + "," + decodeMethod + "," + alpha + "," + beta
    strToPrint += "," + str(100 * float(nCorrect)/total) + "," + t + "," + str(100 * float(nUnionCorrect)/total)
    strToPrint += "," + str(100 * float(nUndirectedCorrect)/total)
    print strToPrint
    #print "nFiles   =", nFiles
    #print "nTokens  =", total
    #print "nCorrect =", nCorrect
    #print "accuracy =", 100 * float(nCorrect)/total
    
