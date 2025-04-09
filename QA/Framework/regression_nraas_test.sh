#!/bin/bash
############# NRaaS regression test script ###############
# Note: make sure ./nrctest/log folder and ./nrctest/log_bak folder exit before run this script

# copy old log & cleanup
echo '---- copy & cleanup ---'
echo
cp -r ./nrctest/log/* ./nrctest/log_bak
rm -fr ./nrctest/log/*

# change test setup for NRaaS test
sh setup_for_NRaaS_test.sh

echo '---- Start NRaaS regression test ----'
echo 
# run NRaaS regression test 
./nrctest.sh -x RegressionTestNRaaS/gRPCTest -r
echo '---- NRaaS regression test done ---'
echo 


# merge test subset result into one xml result
sh merge_nraas_regression_results.sh
echo '---- Merge NRaaS regression test results XML done ---'
echo

# collect logs to NRaaS result older
sh collect_log_nraas.sh
echo '---- Collect test logs to NRaaS log folder ---'
echo


# merge test subset result into one xml result
sh print_test_summary.sh
echo

