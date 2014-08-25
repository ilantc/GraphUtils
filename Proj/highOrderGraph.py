import networkx as nx
import random
import re
import gurobipy as gp

class DiGraph:
    
    def __init__(self,n,infile=None):
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
        self.infile  = infile
        
    def addWeights(self):
        if self.infile:
            self.readFile(self.infile)
        else:
            for (u1,v1) in self.graph.edges():
                # set weight for this edge
                val = random.random() * 3
                element = ((u1,v1),)
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

    def readFile(self,infile):
        
        ins = open( infile, "r" )

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
        
    def writeFile(self,f):
        outFile = open(f, "w")
        for feat in self.allWeights:
            #print("F is: ")
            text = ""
            for (u,v) in feat:
                #print("\tU is " + str(u) + ", V is " + str(v))
                text = text + "(" + str(u) + "," + str(v) + "),"
            text = text + str(self.allWeights[feat]) + "\n"
            outFile.write(text)
        outFile.close()

class LPMaker:
    
    def __init__(self,graph,modelName = 'lpModel'):
        self.modelName = modelName
        self.g = graph
        
    # create the lp
    def createLP(self):
        
        model = gp.Model(self.modelName)
        
        edges = gp.tuplelist(self.g.graph.edges())
        nodes = self.g.graph.nodes()
        
        # Create variables and objective
        z = {}
        modelOrder = 0;
        for feature in self.g.allWeights:
            z[feature] = model.addVar(vtype=gp.GRB.BINARY, name='z_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature]))
            if (len(feature) > modelOrder):
                modelOrder = len(feature)
        self.order = modelOrder
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        for node in nodes:
            if node == 0:
                continue
#             print(edges.select('*',node))
#             print(gp.quicksum(z[u,t] for (u,t) in edges.select('*',node)))
            model.addConstr(gp.quicksum(z[((u,t),)] for (u,t) in edges.select('*',node)), gp.GRB.EQUAL,1,'inEdge_%s' % (node))
        
        # node 0 has no incoming edge
#         model.addConstr(gp.quicksum(z[(u,t)] for (u,t) in edges.select('*',0)),gp.GRB.EQUAL,0,'noInEdge_0')
        
        # projectivity + no circles constraints
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
                        model.addConstr(gp.quicksum(z[((j,k),)] for j in innerSpan) <= 1 - z[((u,v),)],'%s_%s_in_Z_%s_parent' % (u,v,k))
                        if u > 0:
                            model.addConstr(gp.quicksum(z[((j,k),)] for j in innerSpan) <= 1 - z[((v,u),)],'%s_%s_in_Z_%s_parent' % (v,u,k))
                for k in innerSpan:
                    # k's parent cannot be outside of the span
                    model.addConstr(gp.quicksum(z[((j,k),)] for j in notInSpan) <= 1 - z[((u,v),)],'%s_%s_in_Z_%s_parent' % (u,v,k))
                    if u > 0:
                        model.addConstr(gp.quicksum(z[((j,k),)] for j in notInSpan) <= 1 - z[((v,u),)],'%s_%s_in_Z_%s_parent' % (v,u,k))
                if u > 0:
                    # u's parent must be out of the span for (u,v) \in E
                    model.addConstr(gp.quicksum(z[((j,u),)] for j in notInSpan) >=  z[((u,v),)],'%s_%s_in_Z_%s_parent' % (u,v,u))
                    # v's parent must out of span for (v,u) \in E
                    model.addConstr(gp.quicksum(z[((j,v),)] for j in notInSpan) >=  z[((v,u),)],'%s_%s_in_Z_%s_parent' % (u,v,u))
        self.LPModel = model
        self.LPVars = z
            
    def solveLP(self):   
        self.LPModel.setObjective(gp.quicksum(self.LPVars[t]*self.g.allWeights[t] for t in self.g.allWeights),gp.GRB.MAXIMIZE) 
        # solve the model
        self.LPModel.update()
        self.LPModel.write("simpleModel.lp")
        self.LPModel.optimize()
        if self.LPModel.status == gp.GRB.status.OPTIMAL:
            for (u,v) in self.g.graph.edges():
                if self.LPVars[((u,v),)].x > 0:
                    print('(%s,%s)' % (u,v))
        
    def createWeightReductionLP(self):
        self.createLP()
        model = self.LPModel
        edges = gp.tuplelist(self.g.graph.edges())
        nodes = self.g.graph.nodes()
        
        # add the new variables:
        # new weights
        w = {}
        # incidence vector for the new graph
        y = {}
        # diff edges counters
        d = {}
        for (u,v) in edges:
            w[u,v] = model.addVar(vtype=gp.GRB.CONTINUOUS,lb=0, name='w_%s_%s' % (u,v))
            y[u,v] = model.addVar(vtype=gp.GRB.BINARY, name='y_%s_%s' % (u,v))
            d[u,v] = model.addVar(vtype=gp.GRB.BINARY, name='d_%s_%s' % (u,v))
            
        
        model.update()
        
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        for node in nodes:
            if node == 0:
                continue
#             print(edges.select('*',node))
#             print(gp.quicksum(z[u,t] for (u,t) in edges.select('*',node)))
            model.addConstr(gp.quicksum(y[u,t] for (u,t) in edges.select('*',node)), gp.GRB.EQUAL,1,'newGraphInEdge_%s' % (node))
        
        # node 0 has no incoming edge
#         model.addConstr(gp.quicksum(y[(u,t)] for (u,t) in edges.select('*',0)),gp.GRB.EQUAL,0,'newGraphNoInEdge_0')
        
        # projectivity + no circles constraints
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
                        model.addConstr(gp.quicksum(y[j,k] for j in innerSpan) <= 1 - y[u,v],'%s_%s_in_Y_%s_parent' % (u,v,k))
                        if u > 0:
                            model.addConstr(gp.quicksum(y[j,k] for j in innerSpan) <= 1 - y[v,u],'%s_%s_in_Y_%s_parent' % (v,u,k))
                for k in innerSpan:
                    # k's parent cannot be outside of the span
                    model.addConstr(gp.quicksum(y[j,k] for j in notInSpan) <= 1 - y[u,v],'%s_%s_in_Y_%s_parent' % (u,v,k))
                    if u > 0:
                        model.addConstr(gp.quicksum(y[j,k] for j in notInSpan) <= 1 - y[v,u],'%s_%s_in_Y_%s_parent' % (v,u,k))
                if u > 0:
                    # u's parent must be out of the span for (u,v) \in E
                    model.addConstr(gp.quicksum(y[j,u] for j in notInSpan) >=  y[u,v],'%s_%s_in_Y_%s_parent' % (u,v,u))
                    # v's parent must out of span for (v,u) \in E
                    model.addConstr(gp.quicksum(y[j,v] for j in notInSpan) >=  y[v,u],'%s_%s_in_Y_%s_parent' % (u,v,u))
        
        # diff edges constraints
        for (u,v) in edges:
            model.addConstr(d[u,v] + y[u,v], gp.GRB.GREATER_EQUAL,self.LPVars[((u,v),)],'d_z_y_%s_%s' % (u,v))
            model.addConstr(d[u,v] + self.LPVars[((u,v),)], gp.GRB.GREATER_EQUAL,y[u,v],'d_y_z_%s_%s' % (u,v))
        
        # lower bounds on w constraints
        for feature in self.LPVars:
            allSubsets = allNonEmptySubsets(feature)
            allW = 0
            for f in allSubsets:
                if self.g.allWeights.has_key(f):
                    allW += self.g.allWeights[f]
                else:
                    print('Oh no!')
            model.addConstr(gp.quicksum(w[u,v] for (u,v) in feature),gp.GRB.GREATER_EQUAL,allW,'subset_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature])) 
                 
           
        model.setObjective(gp.quicksum(self.LPVars[t]*self.g.allWeights[t] for t in self.g.allWeights) + 
                           gp.quicksum(y[u,v]*w[u,v] for (u,v) in edges) - 
                           gp.quicksum(d[u,v] for (u,v) in edges) - 
                           gp.quicksum(w[u,v]*w[u,v] for (u,v) in edges) -
                           gp.quicksum(y[u,v]*y[u,v] for (u,v) in edges) ,gp.GRB.MAXIMIZE) 
        model.update()
        self.WeightReductionLPModel = model
        self.WeightReductionLPModel.write('model.lp')
        self.newWeightsVars = w
        self.newLPVars = y
        self.diffEdges = d
        
    def solveWeightReductionLP(self):    
        # solve the model
        self.WeightReductionLPModel.optimize()
        if self.WeightReductionLPModel.status == gp.GRB.status.OPTIMAL:
            for (u,v) in self.g.graph.edges():
                if self.LPVars[((u,v),)].x > 0:
                    print('(%s,%s)' % (u,v))
            print('=====')
            newWeights = {}
            for (u,v) in self.g.graph.edges():
                text = '(%s,%s)' % (u,v)
                text = text + ', w = %s' % (self.newWeightsVars[u,v].x)
                newWeights[(u,v)] = self.newWeightsVars[u,v].x
                if self.newLPVars[u,v].x > 0:
                    text = text + ' *'
                print(text)
            self.newWeights = newWeights

    def printWs(self):
        for (u,v) in self.g.graph.edges():
            newW = self.newWeights[(u,v)]
            allW = filter(lambda x: (u,v) in x,self.g.allWeights)

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


