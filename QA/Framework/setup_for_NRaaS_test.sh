#!/bin/bash
echo
echo '---- Setup for NRaaS regression test ---'
echo 
echo '---- change config for NRaaS test ---'
cd /package/unarchive/Framework/config
echo yes | cp testServerConfig_NRaaS.yaml testServerConfig.yaml

echo 
echo '---- change test client for NRaaS test ---'
cd /package/unarchive/Framework/nrctest/NRCSetupClass
echo yes | cp gRPCClient_nraas.py gRPCClient.py	
echo 

echo '---- Done (note: suggest to run smoke test to make sure) ---'
echo

