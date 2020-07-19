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

    cursor.execute("UPDATE devices SET status = 0 where ID = " + request.json['id'])
    cursor.execute("INSERT INTO lectures (id, temperatura, umidita, lettura) VALUES (" + request.json['id'] +"," + request.json['temperatura'] + "," + request.json['umidita']+",now())")

    cursor.close()
    db.commit()

    return "Ok, inserted."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8005)
