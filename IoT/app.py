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
import check_image
from pprint import pprint

'''
Module for the single IoT device. Each device could be of 2 type:

- Sensor
    - Send, at regular interval of time, lectures to the cluster.
- Control
    - Receive, at regular interval of the time, info about how many water have to be "open" for the field.

The module need to send data to the Proxy. The IP address of the proxy is discovered using the SSDP protocol.

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
WATER_SPEED = 0
TYPE = ""
REFERENCE_IMAGE = ""
IMAGE_INTERVAL = ""
CAMERA = ""

# Read the .json file to get the config.
def readJson():
    global CAMERA, IMAGE_INTERVAL, REFERENCE_IMAGE, data, WATER_SPEED, TYPE, SEARCH_INTERVAL, CLUSTER_PORT, BCAST_IP, BCAST_PORT, PROTOCOL, MINE_IP_PORT, NETWORK_ID, MINE_IP_PORT, DATA, NAME, GROUP_NAME, MINE_ID, LECTURE_INTERVAL
    with open(sys.argv[1]) as config_file:
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
        CAMERA = data['camera'] 

        if CAMERA == "Yes":
            REFERENCE_IMAGE = data['reference_image']
            IMAGE_INTERVAL = data['image_interval']

        if TYPE == 'execute':
            WATER_SPEED = data['water_speed']
            
        config_file.close()

# Get the device ip addres that need to be sent for the registration to the cluster.
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

# Get the proxy IP address using the SSDP protocol.
def getProxyIPAddress():
        global CLUSTER_IP_ADDRESS
        while True:
            try:
                # Send broadcast message.
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
                    # Waiting for the reply of the server. After reply received, save the IP address.
                    data, addr = sock.recvfrom(1024)
                    print('Risposta SSDP ricevuta.')
                    CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                    return
            except:
                sock.close()

app = Flask(__name__) #create the Flask app

# Route to check the status of the device
@app.route('/checkStatus', methods=['GET'])
def checkStatus():
    return "Ok"

# Route to get the value for the device of type 'control'
@app.route('/getEC2Value', methods=['GET'])
def getEC2Value():
    fakesensor.setValue(request.args.get("value")/WATER_SPEED)
    return "Ok"

# Route for the edit of the configuration.
@app.route('/editConfig', methods=['GET'])
def editConfig():
    global LECTURE_INTERVAL
    with open('config.json') as config_file:
        data = json.load(config_file)
        config_file.close()

        configFile = open("config.json", "w")

        if (request.args.get("type") == "name"):
            data["name"] = request.args.get("new_value")
            NAME = request.args.get("new_value")
        if (request.args.get("type") == "groupName"):
            data["groupName"] = request.args.get("new_value")
            GROUP_NAME = request.args.get("new_value")
        if (request.args.get("type") == "lecture_interval"):
            LECTURE_INTERVAL = int(request.args.get("new_value"))
            data["lecture_interval"] = int(request.args.get("new_value"))

        json.dump(data, configFile)
        configFile.close()

    return "Ok"

# Function that register the device and send the lecture to the proxy.
# Function that register the device and send the lecture to the proxy.
def sendData():

    getProxyIPAddress()
    getMineIpAddress()
    responnse = ""

    # Till when the device is not correctly registered.
    while (responnse != "Ok"):
        
        # Build the content of the POST request.       
        dictToSend = {'id':MINE_ID, 'ipAddress': MINE_IP_ADDRESS, 'ipPort': MINE_IP_PORT, 'name': data['name'], 'type':data['type']}
        
        try:    
            # Send the request to the Proxy
            responnse = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+ str(CLUSTER_PORT)+'/newDevice', json=dictToSend, timeout = 3).text
            
            # Check the reply
            if responnse == "Ok":
                logging.info('Device registered correctly.')
            else:
                raise(request.exceptions.RequestException)
        
        except requests.exceptions.RequestException as e:  # This is the correct syntax

             # Connection error. Is the proxy down? Try searching for it...
            logging.warning('Errore during the registration of the device.')
            getProxyIPAddress()
            time.sleep(20)
        
    # If the device is a sensor, send the lectures.
    if TYPE == 'monitor':

        # Invio ad intervallo di tempo regolari le letture di temperatura ed umidità
        while (True):

            # Build the content of the POST request.       
            dictToSend = {'id':data['id'], 'temperature': fakesensor.getTemperature(), 'humidity': fakesensor.getUmidity(), 'type': 'monitor'}
           
            try:
                # Send the request to the Proxy
                responnse = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+str(CLUSTER_PORT)+'/sendDataToCluster', json=dictToSend, timeout=3).text
                
                # Check the responnse
                if responnse == "Ok":
                    logging.info("Measurement registered correctly.")    
                elif responnse == "Not present":
                    logging.warning('Device not registered.')
                else:
                    raise(requests.exceptions.RequestException)
                    
            except requests.exceptions.RequestException as e:  # This is the correct syntax

                 # Connection error. Is the PROXY down? Try searching for it...
                logging.warning('Errore during the registration of the measurement.')
                getProxyIPAddress()
                continue
            
            # Wait till the next lecture
            time.sleep(LECTURE_INTERVAL)

# Function that check the quality of the field using camera
def checkImage():

    getProxyIPAddress()
    getMineIpAddress()
    response = ""
        
    # Invio ad intervallo di tempo regolari le letture di temperatura ed umidità
    while (True):

        time.sleep(IMAGE_INTERVAL)

        dictToSend = check_image.disease_detection("img/003.jpeg", REFERENCE_IMAGE)

        if dictToSend != {}:

            dictToSend['deviceId'] = data['id']
            dictToSend['type'] = 'alert'

            try:
                # Send the request to the Proxy
                response = requests.post('http://'+CLUSTER_IP_ADDRESS+':'+str(CLUSTER_PORT)+'/sendDataToCluster', json=dictToSend, timeout=3).text
                logging
                # Check the response
                if response == "Ok":
                    logging.info("Alert registered correctly.")    
                elif response == "Not present":
                    logging.warning('Device not registered.')
                else:
                    raise(requests.exceptions.RequestException)
                    
            except requests.exceptions.RequestException as e:  # This is the correct syntax

                logging.warning(str(e) + " ERRORE")
                getProxyIPAddress()
                continue

if __name__ == '__main__':

    readJson()
    thread = Thread(target = sendData)
    
    if CAMERA == "Yes":
        thread1 = Thread(target = checkImage)
        thread1.start()
        
    thread.start()
    app.run(host='0.0.0.0', debug=False, port=MINE_IP_PORT) #run app in debug mode on port 5000