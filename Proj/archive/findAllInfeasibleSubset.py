# import networkx as nx
import xlsxwriter as xw
import math
import re
import string
from os import listdir
from os.path import isfile, join
from inspect import joinseq
# import re
# from gurobipy import *
# G=nx.DiGraph()
# G.add_nodes_from(range(5))
#  
# print(G.nodes())
# print(G.edges())
# for e in nx.non_edges(G):
#     print(e)
#     G.add_edges_from([e])
# G.add_edges_from(nx.non_edges(G))
# 
# for (u,v) in G.edges():
#     print("U is " + str(u) + ", V is " + str(v))
  
# print(G.edges())

def readFile(infile):
    ins = open( infile, "r" )
    allVars = []
    allSubsets = {}
    for line in ins:
        currMatch = re.match("^\s*subset_.*:\s+(.*)\s*([<>]=)\s*(.*)\s*$",line)
        if (not currMatch):
            continue;
        
        currVars = re.split("\s*\+?\s*",currMatch.group(1));
        currVars.remove('');
        for var in currVars:
            if allVars.count(var) == 0:
                allVars.append(var)
        currVars.sort();
        currSubset = tuple(currVars);
        allSubsets[currSubset] = (currMatch.group(2),float(currMatch.group(3)))
    ins.close()
    return (allVars,allSubsets)


out = readFile("reduction.lp");
allVars = out[0];
allSubsets = out[1];
conflictedSubsets = [];
deducedConstrains = {};
conflictedSubsets2 = [];
# {origSubset: {currSubset:(sign,value)}}

# print string.join(allVars,"\n")
for subset in allSubsets:
    # easy test - didn't work
    allSigns = map(lambda var: allSubsets[(var,)][0], subset)
    if ((allSigns.count("<=") == len(allSigns)) or (allSigns.count(">=") == len(allSigns))):
        sign = allSigns[0];
#         print (sign,subset,allSubsets[subset][0])
        if allSubsets[subset][0] != sign:
            conflictedSubsets.append(subset)
print (conflictedSubsets)
# print allSubsets
for var in allVars:
    currSign = allSubsets[(var,)][0];
    currvalue = allSubsets[(var,)][1];
    allCurrSubsets = filter(lambda subset: subset.count(var) > 0, allSubsets.keys());
    for subset in allCurrSubsets:
        currSubsetSign = allSubsets[subset][0];
        if (currSign != currSubsetSign):
            if (deducedConstrains.has_key(subset)):
                currConstraint = deducedConstrains[subset];
                currSubset = currConstraint.keys()[0];
                if (currSubset.count(var) > 0):
                    newSubset = list(currSubset)
                    newSubset.remove(var);
                    if len(newSubset) == 0:
                        conflictedSubsets2.append(subset)
                    newValue = currConstraint[currSubset][1];
                    newValue -= currvalue;
#                     if (currSign == ">="):
#                         newValue -= currvalue;
#                     else:
#                         newValue += currvalue;
                    deducedConstrains[subset] = {tuple(newSubset): (currSubsetSign,newValue)}
            else:
                newSubset = list(subset)
                newSubset.remove(var);
                newValue = allSubsets[subset][1];
                newValue -= currvalue;
#                 if (currSign == ">="):
#                     newValue -= currvalue;
#                 else:
#                     newValue += currvalue;
                deducedConstrains[subset] = {tuple(newSubset): (currSubsetSign,newValue)}
# print (deducedConstrains)
print (conflictedSubsets2)

