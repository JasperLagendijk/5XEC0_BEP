import Factor_Graph as FG
import Codes as Codes
import numpy as np

b = 4
c = 8

#parity = Codes.LDPC_parity(b, c)
parity = np.transpose(np.array(np.mat('1 0 1 0; 0 1 1 0; 0 1 1 1; 1 1 0 0 ; 0 0 1 1; 1 0 0 1; 0 1 0 1; 1 0 1 1')))
generator = np.array(np.mat('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1; 1 1 0 0; 1 0 1 1; 0 1 1 1; 0 0 1 0'))

LDPC = Codes.generate_LDPC(b, c, parity)


for i in range(16):
	print("New Codeword:", i)
	p = [0, 0, 0, 0]
	x = bin(i)[2:].zfill(4)
	for j in range(4):
		p[j] = int(x[j])
	print(p)
	p = Codes.LDPC_encode_m(p, generator)
	print(p)
	#p = Codes.flip_bit(p)
	
	#print(p)
	for i in range(len(p)):
		if (p[i] == 0):
			p[i] = 0.9
		else:
			p[i] = 0.1
	#print(p)
	p[2] = 0.5
	message, prob = Codes.calculate_LDPC_LLR(LDPC, b, c, p, domain="p", option="d")
	message2, prob2 = Codes.calculate_LDPC_prob(LDPC, b, c, p, domain="p", option="d")
	#print("LLR", message, "Prob", message2) 
	#print("LLR", prob, "Prob", prob2)
	print(message, prob)
	LDPC.reset()

