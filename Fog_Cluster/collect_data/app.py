# -*- coding: utf-8 -*- 

from flask import Flask
import requests
import mysql.connector as mysql
from flask import request
import json
import logging
from pprint import pprint

app = Flask(__name__)

'''
The module is exposed outside the cluster. It receives data from the Proxy and insert it on the database.
'''

@app.route('/test')
def testRoute():
    return "Ok"

# Route to get data about lectures.
@app.route('/collectDataImage', methods=['POST'])
def collectDataImage():

    if request.method != 'POST':
        return "Wrong request method."

    elif  ('deviceId' or 'message') not in request.json:
        return "Wrong request."

    else:
        configFile = open("/config/config.json", "r")
        json_object = json.load(configFile)

        try:
            db = mysql.connect(
                host = json_object['host'],
                user = json_object['user'],
                passwd = json_object['passwd'],
                database = json_object['database']
            )

            cursor = db.cursor()

            # Select all the devices.
            cursor.execute("SELECT ipAddress, ipPort, groupName from devices WHERE id = " + str(request.json['deviceId']))

            queryResult = cursor.fetchall()

            for x in queryResult:

                # If present, update the devices status and insert the lecture on the db.
                cursor.execute("UPDATE devices SET alert = \'" + str(request.json['message']) + "\' where id = " + str(request.json['deviceId']))
                cursor.close()
                db.commit()
                request.json['deviceIp'] = x[0]
                request.json['devicePort'] = x[1]
                request.json['deviceGroup'] = x[2]
                res = requests.get('http://sendemailservice:8081/sendEmail', timeout=5, json=request.json)

            return "Ok"
        except mysql.Error as err:
            logging.info(str(err), flush=True)
            return str(err)

# Route to get data about lectures.
@app.route('/collectData', methods=['POST'])
def collectData():

    if request.method != 'POST':
        return "Wrong request method."

    elif  ('id' or 'temperature' or 'humidity' or 'type') not in request.json:
        return "Wrong request."

    else:
        configFile = open("/config/config.json", "r")
        json_object = json.load(configFile)

        try:
            db = mysql.connect(
                host = json_object['host'],
                user = json_object['user'],
                passwd = json_object['passwd'],
                database = json_object['database']
            )


            cursor = db.cursor()

            # Check if the devices is present on the database. Needed for the foreign key check.
            cursor.execute("select * FROM devices WHERE id = " + str(request.json['id']))
            
            # Check if the result exists
            row = cursor.fetchone()
            if row == None:
                return "Not present"

            # If present, update the devices status and insert the lecture on the db.
            cursor.execute("UPDATE devices SET status = 0, lastLecture=now() where id = " + str(request.json['id']))
            cursor.execute("INSERT INTO lectures (id, temperature, humidity, lastLecture) VALUES (" + str(request.json['id']) +"," + str(request.json['temperature']) + "," + str(request.json['humidity'])+",now())")
            cursor.close()
            db.commit()

            return "Ok"
        except mysql.Error as err:
            logging.info(str(err), flush=True)
            return str(err)

# Route to add a new device to the cluster.
@app.route('/newDevice', methods=['POST'])
def newDevice():

    if request.method != 'POST':
        return "Wrong request method."

    elif  ('id' or 'ipPort' or 'ipAddress' or 'name' or 'type') not in request.json:
        return "Wrong request."

    else:
        try:
            configFile = open("/config/config.json", "r")
            json_object = json.load(configFile)

            db = mysql.connect(
                host = json_object['host'],
                user = json_object['user'],
                passwd = json_object['passwd'],
                database = json_object['database']
            )

            cursor = db.cursor()

            # Insert the new device on the db.
            cursor.execute("INSERT INTO devices (id, ipAddress, ipPort, status, name, groupName, type) VALUES (" + str(request.json['id']) + ", \'" + str(request.json['ipAddress']) + "\'" + ", \'" + str(request.json['ipPort']) + "\',0,\'" + str(request.json['name']) + "\',\'default\',\'" + str(request.json['type']) + "\') ON DUPLICATE KEY UPDATE status = 0, ipAddress =\'" + str(request.json['ipAddress']) +"\', name =\'" + str(request.json["name"]) + "\', type =\'" + str(request.json["type"]) + "\'")

            cursor.close()
            db.commit()

            return "Ok"
        except mysql.Error as err:
            logging.info(str(err), flush=True)
            return str(err)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005, threaded=True)
