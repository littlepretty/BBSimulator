#!/usr/bin/env python

import logging
from job import BBJobStatus
from dp_solver import DPSolver
from tabulate import tabulate
import csv


class BBResource(object):
    """abstract class for all resources"""
    def __init__(self, capacity):
        super(BBResource, self).__init__()
        self.name = ''
        self.capacity = float(capacity)
        self.available = float(capacity)

    def __str__(self):
        return "%.2f available %s" % (self.available, self.name)


class BBCpu(BBResource):
    """CPU"""
    def __init__(self, capacity, to_bb, to_io):
        super(BBCpu, self).__init__(capacity)
        self.name = 'cpu'
        self.to_bb = float(to_bb)
        self.to_io = float(to_io)


class BBBurstBuffer(BBResource):
    """Burst Buffer"""
    def __init__(self, capacity, to_cpu, to_io):
        super(BBBurstBuffer, self).__init__(capacity)
        self.name = 'burst buffer'
        self.to_cpu = float(to_cpu)
        self.to_io = float(to_io)


class BBIo(BBResource):
    """IO nodes"""
    def __init__(self, to_cpu, to_bb):
        super(BBIo, self).__init__(1000000)
        self.name = 'io disk'
        self.to_cpu = float(to_cpu)
        self.to_bb = float(to_bb)


class BBSystem(object):
    def __init__(self, cpu, io):
        super(BBSystem, self).__init__()
        self.cpu = cpu
        self.io = io

    def __str__(self):
        cap = 'System capacity: %d cpu, %.2f GBps IO' % \
            (self.cpu.capacity, self.io.to_cpu)
        available = 'System availability: %d cpu' % self.cpu.available
        return cap + '\n' + available


class BBSystemBurstBuffer(BBSystem):
    def __init__(self, cpu, bb, io):
        super(BBSystemBurstBuffer, self).__init__(cpu, io)
        self.bb = bb

    def __str__(self):
        cap = 'System capacity: %d cpu, %.2f GB burst buffer, %.2f GBps IO' \
            % (self.cpu.capacity, self.bb.capacity, self.io.to_cpu)
        available = 'System availability: %d cpu, %.2f GB burst buffer' \
            % (self.cpu.available, self.bb.available)
        return cap + '\n' + available


class BBSchedulerBase(object):
    """3 phase scheduler"""
    def __init__(self, system):
        super(BBSchedulerBase, self).__init__()
        self.system = system
        self.complete_q = []

    def dumpQueue(self, queue):
        for job in queue:
            logging.debug('\t ' + str(job))

    def dumpResource(self):
        logging.debug('\t Dump resources')
        logging.debug('\t ' + str(self.system))

    def insertToCompleteQ(self, job):
        """Override me when consider burst buffer"""
        job.status = BBJobStatus.Complete
        self.complete_q.append(job)

    def scheduleCore(self, now):
        """override me to do scheduling"""
        return []

    def schedule(self, now):
        return self.scheduleCore(now)

    def dumpJobSummary(self):
        pass

    def outputJobSummary(self, filename):
        pass


class BBSchedulerDirect(BBSchedulerBase):
    """1 phase scheduler with burst buffer demand"""
    def __init__(self, system):
        super(BBSchedulerDirect, self).__init__(system)
        self.direct_q = []

    def insertToDirectQ(self, job):
        job.status = BBJobStatus.WaitInput
        self.direct_q.append(job)

    def insertToCompleteQ(self, job):
        """Override me when consider burst buffer"""
        job.status = BBJobStatus.Complete
        self.system.cpu.available += job.demand.num_core
        self.complete_q.append(job)

    def scheduleDirect(self):
        return []

    def scheduleCore(self, now):
        jobs = self.scheduleDirect()
        for job in jobs:
            job.ts.start_in = now
            job.status = BBJobStatus.Outputing
            logging.debug('\t [%7.2d] Schedule %s' %
                          (now, str(job)))
        if not jobs:
            self.dumpResource()
        return jobs

    def dumpJobSummary(self):
        table = []
        first_row = ['id', 'submit', 'input', 'run',
                     'output', 'complete', 'wait',
                     'response']
        table.append(first_row)
        # self.complete_q.sort(key=lambda job: job.job_id)
        for job in self.complete_q:
            if job.status == BBJobStatus.Complete:
                statistic = job.dumpTimeStatisticDirect()
                table.append(statistic)
        tabulate(table, headers="firstrow", tablefmt='plain')

    def outputJobSummary(self, filename):
        writer = csv.writer(open(filename, 'w'))
        first_row = ['id', 'submit', 'input', 'run',
                     'output', 'complete', 'wait',
                     'response']
        writer.writerow(first_row)
        # self.complete_q.sort(key=lambda job: job.job_id)
        for job in self.complete_q:
            if job.status == BBJobStatus.Complete:
                statistic = job.dumpTimeStatisticDirect()
                writer.writerow(statistic)


class BBSchedulerDirectIO(BBSchedulerDirect):
    """scheduler don't know burst buffer"""
    def __init__(self, system):
        super(BBSchedulerDirectIO, self).__init__(system)

    def scheduleDirect(self):
        "return jobs with status running"
        jobs = []
        # sort descendingly, max cpu utilization
        # sort ascendingly, max parallelism
        # self.direct_q.sort(key=lambda job: job.demand.num_core)
        while len(self.direct_q) > 0 and \
                self.system.cpu.available >= self.direct_q[0].demand.num_core:
            job = self.direct_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            jobs.append(job)
        return jobs


class BBSchedulerDirectBurstBuffer(BBSchedulerDirect):
    """consider burst buffer constraint"""
    def __init__(self, system):
        super(BBSchedulerDirectBurstBuffer, self).__init__(system)

    def insertToCompleteQ(self, job):
        job.status = BBJobStatus.Complete
        self.system.cpu.available += job.demand.num_core
        self.system.bb.available += job.demand.data_in
        self.complete_q.append(job)

    def scheduleDirect(self):
        jobs = []
        while len(self.direct_q) > 0 and \
                self.system.cpu.available >= \
                self.direct_q[0].demand.num_core and \
                self.system.bb.available >= self.direct_q[0].demand.data_in:
            job = self.direct_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            self.system.bb.available -= job.demand.data_in
            jobs.append(job)
        return jobs


class BBSchedulerViaBurstBuffer(BBSchedulerBase):
    """scheduler knows burst buffer"""
    def __init__(self, system):
        super(BBSchedulerViaBurstBuffer, self).__init__(system)
        self.input_q = []
        self.run_q = []
        self.output_q = []

    def dumpInputQ(self):
        logging.debug('\t Dump input queue')
        self.dumpQueue(self.input_q)

    def dumpRunQ(self):
        logging.debug('\t Dump run queue')
        self.dumpQueue(self.run_q)

    def dumpOutputQ(self):
        logging.debug('\t Dump output queue')
        self.dumpQueue(self.output_q)

    def insertToInputQ(self, job):
        job.status = BBJobStatus.WaitInput
        self.input_q.append(job)

    def insertToRunQ(self, job):
        job.status = BBJobStatus.WaitRun
        self.system.bb.available += job.demand.data_in
        self.run_q.append(job)

    def insertToOutputQ(self, job):
        job.status = BBJobStatus.WaitOutput
        self.system.cpu.available += job.demand.num_core
        self.system.bb.available += job.demand.data_run
        self.output_q.append(job)

    def insertToCompleteQ(self, job):
        job.status = BBJobStatus.Complete
        self.system.bb.available += job.demand.data_out
        self.complete_q.append(job)

    def scheduleStageIn(self):
        "greedily choose jobs s.t. max|jobs| with bb constraint"
        jobs = []
        # sort descendingly, max data throughput
        # sort ascendingly, max parallelism
        # self.input_q.sort(key=lambda job: job.demand.data_in)
        while len(self.input_q) > 0 and \
                self.system.bb.available >= self.input_q[0].demand.data_in:
            job = self.input_q.pop(0)
            self.system.bb.available -= job.demand.data_in
            jobs.append(job)
        return jobs

    def scheduleRun(self):
        "greedily choose jobs s.t. max|jobs| with cpu and bb constraint"
        jobs = []
        # self.run_q.sort(key=lambda job: job.demand.num_core)
        while len(self.run_q) > 0 and \
                self.system.cpu.available >= self.run_q[0].demand.num_core and\
                self.system.bb.available >= self.run_q[0].demand.data_run:
            job = self.run_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            self.system.bb.available -= job.demand.data_run
            jobs.append(job)
        return jobs

    def scheduleStageOut(self):
        "greedily choose jobs s.t. max|jobs| with bb constraint"
        jobs = []
        # self.output_q.sort(key=lambda job: job.demand.data_out)
        while len(self.output_q) > 0 and \
                self.system.bb.available >= self.output_q[0].demand.data_out:
            job = self.output_q.pop(0)
            self.system.bb.available -= job.demand.data_out
            jobs.append(job)
        return jobs

    def scheduleCore(self, now):
        """
        return scheduled jobs with proper status
        """
        job_ins = self.scheduleStageIn()
        for job in job_ins:
            job.ts.start_in = now
            job.status = BBJobStatus.Inputing
        if not job_ins:
            self.dumpInputQ()

        job_runs = self.scheduleRun()
        for job in job_runs:
            job.ts.start_run = now
            job.status = BBJobStatus.Running
        if not job_runs:
            self.dumpRunQ()

        job_outs = self.scheduleStageOut()
        for job in job_outs:
            job.ts.start_out = now
            job.status = BBJobStatus.Outputing
        if not job_outs:
            self.dumpOutputQ()

        jobs = []
        jobs.extend(job_ins)
        jobs.extend(job_runs)
        jobs.extend(job_outs)
        for job in jobs:
            logging.debug('\t [%7.2d] Schedule %s' %
                          (now, str(job)))
        if not jobs:
            self.dumpResource()

        return jobs

    def dumpJobSummary(self):
        table = []
        first_row = ['id', 'submit', 'wait in', 'input',
                     'wait run', 'run', 'wait out',
                     'output', 'complete', 'wait',
                     'response']
        table.append(first_row)
        # self.complete_q.sort(key=lambda job: job.job_id)
        for job in self.complete_q:
            if job.status == BBJobStatus.Complete:
                statistic = job.dumpTimeStatisticBurstBuffer()
                table.append(statistic)
        logging.info('\n%s' % tabulate(table, headers="firstrow",
                                       tablefmt='fancy_grid'))

    def outputJobSummary(self, filename):
        writer = csv.writer(open(filename, 'w'))
        first_row = ['id', 'submit', 'wait in', 'input',
                     'wait run', 'run', 'wait out',
                     'output', 'complete', 'wait',
                     'response']
        writer.writerow(first_row)
        # self.complete_q.sort(key=lambda job: job.job_id)
        for job in self.complete_q:
            if job.status == BBJobStatus.Complete:
                statistic = job.dumpTimeStatisticBurstBuffer()
                writer.writerow(statistic)


class BBSchedulerMaxBurstBuffer(BBSchedulerViaBurstBuffer):
    """Maximize burst buffer's total usage with DP"""
    def __init__(self, system):
        super(BBSchedulerMaxBurstBuffer, self).__init__(system)
        self.solver = DPSolver()

    def scheduleStageIn(self):
        jobs = []
        if len(self.input_q) > 0:
            logging.debug('\t Solving on input queue, %.2f' %
                          self.system.bb.available)
            jobs = self.solver.maxStageInBurstBuffer(self.system.bb.available,
                                                     self.input_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_in
                self.input_q.remove(job)
        return jobs

    def scheduleRun(self):
        jobs = []
        if len(self.run_q) > 0:
            logging.debug('\t Solving on running queue')
            jobs = self.solver.maxRunningCpuBb(self.system.cpu.available,
                                               self.system.bb.available,
                                               self.run_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_run
                self.system.cpu.available -= job.demand.num_core
                self.run_q.remove(job)
        return jobs

    def scheduleStageOut(self):
        jobs = []
        if len(self.output_q) > 0:
            logging.debug('\t Solving on output queue')
            jobs = self.solver.maxStageOutBurstBuffer(self.system.bb.available,
                                                      self.output_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_out
                self.output_q.remove(job)
        return jobs


class BBSchedulerMaxParallel(BBSchedulerViaBurstBuffer):
    """Maximize number of tasks possible to run with DP"""
    def __init__(self, system):
        super(BBSchedulerMaxParallel, self).__init__(system)
        self.solver = DPSolver()

    def scheduleStageIn(self):
        jobs = []
        if len(self.input_q) > 0:
            logging.debug('\t Solving on input queue, %.2f' %
                          self.system.bb.available)
            jobs = self.solver.maxStageInParallelJobs(self.system.bb.available,
                                                      self.input_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_in
                self.input_q.remove(job)
        return jobs

    def scheduleRun(self):
        jobs = []
        if len(self.run_q) > 0:
            logging.debug('\t Solving on running queue')
            jobs = self.solver.maxRunningCpuBb(self.system.cpu.available,
                                               self.system.bb.available,
                                               self.run_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_run
                self.system.cpu.available -= job.demand.num_core
                self.run_q.remove(job)
        return jobs

    def scheduleStageOut(self):
        jobs = []
        if len(self.output_q) > 0:
            logging.debug('\t Solving on output queue')
            jobs = self.solver.maxStageOutParallelJobs(self.system.bb.available,
                                                       self.output_q)
            for job in jobs:
                self.system.bb.available -= job.demand.data_out
                self.output_q.remove(job)
        return jobs
