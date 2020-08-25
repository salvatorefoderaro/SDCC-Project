from flask import Flask
import requests
import mysql.connector as mysql
import json

'''
Modulo che si occupa dell'instanziazione del database.
'''

def instantiateDatabase():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd']
    )

    cursor = db.cursor()

    # Effettuo la creazione del database
    cursor.execute("CREATE DATABASE IF NOT EXISTS cluster")
    
    cursor.close()

    db.close()

    db = mysql.connect(
        host = json_object['host'],
        user = json_object['user'],
        passwd = json_object['passwd'],
        database = json_object['database']
    )

    # Eseguo le query per la creazione delle tabelle

    cursor = db.cursor()

    # Query per l'instanziazione di una tabella con le info riguardanti il cluster
    # cursor.execute("CREATE TABLE")

    cursor.execute("CREATE TABLE IF NOT EXISTS devicesGroups (groupName VARCHAR(100) PRIMARY KEY, p1 float, p2 float, p3 float, latCenter DOUBLE, longCenter DOUBLE)")
    cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'default\', 0, 0, 0, 0, 0) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0, latCenter = 0, longCenter = 0")
    db.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT PRIMARY KEY, lettura DATETIME, ipAddress VARCHAR(30), ipPort INT, status INT, name VARCHAR(100), groupName VARCHAR(100), type VARCHAR(100), FOREIGN KEY (groupName) REFERENCES devicesGroups(groupName))")
    db.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS lectures (id INT, temperatura float, umidita float,lettura DATETIME, PRIMARY KEY(id, lettura), FOREIGN KEY (id) REFERENCES devices(id))")
    db.commit()
    cursor.close()
    db.close()

    return 0

if __name__ == '__main__':
    instantiateDatabase()