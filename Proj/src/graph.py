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
        
        dependencyType2partKey = {"DEPENDENCYPART_ARC"                      : 'arc',                    \
                                  "DEPENDENCYPART_NEXTSIBL_LAST_SIB"        : 'lastSibl',               \
                                  "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD"   : 'grandParantNoGrandChild',\
                                  "DEPENDENCYPART_GRANDSIBL_NO_CHILDREN"    : 'grandSiblNoSibl',        \
                                  "DEPENDENCYPART_NEXTSIBL_NO_SIBS"         : 'nextSiblNoChild',        \
                                  "DEPENDENCYPART_SIBL"                     : 'sibl',                   \
                                  "DEPENDENCYPART_NEXTSIBL"                 : 'nextSibl',               \
                                  "DEPENDENCYPART_NEXTSIBL_FIRST_SIB"       : 'firstSibl',              \
                                  "DEPENDENCYPART_GRANDPAR"                 : 'grandParant',            \
                                  "DEPENDENCYPART_GRANDSIBL"                : 'grandSibl',              \
                                  "DEPENDENCYPART_GRANDSIBL_FIRST_SIB"      : 'grandSiblFirstSibl',     \
                                  "DEPENDENCYPART_GRANDSIBL_LAST_SIB"       : 'grandSiblLastSibl',      \
                                  "DEPENDENCYPART_TRISIBL"                  : 'triSibl',                \
                                  "DEPENDENCYPART_TRISIBL_LAST_SIBS"        : 'triSiblLastSibl',        \
                                  "DEPENDENCYPART_TRISIBL_FIRST_SIBS"       : 'triSiblFirstSibl',       \
                                  "DEPENDENCYPART_TRISIBL_ONLY_CHILD"       : 'triSiblOnlyChild',       \
                                  "DEPENDENCYPART_HEADBIGRAM"               : 'headBigram'}
        def parseEdges(edges):
            nodes = []
            for edge in edges:
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edge)
                nodes.append(int(matchObj.group(1)))
                nodes.append(int(matchObj.group(2)))
            return nodes
        # line is something like: "(1,2),(3,5),4.25"
        for line in ins:
            matchObj = re.search(" # (\w+)$",line)
            dependencyType = matchObj.group(1)
            # all edges of this feature
            edges = re.findall("\(\d+,\d+\)",line)
            v = re.findall("\),([-]?\d+[.\d+]*)",line)
            val = float(v[0])
            partVals = {}
            if dependencyType in ["DEPENDENCYPART_ARC", "DEPENDENCYPART_NEXTSIBL_LAST_SIB", "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD",\
                                  "DEPENDENCYPART_GRANDSIBL_NO_CHILDREN", "DEPENDENCYPART_NEXTSIBL_NO_SIBS"]:
                nodes = parseEdges([edges[0]])
                partVals['u'] = nodes[0]
                partVals['v'] = nodes[1]
            elif dependencyType in ["DEPENDENCYPART_SIBL", "DEPENDENCYPART_NEXTSIBL"]:
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
            elif dependencyType == "DEPENDENCYPART_NEXTSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v'] = v
            elif dependencyType == "DEPENDENCYPART_GRANDPAR":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v = int(matchObj.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
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
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_FIRST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj1 = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v = int(matchObj1.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
            elif dependencyType == "DEPENDENCYPART_GRANDSIBL_LAST_SIB":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                g = int(matchObj.group(1))
                u = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v = int(matchObj.group(2))
                partVals['g'] = g
                partVals['u'] = u
                partVals['v'] = v
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
            elif dependencyType == "DEPENDENCYPART_TRISIBL_LAST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
            elif dependencyType == "DEPENDENCYPART_TRISIBL_FIRST_SIBS":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v1 = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[2])
                v2 = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v1'] = v1
                partVals['v2'] = v2
            elif dependencyType == "DEPENDENCYPART_TRISIBL_ONLY_CHILD":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                partVals['u'] = u
                partVals['v'] = v
            elif dependencyType == "DEPENDENCYPART_HEADBIGRAM":
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[0])
                u = int(matchObj.group(1))
                v = int(matchObj.group(2))
                matchObj = re.match('^\s*\((\d+),(\d+)\)\s*$', edges[1])
                prev_u = int(matchObj.group(1))
                partVals['u'] = u
                partVals['v'] = v
                partVals['prev_u'] = prev_u
                if (prev_u ==  v):
                    partVals = {}
            if partVals != {}:
                partVals['val'] = val
                self.partsManager.createPart(dependencyType2partKey[dependencyType],partVals)
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
            self.LPFlowVars = self.addNonProjectiveConstrs(nodes,edges,z,model,'Z',partsManager)
        # diff edges constraints
        for (u,v) in edges:
            isEdge = 0;
            if (u,v) in setGraphEdges:
                isEdge =1;
            model.addConstr(d[u,v] + z[u,v], gp.GRB.GREATER_EQUAL,isEdge,'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + isEdge, gp.GRB.GREATER_EQUAL,z[u,v],'d_y_z_%s_%s' % (u,v))
        
#         # for z to be the incoming graph 
#         for (u,v) in setGraphEdges:
#             if (u,v) in edges:
#                 model.addConstr(z[u,v], gp.GRB.GREATER_EQUAL,1,'z_%s_%s_eq_1' % (u,v))
        
        # lower bounds on w constraints
        for part in filter(lambda prt: prt.type in ["arc","grandParant"],partsManager.getAllParts()):
            
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

#         model.setObjective(- gp.quicksum(wplus[u,v]*wplus[u,v] for (u,v) in edges)\
#                            - gp.quicksum(M*slackVars[part]     for  part in nonEdgeParts),gp.GRB.MAXIMIZE)
        
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

# unused functions 
