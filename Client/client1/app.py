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
MINE_IP_PORT = 9003
MINE_ID = 0
NAME = ""
GROUP_NAME = ""
data = ""
CLUSTER_PORT = 0
LECTURE_INTERVAL = 0

# Funzione per la lettura del file 'config.json'
def readJson():
    global data, SEARCH_INTERVAL, CLUSTER_PORT, BCAST_IP, BCAST_PORT, PROTOCOL, MINE_IP_PORT, NETWORK_ID, MINE_IP_PORT, DATA, NAME, GROUP_NAME, MINE_ID, LECTURE_INTERVAL
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
        MINE_IP_PORT = data['mine_ip_port']
        CLUSTER_PORT = data['cluster_port']
        LECTURE_INTERVAL = data['lecture_interval']
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
def getClusterIpAddress():
        global CLUSTER_IP_ADDRESS
        '''
        broadcast SSDP DISCOVER message to LAN network
        filter our protocal and add to network
        '''
        while True:
            try:
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
                    data, addr = sock.recvfrom(1024)
                    print('Risposta SSDP ricevuta.')
                    CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                    return
            except:
                sock.close()


app = Flask(__name__) #create the Flask app

# Router per la get per controllare lo stato del dispositivo
@app.route('/checkStatus', methods=['GET'])
def checkStatus():
    return "Ok"

# Router per la get per controllare lo stato del dispositivo
@app.route('/getEC2Value', methods=['GET'])
def getEC2Value():
    fakesensor.setValue(request.args.get("value"))
    return "Ok"

# Route per modificare la configurazione a runtime, magari tramite la dashboard
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
    readJson()
    getClusterIpAddress()
    getMineIpAddress()
    result = ""

    while (result != "Ok"):
        dictToSend = {'id':MINE_ID, 'ipAddress': MINE_IP_ADDRESS, 'ipPort': MINE_IP_PORT, 'name': data['name'], 'type':data['type']}
        try:
            result = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+ str(CLUSTER_PORT)+'/newDevice', json=dictToSend, timeout = 3).text
            logging.info(result)
            if result == "Ok":
                print('Dispositivo inserito correttamente.')
            else:
                raise(request.exceptions.RequestException)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("Errore durante l'inserimento del dispositivo.")
        
    if data['type'] == 'sensor':

        while (True):
            dictToSend = {'id':data['id'], 'temperatura': fakesensor.getTemperature(), 'umidita': fakesensor.getUmidity()}
            try:
                result = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+str(CLUSTER_PORT)+'/sendDataToCluster', json=dictToSend, timeout=3).text
                if result == "Ok":
                    print("Misurazione inserita correttamente.")
                elif result == "Not present":
                    print("Il dispositivo non e' registrato.")
                else:
                    print("Errore durante la registrazione della misurazione.")
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                logging.warning('Errore durante la registrazione della misurazione.')
                getClusterIpAddress()
            time.sleep(LECTURE_INTERVAL)

if __name__ == '__main__':
    thread = Thread(target = doSomeStuff)
    thread.start()
    app.run(host='0.0.0.0', debug=False, port=MINE_IP_PORT) #run app in debug mode on port 5000
