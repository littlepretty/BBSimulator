#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorBurstBuffer, BBSimulatorDirect
from bbsimulator.scheduler import BBSchedulerViaBurstBuffer
from bbsimulator.scheduler import BBSchedulerDirectIO
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt


def runDirectIOScheduler():
    simulator = BBSimulatorDirect(system)
    scheduler = BBSchedulerDirectIO(system)
    simulator.setScheduler(scheduler)

    jobs = trace_reader.generateJobs()

    simulator.simulate(jobs)
    scheduler.outputJobSummary(file_prefix + '_direct.out.csv')


def runPlainBBScheduler():
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerViaBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)

    bb_jobs = trace_reader.generateJobs()

    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_plain.out.csv')


def cdfPlot(prefix, column='response'):
    data0 = np.genfromtxt(prefix + '_direct.out.csv', delimiter=',',
                          skip_header=1, names=['jid', 'submit', 'iput',
                                                'run', 'oput', 'complete',
                                                'wait', 'response'])
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=['jid', 'submit', 'wait_in',
                                                'iput', 'wait_run', 'run',
                                                'wait_out', 'oput',
                                                'complete', 'wait',
                                                'response'])

    time0 = data0[column]
    time1 = data1[column]

    sorted_time0 = np.sort(time0)
    yvals0 = np.arange(len(sorted_time0))/float(len(sorted_time0))

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    plt.figure(0)
    plt.plot(sorted_time0, yvals0*100, label='direct', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time1, yvals1*100, label='plain', linewidth=3,
             color='red', linestyle='--')
    plt.legend(loc='lower right')
    # plt.xlim([0, 100000])
    plt.savefig(prefix + '_direct_vs_bb.eps', format='eps')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf')
    data_range = [[10, 40, 10],
                  [2000, 6000, 1000],
                  [4000, 10000, 1000]]
    trace_reader.patchTraceFileThreePhases(data_range, mod_submit=True)

    cpu = BBCpu(163840, 4000, 7.5)
    bb = BBBurstBuffer(1600000, 4000, 400)
    io = BBIo(7.5, 400)
    system = BBSystemBurstBuffer(cpu, bb, io)

    runDirectIOScheduler()
    runPlainBBScheduler()
    cdfPlot(file_prefix)
