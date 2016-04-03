#!/usr/bin/env python

import logging
import numpy as np
from bisect import bisect_left, bisect_right
from python_log_indenter import IndentedLoggerAdapter


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
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data2 = np.genfromtxt(file_prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(file_prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)

    labels = ['FCFS Cerberus', 'MaxT Cerberus', 'MaxP Cerberus']

    all_data = [data1, data2, data3]
    avgs = []
    i = 0
    end = -1
    for data in all_data:
        finish = data['complete']
        finish = np.sort(finish)
        log.info('Ending time of %s = %.2f' % (labels[i], finish[-1]))
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        log.info('Max throughput of %s = %.3f' %
                 (labels[i], np.max(throughputs)))
        avgs.append(np.mean(throughputs))

        i += 1
        end = max(end, intervals[-1])
    i = 0
    end += 50000
    for avg in avgs:
        log.info('Avg Throughput of %s = %.3f' % (labels[i], avg))
        i += 1

    log.sub()


def cdfPlot(prefix, column='wait'):
    global figure_no
    log.add()
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data2 = np.genfromtxt(prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    """data4 = np.genfromtxt(file_prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data5 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data6 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)"""
    figure_no += 1
    labels = ['FCFS Cerberus', 'MaxT Cerberus', 'MaxP Cerberus']

    i = 0
    for data in [data1, data2, data3]:
        time = data[column]
        sorted_time = np.sort(time)
        log.info('%s\'s %s = %.2f' % (labels[i], column, sorted_time[-1]))
        i += 1
    log.sub()


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    log = IndentedLoggerAdapter(logging.getLogger(__name__))
    log.info('Dynamic Programming vs FIFO')
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
    cdfPlot(file_prefix, 'response')
    cdfPlot(file_prefix, 'wait')
    cdfPlot(file_prefix, 'wait_in')
    cdfPlot(file_prefix, 'wait_run')
    cdfPlot(file_prefix, 'wait_out')
    throughputPlot(file_prefix)
