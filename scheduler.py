#!/usr/bin/env python

import logging
from job import BBJobStatus
from simulator import BBEvent, BBEventType
from tabulate import tabulate


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
        self.input_q = []
        self.run_q = []
        self.output_q = []
        self.complete_q = []

    def dumpQueue(self, queue):
        for job in queue:
            logging.debug('\t ' + str(job))

    def dumpInputQ(self):
        logging.debug('\t Dump input queue')
        self.dumpQueue(self.input_q)

    def dumpRunQ(self):
        logging.debug('\t Dump run queue')
        self.dumpQueue(self.run_q)

    def dumpOutputQ(self):
        logging.debug('\t Dump output queue')
        self.dumpQueue(self.output_q)

    def dumpResource(self):
        logging.debug('\t Dump resources')
        logging.debug('\t ' + str(self.system))

    def insertToInputQ(self, job, now):
        job.status = BBJobStatus.WaitInput
        self.input_q.append(job)

    def insertToRunQ(self, job, now):
        job.status = BBJobStatus.WaitRun
        self.run_q.append(job)

    def insertToOutputQ(self, job, now):
        job.status = BBJobStatus.WaitOutput
        self.system.cpu.available += job.demand.num_core
        self.output_q.append(job)

    def insertToCompleteQ(self, job, now):
        job.status = BBJobStatus.Complete
        self.complete_q.append(job)

    def dumpJobSummary(self):
        table = []
        first_row = ['id', 'submit', 'wait in', 'input',
                     'wait run', 'run', 'wait out',
                     'output', 'complete', 'wait',
                     'response']
        table.append(first_row)
        self.complete_q.sort(key=lambda job: job.job_id)
        for job in self.complete_q:
            if job.status == BBJobStatus.Complete:
                statistic = job.dumpTimeStatistic()
                table.append(statistic)
        logging.info('\n%s' % tabulate(table, headers="firstrow",
                                       tablefmt='fancy_grid'))

    def scheduleStageIn(self):
        """return all jobs in input queue"""
        jobs = []
        while len(self.input_q) > 0:
            job = self.input_q.pop(0)
            jobs.append(job)
        return jobs

    def scheduleRun(self):
        """FIFO as long as there are cpu available"""
        jobs = []
        while len(self.run_q) > 0 and \
                self.system.cpu.available > self.run_q[0].demand.num_core:
            job = self.run_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            jobs.append(job)
        return jobs

    def scheduleStageOut(self):
        """return all jobs in output queue"""
        jobs = []
        while len(self.output_q) > 0:
            job = self.output_q.pop(0)
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

    def schedule(self, now):
        return self.scheduleCore(now)


class BBSchedulerDirectIO(BBSchedulerBase):
    def __init__(self, system):
        super(BBSchedulerDirectIO, self).__init__(system)

    def scheduleRun(self):
        "return jobs with status running"
        jobs = []
        # sort descendingly, max cpu utilization
        # sort ascendingly, max parallelism
        self.run_q.sort(key=lambda job: job.demand.num_core)
        while len(self.run_q) > 0 and \
                self.system.cpu.available >= self.run_q[0].demand.num_core:
            job = self.run_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            jobs.append(job)
        return jobs


class BBSchedulerViaBurstBuffer(BBSchedulerBase):
    def __init__(self, system):
        super(BBSchedulerViaBurstBuffer, self).__init__(system)

    def insertToRunQ(self, job, now):
        job.status = BBJobStatus.WaitRun
        self.system.bb.available += job.demand.bb_in
        self.run_q.append(job)

    def insertToCompleteQ(self, job, now):
        job.status = BBJobStatus.Complete
        self.system.bb.available += job.demand.bb
        self.complete_q.append(job)

    def scheduleStageIn(self):
        "return jobs s.t. max|jobs| with bb constraint"
        jobs = []
        # sort descendingly, max data throughput
        # sort ascendingly, max parallelism
        self.input_q.sort(key=lambda job: job.demand.bb_in)
        while len(self.input_q) > 0 and \
                self.system.bb.available >= self.input_q[0].demand.bb_in:
            job = self.input_q.pop(0)
            self.system.bb.available -= job.demand.bb_in
            jobs.append(job)
        return jobs

    def scheduleRun(self):
        "return jobs s.t. max|jobs| with cpu and bb constraint"
        jobs = []
        self.run_q.sort(key=lambda job: job.demand.num_core)
        while len(self.run_q) > 0 and \
                self.system.cpu.available >= self.run_q[0].demand.num_core:
            job = self.run_q.pop(0)
            self.system.cpu.available -= job.demand.num_core
            jobs.append(job)
        return jobs

    def scheduleStageOut(self):
        "return jobs s.t. max|jobs| with bb constraint"
        jobs = []
        self.output_q.sort(key=lambda job: job.demand.bb)
        while len(self.output_q) > 0 and \
                self.system.bb.available >= self.output_q[0].demand.bb:
            job = self.output_q.pop(0)
            self.system.bb.available -= job.demand.bb
            jobs.append(job)
        return jobs


class BBSchedulerDynamicProgramming(BBSchedulerViaBurstBuffer):
    def __init__(self, system, solver):
        super(BBSchedulerDynamicProgramming, self).__init__(system)
        self.solver = solver

    def scheduleStageIn(self):
        pass

    def scheduleRun(self):
        pass

    def scheduleStageOut(self):
        pass
