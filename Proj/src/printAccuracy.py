import os
import sys
from graph import DiGraph

if __name__ == '__main__':
    
    if len(sys.argv) > 2:
        print "usage:",sys.argv[0],"dirname" 
    
    d = sys.argv[1]
    if (d == "."):
        d = os.getcwd()
    
    allFileData  = []
    fileIdsToSkip = []
    allFiles = []
    
    nCorrect    = 0;
    total       = 0;
    nFiles      = 0;
    for f in os.listdir(d):
        if not f.endswith(".txt"):
            continue
        nFiles += 1
        g = DiGraph(d + "/" + f)
        optHeads = g.optHeads
        goldHeads = g.goldHeads
        for i in range(0,g.n):
            v           = i + 1
            goldu       = goldHeads[i]
            optu        = optHeads[i]
            if optu == goldu:
                nCorrect += 1
            total += 1
    
    print "nFiles   =", nFiles
    print "nTokens  =", total
    print "nCorrect =", nCorrect
    print "accuracy =", float(nCorrect)/total
    
