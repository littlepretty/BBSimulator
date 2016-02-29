#!/usr/bin/env python

# import logging
import numpy as np
from random import randrange, seed
from job import BBJob, BBJobDemand


class BBTraceReader(object):
    """Read in swf trace file"""
    def __init__(self, filename, random_seed=None):
        super(BBTraceReader, self).__init__()
        self.trace = np.loadtxt(filename, comments=';')
        self.output = open(filename + '.bb', 'w')
        seed(random_seed)

    def generateJob(self, row):
        """convert one row of data to job object"""
        job_id = row[0]
        submit = row[1]
        runtime = row[3]
        num_core = row[4]

        data_in = randrange(self.data_in_low,
                            self.data_in_hi, self.data_in_step)
        data_run = randrange(self.data_run_low,
                             self.data_run_hi, self.data_run_step)
        data_out = randrange(self.data_out_low,
                             self.data_out_hi, self.data_out_step)

        demand = BBJobDemand(num_core, data_in, data_run, data_out)
        job = BBJob(job_id, submit, demand, runtime)

        new_row = row + [data_in, data_run, data_out]
        for x in new_row:
            self.output.write(".2f\t" % x)
        self.output.write('\n')
        return job

    def generateJobs(self, data_range):
        """return all jobs in trace file"""
        jobs = []
        self.data_in_low = data_range[0][0]
        self.data_in_hi = data_range[0][1]
        self.data_in_step = data_range[0][2]

        self.data_run_low = data_range[1][0]
        self.data_run_hi = data_range[1][1]
        self.data_run_step = data_range[1][2]

        self.data_out_low = data_range[2][0]
        self.data_out_hi = data_range[2][1]
        self.data_out_step = data_range[2][2]

        for row in self.trace:
            jobs.append(self.generateJob(row))
        self.output.close()
        return jobs
