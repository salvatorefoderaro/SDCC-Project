# -*- coding: utf-8 -*- 

from flask import Flask
import requests
import mysql.connector as mysql
from flask import request
import json

app = Flask(__name__)

'''
Modulo che si occupa di regisrare i nuovi dispositivi e le registrazioni prodotte nel sengolo dai singoli dispositivi.
'''

@app.route('/collectData', methods=['POST'])
def collectData():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    # Controllo se il dispositivo è attualmente presente nella base dati
    cursor.execute("select * FROM devices WHERE id = " + str(request.json['id']))
    
    row = cursor.fetchone()
    if row == None:
        return "Not present"

    cursor.execute("UPDATE devices SET status = 0, lettura=now() where id = " + str(request.json['id']))
    if request.json['type'] == 'sensor':
        cursor.execute("INSERT INTO lectures (id, temperatura, umidita, lettura) VALUES (" + str(request.json['id']) +"," + str(request.json['temperatura']) + "," + str(request.json['umidita'])+",now())")

    elif request.json['type'] == 'check_water':
        cursor.execute("INSERT INTO water_level (id, water_L, lettura) VALUES (" + str(request.json['id']) +"," + str(request.json['water_level']) + ",now()) ON DUPLICATE KEY UPDATE water_L =\'" + str(request.json['water_level']) +"\', lettura = now()")

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/newDevice', methods=['POST'])
def newDevice():

    try:

        configFile = open("/config/config.json", "r")
        json_object = json.load(configFile)

        db = mysql.connect(
            host = json_object['host'],
            user = json_object['user'],
            passwd = json_object['passwd'],
            database = json_object['database']
        )

        cursor = db.cursor()

        # Inserisco il dispositivo nel database
        cursor.execute("INSERT INTO devices (id, ipAddress, ipPort, status, name, groupName, type) VALUES (" + str(request.json['id']) + ", \'" + str(request.json['ipAddress']) + "\'" + ", \'" + str(request.json['ipPort']) + "\',0,\'" + str(request.json['name']) + "\',\'default\',\'" + str(request.json['type']) + "\') ON DUPLICATE KEY UPDATE status = 0, ipAddress =\'" + str(request.json['ipAddress']) +"\', name =\'" + str(request.json["name"]) + "\', type =\'" + str(request.json["type"]) + "\'")

        cursor.close()
        db.commit()

        return "Ok"
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005, threaded=True)
