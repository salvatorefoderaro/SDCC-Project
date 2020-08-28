# -*- coding: utf-8 -*- 

import requests
import json
import mysql.connector as mysql
from flask import Flask, render_template, send_file
from flask import request
import boto3
from botocore.client import Config
import botocore.exceptions
import os.path
from datetime import datetime


FOLDER_NAME = ""
SERVICE_IP = 0
SERVICE_PORT = 0
EC2_IP = ""
EC2_PORT = ""
CONTAINER_HISTORY_ERROR = "Errore nell'ottenimento dello storico dei container."
METEO_INFO_ERROR = "Errore nell'ottenimento delle informazioni meteo."
DEVICES_LIST_ERROR = "Errore nell'ottenimento della lista dei dispositivi."
ADD_GROUP_ERROR = "Errore nell'aggiunta del gruppo."
DELETE_GROUP_ERROR = "Errore nell'eliminazione del gruppo."
ERROR_DELETE_CONTAINER = "Errore nell'eliminazione del container."
ERROR_ADD_CONTAINER = "Errore nell'aggiunta del conteiner."
ERROR_DELETE_DEVICE = "Errore nell'eliminazione del dispositivo."
ERROR_EDIT_DEVICE = "Errore nella modifica del dispositivo."
GROUP_LIST_ERROR = "Errore nell'ottenimento della lista dei gruppi."
ERROR_GET_S3_FILE = "Errore nell'ottenimento della lista dei file."
ERROR_DOWNLOAD_S3_FILE = "Errore nel download dei file da S3."

BUCKET_NAME = "sdcc-test-bucket"
ACCESS_KEY_ID = "AKIA57G4V3XAXOJRI7HS"
ACCESS_SECRET_KEY = "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"


'''
Modulo per la dashboard di gestione dell'intero applicativo.
'''

app = Flask(__name__)

def readJson():
    global FOLDER_NAME, SERVICE_IP, SERVICE_PORT, EC2_IP, EC2_PORT
    with open('/config/config.json') as config_file:
        data = json.load(config_file)
        SERVICE_IP = data['service_ip']
        SERVICE_PORT = data['service_port']
        EC2_IP = data['ec2_ip']
        EC2_PORT = data['ec2_port']
        config_file.close()
    with open('/config/cluster_config.json') as config_file:
        data = json.load(config_file)
        FOLDER_NAME = data['folder_name']
        config_file.close()

# Make a manual check of the status of the device
@app.route('/checkDevicesStatus', methods=['GET'])
def checkDevicesStatus():

    try:
        errorMessage = METEO_INFO_ERROR
        data_meteo = requests.get('http://' + EC2_IP + ':' +EC2_PORT + '/weather_forecasts', timeout=5).json()

        if os.path.isfile('dump/awsvalue.json'): 
            dictec2 = {}
            with open('dump/awsvalue.json') as config_file:
                data_ec2 = json.load(config_file)
                config_file.close()

            for i in range(0, len(data_ec2['groups_list'])):
                dictec2[data_ec2['groups_list'][i]['groupName']] = round(data_ec2['groups_list'][i]['ndvi_mean'], 4)
        else:
            dictec2 = None

        errorMessage = DEVICES_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()

    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap.html', dataToPlot=data, weather=data_meteo, ndvi=dictec2)

# Route to render the page
@app.route('/addGroupLink', methods=['GET'])
def addGroupLink():
    return render_template('template_bootstrap_add_groups.html')

# Route to render the page
@app.route('/addWaterContainerLink', methods=['GET'])
def addWaterContainerLink():
    return render_template('template_bootstrap_add_water_container.html')

# Route to add a water container
@app.route('/deleteWaterContainer', methods=['GET'])
def deleteWaterContainer():

    container_id = str(request.args.get("container_id"))

    try:
        errorMessage = ERROR_DELETE_CONTAINER
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/deleteContainer?container_id='+container_id, timeout=5)

        if res.text != "Ok":
            raise(requests.exceptions.RequestException)
        
        errorMessage = CONTAINER_HISTORY_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getWaterList").json()

    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap_groups_water_container.html', dataToPlot=data,response=True)

# Route to delete a group
@app.route('/deleteGroup', methods=['GET'])
def deleteGroup():

    groupName = str(request.args.get("groupName"))
    try:
        errorMessage = DELETE_GROUP_ERROR
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/deleteGroup?groupName='+groupName, timeout=5)

        if res.text != "Ok":
            raise(requests.exceptions.RequestException)
        
        errorMessage = GROUP_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()

    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap_groups.html', dataToPlot=data, response=True)

# Route to add a group
@app.route('/addGroup', methods=['GET'])
def addGroup():

    groupName = str(request.args.get("groupName"))
    parameter1 = str(request.args.get("parameter1"))
    parameter2 = str(request.args.get("parameter2"))
    parameter3 = str(request.args.get("parameter3"))
    latCenter = str(request.args.get("latCenter"))
    longCenter = str(request.args.get("longCenter"))

    try:
        errorMessage = ADD_GROUP_ERROR
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/addGroup?groupName='+groupName+'&parameter1=' + parameter1 + '&parameter2=' + parameter2 + '&parameter3=' + parameter3 + '&longCenter=' + longCenter + '&latCenter=' + latCenter, timeout=5)
        if res.text != "Ok":
            raise(requests.exceptions.RequestException)        

        errorMessage = GROUP_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)

    return render_template('template_bootstrap_groups.html', dataToPlot=data, response=True)

# Route to add a water container
@app.route('/addWaterContainer', methods=['GET'])
def addWaterContainer():

    start = str(request.args.get("start"))
    end = str(request.args.get("end"))
    water_value = str(request.args.get("water_value"))

    try:
        errorMessage = ERROR_ADD_CONTAINER
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/addWaterContainer?start='+start+'&end=' + end + '&water_value=' + water_value, timeout=5)
        if res.text != "Ok":
            raise(requests.exceptions.RequestException)

        errorMessage = CONTAINER_HISTORY_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getWaterList").json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)

    return render_template('template_bootstrap_groups_water_container.html', dataToPlot=data, response=True)

# Route to get the stat needed for the chart
@app.route('/getStat', methods=['GET'])
def getStat():

    try:
        errorMessage = ERROR_ADD_CONTAINER
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/getStat', timeout=5).json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap_stat.html', dataToPlot=res)

# Route to delete a device
@app.route('/deleteDevice', methods=['GET'])
def deleteDevice():

    try:
        if os.path.isfile('dump/awsvalue.json'): 
            dictec2 = {}
            with open('dump/awsvalue.json') as config_file:
                data_ec2 = json.load(config_file)
                config_file.close()

            for i in range(0, len(data_ec2['groups_list'])):
                dictec2[data_ec2['groups_list'][i]['groupName']] = round(data_ec2['groups_list'][i]['ndvi_mean'], 4)
        else:
            dictec2 = None

        new_value = str(request.args.get("new_value"))
        id = str(request.args.get("id"))
        type = str(request.args.get("type"))
        ip_address = str(request.args.get("ip_address"))
        port = str(request.args.get("port"))

        errorMessage = ERROR_DELETE_DEVICE
        res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/deleteDevice?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
        if res.text != "Ok":
            raise(requests.exceptions.RequestException)

        errorMessage = METEO_INFO_ERROR
        data_meteo = requests.get('http://' + EC2_IP + ':' +EC2_PORT + '/weather_forecasts', timeout=5).json()

        errorMessage = GROUP_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap.html', dataToPlot=data, weather=data_meteo, ndvi=dictec2, response=True)

# Route to modify a device
@app.route('/modifyDevice', methods=['GET'])
def modifyDevice():

    try: 
        if os.path.isfile('dump/awsvalue.json'): 
            dictec2 = {}
            with open('dump/awsvalue.json') as config_file:
                data_ec2 = json.load(config_file)
                config_file.close()

            for i in range(0, len(data_ec2['groups_list'])):
                dictec2[data_ec2['groups_list'][i]['groupName']] = round(data_ec2['groups_list'][i]['ndvi_mean'], 4)
        else:
            dictec2 = None

        new_value = str(request.args.get("new_value"))
        id = str(request.args.get("id"))
        type = str(request.args.get("type"))
        ip_address = str(request.args.get("ip_address"))
        port = str(request.args.get("port"))
        
        if type == "lecture_interval" or type == "group_name":     
            errorMessage = ERROR_EDIT_DEVICE
            res = requests.get('http://' + str(ip_address) + ':' +str(port) +'/editConfig?new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
            if (res.text != "Ok"):
                raise(requests.exceptions.RequestException)
        
        else:
            if type =="name":
                errorMessage = ERROR_EDIT_DEVICE
                res = requests.get('http://' + str(ip_address) + ':' +str(port) +'/editConfig?new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
                if (res.text != "Ok"):
                    raise(requests.exceptions.RequestException)
            
            errorMessage = "Errore nella modifica del dispositivo."
            res = requests.get('http://' + SERVICE_IP + ':' + str(SERVICE_PORT) +'/editConfig?ipAddress='+ip_address+'&ipPort=' + port + '&new_value=' + new_value + '&type=' + type + '&id=' + id, timeout=3)
            if (res.text == "Group name not present."):
                errorMessage = "Il gruppo indicato non è presente. Aggiungerlo prima."
                raise(requests.exceptions.RequestException)
            elif (res.text != "Ok"):
                errorMessage = "Errore nella modifica del dispositivo."
                raise(requests.exceptions.RequestException)

        errorMessage = METEO_INFO_ERROR
        data_meteo = requests.get('http://' + EC2_IP + ':' +EC2_PORT + '/weather_forecasts', timeout=5).json()

        errorMessage = DEVICES_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat").json()
        
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)

    return render_template('template_bootstrap.html', dataToPlot=data, weather=data_meteo, ndvi=dictec2, response=True)

# Route for the index page
@app.route('/')
def indexRoute():

    try:
        errorMessage = METEO_INFO_ERROR
        data_meteo = requests.get('http://' + EC2_IP + ':' +EC2_PORT + '/weather_forecasts', timeout=5).json()

        if os.path.isfile('dump/awsvalue.json'): 
            dictec2 = {}
            with open('dump/awsvalue.json') as config_file:
                data_ec2 = json.load(config_file)
                config_file.close()

            for i in range(0, len(data_ec2['groups_list'])):
                dictec2[data_ec2['groups_list'][i]['groupName']] = round(data_ec2['groups_list'][i]['ndvi_mean'], 4)
                dictec2['warning'] = data_ec2['warning']
        else:
            dictec2 = None
        
        errorMessage = DEVICES_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getDeviceStat", timeout=5).json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap.html', dataToPlot=data, weather=data_meteo, ndvi=dictec2)

# Route to get the list of groups
@app.route('/getGroupsList',)
def getGroupsList():
     
    try:
        errorMessage = GROUP_LIST_ERROR
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getGroupsList").json()
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap_groups.html', dataToPlot=data)

# Route to get the list of water container
@app.route('/getWaterList',)
def getWaterList():
     
    try:
        data = requests.get("http://" + SERVICE_IP + ":" + str(SERVICE_PORT) +"/getWaterList").json()
        errorMessage = GROUP_LIST_ERROR
    except requests.exceptions.RequestException as e:
        return render_template('error_template.html', responseMessage=errorMessage)
    return render_template('template_bootstrap_groups_water_container.html', dataToPlot=data)

# Route to download a file
@app.route('/downloadFile', methods=['GET'])
def downloadFile():

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

    except Exception as e:
        print(str(e), flush=True)
        return render_template('error_template.html', responseMessage=ERROR_DOWNLOAD_S3_FILE)

# Route to get the file list from S3
@app.route('/getFileList')
def getFileList():

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
        return render_template('template_bootstrap_file.html', dataToPlot=file_key_list)
    except Exception as e:
        print(str(e), flush=True)
        return render_template('error_template.html', responseMessage=ERROR_GET_S3_FILE)

if __name__ == '__main__':
    readJson()
    app.run(debug=True, host='0.0.0.0', port=8010)