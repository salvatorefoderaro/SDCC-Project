from flask import Flask, request #import main Flask class and request object
import requests
import subprocess

app = Flask(__name__) #create the Flask app

SERVICE_EXTERNAL_IP = ""

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
    dictToSend = {'id':request.json['id'], 'ip':request.json['ip'], 'status':request.json['status']}
    print(request.json['id'])
    try:
        res = requests.post('http://' + SERVICE_EXTERNAL_ip + ':30006/collectData', json=dictToSend)
        print(res.text)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        return e
    return res.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True) #run app in debug mode on port 5000