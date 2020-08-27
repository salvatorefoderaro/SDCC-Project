import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request
from datetime import datetime

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
@app.route('/getDeviceStat', methods=['GET'])
def getDevicesStat():

    db = connectToDb()

    cursor = db.cursor()

    keyList = []

    dict = {}
    dictControl = {}
    dictWaterLevel = {}

    rows_count = cursor.execute("SELECT startDate, endDate, currentValue, totalValue FROM water_container WHERE now() <= endDate  ORDER BY endDate DESC LIMIT 1")
    myresult = cursor.fetchall()
    for x in myresult:
        dictWaterLevel['startDate'] = x[0].strftime("%d-%m-%Y")
        dictWaterLevel['endDate'] = x[1].strftime("%d-%m-%Y")
        dictWaterLevel['currentValue'] = x[2]
        dictWaterLevel['totalValue'] = x[3]
        dictWaterLevel['percentage'] = int(((x[3]-x[2])/x[3])*100)

    cursor.execute("select L.id, L.temperatura, L.umidita, L.lettura, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE L.lettura = (SELECT MAX(Lettura) FROM lectures WHERE id = L.id) and D.type='\sensor\'")

    myresult = cursor.fetchall()

    for x in myresult:
        if str(x[8]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[8])
        if key not in keyList:
            keyList.append(key)
        if key not in dict:
            dict[key] = []
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})
        else:
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})

    cursor.execute("select D.id, D.lettura, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM devices as D where type='\control\'")

    myresult = cursor.fetchall()

    for x in myresult:
        if str(x[6]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[6])

        if key not in keyList:
            keyList.append(key)
        if key not in dictControl:
            dictControl[key] = []
            dictControl[key].append({'id':x[0], 'lettura':str(x[1]), 'ipAddress':x[2], 'ipPort':x[3], 'status':x[4], 'name':x[5], 'groupName':str(x[6])})
        else:
            dictControl[key].append({'id':x[0], 'lettura':str(x[1]), 'ipAddress':x[2], 'ipPort':x[3], 'status':x[4], 'name':x[5], 'groupName':str(x[6])})

    jsonDict = {'list' : []}

    for i in keyList:
        if i in dict:
            devicesList = dict[i]
        else:
            devicesList = []
        if i in dictControl:
            devicesControlList = dictControl[i]
        else:
            devicesControlList = []
        singleDict = {'groupName' : i, 'devicesList' : devicesList, 'controlList' : devicesControlList}
        jsonDict['list'].append(singleDict)
    jsonDict['water_level'] = dictWaterLevel
    json_data = json.dumps(jsonDict)
       
    cursor.close()

    return json_data

# Funzione che modifica la configurazione di un siingolo dispositivo
@app.route('/editConfig', methods=['GET'])
def editConfig():

    db = connectToDb()

    cursor = db.cursor()

    # Se la richiesta è di tipo nome, oltre a modificare il record nel db contatto anche il dispositivo per l'aggiornamento
    # del file 'config.json'
    if (request.args.get("type") == "name"):
        cursor.execute("UPDATE devices SET name=\'"+ str(request.args.get("new_value")) + "\' where id = " + str(request.args.get("id")))
    # Se devo modificare il gruppo di appartenenza di un dispositivo, controllo prima che il gruppo esista
    # altrimenti fallirebbe il controllo sulla foreign key.
    elif (request.args.get("type") == "groupName"):
        cursor.execute("select * FROM devicesGroups WHERE groupName = \'" + str(request.args.get("new_value")) +"\'")
        row = cursor.fetchone()
        if row == None:
            return "Group name not present."
        cursor.execute("UPDATE devices SET groupName=\'"+ str(request.args.get("new_value")) +"\' where id = " + str(request.args.get("id")))

    cursor.close()
    db.commit()

    return "Ok"

# Funzione per l'eliminazione di un dispositivo
@app.route('/deleteDevice', methods=['GET'])
def deleteDevice():

    try:
        db = connectToDb()

        cursor = db.cursor()

        cursor.execute("DELETE from lectures where id = " + request.args.get("id"))
        cursor.execute("DELETE from water_level where id= " + request.args.get("id"))
        cursor.execute("DELETE from devices where id = " + request.args.get("id"))
        cursor.close()
        db.commit()
    except Exception as e:
        print(str(e))
    print("Finitooooo")
    return "Ok"

# Funzione per l'eliminazione di un dispositivo
@app.route('/deleteGroup', methods=['GET'])
def deleteGroup():

    db = connectToDb()

    cursor = db.cursor()

    cursor.execute("DELETE from devicesGroups where groupName =\'" + str(request.args.get("groupName")) + "\'")

    cursor.close()
    db.commit()

    return "Ok"

    # Funzione per l'eliminazione di un dispositivo
@app.route('/deleteContainer', methods=['GET'])
def deleteContainer():

    db = connectToDb()

    cursor = db.cursor()

    cursor.execute("DELETE from water_container where id =" + str(request.args.get("container_id")))

    cursor.close()
    db.commit()

    return "Ok"

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroup', methods=['GET'])
def addGroup():

    db = connectToDb()

    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) VALUES (\'" + str(request.args.get("groupName")) + "\'," + str(request.args.get("parameter1")) + ", " + str(request.args.get("parameter2")) + ", " + str(request.args.get("parameter3")) + ", " + str(request.args.get("latCenter")) + ", " + str(request.args.get("longCenter")) + ")")
    except Exception as e:
        print(str(e))

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/addWaterContainer', methods=['GET'])
def addWaterContainer():

    db = connectToDb()

    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO water_container (startDate, endDate, currentValue, totalValue) VALUES (\'" + str(request.args.get("start")) + "\',\'" + str(request.args.get("end")) + "\', " + str(request.args.get("water_value")) + ", " + str(request.args.get("water_value")) + ")")
    except Exception as e:
        print(str(e))

    cursor.close()
    db.commit()

    return "Ok"

# Funzione per l'ottenimento dei gruppi attualmente presenti.
@app.route('/getGroupsList', methods=['GET'])
def getGroupsList():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}

    cursor.execute("select * from devicesGroups")

    myresult = cursor.fetchall()

    jsonDict = {'list' : []}

    for x in myresult:
        dict = {}
        dict['groupName'] = x[0]
        dict['parameter1'] = x[1]
        dict['parameter2'] = x[2]
        dict['parameter3'] = x[3]
        jsonDict['list'].append(dict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    print(json_data)

    return json_data

# Funzione per l'ottenimento dei gruppi attualmente presenti.
@app.route('/getWaterList', methods=['GET'])
def getWaterList():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}

    rows_count = cursor.execute("SELECT startDate, endDate, currentValue, totalValue, id FROM water_container ORDER BY endDate DESC")

    myresult = cursor.fetchall()

    jsonDict = {'list' : []}

    for x in myresult:
        dict = {}
        dict['startDate'] = x[0].strftime("%d-%m-%Y")
        dict['endDate'] = x[1].strftime("%d-%m-%Y")
        dict['currentValue'] = x[2]
        dict['totalValue'] = x[3]
        dict['percentage'] = int(((x[3]-x[2])/x[3])*100)
        dict['container_id'] = x[4]
        jsonDict['list'].append(dict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    print(json_data)

    return json_data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)
