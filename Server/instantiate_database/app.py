from flask import Flask
import requests
import mysql.connector as mysql
import json

def hello_world():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

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
    cursor.execute("CREATE TABLE IF NOT EXISTS groups (groupName VARCHAR(100) PRIMARY KEY, parameter1 float, parameter2 float, parameter3 float)")
    db.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT PRIMARY KEY, ipAddress VARCHAR(30), ipPort INT, status INT, name VARCHAR(100), groupName VARCHAR(100), type VARCHAR(100), FOREIGN KEY (groupName) REFERENCES groups(groupName))")
    db.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS lectures (id INT, temperatura float, umidita float,lettura DATETIME, PRIMARY KEY(id, lettura))")
    db.commit()
    cursor.close()
    db.close()

    return 0

if __name__ == '__main__':
    hello_world()