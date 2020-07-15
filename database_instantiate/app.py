from flask import Flask
import requests
import mysql.connector as mysql

app = Flask(__name__)

@app.route('/')
def hello_world():
    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password"
    )

    databaseList = ""

    ## creating an instance of 'cursor' class which is used to execute the 'SQL' statements in 'Python'
    cursor = db.cursor()

    ## creating a databse called 'datacamp'
    ## 'execute()' method is used to compile a 'SQL' statement
    ## below statement is used to create tha 'datacamp' database
    cursor.execute("CREATE DATABASE IF NOT EXISTS datacamp")
    
    cursor.close()

    db.close()

    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password",
        database = "datacamp"
    )

    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
