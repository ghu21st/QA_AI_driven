#!/bin/bash
echo
echo '---- Setup for NRC regression test ---'
echo 
echo '---- change config for NRC test ---'
cd /package/unarchive/Framework/config
echo yes | cp testServerConfig_NRC.yaml testServerConfig.yaml

echo 
echo '---- change test client for NRC test ---'
cd /package/unarchive/Framework/nrctest/NRCSetupClass
echo yes | cp gRPCClient_nrc.py gRPCClient.py	
echo 

echo '---- Done (note: suggest to run smoke test to make sure) ---'
echo

