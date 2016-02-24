#!/usr/bin/env python

import logging


class DPSolver(object):
    """dynamic programming solver for scheduling"""
    def __init__(self, jobs, available_cpu, available_bb):
        super(DPSolver, self).__init__()
        self.jobs = None

    def maxStageInBurstBuffer(self, BB, all_jobs):
        """maximize utilization of burst buffer"""
        self.jobs = all_jobs
        demand = [job.demand.bb_in for job in self.jobs]
        N = len(demand)
        # memo[i][w] is the optimal solution for jobs[0...i-1]
        # with w GB of burst buffer
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
            if i <= 0:
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

    def maxStageInParallelJobs(self, BB, all_jobs):
        """maximize utilization of burst buffer"""
        self.jobs = all_jobs
        demand = [job.demand.bb_in for job in self.jobs]
        N = len(demand)
        # memo[i][w] is the optimal solution for jobs[0...i-1]
        # with w GB of burst buffer
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
            if i <= 0:
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

    def maxRunningCpuBb(self, CPU, BB, all_jobs):
        """maximize utilization of (cpu, burst buffer) pair"""
        self.jobs = all_jobs
        cpu_demand = [job.demand.num_core for job in self.jobs]
        bb_demand = [job.demand.bb for job in self.jobs]
        N = len(cpu_demand)
        CPU = int(CPU)
        # memo[i][c][w] is the optimal solution for jobs[0...i-1] with
        # c cpus and w GB of burst buffer
        memo = {}
        for job in range(0, N + 1):
            memo[job] = {}
            for cpu in range(0, CPU + 1):
                memo[job][cpu] = {}
        jobs = []

        def recursiveRCB(i, c, w):
            """dynamic programming for 0-1 knapsack problem"""
            if i == 0:
                memo[0][c][w] = 0
                return 0
            elif c in memo[i] and w in memo[i][c]:
                return memo[i][c][w]
            else:
                if cpu_demand[i-1] <= c and bb_demand[i-1] <= w:
                    dp1 = recursiveRCB(i - 1, c - cpu_demand[i-1],
                                       w - bb_demand[i-1]) + \
                        cpu_demand[i-1] * bb_demand[i-1]
                    dp2 = recursiveRCB(i - 1, c, w)
                    if dp1 >= dp2:
                        memo[i][c][w] = dp1
                    else:
                        memo[i][c][w] = dp2
                else:
                    memo[i][c][w] = recursiveRCB(i - 1, c, w)
                return memo[i][c][w]

        def trackBackJobs(i, c, w):
            """return a optimal solution for 0-1 knapsack problem"""
            if i < 0:
                return
            if cpu_demand[i-1] <= c and bb_demand[i-1] <= w:
                if memo[i-1][c - cpu_demand[i-1]][w - bb_demand[i-1]] \
                        + 1 >= memo[i-1][c][w]:
                    jobs.append(self.jobs[i-1])
                    trackBackJobs(i - 1, c - cpu_demand[i-1],
                                  w - bb_demand[i-1])
                else:
                    trackBackJobs(i - 1, c, w)
            else:
                trackBackJobs(i - 1, c, w)

        recursiveRCB(N, CPU, BB)
        trackBackJobs(N, CPU, BB)
        for job in jobs:
            logging.debug('\t ' + str(job))
        logging.debug('\t Maximum value is %.2f' % memo[N][CPU][BB])
        return jobs