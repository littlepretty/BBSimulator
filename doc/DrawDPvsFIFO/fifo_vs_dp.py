#!/usr/bin/env python

import logging
import numpy as np
import matplotlib.pyplot as plt
from bisect import bisect_left, bisect_right


def calculateThroughput(finish, interval):
    throughputs = []
    i = 0
    for i in range(1, len(interval)):
        low = bisect_left(finish, interval[i-1])
        high = bisect_right(finish, interval[i])
        if finish[low] != interval[i-1] and high < len(finish) \
                and finish[high] != interval[i]:
            throughputs.append(high - low)
        else:
            throughputs.append(high - low + 1)
    return throughputs


def throughputPlot(prefix, delta=500.0):
    global figure_no
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data2 = np.genfromtxt(file_prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data3 = np.genfromtxt(file_prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    lines = ['b-.', 'r-.', 'g:', 'b', 'r', 'g']
    labels = ['Plain BB', 'Max BB', 'Max #Tasks', 'Plain BB 1D']
    hatches = ['/', '\\', '-']
    all_data = [data1, data2, data3]
    avgs = []
    i = 0
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    figure_no += 1
    width = 20000
    end = -1
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        avgs.append(np.mean(throughputs))

        ax1.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
        end = max(end, intervals[-1])
    i = 0
    end += 10000
    for avg in avgs:
        logging.info('Avg Throughput %s = %.3f' % (labels[i], avg))
        ax2.bar(end + width * i, avg, width, hatch=hatches[i],
                color=lines[i+3], label='Avg %s' % labels[i])
        i += 1

    ax2.set_ylim([2, 2.9])
    ax2.set_yticks(np.arange(2.0, 3.0, 0.1))
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid()
    plt.grid()
    plt.savefig(prefix + '_dp_vs_fifo_throughput.eps', fmt='eps')


def cmpDP(prefix, column='response'):
    global figure_no
    data2 = np.genfromtxt(prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)

    time2 = data2[column]
    time3 = data3[column]

    sorted_time2 = np.sort(time2)
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

    sorted_time3 = np.sort(time3)
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time2, yvals2*100, 'r-.', label='maxbb', linewidth=3)
    plt.plot(sorted_time3, yvals3*100, 'g:', label='maxpar', linewidth=3)
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_maxbb_vs_maxpara_%s.eps' % column, fmt='eps')


def cdfPlot(prefix, column='wait'):
    global figure_no
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data2 = np.genfromtxt(prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data4 = np.genfromtxt(file_prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data5 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data6 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    plt.figure(figure_no)
    figure_no += 1
    labels = ['Plain BB', 'Max BB', 'Max #Tasks']
    lines = ['b-.', 'r:', 'g-.']
    i = 0
    for data in [data1, data2, data3]:
        time = data[column]
        sorted_time = np.sort(time)
        yvals = np.arange(len(sorted_time))/float(len(sorted_time))
        plt.plot(sorted_time, yvals*100, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    plt.ylim([0, 101])
    plt.grid()
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_dp_vs_fifo_%s.eps' % column, fmt='eps')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    first_row3 = ['jid', 'submit', 'wait_in',
                  'iput', 'wait_run', 'run',
                  'wait_out', 'oput',
                  'complete', 'wait', 'response']
    first_row1 = ['jid', 'submit', 'iput',
                  'run', 'oput', 'complete',
                  'wait', 'response']
    figure_no = 0
    cdfPlot(file_prefix, 'response')
    # cmpDP(file_prefix, 'response')
    throughputPlot(file_prefix)
