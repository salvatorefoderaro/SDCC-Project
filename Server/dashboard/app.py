# -*- coding: utf-8 -*- 

import requests
import json
import mysql.connector as mysql
from flask import Flask, render_template, send_file
from flask import request
import boto3
from botocore.client import Config

FOLDER_NAME = ""
SERVICE_IP = 0
SERVICE_PORT = 0

'''
Modulo per la dashboard di gestione dell'intero applicativo.
'''

app = Flask(__name__)

def readJson():
    global FOLDER_NAME, SERVICE_IP, SERVICE_PORT
    with open('/config/config.json') as config_file:
        data = json.load(config_file)
        SERVICE_IP = data['service_ip']
        SERVICE_PORT = data['service_port']
        config_file.close()
    with open('/config/cluster_config.json') as config_file:
        data = json.load(config_file)
        FOLDER_NAME = data['folder_name']
        config_file.close()

@app.route('/checkDevicesStatus', methods=['GET'])
def checkDevicesStatus():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    # Vengono selezionati tutti i dispositivi presenti nel database
    cursor.execute("SELECT id, ipAddress, ipPort from devices")

    myresult = cursor.fetchall()

    # Per ogni singolo dispositivo...
    for x in myresult:
        # Effettuo una chiamata get e, in base alla risposta, aggiorno l stato del dispositivo
        try:

            res = requests.get('http://' + str(x[1]) + ':' + str(x[2]) +'/checkStatus', timeout=3)
            if res.text != "Ok":
                cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
            else:
                cursor.execute("UPDATE devices SET status = 0 WHERE id ="+str(x[0])+"")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
                
    cursor.close()
    db.commit()
    
    try:
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nell'ottenimento della lista dei dispositivi.")
    return render_template('template_bootstrap.html', myString=data)

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroupLink', methods=['GET'])
def addGroupLink():

    return render_template('template_bootstrap_add_groups.html')

@app.route('/deleteGroup', methods=['GET'])
def deleteGroup():


    groupName = str(request.args.get("groupName"))

    try:
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/deleteGroup?groupName='+groupName, timeout=5)
        response123 = True
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))

    if res.text != "Ok":
        return render_template('error_template.html', responseMessage=str("Errore nell'eliminazione del gruppo."))

    data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    return render_template('template_bootstrap_groups.html', myString=data, response=response123)

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroup', methods=['GET'])
def addGroup():

    groupName = str(request.args.get("groupName"))
    parameter1 = str(request.args.get("parameter1"))
    parameter2 = str(request.args.get("parameter2"))
    parameter3 = str(request.args.get("parameter3"))

    response123 = False

    try:
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/addGroup?groupName='+groupName+'&parameter1=' + parameter1 + '&parameter2=' + parameter2 + '&parameter3=' + parameter3, timeout=5)
        response123 = True
        if res.text != "Ok":
            message = "Errore nell'aggiunta del gruppo."
            return render_template('error_template.html', responseMessage=message)
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))


    data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    return render_template('template_bootstrap_groups.html', myString=data, response=response123)

# Funzione per l'eliminazione di un dispositivo
@app.route('/deleteDevice', methods=['GET'])
def deleteDevice():

    new_value = str(request.args.get("new_value"))
    id = str(request.args.get("id"))
    type = str(request.args.get("type"))
    ip_address = str(request.args.get("ip_address"))
    port = str(request.args.get("port"))

    response123 = True

    try:
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/deleteDevice?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
        if res.text != "Ok":
            message = "Errore nell'eliminazione del dispositivo."
            return render_template('error_template.html', responseMessage = message)
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))

    data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()
    return render_template('template_bootstrap.html', myString=data, response=response123)

# Funzione per la modifica di un dispositivo
@app.route('/modifyDevice', methods=['GET'])
def modifyDevice():

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
            res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/editConfig?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
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
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage=str(e))
    return render_template('template_bootstrap.html', myString=data, response=True)

# Funzione per la visualizzazione della lista dei dispositivi
@app.route('/',)
def indexRoute():
     
    try:
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nell'ottenimento della lista dei dispositivi.")
    return render_template('template_bootstrap.html', myString=data)

@app.route('/getGroupsList',)
def getGroupsList():
     
    try:
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    except Exception as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nell'ottenimento della lista dei dispositivi.")
    return render_template('template_bootstrap_groups.html', myString=data)
    ##return render_template('template_bootstrap.html', myString=data)

@app.route('/downloadFile', methods=['GET'])
def downloadFile():

    ### information from configS3
    BUCKET_NAME = "sdcc-test-bucket"
    ACCESS_KEY_ID = "AKIA57G4V3XAZXYSWEYA"
    ACCESS_SECRET_KEY = "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"

    try:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4'))

        file_key = request.args.get("file_name")
        file_name_save = file_key.split("/")
        file_name_save = file_name_save[len(file_name_save)-1]
        s3.Bucket(BUCKET_NAME).download_file(file_key, file_name_save)
        return send_file(file_name_save, as_attachment=True)
    except requests.exceptions.RequestException as e:
        print(e)
        return render_template('error_template.html', responseMessage="Errore nel download del file da S3.")

@app.route('/getFileList')
def getFileList():

    ### information from configS3   
    ACCESS_KEY_ID = "AKIA57G4V3XAZXYSWEYA"
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
    
        for file in my_bucket.objects.filter(Prefix=FOLDER_NAME):
            file_key_list.append(file.key)

        return render_template('template_bootstrap_file.html', myString=file_key_list)
    except Exception as e:
        return render_template('error_template.html', responseMessage="Errore nell'ottenumento dei file da S3.")

if __name__ == '__main__':
    readJson()
    app.run(debug=True, host='0.0.0.0', port=8010)