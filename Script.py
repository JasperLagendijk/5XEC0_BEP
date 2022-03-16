import Factor_Graph as FG
import Codes as C
import numpy as np



f = FG.createNodes(3)
C = FG.createEdges(4, 2, "C")
eq = FG.createNodes(1, "eq")

C[0].addNode(f[2])


C[0].addNode(eq)
C[1].addNode(eq)
C[2].addNode(eq)

C[1].addNode(f[0])
C[3].addNode(f[0])

C[3].addNode(f[1])
C[2].addNode(f[1])


f[0].createFunction(np.array(([[0.1, 0.5],[0.5, 0.4]])))
f[1].createFunction(np.array(([[0.1, 0.5], [0.25, 0.45]])))
f[2].createFunction(np.array([0.9, 0.5]))
#f[3].createFunction(np.array([0.9, 0.5]))
#fB.createFunction(np.array([0.5, 0.5]))
#eq.createFunction(np.array([[[0.5, 0.4],[0.2, 0.8]],[[0.4, 0.2],[0.7, 0.9]]]))
eq.createFunction(nodeType="=")

a = eq.function.copy()

for x in f:
	a *= x.function

#print(a.shape)
#print("Equalization function:",eq.function)
marginal = FG.findMarginal(C[0], f[2])

#print(marginal_E)
print(marginal)
