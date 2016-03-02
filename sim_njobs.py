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
    file_prefix = '1000jobs'
    trace_reader = BBTraceReader(file_prefix + '.swf')
    data_range = [[10000, 40000, 1000],
                  [20000, 60000, 1000],
                  [40000, 100000, 1000]]
    trace_reader.patchTraceFile(data_range)

    cpu = BBCpu(163840, 4000, 4)
    bb = BBBurstBuffer(1600000, 4000, 40)
    io = BBIo(4, 40)
    system = BBSystemBurstBuffer(cpu, bb, io)

    runDirectIOScheduler()
    runPlainBBScheduler()
    runMaxParallelScheduler()
    runMaxBBScheduler()
