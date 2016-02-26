#!/usr/bin/env python

# import logging
import numpy as np
from job import BBJob, BBJobDemand


class BBTraceReader(object):
    """Read in swf trace file"""
    def __init__(self, filename):
        super(BBTraceReader, self).__init__()
        self.trace = np.loadtxt(filename, comments=';')

    def generateJob(self, row):
        """convert one row of data to job object"""
        job_id = row[0]
        submit = row[1]
        runtime = row[3]

        num_core = row[4]
        data_in = row[18]
        data_run = row[19]
        data_out = row[20]
        demand = BBJobDemand(num_core, data_in, data_run, data_out)

        job = BBJob(job_id, submit, demand, runtime)
        return job

    def generateJobs(self):
        """return all jobs in trace file"""
        jobs = []
        for row in self.trace:
            jobs.append(self.generateJob(row))
        return jobs
