import requests
import mysql.connector as mysql
import json
import logging

def checkStatus():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    cursor.execute("SELECT id, ipAddress, ipPort from devices")

    myresult = cursor.fetchall()

    for x in myresult:
        print(x)
        try:
            res = requests.get('http://' + str(json_object['proxy_ip']) + ':'+str(json_object['proxy_port']) +'/checkStatus?ipAddress='+str(x[1])+'&ipPort=' + str(x[2]), timeout=3)
            logging.info(res.text)
            if res.text != "Ok":
                cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
            else:
                cursor.execute("UPDATE devices SET status = 0 WHERE id ="+str(x[0])+"")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
                
    cursor.close()
    db.commit()

    return 0

if __name__ == '__main__':
    checkStatus()