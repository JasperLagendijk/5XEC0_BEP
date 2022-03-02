import numpy as np

class Message():
	def __init__(self, varName, message):
		self.varName = varName #List of incomming messages, 2-dimensional array -> x: distribution of vars, y: connected node
		self.message = message #List of outgoing messages, 2-dimensional array -> x: distribution of vars
		


class Node():
	def __init__(self, nodeNumber=0, nodeName="f"):
		if (nodeNumber >= 0):
			self.name = nodeName+str(nodeNumber)
		else:
			self.name = nodeName
		self.edges = []
		self.messages = np.empty((0, 2))
		self.function = "Empty"
		self.edgeNames = []
		
	def addEdge(self, edge):
		if (edge.name in self.edgeNames):
			print("ERROR: Already an edge with that name connected")
		else:
			self.edges.append(edge)
			self.edgeNames.append(edge.name)
			self.messages = np.concatenate((self.messages, np.zeros((1, edge.nSymbols))))
			
	def printEdges(self):
			for obj in self.edges:
				print("Edge: ", obj.name, "Message: ", self.messages[self.edgeNames.index(obj.name)])

		
	def createFunction(self, probArray): #Not finished -> just for now
		self.function = probArray
		pass
		


	
class Edge():
	def __init__(self, edgeNumber=0, nSymbols=2, edgeName="X"):
		self.nSymbols = nSymbols
		self.symbols = list(range(nSymbols))
		if (edgeNumber >= 0):
			self.name = edgeName+str(edgeNumber)
		else:
			self.name = edgeName
		self.nodes = []
		self.messages = np.empty((0, nSymbols))
		self.nodeNames = []
		
	def addNode(self, node):
		if (node.name in self.nodeNames):
			print("ERROR: Already a node with that name connected")
		else:
			self.nodes.append(node)
			self.nodeNames.append(node.name)
			self.messages = np.concatenate((self.messages, np.zeros((1, self.nSymbols))))
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
			tempMessages = -1*np.ones((1, sender.nSymbols))
			for obj in sender.nodes: 
				if (obj != recip): #Only enter other connected nodes
					#1. Check if message is already generated
					#2. If not -> generate message for this node
					generateMessage(obj, sender)
					if (len(obj.messages.shape) == 2): #2dimensional array -> multiple messages
						if(tempMessages[0, 0] != -1):
							tempMessages = np.vstack((tempMessages, obj.messages[obj.edgeNames.index(sender.name), :]))
						else:
							tempMessages[0, 0] = obj.messages[obj.edgeNames.index(sender.name), 0]
							tempMessages[0, 1] = obj.messages[obj.edgeNames.index(sender.name), 1]
					elif(len(obj.messages.shape) == 1):
						if(tempMessages[0, 0] != -1):
							tempMessages = np.vstack((tempMessages, obj.messages))
						else:
							tempMessages[0, 0] = obj.messages[0]
							tempMessages[0, 1] = obj.messages[1]
					
			#3. Loop through for all nodes -> sending message is product of all other messages
			if(tempMessages.shape[0] > 1):			
				messageOut = np.array([np.prod(tempMessages[0, :]), np.prod(tempMessages[0, :])])
			else:
				messageOut = np.array([tempMessages[0, 0], tempMessages[0, 1]])
			
			sender.messages[sender.nodeNames.index(recip.name)] = messageOut	
		elif(len(sender.nodes) == 1): # Half-edge -> no recursivity needed
			#1 Generate Message, should be 1 for half edges
			print("This is a half edge")
			sender.message = [1]
				
		else: #Something went wrong, no message can be generated
			print("ERROR: Unconnected edge")
		return
	
	
	elif (isinstance(sender, Node)):
		if ( len(sender.edges) > 1): # Not a leaf node -> recursivity needed
			print("This is not a leaf node")
			#tempMessages = -1*np.ones((1, recip.nSymbols))
			tempOut = sender.function
			for obj in sender.edges:
				if (obj != recip):
					generateMessage(obj, sender)
					print(obj.name, obj.messages)
					tempMessage = obj.messages[obj.nodeNames.index(sender.name)]
					a =  [1] *len(sender.function.shape)
					a[sender.edgeNames.index(obj.name)] = -1
					tempOut *= tempMessage.reshape(tuple(a))
			
			tempTup = list(range( len(sender.function.shape)))
			tempTup.pop(sender.edgeNames.index(recip.name))

			messageOut = np.sum(tempOut, tuple(tempTup))
			sender.messages[sender.edgeNames.index(recip.name)] = messageOut
			
			print("Marginal: ", messageOut)
		elif (len(sender.edges) == 1):
			print("This is a leaf node") #Leaf node -> no recursivity needed
			if (sender.function != "Empty"):
				sender.messages = np.array(sender.function)
			else:
				print("ERROR: Node without function")
				
		else:
			print("ERROR: Unconnected node")
		return
	else:
		print("ERROR: Incorrect input")


def findMessage(sender, recip):
	






E = createEdges(1, 2, "E")
B = createEdges(1, 2, "B")
C = createEdges(4, 2, "C")
fB = createNodes(1, "fB")
fE = createNodes(1, "fE")
g = createNodes(1, "g")
T = createEdges(1, 2, "C")

fX = createNodes(1, "fX")

E.addNode(fE)
B.addNode(fB)
E.addNode(g)
B.addNode(g)
#B.addNode(fX)

g.createFunction(np.array([[0.001, 0.7],[0.1, 0.9]]))

fE.createFunction([0.99, 0.01])
fB.createFunction([0.99, 0.01])
#fX.createFunction([0.89, 0.11])
generateMessage(E, fE)
generateMessage(B, fB)
g.printEdges()
