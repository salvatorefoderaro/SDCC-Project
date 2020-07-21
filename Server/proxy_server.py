from flask import Flask, request #import main Flask class and request object
import requests
import subprocess
from ssdp import Server
from ssdp import gen_logger

app = Flask(__name__) #create the Flask app

SERVICE_EXTERNAL_IP = ""

logger = gen_logger('sample')


def getServiceExternalIP():
    global SERVICE_EXTERNAL_IP
    a = subprocess.Popen(['kubectl','get','services'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT).communicate()

    list = str(a[0])
    for i in range(0, len(list.split("\\n"))):
        list = str(a[0]).split("\\n")[i].split("  ")
        for k in list:
            if '' in list:
                list.remove('')
        if list[0] == "collectdataservice":
            SERVICE_EXTERNAL_IP = list[3].replace(" ", "")
            return

@app.route('/checkStatus', methods=['GET'])
def query_example():
    print( " A chi mando la richiesta? " + " " + "http://"+ str(request.args.get("ipAddress"))+":"+ str(request.args.get("ipPort")))
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
        res = requests.post("http://" + SERVICE_EXTERNAL_IP + ":30006/newDevice", json=dictToSend)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Connection error"

@app.route('/sendDataToCluster', methods=['POST'])
def jsonexample():
    print(SERVICE_EXTERNAL_IP)
    dictToSend = {'id':request.json['id'], 'temperatura':request.json['temperatura'], 'umidita':request.json['umidita']}
    try:
        print ("http://" + SERVICE_EXTERNAL_IP + ":30006/collectData")
        res = requests.post("http://" + SERVICE_EXTERNAL_IP + ":30006/collectData", json=dictToSend)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "Not inserted"

if __name__ == '__main__':
    getServiceExternalIP()
    print(SERVICE_EXTERNAL_IP)
    upnpServer = Server(9001, 'blockchain', 'main1111')
    upnpServer.start()
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True) #run app in debug mode on port 5000