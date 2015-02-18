import csv
import stats
from graph import DiGraph

if __name__ == '__main__':
    data = []
    su = stats.statsUtils()
    nFiles = 'all'
    offset = 0
    inputFile = "./data/sec2-21_dep.gold"
    inputFile = "./data/sec22_dep.gold"
    resFilePath = ".data/2ndOrder/dev/"
    inputFile = "./data/sec23_dep.gold"
    resFilePath = "./data/1stOrder/test/"
    allSentences = su.readDepFile(nFiles,offset,inputFile)
    fileIndex = 0
    maxDegData = 9
    highOrderAccuracy = 0.0
    nCorrect = 0
    total = 0
    for goldHeads in allSentences:
        # tree stats
        st = stats.treeStats(goldHeads)
        currData = st.getDepthAndDeg(maxDegData)
        currData["sentence"] = fileIndex
        data.append(currData)
        
        # heads stats
        resFile = resFilePath + "output_" + str(fileIndex) + ".txt"
        g = DiGraph(resFile)
        g_goldHeads = map(lambda t: int(t), g.goldHeads)
        g_optHeads  = map(lambda t: int(t), g.optHeads)
        if (g_goldHeads != goldHeads):
            print g_goldHeads
            print goldHeads
            assert False, "bad gold heads!! fileIndex = " + str(fileIndex)
        a_s = stats.accuracyStats(g_goldHeads, g_optHeads, None)
        nCorrect += a_s.getNcorrect(g_goldHeads, g_optHeads)
        total += a_s.n
        currAccuracy = a_s.get_HighOrderOpt_gold_accuracy()
        highOrderAccuracy += currAccuracy
        print "currAccuracy =", str(currAccuracy), currData 
        
        fileIndex += 1
    highOrderAccuracy = highOrderAccuracy/len(allSentences)
    
    print "\n\nhigh order accuracy is", highOrderAccuracy
    print "\n\nhigh order accuracy2 is", float(nCorrect)/float(total)
    outputFileName = "statsGold.csv"
    csvfile = open(outputFileName, 'wb')
    fieldnames = ["sentence","n","depth","max degree"]
    for deg in range(0,maxDegData):
        fieldnames.append("deg" + str(deg))
    fieldnames.append("deg > " + str(maxDegData))
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    csvfile.close()
    
        

