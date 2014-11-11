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
            # remove edges that are not in the model
            for (u,v) in self.graph.edges():
                if not self.graph.allWeights[((u,v),)]:
                    self.graph.remove_edge(u,v)
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
            if (self.allWeights[tuple(feature)]):
                val = val + self.allWeights[tuple(feature)]          
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
    
    def createLP(self,projective):
        
        model = gp.Model(self.modelName)
        
        edges = gp.tuplelist(self.g.graph.edges())
        nodes = self.g.graph.nodes()
        
        # Create variables and objective
        z = {}

        for feature in self.g.allWeights:
            z[feature] = model.addVar(vtype=gp.GRB.BINARY, name='z_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature]))
        model.update()
        
        # incoming edges constraints - every node except for 0 has one incoming edge
        self.addIncomingEdgesConstrs(nodes,edges,model,z,'Z')        
        
        if (projective):
            # projectivity + no circles constraints
            self.addProjectiveConstrs(nodes,model,z,'Z')
        else:
            # non proj constrs and vars
            self.LPFlowVars = self.addNonProjectiveConstrs(nodes,edges,z,model,'Z')
        
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
            w[u,v]      = model.addVar(vtype=gp.GRB.CONTINUOUS, name='w_%s_%s' % (u,v))
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
                    print('Oh no!')
            operator = gp.GRB.GREATER_EQUAL;
            if (allW < 0):
                operator = gp.GRB.LESS_EQUAL
            
            model.addConstr(gp.quicksum(w[u,v] for (u,v) in feature),operator,allW,'subset_%s' % '_'.join([str(u) + '_' + str(v) for (u,v) in feature])) 
                 
        self.WeightReductionLPModel = model
        self.newWeightsVars = w
        self.newLPVars = y
        self.diffEdges = d
              
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
    
    def solveWeightReductionLP(self):    
        
        # define objective 
        self.WeightReductionLPModel.setObjective(  gp.quicksum(self.LPVars[t]*self.g.allWeights[t]               for t     in self.g.allWeights) + 
                                                   gp.quicksum(self.newLPVars[((u,v),)]*self.newWeightsVars[u,v] for (u,v) in self.edges) - 
                                                   gp.quicksum(self.diffEdges[u,v]                               for (u,v) in self.edges) - 
                                                   gp.quicksum(self.newWeightsVars[u,v]*self.newWeightsVars[u,v] for (u,v) in self.edges) -
                                                   gp.quicksum(self.newLPVars[((u,v),)]*self.newLPVars[((u,v),)] for (u,v) in self.edges) ,gp.GRB.MAXIMIZE) 
        
        self.WeightReductionLPModel.update()
        # write the model 
        self.WeightReductionLPModel.write('model1.lp')
        
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
                        model.addConstr(gp.quicksum(y[((j,k),)] for j in innerSpan) <= 1 - y[((u,v),)],'%s_%s_in_%s_%s_parent' % (u,v,constName,k))
                        if u > 0:
                            model.addConstr(gp.quicksum(y[((j,k),)] for j in innerSpan) <= 1 - y[((v,u),)],'%s_%s_in_%s_%s_parent' % (v,u,constName,k))
                for k in innerSpan:
                    # k's parent cannot be outside of the span
                    model.addConstr(gp.quicksum(y[((j,k),)] for j in notInSpan) <= 1 - y[((u,v),)],'%s_%s_in_%s_%s_parent' % (u,v,constName,k))
                    if u > 0:
                        model.addConstr(gp.quicksum(y[((j,k),)] for j in notInSpan) <= 1 - y[((v,u),)],'%s_%s_in_%s_%s_parent' % (v,u,constName,k))
                if u > 0:
                    # u's parent must be out of the span for (u,v) \in E
                    model.addConstr(gp.quicksum(y[((j,u),)] for j in notInSpan) >=  y[((u,v),)],'%s_%s_in_%s_%s_parent' % (u,v,constName,u))
                    # v's parent must out of span for (v,u) \in E
                    model.addConstr(gp.quicksum(y[((j,v),)] for j in notInSpan) >=  y[((v,u),)],'%s_%s_in_%s_%s_parent' % (u,v,constName,u))
    
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
            model.addConstr(flowVars[(u,v)],gp.GRB.LESS_EQUAL,(len(nodes) - 1)*y[((u,v),)],'%s_edge_%s_%s_flow' % (constName,u,v))
        return flowVars
    
    def addIncomingEdgesConstrs(self,nodes,edges,model,y,constName):
        # incoming edges constraints - every node except for 0 has one incoming edge
        for node in nodes:
            if node == 0:
                continue
            model.addConstr(gp.quicksum(y[((u,t),)] for (u,t) in edges.select('*',node)), gp.GRB.EQUAL,1,'%s_inEdge_%s' % (constName,node))
    
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
