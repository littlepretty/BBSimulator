#!/usr/bin/env python

from enum import Enum
import logging


class BBEventType(Enum):
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


class BBSimulator(object):
    """Event driven simulator"""
    def __init__(self):
        super(BBSimulator, self).__init__()
        self.scheduler = None
        self.event_q = []
        self.virtual_time = float(0)

    def setScheduler(self, sched):
        """change scheduler"""
        self.scheduler = sched

    def simulate(self, jobs):
        """main simulation"""
        events = self.scheduler.generateEvents(jobs)
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
        """trigger scheduler when event happens"""
        self.virtual_time = events[0].timestamp
        now = self.virtual_time

        # handle events based on type
        for evt in events:
            logging.info(' Handle %s' % str(evt))
            if evt.evt_type == BBEventType.Submitted:
                self.scheduler.insertToInputQ(evt.job, now)
            elif evt.evt_type == BBEventType.FinishIn:
                self.scheduler.insertToRunQ(evt.job, now)
            elif evt.evt_type == BBEventType.FinishRun:
                self.scheduler.insertToOutputQ(evt.job, now)
            elif evt.evt_type == BBEventType.FinishOut:
                self.scheduler.insertToCompleteQ(evt.job, now)
            else:
                logging.warn(' Unable to handle event %s' % str(evt))
        jobs = self.scheduler.schedule(now)
        if jobs:
            new_events = self.scheduler.generateEvents(jobs)
            for evt in new_events:
                self.event_q.append(evt)

    def simulateCore(self):
        """keep popping events and handle them"""
        while len(self.event_q) > 0:
            evts = self.nextEvents()
            self.handleEvents(evts)
