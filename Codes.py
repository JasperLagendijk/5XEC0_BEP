import Factor_Graph as FG
import numpy as np
import random
import math

class LDPC_Code():
	def __init__(self, B, C, inp, out, check, equality):
		self.B = B
		self.C = C
		self.inp = inp
		self.out = out
		self.check = check
		self.equality = equality
	def reset(self):
		for i, x in enumerate(self.B):
			for j, y in enumerate(self.B[i].messages):
				self.B[i].messages[j] *= -100 
				self.out[i].messages[j] *= -100 
		for i, x in enumerate(self.C):
			for j, y in enumerate(self.C[i].messages):
				self.C[i].messages[j] *= -100 
				self.equality[i].messages[j] *= -100 
				self.inp[i].messages[j] *= -100 
		for i, x in enumerate(self.check):
			for j, y in enumerate(self.check[i].messages):
				self.check[i].messages[j] *= -100 

def flip_bit(code, n=1):
	temp = []
	i = 0
	if (n > len(code)):
		n = len(code)
	
	while(i < n):
			a = random.randint(0, len(code)-1)
			if (not a in temp):
					i += 1
			code[a] = 1-code[a]
			temp.append(a)
	return code	
		
	

def LDPC_encode_m(code, generator):
	w = np.zeros(max(generator.shape))
	for i, c in enumerate(generator):
		temp = np.sum(generator[i, :]*code) % 2
		if (i > max(generator.shape)-min(generator.shape)):
			temp = not temp
		w[i] = temp
	
	return w

def LDPC_parity(k, n, j=3):
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
	
def generate_LDPC(b, c, parity):
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
		inp[i].createFunction(np.array([0.5, 0.5]))
	for i in range(b):
		B[i].addNode(equality[i])
		B[i].addNode(out[i])
		out[i].createFunction(np.array([0.5, 0.5]))

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
	
	
	LDPC = LDPC_Code(B, C, inp, out, check, equality)
	
	return LDPC

	
	
	

def calculate_LDPC(LDPC, b, c, prob, base=10, option="d", domain="p"): #Decoding/encoding LDPC code:
	
	#0 Initialize probabilities
		#1 Transform to probability domain
	m = []
	if(domain == "l"):
		for p in prob:
			x = pow(base, p)
			y = 1/(x+1)
			a = 1-y
			m.append(np.array([a, y]))
	if(domain == "p"):
		for a in prob:
			m.append(np.array([a, 1-a]))	
							
	if (option == "e"): #Encoding option is chosen, probabilities for incoming bit are enabled
		prevMessages = np.zeros(c)
		if(len(m) != b): #Not enough bits in the codeword -> End program
			print("ERROR: Incorrect codeword length")
			quit()
		for i  in (range(b)): #Set incomming messages
			LDPC.out[i].createFunction(m[i])
			
			
	if (option == "d"):	#Decoding option is chosen, probabilities for 
		prevMessages = np.zeros(b)
		if(len(m) != c): #Not enough bits in the codeword -> End program
			print("ERROR: Incorrect codeword length:", len(m))	
			quit()
		for i  in (range(c)): #Set incomming messages
			LDPC.inp[i].createFunction(m[i])
	
	#1 Set messages outgoing messages from checknodes to [0.5,0.5]
	for i, obj in enumerate(LDPC.check):
		for j, x in enumerate(LDPC.check[i].messages):
			LDPC.check[i].messages[j] = np.array([0.5, 0.5])
	
	
	
	
	test = 0
	for k in range(100):
	#2 Calculate upward Messages
		a = 0
		boolean = True
		#1 Calculate outgoing messages from equality nodes into interconnect
		for i, x in enumerate(LDPC.equality):
			#1 Take incoming message from interconnect
			for j, obj in enumerate(LDPC.equality[i].edges):
				LDPC.equality[i].edges[j].messages[obj.nodeNames.index(LDPC.equality[i].name)] = obj.nodes[not obj.nodeNames.index(LDPC.equality[i].name)].messages[obj.nodes[not obj.nodeNames.index(LDPC.equality[i].name)].edgeNames.index(obj.name)]
				
			#2 Take incoming messages from C and B
			FG.generateMessage(LDPC.C[i], LDPC.equality[i])
			
			if(i < c-b):
				FG.generateMessage(LDPC.B[i], LDPC.equality[i])

			#print("Node:", LDPC.equality[i].name)
			#LDPC.C[i].printNodes()
				
			#3 Calculate outgoing messages towards edges
			for outgoing in LDPC.equality[i].edges: #For each outgoing message
				tempOut = LDPC.equality[i].function.copy()
				for incoming in LDPC.equality[i].edges: #Loop through all incoming messages, multiply all messages with outgoing function
					if (incoming != outgoing): 
						tempMessage = incoming.messages[incoming.nodeNames.index(LDPC.equality[i].name)]
						#print("Message going to:", LDPC.equality[i].name, "from:", incoming.name, ":", tempMessage)
						a =  [1] *len(LDPC.equality[i].function.shape)
						a[LDPC.equality[i].edgeNames.index(incoming.name)] = -1
						tempOut *= tempMessage.reshape(tuple(a))
			
				tempTup = list(range( len(LDPC.equality[i].function.shape)))
				tempTup.pop(LDPC.equality[i].edgeNames.index(outgoing.name))
				messageOut = np.sum(tempOut, tuple(tempTup))	
				#Normalize messages:
				if (np.sum(messageOut) > 0):
					messageOut = messageOut/(np.sum(messageOut))
				#print("Outgoing message from:", LDPC.equality[i].name, "to:", outgoing.name,":", messageOut)
				LDPC.equality[i].messages[LDPC.equality[i].edgeNames.index(outgoing.name)] = messageOut	

	

	#3 Calculate downward Messages
		for i, x in enumerate(LDPC.check):
			#1 Take incomming messages from interconnect
			for j, obj in enumerate(LDPC.check[i].edges):
				LDPC.check[i].edges[j].messages[obj.nodeNames.index(LDPC.check[i].name)] = obj.nodes[not obj.nodeNames.index(LDPC.check[i].name)].messages[obj.nodes[not obj.nodeNames.index(LDPC.check[i].name)].edgeNames.index(obj.name)]
				
			#2 Calculate outgoing messages towards edges
			for outgoing in LDPC.check[i].edges: #For each outgoing message
				tempOut = LDPC.check[i].function.copy()
				for incoming in LDPC.check[i].edges: #Loop through all incoming messages, multiply all messages with outgoing function
					if (incoming != outgoing): 
						tempMessage = incoming.messages[incoming.nodeNames.index(LDPC.check[i].name)]
						#print("Message going to:", LDPC.check[i].name, "from:", incoming.name, ":", tempMessage)
						a =  [1] *len(LDPC.check[i].function.shape)
						a[LDPC.check[i].edgeNames.index(incoming.name)] = -1
						tempOut *= tempMessage.reshape(tuple(a))
			
				tempTup = list(range( len(LDPC.check[i].function.shape)))
				tempTup.pop(LDPC.check[i].edgeNames.index(outgoing.name))
				messageOut = np.sum(tempOut, tuple(tempTup))
				#print("Outgoing message from:", LDPC.check[i].name, "to:", outgoing.name,":", messageOut)	
				if (np.sum(messageOut) > 0):
					messageOut = messageOut/(np.sum(messageOut))
				
				LDPC.check[i].messages[LDPC.check[i].edgeNames.index(outgoing.name)] = messageOut	
	
	
	#4 See if the probabilities of outgoing messages have changed (significantly)
		if (option == "e"): #Encoding option is called, outgoing messages to c are needed
			for i, obj in enumerate(LDPC.C):
				x  = LDPC.equality[i].messages[LDPC.equality[i].edgeNames.index(LDPC.C[i].name), 0]
				if (abs(prevMessages[i]-x) > 0.0001):
					boolean = False
				prevMessages[i] = x
			
		if (option == "d"): #Decoding option is called, outgoing messages to b are needed
			for i, obj in enumerate(LDPC.B):
				x  = LDPC.equality[i].messages[LDPC.equality[i].edgeNames.index(LDPC.B[i].name), 0]
				if (abs(prevMessages[i]-x) > 0.0001):
					boolean = False
				prevMessages[i] = x
			
		if (boolean):
			break
			
	#5 After looping calculate outoing messages 
	temp = []
	finalMessage = []
	if (option == "e"):
		for i, obj in enumerate(LDPC.C):
			temp.append(FG.findMarginal(LDPC.C[i], LDPC.inp[i]))
		print(temp)
		for obj in temp:
			finalMessage.append(np.argmax(obj))
		
	if (option == "d"):
		for i, obj in enumerate(LDPC.B):
			temp.append(FG.findMarginal(LDPC.B[i], LDPC.out[i]))			
	
		for obj in temp:
			finalMessage.append(np.argmax(obj))
		
	return finalMessage, temp

def generate_RA():
	pass
	
def generate_Turbo():
	pass
