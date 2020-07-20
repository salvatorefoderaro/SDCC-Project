import requests
import mysql.connector as mysql
import json

def checkStatus():

    configFile = open("config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    cursor.execute("SELECT id, ipAddress from devices")

    myresult = cursor.fetchall()

    for x in myresult:
        try:
            res = requests.get('http://' + json_object['proxy_ip'] + ':'+5000 +'/checkStatus?ipAddress='+str(x[1]), timeout=3)
            cursor.execute("UPDATE devices SET status = 0 WHERE id ="+str(x[0])+"")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
                
    cursor.close()
    db.commit()

    return 0

if __name__ == '__main__':
    checkStatus()