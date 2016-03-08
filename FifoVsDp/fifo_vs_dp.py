#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorCerberus, BBSimulatorDirect
from bbsimulator.scheduler import BBSchedulerCerberus
from bbsimulator.scheduler import BBSchedulerDirectBB, BBSchedulerDirectIO
from bbsimulator.scheduler import BBSchedulerMaxBurstBuffer
from bbsimulator.scheduler import BBSchedulerMaxParallel
from bbsimulator.scheduler import BBSystemBurstBuffer
from bbsimulator.scheduler import BBCpu, BBBurstBuffer, BBIo
from bbsimulator.trace_reader import BBTraceReader
import logging
import numpy as np
import matplotlib.pyplot as plt


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


def runPlainBBScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerCerberus(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_jobs = trace_reader.generateJobs()
    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_plain.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_plain.usg.csv')


def runMaxBBScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerMaxBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_jobs = trace_reader.generateJobs()
    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_maxbb.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_maxbb.usg.csv')


def runMaxParallelScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerMaxParallel(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_jobs = trace_reader.generateJobs()
    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary(file_prefix + '_maxparallel.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_maxparallel.usg.csv')


def cmpDP(prefix, column='response'):
    global figure_no
    first_row = ['jid', 'submit', 'wait_in',
                 'iput', 'wait_run', 'run',
                 'wait_out', 'oput',
                 'complete', 'wait', 'response']
    data2 = np.genfromtxt(prefix + '_maxparallel.out.csv', delimiter=',',
                          skip_header=1, names=first_row)
    data3 = np.genfromtxt(prefix + '_maxbb.out.csv', delimiter=',',
                          skip_header=1, names=first_row)

    time2 = data2[column]
    time3 = data3[column]

    sorted_time2 = np.sort(time2)
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

    sorted_time3 = np.sort(time3)
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    plt.figure(figure_no)
    plt.plot(sorted_time2, yvals2*100, 'r-.', label='maxbb', linewidth=3)
    plt.plot(sorted_time3, yvals3*100, 'g:', label='maxpar', linewidth=3)
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_maxbb_vs_maxpara_%s.eps' % column, fmt='eps')


def cdfPlot(prefix, column='wait'):
    global figure_no
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
    data4 = np.genfromtxt(file_prefix + '_1pio.out.csv', delimiter=',',
                          skip_header=1,
                          names=['jid', 'submit', 'iput',
                                 'run', 'oput', 'complete',
                                 'wait', 'response'])
    data5 = np.genfromtxt(file_prefix + '_1pbb.out.csv', delimiter=',',
                          skip_header=1,
                          names=['jid', 'submit', 'iput',
                                 'run', 'oput', 'complete',
                                 'wait', 'response'])
    data6 = np.genfromtxt(prefix + '_3p_same.out.csv', delimiter=',',
                          skip_header=1, names=first_row)

    time1 = data1[column]
    time2 = data2[column]
    time3 = data3[column]
    time4 = data4[column]
    time5 = data5[column]
    time6 = data6[column]

    sorted_time1 = np.sort(time1)
    yvals1 = np.arange(len(sorted_time1))/float(len(sorted_time1))

    sorted_time2 = np.sort(time2)
    yvals2 = np.arange(len(sorted_time2))/float(len(sorted_time2))

    sorted_time3 = np.sort(time3)
    yvals3 = np.arange(len(sorted_time3))/float(len(sorted_time3))

    sorted_time4 = np.sort(time4)
    yvals4 = np.arange(len(sorted_time4))/float(len(sorted_time4))

    sorted_time5 = np.sort(time5)
    yvals5 = np.arange(len(sorted_time5))/float(len(sorted_time5))

    sorted_time6 = np.sort(time6)
    yvals6 = np.arange(len(sorted_time6))/float(len(sorted_time6))

    plt.figure(figure_no)
    figure_no += 1
    plt.plot(sorted_time1, yvals1*100, 'b--', label='Plain/BB IRO', linewidth=3)
    plt.plot(sorted_time2, yvals2*100, 'r-.', label='Max BB', linewidth=3)
    plt.plot(sorted_time3, yvals3*100, 'g:', label='Max #Tasks', linewidth=3)
    plt.plot(sorted_time4, yvals4*100, 'y-', label='Direct IO', linewidth=3)
    plt.plot(sorted_time5, yvals5*100, 'm-.', label='Direct BB', linewidth=3)
    plt.plot(sorted_time6, yvals6*100, 'c:', label='BB D', linewidth=3)
    plt.legend(loc='lower right')
    plt.savefig(prefix + '_fifo_vs_dp_%s.eps' % column, fmt='eps')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '1000jobs'
    figure_no = 0
    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    data_range = [[1000, 10000, 1000],
                  [1000, 10000, 1000],
                  [1000, 10000, 1000]]
    data = trace_reader.patchTraceFileThreePhases(data_range,
                                                  mod_submit=True)

    cpu = BBCpu(300000, 8, 2.5)
    bb = BBBurstBuffer(4000000, 8, 1)
    io = BBIo(2.5, 1)
    system = BBSystemBurstBuffer(cpu, bb, io)

    # runPlainBBScheduler()
    # runMaxParallelScheduler()
    # runMaxBBScheduler()
    # threePhaseSameData(data)
    # onePhaseIO(data)
    # onePhaseBurstBuffer(data)
    cdfPlot(file_prefix, 'response')
    cmpDP(file_prefix, 'response')
