#!/usr/bin/env python

from bbsimulator.scheduler import BBCpu, BBBurstBuffer
from bbsimulator.job import BBJob, BBJobDemand
from bbsimulator.dp_solver import DPSolver
import logging
import time


def testDynamicProgramming():
    cpu = BBCpu(3000, 0.1, 0.001)
    bb = BBBurstBuffer(200, 0.1, 0.001)
    solver = DPSolver()

    # num_core, bb_in, bb_run, data_out
    demand1 = BBJobDemand(100, 12, 10, 50)
    demand2 = BBJobDemand(600, 80, 80, 20)
    demand3 = BBJobDemand(200, 64, 800, 10)
    demand4 = BBJobDemand(300, 24, 600, 80)
    demand5 = BBJobDemand(400, 80, 250, 40)
    demand6 = BBJobDemand(200, 12, 200, 30)
    demand7 = BBJobDemand(200, 10, 100, 30)
    demand8 = BBJobDemand(200, 14, 80, 30)
    demand9 = BBJobDemand(200, 80, 60, 30)

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
    solver.maxStageInBurstBuffer(bb.available, jobs)

    jobs = [job5, job6, job7, job8, job9]
    solver.maxStageInParallelJobs(bb.available, jobs)

    jobs = [job1, job2, job3, job4, job5, job6, job7, job8, job9]
    start = time.clock()
    solver.maxRunningCpuBb(cpu.available, bb.available, jobs)
    logging.info('Optimization time = %.2f seconds' % (time.clock() - start))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)
    testDynamicProgramming()
