#!/usr/bin/env python

from simulator import BBSimulatorDirect, BBSimulatorBurstBuffer
from scheduler import BBSchedulerDirectIO, BBSchedulerMaxParallel
from scheduler import BBSystemBurstBuffer, BBCpu, BBBurstBuffer, BBIo
from trace_reader import BBTraceReader
import logging


def testTraceReader():
    cpu = BBCpu(10, 100, 1)
    bb = BBBurstBuffer(2000, 100, 10)
    io = BBIo(1, 10)
    system = BBSystemBurstBuffer(cpu, bb, io)

    simulator = BBSimulatorDirect(system)
    bb_simulator = BBSimulatorBurstBuffer(system)

    scheduler = BBSchedulerDirectIO(system)
    bb_scheduler = BBSchedulerMaxParallel(system)

    simulator.setScheduler(scheduler)
    bb_simulator.setScheduler(bb_scheduler)

    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()
    bb_jobs = trace_reader.generateJobs()

    simulator.simulate(jobs)
    bb_simulator.simulate(bb_jobs)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    testTraceReader()
