from flask import Flask, request #import main Flask class and request object
import requests

app = Flask(__name__) #create the Flask app

# Router per la get per controllare lo stato del dispositivo
@app.route('/checkStatus', methods=['GET'])
def query_example():
    return "I'm alive"

# Route per modificare la configurazione a runtime, magari tramite la dashboard
@app.route('/editConfig', methods=['GET'])
def editConfig():
    configFile = open("config.json", "w")
    json_object = json.load(config)
    
    if (request.args.get("name") is not None):
        json_object["name"] = request.args.get("name")
    if (requests.arg.get("groupName") is not None):
        json_object["groupName"] = request.args.get("groupName")

    json.dump(json_object, configFile)
    configFile.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7000) #run app in debug mode on port 5000