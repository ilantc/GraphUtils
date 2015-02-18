import networkx as nx
import re
import gurobipy as gp
from partsManager import partsManager

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
            if not self.partsManager.hasArc(u,v):
                totalNumRemoved += 1;
#                     print("removing edge: (" + str(u) + "," + str(v) + ")")
                G.remove_edge(u,v)
        # print("removed " + str(totalNumRemoved) + " edges");
        return G

    def readFile(self,infile):
        ins = open( infile, "r" )
        logfile = open("log.txt", "w")
        #print(infile)
        
        sentenceString = ins.next()
        sentence = sentenceString.split();
        # skip "#" char
        self.sentence = sentence[2:]
        self.n = len(self.sentence)
        
        goldHeads = ins.next().split("=");
        goldHeads = goldHeads[1].split(",");
        # remove last empty element
        goldHeads = goldHeads[:-1]
        self.goldHeads = goldHeads;
        
        optHeads = ins.next().split("=");
        optHeads = optHeads[1].split(",");
        # remove last empty element
        optHeads = optHeads[:-1]
        self.optHeads = optHeads;
        
        # line is something like: "(1,2),(3,5),4.25"
        for line in ins:
            matchObj = re.search(" # (\w+)$",line)
            dependencyType = matchObj.group(1)
#             print line, dependencyType
            # all edges of this feature
            edges = re.findall("\(\d+,\d+\)",line)
            v = re.findall("\),([-]?\d+[.\d+]*)",line)
            val = float(v[0])
            partVals = {'val':val}
            
            if dependencyType == "DEPENDENCYPART_ARC" or dependencyType == "DEPENDENCYPART_NEXTSIBL_LAST_SIB" \
                or dependencyType == "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD" or dependencyType == "DEPENDENCYPART_GRANDSIBL_NO_CHILDREN" \
                or dependencyType == "DEPENDENCYPART_NEXTSIBL_NO_SIBS":
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
                elif dependencyType == "DEPENDENCYPART_NEXTSIBL_NO_SIBS":
                    self.partsManager.createPart('nextSiblNoChild', partVals)
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
                else:
                    self.partsManager.createPart('nextSibl',partVals)
                    #part = parts.part_DEPENDENCYPART_NEXTSIBL(u,v1,v2,val)
                #self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_NEXTSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v'] = v
#                 part = parts.part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB(u,v,val)
#                 self.allParts.append(part)
                self.partsManager.createPart('firstSibl',partVals)
            elif dependencyType == "DEPENDENCYPART_GRANDPAR":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v = int(matchObj.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
                self.partsManager.createPart('grandParant',partVals)
#                 part = parts.part_DEPENDENCYPART_GRANDPAR(g,u,v,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj1 = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v1 = int(matchObj1.group(2))
                matchObj2 = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v2 = int(matchObj2.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
                self.partsManager.createPart('grandSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_GRANDSIBL(g,u,v1,v2,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj1 = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v = int(matchObj1.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
                self.partsManager.createPart('grandSiblFirstSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB(g,u,v,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_LAST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v = int(matchObj.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
                self.partsManager.createPart('grandSiblLastSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_GRANDSIBL_LAST_SIB(g,u,v,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v3 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
                partVals['v3'] = v3
                self.partsManager.createPart('triSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_TRISIBL(u,v1,v2,v3,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_LAST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
                self.partsManager.createPart('triSiblLastSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_TRISIBL_LAST_SIBS(u,v1,v2,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_FIRST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
                self.partsManager.createPart('triSiblFirstSibl',partVals)
#                 part = parts.part_DEPENDENCYPART_TRISIBL_FIRST_SIBS(u,v1,v2,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_TRISIBL_ONLY_CHILD":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v'] = v
                self.partsManager.createPart('triSiblOnlyChild',partVals)
#                 part = parts.part_DEPENDENCYPART_TRISIBL_ONLY_CHILD(u,v,val)
#                 self.allParts.append(part)
            elif dependencyType == "DEPENDENCYPART_HEADBIGRAM":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                prev_u = int(matchObj.group(1))
                partVals['u'] = u
                partVals['v'] = v
                partVals['prev_u'] = prev_u
                if (prev_u !=  v):
                    self.partsManager.createPart('headBigram',partVals)
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

    def createLP(self,projective,setGraphEdges,applyPositiveSlacks,alpha):
        
        model = gp.Model(self.modelName)
        graph = self.g.graph
        partsManager = self.g.partsManager
        edges = gp.tuplelist(graph.edges())
        nodes = graph.nodes()
        nonEdgeParts = []
        
        M = 1000
        # Create variables and objective
        z = {}
        # weights
        wplus = {}
#         wminus = {}
        # diff edges counters
        d = {}
        # slack variables
        slackVars = {}
        for p in partsManager.getAllParts():
            if p.type == 'arc':
                u = p.u
                v = p.v
                z[u,v]       = model.addVar(vtype=gp.GRB.BINARY,     name=('z_%s_%s' % (u,v)))
                wplus[u,v]   = model.addVar(vtype=gp.GRB.CONTINUOUS, name=('w+_%s_%s' % (u,v)), lb=-1e21)
#                 wminus[u,v]  = model.addVar(vtype=gp.GRB.CONTINUOUS, name=('w-_%s_%s' % (u,v)), lb=-1e21)
                d[u,v]       = model.addVar(vtype=gp.GRB.BINARY,     name=('d_%s_%s' % (u,v)))
            nonEdgeParts.append(p)
            slackVars[p] = model.addVar(vtype=gp.GRB.CONTINUOUS)
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(nodes,edges,model,z,'Z')        
        
        if (projective):
            # projectivity + no circles constraints
            self.addProjectiveConstrs(nodes,model,z,'Z',partsManager)
        else:
            # non proj constrs and vars
            self.LPFlowVars = self.addNonProjectiveConstrs(nodes,edges,z,model,'Z')
        
        # diff edges constraints
        for (u,v) in edges:
            isEdge = 0;
            if (u,v) in setGraphEdges:
                isEdge =1;
            model.addConstr(d[u,v] + z[u,v], gp.GRB.GREATER_EQUAL,isEdge,'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + isEdge, gp.GRB.GREATER_EQUAL,z[u,v],'d_y_z_%s_%s' % (u,v))
        
        # lower bounds on w constraints
        for part in partsManager.getAllParts():
            allSubparts = part.getAllSubParts()
            allW = part.val
            for p in allSubparts:
                try:
                    partType = p['type']
                except KeyError:
                    print allSubparts
                    print p
                    print part
                    raise
                if partsManager.hasPart(partType,p):
                    allW += partsManager.getPart(partType,p).val
            operator = gp.GRB.GREATER_EQUAL;
            if (allW < 0):
                operator = gp.GRB.LESS_EQUAL
            # print(self.g.graph.edges())
            allExistingEdges = part.getAllExistingEdges()
            allExistingEdges = filter(lambda (u,v): partsManager.hasArc(u,v),allExistingEdges)
            allNonExistingEdges = part.getAllNonExistingEdges(self.g.n)
            allNonExistingEdges = filter(lambda (u,v): partsManager.hasArc(u,v),allNonExistingEdges)
            if (len(allExistingEdges) + len(allNonExistingEdges) > 0):
#                 print "adding constr '" + str(part) + "', allExisting edges are:",allExistingEdges,", all non existing edges are:",allNonExistingEdges
                if allW < 0:
                    model.addConstr(gp.quicksum(wplus[u,v] for (u,v) in allExistingEdges) \
#                                     + gp.quicksum(wminus[u,v] for (u,v) in allNonExistingEdges)\
                                    - slackVars[part],\
                                    operator,allW,str(part))
                elif applyPositiveSlacks:
                    model.addConstr(gp.quicksum(wplus[u,v] for (u,v) in allExistingEdges) \
#                                     + gp.quicksum(wminus[u,v] for (u,v) in allNonExistingEdges) \
                                    + slackVars[part],\
                                    operator,allW,str(part))
                else:
                    model.addConstr(gp.quicksum(wplus[u,v] for (u,v) in allExistingEdges) \
#                                     + gp.quicksum(wminus[u,v] for (u,v) in allNonExistingEdges) \
                                    ,operator,allW,str(part))
        model.update()
                
        # define objective 
        model.setObjective(
#                            gp.quicksum(2*z[u,v]*(wplus[u,v] - wminus[u,v])                   for (u,v) in edges)          \
                           gp.quicksum(2*z[u,v]*wplus[u,v]                                     for (u,v) in edges)        \
                           - gp.quicksum(d[u,v]*alpha                                          for (u,v) in edges)        \
#                            - gp.quicksum((wplus[u,v] - wminus[u,v])*(wplus[u,v] - wminus[u,v]) for (u,v) in edges)        \
                           - gp.quicksum(wplus[u,v]*wplus[u,v]                                 for (u,v) in edges)        \
                           - gp.quicksum(M*slackVars[part]                                     for  part in nonEdgeParts) \
                           - gp.quicksum(z[u,v]*z[u,v]                                         for (u,v) in edges)        \
                           ,gp.GRB.MAXIMIZE) 
        
        model.update()
        
        self.model  = model
        self.LPVars = z
        self.edges  = edges
        self.nodes  = nodes
        self.wplus  = wplus
#         self.wminus = wminus
        self.slack  = slackVars
              
    def solve(self,verbose,fileName=None):    
        
        # write the model 
        modelFile = None
        if (self.lpFile):
            modelFile = self.lpFile;
        elif fileName:
            modelFile = fileName;
        if modelFile:
            self.model.write(modelFile)
        if not verbose:
            self.model.setParam('OutputFlag', False )
        # solve the model
        self.model.optimize()

        if self.model.status == gp.GRB.status.OPTIMAL:
            if verbose:
                for (u,v) in self.edges:
                    if self.LPVars[u,v].x > 0:
                        print('(%s,%s)' % (u,v))
                print('=====')
            newWeights = {}
            optEdges = []
            for (u,v) in self.edges:
                text = '(%s,%s)' % (u,v)
#                 newW = self.wplus[u,v].x - self.wminus[u,v].x
                newW = self.wplus[u,v].x
                text = text + ', w = %s' % (newW)
                newWeights[u,v] = newW
                if self.LPVars[u,v].x > 0:
                    optEdges.append((u,v))
                if verbose:
                    print(text)
            if verbose:
                print "====="
                for key in self.slack.keys():
                    if self.slack[key].x > 0.0:
                        print key,":",self.slack[key].x
            self.newWeights = newWeights
            self.optEdges = optEdges

    def getConflictingConstrsNames(self, model,edges,partsManager):
        edgeToSense = {}
        constrNamesToRemove = []
        for edge in edges:
            edgePart = partsManager.getPart('arc', {'u': edge[0], 'v': edge[1]})
            edgeSense = model.getConstrByName(str(edgePart)).getAttr(gp.GRB.Attr.Sense)
            edgeToSense[edge] = edgeSense
        for part in partsManager.getAllParts():
            allNonExistingEdges = part.getAllNonExistingEdges(self.g.n)
            if len(allNonExistingEdges) > 0:
                continue
            allExistingEdges = part.getAllExistingEdges()
            constrSense = model.getConstrByName(str(part)).getAttr(gp.GRB.Attr.Sense)
            for edge in allExistingEdges:
                edgeSense = edgeToSense[edge]
                if edgeSense == constrSense:
                    break
                constrNamesToRemove.append(str(part))
        return constrNamesToRemove

# inner functions for building the ILP

    def addProjectiveConstrs(self,nodes,model,y,constName,partsManager):
        for u in nodes:
            for v in nodes:
                # only run for u > v 
                if v <= u:
                    continue 
                span = range(u,v+1)
                notInSpan = filter(lambda x:x not in span, nodes)
                innerSpan = range(u+1,v)
                # constraint for (u,v),(v,u) \in E
                for k in notInSpan:
                    if k > 0:
                        kParentsInSpan = filter(lambda j: partsManager.hasArc(j,k),innerSpan)
                        if len(kParentsInSpan) > 0:
                            if partsManager.hasArc(u,v):
                                # k's parent cannot be inside the span
                                model.addConstr(gp.quicksum(y[j,k] for j in kParentsInSpan) <= 1 - y[u,v],'%s_%s_in_%s_%s_parent1' % (u,v,constName,k))
                            if partsManager.hasArc(v,u):
    #                             print kParentsInSpan , "u=",u,"v=",v 
                                model.addConstr(gp.quicksum(y[j,k] for j in kParentsInSpan) <= 1 - y[v,u],'%s_%s_in_%s_%s_parent2' % (v,u,constName,k))
                for k in innerSpan:
                    kParentsNotInSpan = filter(lambda j: partsManager.hasArc(j,k),notInSpan)
                    if len(kParentsNotInSpan) > 0:
                        if partsManager.hasArc(u,v):
                            # k's parent cannot be outside of the span
                            model.addConstr(gp.quicksum(y[j,k] for j in kParentsNotInSpan) <= 1 - y[u,v],'%s_%s_in_%s_%s_parent3' % (u,v,constName,k))
                        if partsManager.hasArc(v,u):
    #                         print kParentsNotInSpan , "u=",u,"v=",v,"k=",k
                            model.addConstr(gp.quicksum(y[j,k] for j in kParentsNotInSpan) <= 1 - y[v,u],'%s_%s_in_%s_%s_parent4' % (v,u,constName,k))
                if u > 0:
                    if partsManager.hasArc(u,v):
                        # u's parent must be out of the span for (u,v) \in E
                        uParentsNotInSpan = filter(lambda j: partsManager.hasArc(j,u),notInSpan)
                        model.addConstr(gp.quicksum(y[j,u] for j in uParentsNotInSpan) >=  y[u,v],'%s_%s_in_%s_%s_parent5' % (u,v,constName,u))
                    if partsManager.hasArc(v,u):
                        # v's parent must out of span for (v,u) \in E
                        vParentsNotInSpan = filter(lambda j: partsManager.hasArc(j,v),notInSpan)
                        model.addConstr(gp.quicksum(y[j,v] for j in vParentsNotInSpan) >=  y[v,u],'%s_%s_in_%s_%s_parent6' % (v,u,constName,v))
    
    def addNonProjectiveConstrs(self,nodes,edges,y,model,constName,partsManager):
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
    
    
    def createAndSolveOriginalLP(self,projective):
        
        model = gp.Model(self.modelName)
        graph = self.g.graph
        partsManager = self.g.partsManager
        edges = gp.tuplelist(graph.edges())
        nodes = graph.nodes()
        
        M = 1000
        # Create variables and objective
        z = {}
        sibs = {}
        gpnt = {}
        edge2val = {}
        sibs2val = {}
        gpnt2val = {}
        # slack variables
        for p in partsManager.getAllParts():
            if p.type == 'arc':
                u = p.u
                v = p.v
                z[u,v]       = model.addVar(vtype=gp.GRB.BINARY,     name=('z_%s_%s' % (u,v)))
                edge2val[u,v] = p.val
            elif p.type == 'sibl':
                u = p.u
                v1 = p.v1
                v2 = p.v2
                sibs[u,v1,v2] = model.addVar(vtype=gp.GRB.BINARY,     name=('sibs_%s_%s_%s' % (u,v1,v2)))
                sibs2val[u,v1,v2] = p.val
            elif p.type == 'grandParant':
                g = p.g
                u = p.u
                v = p.v
                gpnt[g,u,v] = model.addVar(vtype=gp.GRB.BINARY,     name=('gpnt_%s_%s_%s' % (g,u,v)))
                gpnt2val[g,u,v] = p.val
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(nodes,edges,model,z,'Z')        
        
        if (projective):
            # projectivity + no circles constraints
            self.addProjectiveConstrs(nodes,model,z,'Z',partsManager)
        else:
            # non proj constrs and vars
            self.LPFlowVars = self.addNonProjectiveConstrs(nodes,edges,z,model,'Z')
        
        # high order parts
        for (u,v1,v2) in sibs:
            model.addConstr(sibs[u,v1,v2], gp.GRB.LESS_EQUAL,z[u,v1])
            model.addConstr(sibs[u,v1,v2], gp.GRB.LESS_EQUAL,z[u,v2])
            model.addConstr(sibs[u,v1,v2], gp.GRB.GREATER_EQUAL,z[u,v1] + z[u,v2] - 1)
        
        for (g,u,v) in gpnt:
            model.addConstr(gpnt[g,u,v], gp.GRB.LESS_EQUAL,z[g,u])
            model.addConstr(gpnt[g,u,v], gp.GRB.LESS_EQUAL,z[u,v])
            model.addConstr(gpnt[g,u,v], gp.GRB.GREATER_EQUAL,z[g,u] + z[u,v] - 1)
        
        
        model.update()
                
        # define objective 
        model.setObjective(gp.quicksum(z[u,v]*edge2val[u,v]             for (u,v) in edges) + \
                           gp.quicksum(sibs[u,v1,v2]*sibs2val[u,v1,v2]  for (u,v1,v2) in sibs2val.keys()) + \
                           gp.quicksum(gpnt[u,v1,v2]*gpnt2val[u,v1,v2]  for (u,v1,v2) in gpnt2val.keys()) \
                           ,gp.GRB.MAXIMIZE) 
        
        model.update()
         
        model.setParam('OutputFlag', False )
        # solve the model
        model.optimize()

        if model.status == gp.GRB.status.OPTIMAL:
            optEdges = []
            for (u,v) in edges:
                if z[u,v].x > 0:
                    optEdges.append((u,v))    
        return optEdges

    def initGraph(self,n,w):
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(n + 1)) 
        
        # add edges and weights
        for (u,v) in w.keys():
            G.add_edge(u, v, {'weight': w[u,v]})        
        return G
    
    def contract(self,G,C_edges):
        C_nodes = [u for (u,_) in C_edges]
        subgraphNodes = filter(lambda node: node not in C_nodes, G.nodes())
        Gc = G.subgraph(subgraphNodes)
        newNode = "_".join(map(lambda node: str(node),C_nodes))
        Gc.add_node(newNode)
        scoreC = sum(G[u][v]['weight'] for (u,v) in C_edges)
        for node in subgraphNodes:
            edgesFromC = [(c,node) for c in filter(lambda cNode: G.has_edge(cNode,node),C_nodes)]
            if len(edgesFromC) > 0:
                (best_c,node) = max(edgesFromC, key = lambda (u,v): G[u][v]['weight'])
                Gc.add_edge(newNode,node,{'weight': G[best_c][node]['weight'], 'origU': best_c})
            
            edgesToC = [(node,c) for c in filter(lambda cNode: G.has_edge(node,cNode),C_nodes)]
            if len(edgesToC) > 0:
                bestScore = float('Inf') * (-1)
                bestCnode = 0
                for (node,c_node) in edgesToC:
                    filtered = filter(lambda (u,v): v == c_node,C_edges)
                    (c_u,_) = filtered[0]
                    score = G[node][c_node]['weight'] - G[c_u][c_node]['weight']
                    if score > bestScore:
                        bestScore = score
                        bestCnode = c_node
                Gc.add_edge(node,newNode,{'weight': bestScore + scoreC, 'origV': bestCnode})
        return {'G':Gc, 'newnode':newNode}
    
    def chuLiuEdmondsWrapper(self, n, w):
        G = self.initGraph(n,w)
        optG = self.chuLiuEdmonds(G)
        return optG
    
    def chuLiuEdmonds(self,G):
        edges = G.edges()
        bestInEdges = []
        for node in G.nodes():
            if node == 0:
                continue
            allInNodes = [u for (u,_) in filter(lambda (u,v): v == node, edges)]
            bestP = max(allInNodes, key = lambda u: G[u][node]['weight'])
            bestInEdges.append((bestP,node,G.get_edge_data(bestP,node)))
        newG = nx.DiGraph()
        newG.add_nodes_from(G.nodes())
        newG.add_edges_from(bestInEdges)
        
        # get the first cycle in newG
        cs = list(nx.simple_cycles(newG))
        if len(cs) == 0:
            return newG
        c = max(cs, key = lambda circle: len(circle))
        C_edges = []
        for c_node_index in range(len(c) - 1):
            C_edges.append((c[c_node_index],c[c_node_index + 1]))
        C_edges.append((c[-1],c[0]))
        contractOutput = self.contract(G, C_edges)
        Gc = contractOutput['G']
        newNode = contractOutput['newnode']
        Gopt = self.chuLiuEdmonds(Gc)
        
        # now we need to take care of the new graph:
        # 1) remove the dummy node that was contracted
        newNodeInEdge = filter(lambda (u,v): v == newNode,Gopt.edges())
        if len(newNodeInEdge)==0:
            print "oh no"
        newNodeInEdgeU = newNodeInEdge[0][0]
        newNodeInEdgeV = newNodeInEdge[0][1]
        newNodeInEdgeData = Gc.get_edge_data(newNodeInEdgeU,newNodeInEdgeV)
        
        newNodeOutEdges = filter(lambda (u,v): u == newNode,Gopt.edges())
        edgesToAdd = []
        for i in range(len(newNodeOutEdges)):
            newNodeOutEdgeU = newNodeOutEdges[i][0]
            newNodeOutEdgeV = newNodeOutEdges[i][1]
            newNodeOutEdgeData = Gc.get_edge_data(newNodeOutEdgeU,newNodeOutEdgeV)
            edgesToAdd.append({'u':newNodeOutEdgeU, 'v':newNodeOutEdgeV, 'data': newNodeOutEdgeData})
        
        Gopt.remove_node(newNode)
        
        # 2) add the edges from C
        for (u,v) in C_edges:
            Gopt.add_edge(u,v,G.get_edge_data(u,v))
        
        # 3) remove the edge from C that cones just before the entry point to C in the 
        # contracted graph, 
        uToRemove = c[c.index(newNodeInEdgeData['origV']) - 1]
        Gopt.remove_edge(uToRemove,newNodeInEdgeData['origV'])
        
        # 4) add the incoming edge to the contracted node back to the graph
        Gopt.add_edge(newNodeInEdgeU, newNodeInEdgeData['origV'], G.get_edge_data(newNodeInEdgeU, newNodeInEdgeData['origV']))
        
        # 5) if there was an outgoing edge from the contracted node, add it as well
        for edgeToAdd in edgesToAdd:
            Gopt.add_edge(edgeToAdd['data']['origU'], edgeToAdd['v'], G.get_edge_data(edgeToAdd['data']['origU'], edgeToAdd['v']))
        
        return Gopt

    def eisnerProjective(self,n,w):
        G = self.initGraph(n,w)
        right = "right"
        left = "left"
        complete = "complete"
        incomplete = "incomplete"
        minusInf = float('Inf')* (-1)
        n = n + 1
        C = {}
        bp = {}
        # handle span size 0
        for u in range(0,n):
            C[u] = {}
            bp[u] = {}
            C[u][u] = {}
            C[u][u][right] = {}
            C[u][u][left] = {}
            C[u][u][right][complete] = 0.0
#             C[u][u][right][incomplete] = 0.0
            C[u][u][left][complete] = 0.0
#             C[u][u][left][incomplete] = 0.0
        
        for spanSize in range(1,n):
            for u in range(0,n):
                rightIndex = u + spanSize
                # right span 
                if rightIndex < n:
                    C[u][rightIndex] = {}
                    C[u][rightIndex][right] = {}
                    bp[u][rightIndex] = {}
                    bp[u][rightIndex][right] = {}
                                        
                    # incomplete
                    if G.has_edge(u, rightIndex):
                        bestValIncomplete = C[u][u][right][complete] + C[rightIndex][u+1][left][complete] + G[u][rightIndex]['weight']
                        bestBpIncomplete = u
                        for q in range(u + 1,rightIndex):
                            currValIncomplete = C[u][q][right][complete] + C[rightIndex][q + 1][left][complete] + G[u][rightIndex]['weight']
                            if currValIncomplete > bestValIncomplete:
                                bestValIncomplete = currValIncomplete
                                bestBpIncomplete = q
                    else:
                        bestValIncomplete = minusInf
                        bestBpIncomplete = -1
                    # save the best
                    C[u][rightIndex][right][incomplete] = bestValIncomplete
                    bp[u][rightIndex][right][incomplete] = bestBpIncomplete
                    
                    # complete
                    bestBpComplete = rightIndex
                    bestValComplete = C[u][rightIndex][right][incomplete] + C[rightIndex][rightIndex][right][complete]
                    for q in range(u + 1,rightIndex):
                        currValComplete = C[u][q][right][incomplete] + C[q][rightIndex][right][complete]
                        if currValComplete > bestValComplete:
                            bestValComplete = currValComplete
                            bestBpComplete = q
                    # save the best
                    C[u][rightIndex][right][complete] = bestValComplete
                    bp[u][rightIndex][right][complete] = bestBpComplete
                    
                leftIndex = u - spanSize
                # left span 
                if leftIndex > 0:
                    C[u][leftIndex] = {}
                    C[u][leftIndex][left] = {}
                    bp[u][leftIndex] = {}
                    bp[u][leftIndex][left] = {}
                    
                    # incomplete
                    if G.has_edge(u,leftIndex):
                        bestValIncomplete = C[leftIndex][leftIndex][right][complete] + C[u][leftIndex + 1][left][complete] + G[u][leftIndex]['weight']
                        bestBpIncomplete = leftIndex
                        for q in range(leftIndex,u):
                            currValIncomplete = C[leftIndex][q][right][complete] + C[u][q + 1][left][complete] + G[u][leftIndex]['weight']
                            if currValIncomplete > bestValIncomplete:
                                bestValIncomplete = currValIncomplete
                                bestBpIncomplete = q
                    else:
                        bestValIncomplete = minusInf
                        bestBpIncomplete = -1
                    # save the best
                    C[u][leftIndex][left][incomplete] = bestValIncomplete
                    bp[u][leftIndex][left][incomplete] = bestBpIncomplete
                    
                    # complete
                    bestBpComplete = leftIndex
                    bestValComplete = C[leftIndex][leftIndex][left][complete] + C[u][leftIndex][left][incomplete]
                    for q in range(leftIndex,u):
                        currValComplete = C[q][leftIndex][left][complete] + C[u][q][left][incomplete]
                        if currValComplete > bestValComplete:
                            bestValComplete = currValComplete
                            bestBpComplete = q
                    # save the best
                    C[u][leftIndex][left][complete] = bestValComplete
                    bp[u][leftIndex][left][complete] = bestBpComplete
        
        uKey = 'u'
        vKey = 'v'
        directionKey = 'direction'
        typeKey = 'type'
        spansToCheck = [{uKey:0,vKey:n - 1,directionKey:right,typeKey:complete}]
        Gopt = nx.DiGraph()
        Gopt.add_nodes_from(range(n))
        
        while len(spansToCheck) > 0:
            spanToCheck = spansToCheck.pop()
            u = spanToCheck[uKey]
            v = spanToCheck[vKey]
            spanType = spanToCheck[typeKey]
            direction = spanToCheck[directionKey]
            otherDirection = right if direction == left else left
            if u == v:
                continue
            q = bp[u][v][direction][spanType]
            if spanType == complete:
                if direction == right:
                    spansToCheck.append({uKey:u,vKey:q,directionKey:direction,typeKey:incomplete})
                    spansToCheck.append({uKey:q,vKey:v,directionKey:direction,typeKey:complete})
                else:
                    spansToCheck.append({uKey:q,vKey:v,directionKey:direction,typeKey:complete})
                    spansToCheck.append({uKey:u,vKey:q,directionKey:direction,typeKey:incomplete})
            else:
                if direction == right:
                    spansToCheck.append({uKey:u,vKey:q,directionKey:direction,typeKey:complete}) 
                    spansToCheck.append({uKey:v,vKey:q+1,directionKey:otherDirection,typeKey:complete})
                else:
                    spansToCheck.append({uKey:v,vKey:q,directionKey:otherDirection,typeKey:complete})
                    spansToCheck.append({uKey:u,vKey:q+1,directionKey:direction,typeKey:complete})
                Gopt.add_edge(u, v, G.get_edge_data(u, v)) 
            
        return Gopt

# unused functions 

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