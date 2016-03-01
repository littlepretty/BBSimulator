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

waitin1 = data1['complete']
waitin2 = data2['complete']
waitin3 = data3['complete']
waitin_plot = [waitin1, waitin2, waitin3]

print waitin1
print waitin2
print waitin3



label_size = 24 
fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)
bp2 = ax2.boxplot(waitin_plot, patch_artist=True)

for box in bp2['boxes']:
    box.set( color='#7570b3', linewidth=2)
    box.set( facecolor = app_color)

for whisker in bp2['whiskers']:
        whisker.set(color=app_color, linewidth=2)
for cap in bp2['caps']:
        cap.set(color=app_color, linewidth=2)
for median in bp2['medians']:
        median.set(color=app_med_color, linewidth=4)
for flier in bp2['fliers']:
        flier.set(marker='o', color= app_color, alpha=0.8)

ax2.set_xticklabels(['plain','maxpara', 'maxbb'],fontsize = label_size)
plt.yticks(fontsize = label_size)
plt.xticks(fontsize = label_size)
#axes = plt.gca()
#axes.set_ylim([800,4000])
ax2.set_ylabel("Second", fontsize=label_size)
plt.title('\n Wait_In Time', fontsize = 16)

'''
sendtime1 = data1['sendtime']/app_scale
sendtime2 = data2['sendtime']/app_scale
sendtime3 = data3['sendtime']/app_scale
sendtime4 = data4['sendtime']/app_scale

sendtime_plot = [sendtime1, sendtime2, sendtime3, sendtime4] 

avgsdt1= map(truediv,sendtime1,data1['nsend'])
avgsdt2= map(truediv,sendtime2,data1['nsend'])
avgsdt3= map(truediv,sendtime3,data1['nsend'])
avgsdt4= map(truediv,sendtime4,data1['nsend'])
avgsdt_plot = [avgsdt1, avgsdt2, avgsdt3, avgsdt4]

fig = plt.figure(0)
ax = fig.add_subplot(111)
bp = ax.boxplot(avgsdt_plot, patch_artist=True)

for box in bp['boxes']:
    box.set( color='#7570b3', linewidth=2)
    box.set( facecolor = app_color)

for whisker in bp['whiskers']:
        whisker.set(color=app_color, linewidth=2)
for cap in bp['caps']:
        cap.set(color=app_color, linewidth=2)
for median in bp['medians']:
        median.set(color=app_med_color, linewidth=4)
for flier in bp['fliers']:
        flier.set(marker='o', color= app_color, alpha=0.8)

ax.set_xticklabels(['cont_adp','cont_min', 'rand_adp','rand_min'],fontsize = label_size)
plt.yticks(fontsize = label_size)
plt.xticks(fontsize = label_size)
ax.set_ylabel("millisecond", fontsize=label_size)
plt.title(appname + '\nAverage Send Time', fontsize = 16)
'''

plt.show()

