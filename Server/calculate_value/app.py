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
EC2_IP = ""
EC2_PORT = ""

app = Flask(__name__)

def connectToDb():
    global LAT, LONG, EC2_IP, EC2_PORT
    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)
    configFile.close()

    EC2_IP = json_object['ec2_ip']
    EC2_PORT = json_object['ec2_port']


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
def calculateValueEC2():
    while(True):
        try: 
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
                dictControl["expire"] = time.mktime(myresult[0][0].timetuple())
                water_container_id = myresult[0][2]
            
                '''else:
                dictControl["water_container_volume"] = 0
                dictControl["expire"] = datetime(2020, 9, 30, 0, 0, 0, 0 ).timestamp()'''

                dictControl['groups_list'] = []

                cursor.execute("select AVG(L.temperatura), AVG(L.umidita), D.groupName, G.latCenter, G.longCenter, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type=\'sensor\' GROUP BY D.groupName, G.latCenter, G.longCenter")

                myresult = cursor.fetchall()

                for x in myresult:
                    key = str(x[2])             
                    if key != 'default':
                        keyList.append(key)
                        dictControl['groups_list'].append({'groupName':key, 'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[5], 'p2':x[6], 'p3':x[7], 'center': [x[3], x[4]]})
                
                json_data = json.dumps(dictControl)
                
                result = requests.post('http://' + EC2_IP + ':' +EC2_PORT + '/planning',  json=dictControl, timeout=5).json()

                print(result, flush=True)

                cursor.execute("INSERT into statistics (dayPeriod, moneySaved, waterSaved) VALUES (now(), " +  str(result['saved_money']) + "," + str(result['saved_water']) + ") ON DUPLICATE KEY UPDATE moneySaved ="+ str(result['saved_money']) + ", waterSaved ="+ str(result['saved_water'])) 
                db.commit()

                with open('dump/ec2value.json', 'w+') as f:
                    json.dump(result, f)

                # Ottengo la lista di tutti i sensori di controllo
                # Idealmente, ad ognuno di loro, per ogni gruppo, invio il valore ricevuto da EC2
                for x in result['groups_list']:
                    cursor.execute("SELECT id, ipAddress, ipPort from devices where groupName = \'" + x['groupName'] + "\' and type = \'control\'") 
                    myresult = cursor.fetchall()
                    for y in myresult:
                        control_water_unit = x['daily_water_unit'] / len(myresult)
                        if control_water_unit == 0:
                            try:
                                res = requests.get('http://' + str(y[1]) + ':' + str(y[2]) +'/getEC2Value?daily_water_unit=' + str(x['daily_water_unit']), timeout=3)
                                if res.text == "Ok":
                                    cursor.execute("UPDATE water_container SET currentValue = currentValue - "+str(control_water_unit) +" WHERE id = " + str(water_container_id))
                                    db.commit()
                            except requests.exceptions.RequestException as e:  # This is the correct syntax
                                print("To do...")
                cursor.close()
                db.close()
                return "Ok"
                time.sleep(1200)
        except (mysql.Error, requests.exceptions.RequestException) as err:
            print(str(err), flush=True)
            continue

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8070, threaded=True)
