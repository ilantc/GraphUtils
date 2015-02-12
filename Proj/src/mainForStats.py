import csv
import stats

if __name__ == '__main__':
    data = []
    su = stats.statsUtils()
    nFiles = 'all'
    offset = 0
    inputFile = "./data/sec2-21_dep.gold"
    allSentences = su.readFile(nFiles,offset,inputFile)
    fileIndex = 0
    maxDegData = 9
    for goldHeads in allSentences:
        st = stats.treeStats(goldHeads)
        currData = st.getDepthAndDeg(maxDegData)
        currData["sentence"] = fileIndex
        data.append(currData)
        print currData
        fileIndex += 1
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

