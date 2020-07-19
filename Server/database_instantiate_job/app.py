from flask import Flask
import requests
import mysql.connector as mysql

def hello_world():

    configFile = open("config.json", "w")
    json_object = json.load(config)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd']
    )

    ## creating an instance of 'cursor' class which is used to execute the 'SQL' statements in 'Python'
    cursor = db.cursor()

    ## creating a databse called 'datacamp'
    ## 'execute()' method is used to compile a 'SQL' statement
    ## below statement is used to create tha 'datacamp' database
    cursor.execute("CREATE DATABASE IF NOT EXISTS datacamp")
    
    cursor.close()

    db.close()

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    cursor = db.cursor()
 
    cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT PRIMARY KEY, ipAddress VARCHAR(30), status INT, name VARCHAR(100), groupName VARCHAR(100))")
    db.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS lectures (id INT, temperatura int, umidita int,lettura DATETIME, PRIMARY KEY(id, lettura))")
    db.commit()
    cursor.close()
    db.close()

    return 0

if __name__ == '__main__':
    hello_world()