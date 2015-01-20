class part_DEPENDENCYPART_ARC:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'arc'
                            
    def getAllSubParts(self):
        return [];
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
    
    def __repr__(self):
        return "ARC           (" + str(self.u) + "," + str(self.v) + ")" 
        
class part_DEPENDENCYPART_SIBL:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
        self.type = 'sibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        return allSubParts;
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
    
    def __repr__(self):
        return "SIB           (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")"
                
class part_DEPENDENCYPART_NEXTSIBL:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
        self.type = 'nextSibl'
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        return allSubParts;

    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for v in range(self.v1 + 1, self.v2):
            edges.append((self.u,v))
        return edges
    
    def __repr__(self):
        return "NXTSIB        (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")"
        
class part_DEPENDENCYPART_NEXTSIBL_LAST_SIB:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'lastSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for v in range(self.v + 1, n + 1):
            edges.append((self.u,v))
        return edges
    
    def __repr__(self):
        return "LSTSIB        (" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'firstSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
        
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for v in range(0, self.v):
            edges.append((self.u,v))
        return edges
  
    def __repr__(self):
        return "FRSTSIB       (" + str(self.u) + "," + str(self.v) + ")"
        
class part_DEPENDENCYPART_GRANDPAR:
    
    def __init__(self,g,u,v,val):
        self.g = g
        self.u = u
        self.v = v
        self.val = val
        self.type = 'grandParant'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.g,self.u))
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
  
    def __repr__(self):
        return "GP            (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'grandParantNoGrandChild'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'nextSiblNoChild','u': self.v,'v': self.v})
        return allSubParts;
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,n + 1):
            edges.append((self.v,w))
        return edges
  
     
    def __repr__(self):
        return "GPNoGC        (" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_GRANDSIBL:
    
    def __init__(self,g,u,v1,v2,val):
        self.g = g;
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
        self.type = 'grandSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u,'v1': self.v1, \
                            'v2': self.v2})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v1})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v2})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.g,self.u))
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
            
    def __repr__(self):
        return "GSBL          (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v1) + "),(" + \
                                              str(self.u) + "," + str(self.v2) + ")"
        
class part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB:
    
    def __init__(self,g,u,v,val):
        self.g = g;
        self.u = u
        self.v = v
        self.val = val
        self.type = 'grandSiblFirstSibl'
        
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.g,self.u))
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,self.v):
            edges.append((self.u,w))
        return edges
    
    def __repr__(self):
        return "GSBLFRST      (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_GRANDSIBL_LAST_SIB:
    
    def __init__(self,g,u,v,val):
        self.g = g;
        self.u = u
        self.v = v
        self.val = val
        self.type = 'grandSiblLastSibl'
        
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.g,self.u))
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(self.v + 1,n + 1):
            edges.append((self.u,w))
        return edges
     
    def __repr__(self):
        return "GSBLLST       (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'grandSiblNoSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'nextSiblNoChild','u': self.v,'v': self.v})

        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,n + 1):
            edges.append((self.v,w))
        return edges
    
    def __repr__(self):
        return "GSBLNOSIBL    (" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_TRISIBL:
    
    def __init__(self,u,v1,v2,v3,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.val = val
        self.type = 'triSibl'
        
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v3})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v3})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v2,'v2': self.v3})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        edges.append((self.u,self.v3))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
    
    def __repr__(self):
        return "TRISBL        (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + "),(" + \
                                            str(self.u) + "," + str(self.v3) + ")"

class part_DEPENDENCYPART_TRISIBL_LAST_SIBS:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
        self.type = 'triSiblLastSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v2})
        return allSubParts

    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(self.v2 + 1, n + 1):
            edges.append((self.u,w))
        return edges
    
    def __repr__(self):
        return "TRISBL_LAST   (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")"
        
class part_DEPENDENCYPART_TRISIBL_FIRST_SIBS:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
        self.type = 'triSiblFirstSibl'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v1})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v1))
        edges.append((self.u,self.v2))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,self.v1):
            edges.append((self.u,w))
        return edges
    
    def __repr__(self):
        return "TRISBL_FRST   (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")"
    
class part_DEPENDENCYPART_TRISIBL_ONLY_CHILD:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'triSiblOnlyChild'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v})
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,n + 1):
            edges.append((self.u,w))
        if (self.u,self.v) not in edges:
            x = 1
            print x
        edges.remove((self.u,self.v))
        return edges
    
    def __repr__(self):
        return "TRISBL_ONLY   (" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_NEXTSIBL_NO_SIBS:
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
        self.type = 'nextSiblNoChild'
    
    def getAllSubParts(self):
        allSubParts = [];
        return allSubParts;
    
    def getAllExistingEdges(self):
        edges = [];
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        for w in range(0,n + 1):
            edges.append((self.u,w))
        return edges
  
    def __repr__(self):
        return "NXTSIBLNoSIBL (" + str(self.u) + "," + str(self.v) + ")"

class part_DEPENDENCYPART_HEADBIGRAM:
    
    def __init__(self,u,v,prev_u,val):
        self.u = u
        self.v = v
        self.prev_u = prev_u
        self.val = val
        self.type = 'headBigram'
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'arc','u': self.prev_u,'v': (self.v - 1)})
        
        return allSubParts
    
    def getAllExistingEdges(self):
        edges = [];
        edges.append((self.u,self.v))
        edges.append((self.prev_u,self.v - 1))
        return edges
    
    def getAllNonExistingEdges(self,n):
        edges = [];
        return edges
    
    def __repr__(self):
        return "HEADBIGRAM    (" + str(self.u) + "," + str(self.v) + "),(" + str(self.prev_u) + "," + str(self.v - 1) + ")"