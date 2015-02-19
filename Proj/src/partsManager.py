import parts

class partsManager:
    
    partTypeToPartConstructor = {'arc':                     { 'ctor':parts.part_DEPENDENCYPART_ARC,                   'args': ['u','v']},\
                                 'sibl':                    { 'ctor':parts.part_DEPENDENCYPART_SIBL,                  'args': ['u', 'v1', 'v2']},\
                                 'nextSibl':                { 'ctor':parts.part_DEPENDENCYPART_NEXTSIBL,              'args': ['u', 'v1', 'v2']},\
                                 'lastSibl':                { 'ctor':parts.part_DEPENDENCYPART_NEXTSIBL_LAST_SIB,     'args': ['u','v']},\
                                 'firstSibl':               { 'ctor':parts.part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB,    'args': ['u','v']},\
                                 'grandParant':             { 'ctor':parts.part_DEPENDENCYPART_GRANDPAR,              'args': ['g','u','v']},\
                                 'grandParantNoGrandChild': { 'ctor':parts.part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD,'args': ['u','v']},\
                                 'grandSibl':               { 'ctor':parts.part_DEPENDENCYPART_GRANDSIBL,             'args': ['g','u','v1','v2']},\
                                 'grandSiblFirstSibl':      { 'ctor':parts.part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB,   'args': ['g','u','v']},\
                                 'grandSiblLastSibl':       { 'ctor':parts.part_DEPENDENCYPART_GRANDSIBL_LAST_SIB,    'args': ['g','u','v']},\
                                 'grandSiblNoSibl':         { 'ctor':parts.part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN, 'args': ['u','v']},\
                                 'triSibl':                 { 'ctor':parts.part_DEPENDENCYPART_TRISIBL,               'args': ['u','v1','v2','v3']},\
                                 'triSiblFirstSibl':        { 'ctor':parts.part_DEPENDENCYPART_TRISIBL_FIRST_SIBS,    'args': ['u','v1','v2']},\
                                 'triSiblLastSibl':         { 'ctor':parts.part_DEPENDENCYPART_TRISIBL_LAST_SIBS,     'args': ['u','v1','v2']},\
                                 'triSiblOnlyChild':        { 'ctor':parts.part_DEPENDENCYPART_TRISIBL_ONLY_CHILD,    'args': ['u','v']},\
                                 'headBigram':              { 'ctor':parts.part_DEPENDENCYPART_HEADBIGRAM,            'args': ['u','v','prev_u']},\
                                 'nextSiblNoChild':         { 'ctor':parts.part_DEPENDENCYPART_NEXTSIBL_NO_SIBS,      'args': ['u','v']}}
    

    def __init__(self):
        self.mapping = {};
        for partType in self.partTypeToPartConstructor.keys():
            self.mapping[partType] = {}

    def createPart(self,partType,values):
        key = self.constructKey(partType,values)
        if self.mapping[partType].has_key(key):
#            raise Exception("trying to create an existing part")
            self.mapping[partType][key].val += values['val']
#             print "found key", key, "for part type", partType, "val is", values['val']
            p = self.mapping[partType][key]
        else:
            pCtor = self.partTypeToPartConstructor[partType]['ctor'];
            p = pCtor(**values)
            self.mapping[partType][key] = p
        return p
    
    def constructKey(self,partType,values):
        try:
            key = [values[t] for t in self.getKeyFields(partType)]
        except KeyError:
            t = partType
            print "expected keys for part",t,":",self.getKeyFields(partType),"\nfound keys:",values.keys()
        return tuple(key)

    def hasPart(self,partType,values):
        key = self.constructKey(partType, values)
        return self.mapping[partType].has_key(key)
    
    def hasArc(self,u,v):
        return self.hasPart('arc', {'u': u, 'v': v})
    
    def getPart(self,partType,values):
        key = self.constructKey(partType, values)
        return self.mapping[partType][key]
    
    def getAllParts(self):
        allP = []
        for partType in self.mapping.keys():
            allP = allP + self.mapping[partType].values()
        return allP
    
    def getKeyFields(self,partType):
        if not self.partTypeToPartConstructor.has_key(partType):
            raise 'bad part type: ' + partType
        return self.partTypeToPartConstructor[partType]['args']