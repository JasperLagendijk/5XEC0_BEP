import Factor_Graph as FG
import Codes as Codes
import numpy as np
from scipy.io import loadmat


def decode_LDPC(parity, message):
	#Create LDPC code
	LDPC = Codes.generate_LDPC(parity)
	message, prob = Codes.calculate_LDPC_LLR(LDPC, message, domain="l", option="d")
	return message, prob

#parity = Codes.LDPC_parity(b, c)
#parity = np.transpose(np.array(np.mat('1 0 1 0; 0 1 1 0; 0 1 1 1; 1 1 0 0 ; 0 0 1 1; 1 0 0 1; 0 1 0 1; 1 0 1 1')))
#generator = np.array(np.mat('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1; 1 1 0 0; 1 0 1 1; 0 1 1 1; 0 0 1 0'))
annots = loadmat('file.mat')
parity = np.mat([[element for element in upperElement] for upperElement in annots['Hldpc']])
message = np.array([[element for element in upperElement] for upperElement in annots['Coded']])
codeword = np.array([[element for element in upperElement] for upperElement in annots['Data']])

p = np.zeros((len(message), 1))

message = Codes.flip_bit(message, 40)

for i in range(len(message)):
		if (message[i] == 0):
			p[i] = -5
		else:
			p[i] = 5
m, prob = decode_LDPC(parity, p)

error = 0

for i in range(len(m)):
	print(m[i], codeword[i])
	if (m[i] != codeword[i]):
		error += 1
print(error)
'''for i in range(16):
	print("New Codeword:", i)
	p = [0, 0, 0, 0]
	x = bin(i)[2:].zfill(4)
	for j in range(4):
		p[j] = int(x[j])
	print(p)
	
	p = Codes.LDPC_encode_m(p, generator)
	#p = Codes.flip_bit(p)
	
	#print(p)
	for i in range(len(p)):
		if (p[i] == 0):
			p[i] = 0.9
		else:
			p[i] = 0.1
	#m, p  = Codes.calculate_LDPC_LLR(LDPC, b, c, p, domain="p", option="e")		
	#p[2] = 1 - p[2]
	p[2] = 0.5
	p[3] = 0.5
	message, prob = Codes.calculate_LDPC_LLR(LDPC, p, domain="p", option="d")
	#message2, prob2 = Codes.calculate_LDPC_prob(LDPC, b, c, p, domain="p", option="d")
	#print("LLR", message, "Prob", message2) 
	#print("LLR", prob, "Prob", prob2)
	print(message, prob)
	#print(message2, prob2)
	#LDPC.reset()'''

