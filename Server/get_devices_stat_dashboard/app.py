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

    cursor.execute("select L.id, L.temperatura, L.umidita, L.lettura, D.ipAddress, D.status, D.name, D.groupName FROM lectures as L JOIN devices as D on L.id = D.id WHERE lettura = (SELECT MAX(Lettura) FROM lectures WHERE id = L.id)")

    myresult = cursor.fetchall()

    for x in myresult:
        if x[6] not in dict:
            dict[x[6]] = []
            dict[x[6]].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'status':x[5], 'name':x[6], 'groupName':str(x[7])})
        else:
            dict[x[6]].append({'id':x[0], 'temperatura':x[1], 'umidita':x[2], 'lettura':str(x[3]), 'ipAddress':x[4], 'status':x[5], 'name':x[6], 'groupName':str(x[7])})

    jsonDict = {'list' : []}

    for i in dict:
        singleDict = {'groupName' : i, 'devicesList' : dict[i]}
        jsonDict['list'].append(singleDict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()

    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020)
