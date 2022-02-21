import math

class Message():
	def __init__(self, i, o):
		self.i = i
		self.o = o
		


class Node():
	def __init__(self, nodeNumber=0, nodeName="f"):
		if (nodeNumber >= 0):
			self.name = nodeName+str(nodeNumber)
		else:
			self.name = nodeName
		self.edges = []
		
	
	
	def addEdge(self, edge):
		self.edges.append(edge)
		
	def printEdges(self):
			for obj in self.edges:
				print(obj.varName)
		
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

def generateMessage(sender, recip):
	if (isinstance(sender, Edge)):
		if( len(sender.nodes) > 1 ): # Not a half-edge -> recursivity needed
			print("This is not a half-edge")
			for obj in sender.nodes: 
				if (obj != recip): #Only enter other connected nodes
					#1. Check if message is already generated
					#2. If not -> generate message for this node
					pass
		elif(len(sender.nodes) == 1): # Half-edge -> no recursivity needed
			#1 Generate Message, should be 1 for half edges
			print("This is a half edge")
				
		else: #Something went wrong, no message can be generated
			print("Error: Unconnected edge")
		return
	elif (isinstance(sender, Node)):
		if ( len(sender.edges) > 1): # Not a leaf node -> recursivity needed
			print("This is not a leaf node")
		elif (len(sender.edges) == 1):
			print("This is a leaf node") #Leaf node -> no recursivity needed
		else:
			print("ERROR: Unconnected node")
		return
	else:
		print("ERROR: Incorrect input")

E = createEdges(1, 2, "E")
B = createEdges(1, 2, "B")
C = createEdges(4, 2, "C")
fB = createNodes(1, "fB")
fE = createNodes(1, "fE")
g = createNodes(1, "g")
T = createEdges(1, 2, "C")

E.addNode(fE)
B.addNode(fB)
E.addNode(g)
B.addNode(g)
T.addNode(fE)
generateMessage(E, fE)
generateMessage(E, fB)
generateMessage(T, fE)
generateMessage(C[0], fB)
