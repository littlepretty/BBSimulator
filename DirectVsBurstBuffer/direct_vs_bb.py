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
    plt.plot(sorted_time0, yvals0*100, label='Direct IO', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time1, yvals1*100, label='BB Plain', linewidth=3,
             color='red', linestyle='--')
    plt.legend(loc='lower right')
    # plt.xlim([0, 100000])
    plt.savefig(prefix + '_direct_vs_bb_%s.eps' % column, format='eps')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    data_range = [[1000, 60000, 1000],
                  [1000, 60000, 1000],
                  [1000, 60000, 1000]]

    cpu = BBCpu(300000, 8, 2.5)
    bb = BBBurstBuffer(4000000, 8, 1)
    io = BBIo(2.5, 1)
    system = BBSystemBurstBuffer(cpu, bb, io)

    data = runPlainBBScheduler()
    runDirectIOScheduler(data)

    cdfPlot(file_prefix)
