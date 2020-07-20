import requests
import mysql.connector as mysql
import json
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

@app.route('/getDeviceStat')
def jsonDict():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    print(data)
    return render_template('template_bootstrap.html', myString=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8010)