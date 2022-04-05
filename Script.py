import Factor_Graph as FG
import Codes as Codes
import numpy as np

b = 4
c = 8

parity = Codes.LDPC_parity(b, c)

LDPC = Codes.generate_LDPC(b, c, parity)


Codes.calculate_LDPC(LDPC, b, c)
