class part_DEPENDENCYPART_ARC:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        return [];
    
    def __repr__(self):
        return "DEPENDENCYPART_ARC (" + str(self.u) + "," + str(self.v) + ")," + str(self.val) 
        
class part_DEPENDENCYPART_SIBL:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        return allSubParts;
    
    def __repr__(self):
        return "DEPENDENCYPART_SIBL (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")," + str(self.val)
                
class part_DEPENDENCYPART_NEXTSIBL:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        return allSubParts;

    
    def __repr__(self):
        return "DEPENDENCYPART_NEXTSIBL (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")," + str(self.val)
        
class part_DEPENDENCYPART_NEXTSIBL_LAST_SIB:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
    
    def __repr__(self):
        return "DEPENDENCYPART_NEXTSIBL_LAST_SIB (" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
    
    def __repr__(self):
        return "DEPENDENCYPART_NEXTSIBL_FIRST_SIB (" + str(self.u) + "," + str(self.v) + ")," + str(self.val)
        
class part_DEPENDENCYPART_GRANDPAR:
    
    def __init__(self,g,u,v,val):
        self.g = g
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
    
    def __repr__(self):
        return "DEPENDENCYPART_GRANDPAR (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        return allSubParts;
        
    def __repr__(self):
        return "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD (" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_GRANDSIBL:
    
    def __init__(self,g,u,v1,v2,val):
        self.g = g;
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
    
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
            
    def __repr__(self):
        return "DEPENDENCYPART_GRANDSIBL (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v1) + "),(" + \
                                              str(self.u) + "," + str(self.v2) + ")," + str(self.val)
        
class part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB:
    
    def __init__(self,g,u,v,val):
        self.g = g;
        self.u = u
        self.v = v
        self.val = val
        
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v})
        return allSubParts
    
    def __repr__(self):
        return "DEPENDENCYPART_GRANDSIBL_FIRST_SIB (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_GRANDSIBL_LAST_SIB:
    
    def __init__(self,g,u,v,val):
        self.g = g;
        self.u = u
        self.v = v
        self.val = val
        
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.g,'v': self.u})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'grandParant','g': self.g,'u': self.u,\
                            'v': self.v})
        return allSubParts
     
    def __repr__(self):
        return "DEPENDENCYPART_GRANDSIBL_LAST_SIB (" + str(self.g) + "," + str(self.u) + "),(" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})

        return allSubParts
   
    def __repr__(self):
        return "DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD (" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_TRISIBL:
    
    def __init__(self,u,v1,v2,v3,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.val = val
        
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
    
    def __repr__(self):
        return "DEPENDENCYPART_TRISIBL (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + "),(" + \
                                            str(self.u) + "," + str(self.v3) + ")," + str(self.val)

class part_DEPENDENCYPART_TRISIBL_LAST_SIBS:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v2})
        return allSubParts
    
    def __repr__(self):
        return "DEPENDENCYPART_TRISIBL_LAST_SIBS (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")," + str(self.val)
        
class part_DEPENDENCYPART_TRISIBL_FIRST_SIBS:
    
    def __init__(self,u,v1,v2,val):
        self.u = u
        self.v1 = v1
        self.v2 = v2
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v1})
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v2})
        allSubParts.append({'type': 'sibl','u': self.u, \
                            'v1': self.v1,'v2': self.v2})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v1})
        return allSubParts
    
    def __repr__(self):
        return "DEPENDENCYPART_TRISIBL_FIRST_SIBS (" + str(self.u) + "," + str(self.v1) + "),(" + str(self.u) + "," + str(self.v2) + ")," + str(self.val)
    
class part_DEPENDENCYPART_TRISIBL_ONLY_CHILD:
    
    def __init__(self,u,v,val):
        self.u = u
        self.v = v
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'firstSibl','u': self.u,'v': self.v})
        allSubParts.append({'type': 'lastSibl','u': self.u,'v': self.v})
        return allSubParts
    
    def __repr__(self):
        return "DEPENDENCYPART_TRISIBL_ONLY_CHILD (" + str(self.u) + "," + str(self.v) + ")," + str(self.val)

class part_DEPENDENCYPART_HEADBIGRAM:
    
    def __init__(self,u,v,prev_u,val):
        self.u = u
        self.v = v
        self.prev_u = prev_u
        self.val = val
    
    def getAllSubParts(self):
        allSubParts = [];
        allSubParts.append({'type': 'arc','u': self.u,'v': self.v})
        allSubParts.append({'type': 'arc','u': self.prev_u,'v': (self.v - 1)})
        
        return allSubParts
    
    def __repr__(self):
        return "DEPENDENCYPART_HEADBIGRAM (" + str(self.u) + "," + str(self.v) + "),(" + str(self.prev_u) + "," + str(self.v - 1) + ")," + str(self.val)