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

		
	def createFunction(self, probArray=np.zeros([2,2]), nodeType="f"): #Not finished -> just for now
		if (nodeType == "f"): #Regular function, array given directly
			self.function = probArray
		
		elif (nodeType == "+"): #Parity-Check node
			l = list([])
			for obj in self.edges:
				l.append(obj.nSymbols)
			tempArray = np.zeros(np.product(l))
			for i, x in enumerate(tempArray):
				if (not (bin(i).count("1") % 2)):
					tempArray[i] = 1	
			self.function = tempArray.reshape(tuple(l))
		
		elif (nodeType == "="): #Equality node
			l = list([])
			for obj in self.edges:
				l.append(obj.nSymbols)
			tempArray = np.zeros(np.product(l))
			tempArray[0] = 1
			tempArray[-1] = 1
			self.function = tempArray.reshape(tuple(l))


	
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
			print("Node: ", obj.name, "Message: ", self.messages[self.nodeNames.index(obj.name)])




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



def generateMessage(sender, recip): #Generates message from acyclic, forest factor graphs
	if (isinstance(sender, Edge)):
		if( len(sender.nodes) > 1 ): # Not a half-edge -> recursivity needed
			print("This is not a half-edge")
			tempMessages = -1*np.ones((1, sender.nSymbols))
			for obj in sender.nodes: 
				if (obj != recip): #Only enter other connected nodes
					#1. Check if message is already generated
					
					if (np.sum(obj.messages[obj.edgeNames.index(sender.name)]) < 0):
						generateMessage(obj, sender)
					
					#print(obj.messages[obj.edgeNames.index(sender.name)])
					
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
					
					#if (np.sum(obj.messages[obj.nodeNames.index(sender.name)]) < 0): #No message present, generate new message
					generateMessage(obj, sender)
					tempMessage = obj.messages[obj.nodeNames.index(sender.name)]
					a =  [1] *len(sender.function.shape)
					a[sender.edgeNames.index(obj.name)] = -1
					tempOut *= tempMessage.reshape(tuple(a))
					#print(tempOut)
			
			tempTup = list(range( len(sender.function.shape)))
			tempTup.pop(sender.edgeNames.index(recip.name))
			
			messageOut = np.sum(tempOut, tuple(tempTup))
			#print(messageOut)
			sender.messages[sender.edgeNames.index(recip.name)] = messageOut
			#print("Outgoing:", tempOut, messageOut)
			
			
			
						
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


def findMessage(sender, recip, l=[]):
	if (isinstance(sender, Edge)):
		#Step 1: Determine if the connected part has a message or not
		#Step 2: Loop through all connected Nodes without a message trying to find forest graph parts and cyclic graph parts
			# For each forest graph part generate incomming message using generateMessage
			# For each cyclic grahp part generate incomming message using generateMessage_cyclic
		
		if (np.sum(sender.messages[sender.nodeNames.index(recip.name)]) < 0): #Step 1
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


