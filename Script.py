import Factor_Graph as FG
import Codes as Codes
import numpy as np
from pyldpc import encode
from scipy.io import loadmat
import time
from multiprocessing import Process, Manager, Pool
import csv
import sys

def decode_LDPC(parity, data, control, checkType, proc_num, return_dict, SNR, factor=0.5):
	#Create LDPC framework
	start = time.time()
	LDPC = Codes.generate_LDPC(parity)
	print("LPDC Object created:", time.time()-start)
	n_BE = []
	#Decode data
	for i in range(100):
		message, prob = Codes.calculate_LDPC_LLR(LDPC, data[0:999, i+(100*0)], base=10, option="d", domain="l", checkType=checkType, constant=factor)
		n_BE.append(np.sum(abs(message - control[0:999, i+(100*0)])))
		
	BER = np.mean(n_BE)/len(control[0:999, 0])
	return_dict[proc_num] = [checkType, BER, len(control[0:999, 0])/len(data[0:999, i]), SNR, factor]
	print("The thread for SNR value of", SNR, "and algorithm", checkType, "had a BER of", BER, " and took", time.time()-start, "seconds")
	return [checkType, BER, len(control[0:999, 0]), SNR]

def generate_work(SNR, checkType, return_dict, proc_num):
	fname = "datasets/dataSet_0.67_"
	annots = loadmat(fname + str(SNR) + ".mat")
	parity = np.array([[element for element in upperElement] for upperElement in annots['Hldpc']])
	data = np.array([[element for element in upperElement] for upperElement in annots['dataSet']])
	control = np.array([[element for element in upperElement] for upperElement in annots['control']])
	
	decode_LDPC(parity, data, control, checkType, proc_num, return_dict, SNR)


#, "datasets/dataSet_0.50_2.mat", "datasets/dataSet_0.50_3.mat", "datasets/dataSet_0.50_4.mat", "datasets/dataSet_0.50_5.mat", "datasets/dataSet_0.50_6.mat", "datasets/dataSet_0.50_7.mat", "datasets/dataSet_0.50_8.mat"]
fields = ["Type", "Bit Error Rate", "CodeRate", "SNR", "factor"]

start = time.time()
manager = Manager()
return_dict = manager.dict()
jobs = []

version = ["gallager", "min-sum", "attenuated"]
#factor = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
coderate = ["1/2", "2/3", "3/4", "5/6"]
bit_rates = []

#for j in range(17, 18):

pool = Pool()
for j in range(len(version)):
	
	for i in range(1, 40):
		proc_num = 40*j+i
		pool.apply_async(generate_work, args=(i, version[j], return_dict, proc_num ))
		print(version[j], i, proc_num)
pool.close()
pool.join()	
	#for i in range(len(version)):
#	p = Process(target=decode_LDPC, args=(parity, data, control, version[0], ((j)), return_dict, j, 0.5))
#	jobs.append(p)
#	p.start()
	
#for proc in jobs:
#		proc.join()

print(time.time() - start)
print(return_dict)
with open('coderate_2_3_temp.csv', 'w') as f:
	write = csv.writer(f)
	write.writerow(fields)
	write.writerows(return_dict.values())
