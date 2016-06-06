import os
import sys
from graph import DiGraph

if __name__ == '__main__':
    
    if len(sys.argv) > 11:
        print "usage:",sys.argv[0],"dirname" 
    
    currArg = 1    
    d = sys.argv[currArg]; currArg += 1
    t = sys.argv[currArg]; currArg += 1
    lang = sys.argv[currArg]; currArg += 1 
    order = sys.argv[currArg]; currArg += 1 
    decodeMethod = sys.argv[currArg]; currArg += 1
    alpha = sys.argv[currArg]; currArg += 1
    beta = sys.argv[currArg]; currArg += 1
    gamma = sys.argv[currArg]; currArg += 1 
    gamma2 = sys.argv[currArg]; currArg += 1
    parserResDir = ""
    if len(sys.argv) == (currArg + 1):
        parserResDir = sys.argv[currArg]

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
    nSharedMistakes     = 0
    oracle2 		= 0
    nAllCorrect 	= 0
    for f in os.listdir(d):
        if not f.endswith(".txt"):
            continue
        if f.endswith("log.txt"):
            continue
        nFiles += 1
        g = DiGraph(d + "/" + f,True)
        optHeads = g.optHeads
        goldHeads = g.goldHeads
        currInferenceCorrect = 0
        currParserCorrect    = 0
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
                currInferenceCorrect += 1
            elif ((parserResDir != "") and (parserHeads[i] == goldu)):
                nUnionCorrect += 1
            elif ((parserResDir != "") and (parserHeads[i] == optu)):
                nSharedMistakes += 1
            if ((parserResDir != "") and (parserHeads[i] == goldu)):
                currParserCorrect += 1
            if ((int(optu) > 0) and ( int(goldHeads[int(optu) - 1]) == (i + 1) )):
                nUndirectedCorrect += 1
            total += 1
        currBest = currInferenceCorrect
        if (currParserCorrect > currBest):
            currBest = currParserCorrect
        oracle2 += currBest
        if (currInferenceCorrect == g.n):
            nAllCorrect += 1
    strToPrint = order + "," + lang + "," + str(nFiles) + "," + str(total) + "," + decodeMethod + "," + alpha + "," + beta + "," + gamma + "," + gamma2
    strToPrint += "," + str(100 * float(nCorrect)/total) + "," + t + "," + str(100 * float(nUnionCorrect)/total)
    strToPrint += "," + str(100 * float(nUndirectedCorrect)/total) + "," + str(100 * float(nSharedMistakes)/total)
    strToPrint += "," + str(100 * float(oracle2)/total) + "," + str(100 * float(nAllCorrect)/nFiles)
    print strToPrint
    #print "nFiles   =", nFiles
    #print "nTokens  =", total
    #print "nCorrect =", nCorrect
    #print "accuracy =", 100 * float(nCorrect)/total
    
