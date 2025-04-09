emissary_service="emissary-emissary-ingress"
nraas_namespace="nraas-qa"
echo "do emissary port-forward"
kubectl port-forward service/${emissary_service} 4433:443 -n ${nraas_namespace} --kubeconfig=/root/.kube/config &
sleep 2