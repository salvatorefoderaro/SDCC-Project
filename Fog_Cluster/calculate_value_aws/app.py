#!/usr/bin/env python3

import requests
import mysql.connector as mysql
import json
import datetime
import time
import logging
import os

'''
The module prepare a JSON that is sent to AWS. AWS reply with a JSON containing infos about the daily water planning.

The data sent have this model:

{
    "water_container_volume": 5000,
    "expire": 0.0,
    "groups_list": [{
            "center": "[longitude,latitude]",
            "groupName": "default",
            "name": "default"
            "avgTemperatura": 21.49385959066843,
            "avgUmidita": 56.084210632009466,
            "p1": 0.0,
            "p2": 0.0,
            "p3": 0.0,
            "coordinates": [[[{}]]]
        }, ...
    ]
}

The data received, this:

{
    "today": "date",
    "warning": "",
    "saved_water": 0.0,
    "saved_money": 0.0,
    "groups_list": [{
            "center": "",
            "groupName": "",
            "ndvi_img_url": "",
            "ndvi_mean": "",
            "daily_water_unit": 0.0
        }...
    ]
}


'''

LAT = 0
LONG = 0
EC2_IP = ""
EC2_PORT = 0
FILE_LOCATION = 'dump/awsvalue.json'

def connectToDb():
    global LAT, LONG, EC2_IP, EC2_PORT
    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)
    configFile.close()

    EC2_IP = json_object['ec2_ip']
    EC2_PORT = json_object['ec2_port']

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    configFile = open("/config/cluster_config.json", "r")
    json_object = json.load(configFile)

    LAT = json_object["lat"]
    LONG = json_object["long"]

    return db

def calculateValueAWS():

    db = connectToDb()
    cursor = db.cursor()
    dictAWS = {}
    water_container_id = 0
    dict_groups = {}

    # Get info about the current water container,
    rows_count = cursor.execute("SELECT endDate, currentValue, id FROM water_container WHERE now() <= endDate ORDER BY endDate DESC LIMIT 1")
    queryResult = cursor.fetchall()

    # If there is a valida water container for the period
    if len(queryResult) > 0:
        # Read group coordinates

        configFile = open("/config/cluster_config.json", "r")
        json_object = json.load(configFile)
        configFile.close()


        for i in json_object['groups_list']:
            dict_groups[i['groupName']] = i['coordinates']

        dictAWS["water_container_volume"] = queryResult[0][1]
        dictAWS["expire"] = time.mktime(queryResult[0][0].timetuple())
        water_container_id = queryResult[0][2]

        dictAWS['groups_list'] = []

        # Select AVG value for each group that need to be sent.
        cursor.execute("select AVG(L.temperature), AVG(L.humidity), D.groupName, G.latCenter, G.longCenter, G.p1, G.p2, G.p3 FROM lectures as L JOIN devices as D on L.id = D.id JOIN devicesGroups as G on D.groupName = G.groupName WHERE D.type=\'monitor\' GROUP BY D.groupName, G.latCenter, G.longCenter")

        queryResult = cursor.fetchall()

        for x in queryResult:
            key = str(x[2])             
            if key != 'default':
                dictAWS['groups_list'].append({'groupName':key, 'name':key, 'avgTemperatura':x[0], 'avgUmidita':x[1], 'p1':x[5], 'p2':x[6], 'p3':x[7], 'coordinates': dict_groups[key], 'center': [x[3], x[4]] })
        
        # Dump the data to JSON.
        json_data = json.dumps(dictAWS)

        if dictAWS['groups_list'] != []:
        
            # Check if planning exist and get last edit/creation time
            if os.path.exists(FILE_LOCATION):
                editTime = os.path.getmtime(FILE_LOCATION)
            
            # If file doesn't exists (first run) contact AWS
            if (os.path.exists(FILE_LOCATION) is False):

                # Send the POST request.
                result = requests.post('http://' + EC2_IP + ':' +EC2_PORT + '/planning',  json=dictAWS, timeout=5).json()
                
                # Update the statistic table needed for the plot.
                cursor.execute("INSERT into statistics(dayPeriod, moneySaved, waterSaved) VALUES (now(), " +  str(result['saved_money']) + "," + str(result['saved_water']) + ") ON DUPLICATE KEY UPDATE moneySaved ="+ str(result['saved_money']) + ", waterSaved ="+ str(result['saved_water'])) 
                
                db.commit()
            
                # Write the JSON Result to file
                with open(FILE_LOCATION, 'w+') as f:
                    json.dump(result, f)
            # If different day (new planning required), contact AWS
            elif (datetime.datetime.now().date() != datetime.datetime.fromtimestamp(editTime).date()):
            
                # Delete the old file
                os.remove(FILE_LOCATION) 

                # Send the POST request.
                result = requests.post('http://' + EC2_IP + ':' +EC2_PORT + '/planning',  json=dictAWS, timeout=5).json()
                
                # Update the statistic table needed for the plot.
                cursor.execute("INSERT into statistics(dayPeriod, moneySaved, waterSaved) VALUES (now(), " +  str(result['saved_money']) + "," + str(result['saved_water']) + ") ON DUPLICATE KEY UPDATE moneySaved ="+ str(result['saved_money']) + ", waterSaved ="+ str(result['saved_water'])) 
                
                db.commit()
            
                # Write the JSON Result to file
                with open(FILE_LOCATION, 'w+') as f:
                    json.dump(result, f)
                


            planningFile = open(FILE_LOCATION, "r")
            planningJson = json.load(planningFile)

            # For each group, take the device of type 'execute' and send info about how much water have to be done to the field.
            for x in planningJson['groups_list']:
                cursor.execute("SELECT id, ipAddress, ipPort from devices where groupName = \'" + x['groupName'] + "\' and type = \'execute\'") 
                queryResult = cursor.fetchall()
                for y in queryResult:
                    
                    # If ther'are more than 1 control device, split the same quantity of water for each one
                    control_water_unit = x['daily_water_unit'] / len(queryResult)
                    
                    if control_water_unit != 0:
                        try:
                            res = requests.get('http://' + str(y[1]) + ':' + str(y[2]) +'/getEC2Value?daily_water_unit=' + str(x['daily_water_unit']), timeout=3)
                            
                            # If the device correctly received the infos, update the water container current value.
                            if res.text == "Ok":
                                cursor.execute("UPDATE water_container SET currentValue = currentValue - "+str(control_water_unit) +" WHERE id = " + str(water_container_id))
                                db.commit()

                        # If the device is not ready, continue
                        except requests.exceptions.RequestException as e:
                            continue
            
    cursor.close()
    db.close()
    return 0

if __name__ == '__main__':
    calculateValueAWS()