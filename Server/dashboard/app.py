import requests
import mysql.connector as mysql
import json
from flask import Flask, render_template
from flask import request

app = Flask(__name__)

@app.route('/deleteDevices')
def asd():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    new_value = str(request.args.get("new_value"))
    id = str(request.args.get("id"))
    type = str(request.args.get("type"))
    ip_address = str(request.args.get("ip_address"))
    port = str(request.args.get("port"))
    res = requests.get('http://' + str(json_object['proxy_ip']) + ':'+str(json_object['proxy_port']) +'/editConfig?id=' + id, timeout=3)

    response123 = False

    res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/deleteDevice?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)

    if res.content == "Ok, deleted.":
        response123 = True

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    return render_template('template_bootstrap.html', myString=data, response=response123)

@app.route('/modifyDevice')
def asd123():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    new_value = str(request.args.get("new_value"))
    id = str(request.args.get("id"))
    type = str(request.args.get("type"))
    ip_address = str(request.args.get("ip_address"))
    port = str(request.args.get("port"))
    res = requests.get('http://' + str(json_object['proxy_ip']) + ':'+str(json_object['proxy_port']) +'/editConfig?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type, timeout=3)

    response123 = False

    if res.text == "Modified":
        res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/editConfig?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
        response123 = True

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    return render_template('template_bootstrap.html', myString=data, response=response123)

@app.route('/getDeviceStat')
def jsonDict():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    print(data)
    return render_template('template_bootstrap.html', myString=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8010)