from flask import Flask, request #import main Flask class and request object
import requests
from ssdp import Server
from ssdp import gen_logger
import minikubeservice
import time
import logging

'''
Modulo necessario per la comunicazione tra la rete interna (dispositivi) ed il cluster.
'''

app = Flask(__name__) #create the Flask app

COLLECT_DATA_PORT = 30006
FLASK_PORT = 5000

logger = gen_logger('sample')

# Ottengo l'indirizzo ip del servizio esposto dal cluster
def getExternalIp():
    global SERVICE_EXTERNAL_IP
    SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 
    while (SERVICE_EXTERNAL_IP == 'None' or SERVICE_EXTERNAL_IP == "<pending>"):
        print("Waiting for SERVICE_EXTERNAL_IP...")
        time.sleep(30)   
        SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 

# Modifico la configurazione di un dispositivo
@app.route('/editConfig', methods=['GET'])
def edit_config():
    try:
        res = requests.get("http://"+ str(request.args.get("ipAddress"))+":"+ str(request.args.get("ipPort")) + "/editConfig?type=" + str(request.args.get("type")) + "&new_value=" + str(request.args.get("new_value")), timeout=3)
        return res.text
    except requests.exceptions.RequestException as e:
        return "Dead"

# Controllo lo stato di un dispositivo
@app.route('/checkStatus', methods=['GET'])
def query_example():
    try:
        res = requests.get("http://"+ str(request.args.get("ipAddress"))+":"+ str(request.args.get("ipPort")) + "/checkStatus", timeout=3)
        return res.text
    except requests.exceptions.RequestException as e:
        return "Dead"

# Aggiungo un dispositivo al cluster
@app.route('/newDevice', methods=['POST'])
def new_device():
    dictToSend = {'id':request.json['id'], 'ipAddress':request.json['ipAddress'], 'ipPort':request.json['ipPort'], 'name':request.json['name'], 'type' : request.json['type']}
    try:
        res = requests.post("http://" + str(SERVICE_EXTERNAL_IP) + ":" + str(COLLECT_DATA_PORT) +"/newDevice", json=dictToSend, timeout=10)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        getExternalIp()
        return "Not ok"

# Invio la lettura del dispositivo al cluster
@app.route('/sendDataToCluster', methods=['POST'])
def jsonexample():
    dictToSend = {'id':request.json['id'], 'temperatura':request.json['temperatura'], 'umidita':request.json['umidita']}
    try:
        res = requests.post("http://" + str(SERVICE_EXTERNAL_IP) + ":"+ str(COLLECT_DATA_PORT) +"/collectData", json=dictToSend, timeout=10)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        getExternalIp()
        return "Not ok"

if __name__ == '__main__':   
    getExternalIp()

    # Avvio il server SSDP
    upnpServer = Server(9001, 'blockchain', 'main1111')
    upnpServer.start()
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT, threaded=True) #run app in debug mode on port 5000