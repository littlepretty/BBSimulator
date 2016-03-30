#!/bin/zsh


cd IOvsBBFigures
cp ../../FifoVsDp/1000jobs.swf.bb .
cp ../../FifoVsDp/1000jobs_1pio* .
cp ../../FifoVsDp/1000jobs_plain* .
./direct_vs_bb.py
cd ../

cd 3Pvs1PFigures
cp ../../FifoVsDp/1000jobs.swf.bb .
cp ../../FifoVsDp/1000jobs_1pbb* .
cp ../../FifoVsDp/1000jobs_3p_same* .
cp ../../FifoVsDp/1000jobs_plain* .
./3p_vs_1p.py
cd ../

cd DPvsFIFOFigures
cp ../../FifoVsDp/1000jobs.swf.bb .
cp ../../FifoVsDp/1000jobs_1pio* .
cp ../../FifoVsDp/1000jobs_1pbb* .
cp ../../FifoVsDp/1000jobs_3p_same* .
cp ../../FifoVsDp/1000jobs_plain* .
cp ../../FifoVsDp/1000jobs_maxbb* .
cp ../../FifoVsDp/1000jobs_maxparallel* .
./dp_vs_fifo.py
cd ../

