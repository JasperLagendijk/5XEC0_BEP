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
	C = FG.createEdges(c)
	B = FG.createEdges(b)
	equality = FG.createNodes(c)
	
	for i, obj in enumerate(C):
		C[i].addNodes(equality[i])
	
	parity = LDPC_parity(c, b)

def generate_RA():
	pass
	
def generate_Turbo():
	pass
