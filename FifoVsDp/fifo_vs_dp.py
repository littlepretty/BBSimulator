#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorBurstBuffer
from bbsimulator.scheduler import BBSchedulerViaBurstBuffer
from bbsimulator.scheduler import BBSchedulerMaxBurstBuffer
from bbsimulator.scheduler import BBSchedulerMaxParallel
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt


def runPlainBBScheduler():
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerViaBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)

    bb_jobs = trace_reader.generateJobs()

    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_plain.out.csv')


def runMaxBBScheduler():
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerMaxBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)

    bb_jobs = trace_reader.generateJobs()

    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_maxbb.out.csv')


def runMaxParallelScheduler():
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerMaxParallel(system)
    bb_simulator.setScheduler(bb_scheduler)

    bb_jobs = trace_reader.generateJobs()

    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_maxparallel.out.csv')


def cdfPlot(prefix, column='wait'):
    first_row = ['jid', 'submit', 'wait_in',
                 'iput', 'wait_run', 'run',
                 'wait_out', 'oput',
                 'complete', 'wait', 'response']
    data1 = np.genfromtxt(prefix + '_plain.out.csv', delimiter=',',
                          skip_header=1, names=first_row)
    data2 = np.genfromtxt(prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row)
    data3 = np.genfromtxt(prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row)

    time1 = data1[column]
    time2 = data2[column]
    time3 = data3[column]

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    sorted_time2 = np.sort(time2)
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

    sorted_time3 = np.sort(time3)
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(0)
    plt.plot(sorted_time1, yvals1*100, label='plain', linewidth=3,
             color='blue', linestyle='--')
    plt.plot(sorted_time2, yvals2*100, label='maxbb', linewidth=3,
             color='red', linestyle='--')
    plt.plot(sorted_time3, yvals3*100, label='maxpar', linewidth=3,
             color='green', linestyle='--')
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_fifo_vs_dp.eps', fmt='eps')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '100jobs_small_data'
    trace_reader = BBTraceReader(file_prefix + '.swf')
    data_range = [[1000, 4000, 100],
                  [2000, 6000, 100],
                  [4000, 10000, 100]]
    trace_reader.patchTraceFile(data_range, mod_submit=True)

    cpu = BBCpu(163840, 4000, 4)
    bb = BBBurstBuffer(160000, 4000, 40)
    io = BBIo(4, 40)
    system = BBSystemBurstBuffer(cpu, bb, io)

    # runPlainBBScheduler()
    # runMaxParallelScheduler()
    # runMaxBBScheduler()
    cdfPlot(file_prefix, 'response')
