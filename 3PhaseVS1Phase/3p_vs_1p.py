#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorCerberus, BBSimulatorDirect
from bbsimulator.scheduler import BBSchedulerCerberus
from bbsimulator.scheduler import BBSchedulerDirectBB
from bbsimulator.scheduler import BBSchedulerDirectIO
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt
from bisect import bisect_left, bisect_right


def threePhaseDifferentData(data_range):
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerCerberus(system)
    bb_simulator.setScheduler(bb_scheduler)
    data = trace_reader.patchTraceFileThreePhases(data_range,
                                                  mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_3p_diff.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_3p_diff.usg.csv')
    return data


def threePhaseSameData(data):
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerCerberus(system)
    bb_simulator.setScheduler(bb_scheduler)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_3p_same.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_3p_same.usg.csv')


def onePhaseIO(data):
    simulator = BBSimulatorDirect(system)
    scheduler = BBSchedulerDirectIO(system)
    simulator.setScheduler(scheduler)
    simulator.setEventGenerator('IO', system)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    simulator.simulate(jobs)
    scheduler.outputJobSummary(file_prefix + '_1pio.out.csv')
    simulator.dumpSystemStatistics(file_prefix + '_1pio.usg.csv')


def onePhaseBurstBuffer(data):
    bb_simulator = BBSimulatorDirect(system)
    bb_scheduler = BBSchedulerDirectBB(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setEventGenerator('BB', system)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_1pbb.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_1pbb.usg.csv')


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
    data3 = np.genfromtxt(prefix + '_3p_diff.usg.csv', delimiter=',',
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
        plt.plot(x0, y0, label='1 phase IO', linewidth=3,
                 color='blue', linestyle='--')
    plt.plot(x1, y1, label='1 phase BB', linewidth=3,
             color='red', linestyle='--')
    plt.plot(x2, y2, label='3 phase D', linewidth=3,
             color='green', linestyle='--')
    plt.plot(x3, y3, label='3 phase IRO', linewidth=3,
             color='black', linestyle='--')

    plt.legend(loc='lower right')
    plt.savefig(prefix + '_3p_vs_1p_%s.eps' % column, format='eps')


def timePlot(prefix, column='response'):
    global figure_no
    data1 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1,
                          names=first_row1)
    data2 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data3 = np.genfromtxt(prefix + '_3p_diff.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)

    if column in ['wait_in', 'wait_out', 'wait_run']:
        time1 = data1['wait']
    else:
        time1 = data1[column]
    time2 = data2[column]
    time3 = data3[column]
    time2 = [x for x in time2 if x > 10.0]
    time3 = [x for x in time3 if x > 10.0]

    sorted_time1 = np.sort(time1)
    sorted_time2 = np.sort(time2)
    sorted_time3 = np.sort(time3)

    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time1, yvals1*100, label='1 phase BB', linewidth=3,
             color='red', linestyle='--')
    plt.plot(sorted_time2, yvals2*100, label='3 phase D', linewidth=3,
             color='green', linestyle='--')
    plt.plot(sorted_time3, yvals3*100, label='3 phase IRO', linewidth=3,
             color='black', linestyle='--')

    plt.legend(loc='lower right')
    plt.savefig(prefix + '_3p_vs_1p_%s.eps' % column, format='eps')
    # plt.show()


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
    data1 = np.genfromtxt(prefix + '_3p_diff.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    data5 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row1)
    data6 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row3)
    lines = ['b:', 'r:', 'g:', 'c-.', 'm-.', 'y:']
    labels = ['Direct BB', 'Plain BB 1D', 'Plain BB 3P']
    i = 0
    plt.figure(figure_no)
    for data in [data5, data6, data1]:
        finish = data['complete']
        finish = np.sort(finish)
        latest_finish = finish.max()
        intervals = range(0, int(latest_finish + delta), int(delta))
        throughputs = calculateThroughput(finish, intervals)
        plt.plot(intervals[1:], throughputs, lines[i],
                 label=labels[i], linewidth=3)
        i += 1
    plt.legend(loc='upper right')
    plt.savefig(prefix + '3p_vs_1p_throughput.eps', fmt='eps')


if __name__ == '__main__':
    figure_no = 0
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
    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    cpu = BBCpu(300000, 8, 2.5)
    bb = BBBurstBuffer(4000000, 8, 1)
    io = BBIo(2.5, 1)
    system = BBSystemBurstBuffer(cpu, bb, io)
    data_range3 = [[1000, 60000, 1000],
                   [1000, 60000, 1000],
                   [1000, 60000, 1000]]
    random_data = threePhaseDifferentData(data_range3)
    logging.info(str(system))
    threePhaseSameData(random_data)
    logging.info(str(system))
    onePhaseIO(random_data)
    logging.info(str(system))
    onePhaseBurstBuffer(random_data)
    logging.info(str(system))

    timePlot(file_prefix, 'response')
    timePlot(file_prefix, 'wait_run')
    # utilizationPlot(file_prefix, 'cpu')
    # utilizationPlot(file_prefix, 'bb')
    jobPlot(file_prefix)
    throughputPlot(file_prefix)
