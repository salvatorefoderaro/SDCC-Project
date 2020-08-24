import requests
import mysql.connector as mysql
import json
import logging

'''
Modulo che si occupa di controllare lo stato di vita dei dispositivi, inviando una chiamata GET.
In caso di risposta, verrà aggiornato lo stato del dispositivo come attivo, altrimenti come non attivo.
'''

def checkDevicesStatus():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()

    # Vengono selezionati tutti i dispositivi presenti nel database
    cursor.execute("SELECT id, ipAddress, ipPort from devices")

    myresult = cursor.fetchall()

    # Per ogni singolo dispositivo...
    for x in myresult:
        # Effettuo una chiamata get e, in base alla risposta, aggiorno l stato del dispositivo
        try:
            res = requests.get('http://' + str(x[1]) + ':' + str(x[2]) +'/checkStatus', timeout=3)
            logging.info(res.text)
            if res.text != "Ok":
                cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
                res = requests.get('http://sendemailservice:8081/sendEmail?deviceId=' + str(x[0]) +'&deviceIp=' + str(x[1]) + '&devicePort=' + str(x[2] +'&type=error'), timeout=5)
            else:
                cursor.execute("UPDATE devices SET status = 0, lettura=now() WHERE id ="+str(x[0])+"")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
            res = requests.get('http://sendemailservice:8081/sendEmail?deviceId=' + str(x[0]) +'&deviceIp=' + str(x[1]) + '&devicePort=' + str(x[2]) + '&type=error', timeout=5)
                
    cursor.close()
    db.commit()

    return 0

if __name__ == '__main__':
    checkDevicesStatus()