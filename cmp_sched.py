#!/usr/bin/env python

from bbsimulator.simulator import BBSimulatorDirect, BBSimulatorBurstBuffer
from scheduler import BBSystemBurstBuffer, BBCpu, BBBurstBuffer, BBIo
from scheduler import BBSchedulerDirectIO, BBSchedulerViaBurstBuffer
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from trace_reader import BBTraceReader
import logging


def testSimulateSchedulerDirectIO():
    trace_reader = BBTraceReader('test.swf.bb')
    jobs = trace_reader.generateJobs()
    scheduler = BBSchedulerDirectIO(system)
    simulator = BBSimulatorDirect(system)
    simulator.setScheduler(scheduler)
    simulator.simulate(jobs)


def testSimulateSchedulerBurstBuffer():
    trace_reader = BBTraceReader('test.swf.bb')
    jobs = trace_reader.generateJobs()
    bb_scheduler = BBSchedulerViaBurstBuffer(system)
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.simulate(jobs)


def testSimulateSchedulerMaximizeBB():
    trace_reader = BBTraceReader('test.swf.bb')
    jobs = trace_reader.generateJobs()
    bb_scheduler = BBSchedulerMaxBurstBuffer(system)
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.simulate(jobs)


def testSimulateSchedulerMaximizeParallel():
    trace_reader = BBTraceReader('test.swf.bb')
    jobs = trace_reader.generateJobs()
    bb_scheduler = BBSchedulerMaxParallel(system)
    bb_simulator = BBSimulatorBurstBuffer(system)
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.simulate(jobs)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    # num_core, to_bb, to_io
    cpu = BBCpu(16, 100, 1)
    # capacity, to_cpu, to_io
    # bb = BBBurstBuffer(2000, 100, 10)
    # this setting make naive burst buffer unable to finish all tasks
    bb = BBBurstBuffer(1000, 100, 10)
    # to_cpu, to_bb
    io = BBIo(1, 10)
    system = BBSystemBurstBuffer(cpu, bb, io)

    testSimulateSchedulerDirectIO()
    testSimulateSchedulerBurstBuffer()
    testSimulateSchedulerMaximizeBB()
    testSimulateSchedulerMaximizeParallel()
