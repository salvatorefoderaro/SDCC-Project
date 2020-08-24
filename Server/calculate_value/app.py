import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request

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

    dictControl['lat'] = LAT
    dictControl['long'] = LONG
    dictControl['groups_list'] = []

    cursor.execute("select AVG(L.temperatura), AVG(L.umidita), D.groupName, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type=\'sensor\' GROUP BY D.groupName")

    myresult = cursor.fetchall()

    for x in myresult:
        key = str(x[2]).replace(" ", "")
        rows_count = cursor.execute("select W.water_L FROM water_level as W JOIN devices as D on W.id = D.id WHERE D.type=\'check_water\' and D.groupName=\'" + key + "\'")
        if rows_count > 0:
            myresult_nid = cursor.fetchall()
            water_level = myresult_nid[0][0]
        else:
            water_level = 0
        keyList.append(key)
        dictControl['groups_list'].append({'groupName':key, 'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[3], 'p2':str(x[4]), 'p3':x[5], 'water_level': water_level})
        json_data = json.dumps(dictControl)

    return json_data
    
    # Ottengo la lista di tutti i sensori di controllo
    # Idealmente, ad ognuno di loro, per ogni gruppo, invio il valore ricevuto da EC2
    dictControl = {}
    for x in keyList:
        cursor.execute("SELECT id, ipAddress, ipPort from devices where groupName = \'" + x + "\' and type = \'control\'") 
        myresult = cursor.fetchall()
        for y in myresult:
            if x not in dictControl:
                dictControl[x] = []
                dictControl[x].append([y[0], y[1], y[2]])
            else:
                dictControl[x].append([y[0], y[1], y[2]])

            try:

                res = requests.get('http://' + str(y[1]) + ':' + str(y[2]) +'/getEC2Value', timeout=3)
                if res.text != "Ok":
                    print("To do...")
                else:
                    print("To do...")
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print("To do...")


    cursor.close()
    db.close()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8070, threaded=True)
