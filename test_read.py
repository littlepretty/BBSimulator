#!/usr/bin/env python

from simulator import BBSimulator
from scheduler import BBScheduler, BBCpu, BBBurstBuffer, BBIo
from trace_reader import BBTraceReader
import logging


def testTraceReader():
    simulator = BBSimulator()

    cpu = BBCpu(100, 10, 1)
    bb = BBBurstBuffer(200, 10, 1)
    io = BBIo(1, 1)

    scheduler = BBScheduler(cpu, bb, io)
    simulator.setScheduler(scheduler)

    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    simulator.simulate(jobs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)
    testTraceReader()
