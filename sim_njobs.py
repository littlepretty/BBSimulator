#!/usr/bin/env python

from simulator import BBSimulatorBurstBuffer, BBSimulatorDirect
from scheduler import BBSchedulerViaBurstBuffer, BBSchedulerDirectIO
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from scheduler import BBSystemBurstBuffer
from scheduler import BBCpu, BBBurstBuffer, BBIo
from trace_reader import BBTraceReader
import logging


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
    file_prefix = '100jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf')
    data_range = [[1000, 4000, 100],
                  [2000, 8000, 100],
                  [4000, 10000, 100]]
    trace_reader.patchTraceFile(data_range)

    cpu = BBCpu(163840, 4000, 400)
    bb = BBBurstBuffer(80000, 4000, 4000)
    io = BBIo(400, 4000)
    system = BBSystemBurstBuffer(cpu, bb, io)

    runDirectIOScheduler()
    runPlainBBScheduler()
    runMaxParallelScheduler()
    runMaxBBScheduler()
