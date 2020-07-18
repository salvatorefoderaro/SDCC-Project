import requests
import mysql.connector as mysql

def checkStatus():

    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password",
        database = "datacamp"
    )

    cursor = db.cursor()

    cursor.execute("SELECT id, ipAddress from devices")

    myresult = cursor.fetchall()

    for x in myresult:
        try:
            res = requests.get('http://10.0.2.2:5000/checkStatus?ipAddress='+str(x[1]))
            cursor.execute("UPDATE devices SET status = 0 WHERE id ="+str(x[0])+"")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            cursor.execute("UPDATE devices SET status = 100 WHERE id ="+str(x[0])+"")
                
    cursor.close()

    db.commit()

    return 0

if __name__ == '__main__':
    checkStatus()