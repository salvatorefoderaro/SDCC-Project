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

    cursor.execute("SELECT device.id, device.name, device.groupName, device.status, lecture.temperatura, lecture.umidita, lecture.lettura FROM devices as device JOIN lectures AS lecture on device.id = lecture.id ORDER BY lecture.lettura DESC LIMIT 1")

    myresult = cursor.fetchall()

    for x in myresult:
        print(x)
        if x[4] not in dict:
            dict[x[4]] = []
            dict[x[4]].append({'id':x[0], 'name':x[1], 'groupName':x[2], 'status':x[3], 'temperatura':x[4], 'umidita':x[5], 'data':str(x[6])})
        else:
            dict[x[4]].append({'id':x[0], 'name':x[1], 'groupName':x[2], 'status':x[3], 'temperatura':x[4], 'umidita':x[5], 'data':str(x[6])})

    jsonDict = {'list' : []}

    for i in dict:
        singleDict = {'groupName' : i, 'devicesList' : dict[i]}
        jsonDict['list'].append(singleDict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020)
