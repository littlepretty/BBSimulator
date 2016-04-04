#!/usr/bin/env python

import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from bisect import bisect_left, bisect_right
from python_log_indenter import IndentedLoggerAdapter


def utilizationPlot(prefix, column='cpu'):
    global figure_no
    data0 = np.genfromtxt(file_prefix + '_1pio.usg.csv', delimiter=',',
                          skip_header=1,
                          names=['time', 'cpu'])
    data1 = np.genfromtxt(file_prefix + '_1pbb.usg.csv', delimiter=',',
                          skip_header=1,
                          names=['time', 'cpu', 'bb'])
    data2 = np.genfromtxt(prefix + '_3p_same.usg.csv', delimiter=',',
                          skip_header=1, names=['time', 'cpu', 'bb'])
    data3 = np.genfromtxt(prefix + '_plain.usg.csv', delimiter=',',
                          skip_header=1, names=['time', 'cpu', 'bb'])
    x0 = data0['time']
    x1 = data1['time']
    x2 = data2['time']
    x3 = data3['time']

    if column != 'bb':
        y0 = data0[column]
    y1 = data1[column]
    y2 = data2[column]
    y3 = data3[column]

    plt.figure(figure_no)
    figure_no += 1

    if column != 'bb':
        plt.plot(x0, y0, label='1-Phase IO', linewidth=3,
                 color='blue', linestyle='--')
    plt.plot(x1, y1, label='1-Phase BB', linewidth=3,
             color='red', linestyle='--')
    plt.plot(x2, y2, label='1D Cerberus', linewidth=3,
             color='green', linestyle='--')
    plt.plot(x3, y3, label='Cerberus', linewidth=3,
             color='black', linestyle='--')

    plt.legend(loc='lower right')
    plt.savefig(prefix + '_3p_vs_1p_%s.eps' % column, format='eps')


def jobPlot(prefix):
    global figure_no
    data = np.loadtxt(prefix + '.swf.bb', comments=';')

    num_bins = 1000
    counts, rt_bin_edges = np.histogram(data[:, 3], bins=num_bins)
    rt_hist = np.cumsum(counts)
    counts, num_core_bin_edges = np.histogram(data[:, 7], bins=num_bins)
    num_core_hist = np.cumsum(counts)

    plt.figure(figure_no)
    figure_no += 1
    fig, ax1 = plt.subplots()
    x = range(0, len(data[:, 3]))
    ax1.plot(x, data[:, 3], label='Running Time', linewidth=3,
             color='red', linestyle='--')
    ax1.set_ylabel('Running Time', color='r')
    for tl in ax1.get_yticklabels():
        tl.set_color('r')

    ax2 = ax1.twinx()
    ax2.plot(x, data[:, 7], label='Num Cores', linewidth=3,
             color='green', linestyle='--')
    ax2.set_ylabel('Num Cores', color='g')
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    plt.savefig(prefix + '_series.eps', format='eps')
    plt.close()

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(rt_bin_edges[1:], rt_hist, label='Running Time', linewidth=3,
             color='red', linestyle='--')
    plt.plot(num_core_bin_edges[1:], num_core_hist,
             label='Num Cores', linewidth=3,
             color='green', linestyle='--')
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_hist.eps', format='eps')


def timePlot(prefix, column='response'):
    global figure_no
    log.add()
    data1 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1,
                          names=first_row1)
    data2 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)

    if column in ['wait_in', 'wait_out', 'wait_run']:
        time1 = data1['wait']
    else:
        time1 = data1[column]
    time2 = data2[column]
    time3 = data3[column]

    sorted_time1 = np.sort(time1)
    sorted_time2 = np.sort(time2)
    sorted_time3 = np.sort(time3)

    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time1, yvals1*100, 'b-',
             label='1-Phase BB', linewidth=3)
    plt.plot(sorted_time2, yvals2*100, 'r-.',
             label='1D Cerberus', linewidth=3)
    plt.plot(sorted_time3, yvals3*100, 'g--',
             label='Cerberus', linewidth=3)
    log.info('Worst-case ratio between %s' % column)
    log.add().info('%2f : %.2f : %.2f' %
                   (sorted_time1[-1], sorted_time2[-1], sorted_time3[-1]))
    log.sub()

    plt.ylim([0, 101])
    plt.xlabel('Time Duration / Seconds')
    plt.ylabel('Culumative Distribution Function / %')
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.grid()
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_3p_vs_1p_%s.eps' % column, format='eps',
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
    data1 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data2 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    all_data = [data1, data2, data3]
    avgs = []
    lines = ['b:', 'r:', 'g:', 'b', 'r', 'g']
    labels = ['1-Phase BB', '1D Cerberus', 'Cerberus']
    hatches = ['/', '\\', '-']
    width = 40000
    i = 0
    end = -1
    fig, ax1 = plt.subplots()
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        log.info('Max Throughput of %s = %.3f' %
                 (labels[i], np.max(throughputs)))
        avgs.append(np.mean(throughputs))
        end = max(end, intervals[-1])
        ax1.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    i = 0
    end += 50000
    ax2 = ax1.twinx()
    for avg in avgs:
        log.info('Avg Throughput of %s = %.3f' % (labels[i], avg))

        ax2.bar(end + i*width, avg, width, color=lines[i+3],
                label='Avg %s' % labels[i], hatch=hatches[i])
        i += 1
    ax1.legend(loc='upper left', fontsize=16)
    ax2.legend(loc='upper right', fontsize=16)
    ax1.set_xlabel('Time Sequence / Seconds')
    ax1.set_ylabel('#Jobs / 500 Seconds')
    ax2.set_ylabel('Mean #Jobs')
    ax1.set_ylim([0, 16])
    ax2.set_ylim([0, 2.4])
    ax2.set_yticks(np.arange(0, 2.5, 0.3))
    ax1.grid()
    plt.grid()
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.savefig(prefix + '_3p_vs_1p_throughput.eps', fmt='eps')
    log.sub()


if __name__ == '__main__':
    figure_no = 0
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    log = IndentedLoggerAdapter(logging.getLogger(__name__))
    log.info('3P vs 1P')
    file_prefix = '1000jobs'
    first_row3 = ['jid', 'submit', 'wait_in',
                  'iput', 'wait_run', 'run',
                  'wait_out', 'oput',
                  'complete', 'wait', 'response']
    first_row1 = ['jid', 'submit', 'iput',
                  'run', 'oput', 'complete',
                  'wait', 'response']
    font = {'size': 16}
    matplotlib.rc('font', **font)
    matplotlib.rc('lines', lw=3)
    timePlot(file_prefix, 'response')
    timePlot(file_prefix, 'wait')
    timePlot(file_prefix, 'wait_in')
    timePlot(file_prefix, 'wait_run')
    timePlot(file_prefix, 'wait_out')
    jobPlot(file_prefix)
    throughputPlot(file_prefix)
