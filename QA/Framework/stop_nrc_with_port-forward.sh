#/bin/bash 
HELM_RELEASE_NAMESPACE=nraas-load
NRAAS_SERVICE=nrc-dhinesh-nraas
# Stop all NRC port forward process....

echo 
echo '--- Stop all NRC port forwarded process which started by QA bash script --- '
echo

echo '--- list before kill NRC port-forward process ---'
ps -ef | grep port-forward

# kill port-forward background process  
pkill -f "sh port-forward_keep-alive_50051.sh"
pkill -f "sh port-forward_keep-alive_50052.sh"
pkill -f "kubectl port-forward service/${NRAAS_SERVICE} --address 0.0.0.0 50051:nrc-svc-http2 50052:nrc-svc-https2 -n ${HELM_RELEASE_NAMESPACE} --kubeconfig=/root/.kube/config"
sleep 2

#
echo
echo '--- list after kill NRC port-forward process ---'
ps -ef | grep port-forward
echo 
echo '--- Done ---'
sleep 2
