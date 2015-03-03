import networkx as nx 

class inference(object):


    def __init__(self, w,n):
        self.w = w
        self.n = n
    
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
    
    def chuLiuEdmondsWrapper(self):
        G = self.initGraph(self.n,self.w)
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

    def eisnerProjective(self):
        G = self.initGraph(self.n,self.w)
        right = "right"
        left = "left"
        complete = "complete"
        incomplete = "incomplete"
        minusInf = float('Inf')* (-1)
        n = self.n + 1
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

    def greedyMinLoss(self):
            arc2parts = {}
            part2Arcs = {}
            
            for arc in self.partsManager.getArcs():
                arc2parts[arc] = []
                
            for part in self.partsManager.getNonArcs():
                part2Arcs[part] = []
                allArcs = filter(lambda subPart: subPart[type] == 'arc', part.getAllSubParts())
                for arc in allArcs:
                    arcPart = self.partsManager.getArc(arc['u'], arc['v'])
                    arc2parts[arcPart].append(part)
                    part2Arcs[part].append(arcPart)
            
            bestScore = float('Inf')
            bestPart = Nonen
