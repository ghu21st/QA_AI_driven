#!/bin/bash
echo
echo '---- Setup for NRaaS regression test ---'
echo 
echo '---- change config for NRaaS test ---'
cd $TESTPATH/ev2/Scripts/Framework/config
echo yes | cp testServerConfig_cd1QA.yaml testServerConfig.yaml

echo 
echo '---- change test client for NRaaS test ---'
cd $TESTPATH/ev2/Scripts/Framework/nrctest/NRCSetupClass
echo yes | cp gRPCClient_cd1nraas.py gRPCClient.py
echo 

echo '---- Done (note: suggest to run smoke test to make sure) ---'
echo

