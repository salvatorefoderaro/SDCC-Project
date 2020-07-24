from flask import Flask
import requests
import mysql.connector as mysql
from flask import request
import json

app = Flask(__name__)

@app.route('/collectData', methods=['POST'])
def hello_worldas():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    cursor.execute("select * FROM devices WHERE id = " + str(request.json['id']))
    
    row = cursor.fetchone()
    if row == None:
        return "Not present"

    cursor.execute("UPDATE devices SET status = 0 where id = " + str(request.json['id']))
    cursor.execute("INSERT INTO lectures (id, temperatura, umidita, lettura) VALUES (" + str(request.json['id']) +"," + str(request.json['temperatura']) + "," + str(request.json['umidita'])+",now())")

    cursor.close()
    db.commit()

    return "Ok"

@app.route('/newDevice', methods=['POST'])
def newDevice():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    cursor.execute("INSERT INTO  devices (id, ipAddress, ipPort, status, name, groupName) VALUES (" + str(request.json['id']) + ", \'" + str(request.json['ipAddress']) + "\'" + ", \'" + str(request.json['ipPort']) + "\',0,\'" + str(request.json['name']) + "\',\'" + str(request.json['groupName'])+"\') ON DUPLICATE KEY UPDATE status = 0, ipAddress =\'" + str(request.json['ipAddress']) +"\', name =\'" + str(request.json["name"]) + "\', groupName = \'" + str(request.json["groupName"])+" \'")

    cursor.close()
    db.commit()

    return "Ok"
  
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005, threaded=True)
