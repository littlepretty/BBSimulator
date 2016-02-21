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


class BBScheduler(object):
    """3 phase scheduler"""
    def __init__(self, cpu, bb, io):
        super(BBScheduler, self).__init__()
        self.cpu = cpu
        self.bb = bb
        self.io = io
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
        logging.debug('\t ' + str(self.cpu))
        logging.debug('\t ' + str(self.bb))
        logging.debug('\t ' + str(self.io))

    def insertToInputQ(self, job, now):
        job.status = BBJobStatus.WaitInput
        self.input_q.append(job)

    def insertToRunQ(self, job, now):
        job.status = BBJobStatus.WaitRun
        self.bb.available += job.demand.bb_in
        self.run_q.append(job)

    def insertToOutputQ(self, job, now):
        job.status = BBJobStatus.WaitOutput
        self.cpu.available += job.demand.num_core
        self.output_q.append(job)

    def insertToCompleteQ(self, job, now):
        job.status = BBJobStatus.Complete
        self.bb.available += job.demand.bb
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
        "return jobs with status inputing"
        jobs = []
        # sort descendingly, max data throughput
        # sort ascendingly, max parallelism
        self.input_q.sort(key=lambda job: job.demand.bb_in)
        while len(self.input_q) > 0 and \
                self.bb.available >= self.input_q[0].demand.bb_in:
            job = self.input_q.pop(0)
            self.bb.available -= job.demand.bb_in
            jobs.append(job)
        return jobs

    def scheduleRun(self):
        "return jobs with status running"
        jobs = []
        self.run_q.sort(key=lambda job: job.demand.num_core)
        while len(self.run_q) > 0 and \
                self.cpu.available >= self.run_q[0].demand.num_core:
            job = self.run_q.pop(0)
            self.cpu.available -= job.demand.num_core
            jobs.append(job)
        return jobs

    def scheduleStageOut(self):
        "return jobs with status outputing"
        jobs = []
        self.output_q.sort(key=lambda job: job.demand.bb)
        while len(self.output_q) > 0 and \
                self.bb.available >= self.output_q[0].demand.bb:
            job = self.output_q.pop(0)
            self.bb.available -= job.demand.bb
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

    def generateSubmittedEvents(self, job):
        evt = BBEvent(job, job.ts.submit, BBEventType.Submitted)
        return evt

    def generateFinishInput(self, job):
        input_dur = job.demand.data_in / self.io.to_bb
        job.ts.finish_in = job.ts.start_in + input_dur
        evt = BBEvent(job, job.ts.finish_in, BBEventType.FinishIn)
        return evt

    def generateFinishRun(self, job):
        job.ts.finish_run = job.ts.start_run + job.runtime
        evt = BBEvent(job, job.ts.finish_run, BBEventType.FinishRun)
        return evt

    def generateFinishOutput(self, job):
        output_dur = job.demand.data_out / self.bb.to_io
        job.ts.finish_out = job.ts.start_out + output_dur
        evt = BBEvent(job, job.ts.finish_out, BBEventType.FinishOut)
        return evt

    def generateEvents(self, jobs):
        """generate new events based on schedule results"""
        events = []
        for job in jobs:
            if job.status == BBJobStatus.WaitInput:
                evt = self.generateSubmittedEvents(job)
                events.append(evt)
            elif job.status == BBJobStatus.Inputing:
                evt = self.generateFinishInput(job)
                events.append(evt)
            elif job.status == BBJobStatus.Running:
                evt = self.generateFinishRun(job)
                events.append(evt)
            elif job.status == BBJobStatus.Outputing:
                evt = self.generateFinishOutput(job)
                events.append(evt)
            else:
                logging.warn('\t Unable to generate events for job')

        for evt in events:
            logging.debug('\t Generate %s' % str(evt))
        return events
