from flask import Flask, request #import main Flask class and request object
import requests

app = Flask(__name__) #create the Flask app


@app.route('/checkStatus', methods=['GET'])
def query_example():
    try:
        res = requests.get('http://'+request.args.get('ipAddress')+'/checkStatus)')
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e

@app.route('/sendDataToCluster', methods=['POST'])
def jsonexample():
    dictToSend = {'id':request.json['id'], 'ip':request.json['id'], 'status':request.json['id']}
    print(request.json['id'])
    try:
        res = requests.post('http://10.98.105.89:30006/collectData', json=dictToSend)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return e
    return res.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000) #run app in debug mode on port 5000