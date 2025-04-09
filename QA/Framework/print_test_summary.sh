#!/bin/bash

# merge test subset result into one xml result
cd ./nrctest

# if you want cvs output with detailed report of how many rerun and result pass -csv
# similarly for the txt report, pass the -txt flag
python3 reporting.py -csv -txt