import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request

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

@app.route('/editConfig', methods=['GET'])
def hello_world():

    db = connectToDb()

    cursor = db.cursor()

    if (request.args.get("type") == "name"):
        cursor.execute("UPDATE devices SET name=\'"+ str(request.args.get("new_value")) + "\' where id = " + str(request.args.get("id")))

    elif (request.args.get("type") == "groupName"):
        cursor.execute("select * FROM groups WHERE groupName = " + str(request.args.get("new_value")))
        row = cursor.fetchone()
        if row == None:
            return "Group name not present."

        cursor.execute("UPDATE devices SET groupName=\'"+ str(request.args.get("new_value")) +"\' where id = " + str(request.args.get("id")))

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/deleteDevice', methods=['GET'])
def hello_world123ssss():

    db = connectToDb()

    cursor = db.cursor()

    cursor.execute("DELETE from devices where id =" + str(request.args.get("id")))
    cursor.execute("DELETE from lectures where id =" + str(request.args.get("id")))

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/addGroup', methods=['GET'])
def addGroup():

    db = connectToDb()

    cursor = db.cursor()

    cursor.execute("INSERT INTO groups (groupName, parameter1, parameter2, parameter3) VALUES (\'" + str(request.args.get("groupName")) + "\'," + str(request.args.get("parameter1")) + ", " + str(request.args.get("parameter2")) + ", " + str(request.args.get("parameter3")) + ")")

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/getGroupsList', methods=['GET'])
def getGroupsList():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}

    cursor.execute("select * from groups")

    myresult = cursor.fetchall()

    for x in myresult:
        key = str(x[0]).replace(" ", "")
        if key not in dict:
            dict[key] = []
            dict[key].append({'groupName':x[0], 'parameter1':x[1], 'parameter2':x[2], 'parameter3':x[3]})
        else:
            dict[key].append({'groupName':x[0], 'parameter1':x[1], 'parameter2':x[2], 'parameter3':x[3]})


    jsonDict = {'list' : []}

    for i in dict:
        jsonDict['list'].append(dict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    print(json_data)

    return json_data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)
