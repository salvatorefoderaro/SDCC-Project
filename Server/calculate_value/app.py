#!/usr/bin/env python3

import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request
from datetime import datetime
import time

'''
Modulo per l'invio dei dati ad Amazon EC2 per il calcolo dei valori.
'''

LAT = 0
LONG = 0

app = Flask(__name__)

def connectToDb():
    global LAT, LONG
    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)
    configFile.close()

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    configFile = open("/config/cluster_config.json", "r")
    json_object = json.load(configFile)

    LAT = json_object["lat"]
    LONG = json_object["long"]

    return db

# Funzione che crea un json con le informazioni dei dispositivi presenti nella base di dati, e delle loro ultime attività.
@app.route('/calculateValueEC2', methods=['GET'])
def getDevicesStat():

    db = connectToDb()
    cursor = db.cursor()

    dict = {}
    keyList = []
    dictControl = {}
    water_container_id = 0
    rows_count = cursor.execute("SELECT endDate, currentValue, id FROM water_container WHERE now() <= endDate ORDER BY endDate DESC LIMIT 1")
    myresult = cursor.fetchall()
    if len(myresult) > 0:
        dictControl["water_container_volume"] = myresult[0][1]
        dictControl["expire"] = datetime(2020, 9, 30, 0, 0, 0, 0 ).timestamp()
        water_container_id = myresult[0][2]
    else:
        dictControl["water_container_volume"] = 0
        dictControl["expire"] = datetime(2020, 9, 30, 0, 0, 0, 0 ).timestamp()

    dictControl['groups_list'] = []

    cursor.execute("select AVG(L.temperatura), AVG(L.umidita), D.groupName, G.latCenter, G.longCenter, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type=\'sensor\' GROUP BY D.groupName, G.latCenter, G.longCenter")

    myresult = cursor.fetchall()

    for x in myresult:
        if x != 'default':
            key = str(x[2])
            keyList.append(key)
            dictControl['groups_list'].append({'groupName':key, 'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[5], 'p2':x[6], 'p3':x[7], 'center': [x[3], x[4]]})
    
    json_data = json.dumps(dictControl)
    print(json_data, flush=True)
    
    result = requests.post('http://192.168.1.106:5000/planning', json=dictControl, timeout=3).json() 

    # Ottengo la lista di tutti i sensori di controllo
    # Idealmente, ad ognuno di loro, per ogni gruppo, invio il valore ricevuto da EC2
    for x in result['groups_list']:
        cursor.execute("SELECT id, ipAddress, ipPort from devices where groupName = \'" + x['groupName'] + "\' and type = \'control\'") 
        myresult = cursor.fetchall()
        for y in myresult:
            try:
                res = requests.get('http://' + str(y[1]) + ':' + str(y[2]) +'/getEC2Value?daily_water_unit=' + str(x['daily_water_unit']), timeout=3)
                if res.text != "Ok":
                    print("To do...")
                else:
                    # Aggiornare la disponibilità del container
                    cursor.execute("UPDATE water_container SET currentValue = currentValue - "+str(x['daily_water_unit']) +" WHERE id = " + str(water_container_id))
                    db.commit()
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print("To do...")

    cursor.close()
    db.close()
    return "Ok"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8070, threaded=True)
