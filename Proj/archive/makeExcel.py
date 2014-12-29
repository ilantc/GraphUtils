from os import listdir
from os.path import isfile, join
import re

allfiles = [ f for f in listdir(".") if isfile(join(".",f)) ]

studenToLine = {}

unknownLines = []

for f in allfiles:
    matchObj = re.search('_(\d+)_(\d+)\.\w+$', f)
    if matchObj:
        line = f + "," + matchObj.group(1);
        if (studenToLine.has_key(matchObj.group(1))):
            line = line + ",submitted twice"
        studenToLine[matchObj.group(1)] = line;
        line = f + "," + matchObj.group(2);
        if (studenToLine.has_key(matchObj.group(2))):
            line = line + ",submitted twice"
        studenToLine[matchObj.group(2)] = line;
        continue
    matchObj = re.search('_(\d+)\.\w+$', f)
    if matchObj:
        line = line = f + "," + matchObj.group(1) + ",submitted alone ";
        if (studenToLine.has_key(matchObj.group(1))):
            line = line + "submitted twice"
        studenToLine[matchObj.group(1)] = line;
        continue
    unknownLines.append(f + ",,wrong format")
outputFile = open("submitions.csv","w")
for student in studenToLine:
    outputFile.write(studenToLine[student] + "\n")
for unknownLine in unknownLines:
    outputFile.write(unknownLine + "\n")
outputFile.close()