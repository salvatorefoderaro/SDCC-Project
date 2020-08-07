# **SDCC-Project - Introduzione**

## **Client**

- Modulo **app.py**

## **Server**

### **Proxy**

- Modulo **proxy_server.py**
  - Si occupa della comunicazione tra la rete locale ed il cluster Kuberneetes. Questo in quanto il cluster viene avviato utilizzando **Minikube** in una macchina virtuale, con connessione di rete solo tra la macchina e l'host stesso. Il proxy è necessario per raggiungere la macchina virtuale dalla rete locale, o viceversa, raggiungere la rete locale da dentro il cluster.
  - Si occupa anche del server SSDP per essere rintracciato in automatico dai Client. Inoltre, trova in automatico l'indirizzo IP del cluster anche in caso di *caduta*.

### **Cluster**

- Modulo **instantiate_database**
  - Si occupa dell'istanziazione del database, dunque creazione del db e delle tabelle necessarie
- Modulo **collect_data**
  - Si occupa della ricezione della lettura dei dati da parte dei vari client. Ogni lettura viene inserita all'interno del database
- Modulo **check_devices_status**
  - Si occupa di andare ad interrogare periodicamente tutti i client, per vedere chi è ancora up e chi invece no
- Modulo **get_devices_stat**
  - Si occupa della comunicazione con il database per la Dashboard. Da rinominare in qualcos'altro
- Modulo **dashboard**
  - Si occupa di fornire la dashboard all'utente
- Modulo **s3_upload_dump**
  - Su occupa di caricare su *S3*, in modo periodico, il backup del singolo cluster

# **SDCC-Project - Installazione**

## **Avvio cluster**

0. **Installo Minikube**
   1. cd Server && sh install_minikube.sh
1. **Effettuo l'instanziazione del cluster**
   1. cd Server && sh instantiate_cluster.sh
2. **Avvio la dashboard**
   1. minikube dashboard

## **Avvio proxy**

1. cd proxy_python
2. **Installo i pacchetti necessari**
   1. sh requirement.sh
3. **Avvio il proxy**
   1. sh run.sh

## **Avvio client**

1. cd Client/client*
2. **Installo i pacchetti necessari**
   1. sh requirement.sh
3. **Avvio il client**
   1. sh run.sh

- **Comandi utili:**
  - **Aggiornamento del deployment:**
    - *sh update_deployment.sh*
  - **Pulizia del cluster:**
    - *sh clean_cluster.sh*

# **SDCC-Project - Materiale vario**

## **Possibile query per l'invio ad EC2**

- *select AVG(L.temperatura), AVG(L.umidita), D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE D.type='sensor' GROUP BY D.groupName;*

## **Dockerizzazione Client**

1. docker build -t client* .
2. docker run -p port:port client*

Esercizio di stile, tanto non va la rete, non potendo mandare messaggi in broadcast al proxy

## **Link utili**

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

## **Sviluppi futuri**

https://github.com/clach04/python-tuya

https://github.com/codetheweb/tuyapi

https://www.amazon.it/compatibile-telecomando-automazione-regolatore-Manipolatore/dp/B084VPD5TM/

## **Possibili problemi di sicurezza**

https://blog.rapid7.com/2013/01/29/security-flaws-in-universal-plug-and-play-unplug-dont-play/

https://blog.cloudflare.com/ssdp-100gbps/

https://www.cloudflare.com/learning/ddos/ssdp-ddos-attack/