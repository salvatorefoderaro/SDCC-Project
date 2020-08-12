# **SDCC-Project - Introduzione**

## **Astract**

L'idea del progetto è quello di realizzare un'applicazione volta al paradigma fog-computing, che utilizza sensori IoT. I sensori possono essere di due tipi:

- **Lettura:** sensori che leggono i valori di umidità e di temperatura, inviando le letture al cluster
- **Controllo:** sensori che controllano un sistema idrico, e che ricevono indicazioni sulla quantità di acqua da destinare ad un determinato gruppo di coltivazioni

I singoli sensori producono ad intervalli di tempi regolari letture che vengono inviate al cluster e vengono memorizzate all'interno di un database locale. Per garantire la disponibilità dei dati, ad intervalli di tempo regolari viene eseguito il backup del database e caricato su S3 dal modulo **s3_upload_dump**. 

Il cluster offre una dashboard per l'utente, tramite la quale è possibile controllare lo stato dei dispositivi, la lista dei gruppi di coltivazioni ed aggiungere nuovi gruppi di coltivazioni.

L'integrazione con i servizi **Amazon AWS** avviene tramite *S3*, per il backup dei dump del database, e con *EC2* per il calcolo dei valori da inoltrare ai singoli dispositivi di controllo.

## **Librerie Python utilizzate**

- **Flask (https://pypi.org/project/Flask/)**
  - Necessario per il web server della dashboard e gli endpoint per le chiamate REST
- **SSDP (https://github.com/codingjoe/ssdp)**
  - Necessario come servizio per il discovery da parte del client del/dei proxy
- **mysql-connector-python (https://pypi.org/project/mysql-connector-python/)**
  - Necessario per la comunicazione con il database
- **requests (https://pypi.org/project/requests/)**
  - Necessario per effettuare chiamate GET e POST
- **boto3 (https://pypi.org/project/boto3/)**
  - Necessario per la comunicazione con S3

## **Altri servizi utilizzati**

- **Minikube**
  - Necessario per avere un'istanza locale di testing per Kuberneetes
- **Kuberneetes**
  - Necessario per l'orchestrazione dei container
- **Docker**
  - Necessario per la creazione dei container

## **Cosa è stato utilizzato, di offerto, da Kuberneetes?**

- *To do...*

## **Possibili problemi di sicurezza**

https://blog.rapid7.com/2013/01/29/security-flaws-in-universal-plug-and-play-unplug-dont-play/

https://blog.cloudflare.com/ssdp-100gbps/

https://www.cloudflare.com/learning/ddos/ssdp-ddos-attack/

---

## **Implementazione**

### **Client**

- Modulo **app.py**
  - Si occupa della ricerca del server tramite il protocollo SSDP
  - Invia ogni tot di tempo le letture al Server
  - ***readJson()***
    - Funzione per la lettura del file *config.json*
  - ***getMineIpAddress()**
    - Funzione per l'ottenimento del proprio indirizzo IP all'interno della rete locale
  - ***getClusterIpAddress()***
    - Funzione per l'avvio del client SSDP per l'ottenimento dell'indirizzo ip del *proxy* in esecuzione sul server
  - ***doSomeStuff()***
    - Funzione per la registrazione del dispositivo e, successivamente, l'invio periodico delle misure registrate

**Gestione dei guasti**

- Nel caso il client non dovesse riuscire a contattare il server, dunque dovesse fallire la *POST*, il client avviera nuovamente la funzione *getClusteIpAddress()* per l'ottenimento dell'indirizzo IP del cluster. La funzione è bloccante fin quando non viene rilevato un indirizzo IP valido. Per una migliore ridondanza, è possibile l'utilizzo di più *proxy*.

### **Server**

#### **Proxy**

- Modulo **proxy_server.py**
  - Si occupa della comunicazione tra la rete locale ed il cluster Kuberneetes. Questo in quanto il cluster viene avviato utilizzando **Minikube** in una macchina virtuale, con connessione di rete solo tra la macchina e l'host stesso. Il proxy è necessario per raggiungere la macchina virtuale dalla rete locale, o viceversa, raggiungere la rete locale da dentro il cluster.
  - Si occupa anche del server SSDP per essere rintracciato in automatico dai Client. Inoltre, trova in automatico l'indirizzo IP del cluster anche in caso di *caduta*.
  - ***getExternalIp()***
    - Funzione per l'ottenimento dell'indirizzo IP del servizio *collect_data* esposto da cluster **Minikube**
  - ***upnpServer()***
    - Funzione per l'avvio del server SSDP
  - ***route sendDataToCluster***
    - Route per la ricezione delle letture da parte dei client ed inoltro al cluster
  - ***route newDevice***
    - Route per la ricezione dell'inserimento del dispositivo da parte dei client ed inoltro al cluster
  - ***route checkStatus***
    - Router per la ricezione delle richieste da parte del cluster da inoltrare ai singoli client per il controllo dello stato, up o down
  - ***route editConfig***
    - Router per la ricezione delle richieste da parte del cluster di modifica della configurazione del dispositivo da inoltrare ai singoli client

**Gestione dei guasti**

- Nel caso il proxy non dovesse riuscire a contattare il cluster, dunque dovesse fallire una delle *POST*, il proxy avviera nuovamente la funzione *getExternalIp()* per l'ottenimento dell'indirizzo IP del cluster. La funzione è bloccante fin quando non viene rilevato un indirizzo IP valido.

#### **Cluster**

- Modulo **instantiate_database**
  - Si occupa dell'istanziazione del database, dunque creazione del db e delle tabelle necessarie. Trattandosi di un job, viene eseguito una sola volta.
- Modulo **collect_data**
  - Si occupa della ricezione della lettura dei dati da parte dei vari client. Ogni lettura viene inserita all'interno del database
- Modulo **check_devices_status**
  - Si occupa di andare ad interrogare periodicamente tutti i client, per vedere chi è ancora up e chi invece no. Trattandosi di un chronjob, viene eseguito ad intervalli regolari di tempo.
- Modulo **get_devices_stat**
  - Si occupa della comunicazione con il database per la Dashboard. Da rinominare in qualcos'altro
- Modulo **dashboard**
  - Si occupa di fornire la dashboard all'utente
- Modulo **s3_upload_dump**
  - Si occupa di caricare su *S3*, in modo periodico, il backup del singolo cluster. Trattandosi di un chronjob, viene eseguito ad intervalli regolari di tempo
- Modulo **calculate_value**
  - Si occupa di inviare i dati ad EC2 per il calcolo dei valori di acqua da inviare ai singoli dispositivi adibiti al controllo

**Gestione dei guasti**

- Tramite il numero di repliche ed altri meccanismi interni, viene gestito in automatico da Kuberneetes.

# **SDCC-Project - Installazione**

## **Avvio cluster**

0. **Installo Minikube**
   1. cd Server && sh install_update_minikube.sh
1. **Effettuo l'instanziazione del cluster**
   1. cd Server && sh instantiate_cluster.sh
      1. La password per l'utente *root* è necessaria per l'avvio del servizio *minikube tunnel*
2. **Avvio la dashboard**
   1. minikube dashboard

- **Comandi utili:**
  - **Aggiornamento del deployment:**
    - *sh update_deployment.sh*
  - **Pulizia del cluster:**
    - *sh clean_cluster.sh*

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

## **Connessione al Database**

1. sh mysql_client.sh
   1. Permette di avviare una shell per interagire con il database

# **SDCC-Project - Materiale vario**

## **Possibile query per l'invio ad EC2**

- *select AVG(L.temperatura), AVG(L.umidita), D.groupName, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type='sensor' GROUP BY D.groupName;*

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