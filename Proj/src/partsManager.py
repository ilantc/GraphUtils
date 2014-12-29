from parts import *
class partsManager:
    
    partTypeToPartConstructor = {'arc':                     { 'ctor':part_DEPENDENCYPART_ARC, 'args': ['u','v']},\
                                 'sibl':                    { 'ctor':part_DEPENDENCYPART_SIBL, 'args': ['u', 'v1', 'v2']},\
                                 'nextSibl':                { 'ctor':part_DEPENDENCYPART_NEXTSIBL, 'args': ['u', 'v1', 'v2']},\
                                 'lastSibl':                { 'ctor':part_DEPENDENCYPART_NEXTSIBL_LAST_SIB, 'args': ['u','v']},\
                                 'firstSibl':               { 'ctor':part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB, 'args': ['u','v']},\
                                 'grandParant':             { 'ctor':part_DEPENDENCYPART_GRANDPAR, 'args': ['g','u','v']},\
                                 'grandParantNoGrandChild': { 'ctor':part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD, 'args': ['u','v']},\
                                 'grandSibl':               { 'ctor':part_DEPENDENCYPART_GRANDSIBL, 'args': ['g','u','v1','v2']},\
                                 'grandSiblFirstSibl':      { 'ctor':part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB, 'args': ['g','u','v']},\
                                 'grandSiblLastSibl':       { 'ctor':part_DEPENDENCYPART_GRANDSIBL_LAST_SIB, 'args': ['g','u','v']},\
                                 'grandSiblNoSibl':         { 'ctor':part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN, 'args': ['u','v']},\
                                 'triSibl':                 { 'ctor':part_DEPENDENCYPART_TRISIBL, 'args': ['u','v1','v2','v3']},\
                                 'triSiblFirstSibl':        { 'ctor':part_DEPENDENCYPART_TRISIBL_FIRST_SIBS, 'args': ['u','v1','v2']},\
                                 'triSiblLastSibl':         { 'ctor':part_DEPENDENCYPART_TRISIBL_LAST_SIBS, 'args': ['u','v1','v2']},\
                                 'triSiblOnlyChild':        { 'ctor':part_DEPENDENCYPART_TRISIBL_ONLY_CHILD, 'args': ['u','v']},\
                                 'headBigram':              { 'ctor':part_DEPENDENCYPART_HEADBIGRAM, 'args': ['u','v','prev_u']}}
    
#     partTypeToPartConstructorArgs = {'arc':                     ['u','v'],\
#                                      'sibl':                    ['u', 'v1', 'v2'],\
#                                      'nextSibl':                ['u', 'v1', 'v2'],\
#                                      'lastSibl':                ['u','v'],\
#                                      'firstSibl':               ['u','v'],\
#                                      'grandParant':             ['g','u','v'],\
#                                      'grandParantNoGrandChild': ['u','v'],\
#                                      'grandSibl':               ['g','u','v1','v2'],\
#                                      'grandSiblFirstSibl':      ['g','u','v'],\
#                                      'grandSiblLastSibl':       ['g','u','v'],\
#                                      'grandSiblNoSibl':         ['u','v'],\
#                                      'triSibl':                 ['u','v1','v2','v3'],\
#                                      'triSiblFirstSibl':        ['u','v1','v2'],\
#                                      'triSiblLastSibl':         ['u','v1','v2'],\
#                                      'triSiblOnlyChild':        ['u','v1'],\
#                                      'headBigram':              ['u','v','prev_u']}

    def __init__(self):
        self.mapping = {};
        for partType in self.partTypeToPartConstructor.keys():
            self.mapping[partType] = {}
#         self.mapping['arc'] = {}
#         self.mapping['sibl'] = {}
#         self.mapping['nextSibl'] = {}
#         self.mapping['lastSibl'] = {}
#         self.mapping['firstSibl'] = {}
#         self.mapping['grandParant'] = {}
#         self.mapping['grandParantNoGrandChild'] = {}
#         self.mapping['grandSibl'] = {}
#         self.mapping['grandSiblFirstSibl'] = {}
#         self.mapping['grandSiblLastSibl'] = {}
#         self.mapping['grandSiblNoSibl'] = {}
#         self.mapping['triSibl'] = {}
#         self.mapping['triSiblFirstSibl'] = {}
#         self.mapping['triSiblLastSibl'] = {}
#         self.mapping['triSiblOnlyChild'] = {}
#         self.mapping['headBigram'] = {}

    def createPart(self,partType,values):
        key = self.constructKey(partType,values)
#         if partType == 'arc':
#             p = part_DEPENDENCYPART_ARC(values.u, values.v, values.val)
#         elif partType == 'sibl':
#             p = part_DEPENDENCYPART_SIBL(values.u, values.v1, values.v2, values.val)
#         elif partType == 'nextSibl':
#             p = part_DEPENDENCYPART_NEXTSIBL(values.u, values.v1, values.v2, values.val)
#         elif partType == 'lastSibl':
#             p = part_DEPENDENCYPART_NEXTSIBL_LAST_SIB(values.u, values.v, values.val)
#         elif partType == 'firstSibl':
#             p = part_DEPENDENCYPART_NEXTSIBL_FIRST_SIB(values.u, values.v, values.val)
#         elif partType == 'grandParant':
#             p = part_DEPENDENCYPART_GRANDPAR(values.g, values.u, values.v, values.val)
#         elif partType == 'grandParantNoGrandChild':
#             p = part_DEPENDENCYPART_GRANDPAR_NO_GRANDCHILD(values.u, values.v, values.val)
#         elif partType == 'grandSibl':
#             p = part_DEPENDENCYPART_GRANDSIBL(values.g, values.u, values.v1, values.v2, values.val)
#         elif partType == 'grandSiblFirstSibl':
#             p = part_DEPENDENCYPART_GRANDSIBL_FIRST_SIB(values.g, values.u, values.v, values.val)
#         elif partType == 'grandSiblLastSibl':
#             p = part_DEPENDENCYPART_GRANDSIBL_LAST_SIB(values.g, values.u, values.v, values.val)
#         elif partType == 'grandSiblNoSibl':
#             p = part_DEPENDENCYPART_GRANDSIBL_NO_CHILDREN(values.u, values.v, values.val)
#         elif partType == 'triSibl':
#             p = part_DEPENDENCYPART_TRISIBL(values.u, values.v1, values.v2, values.v3, values.val)
#         elif partType == 'triSiblFirstSibl':
#             p = part_DEPENDENCYPART_TRISIBL_FIRST_SIBS(values.u, values.v1, values.v2, values.val)
#         elif partType == 'triSiblLastSibl':
#             p = part_DEPENDENCYPART_TRISIBL_LAST_SIBS(values.u, values.v1, values.v2, values.val)
#         elif partType == 'triSiblOnlyChild':
#             p = part_DEPENDENCYPART_TRISIBL_ONLY_CHILD(values.u, values.v, values.val)
#         elif partType == 'headBigram':
#             p = part_DEPENDENCYPART_HEADBIGRAM(values.u, values.v, values.prev_u, values.val)
        if self.mapping[partType].has_key(key):
            raise "trying to create an existing part"
        pCtor = self.partTypeToPartConstructor[partType]['ctor'];
        p = pCtor(**values)
        self.mapping[partType][key] = p
        return p
    
    def constructKey(self,partType,values):
#         if partType == 'arc':
#             key = (values.u, values.v)
#         elif partType == 'sibl':
#             key = (values.u, values.v1, values.v2)
#         elif partType == 'nextSibl':
#             key = (values.u, values.v1)
#         elif partType == 'lastSibl':
#             key = (values.u, values.v)
#         elif partType == 'firstSibl':
#             key = (values.u, values.v)
#         elif partType == 'grandParant':
#             key = (values.g, values.u, values.v)
#         elif partType == 'grandParantNoGrandChild':
#             key = (values.u, values.v)
#         elif partType == 'grandSibl':
#             key = (values.g, values.u, values.v1, values.v2)
#         elif partType == 'grandSiblFirstSibl':
#             key = (values.g, values.u, values.v)
#         elif partType == 'grandSiblLastSibl':
#             key = (values.g, values.u, values.v)
#         elif partType == 'grandSiblNoSibl':
#             key = (values.g, values.u)
#         elif partType == 'triSibl':
#             key = (values.u, values.v1, values.v2, values.v3)
#         elif partType == 'triSiblFirstSibl':
#             key = (values.u, values.v1, values.v2)
#         elif partType == 'triSiblLastSibl':
#             key = (values.u, values.v1, values.v2)
#         elif partType == 'triSiblOnlyChild':
#             key = (values.u, values.v)
#         elif partType == 'headBigram':
#             key = (values.u, values.v, values.prev_u)
        key = [values[t] for t in self.getKeyFields(partType)]
        return tuple(key)

    def hasPart(self,partType,values):
        key = self.constructKey(partType, values)
        return self.mapping[partType].has_key(key)
        
    def getAllParts(self):
        allP = []
        for partType in self.mapping.keys():
            allP = allP + self.mapping[partType].values()
        return allP
    
    def getKeyFields(self,partType):
        if not self.partTypeToPartConstructor.has_key(partType):
            raise 'bad part type: ' + partType
        return self.partTypeToPartConstructor[partType]['args']