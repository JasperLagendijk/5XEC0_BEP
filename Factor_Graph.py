import numpy as np
import math


class Node():
	def __init__(self, nodeNumber=0, nodeName="f"):
		if (nodeNumber >= 0):
			self.name = nodeName+str(nodeNumber)
		else:
			self.name = nodeName
		self.edges = []
		self.messages = np.empty((0, 2))
		self.messagesLLR = np.empty((0, 1))
		self.function = "Empty"
		self.edgeNames = []
		
	def addEdge(self, edge):
		if (edge.name in self.edgeNames):
			print("ERROR: Already an edge with that name connected")
		else:
			self.edges.append(edge)
			self.edgeNames.append(edge.name)
			self.messages = np.concatenate((self.messages, -1 * np.ones((1, edge.nSymbols))))
			self.messagesLLR = np.concatenate((self.messagesLLR, float("NaN")*np.ones((1, 1))))
			
	def printEdges(self):
		for obj in self.edges:
			print("Edge: ", obj.name, "Message: ", self.messages[self.edgeNames.index(obj.name)])

	def printEdgesLLR(self):
		for obj in self.edges:
			print("Edge: ", obj.name, "Message: ", self.messagesLLR[self.edgeNames.index(obj.name)])
		
		
	def createFunction(self, probArray=np.zeros([2,2]), nodeType="f"): #Not finished -> just for now
		if (nodeType == "f"): #Regular function, array given directly
			self.function = probArray
		
		elif (nodeType == "+"): #Parity-Check node
			l = list([])
			for obj in self.edges:
				l.append(obj.nSymbols)
			tempArray = np.zeros(np.product(l))
			for i, x in enumerate(tempArray):
				if ((bin(i).count("1") % 2)):
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
		self.messagesLLR = np.empty((0, 1))
		self.nodeNames = []
		
	def addNode(self, node):
		if (node.name in self.nodeNames):
			print("ERROR: Already a node with that name connected")
		else:
			self.nodes.append(node)
			self.nodeNames.append(node.name)
			self.messages = np.concatenate((self.messages, -1 * np.ones((1, self.nSymbols))))
			self.messagesLLR = np.concatenate((self.messagesLLR, float("NaN")*np.ones((1, 1))))
			node.addEdge(self)

	
	def printNodes(self):
		for obj in self.nodes:
			print("Node: ", obj.name, "Message: ", self.messages[self.nodeNames.index(obj.name)])
	
	def printNodes(self):
		for obj in self.nodes:
			print("Node: ", obj.name, "Message: ", self.messagesLLR[self.nodeNames.index(obj.name)])



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


def jacobian(L):
        if (not isinstance(L, list)):
                print("ERROR: incorrect input, in Jacobian function")
                return 0
        if(len(L) == 1):
                return L[0]
        if(len(L) == 2):
                return max(L[0], L[1])+math.log(1+math.exp(-abs(L[0]-L[1])))
	
        if (len(L) > 2):
                temp = jacobian([L[-1], L[-2]])
                L.pop(-1)
                L.pop(-1)
                for i in range(len(L)):
                        temp = jacobian([temp, L[-1]])
                        L.pop(-1)
         #Return Jacobian value
                return temp
	
def f_check(x, y):
	return jacobian([x, y]) - jacobian([0, x+y])



def calculateMessageProb(sender, outgoing):
	tempOut = sender.function.copy()
	for incoming in sender.edges: #Loop through all incoming messages, multiply all messages with outgoing function
		if (incoming != outgoing): 
			tempMessage = incoming.messages[incoming.nodeNames.index(sender.name)]
			#print("Message going to:", sender.name, "from:", incoming.name, ":", tempMessage)
			a =  [1] *len(sender.function.shape)
			a[sender.edgeNames.index(incoming.name)] = -1
			tempOut *= tempMessage.reshape(tuple(a))
			
	tempTup = list(range( len(sender.function.shape)))
	tempTup.pop(sender.edgeNames.index(outgoing.name))
	messageOut = np.sum(tempOut, tuple(tempTup))	
	#Normalize messages:
	if (np.sum(messageOut) > 0):
		messageOut = messageOut/(np.sum(messageOut))
	#print("Outgoing message from:", sender.name, "to:", outgoing.name,":", messageOut)
	return messageOut


def calculateMessageParity(sender):
	if (len(sender.edges) == 1): #No parity checking needed
		return 0
	elif (len(sender.edges) == 2):
		return 0
	elif (len(sender.edges) == 3): #Simple parity checking using jacobian logarithm
		for outgoing in sender.edges:
			L = []
			for incoming in sender.edges:
				if incoming != outgoing:
					L.append(incoming.messagesLLR[incoming.nodeNames.index(sender.name)])
			sender.messagesLLR[sender.edgeNames.index(outgoing.name)] =  f_check(L[0], L[1])#jacobian([L[0], L[1]]) - jacobian([0, (L[0]+L[1])])
	
	elif (len(sender.edges) > 3): #Check nodes need to be opened -> spa in check nodes
		U = np.zeros((len(sender.edges)-3, 2))
		L = []
		for incoming in sender.edges:
			L.append(incoming.messagesLLR[incoming.nodeNames.index(sender.name)])
			#print(incoming.messagesLLR[incoming.nodeNames.index(sender.name)], incoming.name)
		#Step 1: Calculate messages inward for first and last U (U2 and UD-2)
		U[0, 0] = f_check(L[0], L[1])
		U[-1, 1] = f_check(L[-1], L[-2])
		
		if (len(sender.edges) > 4):
			for i in range(1, len(sender.edges)-3):
				#set message going right
				U[i, 0] = f_check(U[i-1, 0], L[i+1])
				#set message going left
				U[-(1+i), 1] = f_check(U[-i, 1], L[-(i+2)])
		sender.messagesLLR[0] = f_check(U[0,1], L[1])
		sender.messagesLLR[1] = f_check(U[0, 1], L[0])
		sender.messagesLLR[-2] = f_check(U[-1, 0], L[-1])
		sender.messagesLLR[-1] = f_check(U[-1, 0], L[-2])

		for i in range(2, len(sender.edges)-2):
			sender.messagesLLR[i] = f_check(U[i-2, 0], U[i-1, 1])
	
		
def calculateMessageEquality(sender, outgoing):
	tempOut = 0
	for incoming in sender.edges:
		if (incoming != outgoing):
			tempOut += incoming.messagesLLR[incoming.nodeNames.index(sender.name)] 
	sender.messagesLLR[sender.edgeNames.index(outgoing.name)] = tempOut

def generateMessage(sender, recip): #Generates message from acyclic, forest factor graphs
	if (isinstance(sender, Edge)):
		if( len(sender.nodes) > 1 ): # Not a half-edge -> recursivity needed
			tempMessages = -1*np.ones((1, sender.nSymbols))
			for obj in sender.nodes: 
				if (obj != recip): #Only enter other connected nodes
					#1. Check if message is already generated
					
					if (np.sum(obj.messages[obj.edgeNames.index(sender.name)]) < 0):
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
			sender.message = [1]
				
		else: #Something went wrong, no message can be generated
			print("ERROR: Unconnected edge")
		return
	
	
	elif (isinstance(sender, Node)):
		if ( len(sender.edges) > 1): # Not a leaf node -> recursivity needed
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
			#print("This is a leaf node") #Leaf node -> no recursivity needed
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
		if (np.sum(sender.messages[sender.nodeNames.index(recip.name)]) < 0): #No new message present, generate new message
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
	if (np.sum(a*b) > 0):
		marginal = np.divide(a*b, np.sum(a*b))
	else:
		marginal = a*b
	return marginal


