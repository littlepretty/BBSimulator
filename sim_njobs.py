#!/usr/bin/env python

from simulator import BBSimulatorBurstBuffer
from scheduler import BBSchedulerViaBurstBuffer
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from scheduler import BBSystemBurstBuffer, BBCpu, BBBurstBuffer, BBIo
from trace_reader import BBTraceReader
import logging


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

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    file_prefix = '10000jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf')
    data_range = [[1000, 4000, 100],
                  [2000, 8000, 100],
                  [4000, 10000, 100]]
    trace_reader.patchTraceFile(data_range)

    cpu = BBCpu(163840, 16000, 1600)
    bb = BBBurstBuffer(4000000, 16000, 16000)
    io = BBIo(1600, 16000)
    system = BBSystemBurstBuffer(cpu, bb, io)

    runPlainBBScheduler()
    runMaxParallelScheduler()
    runMaxBBScheduler()
