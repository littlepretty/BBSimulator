#!/usr/bin/env python

from simulator import BBSimulator
from simulator import BBEventGenerator, BBEventGeneratorBurstBuffer
from scheduler import BBSchedulerDirectIO, BBSchedulerViaBurstBuffer
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from scheduler import BBSystem, BBSystemBurstBuffer
from scheduler import BBCpu, BBBurstBuffer, BBIo
from job import BBJob, BBJobDemand
from dp_solver import DPSolver
from trace_reader import BBTraceReader
import logging


def testSimulateSchedulerDirectIO():
    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    generator = BBEventGenerator(system)
    scheduler = BBSchedulerDirectIO(system)

    simulator = BBSimulator()
    simulator.setScheduler(scheduler)
    simulator.setGenerator(generator)

    simulator.simulate(jobs)


def testSimulateSchedulerBurstBuffer():
    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    bb_generator = BBEventGeneratorBurstBuffer(system)
    bb_scheduler = BBSchedulerViaBurstBuffer(system)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    bb_simulator.simulate(jobs)


def testSimulateSchedulerMaximizeBB():
    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    bb_solver = DPSolver()
    bb_generator = BBEventGeneratorBurstBuffer(system)
    bb_scheduler = BBSchedulerMaxBurstBuffer(system, bb_solver)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    bb_simulator.simulate(jobs)


def testSimulateSchedulerMaximizeParallel():
    trace_reader = BBTraceReader('test.swf')
    jobs = trace_reader.generateJobs()

    bb_solver = DPSolver()
    bb_generator = BBEventGeneratorBurstBuffer(system)
    bb_scheduler = BBSchedulerMaxParallel(system, bb_solver)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    bb_simulator.simulate(jobs)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    # num_core, to_bb, to_io
    cpu = BBCpu(100, 100, 1)
    # capacity, to_cpu, to_io
    bb = BBBurstBuffer(1000, 100, 10)
    # to_cpu, to_bb
    io = BBIo(1, 10)
    system = BBSystemBurstBuffer(cpu, bb, io)

    testSimulateSchedulerDirectIO()
    testSimulateSchedulerBurstBuffer()
    testSimulateSchedulerMaximizeBB()

    testSimulateSchedulerMaximizeParallel()
