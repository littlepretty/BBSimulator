#!/usr/bin/python

from scheduler import BBScheduler
from job import BBJob
from enum import Enum


class BBEventType(Enum):
    Submitted = 1
    FinishInput = 2
    FinishRun = 3
    FinishOut = 4

class BBEvent(object):
    """
    Simulation event
    """
    def __init__(self, job, ts, evt_type):
        super(BBEvent, self).__init__()
        self.job = job
        self.timestamp = ts
        self.evt_type = evt_type

class BBSimulator(object):
    """
    Event driven simulator
    """
    def __init__(self):
        super(BBSimulator, self).__init__()
        self.scheduler = None
        self.event_q = []
        self.virtual_time = 0

    def setScheduler(self, sched):
        self.scheduler = sched

    def simulate(self):
        self.generateSubmittedEvents()
        self.simulateCore()

    def nextEvents(self):
        # sort based on timestamp
        sorted(self.event_q, key=lambda evt: evt.timestamp)
        
        # there may be events with same timestamp
        events = []
        earliest_ts = self.event_q[0].ts
        while len(self.event_q) > 0:
            if self.event_q[0].ts == earliest_ts:
                evt = self.event_q.pop(0)
                events.append(evt)
            elif self.event_q[0].ts > earliest_ts:
                break
        return events

    def handleEvents(self, events):
        self.virtual_time = events[0].timestamp
        now = self.virtual_time
        
        # handle events based on type
        for evt in events:
            if evt.evt_type == Submitted:
                self.scheduler.insertToInputQ(evt.job, now)
            elif evt.evt_type == FinishInput:
                self.scheduler.insertToRunQ(evt.job, now)
            elif evt.evt_type == FinishRun:
                self.scheduler.insertToOutputQ(evt.job, now)
            elif evt.evt_type == FinishOut:
                self.dumpFinishedJob(evt.job)
            else:
                print 'Unable to handle event', evt
        jobs = self.scheduler.schedule(now)

        # generate new events based on schedule results
        for job in jobs:
            if job.status == Inputing:
                evt = self.generateFinishInput(job)
                self.event_q.append(evt)
            elif job.status == Running:
                evt = self.generateFinishRun(job)
                self.event_q.append(evt)
            elif job.status == Outputing:
                evt = self.generateFinishOutput(job)
                self.event_q.append(evt)

    def dumpFinishedJob(self, job):
        pass

    def simulateCore(self):
        while len(self.event_q) > 0:
            evts = self.nextEvents()
            self.handleEvents(evts)


