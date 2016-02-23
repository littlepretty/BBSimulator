#!/usr/bin/env python

import logging
from job import BBJob


class DPSolver(object):
    """dynamic programming solver for scheduling"""
    def __init__(self, jobs, available_cpu, available_bb):
        super(DPSolver, self).__init__()
        self.jobs = jobs
        self.available_cpu = available_cpu
        self.available_bb = available_bb

    def maxStageInBurstBuffer(self):
        """maximize utilization of burst buffer"""
        demand = [job.demand.bb_in for job in self.jobs]
        N = len(demand)
        BB = self.available_bb
        # memo[i][w] is the optimal solution for jobs[0...i-1]
        memo = [{} for _ in range(0, N+1)]
        jobs = []

        def recursiveMSIBB(i, w):
            """dynamic programming for 0-1 knapsack problem"""
            if i == 0:
                memo[0][w] = 0
                return 0
            elif w in memo[i]:
                return memo[i][w]
            else:
                if demand[i-1] <= w:
                    dp1 = recursiveMSIBB(i - 1, w - demand[i-1]) + demand[i-1]
                    dp2 = recursiveMSIBB(i - 1, w)
                    if dp1 >= dp2:
                        memo[i][w] = dp1
                    else:
                        memo[i][w] = dp2
                else:
                    memo[i][w] = recursiveMSIBB(i - 1, w)
                return memo[i][w]

        def trackBackJobs(i, w):
            """return a optimal solution for 0-1 knapsack problem"""
            if i < 0:
                return
            if demand[i-1] <= w:
                if memo[i-1][w - demand[i-1]] + demand[i-1] >= memo[i-1][w]:
                    jobs.append(self.jobs[i-1])
                    trackBackJobs(i - 1, w - demand[i-1])
                else:
                    trackBackJobs(i - 1, w)
            else:
                trackBackJobs(i - 1, w)

        recursiveMSIBB(N, BB)
        trackBackJobs(N, BB)
        for job in jobs:
            logging.debug('\t ' + str(job))
        logging.debug('\t Maximum value is %.2f' % memo[N][BB])
        return jobs

    def maxStageInParallelJobs(self):
        """maximize utilization of burst buffer"""
        demand = [job.demand.bb_in for job in self.jobs]
        N = len(demand)
        BB = self.available_bb
        # memo[i][w] is the optimal solution for jobs[0...i-1]
        memo = [{} for _ in range(0, N+1)]
        jobs = []

        def recursiveMSIPJ(i, w):
            """dynamic programming for 0-1 knapsack problem"""
            if i == 0:
                memo[0][w] = 0
                return 0
            elif w in memo[i]:
                return memo[i][w]
            else:
                if demand[i-1] <= w:
                    dp1 = recursiveMSIPJ(i - 1, w - demand[i-1]) + 1
                    dp2 = recursiveMSIPJ(i - 1, w)
                    if dp1 >= dp2:
                        memo[i][w] = dp1
                    else:
                        memo[i][w] = dp2
                else:
                    memo[i][w] = recursiveMSIPJ(i - 1, w)
                return memo[i][w]

        def trackBackJobs(i, w):
            """return a optimal solution for 0-1 knapsack problem"""
            if i < 0:
                return
            if demand[i-1] <= w:
                if memo[i-1][w - demand[i-1]] + 1 >= memo[i-1][w]:
                    jobs.append(self.jobs[i-1])
                    trackBackJobs(i - 1, w - demand[i-1])
                else:
                    trackBackJobs(i - 1, w)
            else:
                trackBackJobs(i - 1, w)

        recursiveMSIPJ(N, BB)
        trackBackJobs(N, BB)
        for job in jobs:
            logging.debug('\t ' + str(job))
        logging.debug('\t Maximum value is %.2f' % memo[N][BB])
        return jobs


