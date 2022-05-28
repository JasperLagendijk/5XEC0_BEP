import Factor_Graph as FG
import Codes as Codes
import numpy as np
from pyldpc import encode
from scipy.io import loadmat
import time
from multiprocessing import Process, Manager
import csv
def decode_LDPC(parity, data, control, checkType, proc_num, return_dict, SNR):
	#Create LDPC framework
	LDPC = Codes.generate_LDPC(parity)
	
	n_BE = []
	#Decode data
	for i in range(2):
		message, prob = Codes.calculate_LDPC_LLR(LDPC, data[0:999, i], base=10, option="d", domain="l", checkType=checkType, constant=0.5)
		n_BE.append(np.sum(abs(message - control[0:999, i])))
		
	BER = np.mean(n_BE)/len(control[0:999, 0])
	return_dict[proc_num] = [checkType, BER, len(control[0:999, 0])/len(data[0:999, i]), SNR]
	
	return [checkType, BER, len(control[0:999, 0]), SNR]

fname = ["dataSet_0.50_1.mat", "dataSet_0.67_1.mat", "dataSet_0.75_1.mat", "dataSet_0.83_1.mat"]

fields = ["Type", "Bit Error Rate", "Databits"]

start = time.time()
manager = Manager()
return_dict = manager.dict()
jobs = []

versions = ["default", "gallager", "min-sum", "attenuated", "offset"]
coderate = ["1/2", "2/3", "3/4", "5/6"]
bit_rates = []

for j in range(len(fname)):
	annots = loadmat(fname[j])
	parity = np.array([[element for element in upperElement] for upperElement in annots['Hldpc']])
	data = np.array([[element for element in upperElement] for upperElement in annots['dataSet']])
	control = np.array([[element for element in upperElement] for upperElement in annots['control']])
	
	for i in range(len(versions)):
		p = Process(target=decode_LDPC, args=(parity, data, control, versions[i], ((len(versions)*j+i)), return_dict, fname[j][-5]))
		jobs.append(p)
		p.start()
	
	print(jobs)
	
	for proc in jobs:
		proc.join()
	print(return_dict.values())
	
print(time.time() - start)

with open('test.csv', 'w') as f:
	write = csv.writer(f)
	write.writerow(fields)
	write.writerows(return_dict.values())
