#!/usr/bin/env python

from simulator import BBSimulator
from scheduler import BBScheduler, BBCpu, BBBurstBuffer, BBIo
from job import BBJob, BBJobDemand
import logging


def testSimulator():
    simulator = BBSimulator()

    cpu = BBCpu(100, 10, 1)
    bb = BBBurstBuffer(2000, 10, 1)
    io = BBIo(1, 1)

    scheduler = BBScheduler(cpu, bb, io)
    simulator.setScheduler(scheduler)

    # num_core, bb_in, bb, data_out
    demand1 = BBJobDemand(10, 20, 10, 50)
    demand2 = BBJobDemand(60, 40, 80, 20)
    demand3 = BBJobDemand(20, 80, 80, 10)
    demand4 = BBJobDemand(30, 10, 600, 80)
    demand5 = BBJobDemand(40, 80, 20, 40)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 0, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 40, demand4, 400)
    job5 = BBJob(5, 80, demand5, 800)

    jobs = [job1, job2, job3, job4, job5]
    simulator.simulate(jobs)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    testSimulator()
