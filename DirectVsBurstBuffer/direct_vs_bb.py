#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorCerberus, BBSimulatorDirect
from bbsimulator.scheduler import BBSchedulerCerberus
from bbsimulator.scheduler import BBSchedulerDirectIO
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt
from bisect import bisect_left, bisect_right


def runDirectIOScheduler(data):
    simulator = BBSimulatorDirect(system)
    scheduler = BBSchedulerDirectIO(system)
    simulator.setScheduler(scheduler)
    simulator.setEventGenerator('IO', system)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    simulator.simulate(jobs)
    scheduler.outputJobSummary(file_prefix + '_direct.out.csv')


def runPlainBBScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerCerberus(system)
    bb_simulator.setScheduler(bb_scheduler)
    data = trace_reader.patchTraceFileThreePhases(data_range,
                                                  mod_submit=True)
    bb_jobs = trace_reader.generateJobs()
    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_plain.out.csv')
    return data


def cdfPlot(prefix, column='response'):
    global figure_no
    data0 = np.genfromtxt(prefix + '_direct.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    time0 = data0[column]
    time1 = data1[column]

    sorted_time0 = np.sort(time0)
    yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time0, yvals0*100, label='Direct IO', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time1, yvals1*100, label='BB Plain', linewidth=3,
             color='red', linestyle='--')
    plt.legend(loc='lower right')
    # plt.xlim([0, 100000])
    plt.savefig(prefix + '_direct_vs_bb_%s.eps' % column, format='eps')


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
    data1 = np.genfromtxt(prefix + '_direct.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data2 = np.genfromtxt(file_prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    lines = ['b:', 'r:', 'g:', 'c-.', 'm-.', 'y:']
    labels = ['Direct IO', 'Plain BB']
    i = 0
    plt.figure(figure_no)
    figure_no += 1
    for data in [data1, data2]:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        plt.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    plt.legend(loc='upper right')
    plt.savefig(prefix + '_direct_vs_bb_throughput.eps', fmt='eps')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    figure_no = 0
    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    data_range = [[1000, 60000, 1000],
                  [1000, 60000, 1000],
                  [1000, 60000, 1000]]
    first_row1 = ['jid', 'submit', 'iput',
                  'run', 'oput', 'complete',
                  'wait', 'response']
    first_row3 = ['jid', 'submit', 'wait_in',
                  'iput', 'wait_run', 'run',
                  'wait_out', 'oput', 'complete',
                  'wait', 'response']
    cpu = BBCpu(300000, 8, 2.5)
    bb = BBBurstBuffer(4000000, 8, 1)
    io = BBIo(2.5, 1)
    system = BBSystemBurstBuffer(cpu, bb, io)

    data = runPlainBBScheduler()
    runDirectIOScheduler(data)

    cdfPlot(file_prefix)
    throughputPlot(file_prefix)
