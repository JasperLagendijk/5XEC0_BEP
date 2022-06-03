import Factor_Graph as FG
import Codes as Codes
import numpy as np
from pyldpc import encode
from scipy.io import loadmat
import time
from multiprocessing import Process, Manager
import csv
import sys

def decode_LDPC(parity, data, control, checkType, proc_num, return_dict, SNR, factor):
	#Create LDPC framework
	start = time.time()
	LDPC = Codes.generate_LDPC(parity)
	print("LPDC Object created:", time.time()-start)
	n_BE = []
	#Decode data
	for i in range(100):
		message, prob = Codes.calculate_LDPC_LLR(LDPC, data[0:999, i], base=10, option="d", domain="l", checkType=checkType, constant=factor)
		n_BE.append(np.sum(abs(message - control[0:999, i])))
		
	BER = np.mean(n_BE)/len(control[0:999, 0])
	return_dict[proc_num] = [checkType, BER, len(control[0:999, 0])/len(data[0:999, i]), SNR, factor]
	print("The thread for SNR value of", SNR, "and attenuation factor", factor, "took", time.time()-start, "seconds")
	return [checkType, BER, len(control[0:999, 0]), SNR]

fname = ["datasets/dataSet_0.50_1.mat", "datasets/dataSet_0.50_2.mat", "datasets/dataSet_0.50_3.mat", "datasets/dataSet_0.50_4.mat", "datasets/dataSet_0.50_5.mat", "datasets/dataSet_0.50_6.mat", "datasets/dataSet_0.50_7.mat", "datasets/dataSet_0.50_8.mat", ]

fields = ["Type", "Bit Error Rate", "CodeRate", "SNR", "factor"]

start = time.time()
manager = Manager()
return_dict = manager.dict()
jobs = []

version = "attenuated"
factor = [0.001, 0.01, 0.03, 0.05]
coderate = ["1/2", "2/3", "3/4", "5/6"]
bit_rates = []

for j in range(len(fname)):
	annots = loadmat(fname[j])
	parity = np.array([[element for element in upperElement] for upperElement in annots['Hldpc']])
	data = np.array([[element for element in upperElement] for upperElement in annots['dataSet']])
	control = np.array([[element for element in upperElement] for upperElement in annots['control']])
	
	for i in range(len(factor)):
		p = Process(target=decode_LDPC, args=(parity, data, control, version, ((len(factor)*j+i)), return_dict, fname[j][-5], factor[i]))
		jobs.append(p)
		p.start()
	
	#print(jobs)
	
	for proc in jobs:
		proc.join()
	#print(return_dict.values())
	print("SNR:", fname[j][-5])
	
print(time.time() - start)

with open('attenuated_1_2_temp.csv', 'w') as f:
	write = csv.writer(f)
	write.writerow(fields)
	write.writerows(return_dict.values())
