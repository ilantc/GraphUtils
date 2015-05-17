import networkx as nx 
import math

class inference(object):


    def __init__(self, w,n,partsManager = None):
        self.w = w
        self.n = n
        self.partsManager = partsManager
    
    def printMatrix(self, V,n):
        for i in range(n + 1):
            rowStr = ""
            for j in range(n):
                if (i,j) in V:
                    rowStr += "1,"
                else:
                    rowStr += " ,"
            if (i,n) in V:
                rowStr += "1"
            print rowStr
        
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

    class node:
        def __init__(self,name,root=None):
            self.nodeName = name
            if root is None:
                self.root = name
            else:
                self.root = root 
    
    class cluster:
        
        def __init__(self,root,subNodes = []):
            self.subNodes = {root:None}
            for node in subNodes:
                self.subNodes[node] = None
            self.root = root
             
    def getLoss(self,G,u,v,w,nodes,allClusters,w_rev,iterNum):
        
        edgesLost = {}
        uRoot = nodes[u].root
        
        # clear all incoming edges to v
        for s in w_rev[v].keys():
            edgesLost[(s,v)] = w[s][v]
            
        # clear path from v sub tree to uRoot
        if v in allClusters:
            for t in allClusters[v].subNodes:
                if t in w:
                    if uRoot in w[t]:
                        edgesLost[(t,uRoot)] = w[t][uRoot]
            # if any node had [v,uRoot] as roots - remove all edges from 
            # that node's sub tree back to uRoot
            for t in w[v].keys():
                uRootInTroots = False
                otherRoot = False
                for s in w_rev[t]:
                    if nodes[s].root not in [v,uRoot]:
                        otherRoot = True
                        break
                    if nodes[s].root == uRoot:
                        uRootInTroots = True
                if otherRoot or (not uRootInTroots):
                    # some other root available for t
                    continue
                # clear path from t sub tree to uRoot
                for r in allClusters[t].subNodes:
                    if r in w_rev[uRoot]:
                        edgesLost[(r,uRoot)] = w[r][uRoot] 


        
        edgeVal = edgesLost[(u,v)]
        del edgesLost[(u,v)]
        
        edges = edgesLost.keys()
        loss = sum(map(lambda e: edgesLost[e], edges))
        
        loss -= edgeVal
        
        return (loss,edges)
    
    def updateW(self,G,w,w_rev,nodes,allClusters,bestu,bestv,edgesLost,iterNum):
        
#         if iterNum == 20:
#             print ""
#         print "iter ", iterNum, "len w_rev[10] =", len(w_rev[10]), "root_10 =", nodes[10].root, "len w_rev[5] =", len(w_rev[5]), "(u,v) = (" + str(bestu) + "," + str(bestv) + ")"
#         print "(" + str(bestu) + "," + str(bestv) + ")"
#         print edgesLost
        G.add_edge(bestu, bestv , {'weight': w[bestu][bestv]})
        
        
        del w[bestu][bestv]
        del w_rev[bestv][bestu]
        for (u,v) in edgesLost:
            del w[u][v]
            del w_rev[v][u]
        
        # update v sub tree to be rooted at uRoot
        if bestv in allClusters:
            for t in allClusters[bestv].subNodes:
                nodes[t].root = nodes[bestu].root
#             allClusters[bestu].subNodes += allClusters[bestv].subNodes
            allClusters[nodes[bestu].root].subNodes.update(allClusters[bestv].subNodes)
            del allClusters[bestv]
        
        # update root data
        allClusterKeys = allClusters.keys()
        for c in allClusterKeys:
            if allClusters[c].root == 0:
                continue
            allRoots = w_rev[allClusters[c].root].keys()
            try:
                possibleRoot = allRoots.pop()
            except IndexError:
                print "Ilan"
                raise
            possibleRoot = nodes[possibleRoot].root
            singlePossibleRoot = True
            for otherPossibleRoot in allRoots:
                if nodes[otherPossibleRoot].root != possibleRoot:
                    singlePossibleRoot = False
                    break
            if singlePossibleRoot:
                for node in allClusters[c].subNodes:
                    nodes[node].root = possibleRoot
                    if possibleRoot in w[node]:
                        raise Exception("backEdge from " + str(node) + " to " + str(possibleRoot))
                allClusters[possibleRoot].subNodes.update(allClusters[c].subNodes)
                del allClusters[c]

         
#         for v in w_rev.keys():
#             if v == nodes[v].root:
#                 singlePossibleRoot = True
#                 allRoots = w_rev[v].keys()
#                 if allRoots == []:
#                     continue
#                 possibleRoot = allRoots.pop()
#                 possibleRoot = nodes[possibleRoot].root
#                 for otherPossibleRoot in allRoots:
#                     if nodes[otherPossibleRoot].root != possibleRoot:
#                         singlePossibleRoot = False
#                         break
#                 if singlePossibleRoot:
#                     nodes[v].root = possibleRoot
#                     
    
    def greedyMinLoss(self):
        print self.n
        # update W:
        w = {}
        w_reversed = {0:{}}
        nodes = {}
        allClusters = {}
        for i in range(self.n + 1):
            nodes[i]                = inference.node(i)
            allClusters[i]          = inference.cluster(i)
            w[i]                    = {}
            w_reversed[i]           = {}
        
        for (u,v) in self.w:
            w[u][v] = self.w[u,v]
            w_reversed[v][u] = self.w[u,v]
        
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(self.n + 1)) 
        
        for iterNum in range(self.n):
            bestLoss = float('Inf')
            bestEdgesLost = []
            bestu = None
            bestv = None
            
            rootModifiers = w[0].keys()
            if (len(rootModifiers) == 1) and G.out_degree(0) == 0:
                v = rootModifiers[0]
                (_,edgesLost) = self.getLoss(G,0,v,w,nodes,allClusters,w_reversed,iterNum)
                self.updateW(G, w, w_reversed, nodes,allClusters, 0, v, edgesLost,iterNum)
                continue
            
            foundCount1edge = False
            for v in w_reversed:
                if v in allClusters:
                    continue
                allU = w_reversed[v].keys()
                if len(allU) > 0:
                    foundCount1edge = True
                    bestv = v
                    bestu = None
                    bestLoss = float('Inf')
                    bestEdgesLost = []
                    for u in allU:
                        (loss,edgesLost) = self.getLoss(G,u,bestv,w,nodes,allClusters,w_reversed,iterNum)
                        if loss < bestLoss:
                            bestLoss = loss
                            bestu = u
                            bestEdgesLost = edgesLost
                    self.updateW(G, w, w_reversed, nodes,allClusters, bestu, bestv, bestEdgesLost,iterNum)
                    break
            if foundCount1edge:
                continue
            
            for u in w.keys():
                allV = w[u].keys()
                for v in allV:
                    (loss,edgesLost) = self.getLoss(G,u,v,w,nodes,allClusters,w_reversed,iterNum)
                    if loss < bestLoss:
                        bestLoss = loss
                        bestu = u
                        bestv = v
                        bestEdgesLost = edgesLost
            if bestu is None:
                raise Exception("could not find an arc to add")
            self.updateW(G, w, w_reversed, nodes, allClusters, bestu, bestv, bestEdgesLost,iterNum)
        return G
    #####################################
    
    def twoSidedMinLoss(self):
        w = {}
        w_reversed = {}
        leftNodes   = {0:None}
        rightNodes  = {}
        for i in range(self.n + 1):
            w[i]            = {}
            w_reversed[i]   = {}
            rightNodes[i]   = None
        del rightNodes[0]
        
        for (u,v) in self.w:
            w[u][v] = self.w[u,v]
            w_reversed[v][u] = self.w[u,v]
        
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(self.n + 1)) 
        
        for _ in range(self.n):
            bestLoss = float('Inf')
            bestEdgesLost = []
            bestu = None
            bestv = None
            
            for u in leftNodes:
                for v in w[u].keys():
                    edgesLost = w_reversed[v].keys()
                    loss = sum(map(lambda r: w_reversed[v][r], edgesLost))
                    loss -= 2 * w_reversed[v][u]
                    if loss < bestLoss:
                        bestLoss = loss
                        bestu = u
                        bestv = v
                        bestEdgesLost = edgesLost
            if bestu is None: 
                raise Exception("could not find an arc to add")
            G.add_edge(bestu, bestv, {'weight':w[bestu][bestv]})
            leftNodes[bestv] = None
            del rightNodes[bestv]
            for u in bestEdgesLost:
                del w_reversed[bestv][u]
                del w[u][bestv]
        return G
    
    ###################################################
    def calcEdgeProbability(self,u,v,E_rev,edgesLost, V):
        sumEdges = 0
        n = 0.0
        minVal = 0
        for u_ in E_rev[v]:
            sumEdges += math.exp(V[u_,v])
            n += 1
#             minVal = min(minVal, V[u_,v])
        return 1/n
        return math.exp(V[u,v]) / sumEdges
        return (V[u,v] - (2 * minVal)) / (sumEdges - (2 * n * minVal))
    
    def calcPartProbability(self,part,E_rev,V, edgeProbabilities, unAssignedHeads):
        p = 1
        for (u,v) in part.getAllExistingEdges():
            if v in unAssignedHeads:
                if (u,v) not in edgeProbabilities:
                    edgeProbabilities[u,v] = self.calcEdgeProbability(u, v, E_rev, None, V)
                p *= edgeProbabilities[u,v]
        return p
    
    def calcLossPerEdge(self,u,v,edge2edgesLost, edge2Parts, unAssignedHeads, edgeProbabilities, partsProbabilities, E_rev, V):
        partsLost = set([])
        loss = 0
        for e in edge2edgesLost[u,v]:
            for p in edge2Parts[e]:
                if p not in partsLost:
                    partsLost.add(p)
                    if p not in partsProbabilities:
                        try:
                            partsProbabilities[p] = self.calcPartProbability(p, E_rev, V, edgeProbabilities, unAssignedHeads)
                        except KeyError:
                            print p,"\n",u,v,"\n",e,p.getAllExistingEdges()
                            raise
                    loss += partsProbabilities[p] * p.val
        
        gain = 0
        for p in edge2Parts[u,v]:
            if p in partsLost:
                continue
            pMissingEdges = filter(lambda (u_,v_): v_ in unAssignedHeads, p.getAllExistingEdges())
            
            # calculate the probability to complete this part
            pr = 1
            for (u_,v_) in pMissingEdges:
                if (u_,v_) not in edgeProbabilities:
                    edgeProbabilities[u_,v_] = self.calcEdgeProbability(u_,v_, E_rev, edge2edgesLost[u_,v_], V)
                if (u_,v_) != (u,v):
                    pr *= edgeProbabilities[u_,v_]
            
            gain += (pr * p.val)     
            
        
#         loss = sum(map(lambda p: p.val,partsLost))
        
        return (loss - gain)
    
    def updateData(self,u,v,E,E_rev,V,cluster2cluster,cluster2cluster_rev,allClusters,allNodes,edge2edgesLost,\
                   edge2Loss, edge2clustersMerged,edge2edgesLost_rev, G, singleEdgeLossFn, edge2Parts, unAssignedHeads,\
                   edgeProbabilities,partsProbabilities):
        
        def delEdgeSimple(u,v,E,E_rev,V):
            del E[u][v]
            del E_rev[v][u]
            del V[u,v]
        
        def delEdge(u,v,edge2Loss,edge2edgesLost,edge2edgesLost_rev,edge2Parts,edgeWasAddedToGraph = False, edgeProbability = None, partsProbabilities = None):
            del edge2edgesLost[u,v]
            del edge2Loss[u,v]
            del edge2edgesLost_rev[u,v]
            allParts = edge2Parts[u,v].copy()
            if edgeWasAddedToGraph:
                for part in edge2Parts[u,v]:
                    try:
                        partsProbabilities[part] /= edgeProbability
                    except KeyError:
                        raise
            else:
                for part in allParts:
                    edges = part.getAllExistingEdges()
                    for e in edges:
                        edge2Parts[e].remove(part)
                del edge2Parts[u,v]
            
                
        def list2set(ls):
            uniq = set([])
            for l in ls:
                if l not in uniq:
                    uniq.add(l)
            return uniq
        
        G.add_edge(u, v, {'weight': E[u][v]})
        
        uRoot = allNodes[u].root
        
        # del all edges lost from all structures
        changedHeads = set([])
        edgesLost = edge2edgesLost[u,v].copy()
        for (u2,v2) in edgesLost:
            changedHeads.add(v2)
            for (u3,v3) in edge2edgesLost_rev[u2,v2]:
                if (u3,v3) not in edgesLost:
#                     print "(u3,v3) = (" + str(u3) + "," + str(v3) + "), (u2,v2) = (" + str(u2) + "," + str(v2) + ")"
                    edge2edgesLost[u3,v3].remove((u2,v2))
                    edge2Loss[u3,v3] -= singleEdgeLossFn((u2,v2))
                    edge2edgesLost_rev[u3,v3].remove((u2,v2))
            delEdge(u2,v2,edge2Loss,edge2edgesLost,edge2edgesLost_rev, edge2Parts)
            delEdgeSimple(u2,v2,E,E_rev,V)
        
        # update probability
        for lostV in changedHeads:
            if lostV == v:
                continue
            nHeads = len(E_rev[lostV])
            newP = 1.0/nHeads
            for head in E_rev[lostV]:
                e = (head,lostV)
                oldP = edgeProbabilities[e]
                ratio = newP/oldP
                edgeProbabilities[e] = newP
                for part in edge2Parts[e]:
                    partsProbabilities[part] *= ratio
        
        # remove mapping from u,v to edges lost
#         print edgeProbabilities[u,v]
        delEdge(u,v,edge2Loss,edge2edgesLost,edge2edgesLost_rev, edge2Parts,True, edgeProbabilities[u,v],partsProbabilities)
        
        # del u,v from structures:
        delEdgeSimple(u, v, E, E_rev, V)

        # update new edges lost for all E_rev[u] and E[v]
        uRootPossibleRoots = map(lambda uParent: allNodes[uParent].root, E_rev[uRoot])
        uniqRoots = list(list2set(uRootPossibleRoots))
        uniqRootsLen = len(uniqRoots)
        
        if v in allClusters:
            if v == 2:
                x = 4
            for s in allClusters[v].subNodes:
                for t in E[s]:
                    if t not in allClusters:
                        continue
                    otherPar = None
                    if uniqRootsLen == 2 and (t in uniqRoots):
                        otherPar = uniqRoots[0]
                        if otherPar == t:
                            otherPar = uniqRoots[1]
                        edge2clustersMerged[s,t].append((otherPar,uRoot))
                    for tNode in allClusters[t].subNodes:
                        if uRoot in E[tNode]:
                            if (tNode,uRoot) not in edge2edgesLost[s,t]:
                                edge2edgesLost[s,t].add((tNode,uRoot))
                                edge2Loss[s,t] += singleEdgeLossFn((tNode,uRoot))
                                edge2edgesLost_rev[tNode,uRoot].add((s,t))                          
                                edge2edgesLost[tNode,uRoot].add((s,t))
                                edge2Loss[tNode,uRoot] += singleEdgeLossFn((s,t))
                                edge2edgesLost_rev[s,t].add((tNode,uRoot))                            
                            if (otherPar is not None) and (otherPar in E[tNode]):
                                if (tNode,otherPar) not in edge2edgesLost[s,t]:
                                    edge2edgesLost[s,t].add((tNode,otherPar))
                                    edge2Loss[s,t] += singleEdgeLossFn((tNode,otherPar))
                                    edge2edgesLost_rev[tNode,otherPar].add((s,t))
                                    edge2edgesLost[tNode,otherPar].add((s,t))
                                    edge2Loss[tNode,otherPar] += singleEdgeLossFn((s,t))
                                    edge2edgesLost_rev[s,t].add((tNode,otherPar)) 
        
#         edgeProbabilities = {}
#         partsProbabilities = {}
#         for (u2,v2) in edge2Loss:
# #             loss = edge2Loss[u2,v2]
#             edge2Loss[u2,v2] = self.calcLossPerEdge(u2,v2,edge2edgesLost, edge2Parts, unAssignedHeads, edgeProbabilities, partsProbabilities, E_rev, V)
#             if abs(edge2Loss[u2,v2] - loss) > 0.0000001:
#                 print "diff loss:", u2, v2, edge2Loss[u2,v2], loss
        
        # update the clusters
        for (cFrom,cTo) in edge2clustersMerged[u,v]:
            cFromRoot = allNodes[cFrom].root
            cToRoot = allNodes[cTo].root
            if cToRoot != cFromRoot: 
                for s in allClusters[cTo].subNodes:
                    allNodes[s].root = cFromRoot
                    allClusters[cFromRoot].subNodes[s] = None 
                del allClusters[cTo]        
#     
#         # check if we can infer more cluster merges
#         for s in E[v]:
#             vRoot = allNodes[v].root
#             if vRoot not in clustersEntringU:
#                 clustersEntringU[vRoot] = []
#             clustersEntringU[vRoot].append(v)
            
    
    def greedyMinLossTake2(self,order):
        E                   = {}
        E_rev               = {}
        V                   = {}
        cluster2cluster     = {}
        cluster2cluster_rev = {}
        allClusters         = {}
        allNodes            = {}
        edge2edgesLost      = {}
        edge2clustersMerged = {}
        edge2edgesLost_rev  = {}
        edge2Loss           = {}
        edge2Parts          = {}
        
        self.partsManager.mapping['grandParantNoGrandChild'] = {}
        
        getSingleEdgeLoss = lambda e: V[e]
        if order == 2:
            getSingleEdgeLoss = lambda e: V[e]
        
        for i in range(self.n + 1):
            E[i]                    = {}
            E_rev[i]                = {}
            cluster2cluster[i]      = {}
            cluster2cluster_rev[i]  = {}
            allNodes[i]             = inference.node(i)
            allClusters[i]          = inference.cluster(i)
            
        for (u,v) in self.w:
            V[(u,v)]                    = self.w[u,v]
            edge2edgesLost[u,v]         = set([])
            edge2Loss[u,v]              = -1 * getSingleEdgeLoss((u,v)) 
            edge2clustersMerged[(u,v)]  = [(u,v)]
            edge2edgesLost_rev[(u,v)]   = set([])
            E[u][v]                     = None
            E_rev[v][u]                 = None
            cluster2cluster[u][v]       = None
            cluster2cluster_rev[v][u]   = None
            edge2Parts[u,v]             = set([])
        
        
        for p in self.partsManager.getAllParts():
            edges = p.getAllExistingEdges()
            for e in edges:
                edge2Parts[e].add(p)
        
        edges = self.partsManager.getArcs()
        for edge in edges:
            (u,v) = (edge.u,edge.v)
#             if (u,v) == (1,3):
#                 print ""
            for otheru in E_rev[v]:
                if otheru != u:
                    edge2edgesLost[u,v].add((otheru,v))
                    edge2Loss[u,v] += getSingleEdgeLoss((otheru,v))
                    edge2edgesLost_rev[otheru,v].add((u,v))
            if u in E[v]:
                edge2edgesLost[u,v].add((v,u))
                edge2Loss[u,v] += getSingleEdgeLoss((v,u))
                edge2edgesLost_rev[v,u].add((u,v))
        
        unAssignedHeads = set(range(1,self.n + 1))
        edgeProbabilities = {}
        partsProbabilities = {}
        for (u,v) in edge2Loss:
            edge2Loss[u,v] = self.calcLossPerEdge(u,v,edge2edgesLost, edge2Parts, unAssignedHeads,edgeProbabilities,partsProbabilities,E_rev, V)

        for v in E_rev:
            if len(E_rev[v]) == 2:
                u1 = E_rev[v].keys()[0]
                u2 = E_rev[v].keys()[1]
                if (u1,u2) in V:
                    edge2clustersMerged[u1,u2].append((u1,v))
                if (u2,u1) in V:
                    edge2clustersMerged[u2,u1].append((u2,v))
        
        
        G = nx.DiGraph()
        # add all nodes and edges
        G.add_nodes_from(range(self.n + 1)) 
        
        for iterNum in range(self.n):
            bestLoss = float('Inf')
            (bestu,bestv) = (None,None)
            cluster_0_nodes = allClusters[0].subNodes
            cluster_0_outEdges = []
            for node in cluster_0_nodes:
                cluster_0_outEdges += [(node,v) for v in E[node].keys()]
            cluster_0_outEdges = filter(lambda (u,v): len(E[v]) > 0, cluster_0_outEdges)
            cluster_0_outEdges = filter(lambda (u,v): v in unAssignedHeads, cluster_0_outEdges)
            if len(cluster_0_outEdges) == 1:
                (bestu,bestv) = (cluster_0_outEdges[0][0],cluster_0_outEdges[0][1])
            else:
#                 getLoss = lambda e: V[e]
                for v in unAssignedHeads:
                    # if v is a leaf - assigne it now
#                     vIsLeaf = False
#                     if len(E[v]) == 0:
#                         vIsLeaf = True
#                         bestLoss = float('Inf')
#                         (bestu,bestv) = (None,None)
                    vHeads = E_rev[v].keys()
                    singleHead = False
                    parentClusters = set(map(lambda t: allNodes[t].root,vHeads))
                    if len(parentClusters) == 1:
                        bestLoss = float('Inf')
                        (bestu,bestv) = (None,None)
                        singleHead = True
                    for u in vHeads:
#                         currLoss = sum(map(getLoss, edge2edgesLost[u,v])) - V[u,v]
                        currLoss = edge2Loss[u,v]
#                         currLossOrig = sum(map(getLoss, edge2edgesLost[u,v])) - V[u,v]
#                         if abs(currLossOrig - currLoss) > 0.000001:
#                             print "loss =",currLoss, "calculated Loss =", currLossOrig
#                             raise 
                        if currLoss < bestLoss:
                            bestLoss = currLoss
                            (bestu,bestv) = (u,v)
                    if singleHead: #or vIsLeaf:
                        break
#             print bestu,bestv
            if bestv is not None:
                unAssignedHeads.remove(bestv)
#                 print edgeProbabilities[bestu, bestv]
                self.updateData(bestu, bestv, E, E_rev, V, cluster2cluster, cluster2cluster_rev, allClusters, allNodes, edge2edgesLost, edge2Loss, edge2clustersMerged, edge2edgesLost_rev, G, getSingleEdgeLoss, edge2Parts, unAssignedHeads, edgeProbabilities,partsProbabilities)
            else:
                print "\t",iterNum, self.n - 1
                G = None
                break
                     
        return G    