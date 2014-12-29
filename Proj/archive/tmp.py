#! /usr/bin/python

import sys;
import re;
import math;
import random;

# Open Input File for Reading
infile = open(sys.argv[1],'rt');
# Open Output File for Writing
outfile = open(sys.argv[2],'w');

numSentences = sys.argv[3];

allSentences = [];
currSentence = [];
for line in infile:
    if re.match('^\s*$',line):
        continue
    # new sentence
    if re.match('^\s*1\s+',line):
        # if we had a sentence in the pipe
        if (len(currSentence) > 0):
            allSentences.append(currSentence)
            currSentence = [];
    currSentence.append(line)
# finish last sentence
if (len(currSentence) > 0):
    allSentences.append(currSentence)

sentenceCount = len(allSentences)

# convert % to num
matchObj = re.match('(\d+)%',numSentences)
if (matchObj):
    print('converting percent to num...')
    percent = matchObj.group(1)
    numSentences = math.floor(percent * sentenceCount / 100)
    print('converted ' + percent + '% to ' + numSentences + "\n")

print('sampling ' + str(numSentences) + ' out of ' + str(sentenceCount) + ' sentences...')
allSentecesIndices = [];
while (len(allSentecesIndices) < numSentences):
    randNumber = math.floor(random.random() * sentenceCount)
    if (allSentecesIndices.count(randNumber) == 0):
        allSentecesIndices.append(randNumber) 

print('sampled indices ' + str(allSentecesIndices))
# Close Input and Output Files
infile.close();
outfile.close();