from graph import DiGraph
from graph import LPMaker
import gurobipy as gp

fileIndex = '6'
inputFile = "./data/output_" + fileIndex + ".txt"
g = DiGraph(inputFile)
lpm = LPMaker(g, "try_input_" + fileIndex, "input_" + fileIndex + ".lp")

bestTree = [];
print "n =",g.n
for i in range(0,g.n - 1):
    v = i + 1
    u = int(g.optHeads[i])
    bestTree.append((u,v))
    print "best tree added (" + str(u) + "," + str(v) + ")"
lpm.createLP(True, bestTree)
lpm.solve()
lpm.model.computeIIS()
for c in lpm.model.getConstrs():
    if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
        print c.getAttr(gp.GRB.Attr.ConstrName),c.getAttr(gp.GRB.Attr.Sense),c.getAttr(gp.GRB.Attr.RHS) 

# names = lpm.getConflictingConstrsNames(lpm.model, lpm.edges, lpm.g.partsManager)
# for name in names:
#     lpm.model.remove(lpm.model.getConstrByName(name))
# 
# lpm.solve("input_" + fileIndex + ".out")
# numRemoved = 0
# while lpm.model.status != gp.GRB.status.OPTIMAL:
#     lpm.model.computeIIS()
#     for c in lpm.model.getConstrs():
#         if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
#             print c.getAttr(gp.GRB.Attr.ConstrName),c.getAttr(gp.GRB.Attr.Sense),c.getAttr(gp.GRB.Attr.RHS) 
#             lpm.model.remove(c)
#             numRemoved += 1
#     lpm.model.update()
#     lpm.solve()
# 
#     
# print "removed", len(names),"+",numRemoved, "constrs"


# for c in lpm.model.getConstrs():
#     if c.getAttr(gp.GRB.Attr.IISConstr) > 0:
#         print c.getAttr(gp.GRB.Attr.ConstrName)
        
print "Ilan"
