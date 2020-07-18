from flask import Flask
import requests
import mysql.connector as mysql
from flask import request

app = Flask(__name__)

@app.route('/collectData', methods=['POST'])
def hello_world():

    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password",
        database = "datacamp"
    )

    cursor = db.cursor()

    cursor.execute("INSERT INTO devices (id, ipAddress, status) VALUES (" + request.json['id'] +",\'" + request.json['ip'] + "\'," + request.json['status']+") ON DUPLICATE KEY UPDATE ipAddres = " + request.json['ip'] + ", status = " + request.json['status'])

    cursor.close()
    db.commit()

    return "Ok, inserted."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005)
