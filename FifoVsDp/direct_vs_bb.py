#!/usr/bin/env python

import logging
import numpy as np
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
    sorted_time1 = np.sort(time1)

    log.info('Worst-case ratio between %s = %.2f' %
             (column, float(sorted_time0[-1]) / sorted_time1[-1]))
    log.add().info('Longest %2f : %.2f' % (sorted_time0[-1], sorted_time1[-1]))
    log.sub()
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

    labels = ['1-Phase IO', 'Cerberus']

    i = 0
    figure_no += 1
    end = -1
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        end = max(end, intervals[-1])
        throughputs = calculateThroughput(finish, intervals)
        avgs.append(np.mean(throughputs))
        i += 1
    i = 0
    end += 180000
    for avg in avgs:
        log.info('Avg Throughput %s = %.3f' % (labels[i], avg))
        i += 1
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
    cdfPlot(file_prefix)
    cdfPlot(file_prefix, 'wait')
    throughputPlot(file_prefix)
