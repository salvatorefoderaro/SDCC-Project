import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/getDeviceStat', methods=['GET'])
def getDevicesStat():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    dict = {}

    cursor.execute("select L.id, L.temperatura, L.umidita, L.lettura, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE lettura = (SELECT MAX(Lettura) FROM lectures WHERE id = L.id)")

    myresult = cursor.fetchall()

    for x in myresult:
        key = str(x[8]).replace(" ", "")
        if key not in dict:
            dict[key] = []
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})
        else:
            dict[key].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8])})
    
    jsonDict = {'list' : []}

    for i in dict:
        singleDict = {'groupName' : i, 'devicesList' : dict[i]}
        jsonDict['list'].append(singleDict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    return json_data

@app.route('/editConfig', methods=['GET'])
def hello_world():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    if (request.args.get("type") == "name"):
        cursor.execute("UPDATE devices SET name=\'"+ str(request.args.get("new_value")) + "\' where id = " + str(request.args.get("id")))

    elif (request.args.get("type") == "groupName"):
        cursor.execute("UPDATE devices SET groupName=\'"+ str(request.args.get("new_value")) +"\' where id = " + str(request.args.get("id")))

    cursor.close()
    db.commit()

    return "Ok"


@app.route('/deleteDevice', methods=['GET'])
def hello_world123ssss():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    cursor.execute("DELETE from devices where id =" + str(request.args.get("id")))
    cursor.execute("DELETE from lectures where id =" + str(request.args.get("id")))

    cursor.close()
    db.commit()

    return "Ok"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)
