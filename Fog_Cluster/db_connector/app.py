import requests
import mysql.connector as mysql
import json
from flask import Flask
from flask import request
from datetime import datetime
import logging

'''
Module to get infos from the db. The communication is made using JSON response.
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

# Get devices stat for display on the dashboard.
@app.route('/getDeviceStat', methods=['GET'])
def getDevicesStat():

    db = connectToDb()
    cursor = db.cursor()
    keyList = []
    dict = {}
    dictControl = {}
    dictWaterLevel = {}

    # Get info about the water_container.
    cursor.execute("SELECT startDate, endDate, currentValue, totalValue FROM water_container WHERE now() <= endDate  ORDER BY endDate DESC LIMIT 1")
    queryResult = cursor.fetchall()
    for x in queryResult:
        dictWaterLevel['startDate'] = x[0].strftime("%d-%m-%Y")
        dictWaterLevel['endDate'] = x[1].strftime("%d-%m-%Y")
        dictWaterLevel['currentValue'] = x[2]
        dictWaterLevel['totalValue'] = x[3]
        dictWaterLevel['percentage'] = int(((x[3]-x[2])/x[3])*100)
        dictWaterLevel['today'] = datetime.today().strftime('%d-%m-%Y')

    # Get info about the devices with type 'monitor'
    cursor.execute("select L.id, L.temperature, L.humidity, L.lastLecture, D.ipAddress, D.ipPort, D.status, D.name, D.groupName, D.alert FROM lectures as L JOIN devices as D on L.id = D.id WHERE L.lastLecture = (SELECT MAX(lastLecture) FROM lectures WHERE id = L.id) and D.type='\monitor\'")

    queryResult = cursor.fetchall()

    for x in queryResult:
        if str(x[8]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[8])
        if key not in keyList:
            keyList.append(key)
        if key not in dict:
            dict[key] = []
            dict[key].append({'id':x[0], 'temperature':x[1], 'humidity':x[2], 'lastLecture':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8]), 'alert':str(x[9])})
        else:
            dict[key].append({'id':x[0], 'temperature':x[1], 'humidity':x[2], 'lastLecture':str(x[3]), 'ipAddress':x[4], 'ipPort':x[5], 'status':x[6], 'name':x[7], 'groupName':str(x[8]), 'alert':str(x[9])})

    # Get info about the devices with type 'execute'
    cursor.execute("select D.id, D.lastLecture, D.ipAddress, D.ipPort, D.status, D.name, D.groupName FROM devices as D where type='\execute\'")

    queryResult = cursor.fetchall()

    for x in queryResult:
        if str(x[6]).replace(" ", "") == 'None':
            key = 'Default'
        else:
            key = str(x[6])

        if key not in keyList:
            keyList.append(key)
        if key not in dictControl:
            dictControl[key] = []
            dictControl[key].append({'id':x[0], 'lastLecture':str(x[1]), 'ipAddress':x[2], 'ipPort':x[3], 'status':x[4], 'name':x[5], 'groupName':str(x[6])})
        else:
            dictControl[key].append({'id':x[0], 'lastLecture':str(x[1]), 'ipAddress':x[2], 'ipPort':x[3], 'status':x[4], 'name':x[5], 'groupName':str(x[6])})

    # Build the json for sending.
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

# Edit the config on the database of a specific device.
@app.route('/editConfig', methods=['GET'])
def editConfig():

    try:
        db = connectToDb()
        cursor = db.cursor()

        # Check the type of the edit.
        if (request.args.get("type") == "name"):
            cursor.execute("UPDATE devices SET name=\'"+ str(request.args.get("new_value")) + "\' where id = " + str(request.args.get("id")))


        elif (request.args.get("type") == "groupName"):
            # Check if group exist.
            cursor.execute("select * FROM devicesGroups WHERE groupName = \'" + str(request.args.get("new_value")) +"\'")
            row = cursor.fetchone()
            
            # Check if the result exists
            if row == None:
                return "Group name not present."

            cursor.execute("UPDATE devices SET groupName=\'"+ str(request.args.get("new_value")) +"\' where id = " + str(request.args.get("id")))

        cursor.close()
        db.commit()
        return "Ok"

    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Delete a device from the database.
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
        return "Ok"

    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Delete a group from the database.
@app.route('/deleteGroup', methods=['GET'])
def deleteGroup():

    try:
        db = connectToDb()

        cursor = db.cursor()

        cursor.execute("DELETE from devicesGroups where groupName =\'" + str(request.args.get("groupName")) + "\'")

        cursor.close()
        db.commit()

        return "Ok"

    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Delete a water container.
@app.route('/deleteContainer', methods=['GET'])
def deleteContainer():
    try: 
        db = connectToDb()

        cursor = db.cursor()

        cursor.execute("DELETE from water_container where id =" + str(request.args.get("container_id")))

        cursor.close()
        db.commit()

        return "Ok"
    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Add a group.
@app.route('/addGroup', methods=['GET'])
def addGroup():

    try: 
        db = connectToDb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO devicesGroups (groupName) VALUES (\'" + str(request.args.get("groupName")) + "\')")
        cursor.close()
        db.commit()
        return "Ok"

    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Add a water container.
@app.route('/addWaterContainer', methods=['GET'])
def addWaterContainer():

    try: 
        db = connectToDb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO water_container (startDate, endDate, currentValue, totalValue) VALUES (\'" + str(request.args.get("start")) + "\',\'" + str(request.args.get("end")) + "\', " + str(request.args.get("water_value")) + ", " + str(request.args.get("water_value")) + ")")
        cursor.close()
        db.commit()
        return "Ok"
    except mysql.Error as err:
        logging.info(str(err), flush=True)
        return str(err)

# Get stat for plotting.
@app.route('/getStat', methods=['GET'])
def getStat():

    db = connectToDb()
    cursor = db.cursor()
    dict = {}
    cursor.execute("select * from statistics")
    queryResult = cursor.fetchall()
    label = []
    data1 = []
    data2 = []
    for x in queryResult:
        label.append(x[0].strftime("%d-%m-%Y"))
        data1.append(x[1])
        data2.append(x[2])
    dict['label'] = label
    dict['data1'] = data1
    dict['data2'] = data2
    json_data = json.dumps(dict)
       
    cursor.close()
    return json_data

# Get groups list.
@app.route('/getGroupsList', methods=['GET'])
def getGroupsList():

    db = connectToDb()
    cursor = db.cursor()
    dict = {}
    cursor.execute("select * from devicesGroups")
    queryResult = cursor.fetchall()
    jsonDict = {'list' : []}

    for x in queryResult:
        dict = {}
        dict['groupName'] = x[0]
        jsonDict['list'].append(dict)

    json_data = json.dumps(jsonDict)
       
    cursor.close()
    return json_data

# Get water container list.
@app.route('/getWaterList', methods=['GET'])
def getWaterList():

    db = connectToDb()

    cursor = db.cursor()

    dict = {}

    cursor.execute("SELECT startDate, endDate, currentValue, totalValue, id FROM water_container ORDER BY endDate DESC")

    queryResult = cursor.fetchall()

    jsonDict = {'list' : []}

    for x in queryResult:
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

    return json_data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8020, threaded=True)