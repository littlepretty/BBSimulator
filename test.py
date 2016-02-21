#!/usr/bin/env python

from simulator import BBSimulator
from scheduler import BBScheduler, BBCpu, BBBurstBuffer, BBIo
from job import BBJob, BBJobDemand
import logging


def testSimulator():
    simulator = BBSimulator()

    cpu = BBCpu(100, 10, 1)
    bb = BBBurstBuffer(200, 10, 1)
    io = BBIo(1, 1)

    scheduler = BBScheduler(cpu, bb, io)
    simulator.setScheduler(scheduler)

    # num_core, bb_in, bb, data_out
    demand1 = BBJobDemand(100, 20, 10, 500)
    job1 = BBJob(1, 0, demand1, 500)
    demand2 = BBJobDemand(60, 40, 80, 200)
    job2 = BBJob(2, 20, demand2, 100)
    demand3 = BBJobDemand(20, 80, 80, 100)
    job3 = BBJob(3, 20, demand3, 100)
    # demand4 = BBJobDemand(3, 10, 60, 50)
    # job4 = BBJob(4, 80, demand4, 200)
    # demand5 = BBJobDemand(3, 40, 20, 30)
    # job5 = BBJob(5, 80, demand5, 200)

    jobs = [job1, job2, job3]
    # jobs = [job1, job2, job3, job4, job5]
    simulator.simulate(jobs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    testSimulator()
