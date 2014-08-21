import networkx as nx
import random
import re


class DiGraph:
    
    def __init__(self,n,file=None):
        # create a new graph
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(n+1)) 
        G.add_edges_from(nx.non_edges(G))
        
        # remove incoming edges to 0
        for node in range(1,n+1):
            G.remove_edge(node, 0) 
            
        # init weights DS
        self.allWeights = {}
        
        # save graph
        self.graph = G
        self.file  = file
        
    def addWeights(self):
        if self.file:
            self.readFile(self.file)
        else:
            for (u1,v1) in self.graph.edges():
                # set weight for this edge
                val = random.random() * 3
                element = tuple([(u1,v1)])
                self.allWeights[element] = val
                # 2nd order features
                for (u2,v2) in self.graph.edges():
                    feature = [(u2,v2),(u1,v1)]
                    feature.sort()
                    feature = tuple(feature)
                    val = random.random() * 3
                    # sib features
                    if (u2 == u1) and (v2 != v1):
                        self.allWeights[feature] = val
                    # grandchild feature
                    elif (v1 == u2) and (u1 != v2):
                        self.allWeights[feature] = val

    def readFile(self,file):
        
        ins = open( file, "r" )

        for line in ins:
            # line is something like: "(1,2),(3,5),4.25"
            # all edges of this feature
            edges = re.findall("\(\d+,\d+\)",line)
            feature = []
            for e in edges:
                edge = tuple(int(v) for v in re.findall("[0-9]+", e))
                feature.append(edge)
            feature.sort()
            # value of this feature
            v = re.findall("\),(\d+[.\d+]*)",line)
            val = float(v[0])
            
            # save this feature
            self.allWeights[tuple(feature)] = val
            
        ins.close()
        
    def writeFile(self,file):
        outFile = open(file, "w")
        for f in self.allWeights:
            print("F is: ")
            text = ""
            count = 0
            for (u,v) in f:
                print("\tU is " + str(u) + ", V is " + str(v))
                text = text + "(" + str(u) + "," + str(v) + "),"
            text = text + str(self.allWeights[f]) + "\n"
            outFile.write(text)



