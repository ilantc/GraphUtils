import sys
import re
from graph import DiGraph
from string import join

"""
cmd to run all:

treeViewConvertor.py ./data/forRunFrom2007/arabic_test_1000.conll    inferenceApx_nFiles_1000_1stOrderModel_arabic.csv     arabic_infTrees.conll    ./data/1stOrderUnPruned/arabic/    inference
treeViewConvertor.py ./data/forRunFrom2007/chinese_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_chinese.csv    chinese_infTrees.conll   ./data/1stOrderUnPruned/chinese/   inference
treeViewConvertor.py ./data/forRunFrom2007/basque_test_1000.conll    inferenceApx_nFiles_1000_1stOrderModel_basque.csv     basque_infTrees.conll    ./data/1stOrderUnPruned/basque/    inference
treeViewConvertor.py ./data/forRunFrom2007/catalan_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_catalan.csv    catalan_infTrees.conll   ./data/1stOrderUnPruned/catalan/   inference
treeViewConvertor.py ./data/forRunFrom2007/czech_test_1000.conll     inferenceApx_nFiles_1000_1stOrderModel_czech.csv      czech_infTrees.conll     ./data/1stOrderUnPruned/czech/     inference
treeViewConvertor.py ./data/forRunFrom2007/greek_test_1000.conll     inferenceApx_nFiles_1000_1stOrderModel_greek.csv      greek_infTrees.conll     ./data/1stOrderUnPruned/greek/     inference
treeViewConvertor.py ./data/forRunFrom2007/hungarian_test_1000.conll inferenceApx_nFiles_1000_1stOrderModel_hungarian.csv  hungarian_infTrees.conll ./data/1stOrderUnPruned/hungarian/ inference
treeViewConvertor.py ./data/forRunFrom2007/turkish_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_turkish.csv    turkish_infTrees.conll   ./data/1stOrderUnPruned/turkish/   inference
treeViewConvertor.py ./data/forRunFrom2007/sec22_dep.gold            inferenceApx_nFiles_1700_1stOrderModel_english.csv    english_infTrees.conll   ./data/1stOrderUnPruned/english/   inference

treeViewConvertor.py ./data/forRunFrom2007/arabic_test_1000.conll    inferenceApx_nFiles_1000_1stOrderModel_arabic.csv     arabic_cleTrees.conll    ./data/1stOrderUnPruned/arabic/    cle
treeViewConvertor.py ./data/forRunFrom2007/chinese_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_chinese.csv    chinese_cleTrees.conll   ./data/1stOrderUnPruned/chinese/   cle
treeViewConvertor.py ./data/forRunFrom2007/basque_test_1000.conll    inferenceApx_nFiles_1000_1stOrderModel_basque.csv     basque_cleTrees.conll    ./data/1stOrderUnPruned/basque/    cle
treeViewConvertor.py ./data/forRunFrom2007/catalan_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_catalan.csv    catalan_cleTrees.conll   ./data/1stOrderUnPruned/catalan/   cle
treeViewConvertor.py ./data/forRunFrom2007/czech_test_1000.conll     inferenceApx_nFiles_1000_1stOrderModel_czech.csv      czech_cleTrees.conll     ./data/1stOrderUnPruned/czech/     cle
treeViewConvertor.py ./data/forRunFrom2007/greek_test_1000.conll     inferenceApx_nFiles_1000_1stOrderModel_greek.csv      greek_cleTrees.conll     ./data/1stOrderUnPruned/greek/     cle
treeViewConvertor.py ./data/forRunFrom2007/hungarian_test_1000.conll inferenceApx_nFiles_1000_1stOrderModel_hungarian.csv  hungarian_cleTrees.conll ./data/1stOrderUnPruned/hungarian/ cle
treeViewConvertor.py ./data/forRunFrom2007/turkish_test_1000.conll   inferenceApx_nFiles_1000_1stOrderModel_turkish.csv    turkish_cleTrees.conll   ./data/1stOrderUnPruned/turkish/   cle
treeViewConvertor.py ./data/forRunFrom2007/sec22_dep.gold            inferenceApx_nFiles_1700_1stOrderModel_english.csv    english_cleTrees.conll   ./data/1stOrderUnPruned/english/   cle

python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/arabic_test_1000.conll    _     arabic_infTrees.conll /u/ilantc/runArea2/minLoss_2/arabic/    inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/chinese_test_1000.conll   _    chinese_infTrees.conll /u/ilantc/runArea2/minLoss_2/chinese/   inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/basque_test_1000.conll    _     basque_infTrees.conll /u/ilantc/runArea2/minLoss_2/basque/    inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/catalan_test_1000.conll   _    catalan_infTrees.conll /u/ilantc/runArea2/minLoss_2/catalan/   inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/czech_test_1000.conll     _      czech_infTrees.conll /u/ilantc/runArea2/minLoss_2/czech/     inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/greek_test_1000.conll     _      greek_infTrees.conll /u/ilantc/runArea2/minLoss_2/greek/     inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/hungarian_test_1000.conll _  hungarian_infTrees.conll /u/ilantc/runArea2/minLoss_2/hungarian/ inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/turkish_test_1000.conll   _    turkish_infTrees.conll /u/ilantc/runArea2/minLoss_2/turkish/   inference
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/sec22_dep.gold            _    english_infTrees.conll /u/ilantc/runArea2/minLoss_2/english/   inference

python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/arabic_test_1000.conll    _     arabic_cleTrees.conll /u/ilantc/runArea2/minLoss_2/arabic/    gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/chinese_test_1000.conll   _    chinese_cleTrees.conll /u/ilantc/runArea2/minLoss_2/chinese/   gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/basque_test_1000.conll    _     basque_cleTrees.conll /u/ilantc/runArea2/minLoss_2/basque/    gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/catalan_test_1000.conll   _    catalan_cleTrees.conll /u/ilantc/runArea2/minLoss_2/catalan/   gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/czech_test_1000.conll     _      czech_cleTrees.conll /u/ilantc/runArea2/minLoss_2/czech/     gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/greek_test_1000.conll     _      greek_cleTrees.conll /u/ilantc/runArea2/minLoss_2/greek/     gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/hungarian_test_1000.conll _  hungarian_cleTrees.conll /u/ilantc/runArea2/minLoss_2/hungarian/ gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/turkish_test_1000.conll   _    turkish_cleTrees.conll /u/ilantc/runArea2/minLoss_2/turkish/   gold
python /u/ilantc/GraphUtils/Proj/src/treeViewConvertor.py /u/ilantc/data/forRunFrom2007/sec22_dep.gold            _    english_cleTrees.conll /u/ilantc/runArea2/minLoss_2/english/   gold

"""

args = sys.argv[1:]
 
originalConllFile   = args[0]
headsCsv            = args[1]
outputFileName      = args[2]
weightsDirName      = args[3]
treeType            = args[4]
 
if treeType not in ["inference","cle","gold"]:
    raise "invalid treeType"
 
print "running, output file name is", outputFileName

conllInfile = open(originalConllFile,'rt')
allSentences = []
currSentence = []
for line in conllInfile:
    if re.match('^\s*$',line):
        continue
    # new sentence
    if re.match('^\s*1\s+',line):
        # if we had a sentence in the pipe
        if (len(currSentence) > 0):
            allSentences.append(currSentence)
            currSentence = []
    currSentence.append(line)
# finish last sentence
if (len(currSentence) > 0):
    allSentences.append(currSentence)
 
sentenceCount = len(allSentences)

# headsCsv = "inferenceApx_nFiles_1700_1stOrderMod/el_english.csv"
# sentenceCount = 5
allHeads = []
if not headsCsv == "_":
    headsInfile = open(headsCsv,'rt')
    iterNum = 0
    while iterNum < sentenceCount:
        iterNum += 1
        currHeads = {}
        for _ in range(4):
            line = headsInfile.next().strip()
            line = line.split(",")
            currHeads[line[0]] = line[2:]
        headsInfile.next() # blank line
        allHeads.append(currHeads)

outputFileHnadler = open(outputFileName,'wb')
for sentenceId in range(sentenceCount):
    sentence = allSentences[sentenceId]
    currWeightsFileName = weightsDirName + "output_" +  str(sentenceId) + ".txt"
    g = DiGraph(currWeightsFileName)
    if headsCsv == "_":
        if treeType == "inference":
            currTree = g.optHeads            
        else:
            currTree = g.goldHeads
    else:
        currTree = allHeads[sentenceId][treeType]
    for v in range(len(currTree)):
        u = currTree[v]
        try:
            w = g.partsManager.getArc(int(u),v + 1).val
        except KeyError:
            w = "nan"
        line = sentence[v].split("\t")
        line[6] = str(u)
        line[7] = str(w)
        line = join(line, "\t")
        outputFileHnadler.write(line)
    outputFileHnadler.write("\n")
    if sentenceId % 300 == 0:
        print "sentence",sentenceId , "out of", sentenceCount
    
outputFileHnadler.close()
print "\n"
        
    

