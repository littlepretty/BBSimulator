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
        self.running_q = []
        self.out_q = []

    def scheduleStageIn(self):
        pass

    def scheduleRunning(self):
        pass

    def scheduleStageOut(self):
        pass

    def scheduleCore(self):
        events = []
        events.append(self.scheduleStageIn())
        events.append(self.scheduleRunning())
        events.append(self.scheduleStageOut())
        return events


