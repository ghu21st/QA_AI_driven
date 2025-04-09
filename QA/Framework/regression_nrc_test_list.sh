#!/bin/bash
############# NRC regression test script ###############
# Note: make sure ./nrctest/log folder and ./nrctest/log_bak folder exit before run this script

# copy old log
cp -r ./nrctest/log/* ./nrctest/log_bak
rm -fr ./nrctest/log/*

# run NRC regression test
./nrctest.sh -x RegressionTest/gRPCTest/ -v >/dev/null
echo '---- regression test done --- '
echo 

# merge test subset result into one xml result
sh merge_nrc_regression_results.sh
echo
