import networkx as nx
import re
import gurobipy as gp
import parts
from src.model.partsManager import partsManager

class DiGraph:
    
    def __init__(self,infile):
        # create a new graph
        G = nx.DiGraph()
        self.allParts = []
        self.partsManager = partsManager()
        self.infile = infile
        if(self.infile):
            self.readFile(self.infile);
        
        # edge to feature list 
        
        
        # add all nodes and edges
        G.add_nodes_from(range(self.n+1)) 
        G.add_edges_from(nx.non_edges(G))
        
        # remove incoming edges to 0
        for node in range(1,self.n+1):
            G.remove_edge(node, 0) 
        
        # remove pruned edges
        G = self.removePrunedEdges(G);
        
        # save graph
        self.graph = G
        
        
        
    def removePrunedEdges(self,G):
        totalNumRemoved = 0;
        for (u,v) in G.edges():
            if not self.allWeights.has_key(((u,v),)):
                totalNumRemoved += 1;
#                     print("removing edge: (" + str(u) + "," + str(v) + ")")
                G.remove_edge(u,v)
        print("removed " + str(totalNumRemoved) + " edges");
        return G

    def readFile(self,infile):
        ins = open( infile, "r" )
        logfile = open("log.txt", "w")
        print(infile)
        
        sentenceString = ins.next()
        sentence = sentenceString.split();
        # skip "#" char
        self.sentence = sentence[1:]
        self.n = len(sentence) + 1
        
        goldHeads = ins.next().split("=");
        goldHeads = goldHeads[1].split(",");
        # remove last empty element
        goldHeads[:-1]
        self.goldHeads = goldHeads;
        
        optHeads = ins.next().split("=");
        optHeads = optHeads[1].split(",");
        # remove last empty element
        optHeads[:-1]
        self.optHeads = optHeads;
        
        # line is something like: "(1,2),(3,5),4.25"
        for line in ins:
            matchObj = re.search(" # (\w+)$",line)
            dependencyType = matchObj.group(1)
            
            # all edges of this feature
            edges = re.findall("\(\d+,\d+\)",line)
            v = re.findall("\),([-]?\d+[.\d+]*)",line)
            val = float(v[0])
            partVals = {'val':val}
            
            if dependencyType == "DEPENDENCYPART_ARC" or dependencyType == "DEPENDENCYPART_NEXTSIBL_LAST_SIB" \
                or dependencyType == "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD" or dependencyType == "DEPENDENCYPART_GRANDSIBL_NO_CHILDREN":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v'] = v 
                if dependencyType == "DEPENDENCYPART_ARC": 
                    self.partsManager.createPart('arc',partVals)
                elif dependencyType == "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD":
                    self.partsManager.createPart('grandParantNoGrandChild',partVals)
                    # part = parts.part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD(u,v,val)
                elif dependencyType == "DEPENDENCYPART_GRANDSIBL_NO_CHILDREN":
                    self.partsManager.createPart('grandSiblNoSibl',partVals)
                    #part = parts.part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN(u,v,val)
                else:
                    self.partsManager.createPart('lastSibl',partVals)
                    #part = parts.part_DEPENDENCYPART_NEXTSIBL_LAST_SIB(u,v,val)
                #self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_SIBL" or dependencyType == "part_DEPENDENCYPART_NEXTSIBL":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
                if (dependencyType == "DEPENDENCYPART_SIBL"):
                    self.partsManager.createPart('sibl',partVals)
                    #part = parts.part_DEPENDENCYPART_SIBL(u,v1,v2,val)
                    # TOTOTOTODO - the line below should not be here.... 
                elif (dependencyType == "DEPENDENCYPART_GRANDSIBL_LAST_SIB"):
                    self.partsManager.createPart('sibl',partVals)
                    #part = parts.part_DEPENDENCYPART_GRANDSIBL_LAST_SIB()
                else:
                    #part = parts.part_DEPENDENCYPART_NEXTSIBL(u,v1,v2,val)
                #self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_NEXTSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB(u,v,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDPAR" or dependencyType == "DEPENDENCYPART_GRANDSIBL_LAST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_GRANDPAR(g,u,v,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v2 = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_GRANDSIBL(g,u,v1,v2,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB(g,u,v,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_LAST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_GRANDSIBL_LAST_SIB(g,u,v,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v3 = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_TRISIBL(u,v1,v2,v3,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_LAST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_TRISIBL_LAST_SIBS(u,v1,v2,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_FIRST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v2 = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_TRISIBL_FIRST_SIBS(u,v1,v2,val)
                self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_ONLY_CHILD":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                part = parts.part_DEPENDENCYPART_TRISIBL_ONLY_CHILD(u,v,val)
                self.allParts.append(part)
        logfile.close();
        ins.close()
        
    def writeFile(self,f):
        outFile = open(f, "w")
        for part in self.allParts:
            outFile.write(part)
        outFile.close()

class LPMaker:
    
    def __init__(self,graph,modelName = 'lpModel',lpFile=None):
        self.modelName = modelName
        self.lpFile = lpFile
        self.g = graph
    
    # create the lp
    
    def createLP(self,projective,setGraphEdges):
        
        model = gp.Model(self.modelName)
        graph = self.g.graph
        
        edges = gp.tuplelist(graph.edges())
        nodes = graph.nodes()
        
        # Create variables and objective
        z = {}
        # weights
        w = {}
        # diff edges counters
        d = {}
        for (u,v) in edges:
            z[u,v] = model.addVar(vtype=gp.GRB.BINARY,     name='z_%s_%s' % u,v)
            w[u,v] = model.addVar(vtype=gp.GRB.CONTINUOUS, name='w_%s_%s' % u,v, lb=-1e21)
            d[u,v] = model.addVar(vtype=gp.GRB.BINARY,     name='d_%s_%s' % u,v)
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(nodes,edges,model,z,'Z')        
        
        if (projective):
            # projectivity + no circles constraints
            self.addProjectiveConstrs(nodes,model,z,'Z')
        else:
            # non proj constrs and vars
            self.LPFlowVars = self.addNonProjectiveConstrs(nodes,edges,z,model,'Z')
        
        # diff edges constraints
        for (u,v) in self.edges:
            isEdge = 0;
            if (setGraphEdges.has_key(u,v)):
                isEdge =1;
            model.addConstr(d[u,v] + z[u,v], gp.GRB.GREATER_EQUAL,isEdge,'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + isEdge, gp.GRB.GREATER_EQUAL,z[u,v],'d_y_z_%s_%s' % (u,v))
        
        # lower bounds on w constraints
        for part in self.g.allParts:
            allSubparts = part.getAllSubParts()
            allW = 0
            for p in allSubparts:
                if self.g.allWeights.has_key(f):
                    allW += self.g.allWeights[f]
                else:
                    print('Oh no! subset is %s, expected to find %s' % (feature,f))
            operator = gp.GRB.GREATER_EQUAL;
            if (allW < 0):
                operator = gp.GRB.LESS_EQUAL
            # print(self.g.graph.edges())
            model.addConstr(gp.quicksum(w[u,v] for (u,v) in feature),operator,allW,'subset_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature])) 
        
        self.LPModel = model
        self.LPVars = z
        self.edges = edges
        self.nodes = nodes
            
    def createWeightReductionLP(self,projective):
        
        self.createLP(projective)
        model = self.LPModel
        
        # add the new variables:
        # new weights
        w = {}
        # incidence vector for the new graph
        y = {}
        # diff edges counters
        d = {}
        
        # declare varuables
        for (u,v) in self.edges:
            w[u,v]      = model.addVar(lb=-1e21,vtype=gp.GRB.CONTINUOUS, name='w_%s_%s' % (u,v))
            y[((u,v),)] = model.addVar(vtype=gp.GRB.BINARY,     name='y_%s_%s' % (u,v))
            d[u,v]      = model.addVar(vtype=gp.GRB.BINARY,     name='d_%s_%s' % (u,v))
            
        
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(self.nodes,self.edges,model,y,'Y')
                
        if projective:
            #  non projectivie constrs
            self.addProjectiveConstrs(self.nodes,model,y,'Y')
        else:
            # non proj constrs and vars
            self.newLPFlowVars = self.addNonProjectiveConstrs(self.nodes,self.edges,y,model,'Y')
        
        # diff edges constraints
        for (u,v) in self.edges:
            model.addConstr(d[u,v] + y[((u,v),)], gp.GRB.GREATER_EQUAL,self.LPVars[((u,v),)],'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + self.LPVars[((u,v),)], gp.GRB.GREATER_EQUAL,y[((u,v),)],'d_y_z_%s_%s' % (u,v))
        
        # lower bounds on w constraints
        for feature in self.LPVars:
            allSubsets = allNonEmptySubsets(feature)
            allW = 0
            for f in allSubsets:
                if self.g.allWeights.has_key(f):
                    allW += self.g.allWeights[f]
                else:
                    print('Oh no! subset is %s, expected to find %s' % (feature,f))
            operator = gp.GRB.GREATER_EQUAL;
            if (allW < 0):
                operator = gp.GRB.LESS_EQUAL
            
            model.addConstr(gp.quicksum(w[u,v] for (u,v) in feature),operator,allW,'subset_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature])) 
                 
        self.WeightReductionLPModel = model
        self.newWeightsVars = w
        self.newLPVars = y
        self.diffEdges = d
    
    def createWeightReductionLPWithSetGraph(self,projective,setGraphEdges):
        model = gp.Model(self.modelName)
        self.edges = gp.tuplelist(self.g.graph.edges())
        self.nodes = self.g.graph.nodes()

        # add the new variables:
        # new weights
        w = {}
        # incidence vector for the new graph
        y = {}
        # diff edges counters
        d = {}
        
        # declare varuables
        for (u,v) in self.edges:
            w[u,v]      = model.addVar(lb=-1e21,vtype=gp.GRB.CONTINUOUS, name='w_%s_%s' % (u,v))
            y[((u,v),)] = model.addVar(vtype=gp.GRB.BINARY,     name='y_%s_%s' % (u,v))
            d[u,v]      = model.addVar(vtype=gp.GRB.BINARY,     name='d_%s_%s' % (u,v))
            
        
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(self.nodes,self.edges,model,y,'Y')
                
        if projective:
            #  non projectivie constrs
            self.addProjectiveConstrs(self.nodes,model,y,'Y')
        else:
            # non proj constrs and vars
            self.newLPFlowVars = self.addNonProjectiveConstrs(self.nodes,self.edges,y,model,'Y')
        
        # diff edges constraints
        for (u,v) in self.edges:
            isEdge = 0;
            if (setGraphEdges.has_key((u,v))):
                isEdge =1;
                
            model.addConstr(d[u,v] + y[((u,v),)], gp.GRB.GREATER_EQUAL,isEdge,'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + isEdge, gp.GRB.GREATER_EQUAL,y[((u,v),)],'d_y_z_%s_%s' % (u,v))
        
        # lower bounds on w constraints
        for feature in self.g.allWeights:
            allSubsets = allNonEmptySubsets(feature)
            allW = 0
            for f in allSubsets:
                if self.g.allWeights.has_key(f):
                    allW += self.g.allWeights[f]
                else:
                    print('Oh no! subset is %s, expected to find %s' % (feature,f))
            operator = gp.GRB.GREATER_EQUAL;
            if (allW < 0):
                operator = gp.GRB.LESS_EQUAL
            # print(self.g.graph.edges())
            model.addConstr(gp.quicksum(w[u,v] for (u,v) in feature),operator,allW,'subset_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature])) 
                 
        self.WeightReductionLPModelWithSetGraph = model
        self.newWeightsVars = w
        self.newLPVars = y
        self.diffEdges = d
              
    def solveLP(self):   
        self.LPModel.setObjective(gp.quicksum(self.LPVars[t]*self.g.allWeights[t] for t in self.g.allWeights),gp.GRB.MAXIMIZE) 
        # solve the model
        self.LPModel.update()
        modelFile = "simpleModel.lp"
        if (self.lpFile):
            modelFile = self.lpFile;
        self.LPModel.write(modelFile)
        self.LPModel.optimize()
        if self.LPModel.status == gp.GRB.status.OPTIMAL:
            for (u,v) in self.g.graph.edges():
                if self.LPVars[((u,v),)].x > 0:
                    print('(%s,%s)' % (u,v))
    
    def solveWeightReductionLPWithSetGraph(self):    
        
        # define objective 
        self.WeightReductionLPModelWithSetGraph.setObjective(  gp.quicksum(self.newLPVars[((u,v),)]*self.newWeightsVars[u,v] for (u,v) in self.edges) - 
                                                   gp.quicksum(self.diffEdges[u,v]                               for (u,v) in self.edges) - 
                                                   gp.quicksum(self.newWeightsVars[u,v]*self.newWeightsVars[u,v] for (u,v) in self.edges) -
                                                   gp.quicksum(self.newLPVars[((u,v),)]*self.newLPVars[((u,v),)] for (u,v) in self.edges) ,gp.GRB.MAXIMIZE) 
        
        self.WeightReductionLPModelWithSetGraph.update()
        # write the model 
        modelFile = 'model1.lp'
        if (self.lpFile):
            modelFile = self.lpFile;
        self.WeightReductionLPModelWithSetGraph.write(modelFile)
#         self.WeightReductionLPModelWithSetGraph.computeIIS();
#         self.WeightReductionLPModelWithSetGraph.write('model2.ilp')
#         return;
        # solve the model
        self.WeightReductionLPModelWithSetGraph.optimize()
        return;
        if self.WeightReductionLPModelWithSetGraph.status == gp.GRB.status.OPTIMAL:
            for (u,v) in self.edges:
                if self.LPVars[((u,v),)].x > 0:
                    print('(%s,%s)' % (u,v))
            print('=====')
            newWeights = {}
            for (u,v) in self.edges:
                text = '(%s,%s)' % (u,v)
                text = text + ', w = %s' % (self.newWeightsVars[u,v].x)
                newWeights[(u,v)] = self.newWeightsVars[u,v].x
                if self.newLPVars[((u,v),)].x > 0:
                    text = text + ' *'
                #print(text)
            self.newWeights = newWeights
    
    def solveWeightReductionLP(self):    
        
        # define objective 
        self.WeightReductionLPModel.setObjective(  gp.quicksum(self.LPVars[t]*self.g.allWeights[t]               for t     in self.g.allWeights) + 
                                                   gp.quicksum(self.newLPVars[((u,v),)]*self.newWeightsVars[u,v] for (u,v) in self.edges) - 
                                                   gp.quicksum(self.diffEdges[u,v]                               for (u,v) in self.edges) - 
                                                   gp.quicksum(self.newWeightsVars[u,v]*self.newWeightsVars[u,v] for (u,v) in self.edges) -
                                                   gp.quicksum(self.newLPVars[((u,v),)]*self.newLPVars[((u,v),)] for (u,v) in self.edges) ,gp.GRB.MAXIMIZE) 
        
        self.WeightReductionLPModel.update()
        # write the model 
        modelFile = 'model2.lp'
        if (self.lpFile):
            modelFile = self.lpFile;
        self.WeightReductionLPModel.write(modelFile)
#         self.WeightReductionLPModel.computeIIS();
#         self.WeightReductionLPModel.write('model2.ilp')
#         return 
        # solve the model
        self.WeightReductionLPModel.optimize()
        if self.WeightReductionLPModel.status == gp.GRB.status.OPTIMAL:
            for (u,v) in self.edges:
                if self.LPVars[((u,v),)].x > 0:
                    print('(%s,%s)' % (u,v))
            print('=====')
            newWeights = {}
            for (u,v) in self.edges:
                text = '(%s,%s)' % (u,v)
                text = text + ', w = %s' % (self.newWeightsVars[u,v].x)
                newWeights[(u,v)] = self.newWeightsVars[u,v].x
                if self.newLPVars[((u,v),)].x > 0:
                    text = text + ' *'
                #print(text)
            self.newWeights = newWeights

    
    def addProjectiveConstrs(self,nodes,model,y,constName):
        for u in nodes:
            for v in nodes:
                # only run for u > v 
                if v <= u:
                    continue
                span = range(u,v+1)
                notInSpan = filter(lambda x:x not in span, nodes)
                innerSpan = range(u+1,v)
                #notInInnerSpan = filter(lambda x:x not in innerSpan, nodes)
                # constraint for (u,v),(v,u) \in E
                for k in notInSpan:
                    if k > 0:
                        # k's parent cannot be inside the span
                        model.addConstr(gp.quicksum(y[(j,k)] for j in innerSpan) <= 1 - y[(u,v)],'%s_%s_in_%s_%s_parent' % (u,v,constName,k))
                        if u > 0:
                            model.addConstr(gp.quicksum(y[(j,k)] for j in innerSpan) <= 1 - y[(v,u)],'%s_%s_in_%s_%s_parent' % (v,u,constName,k))
                for k in innerSpan:
                    # k's parent cannot be outside of the span
                    model.addConstr(gp.quicksum(y[(j,k)] for j in notInSpan) <= 1 - y[(u,v)],'%s_%s_in_%s_%s_parent' % (u,v,constName,k))
                    if u > 0:
                        model.addConstr(gp.quicksum(y[(j,k)] for j in notInSpan) <= 1 - y[(v,u)],'%s_%s_in_%s_%s_parent' % (v,u,constName,k))
                if u > 0:
                    # u's parent must be out of the span for (u,v) \in E
                    model.addConstr(gp.quicksum(y[(j,u)] for j in notInSpan) >=  y[(u,v)],'%s_%s_in_%s_%s_parent' % (u,v,constName,u))
                    # v's parent must out of span for (v,u) \in E
                    model.addConstr(gp.quicksum(y[(j,v)] for j in notInSpan) >=  y[(v,u)],'%s_%s_in_%s_%s_parent' % (u,v,constName,u))
    
    def addNonProjectiveConstrs(self,nodes,edges,y,model,constName):
        # first define the flow vars
        flowVars = {}

        for (u,v) in edges:
            flowVars[(u,v)] = model.addVar(vtype=gp.GRB.INTEGER, name='flow_%s_%s_%s' % (constName,u,v))
        model.update()
        
        # root sends n flow:
        model.addConstr(gp.quicksum(flowVars[(u,v)] for (u,v) in edges.select(0,'*')),gp.GRB.EQUAL,len(nodes) - 1,'%s_root_flow' % (constName))
        
        # every node consumes one unit of flow
        for node in nodes:
            if node == 0:
                continue
            model.addConstr(gp.quicksum(flowVars[(u,v)] for (u,v) in edges.select('*',node)),gp.GRB.EQUAL,
                            1 + gp.quicksum(flowVars[(u,v)] for (u,v) in edges.select(node,'*')),'%s_node_%s_flow' % (constName,node))
        
        # flow is 0 on disabled arcs
        for (u,v) in edges:
            model.addConstr(flowVars[(u,v)],gp.GRB.LESS_EQUAL,(len(nodes) - 1)*y[(u,v)],'%s_edge_%s_%s_flow' % (constName,u,v))
        return flowVars
    
    def addIncomingEdgesConstrs(self,nodes,edges,model,y,constName):
        # incoming edges constraints - every node except for 0 has one incoming edge
        for node in nodes:
            if node == 0:
                continue
            model.addConstr(gp.quicksum(y[(u,t)] for (u,t) in edges.select('*',node)), gp.GRB.EQUAL,1,'%s_inEdge_%s' % (constName,node))
    
def allNonEmptySubsets(feature):
    if len(feature) == 0:
        return
    out = [[]]
    for e in feature:
        out += [x+[e] for x in out]
    out.remove([])
    out2 = []
    for e in out:
        out2.append( tuple(e) )
    return out2

def cmpFeatures(x,y):
    if (len(x) < len(y)):
        return 1
    if (len(x) > len(y)):
        return -1
    return 0
