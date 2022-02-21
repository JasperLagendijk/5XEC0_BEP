class Message():
	def __init__(self, node, edge):
		self.node = node
		self.edge = edge
	


class Node():
	def __init__(self, nodeNumber=0, nodeName="f"):
		if (nodeNumber >= 0):
			self.name = nodeName+str(nodeNumber)
		else:
			self.name = nodeName
		self.edges = []
		
	
	
	def addEdge(self, edge):
		self.edges.append(edge)
		
	def createFunction():
		pass
		
	
class Edge():
	def __init__(self, edgeNumber=0, nSymbols=2, edgeName="X"):
		self.nSymbols = nSymbols
		self.symbols = list(range(nSymbols))
		if (edgeNumber >= 0):
			self.varName = edgeName+str(edgeNumber)
		else:
			self.varName = edgeName
		self.nodes = []
	
	def addNode(self, node):
		self.nodes.append(node)
		node.addEdge(self)
		print(self.nodes[-1].name)
	
	def printNodes(self):
		for obj in self.nodes:
			print(obj.name)
		
def createEdges(nEdges, nSymbols=2, edgeName="X", startVal=1):
	edges = []
	if nEdges > 1:
		for x in range(nEdges):
			edges.append( Edge(startVal+x, nSymbols, edgeName))
		return edges
	else:
		edges = Edge(-1, nSymbols, edgeName)
	return edges

def createNodes(nNodes, nodeName="f", startVal=1):
	nodes = []
	if nNodes > 1:
		for x in range(nNodes):
			nodes.append(Node(startVal+x, nodeName))
		return nodes
	else:
		nodes = Node(-1, nodeName)
	return nodes

print("Hello world")
E = createEdges(1, 2, "E")
B = createEdges(1, 2, "B")
C = createEdges(4, 2, "C")
fB = createNodes(1, "fB")
fE = createNodes(1, "fE")
g = createNodes(1, "g")
E.addNode(fE)
B.addNode(fB)
E.addNode(g)
B.addNode(g)


