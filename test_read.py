#!/usr/bin/env python

from simulator import BBSimulator
from simulator import BBEventGeneratorBurstBuffer
from scheduler import BBSchedulerViaBurstBuffer, BBCpu, BBBurstBuffer, BBIo
from scheduler import BBSystemBurstBuffer
from trace_reader import BBTraceReader
import logging


def testTraceReader():
    simulator = BBSimulator()

    cpu = BBCpu(100, 100, 1)
    bb = BBBurstBuffer(200, 100, 10)
    io = BBIo(1, 10)

    system = BBSystemBurstBuffer(cpu, bb, io)

    generator = BBEventGeneratorBurstBuffer(system)
    scheduler = BBSchedulerViaBurstBuffer(system)

    simulator.setScheduler(scheduler)
    simulator.setGenerator(generator)

    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    simulator.simulate(jobs)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)
    testTraceReader()
