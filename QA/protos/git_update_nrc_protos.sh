#!/bin/bash

#clean up
echo "--- clean up Git folder for nrc_protos ---" 
rm -fr nrc_protos
mkdir -p nrc_protos
cd nrc_protos
echo

# init git
echo "--- git init ---"
git init
echo

# partial clone for specific nrc proto updates from git
echo " --- git clone for specific nrc proto updates from git ---"
git remote add origin git@git.labs.nuance.com:ent-rd/ivr/cn-nr/nrc-grpc.git
git config core.sparseCheckout true
echo nuance/*>> .git/info/sparse-checkout
echo nuance/nrc/*>> .git/info/sparse-checkout
echo master/nuance/nrc/v1/*>> .git/info/sparse-checkout
git pull --depth=1 origin master --allow-unrelated-histories
echo

# copy proto
echo "--- copy proto to /QA/protos ---"
echo y | cp ./nuance/nrc/v1/nrc.proto ../
cd ..
echo

