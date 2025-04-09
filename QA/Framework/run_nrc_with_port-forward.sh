#!/bin/bash
HELM_RELEASE_NAMESPACE=nraas-load
NRAAS_SERVICE=nrc-dhinesh-nraas
# stop NRC port forward
echo "********* Stop NRC port forward ********"
sh stop_nrc_with_port-forward.sh

echo 
echo "--------- Run NRC with port forwarded-----------"

# wait
echo "------ ----------"
sleep 2

# check kubernetes status after nrc install
echo "------ Check Kubernetes status after nrc install --------------"
echo " ---- Pods ------ "
kubectl get pods --output=wide -n ${HELM_RELEASE_NAMESPACE} --kubeconfig=/root/.kube/config
echo "---- Services ----"
kubectl get services --output=wide -n ${HELM_RELEASE_NAMESPACE} --kubeconfig=/root/.kube/config
echo "---- Deployments ----"
kubectl get deployments --output=wide -n ${HELM_RELEASE_NAMESPACE} --kubeconfig=/root/.kube/config
echo

# forward traffic to the cluster from an external machine
echo "------- Forward nrc traffice to cluster(via master node, running on worker node) from external machine -----------"
kubectl port-forward service/${NRAAS_SERVICE} --address 0.0.0.0 50051:nrc-svc-http2 50052:nrc-svc-https2 -n ${HELM_RELEASE_NAMESPACE} --kubeconfig=/root/.kube/config &
sleep 2
#

# Speical scripts to avoid port forward timeout (optional, make sure netcat installed before run this script! "yum install -y nc")
sleep 2
nc -vz 127.0.0.1 50051
nc -vz 127.0.0.1 50052
sh port-forward_keep-alive_50051.sh > /dev/null 2>&1 &
sh port-forward_keep-alive_50052.sh > /dev/null 2>&1 &

#
echo '---- Done ----'
