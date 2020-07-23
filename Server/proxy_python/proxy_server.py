from flask import Flask, request #import main Flask class and request object
import requests
from ssdp import Server
from ssdp import gen_logger
import minikubeservice
import time

app = Flask(__name__) #create the Flask app

COLLECT_DATA_PORT = 30006
FLASK_PORT = 5000

logger = gen_logger('sample')

@app.route('/editConfig', methods=['GET'])
def edit_config():
    try:
        res = requests.get("http://"+ str(request.args.get("ipAddress"))+":"+ str(request.args.get("ipPort")) + "/editConfig?type=" + str(request.args.get("type")) + "&new_value=" + str(request.args.get("new_value")), timeout=3)
        return res.text
    except requests.exceptions.RequestException as e:
        return "Dead"

@app.route('/checkStatus', methods=['GET'])
def query_example():
    try:
        res = requests.get("http://"+ str(request.args.get("ipAddress"))+":"+ str(request.args.get("ipPort")) + "/checkStatus", timeout=3)
        print(res.text)
        return res.text
    except requests.exceptions.RequestException as e:
        print("Dead")
        return "Dead"

@app.route('/newDevice', methods=['POST'])
def new_device():
    dictToSend = {'id':request.json['id'], 'ipAddress':request.json['ipAddress'], 'ipPort':request.json['ipPort'], 'name':request.json['name'], 'groupName' : request.json['groupName']}
    try:
        res = requests.post("http://" + SERVICE_EXTERNAL_IP + ":" + COLLECT_DATA_PORT +"/newDevice", json=dictToSend)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Connection error"

@app.route('/sendDataToCluster', methods=['POST'])
def jsonexample():
    print(SERVICE_EXTERNAL_IP)
    dictToSend = {'id':request.json['id'], 'temperatura':request.json['temperatura'], 'umidita':request.json['umidita']}
    try:
        print ("http://" + SERVICE_EXTERNAL_IP + ":" + COLLECT_DATA_PORT +"/collectData")
        res = requests.post("http://" + SERVICE_EXTERNAL_IP + ":"+ COLLECT_DATA_PORT +"/collectData", json=dictToSend)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Not inserted"

if __name__ == '__main__':
   
    global SERVICE_EXTERNAL_IP
    SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 
    while SERVICE_EXTERNAL_IP == None or SERVICE_EXTERNAL_IP == "<pending>":
        time.sleep(30)   
        SERVICE_EXTERNAL_IP = minikubeservice.getServiceExternalIP("collectdataservice") 
   
    upnpServer = Server(9001, 'blockchain', 'main1111')
    upnpServer.start()
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT, threaded=True) #run app in debug mode on port 5000