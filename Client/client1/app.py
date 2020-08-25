from flask import Flask, request #import main Flask class and request object
import requests
import os
import socket
import re
import sys
import threading
import socket
import time
import json
from threading import Thread
from random import randint
import fakesensor
import logging

'''
Modulo del singolo dispositivo IoT per la registrazione dei dati.
'''

MINE_IP_ADDRESS = ""
CLUSTER_IP_ADDRESS = ""
SEARCH_INTERVAL = 0
BCAST_IP = ''
BCAST_PORT = 0  
PROTOCOL = ""
NETWORK_ID = ""
MINE_IP_ADDRESS = ""
MINE_IP_PORT = 0
MINE_ID = 0
NAME = ""
GROUP_NAME = ""
data = ""
CLUSTER_PORT = 0
LECTURE_INTERVAL = 0
TYPE = ""

# Leggo il file 'config.json' e memorizzo i vari parametri in specifiche variabili.
def readJson():
    global data, TYPE, SEARCH_INTERVAL, CLUSTER_PORT, BCAST_IP, BCAST_PORT, PROTOCOL, MINE_IP_PORT, NETWORK_ID, MINE_IP_PORT, DATA, NAME, GROUP_NAME, MINE_ID, LECTURE_INTERVAL
    with open('config.json') as config_file:
        data = json.load(config_file)
        MINE_ID = data['id']
        NAME = data['name']
        GROUP_NAME = data['groupName']
        SEARCH_INTERVAL = data['search_interval']
        BCAST_IP = data['bcast_ip']
        BCAST_PORT = data['bcast_port']
        PROTOCOL = data['protocol']
        NETWORK_ID = data['networkid']
        MINE_IP_PORT = data['port']
        CLUSTER_PORT = data['cluster_port']
        LECTURE_INTERVAL = data['lecture_interval']
        TYPE = data['type']
        config_file.close()

# Funzione per l'ottenimento del proprio indirizzo IP all'interno della rete
def getMineIpAddress():
    global MINE_IP_ADDRESS
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    MINE_IP_ADDRESS = IP

# Client SSDP per l'ottenimento dell'indirizzo IP del cluster.
def getProxyIPAddress():
        global CLUSTER_IP_ADDRESS
        while True:
            try:
                # Invio in broadcast sulla rete locale il messaggio di discovery del server SSDP
                SSDP_DISCOVER = ('M-SEARCH * HTTP/1.1\r\n' +
                            'HOST: 239.255.255.250:1900\r\n' +
                            'MAN: "ssdp:discover"\r\n' +
                            'MX: 1\r\n' +
                            'ST: ssdp:all\r\n' +
                            '\r\n')
                LOCATION_REGEX = re.compile("LOCATION: {}_{}://[ ]*(.+)\r\n".format(PROTOCOL, NETWORK_ID), re.IGNORECASE)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(SSDP_DISCOVER.encode('ASCII'), (BCAST_IP, BCAST_PORT))
                sock.settimeout(3)
                while True:
                    # Attendo la risposta da parte del Server, andando a memorizzare il suo indirizzo IP.
                    data, addr = sock.recvfrom(1024)
                    print('Risposta SSDP ricevuta.')
                    CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                    return
            except:
                sock.close()

app = Flask(__name__) #create the Flask app

# Route per la GET per il controllo dello stato del dispositivo
@app.route('/checkStatus', methods=['GET'])
def checkStatus():
    return "Ok"

# Route per la GET per il controllo della valvola
@app.route('/getEC2Value', methods=['GET'])
def getEC2Value():
    fakesensor.setValue(request.args.get("value"))
    return "Ok"

# Route per la modifica della configurazione del dispositivo a runtime
@app.route('/editConfig', methods=['GET'])
def editConfig():
    global LECTURE_INTERVAL
    with open('config.json') as config_file:
        data = json.load(config_file)
        config_file.close()

        configFile = open("config.json", "w")

        if (request.args.get("type") == "name"):
            data["name"] = request.args.get("new_value")
        if (request.args.get("type") == "groupName"):
            data["groupName"] = request.args.get("new_value")
        if (request.args.get("type") == "lecture_interval"):
            LECTURE_INTERVAL = int(request.args.get("new_value"))
            data["lecture_interval"] = int(request.args.get("lecture_interval"))

        json.dump(data, configFile)
        configFile.close()

    return "Ok"

# Funzione per l'inserimento del dispositivo e delle letture.
def doSomeStuff():

    # Ottengo l'indirizzo ip del cluster
    getProxyIPAddress()

    # Ottengo il mio indirizzo ip
    getMineIpAddress()
    result = ""

    while (result != "Ok"):
        
        # Preparo il dizionario con i dati da inviare al cluster per la registrazione del dispositivo
        dictToSend = {'id':MINE_ID, 'ipAddress': MINE_IP_ADDRESS, 'ipPort': MINE_IP_PORT, 'name': data['name'], 'type':data['type']}
        try:
            
            # Invio i dati al proxy tramite chiamata POST
            result = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+ str(CLUSTER_PORT)+'/newDevice', json=dictToSend, timeout = 3).text
            
            # Controllo la risposta da parte del proxy
            if result == "Ok":
                print('Dispositivo inserito correttamente.')
            else:
                raise(request.exceptions.RequestException)
        
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("Errore durante l'inserimento del dispositivo.")
            getProxyIPAddress()
        
    # Se il dispositivo è un sensore...
    if TYPE == 'sensor':

        # Invio ad intervallo di tempo regolari le letture di temperatura ed umidità
        while (True):

            # Preparo i dati da inviare
            dictToSend = {'id':data['id'], 'temperatura': fakesensor.getTemperature(), 'umidita': fakesensor.getUmidity(), 'type': 'sensor'}
            try:

                # Effettuo la POST verso il proxy
                result = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+str(CLUSTER_PORT)+'/sendDataToCluster', json=dictToSend, timeout=3).text
                
                # Controllo il risultato
                if result == "Ok":
                    print("Misurazione inserita correttamente.")
                
                # Accade nel caso di errori, se il dispositivo non era stato precedentemente registrato
                elif result == "Not present":
                    print("Il dispositivo non e' registrato.")
                    
                else:
                    print("Errore durante la registrazione della misurazione.")
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                logging.warning('Errore durante la registrazione della misurazione.')
                
                # Nel caso di errore, mi rimetto alla ricerca dell'indirizzo IP del cluster
                getProxyIPAddress()
            
            # Attendo prima di inviare la prossima lettura
            time.sleep(LECTURE_INTERVAL)

if __name__ == '__main__':
    readJson()
    thread = Thread(target = doSomeStuff)
    thread.start()
    app.run(host='0.0.0.0', debug=False, port=MINE_IP_PORT) #run app in debug mode on port 5000