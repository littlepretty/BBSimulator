#!/usr/bin/env python

from simulator import BBSimulatorDirect, BBSimulatorBurstBuffer
from scheduler import BBSchedulerDirectIO, BBSchedulerViaBurstBuffer
from scheduler import BBSchedulerMaxBurstBuffer, BBSchedulerMaxParallel
from scheduler import BBSystem, BBSystemBurstBuffer
from scheduler import BBCpu, BBBurstBuffer, BBIo
from job import BBJob, BBJobDemand
import logging


def testSimulateSchedulerDirectIO():
    cpu = BBCpu(100, 100, 1)
    io = BBIo(1, 10)
    system = BBSystem(cpu, io)

    scheduler = BBSchedulerDirectIO(system)
    simulator = BBSimulatorDirect(system)
    simulator.setScheduler(scheduler)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 5000)
    job2 = BBJob(2, 20, demand2, 3000)
    job3 = BBJob(3, 20, demand3, 6000)
    job4 = BBJob(4, 20, demand4, 4000)
    job5 = BBJob(5, 20, demand5, 8000)

    jobs = [job1, job2, job3, job4, job5]

    simulator.simulate(jobs)
    logging.info(str(system))


def testSimulateSchedulerBurstBuffer():
    bb_scheduler = BBSchedulerViaBurstBuffer(bb_system)
    bb_simulator = BBSimulatorBurstBuffer(bb_system)
    bb_simulator.setScheduler(bb_scheduler)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 5000)
    job2 = BBJob(2, 20, demand2, 3000)
    job3 = BBJob(3, 20, demand3, 6000)
    job4 = BBJob(4, 20, demand4, 4000)
    job5 = BBJob(5, 20, demand5, 8000)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))


def testSimulateSchedulerMaximizeBB():
    bb_scheduler = BBSchedulerMaxBurstBuffer(bb_system)
    bb_simulator = BBSimulatorBurstBuffer(bb_system)
    bb_simulator.setScheduler(bb_scheduler)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 5000)
    job2 = BBJob(2, 20, demand2, 3000)
    job3 = BBJob(3, 20, demand3, 6000)
    job4 = BBJob(4, 20, demand4, 4000)
    job5 = BBJob(5, 20, demand5, 8000)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))


def testSimulateSchedulerMaximizeParallel():
    bb_scheduler = BBSchedulerMaxParallel(bb_system)
    bb_simulator = BBSimulatorBurstBuffer(bb_system)
    bb_simulator.setScheduler(bb_scheduler)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 5000)
    job2 = BBJob(2, 20, demand2, 3000)
    job3 = BBJob(3, 20, demand3, 6000)
    job4 = BBJob(4, 20, demand4, 4000)
    job5 = BBJob(5, 20, demand5, 8000)

    jobs = [job1, job2, job3, job4, job5]

    bb_simulator.simulate(jobs)
    logging.info(str(bb_system))

if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    # num_core, data_in, data_run, data_out
    demand1 = BBJobDemand(30, 400, 3000, 5000)
    demand2 = BBJobDemand(60, 800, 5000, 2000)
    demand3 = BBJobDemand(40, 900, 6000, 1000)
    demand4 = BBJobDemand(30, 500, 2000, 8000)
    demand5 = BBJobDemand(40, 600, 1000, 4000)

    cpu = BBCpu(100, 100, 1)
    bb = BBBurstBuffer(10000, 100, 10)
    io = BBIo(1, 10)
    bb_system = BBSystemBurstBuffer(cpu, bb, io)

    testSimulateSchedulerDirectIO()
    testSimulateSchedulerBurstBuffer()
    testSimulateSchedulerMaximizeBB()
    testSimulateSchedulerMaximizeParallel()
