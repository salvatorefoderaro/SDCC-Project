import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request

'''
Modulo per la comunicazione tra la dashboard ed il database.
'''

app = Flask(__name__)

def connectToDb():
    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    return db

# Funzione che crea un json con le informazioni dei dispositivi presenti nella base di dati, e delle loro ultime attivitò.
@app.route('/calculateValueEC2', methods=['GET'])
def getDevicesStat():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}
    keyList = []
    dictControl = {}

    cursor.execute("select AVG(L.temperatura), AVG(L.umidita), D.groupName, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type=\'sensor\' GROUP BY D.groupName")

    myresult = cursor.fetchall()

    for x in myresult:
        key = str(x[2]).replace(" ", "")

        if key not in dictControl:
            dictControl[key] = []
            dictControl[key].append({'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[3], 'p2':str(x[4]), 'p3':x[5]})
        else:
            dictControl[key].append({'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[3], 'p2':str(x[4]), 'p3':x[5]})

    json_data = json.dumps(dictControl)
       
    cursor.close()

    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)
