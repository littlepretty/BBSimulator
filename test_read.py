#!/usr/bin/env python

from simulator import BBSimulatorBurstBuffer
from scheduler import BBSchedulerMaxParallel
from scheduler import BBSystemBurstBuffer, BBCpu, BBBurstBuffer, BBIo
from trace_reader import BBTraceReader
import logging


def testTraceReader():
    cpu = BBCpu(10, 100, 1)
    bb = BBBurstBuffer(2000, 100, 10)
    io = BBIo(1, 10)
    system = BBSystemBurstBuffer(cpu, bb, io)
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_scheduler = BBSchedulerMaxParallel(system)
    bb_simulator.setScheduler(bb_scheduler)
    trace_reader = BBTraceReader('unbb.swf')
    data_range = [[1000, 1600, 100],
                  [1400, 1800, 100],
                  [1600, 1900, 100]]
    bb_jobs = trace_reader.generateJobs(data_range)

    bb_simulator.simulate(bb_jobs)
    bb_scheduler.outputJobSummary('unbb.out.csv')


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    testTraceReader()
