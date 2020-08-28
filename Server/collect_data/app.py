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

    if request.method != 'POST':
        return "Wrong request method."

    elif  ('id' or 'temperatura' or 'umidita' or 'type') not in request.json:
        return "Wrong request."

    else:
        configFile = open("/config/config.json", "r")
        json_object = json.load(configFile)

        try:
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
            cursor.execute("INSERT INTO lectures (id, temperatura, umidita, lettura) VALUES (" + str(request.json['id']) +"," + str(request.json['temperatura']) + "," + str(request.json['umidita'])+",now())")
            cursor.close()
            db.commit()

            return "Ok"
        except mysql.Error as err:
            print(str(err), flush=True)
            return str(err)

@app.route('/newDevice', methods=['POST'])
def newDevice():

    if request.method != 'POST':
        return "Wrong request method."

    elif  ('id' or 'ipPort' or 'ipAddress' or 'name' or 'type') not in request.json:
        return "Wrong request."

    else:
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
        except mysql.Error as err:
            print(str(err), flush=True)
            return str(err)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005, threaded=True)
