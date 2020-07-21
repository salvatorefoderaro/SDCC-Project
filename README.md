# Introduzione

0. **Installo Minikube**
   1. https://computingforgeeks.com/how-to-install-minikube-on-ubuntu-debian-linux/
1. **Avvio Minikube** 
   1. minikube start
2. **Effettuo l'instanziazione del cluster**
   1. cd Server && sh instantiate_cluster.sh
3. **Attivo il tunnel verso i servizi di tipo *LoadBalancer***
   1. minikube tunnel
4. **Avvio la dashboard**
   1. minikube dashboard
5. **Trovo l'IP esposto dai servizi del cluster**
   1. Andare alla sezione *Discovery and Load Balancing*
   2. Trovare il servizio *exampleservice*
   3. Cliccare sull'ip alla colonna *External Endpoints*

# Link utili

https://medium.com/@felipedutratine/kubernetes-on-local-with-minikube-tutorial-413475d587e6

https://stackoverflow.com/questions/46180814/how-to-connect-to-minikube-services-from-outside

https://stackoverflow.com/questions/53105262/cant-access-service-in-my-local-kubernetes-cluster-using-nodeport

https://stackoverflow.com/questions/55462654/cant-access-minikube-loadbalancer-service-from-host-machine

https://stackoverflow.com/questions/40144138/pull-a-local-image-to-run-a-pod-in-kubernetes

https://stackoverflow.com/questions/46245508/how-create-service-on-minikube-with-yaml-configuration-which-accessible-from-hos

https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube

https://stackoverflow.com/questions/882712/sending-html-email-using-python

https://stackoverflow.com/questions/20212894/how-do-i-get-flask-to-run-on-port-80

https://stackoverflow.com/questions/41322541/rebuild-docker-container-on-file-changes

https://stackoverflow.com/questions/48077931/delete-all-the-contents-from-a-kubernetes-node

https://kubernetes.io/docs/tasks/run-application/run-single-instance-stateful-application/