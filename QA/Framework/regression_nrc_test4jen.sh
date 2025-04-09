#!/bin/bash
############# NRC regression test script ###############
echo '---- NRC regression test start ---'
echo 
# run NRC regression test with -r flag for enable rerun failed cases mode
./nrctest.sh -x RegressionTest/gRPCTest/ -r
echo '---- NRC regression test done --- '
echo 

# merge test subset result into one xml result
sh merge_nrc_regression_results.sh
echo '---- Merge NRC regression test result XML done ---'
echo

# collect logs to NRC result older
sh collect_log_nrc.sh
echo '---- Collect test logs to NRC log folder done ---'
echo

# merge test subset result into one xml result
sh print_test_summary.sh
echo


