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


def threePhaseDifferentData(data_range):
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerCerberus(system)
    bb_simulator.setScheduler(bb_scheduler)
    data = trace_reader.patchTraceFileThreePhases(data_range, mod_submit=True)
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
    # plt.show()


def cdfPlot(prefix, column='response'):
    global figure_no
    first_row = ['jid', 'submit', 'wait_in',
                 'iput', 'wait_run', 'run',
                 'wait_out', 'oput',
                 'complete', 'wait', 'response']
    data0 = np.genfromtxt(file_prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1,
                          names=['jid', 'submit', 'iput',
                                 'run', 'oput', 'complete',
                                 'wait', 'response'])
    data1 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1,
                          names=['jid', 'submit', 'iput',
                                 'run', 'oput', 'complete',
                                 'wait', 'response'])
    data2 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row)
    data3 = np.genfromtxt(prefix + '_3p_diff.out.csv', delimiter=',',
                          skip_header=1, names=first_row)

    time0 = data0[column]
    time1 = data1[column]
    time2 = data2[column]
    time3 = data3[column]
    time2 = [x for x in time2 if x > 10.0]
    time3 = [x for x in time3 if x > 10.0]

    sorted_time0 = np.sort(time0)
    sorted_time1 = np.sort(time1)
    sorted_time2 = np.sort(time2)
    sorted_time3 = np.sort(time3)

    yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time0, yvals0*100, label='1 phase IO', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time1, yvals1*100, label='1 phase BB', linewidth=3,
             color='red', linestyle='--')
    plt.plot(sorted_time2, yvals2*100, label='3 phase D', linewidth=3,
             color='green', linestyle='--')
    plt.plot(sorted_time3, yvals3*100, label='3 phase IRO', linewidth=3,
             color='black', linestyle='--')

    plt.legend(loc='lower right')
    plt.savefig(prefix + '_3p_vs_1p_%s.eps' % column, format='eps')
    # plt.show()


if __name__ == '__main__':
    figure_no = 0
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'

    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    # cpu = BBCpu(163840, 4000, 7.5)
    cpu = BBCpu(160000, 6, 0.9)
    bb = BBBurstBuffer(400000, 6, 1)
    io = BBIo(0.9, 1)
    system = BBSystemBurstBuffer(cpu, bb, io)
    data_range3 = [[1000, 10000, 100],
                   [1000, 10000, 100],
                   [1000, 10000, 100]]

    random_data = threePhaseDifferentData(data_range3)
    threePhaseSameData(random_data)
    onePhaseIO(random_data)
    onePhaseBurstBuffer(random_data)

    cdfPlot(file_prefix, 'response')
    cdfPlot(file_prefix, 'wait')
    utilizationPlot(file_prefix, 'cpu')
    utilizationPlot(file_prefix, 'bb')
