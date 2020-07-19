import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/getDeviceStat', methods=['GET'])
def getDevicesStat():

    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password",
        database = "datacamp"
    )

    cursor = db.cursor()

    dict = {}

    cursor.execute("SELECT device.id, device.name, device.groupName, device.status, lecture.temperatura, lecture.umidita, lecture.lettura FROM devices as device JOIN lectures AS lecture on device.id = lecture.id WHERE device.id = (SELECT MAX(lettura) FROM lectures WHERE lectures.id = device.id")

    myresult = cursor.fetchall()

    for x in myresult:
        if x[4] not in dict:
            dict[x[4]] = []
            dict[x[4]].append({'id':x[0], 'ip':x[1], 'status':x[2], 'name':x[3]})
        else:
            dict[x[4]].append({'id':x[0], 'ip':x[1], 'status':x[2], 'name':x[3]})

    jsonDict = {'list':[]}

    for i in dict:
        singleDict = {'groupName':i, 'devicesList':dict[i]}
        jsonDict['list'].append(singleDict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020)
