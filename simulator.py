#!/usr/bin/python

from scheduler import BBScheduler
from job import BBJob

class BBEvent(object):
    """
    Simulation event
    """
    def __init__(self, job, ts):
        super(BBEvent, self).__init__()
        self.job = job
        self.timestamp = ts


class BBSimulator(object):
    """
    Event driven simulator
    """
    def __init__(self):
        super(BBSimulator, self).__init__()
        self.scheduler = None
        self.event_q = []
        self.jobs = []
        self.virtual_time = 0

    def initializeJobs(self):
        pass

    def simulate(self):
        self.initializeJobs()

    
    def nextEvent(self):
        return self.event_q.pop(0)

    def handleEvent(self, evt):
        

    def simulate_core(self):
        while len(self.event_q) > 0:
            evt = self.nextEvent()
            self.handleEvent(evt)


