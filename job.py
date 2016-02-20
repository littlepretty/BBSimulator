#!/usr/bin/python

from enum import Enum

class BBJobTimeStamp(object):
    """
    Timing statistics
    """
    def __init__(self, submit):
        super(BBTimeStamp, self).__init__()
        self.submit = submit # when job goes into input queue
        self.start_in = 0
        self.finish_in = 0 # when job goes into run queue  
        self.start_run = 0
        self.finish_run = 0 # when job goes into out queue 
        self.start_out = 0
        self.finish_out = 0

        self.response = self.finish_out - self.submitted


class BBJobDemand(object):
    """
    Demand statistics
    """
    def __init__(self, num_core, bb_in, bb, data_in, data_out):
        super(BBDemand, self).__init__()
        self.num_core = num_core
        self.bb_in = bb_in
        self.bb = bb
        # additional trace data
        self.data_in = data_in
        self.data_out = data_out

class BBJobStatus(Enum):
    WaitInput = 1
    Inputing = 2
    WaitRun = 3
    Running = 4
    WaitOut = 5
    Outputing = 6

class BBJob(object):
    """
    Jobs with burst buffer demand
    """
    def __init__(self, job_id, ts, demand):
        super(BBJob, self).__init__()
        self.job_id = job_id
        self.ts = ts
        self.demand = demand
        self.status = BBJobStatus.WaitInput



