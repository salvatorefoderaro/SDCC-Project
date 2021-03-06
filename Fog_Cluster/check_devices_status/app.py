import requests
import mysql.connector as mysql
import json
import logging

'''
The module contact each device, to check the status and update it on the dabase. This is needed for the dashboard.
'''

# Check the status of the cluster devices.
def checkDevicesStatus():

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
        cursor.execute("SELECT id, ipAddress, ipPort, groupName from devices")

        queryResult = cursor.fetchall()

        for x in queryResult:

            # For each devices, try to contact and check for response
            try:
                res = requests.get('http://' + str(x[1]) + ':' + str(x[2]) +'/checkStatus', timeout=3)
                logging.info(res.text)

                if res.text == "Ok":
                    cursor.execute("UPDATE devices SET status = 0, lastLecture=now() WHERE id ="+str(x[0])+"")
                else:
                    raise(requests.exceptions.RequestException)
            except requests.exceptions.RequestException as e:

                # Set the device like 'non reachable' and send an e-mail to notify this event.
                cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")

                dictToSend = {'deviceId': str(x[0]), 'deviceIp': str(x[1]), 'devicePort': str(x[2]), 'deviceGroup':str(x[3]), 'type':'error'}
                res = requests.get('http://sendemailservice:8081/sendEmail', json = dictToSend, timeout=10)
                    
        cursor.close()
        db.commit()

        return 0
    except mysql.Error as err:
        logging.info(str(err))

if __name__ == '__main__':
    checkDevicesStatus()