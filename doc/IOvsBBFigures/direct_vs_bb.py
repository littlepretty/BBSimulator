#!/usr/bin/env python

import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from bisect import bisect_left, bisect_right
from python_log_indenter import IndentedLoggerAdapter


def cdfPlot(prefix, column='response'):
    global figure_no
    log.add()
    data0 = np.genfromtxt(prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    time0 = data0[column]
    time1 = data1[column]
    complete0 = data0['complete'][-1]
    complete1 = data1['complete'][-1]
    log.info('Direct IO complete all jobs at %.2f' % complete0)
    log.info('Plain BB complete all jobs at %.2f' % complete1)

    sorted_time0 = np.sort(time0)
    yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    log.info('Worst-case ratio between %s = %.2f' %
             (column, float(sorted_time0[-1]) / sorted_time1[-1]))
    log.add().info('Longest %2f : %.2f' % (sorted_time0[-1], sorted_time1[-1]))
    log.sub()
    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time0, yvals0*100, label='1-Phase IO',
             linewidth=3, color='blue', linestyle='-')
    plt.plot(sorted_time1, yvals1*100, label='Cerberus',
             linewidth=3, color='red', linestyle='--')
    plt.legend(loc='lower right')
    plt.ylim([0, 101])
    plt.xlabel('Time Duration / Seconds')
    plt.ylabel('Cumulative Distribution Function / %')
    plt.grid()
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.savefig(prefix + '_direct_vs_bb_%s.eps' % column, format='eps',
                bbox_inches='tight')
    log.sub()


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
    log.add()
    data1 = np.genfromtxt(prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data2 = np.genfromtxt(file_prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    all_data = [data1, data2]
    avgs = []
    lines = ['b:', 'r-.', 'b', 'r']
    labels = ['1-Phase IO', 'Cerberus']
    hatches = ['/', '\\', '-']
    i = 0
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    figure_no += 1
    width = 80000
    end = -1
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        end = max(end, intervals[-1])
        throughputs = calculateThroughput(finish, intervals)
        avgs.append(np.mean(throughputs))
        ax1.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    i = 0
    end += 180000
    for avg in avgs:
        log.info('Avg Throughput %s = %.3f' % (labels[i], avg))
        ax2.bar(end + width * i, avg, width, hatch=hatches[i],
                color=lines[i+2], label='Avg %s' % labels[i])
        i += 1
    ax1.set_ylim([0, 16])
    ax2.set_ylim([0, 2.0])
    ax2.set_yticks(np.arange(0, 2.1, 0.25))
    ax1.grid()
    plt.grid()
    plt.xlim([0, 1400000])
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.set_xlabel('Time Sequence / Seconds')
    ax1.set_ylabel('#Jobs / 500 Seconds')
    ax2.set_ylabel('Mean #Jobs')
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.savefig(prefix + '_direct_vs_bb_throughput.eps', fmt='eps')
    log.sub()

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    log = IndentedLoggerAdapter(logging.getLogger(__name__))
    log.info('Direct IO vs Cerberus')
    file_prefix = '1000jobs'
    figure_no = 0
    first_row1 = ['jid', 'submit', 'iput',
                  'run', 'oput', 'complete',
                  'wait', 'response']
    first_row3 = ['jid', 'submit', 'wait_in',
                  'iput', 'wait_run', 'run',
                  'wait_out', 'oput', 'complete',
                  'wait', 'response']
    font = {'size': 16}
    matplotlib.rc('font', **font)
    matplotlib.rc('lines', lw=3)
    cdfPlot(file_prefix)
    cdfPlot(file_prefix, 'wait')
    throughputPlot(file_prefix)
