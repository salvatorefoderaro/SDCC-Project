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
@app.route('/getDeviceStat', methods=['GET'])
def getDevicesStat():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}
    keyList = []
    dictControl = {}


    cursor.execute("select L.id, L.temperatura, L.umidita, L.lettura, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE lettura = (SELECT MAX(Lettura) FROM lectures WHERE id = L.id) and D.type='\sensor\'")

    myresult = cursor.fetchall()

    for x in myresult:
        if str(x[8]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[8]).replace(" ", "")
        if key not in keyList:
            keyList.append(key)
        if key not in dict:
            dict[key] = []
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})
        else:
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})

    cursor.execute("select L.id, L.temperatura, L.umidita, L.lettura, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE lettura = (SELECT MAX(Lettura) FROM lectures WHERE id = L.id) and D.type='\control\'")

    myresult = cursor.fetchall()

    for x in myresult:
        if str(x[8]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[8]).replace(" ", "")

        if key not in keyList:
            keyList.append(key)
        if key not in dictControl:
            dictControl[key] = []
            dictControl[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})
        else:
            dictControl[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})

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

    db = connectToDb()

    cursor = db.cursor()

    cursor.execute("DELETE from devices where id =" + str(request.args.get("id")))
    cursor.execute("DELETE from lectures where id =" + str(request.args.get("id")))

    cursor.close()
    db.commit()

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

# Funzione per l'aggiunta di un nuovo gruppo
@app.route('/addGroup', methods=['GET'])
def addGroup():

    db = connectToDb()

    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO devicesGroups(groupName, p1, p2, p3) VALUES (\'" + str(request.args.get("groupName")) + "\'," + str(request.args.get("parameter1")) + ", " + str(request.args.get("parameter2")) + ", " + str(request.args.get("parameter3")) + ")")
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)
