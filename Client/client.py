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

MINE_IP_ADDRESS = ""
CLUSTER_IP_ADDRESS = ""
SEARCH_INTERVAL = 5
BCAST_IP = '239.255.255.250'
BCAST_PORT = 10000
port = 9001
protocol = "blockchain"
networkid = "main1111"

with open('config.json') as config_file:
    data = json.load(config_file)

def getMineIPAddress():
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

def getClusterIPAddress():
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
                LOCATION_REGEX = re.compile("LOCATION: {}_{}://[ ]*(.+)\r\n".format(protocol, networkid), re.IGNORECASE)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(SSDP_DISCOVER.encode('ASCII'), (BCAST_IP, BCAST_PORT))
                sock.settimeout(3)
                while True:
                    data, addr = sock.recvfrom(1024)
                    print("Risposta ricevuta!")
                    CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                    return

                '''
                                while True:
                    data, addr = sock.recvfrom(1024)
                    print("Risposta ricevuta!")
                    CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                    dictToSend = {'id':data['id'], 'ipAddress': MINE_IP_ADDRESS, 'name': json_object['name'], 'groupName':json_object['groupName']}
                    try:
                        res = requests.post('http://'+CLUSTER_IP_ADDRESS+':5000/newDevice', json=dictToSend)
                        return
                    except requests.exceptions.RequestException as e:  # This is the correct syntax
                        print("ricevuto errore")
                    
                '''
            except:
                sock.close()


app = Flask(__name__) #create the Flask app

# Router per la get per controllare lo stato del dispositivo
@app.route('/checkStatus', methods=['GET'])
def query_example():
    return "I'm alive"

# Route per modificare la configurazione a runtime, magari tramite la dashboard
@app.route('/editConfig', methods=['GET'])
def editConfig():
    configFile = open("config.json", "r")
    json_object = json.load(configFile)
    
    if (request.args.get("name") is not None):
        json_object["name"] = request.args.get("name")
    if (requests.arg.get("groupName") is not None):
        json_object["groupName"] = request.args.get("groupName")

    json.dump(json_object, configFile)
    configFile.close()

def doSomeStuff():
    getClusterIPAddress()
    getMineIPAddress()


    dictToSend = {'id':data['id'], 'ipAddress': MINE_IP_ADDRESS, 'name': data['name'], 'groupName':data['groupName']}
    try:
        res = requests.post('http://'+CLUSTER_IP_ADDRESS+':5000/newDevice', json=dictToSend)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ricevuto errore")
    
    while (True):
        dictToSend = {'id':data['id'], 'temperatura': randint(0, 10), 'umidita': randint(0, 100)}
        try:
            res = requests.post('http://'+CLUSTER_IP_ADDRESS+':5000/sendDataToCluster', json=dictToSend)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("ricevuto errore")
            getClusterIPAddress()
        time.sleep(60)

if __name__ == '__main__':
    thread = Thread(target = doSomeStuff)
    thread.start()
    app.run(host='0.0.0.0', debug=False, port=7000) #run app in debug mode on port 5000
