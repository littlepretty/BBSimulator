#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorBurstBuffer, BBSimulatorDirect
from bbsimulator.scheduler import BBSchedulerViaBurstBuffer
from bbsimulator.scheduler import BBSchedulerDirectBurstBuffer
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt


def threePhaseDifferentData(data_range):
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerViaBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    data = trace_reader.patchTraceFileThreePhases(data_range, mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_3p_diff.out.csv')
    return data


def threePhaseSameData(data):
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerViaBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_3p_same.out.csv')


def onePhase(data):
    bb_simulator = BBSimulatorDirect(system)
    bb_scheduler = BBSchedulerDirectBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    trace_reader.patchTraceFileOnePhase(data, mod_submit=True)
    jobs = trace_reader.generateJobs()
    bb_simulator.simulate(jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_1p.out.csv')


def cdfPlot(prefix, column='response'):
    first_row = ['jid', 'submit', 'wait_in',
                 'iput', 'wait_run', 'run',
                 'wait_out', 'oput',
                 'complete', 'wait', 'response']
    data0 = np.genfromtxt(file_prefix + '_1p.out.csv', delimiter=',',
                          skip_header=1,
                          names=['jid', 'submit', 'iput',
                                 'run', 'oput', 'complete',
                                 'wait', 'response'])
    data1 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row)
    data2 = np.genfromtxt(prefix + '_3p_diff.out.csv', delimiter=',',
                          skip_header=1, names=first_row)

    time0 = data0[column]
    time1 = data1[column]
    time2 = data2[column]

    sorted_time0 = np.sort(time0)
    yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    sorted_time2 = np.sort(time2)
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

    plt.figure(0)
    plt.plot(sorted_time0, yvals0*100, label='1 phase', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time1, yvals1*100, label='3 phase D', linewidth=3,
             color='red', linestyle='--')
    plt.plot(sorted_time2, yvals2*100, label='3 phase IRO', linewidth=3,
             color='green', linestyle='--')

    plt.legend(loc='lower right')
    # plt.xlim([0, 100000])
    plt.savefig(prefix + '_direct_vs_bb.eps', format='eps')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf')

    cpu = BBCpu(163840, 4000, 7.5)
    bb = BBBurstBuffer(200000, 4000, 400)
    io = BBIo(7.5, 400)
    system = BBSystemBurstBuffer(cpu, bb, io)

    data_range1 = [6000, 10000, 1000]
    data_range3 = [[10, 40, 10],
                   [2000, 6000, 1000],
                   [6000, 10000, 1000]]

    random_data = threePhaseDifferentData(data_range3)
    threePhaseSameData(random_data)
    onePhase(random_data)
    cdfPlot(file_prefix)
