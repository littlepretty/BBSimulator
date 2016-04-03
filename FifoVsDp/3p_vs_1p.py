#!/usr/bin/env python

import logging
import numpy as np
from bisect import bisect_left, bisect_right
from python_log_indenter import IndentedLoggerAdapter


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

    log.info('Worst-case ratio between %s' % column)
    log.add().info('%2f : %.2f : %.2f' %
                   (sorted_time1[-1], sorted_time2[-1], sorted_time3[-1]))
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
    data1 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data2 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    all_data = [data1, data2, data3]
    avgs = []

    labels = ['1-Phase BB', '1D Cerberus', 'Cerberus']
    i = 0
    end = -1
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
        i += 1
    i = 0
    for avg in avgs:
        log.info('Avg Throughput of %s = %.3f' % (labels[i], avg))
        i += 1
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
    timePlot(file_prefix, 'response')
    timePlot(file_prefix, 'wait')
    timePlot(file_prefix, 'wait_in')
    timePlot(file_prefix, 'wait_run')
    timePlot(file_prefix, 'wait_out')
    throughputPlot(file_prefix)
