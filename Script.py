import Factor_Graph as FG
import Codes as Codes
import numpy as np
from scipy.io import loadmat

def decode_LDPC(parity, data, LDPC, damp):
	#Create LDPC code
	message, prob = Codes.calculate_LDPC_LLR(LDPC, data, domain="l", option="d", damp=damp)
	return message, prob

LDPC = Codes.generate_LDPC(parity)

message, prob = decode_LDPC(parity, data, LDPC, damp)


