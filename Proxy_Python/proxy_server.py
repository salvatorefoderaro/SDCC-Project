from flask import Flask, request #import main Flask class and request object
import requests
from ssdp import Server
from ssdp import gen_logger
import minikubeservice
import time
import logging
import json
import logging
from pprint import pprint

'''
The module make a bridge between the devices and the cluster. Because of Minikube, the outside-exposed services could be reached just from the
host machine where Minikube is running. In this way, all the request incoming from the devices, are sent to the cluster.

The proxy run an SSDP server, needed to be founded dinamically by the client.
'''

app = Flask(__name__) 

EXTERNAL_IP_INTERVAL = 0
COLLECT_DATA_PORT = 0
FLASK_PORT = 0
SERVICE_EXTERNAL_IP = ""

logger = gen_logger('sample')

# Read config from file 'config.json'
def readJson():
    global EXTERNAL_IP_INTERVAL, COLLECT_DATA_PORT, FLASK_PORT
    with open('config.json') as config_file:
        data = json.load(config_file)
        EXTERNAL_IP_INTERVAL = data['external_ip_interval']
        COLLECT_DATA_PORT = data['collect_data_port']
        FLASK_PORT = data['flask_port']
        config_file.close()

# Get the IP of the 'collect_data' service.
# Run the terminal command 'kubectl get services' and parse it in the 'minikubeservice' module
def getCollectDataIP():
    global SERVICE_EXTERNAL_IP
    SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 
    while (SERVICE_EXTERNAL_IP == 'None' or SERVICE_EXTERNAL_IP == '<pending>'):
        logging.info("Waiting for cluster 'collect_data' ip...")
        time.sleep(EXTERNAL_IP_INTERVAL)   
        SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 

# Route to add a new device to the cluster. Send to the cluster the received POST content.
@app.route('/newDevice', methods=['POST'])
def newDevice():
    try:
        responnse = requests.post("http://" + str(SERVICE_EXTERNAL_IP) + ":" + str(COLLECT_DATA_PORT) +"/newDevice", json=request.json, timeout=10)
        return responnse.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        
        # Connection error. Is the cluster down? Try searching for it...
        getCollectDataIP()
        return "Not ok"

# Route to send data to the cluster. Send to the cluster the received POST content.
@app.route('/sendDataToCluster', methods=['POST'])
def sendDataToCluster():

    if request.json['type'] != 'alert':

        try:
            response = requests.post("http://" + str(SERVICE_EXTERNAL_IP) + ":"+ str(COLLECT_DATA_PORT) +"/collectData", json=request.json, timeout=10)
            return response.text
        except requests.exceptions.RequestException as e:  
            # Connection error. Is the cluster down? Try searching for it...      
            getCollectDataIP()
            return "Not ok"
    else:

        try:
            response = requests.post("http://" + str(SERVICE_EXTERNAL_IP) + ":"+ str(COLLECT_DATA_PORT) +"/collectDataImage", json=request.json, timeout=10)
            print(response.text)
            return response.text
        except requests.exceptions.RequestException as e:  
            # Connection error. Is the cluster down? Try searching for it...      
            getCollectDataIP()
            return "Not ok"    

if __name__ == '__main__':   
    readJson()
    getCollectDataIP()

    # Start SSDP server
    ssdpServer = Server(9001, 'ssdp', 'cluster')
    ssdpServer.start()

    # Run Flask
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT, threaded=True) #run app in debug mode on port 5000