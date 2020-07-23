import requests
import mysql.connector as mysql
import json
from flask import Flask, render_template
from flask import request
import boto3
from botocore.client import Config
from flask import send_file

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
def jsonDictasddd():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    print(data)
    return render_template('template_bootstrap.html', myString=data)

@app.route('/downloadFile')
def jsonDictDownload():

    ### information from configS3
    BUCKET_NAME = "sdcc-test-bucket"

    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4'))

    file_key = request.args.get("file_name")
    s3.Bucket(BUCKET_NAME).download_file(file_key, file_key)
    return send_file(file_key, as_attachment=True)


@app.route('/getFileList')
def jsonDict():

    ### information from configS3
    BUCKET_NAME = "sdcc-test-bucket"

    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4'))
    
    file_key_list = []
    my_bucket = s3.Bucket(BUCKET_NAME)
    
    for file in my_bucket.objects.all():
        file_key_list.append(file.key)

    return render_template('template_bootstrap_file.html', myString=file_key_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8010)