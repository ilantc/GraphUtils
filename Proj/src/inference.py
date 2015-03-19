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


####################################################################
    def getRoot(self,u,possibleRoots):
        if u == 0:
            return u
        uRoots = possibleRoots[u].keys()
        if len(uRoots) == 1:
            return uRoots[0]
        else:
            return u

    def getLoss(self,G,u,v,w,possibleRoots,w_rev,iterNum):
        
        def addToEdgesLost(lostU,lostV,loss,edgesLost,w,u,v):
            if (lostU,lostV) == (u,v):
                raise Exception("trying to add (u,v)=(" + str(u) + "," + str(v) + ") to edgesLost")
            loss += w[lostU][lostV]
            edgesLost.append((lostU,lostV))
            return loss
            
#         if (iterNum == 19) and ((u,v) == (4,3)):
#             print "break now!"
        edgesLost = []
        loss = 0.0
        uRoot = self.getRoot(u, possibleRoots)
        vRoot = self.getRoot(v, possibleRoots)
        for s in w.keys():
            sRoot = self.getRoot(s, possibleRoots)
            if sRoot == vRoot:
#                 if s == u:
#                     raise Exception(str(u) + ' root is ' + str(v) + ', but (' + str(u) + ',' + str(v) + ') was not removed')
                if uRoot in w[s].keys():
                    if (s,uRoot) not in edgesLost:
                        loss = addToEdgesLost(s,uRoot,loss,edgesLost,w,u,v)
#                 for t in w[s].keys():
#                     tRoot = self.getRoot(t, possibleRoots)
#                     if tRoot == uRoot:
#                         try:
#                             if (s,t) not in edgesLost:
#                                 loss = addToEdgesLost(s,t,loss,edgesLost,w,u,v)
#                         except KeyError:
#                             raise Exception("key error - when adding (" + str(s) + ',' + str(t) + ") to edges lost with (u,v) = (" + str(u) + "," + str(v) +")")
            if s != 0 and (s == uRoot):
                if v in w_rev[s] and (v,s) not in edgesLost:
                    try:
                        loss = addToEdgesLost(v,s,loss,edgesLost,w,u,v)
                    except KeyError:
                        raise Exception("key error - when adding (" + str(v) + ',' + str(s) + ") to edges lost with (u,v) = (" + str(u) + "," + str(v) +")")
            
        for s in w_rev[v].keys():
            if s != u and (s,v) not in edgesLost:
                loss = addToEdgesLost(s,v,loss,edgesLost,w,u,v)
#         for otherU in w.keys():
#             if otherU == u:
#                 continue
#             for otherV in w[otherU].keys():
#                 if otherV == v:
#                     edgesLost.append((otherU,otherV))
#                     continue
#                 G.add_edge(otherU,otherV)
#                 cs = list(nx.simple_cycles(G))
#                 if len(cs) > 0:
#                     edgesLost.append((otherU,otherV))
#                 G.remove_edge(otherU,otherV)
# #         G.remove_edge(u,v)
#         loss = 0.0
#         for (otherU,otherV) in edgesLost:
#             loss += w[otherU][otherV]
        return (loss,edgesLost)
    
    def updateW(self,G,w,w_rev,possibleRoots,bestu,bestv,edgesLost,iterNum):
        
        def updatePossibleRoots(oldU,newU,possibleRoots):
            for v in possibleRoots.keys():
                if possibleRoots[v].has_key(bestv):
                    n = possibleRoots[v][bestv]
                    del possibleRoots[v][bestv]
                    try:
                        possibleRoots[v][uRoot] += n
                    except KeyError:
                        possibleRoots[v][uRoot] = n
        def rootInfo(root,possibleRoots):
            ks = possibleRoots[root].keys()
            if len(ks) == 1:
                return str(ks[0])
            return len(ks)
        def printRoots(possibleRoots):
            for v in possibleRoots.keys():
                print v,":",possibleRoots[v]
        
        
        
#         if (bestu,bestv) == (3,5):
#             print "Ilan - make sure possibleRoots[5] = 3"
        G.add_edge(bestu, bestv , {'weight': w[bestu][bestv]})
         
        del w[bestu][bestv]
        del w_rev[bestv][bestu]
        possibleRootsUpdates = []
        for (u,v) in edgesLost:
            try:
                del w[u][v]
                del w_rev[v][u]
                uRoot = self.getRoot(u, possibleRoots)
                # corner case
#                 if u == bestv:
#                     uRoot = u
                if uRoot in possibleRoots[v].keys():
                    if possibleRoots[v][uRoot] == 1:
                        del possibleRoots[v][uRoot]
                        vRoots = possibleRoots[v].keys()
                        if len(vRoots) == 1:
                            possibleRootsUpdates.append({'oldU':v, 'newU': vRoots[0]})
                    else:
                        possibleRoots[v][uRoot] -= 1
            except KeyError:
                raise
        # make sure v,uRoot is in
        uRoot = self.getRoot(bestu,possibleRoots)
#         possibleRoots[bestv][uRoot] = 1
        possibleRootsUpdates.append({'oldU':bestv, 'newU': uRoot})
        sortedPossibleRoots = []
        nIter = len(possibleRootsUpdates)
        for _ in range(nIter):
            nUnsorted = len(possibleRootsUpdates)
            for currIndex in range(nUnsorted):
                currData = possibleRootsUpdates[currIndex]
                currOldU = currData['oldU']
                nOldUAppearsAsNewU = filter(lambda data: data['newU'] == currOldU, possibleRootsUpdates)
                if len(nOldUAppearsAsNewU) == 0:
                    sortedPossibleRoots.append(currData)
                    possibleRootsUpdates.remove(currData)
                    break
        for PRData in possibleRootsUpdates: 
            updatePossibleRoots(PRData['oldU'],PRData['newU'],possibleRoots)
         
#         print "i=" + str(iterNum) + ", (" + str(bestu) + "," + str(bestv) + ")" \
#                     ,map(lambda v: len(w_rev[v].keys()), w_rev.keys()) ,edgesLost,\
#                 map(lambda x: rootInfo(x, possibleRoots),possibleRoots.keys())
#         printRoots(possibleRoots)
    
    def greedyMinLoss(self):
#         arc2parts = {}
#         part2Arcs = {}
        
#         for arc in self.partsManager.getArcs():
#             arc2parts[arc] = []
#             
#         for part in self.partsManager.getNonArcs():
#             part2Arcs[part] = []
#             allArcs = filter(lambda subPart: subPart[type] == 'arc', part.getAllSubParts())
#             for arc in allArcs:
#                 arcPart = self.partsManager.getArc(arc['u'], arc['v'])
#                 arc2parts[arcPart].append(part)
#                 part2Arcs[part].append(arcPart)
        
        # update W:
        w_reversed = {}
        possibleRoots = {}
        w = {}
        for (u,v) in self.w:
            if not w.has_key(u):
                w[u] = {}
            w[u][v] = self.w[u,v]
            if not w_reversed.has_key(v):
                w_reversed[v] = {}
                possibleRoots[v] = {}
            w_reversed[v][u] = self.w[u,v]
            possibleRoots[v][u] = 1
        
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(self.n + 1)) 
        
#         print "heads:"
#         for v in w_reversed.keys():
#             print str(v) + ":",w_reversed[v].keys()
        
        for iterNum in range(self.n):
            bestLoss = float('Inf')
            bestEdgesLost = []
            bestu = None
            bestv = None
            
            rootModifiers = w[0].keys()
            if (len(rootModifiers) == 1) and G.out_degree(0) == 0:
                v = rootModifiers[0]
                (_,edgesLost) = self.getLoss(G,0,v,w,possibleRoots,w_reversed,iterNum)
                self.updateW(G, w, w_reversed, possibleRoots, 0, v, edgesLost,iterNum)
                continue
            
            foundCount1edge = False
            for (v) in possibleRoots.keys():
                if (len(possibleRoots[v].keys()) == 1) and (G.in_degree(v) == 0):
                    foundCount1edge = True
                    bestv = v
                    for u in w_reversed[v].keys():
                        (loss,edgesLost) = self.getLoss(G,u,bestv,w,possibleRoots,w_reversed,iterNum)
                        if loss < bestLoss:
                            bestLoss = loss
                            bestu = u
                            bestEdgesLost = edgesLost
                    if bestu == None:
                        raise Exception()
                    self.updateW(G, w, w_reversed, possibleRoots, bestu, bestv, bestEdgesLost,iterNum)
                    break
            if foundCount1edge:
                continue
            
            for u in w.keys():
                allV = w[u].keys()
                for v in allV:
                    (loss,edgesLost) = self.getLoss(G,u,v,w,possibleRoots,w_reversed,iterNum)
                    if loss < bestLoss:
                        bestLoss = loss
                        bestu = u
                        bestv = v
                        bestEdgesLost = edgesLost
            if bestu is None:
                raise Exception("could not find an arc to add")
            self.updateW(G, w, w_reversed, possibleRoots, bestu, bestv, bestEdgesLost,iterNum)
        return G
        
