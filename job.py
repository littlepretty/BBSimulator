#!/usr/bin/python

class BBTimeStamp(object):
    """
    Timing statistics
    """
    def __init__(self, submit):
        super(BBTimeStamp, self).__init__()
        self.submit = submit
        # update when job goes into input queue
        self.waiting_in = 0
        # update when job goes into running queue
        self.waiting_run = 0
        # update when job goes into out queue
        self.waiting_out = 0
        # wait = in + run + out
        self.wating = 0
        # transfer_in = data_in / bw
        self.transfer_in = 0
        self.running = 0
        self.transfer_out = 0
        # finish = submit + wait + transfer in/out + running
        self.finish = 0
        # response = finish - submit 
        self.response = 0

class BBDemand(object):
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

status_str = ['SUBMITTED', 'STAGE_IN', 'STAGE_OUT', 'RUNNING', 'FINISHED']

class BBJob(object):
    """
    Jobs with burst buffer demand
    """
    def __init__(self, job_id, timestamp, demand):
        super(BBJob, self).__init__()
        self.job_id = job_id
        self.timestamp = timestamp
        self.demand = demand
        self.status = 'SUBMITTED'



