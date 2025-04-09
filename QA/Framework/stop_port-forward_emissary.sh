emissary_service="emissary-emissary-ingress"
nraas_namespace="nraas-qa"
echo "kill emissary port-forward"
pkill -f "port-forward service/${emissary_service} 4433:443 -n ${nraas_namespace} --kubeconfig=/root/.kube/config"
sleep 2