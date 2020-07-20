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
        if str(a[0]).split("\\n")[i].split("  ")[0] == "collectdataservice":
            SERVICE_EXTERNAL_IP = str(a[0]).split("\\n")[i].split("  ")[3]
            print(SERVICE_EXTERNAL_IP)
            return

@app.route('/checkStatus', methods=['GET'])
def query_example():
    try:
        res = requests.get('http://'+request.args.get('ipAddress')+':7000/checkStatus')
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e

@app.route('/sendDataToCluster', methods=['POST'])
def jsonexample():
    dictToSend = {'id':request.json['id'], 'temperatura':request.json['temperatura'], 'umidita':request.json['umidita']}
    try:
        res = requests.post('http://' + SERVICE_EXTERNAL_IP + ':30006/collectData', json=dictToSend)
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e

if __name__ == '__main__':
    getServiceExternalIP()
    upnpServer = Server(9001, 'blockchain', 'main1111')
    upnpServer.start()
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True) #run app in debug mode on port 5000