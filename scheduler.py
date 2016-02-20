#!/usr/bin/python

class BBResource(object):
    """
    Abstract class for all resources
    """
    def __init__(self, capacity):
        super(BBResource, self).__init__()
        self.capacity = capacity
        self.available = capacity

class BBCpu(BBResource):
    """
    CPU
    """
    def __init__(self, capacity, to_bb, to_io):
        super(BBCpu, self, capacity).__init__()
        self.to_bb = to_bb
        self.to_io = to_io

class BBBurstBuffer(BBResource):
    """
    Burst Buffer
    """
    def __init__(self, capacity, to_cpu, to_io):
        super(BBBurstBuffer, self, capacity).__init__()
        self.to_cpu = to_cpu
        self.to_io = to_io

class BBIo(BBResource):
    """
    IO nodes
    """
    def __init__(self, to_cpu, to_bb):
        super(BBIo, self, 1000000).__init__()
        self.to_cpu = to_cpu
        self.to_bb = to_bb

class BBScheduler(object):
    """
    3 phase scheduler
    """
    def __init__(self, cpu, bb, io):
        super(BBScheduler, self).__init__()
        self.cpu = cpu
        self.bb = bb
        self.io = io
        self.input_q = []
        self.run_q = []
        self.out_q = []

    def insertToInputQ(self, job, now):
        job.status = WaitInput
        self.input_q.append(job)

    def insertToRunQ(self, job, now):
        job.status = WaitRun
        self.run_q.append(job)

    def insertToOutputQ(self, job, now):
        job.status = WaitOutput
        self.out_q.append(job)

    def scheduleStageIn(self):
        "return jobs with status inputing"
        pass

    def scheduleRun(self):
        "return jobs with status running"
        pass

    def scheduleStageOut(self):
        "return jobs with status outputing"
        pass
 
    def scheduleCore(self, now):
        "return scheduled jobs with proper status"
        job_ins = self.scheduleStageIn()
        for job in job_ins:
            job.ts.start_in = now
            job.status = Inputing
        
        job_runs = self.scheduleRun()
        for job in job_runs:
            job.ts.start_run = now
            job.status = Running

        job_outs = self.scheduleStageOut()
        for job in job_outs:
            job.ts.start_out = now
            job.status = Outputing

        jobs = []
        jobs.append(job_ins)
        jobs.append(job_runs)
        jobs.append(job_outs)
        return jobs


