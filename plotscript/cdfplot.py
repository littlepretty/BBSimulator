#!/usr/bin/python
'''
This script is for drawing lines. The result data in data.csv file has 5 columns. The firts col taken as x-axis. And the data
in each other columns will be used for draw different lines; 
'''
from operator import truediv
import numpy as np
import matplotlib.pyplot as plt
appname = 'CR'
cr_color = 'blue'
cr_med_color = 'black'
app_color = cr_color
app_med_color = cr_med_color


#app_scale = 1000000

data1 = np.genfromtxt('../1000jobs_plain.out.csv', delimiter=',', skip_header=1, names=['jid','submit', 'wait_in', 'iput', 'wait_run', 'run', 'wait_out','oput', 'complete', 'wait','response'])
data2 = np.genfromtxt('../1000jobs_maxparallel.out.csv', delimiter=',', skip_header=1, names=['jid','submit', 'wait_in', 'iput', 'wait_run', 'run', 'wait_out','oput', 'complete', 'wait','response'])
data3 = np.genfromtxt('../1000jobs_maxbb.out.csv', delimiter=',', skip_header=1, names=['jid','submit', 'wait_in', 'iput', 'wait_run', 'run', 'wait_out','oput', 'complete', 'wait','response'])

column = 'wait_out'

time1 = data1[column]
time2 = data2[column]
time3 = data3[column]

sorted_time1 = np.sort(time1)
yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

sorted_time2 = np.sort(time2)
yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

sorted_time3 = np.sort(time3)
yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

plt.figure(0)
plt.plot(sorted_time1, yvals1*100, label='plain', linewidth=3 , color='blue', linestyle='--')
plt.plot(sorted_time2, yvals2*100, label='maxbb', linewidth=3 , color='red', linestyle='--')
#plt.plot(sorted_time3, yvals3*100, label='maxpar', linewidth=3 , color='pink', linestyle='--')
plt.show()
