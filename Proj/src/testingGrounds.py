import random
from partsManager import partsManager

class randomer:
    
    def __init__(self,ID):
        self.ID = ID
        
    def getRandom(self):
        try:
            return self.rand
        except AttributeError:
            self.rand = random.random()
            return self.rand

class randomerFactory:
    
    def __init__(self):
        self.id2Rand = {};
        
    def createRandom(self,ID):
        r = randomer(ID)
        self.id2Rand[ID] = r
        return r
    
    def getRandomer(self,ID):
        return self.id2Rand[ID]
    

pm = partsManager()
parts = []
for partType in pm.partTypeToPartConstructor.keys():
    partKeys = pm.getKeyFields(partType)
    values = {'val' : 8}
    i = 0;
    for partKey in partKeys:
        values[partKey] = i
        i += 1
    part = pm.createPart(partType, values)
    print "'" + str(part.__class__) + "' : " + partType + ",\\"
    parts.append(part)
print 1