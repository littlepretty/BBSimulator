#!/usr/bin/env python

from job import BBJobStatus
from enum import Enum
import logging


class BBEventType(Enum):
    """Possible event types"""
    Submitted = 1
    FinishIn = 2
    FinishRun = 3
    FinishOut = 4


class BBEvent(object):
    """Simulation event"""
    def __init__(self, job, ts, evt_type):
        super(BBEvent, self).__init__()
        self.job = job
        self.timestamp = float(ts)
        self.evt_type = evt_type

    def eventType(self):
        if self.evt_type == BBEventType.Submitted:
            return 'Submitted'
        elif self.evt_type == BBEventType.FinishIn:
            return 'Finish In'
        elif self.evt_type == BBEventType.FinishRun:
            return 'Finish Run'
        elif self.evt_type == BBEventType.FinishOut:
            return 'Finish Out'

    def __str__(self):
        return "%s event[%7.2f] with %s" % \
            (self.eventType(), self.timestamp, str(self.job))


class BBEventGeneratorBase(object):
    """generate events with system resource"""
    def __init__(self, system):
        super(BBEventGeneratorBase, self).__init__()
        self.system = system

    def generateSubmittedEvents(self, job):
        evt = BBEvent(job, job.ts.submit, BBEventType.Submitted)
        return evt

    def generateFinishOutput(self, job):
        return []

    def generateEvents(self, jobs):
        """generate new events based on schedule results"""
        return []


class BBEventGeneratorDirect(BBEventGeneratorBase):
    """generate events with CPU and IO system resource"""
    def __init__(self, system):
        super(BBEventGeneratorDirect, self).__init__(system)

    def generateFinishOutput(self, job):
        input_dur = job.demand.data_in / self.system.io.to_cpu
        output_dur = job.demand.data_out / self.system.cpu.to_io
        run_dur = job.runtime + job.demand.data_run / self.system.cpu.to_io
        job.ts.finish_in = job.ts.start_in + input_dur
        job.ts.start_run = job.ts.finish_in
        job.ts.finish_run = job.ts.start_run + run_dur
        job.ts.start_out = job.ts.finish_run
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
            elif job.status == BBJobStatus.Outputing:
                evt = self.generateFinishOutput(job)
                events.append(evt)
            else:
                logging.warn('\t Unable to generate events for %s' % str(job))

        for evt in events:
            logging.debug('\t Generate %s' % str(evt))
        return events


class BBEventGeneratorBurstBuffer(BBEventGeneratorBase):
    """generate events with CPU, burst buffer and IO system resource"""
    def __init__(self, system):
        super(BBEventGeneratorBurstBuffer, self).__init__(system)

    def generateFinishRun(self, job):
        job.ts.finish_run = job.ts.start_run + job.runtime
        evt = BBEvent(job, job.ts.finish_run, BBEventType.FinishRun)
        return evt

    def generateFinishInput(self, job):
        input_dur = job.demand.data_in / self.system.io.to_bb
        input_dur += job.demand.data_in / self.system.bb.to_cpu
        job.ts.finish_in = job.ts.start_in + input_dur
        evt = BBEvent(job, job.ts.finish_in, BBEventType.FinishIn)
        return evt

    def generateFinishOutput(self, job):
        output_dur = job.demand.data_out / self.system.bb.to_io
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
                logging.warn('\t Unable to generate events for %s' % str(job))

        for evt in events:
            logging.debug('\t Generate %s' % str(evt))
        return events


class BBSimulatorBase(object):
    """event driven simulator"""
    def __init__(self):
        super(BBSimulatorBase, self).__init__()
        self.scheduler = None
        self.generator = None
        self.event_q = []
        self.virtual_time = float(0)

    def setScheduler(self, sched):
        """change scheduler"""
        self.scheduler = sched

    def setGenerator(self, gen):
        self.generator = gen

    def simulate(self, jobs):
        """main simulation"""
        events = self.generator.generateEvents(jobs)
        for evt in events:
            self.event_q.append(evt)
        self.simulateCore()

    def nextEvents(self):
        """choose earliest timestampped events"""
        # sort based on timestamp
        self.event_q.sort(key=lambda evt: evt.timestamp)

        # there may be events with same timestamp
        events = []
        earliest_ts = self.event_q[0].timestamp
        while len(self.event_q) > 0:
            if self.event_q[0].timestamp == earliest_ts:
                evt = self.event_q.pop(0)
                events.append(evt)
            else:
                break
        return events

    def handleEvents(self, events):
        """override me to handle events"""
        pass

    def dumpEventQueue(self):
        logging.debug('\t Dump event queue')
        for evt in self.event_q:
            logging.debug('\t ' + str(evt))

    def simulateCore(self):
        """keep popping events and handle them"""
        while len(self.event_q) > 0:
            evts = self.nextEvents()
            self.handleEvents(evts)
        self.dumpEventQueue()
        self.scheduler.dumpJobSummary()


class BBSimulatorDirect(BBSimulatorBase):
    """only simulator cpu and IO"""
    def __init__(self):
        super(BBSimulatorDirect, self).__init__()

    def handleEvents(self, events):
        self.virtual_time = events[0].timestamp
        now = self.virtual_time
        for evt in events:
            logging.debug('\t Handle %s' % str(evt))
            if evt.evt_type == BBEventType.Submitted:
                self.scheduler.insertToDirectQ(evt.job)
            elif evt.evt_type == BBEventType.FinishOut:
                self.scheduler.insertToCompleteQ(evt.job)
            else:
                logging.warn('\t Unable to handle event %s' % str(evt))
        jobs = self.scheduler.schedule(now)
        if jobs:
            new_events = self.generator.generateEvents(jobs)
            for evt in new_events:
                self.event_q.append(evt)


class BBSimulatorBurstBuffer(BBSimulatorBase):
    """consider burst buffer, e.g. 3 phase scheduling"""
    def __init__(self):
        super(BBSimulatorBurstBuffer, self).__init__()

    def handleEvents(self, events):
        """trigger scheduler when event happens"""
        self.virtual_time = events[0].timestamp
        now = self.virtual_time

        # handle events based on type
        for evt in events:
            logging.debug('\t Handle %s' % str(evt))
            if evt.evt_type == BBEventType.Submitted:
                self.scheduler.insertToInputQ(evt.job)
            elif evt.evt_type == BBEventType.FinishIn:
                self.scheduler.insertToRunQ(evt.job)
            elif evt.evt_type == BBEventType.FinishRun:
                self.scheduler.insertToOutputQ(evt.job)
            elif evt.evt_type == BBEventType.FinishOut:
                self.scheduler.insertToCompleteQ(evt.job)
            else:
                logging.warn('\t Unable to handle event %s' % str(evt))
        jobs = self.scheduler.schedule(now)
        if jobs:
            new_events = self.generator.generateEvents(jobs)
            for evt in new_events:
                self.event_q.append(evt)
