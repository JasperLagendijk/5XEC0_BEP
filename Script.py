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
	print("Test", time.time()-start)
	n_BE = []
	#Decode data
	for i in range(1):
		message, prob = Codes.calculate_LDPC_LLR(LDPC, data[0:999, i], base=10, option="d", domain="l", checkType=checkType, constant=factor)
		n_BE.append(np.sum(abs(message - control[0:999, i])))
		
	BER = np.mean(n_BE)/len(control[0:999, 0])
	return_dict[proc_num] = [checkType, BER, len(control[0:999, 0])/len(data[0:999, i]), SNR, factor]
	print("The thread for SNR value of", SNR, "and attenuation factor", factor, "took", time.time()-start, "seconds")
	return [checkType, BER, len(control[0:999, 0]), SNR]

fname = ["datasets/dataSet_0.50_1.mat", "datasets/dataSet_0.67_1.mat", "datasets/dataSet_0.75_1.mat", "datasets/dataSet_0.83_1.mat"]#, "datasets/dataSet_0.83_2.mat", "datasets/dataSet_0.83_3.mat", "datasets/dataSet_0.83_4.mat", "datasets/dataSet_0.83_5.mat", "datasets/dataSet_0.83_6.mat", "datasets/dataSet_0.83_7.mat", "datasets/dataSet_0.83_8.mat", ]#["datasets/dataSet_0.67_1.mat", "datasets/dataSet_0.67_2.mat", "datasets/dataSet_0.67_3.mat", "datasets/dataSet_0.67_4.mat", "datasets/dataSet_0.67_5.mat", "datasets/dataSet_0.67_6.mat", "datasets/dataSet_0.67_7.mat", "datasets/dataSet_0.67_8.mat", "datasets/dataSet_0.75_1.mat", "datasets/dataSet_0.75_2.mat", "datasets/dataSet_0.75_3.mat", "datasets/dataSet_0.75_4.mat", "datasets/dataSet_0.75_5.mat", "datasets/dataSet_0.75_6.mat", "datasets/dataSet_0.75_7.mat", "datasets/dataSet_0.75_8.mat", "datasets/dataSet_0.83_1.mat", "datasets/dataSet_0.83_2.mat", "datasets/dataSet_0.83_3.mat", "datasets/dataSet_0.83_4.mat", "datasets/dataSet_0.83_5.mat", "datasets/dataSet_0.83_6.mat", "datasets/dataSet_0.83_7.mat", "datasets/dataSet_0.83_8.mat"]

fields = ["Type", "Bit Error Rate", "CodeRate", "SNR", "factor"]

start = time.time()
manager = Manager()
return_dict = manager.dict()
jobs = []

version = "attenuated"
factor = [0.1]#, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
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

#with open('attenuated_5_6.csv', 'w') as f:
#	write = csv.writer(f)
#	write.writerow(fields)
#	write.writerows(return_dict.values())
