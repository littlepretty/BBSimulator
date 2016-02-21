#!/usr/bin/env python

from enum import Enum
import logging


class BBJobTimeStamp(object):
    """timing statistics"""
    def __init__(self, submit):
        super(BBJobTimeStamp, self).__init__()
        self.submit = float(submit)  # when job goes into input queue
        self.start_in = 0.0
        self.finish_in = 0.0  # when job goes into run queue
        self.start_run = 0.0
        self.finish_run = 0.0  # when job goes into out queue
        self.start_out = 0.0
        self.finish_out = 0.0


class BBJobDemand(object):
    """demand statistics"""
    def __init__(self, num_core, bb_in, bb, data_out):
        super(BBJobDemand, self).__init__()
        self.num_core = float(num_core)
        self.bb_in = float(bb_in)
        self.bb = float(bb)
        # additional trace data
        self.data_in = float(bb_in)
        self.data_out = float(data_out)

    def __str__(self):
        return "dv = [%d cores, %.2f in_buffer, %.2f buffer, %.2f out_data]" % \
            (self.num_core, self.bb_in, self.bb, self.data_out)


class BBJobStatus(Enum):
    """job status"""
    WaitInput = 1
    Inputing = 2
    WaitRun = 3
    Running = 4
    WaitOutput = 5
    Outputing = 6
    Complete = 7


class BBJob(object):
    """jobs with burst buffer demand"""
    def __init__(self, job_id, submit, demand, rt):
        super(BBJob, self).__init__()
        self.job_id = job_id
        ts = BBJobTimeStamp(submit)
        self.ts = ts
        self.demand = demand
        self.runtime = float(rt)
        self.status = BBJobStatus.WaitInput

    def jobStatus(self):
        if self.status == BBJobStatus.WaitInput:
            return 'Wait Input'
        elif self.status == BBJobStatus.Inputing:
            return 'Inputing'
        elif self.status == BBJobStatus.WaitRun:
            return 'Wait Run'
        elif self.status == BBJobStatus.Running:
            return 'Running'
        elif self.status == BBJobStatus.WaitOutput:
            return 'Wait Out'
        elif self.status == BBJobStatus.Outputing:
            return 'Outputing'
        else:
            return 'Complete'

    def __str__(self):
        return 'job_%d, %s [%s]' % (self.job_id,
                                     self.demand, self.jobStatus())

    def dumpTimeStatistic(self):
        if self.status == BBJobStatus.Complete:
            submit = self.ts.submit
            waiting_in = self.ts.start_in - self.ts.submit
            waiting_run = self.ts.start_run - self.ts.finish_in
            waiting_out = self.ts.start_out - self.ts.finish_run
            inputing = self.ts.finish_in - self.ts.start_in
            running = self.ts.finish_run - self.ts.start_run
            outputing = self.ts.finish_out - self.ts.start_out
            complete = self.ts.finish_out
            total_wait = waiting_in + waiting_run + waiting_out
            response = complete - submit
            return [self.job_id, submit, waiting_in, inputing,
                    waiting_run, running, waiting_out, outputing,
                    complete, total_wait, response]
