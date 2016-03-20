#!/usr/bin/env python

import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
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
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(file_prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    lines = ['b:', 'r:', 'g:', 'b', 'r', 'g']
    labels = ['FCFS BB', 'Max BB', 'Max #Tasks', 'FCFS BB 1D']
    hatches = ['/', '\\', '-']
    all_data = [data1, data2, data3]
    avgs = []
    i = 0
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    figure_no += 1
    width = 28000
    end = -1
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        logging.info('Ending time = %.2f' % finish[-1])
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        logging.info('Max throughput = %.3f' % np.max(throughputs))
        avgs.append(np.mean(throughputs))

        ax1.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
        end = max(end, intervals[-1])
    i = 0
    end += 50000
    for avg in avgs:
        logging.info('Avg Throughput %s = %.3f' % (labels[i], avg))
        ax2.bar(end + width * i, avg, width, hatch=hatches[i],
                color=lines[i+3], label='Avg %s' % labels[i])
        i += 1

    ax1.set_ylim([0, 21])
    ax1.set_yticks(np.arange(0.0, 21.1, 4.2))
    ax2.set_ylim([0, 3.0])
    ax2.set_yticks(np.arange(0.0, 3.1, 0.6))
    ax1.grid()
    ax1.legend(loc='upper left', fontsize=14)
    ax2.legend(loc='upper right', fontsize=14)
    ax1.set_xlabel('Time Sequence / Seconds')
    ax1.set_ylabel('#Jobs / 500 Seconds')
    ax2.set_ylabel('Mean #Jobs')
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
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
    labels = ['FCFS BB', 'Max BB', 'Max #Tasks']
    lines = ['b-', 'r:', 'g--']
    i = 0
    for data in [data1, data2, data3]:
        time = data[column]
        sorted_time = np.sort(time)
        logging.info('%s = %.2f' % (column, sorted_time[-1]))
        yvals = np.arange(len(sorted_time))/float(len(sorted_time))
        plt.plot(sorted_time, yvals*100, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    plt.ylim([0, 101])
    plt.grid()
    plt.xlabel('Time Duration / Seconds')
    plt.ylabel('Cumulative Distribution Function / %')
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_dp_vs_fifo_%s.eps' % column, fmt='eps',
                bbox_inches='tight')


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
    font = {'size': 16}
    matplotlib.rc('font', **font)
    matplotlib.rc('lines', lw=3)
    cdfPlot(file_prefix, 'response')
    cdfPlot(file_prefix, 'wait')
    cdfPlot(file_prefix, 'wait_in')
    cdfPlot(file_prefix, 'wait_run')
    cdfPlot(file_prefix, 'wait_out')
    throughputPlot(file_prefix)
