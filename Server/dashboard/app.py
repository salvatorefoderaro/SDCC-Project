# -*- coding: utf-8 -*- 

import requests
import json
from flask import Flask, render_template, send_file
from flask import request
import boto3
from botocore.client import Config

'''
Modulo per la dashboard di gestione dell'intero applicativo.
'''

app = Flask(__name__)

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroupLink', methods=['GET'])
def addGroupLink():

    return render_template('template_bootstrap_add_groups.html')

@app.route('/deleteGroup', methods=['GET'])
def deleteGroup():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    groupName = str(request.args.get("groupName"))

    try:
        res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/deleteGroup?groupName='+groupName, timeout=5)
        response123 = True
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))

    if res.text != "Ok":
        return render_template('error_template.html', responseMessage=str("Errore nell'eliminazione del gruppo."))

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getGroupsList").json()
    return render_template('template_bootstrap_groups.html', myString=data, response=response123)

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroup', methods=['GET'])
def addGroup():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    groupName = str(request.args.get("groupName"))
    parameter1 = str(request.args.get("parameter1"))
    parameter2 = str(request.args.get("parameter2"))
    parameter3 = str(request.args.get("parameter3"))

    response123 = False

    try:
        res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/addGroup?groupName='+groupName+'&parameter1=' + parameter1 + '&parameter2=' + parameter2 + '&parameter3=' + parameter3, timeout=5)
        response123 = True
        if res.text != "Ok":
            message = "Errore nell'aggiunta del gruppo."
            return render_template('error_template.html', responseMessage=message)
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))


    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getGroupsList").json()
    return render_template('template_bootstrap_groups.html', myString=data, response=response123)

# Funzione per l'eliminazione di un dispositivo
@app.route('/deleteDevice', methods=['GET'])
def deleteDevice():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    new_value = str(request.args.get("new_value"))
    id = str(request.args.get("id"))
    type = str(request.args.get("type"))
    ip_address = str(request.args.get("ip_address"))
    port = str(request.args.get("port"))

    response123 = True


    try:
        res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/deleteDevice?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
        if res.text != "Ok":
            message = "Errore nell'eliminazione del dispositivo."
            return render_template('error_template.html', responseMessage = message)
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))

    data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    return render_template('template_bootstrap.html', myString=data, response=response123)

# Funzione per la modifica di un dispositivo
@app.route('/modifyDevice', methods=['GET'])
def modifyDevice():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    new_value = str(request.args.get("new_value"))
    id = str(request.args.get("id"))
    type = str(request.args.get("type"))
    ip_address = str(request.args.get("ip_address"))
    port = str(request.args.get("port"))
    

    if type == "lecture_interval":     
        try:
            res = requests.get('http://' + str(ip_address) + ':' +str(port) +'/editConfig?new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
            print(res.text)
            if (res.text != "Ok"):
                raise(Exception)
        except Exception as e:
            print(e)
            return render_template('error_template.html', responseMessage="Errore nella modifica del dispositivo.")
    
    else:
        if type =="name":
            try:
                res = requests.get('http://' + str(ip_address) + ':' +str(port) +'/editConfig?new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
                print(res.text)
                if (res.text != "Ok"):
                    raise(Exception)
            except Exception as e:
                print(e)
                return render_template('error_template.html', responseMessage="Errore nella modifica del dispositivo.")
        try:
            res = requests.get('http://' + json_object['service_ip'] + ':' + str(json_object['service_port']) +'/editConfig?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
            print(res.text)
            if (res.text == "Group name not present."):
                errorMessage = "Il gruppo indicato non è presente. Aggiungerlo prima."
                raise(Exception)
            elif (res.text != "Ok"):
                errorMessage = "Errore nella modifica del dispositivo."
                raise(Exception)
        except Exception as e:
            print(e)
            return render_template('error_template.html', responseMessage=errorMessage)

    try:
        data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))
    return render_template('template_bootstrap.html', myString=data, response=True)

# Funzione per la visualizzazione della lista dei dispositivi
@app.route('/',)
def indexRoute():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)
     
    try:
        data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getDeviceStat").json()
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nell'ottenimento della lista dei dispositivi.")
    return render_template('template_bootstrap.html', myString=data)

@app.route('/getGroupsList',)
def getGroupsList():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)
     
    try:
        data = requests.get("http://" + json_object['service_ip'] + ":" + str(json_object['service_port']) +"/getGroupsList").json()
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nell'ottenimento della lista dei dispositivi.")
    return render_template('template_bootstrap_groups.html', myString=data)
    ##return render_template('template_bootstrap.html', myString=data)

@app.route('/downloadFile', methods=['GET'])
def downloadFile():

    ### information from configS3
    BUCKET_NAME = "sdcc-test-bucket"

    try:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4'))

        file_key = request.args.get("file_name")
        s3.Bucket(BUCKET_NAME).download_file(file_key, file_key)
        return send_file(file_key, as_attachment=True)
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nel download del file da S3.")

@app.route('/getFileList')
def getFileList():

    ### information from configS3   
    ACCESS_KEY_ID =  "AKIA57G4V3XA7CWVE7C7"
    ACCESS_SECRET_KEY = "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"
    BUCKET_NAME = "sdcc-test-bucket"


    try:
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
    except Exception as e:
        return render_template('error_template.html', responseMessage="Errore nell'ottenumento dei file da S3.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8010)