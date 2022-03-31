import Factor_Graph as FG
import numpy as np
import random
import math

def LDPC_parity(n, k, j=3):
	matrix = np.zeros((n-k, n))
	
	for x in range(n): #Loop through all columns 
		i = j
		while (i > 0):
			a = random.randrange(0, n-k)
			if(matrix[a][x] == 0):
				matrix[a][x] = 1
				i -= 1
	count_rows = np.sum(matrix, 1)		
	for x in range(n-k):
		if (count_rows[x] == 0): #Add 2 1's
			i = 2
		elif(count_rows[x] == 1): #Add 1 1
			i = 1
		while (i > 0):
			a = random.randrange(0, n)
			if(matrix[x][a] == 0):
				matrix[x][a] = 1
				i -= 1
	n_per_row = math.ceil((n*j)/(n-k))
	
	for x in range(n-k):
		count_rows = np.sum(matrix, 1)
		if (count_rows[x] > n_per_row): #Has too many 1's, move a 1 to a different row
			l = []
			for z in range(n):
				if (matrix[x][z] == 1):
					l.append(z)
			for y in range(n-k):
				while (np.sum(matrix[y]) < n_per_row and np.sum(matrix[x]) > n_per_row): #A 1 can be added to this row
					r = random.choice(l)
					if (matrix[y][r] == 0 and len(l)-n_per_row > 0 and np.sum(matrix[y]) < n_per_row):
						matrix[y][r] = 1
						matrix[x][r] = 0
						l.pop(l.index(r))
	return matrix
	
def generate_LDPC(b, c):
	#Create necessary nodes and edges
	C = FG.createEdges(c, edgeName="C")
	B = FG.createEdges(b, edgeName="B")
	equality = FG.createNodes(c, nodeName="=")
	check = FG.createNodes(c-b, nodeName="+")
	out = FG.createNodes(b, nodeName="b")
	inp = FG.createNodes(c, nodeName="c")
	
	#attach edges and nodes to eachother
	for i, obj in enumerate(C):
		C[i].addNode(equality[i])
		C[i].addNode(inp[i])
		inp[i].createFunction(np.array([0.75, 0.25]))
	for i in range(b):
		B[i].addNode(equality[i])
		B[i].addNode(out[i])
		out[i].createFunction(np.array([0.5, 0.5]))
	parity = LDPC_parity(c, b)
	print(parity)

	interconnect = FG.createEdges(int(np.sum(parity)))
	
	rows = parity.shape[0]
	columns = parity.shape[1]
	a = 0
		
	for i in range(rows):
		for j in range(columns):
			if (parity[i, j] == 1): #Connect equality node with parity check
				interconnect[a].addNode(check[i])
				interconnect[a].addNode(equality[j])
				a += 1
	
	#Adding functions to check and equality nodes
	for i in range(rows):
		check[i].createFunction(nodeType="+")


	for i in range(columns):
		equality[i].createFunction(nodeType="=")
	

	
	#Decoding/encoding LDPC code:
	#1 Set messages outgoing messages from checknodes to [0.5,0.5]
	for i, obj in enumerate(check):
		for j, x in enumerate(check[i].messages):
			check[i].messages[j] = np.array([0.5, 0.5])
	
	prevMessages_B = np.zeros(b)
	
	test = 0
	for k in range(1000):
	#2 Calculate upward Messages
		a = 0
		boolean = True
		#1 Calculate outgoing messages from equality nodes into interconnect
		for i, x in enumerate(equality):
			#1 Take incoming message from interconnect
			for j, obj in enumerate(equality[i].edges):
				equality[i].edges[j].messages[obj.nodeNames.index(equality[i].name)] = obj.nodes[not obj.nodeNames.index(equality[i].name)].messages[obj.nodes[not obj.nodeNames.index(equality[i].name)].edgeNames.index(obj.name)]
				
			#2 Take incoming messages from C and B
			FG.generateMessage(C[i], equality[i])
			
			if(i < c-b):
				FG.generateMessage(B[i], equality[i])

				
			#3 Calculate outgoing messages towards edges
			for outgoing in equality[i].edges: #For each outgoing message
				tempOut = equality[i].function.copy()
				for incoming in equality[i].edges: #Loop through all incoming messages, multiply all messages with outgoing function
					if (incoming != outgoing): 
						tempMessage = incoming.messages[incoming.nodeNames.index(equality[i].name)]
						a =  [1] *len(equality[i].function.shape)
						a[equality[i].edgeNames.index(incoming.name)] = -1
						tempOut *= tempMessage.reshape(tuple(a))
			
				tempTup = list(range( len(equality[i].function.shape)))
				tempTup.pop(equality[i].edgeNames.index(outgoing.name))
				messageOut = np.sum(tempOut, tuple(tempTup))	
				#Normalize messages:
				messageOut = messageOut/(np.sum(messageOut))
				equality[i].messages[equality[i].edgeNames.index(outgoing.name)] = messageOut	

	

	#3 Calculate downward Messages
		for i, x in enumerate(check):
			#1 Take incomming messages from interconnect
			for j, obj in enumerate(check[i].edges):
				check[i].edges[j].messages[obj.nodeNames.index(check[i].name)] = obj.nodes[not obj.nodeNames.index(check[i].name)].messages[obj.nodes[not obj.nodeNames.index(check[i].name)].edgeNames.index(obj.name)]
				
			#2 Calculate outgoing messages towards edges
			for outgoing in check[i].edges: #For each outgoing message
				tempOut = check[i].function.copy()
				for incoming in check[i].edges: #Loop through all incoming messages, multiply all messages with outgoing function
					if (incoming != outgoing): 
						tempMessage = incoming.messages[incoming.nodeNames.index(check[i].name)]
						a =  [1] *len(check[i].function.shape)
						a[check[i].edgeNames.index(incoming.name)] = -1
						tempOut *= tempMessage.reshape(tuple(a))
			
				tempTup = list(range( len(check[i].function.shape)))
				tempTup.pop(check[i].edgeNames.index(outgoing.name))
				messageOut = np.sum(tempOut, tuple(tempTup))
				messageOut = messageOut/(np.sum(messageOut))
				check[i].messages[check[i].edgeNames.index(outgoing.name)] = messageOut	
	
	
	#4 See if the probabilities of outgoing messages have changed (significantly)
		for i, obj in enumerate(B):
			x  = equality[i].messages[equality[i].edgeNames.index(B[i].name), 0]
			if (abs(prevMessages_B[i]-x) > 0.001):
				boolean = False
			prevMessages_B[i] = x
			
		if (boolean):
			break
			
	#5 After looping calculate outoing messages to B
	temp = []
	for i, obj in enumerate(B):
		temp.append(FG.findMarginal(B[i], out[i]))			
	print(temp)
	finalMessage = []
	for obj in temp:
		finalMessage.append(np.argmax(obj))
		
	print(finalMessage)
def generate_RA():
	pass
	
def generate_Turbo():
	pass
