#!/usr/bin/env python

# import logging
import numpy as np
from random import randrange, seed
from job import BBJob, BBJobDemand


class BBTraceReader(object):
    """Read in swf trace file"""
    def __init__(self, filename, random_seed=None):
        super(BBTraceReader, self).__init__()
        self.input_filename = filename
        self.output_filename = filename + '.bb'

        seed(random_seed)

    def patchTraceFile(self, data_range):
        trace = np.loadtxt(self.input_filename, comments=';')
        output_file = open(self.output_filename, 'w')

        self.data_in_low = data_range[0][0]
        self.data_in_hi = data_range[0][1]
        self.data_in_step = data_range[0][2]

        self.data_run_low = data_range[1][0]
        self.data_run_hi = data_range[1][1]
        self.data_run_step = data_range[1][2]

        self.data_out_low = data_range[2][0]
        self.data_out_hi = data_range[2][1]
        self.data_out_step = data_range[2][2]

        for row in trace:
            data_in = randrange(self.data_in_low,
                                self.data_in_hi, self.data_in_step)
            data_run = randrange(self.data_run_low,
                                 self.data_run_hi, self.data_run_step)
            data_out = randrange(self.data_out_low,
                                 self.data_out_hi, self.data_out_step)
            for x in row:
                output_file.write("%.2f\t" % x)
            for x in [data_in, data_run, data_out]:
                output_file.write("%.2f\t" % x)
            output_file.write('\n')
        output_file.close()

    def generateJob(self, row):
        """convert one row of data to job object"""
        """
        0 Job number
        1 Submit time (in seconds)
        2 Wait time (in seconds)
        3 running time (in seconds)
        4 Number of allocated processors
        7 Requested number of processors
        8 Requested running time (in seconds)
        11 User ID
        14 Queue Number
        """
        job_id = row[0]
        submit = row[1]
        runtime = row[3]
        num_core = row[7]
        data_in = row[18]
        data_run = row[19]
        data_out = row[20]
        demand = BBJobDemand(num_core, data_in, data_run, data_out)
        job = BBJob(job_id, submit, demand, runtime)

        return job

    def generateJobs(self):
        """return all jobs in trace file"""
        jobs = []
        trace = np.loadtxt(self.output_filename, comments=';')
        for row in trace:
            job = self.generateJob(row)
            jobs.append(job)
        return jobs
