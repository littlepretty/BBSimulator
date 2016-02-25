#!/usr/bin/env python

from scheduler import BBCpu, BBBurstBuffer
from job import BBJob, BBJobDemand
from dp_solver import DPSolver
import logging


def testDynamicProgramming():
    cpu = BBCpu(100, 10, 1)
    bb = BBBurstBuffer(2000, 10, 1)

    # num_core, bb_in, bb, data_out
    demand1 = BBJobDemand(10, 120, 10, 50)
    demand2 = BBJobDemand(60, 800, 80, 20)
    demand3 = BBJobDemand(20, 640, 800, 10)
    demand4 = BBJobDemand(30, 240, 600, 80)
    demand5 = BBJobDemand(40, 800, 250, 40)
    demand6 = BBJobDemand(20, 120, 200, 30)
    demand7 = BBJobDemand(20, 100, 100, 30)
    demand8 = BBJobDemand(20, 140, 80, 30)
    demand9 = BBJobDemand(20, 80, 60, 30)

    # job_id, sumbit, demand, runtime
    job1 = BBJob(1, 20, demand1, 500)
    job2 = BBJob(2, 20, demand2, 100)
    job3 = BBJob(3, 20, demand3, 600)
    job4 = BBJob(4, 20, demand4, 400)
    job5 = BBJob(5, 20, demand5, 800)
    job6 = BBJob(6, 20, demand6, 800)
    job7 = BBJob(7, 20, demand7, 800)
    job8 = BBJob(8, 20, demand8, 800)
    job9 = BBJob(9, 20, demand9, 800)

    jobs = [job1, job2, job3, job4, job5, job6, job7, job8, job9]
    solver = DPSolver()
    solver.maxStageInBurstBuffer(bb.available, jobs)

    jobs = [job5, job6, job7, job8, job9]
    solver.maxStageInParallelJobs(bb.available, jobs)

    jobs = [job1, job2, job3, job4, job5, job6, job7, job8, job9]
    solver.maxRunningCpuBb(cpu.available, bb.available, jobs)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)
    testDynamicProgramming()
