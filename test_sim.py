#!/usr/bin/env python

from simulator import BBSimulator
from simulator import BBEventGenerator, BBEventGeneratorBurstBuffer
from scheduler import BBSchedulerDirectIO, BBSchedulerViaBurstBuffer
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from scheduler import BBSystem, BBSystemBurstBuffer
from scheduler import BBCpu, BBBurstBuffer, BBIo
from job import BBJob, BBJobDemand
from dp_solver import DPSolver
import logging


def testSimulateSchedulerDirectIO():
    cpu = BBCpu(100, 100, 1)
    io = BBIo(1, 10)
    system = BBSystem(cpu, io)

    generator = BBEventGenerator(system)
    scheduler = BBSchedulerDirectIO(system)

    simulator = BBSimulator()
    simulator.setScheduler(scheduler)
    simulator.setGenerator(generator)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 20, demand4, 400)
    job5 = BBJob(5, 20, demand5, 800)

    jobs = [job1, job2, job3, job4, job5]

    simulator.simulate(jobs)
    logging.info(str(system))


def testSimulateSchedulerBurstBuffer():
    cpu = BBCpu(100, 100, 1)
    bb = BBBurstBuffer(1000, 100, 10)
    io = BBIo(1, 10)
    bb_system = BBSystemBurstBuffer(cpu, bb, io)

    bb_generator = BBEventGeneratorBurstBuffer(bb_system)
    bb_scheduler = BBSchedulerViaBurstBuffer(bb_system)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 20, demand4, 400)
    job5 = BBJob(5, 20, demand5, 800)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))


def testSimulateSchedulerMaximizeBB():
    cpu = BBCpu(100, 100, 1)
    bb = BBBurstBuffer(1000, 100, 10)
    io = BBIo(1, 10)
    bb_system = BBSystemBurstBuffer(cpu, bb, io)

    bb_solver = DPSolver()
    bb_generator = BBEventGeneratorBurstBuffer(bb_system)
    bb_scheduler = BBSchedulerMaxBurstBuffer(bb_system, bb_solver)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 20, demand4, 400)
    job5 = BBJob(5, 20, demand5, 800)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))


def testSimulateSchedulerMaximizeParallel():
    cpu = BBCpu(100, 100, 1)
    bb = BBBurstBuffer(1000, 100, 10)
    io = BBIo(1, 10)
    bb_system = BBSystemBurstBuffer(cpu, bb, io)

    bb_solver = DPSolver()
    bb_generator = BBEventGeneratorBurstBuffer(bb_system)
    bb_scheduler = BBSchedulerMaxParallel(bb_system, bb_solver)

    bb_simulator = BBSimulator()
    bb_simulator.setScheduler(bb_scheduler)
    bb_simulator.setGenerator(bb_generator)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 20, demand4, 400)
    job5 = BBJob(5, 20, demand5, 800)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    # num_core, bb_in, bb, data_out
    demand1 = BBJobDemand(30, 800, 400, 500)
    demand2 = BBJobDemand(60, 800, 500, 200)
    demand3 = BBJobDemand(40, 180, 600, 100)
    demand4 = BBJobDemand(30, 100, 800, 800)
    demand5 = BBJobDemand(40, 180, 100, 400)

    testSimulateSchedulerDirectIO()
    testSimulateSchedulerBurstBuffer()
    testSimulateSchedulerMaximizeBB()

    testSimulateSchedulerMaximizeParallel()
