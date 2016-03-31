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
import time


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
    start = time.clock()
    bb_simulator.simulate(bb_jobs)
    logging.info('Simulation FCFS time = %.2f seconds' %
                 (time.clock() - start))
    bb_scheduler.outputJobSummary(file_prefix + '_plain.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_plain.usg.csv')


def runMaxBBScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerMaxBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_jobs = trace_reader.generateJobs()
    start = time.clock()
    bb_simulator.simulate(bb_jobs)
    logging.info('Simulation Max BB time = %.2f seconds' %
                 (time.clock() - start))
    bb_scheduler.outputJobSummary(file_prefix + '_maxbb.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_maxbb.usg.csv')


def runMaxParallelScheduler():
    bb_simulator = BBSimulatorCerberus(system)
    bb_scheduler = BBSchedulerMaxParallel(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_jobs = trace_reader.generateJobs()
    start = time.clock()
    bb_simulator.simulate(bb_jobs)
    logging.info('Simulation Max #Task time = %.2f seconds' %
                 (time.clock() - start))
    bb_scheduler.outputJobSummary(file_prefix + '_maxparallel.out.csv')
    bb_simulator.dumpSystemStatistics(file_prefix + '_maxparallel.usg.csv')


if __name__ == '__main__':
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
    figure_no = 0
    trace_reader = BBTraceReader(file_prefix + '.swf', lam=1)
    data_range = [[1, 60, 1],
                  [1, 60, 1],
                  [1, 60, 1]]
    data = trace_reader.patchTraceFileThreePhases(data_range, mod_submit=True)

    cpu = BBCpu(300000, 0.008, 0.001)
    bb = BBBurstBuffer(4000, 0.008, 0.005)
    io = BBIo(0.001, 0.005)
    system = BBSystemBurstBuffer(cpu, bb, io)

    runPlainBBScheduler()
    runMaxParallelScheduler()
    runMaxBBScheduler()
    threePhaseSameData(data)
    onePhaseIO(data)
    onePhaseBurstBuffer(data)
