import numpy as np
from numpy.linalg import norm

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
			self.messages = np.concatenate((self.messages, -1 * np.ones((1, edge.nSymbols))))
			
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
			self.messages = np.concatenate((self.messages, -1 * np.ones((1, self.nSymbols))))
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
					if(sum(obj.messages[obj.edgeNames.index(sender.name)]) >= 0):
						prevMessage = obj.messages[obj.edgeNames.index(sender.name)]
						generateMessage(obj, sender)
					
					else:
						obj.messages[obj.edgeNames.index(sender.name)] = 0.5*np.ones(obj.messages[obj.edgeNames.index(sender.name)].shape)
						generateMessage(obj, sender)
						prevMessage = obj.messages[obj.edgeNames.index(sender.name)]
					
					#3. Compare previous message with newly generated message
					delta = prevMessage - obj.messages[obj.edgeNames.index(sender.name)]
					
					print("Delta:", delta)
					
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
			if ( not isinstance(sender.function, str)):
				tempOut = sender.function.copy()
			else:
				print("ERROR: Node without function")
				quit()
				
			for obj in sender.edges:
				if (obj != recip): #Loop through all incomming messages, multiply all messages with outgoing function
					generateMessage(obj, sender)
					tempMessage = obj.messages[obj.nodeNames.index(sender.name)]
					a =  [1] *len(sender.function.shape)
					a[sender.edgeNames.index(obj.name)] = -1
					tempOut *= tempMessage.reshape(tuple(a))
			
			tempTup = list(range( len(sender.function.shape)))
			tempTup.pop(sender.edgeNames.index(recip.name))
			
			messageOut = np.sum(tempOut, tuple(tempTup))
			sender.messages[sender.edgeNames.index(recip.name)] = messageOut
			
		elif (len(sender.edges) == 1):
			print("This is a leaf node") #Leaf node -> no recursivity needed
			if (not isinstance(sender.function, str)):
				sender.messages = np.array(sender.function)
			else:
				print("ERROR: Node without function")
				
		else:
			print("ERROR: Unconnected node")
		return
	else:
		print("ERROR: Incorrect input")


def findMessage(sender, recip):
	if (isinstance(sender, Edge)):
		if (np.sum(sender.messages[sender.nodeNames.index(recip.name)]) < 0): #No message present, generate new message
			generateMessage(sender, recip)
			
		if 	(len(sender.messages.shape) > 1):
			return sender.messages[sender.nodeNames.index(recip.name)]
		else:
			return sender.messages
	elif (isinstance(sender, Node)):
		if (np.sum(sender.messages[sender.edgeNames.index(recip.name)]) < 0): #No message present, generate new message
			generateMessage(sender, recip)
		if 	(len(sender.messages.shape) > 1):
			return sender.messages[sender.edgeNames.index(recip.name)]
		else:
			return sender.messages
		
	else:
		print("ERROR: Incorrect input")


def findMarginal(edge, node):
	a = findMessage(edge, node)
	b = findMessage(node, edge)
	print(a, b)
	marginal = np.divide(a*b, np.sum(a*b))
	
	return marginal


f = createNodes(4)
C = createEdges(4, 2, "C")
B = createEdges(1, 2, "B")
X = createEdges(1, 2)
fB = createNodes(1, "fB")
eq = createNodes(1, "eq")



for i, obj in enumerate(C):
	obj.addNode(f[i])
	obj.addNode(eq)
	
B.addNode(fB)
B.addNode(eq)
X.addNode(f[0])
X.addNode(f[1])

f[0].createFunction(np.array(([0.1, 0.5], [0.3, 0.4])))
f[1].createFunction(np.array(([0.1, 0.5], [0.6, 0.3])))
f[2].createFunction(np.array([0.9, 0.5]))
f[3].createFunction(np.array([0.9, 0.5]))
fB.createFunction(np.array([0.5, 0.5]))
eq.createFunction(np.ones((2,2,2,2,2)))



marginal_B = findMarginal(B, fB)

#print(marginal_E)
print(marginal_B)
