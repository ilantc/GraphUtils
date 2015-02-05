import networkx as nx
import re

class statsUtils:
    
    def __init__(self):
        pass
    
    def readFile(self,numSentences = 'all',offset = 0,inputFile = "./data/sec22_dep.gold"):
        """ read input file """
        f = open(inputFile,'rt')
        allSentences = []
        # iterate until offset is passed
        currSentenceIndex = 0
        while currSentenceIndex < offset:
            line = f.next()
            # empty line means a sentence had just ended
            if re.match("^\s*$",line):
                currSentenceIndex += 1
        
        # read the required sentences
        if numSentences == 'all':
            stopIndex = float("Inf")
        else:
            stopIndex = numSentences + offset
        goldHeads = []
        while currSentenceIndex < stopIndex:
            try:
                line = f.next()
            except StopIteration:
                return allSentences
            
            # if we are in an empty line - reset all params and save sentence
            if re.match("^\s*$",line):
                currSentenceIndex += 1
                allSentences.append(goldHeads)
                goldHeads = []
            else:
                fields = line.split()
                goldHeads.append(int(fields[6]))
        return allSentences

class treeStats:
    
    def __init__(self,heads):
        g = nx.DiGraph()
        n = len(heads) + 1
        g.add_nodes_from(range(0,n))
        for i in range(n - 1):
            g.add_edge(int(heads[i]), i + 1)
        self.g = g
        self.heads = heads    
    
    def getDepthAndDeg(self,maxDegData):
        # get max num of childs and tree depth
        stack = self.g.neighbors(0)
        depths = {0:0}
        maxDeg = self.g.out_degree(0)
        degs = {}
        maxDegStr = "deg > " + str(maxDegData)
        for deg in range(0,maxDegData):
            degs["deg" + str(deg)] = 0
        degs[maxDegStr] = 0
        while len(stack) > 0:
            currNode = stack.pop()
            outDeg = self.g.out_degree(currNode)
            if outDeg >= maxDegData:
                degs[maxDegStr] += 1
            else:
                degs["deg" + str(outDeg)] += 1
            if outDeg > maxDeg:
                maxDeg = outDeg
            depths[currNode] = depths[int(self.heads[currNode - 1])] + 1
            stack = stack + self.g.neighbors(currNode)
        degs["max degree"] = maxDeg
        degs["depth"] = max(depths.itervalues())
        degs["n"] = len(self.heads)
        return degs