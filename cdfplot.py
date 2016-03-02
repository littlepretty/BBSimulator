#!/usr/bin/python
"""
This script is for drawing lines.
The result data in data.csv file has 5 columns.
The firts col taken as x-axis. And the data
in each other columns will be used for draw different lines.
"""
import numpy as np
import matplotlib.pyplot as plt
import sys


file_prefix = sys.argv[1]
data0 = np.genfromtxt(file_prefix + '_direct.out.csv', delimiter=',',
                      skip_header=1, names=['jid', 'submit', 'iput',
                                            'run', 'oput', 'complete',
                                            'wait', 'response'])
data1 = np.genfromtxt(file_prefix + '_plain.out.csv', delimiter=',',
                      skip_header=1, names=['jid', 'submit', 'wait_in',
                                            'iput', 'wait_run', 'run',
                                            'wait_out', 'oput',
                                            'complete', 'wait', 'response'])
data2 = np.genfromtxt(file_prefix + '_maxparallel.out.csv', delimiter=',',
                      skip_header=1, names=['jid', 'submit', 'wait_in',
                                            'iput', 'wait_run', 'run',
                                            'wait_out', 'oput', 'complete',
                                            'wait', 'response'])
data3 = np.genfromtxt(file_prefix + '_maxbb.out.csv', delimiter=',',
                      skip_header=1, names=['jid', 'submit', 'wait_in',
                                            'iput', 'wait_run', 'run',
                                            'wait_out', 'oput', 'complete',
                                            'wait', 'response'])

column = 'wait_in'

# time0 = data0[column]
time1 = data1[column]
time2 = data2[column]
time3 = data3[column]

# sorted_time0 = np.sort(time0)
# yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))

sorted_time1 = np.sort(time1)
yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

sorted_time2 = np.sort(time2)
yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

sorted_time3 = np.sort(time3)
yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))


plt.figure(0)
# plt.plot(sorted_time0, yvals0*100, label='direct', linewidth=3,
         # color='black', linestyle='--')
plt.plot(sorted_time1, yvals1*100, label='plain', linewidth=3,
         color='blue', linestyle='--')
plt.plot(sorted_time2, yvals2*100, label='maxbb', linewidth=3,
         color='red', linestyle='--')
plt.plot(sorted_time3, yvals3*100, label='maxpar', linewidth=3,
         color='green', linestyle='--')
plt.legend()
plt.show()
