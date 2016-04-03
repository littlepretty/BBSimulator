#!/usr/bin/env python

from job import BBJobStatus
from enum import Enum
import logging
import csv


class BBEventType(Enum):
    """Possible event types"""
    Submitted = 1
    FinishIn = 2
    FinishRun = 3
    FinishOut = 4
    ReleaseIn = 5
    ReleaseRunCN = 6
    ReleaseOut = 7


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
        elif self.evt_type == BBEventType.ReleaseIn:
            return 'Release In'
        elif self.evt_type == BBEventType.ReleaseRun:
            return 'Release Run'
        elif self.evt_type == BBEventType.ReleaseOut:
            return 'Release Out'

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
    """generate events for 1 phase model"""
    def __init__(self, system):
        super(BBEventGeneratorDirect, self).__init__(system)

    def generateFinishOutput(self, job):
        """fill in all timestamps once output finishes"""
        return []

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


class BBEventGeneratorDirectIO(BBEventGeneratorDirect):
    """generate events with CPU and IO system resource"""
    def __init__(self, system):
        super(BBEventGeneratorDirectIO, self).__init__(system)

    def generateFinishOutput(self, job):
        """fill in all timestamps once output finishes"""
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


class BBEventGeneratorDirectBB(BBEventGeneratorDirect):
    """generate events with CPU and IO system resource"""
    def __init__(self, system):
        super(BBEventGeneratorDirectBB, self).__init__(system)

    def generateFinishOutput(self, job):
        """fill in all timestamps once output finishes"""
        input_dur = job.demand.data_in / self.system.io.to_bb
        output_dur = job.demand.data_out / self.system.bb.to_io
        run_dur = job.runtime + job.demand.data_run / self.system.cpu.to_bb
        run_dur += job.demand.data_in / self.system.bb.to_cpu
        run_dur += job.demand.data_out / self.system.cpu.to_bb
        job.ts.finish_in = job.ts.start_in + input_dur
        job.ts.start_run = job.ts.finish_in
        job.ts.finish_run = job.ts.start_run + run_dur
        job.ts.start_out = job.ts.finish_run
        job.ts.finish_out = job.ts.start_out + output_dur
        evt = BBEvent(job, job.ts.finish_out, BBEventType.FinishOut)
        return evt


class BBEventGeneratorCerberus(BBEventGeneratorBase):
    """generate events with CPU, burst buffer and IO system resource"""
    def __init__(self, system):
        super(BBEventGeneratorCerberus, self).__init__(system)

    def generateFinishInput(self, job):
        input_dur = job.demand.data_in / self.system.io.to_bb
        job.ts.finish_in = job.ts.start_in + input_dur
        evt = BBEvent(job, job.ts.finish_in, BBEventType.FinishIn)
        return evt

    def generateFinishRun(self, job):
        run_dur = job.runtime + job.demand.data_run / self.system.cpu.to_bb
        run_dur += job.demand.data_in / self.system.bb.to_cpu
        job.ts.finish_run = job.ts.start_run + run_dur
        evt = BBEvent(job, job.ts.finish_run, BBEventType.FinishRun)
        return evt

    def generateFinishOutput(self, job):
        output_dur = job.demand.data_out / self.system.cpu.to_bb
        job.ts.finish_out = job.ts.start_out + output_dur
        evt = BBEvent(job, job.ts.finish_out, BBEventType.FinishOut)
        return evt

    def generateReleaseInBB(self, job):
        input_dur = job.demand.data_in / self.system.bb.to_cpu
        job.ts.loaded = job.ts.start_run + input_dur
        evt = BBEvent(job, job.ts.loaded, BBEventType.ReleaseIn)
        return evt

    def generateReleaseRunBB(self, job):
        """release bb for data_run is done in FinishRun event"""
        pass

    def generateReleaseRunCN(self, job):
        output_dur = job.demand.data_out / self.system.cpu.to_bb
        ts = job.ts.start_out + output_dur
        evt = BBEvent(job, ts, BBEventType.ReleaseRunCN)
        return evt

    def generateReleaseRunOut(self, job):
        """release bb for data_out is done in FinishOut event"""
        pass

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
        self.cpu_usage = []
        self.virtual_time = float(0)
        self.time_series = []

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

    def gatherSystemStatistics(self, system):
        self.time_series.append(self.virtual_time)
        cpu_usage = 1 - system.cpu.available / system.cpu.capacity
        self.cpu_usage.append(cpu_usage)

    def dumpSystemStatistics(self, filename):
        writer = csv.writer(open(filename, 'w'))
        first_row = ['time', 'cpu']
        writer.writerow(first_row)
        for t, x in zip(self.time_series, self.cpu_usage):
            row = [t, x]
            writer.writerow(row)

    def simulateCore(self):
        """keep popping events and handle them"""
        while len(self.event_q) > 0:
            evts = self.nextEvents()
            self.handleEvents(evts)
            self.gatherSystemStatistics(self.scheduler.system)
        self.dumpEventQueue()


class BBSimulatorDirect(BBSimulatorBase):
    """only 1 phase"""
    def __init__(self, system):
        super(BBSimulatorDirect, self).__init__()
        self.has_bb = False
        self.bb_usage = []

    def setEventGenerator(self, device, system):
        if device == 'IO':
            self.generator = BBEventGeneratorDirectIO(system)
        elif device == 'BB':
            self.generator = BBEventGeneratorDirectBB(system)
            self.has_bb = True

    def gatherSystemStatistics(self, system):
        self.time_series.append(self.virtual_time)
        cpu_usage = 1 - system.cpu.available / system.cpu.capacity
        self.cpu_usage.append(cpu_usage)
        if self.has_bb:
            bb_usage = 1 - system.bb.available / system.bb.capacity
            self.bb_usage.append(bb_usage)

    def dumpSystemStatistics(self, filename):
        writer = csv.writer(open(filename, 'w'))
        if self.has_bb:
            first_row = ['time', 'cpu', 'bb']
            writer.writerow(first_row)
            for t, x, y in zip(self.time_series, self.cpu_usage, self.bb_usage):
                row = [t, x, y]
                writer.writerow(row)
        else:
            first_row = ['time', 'cpu']
            writer.writerow(first_row)
            for t, x in zip(self.time_series, self.cpu_usage):
                row = [t, x]
                writer.writerow(row)

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


class BBSimulatorCerberus(BBSimulatorBase):
    """consider burst buffer, e.g. 3 phase scheduling"""
    def __init__(self, system):
        super(BBSimulatorCerberus, self).__init__()
        self.generator = BBEventGeneratorCerberus(system)
        self.bb_usage = []

    def gatherSystemStatistics(self, system):
        self.time_series.append(self.virtual_time)
        cpu_usage = 1 - system.cpu.available / system.cpu.capacity
        self.cpu_usage.append(cpu_usage)
        bb_usage = 1 - system.bb.available / system.bb.capacity
        self.bb_usage.append(bb_usage)

    def dumpSystemStatistics(self, filename):
        writer = csv.writer(open(filename, 'w'))
        first_row = ['time', 'cpu', 'bb']
        writer.writerow(first_row)
        for t, x, y in zip(self.time_series, self.cpu_usage, self.bb_usage):
            row = [t, x, y]
            writer.writerow(row)

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
