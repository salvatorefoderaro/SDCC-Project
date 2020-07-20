# Introduzione

Esempio di Kuberneetes (*Minikube*), con due applicativi che comunicano tra di loro in ottica di Microservizi. Al momento non è Kuberneetes puro.

0. **Installo Minikube**
   1. https://computingforgeeks.com/how-to-install-minikube-on-ubuntu-debian-linux/
1. **Avvio Minikube** 
   1. minikube start
2. **Entro nel contesto di minikube**
   1. eval $(minikube docker-env)
3. **Effettuo il build dei due container docker che mi servono**
   1. cd check_status_deployment && docker build -t checkstatus:v1 .
   2. cd collect_data_deployment && docker build -t collectdata:v1 .
   3. cd database_instantiate_db_job && docker build -t dbinstantiate:v1 .
   4. cd dashboard && docker build -t dashboard:v1 .
   5. cd get_devices_stat_dashboard && docker build -t getdevicesstat:v1 .
4. **Carico i servizi necessari per Kuberneetes**
   1. cd yaml
   2. kubectl apply -f mysql-pv.yaml
   3. kubectl apply -f mysql-deployment.yaml
   4. kubectl apply -f db_instantiate_job.yaml
   5. kubectl apply -f dep_collect_data.yaml
   6. kubectl apply -f ser_collect_data.yaml
   7. kubectl apply -f cronjob_check_status.yaml
5. **Avvio il tunnel** 
   1. minikube tunnel
6. **Avvio la dashboard**
   1. minikube dashboard
7. **Trovo l'IP esposto del Cluster**
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