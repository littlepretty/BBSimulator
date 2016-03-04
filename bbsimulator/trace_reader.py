#!/usr/bin/env python

# import logging
import numpy as np
from random import randrange, seed
from job import BBJob, BBJobDemand


class BBTraceReader(object):
    """Read in swf trace file"""
    def __init__(self, filename, lam, random_seed=None):
        super(BBTraceReader, self).__init__()
        self.input_filename = filename
        self.output_filename = filename + '.bb'
        self.lam = lam
        seed(random_seed)

    def patchTraceFileOnePhase(self, data, mod_submit=False):
        trace = np.loadtxt(self.input_filename, comments=';')
        output_file = open(self.output_filename, 'w')

        size = len(trace)

        if mod_submit:
            poisson = np.random.poisson(self.lam, size)
            submissions = np.cumsum(poisson)

        i = 0
        d = 0
        for row in trace:
            if mod_submit:
                row[1] = submissions[i]
                i += 1
            for x in row:
                output_file.write("%.2f\t" % x)
            output_file.write('%.2f\t' % data[d])
            output_file.write('%.2f\t' % data[d])
            output_file.write('%.2f\t' % data[d])
            d += 1
            output_file.write('\n')
        output_file.close()

    def patchTraceFileThreePhases(self, data_range, mod_submit=False):
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
        size = len(trace)
        max_random_data = []
        if mod_submit:
            poisson = np.random.poisson(self.lam, size)
            submissions = np.cumsum(poisson)

        i = 0
        for row in trace:
            data_in = randrange(self.data_in_low,
                                self.data_in_hi, self.data_in_step)
            data_run = randrange(self.data_run_low,
                                 self.data_run_hi, self.data_run_step)
            data_out = randrange(self.data_out_low,
                                 self.data_out_hi, self.data_out_step)
            data_max = max(data_in, data_run, data_out)

            max_random_data.append(data_max)

            if mod_submit:
                row[1] = submissions[i]
                i += 1
            for x in row:
                output_file.write("%.2f\t" % x)
            output_file.write('%.2f\t' % data_in)
            output_file.write('%.2f\t' % data_run)
            output_file.write('%.2f\t' % data_out)
            output_file.write('\n')
        output_file.close()
        return max_random_data

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
