from flask import Flask
import requests
import mysql.connector as mysql
import json
import logging

'''
The module instantiate the database, creating tables and inserting data.
'''

# Create and populate the database's table.
def instantiateDatabase():

    configFile = open("/config/config.json", "r")
    json_object = json.load(configFile)

    try:
        db = mysql.connect(
            host = json_object['host'],
            user = json_object['user'],
            passwd = json_object['passwd']
        )

        cursor = db.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS cluster")
        
        cursor.close()

        db.close()

        db = mysql.connect(
            host = json_object['host'],
            user = json_object['user'],
            passwd = json_object['passwd'],
            database = json_object['database']
        )

        cursor = db.cursor()

        # Create and populate table.
        cursor.execute("CREATE TABLE IF NOT EXISTS statistics (dayPeriod date PRIMARY KEY, moneySaved float, waterSaved float)")
        cursor.execute("CREATE TABLE IF NOT EXISTS devicesGroups (groupName VARCHAR(100) PRIMARY KEY, p1 float, p2 float, p3 float, latCenter DOUBLE, longCenter DOUBLE)")
        cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'default\', 0, 0, 0, 0, 0) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0, latCenter = 0, longCenter = 0")
        cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'Polygon A : CORN FIELD\', 0, 0, 0, -121.82537549999999, 39.0955965) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0")
        cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'Polygon B : GREEN PLANTS FIELD\', 0, 0, 0, -121.82471050000001, 39.083796) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0")
        cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'Polygon C : WHEAT FIELD\', 0, 0, 0, -121.81537625, 39.0810165) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0")
        cursor.execute("INSERT into devicesGroups (groupName, p1, p2, p3, latCenter, longCenter) values (\'Polygon D : GROUND VEGETABLES FIELD\', 0, 0, 0, -121.79617174999998, 39.073426) ON DUPLICATE KEY UPDATE p1 = 0, p2 = 0, p3 = 0")
        cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT PRIMARY KEY, lastLecture DATETIME, ipAddress VARCHAR(30), ipPort INT, status INT, name VARCHAR(100), groupName VARCHAR(100), type VARCHAR(100), FOREIGN KEY (groupName) REFERENCES devicesGroups(groupName))")
        cursor.execute("CREATE TABLE IF NOT EXISTS lectures (id INT, temperature float, humidity float, lastLecture DATETIME, PRIMARY KEY(id, lastLecture), FOREIGN KEY (id) REFERENCES devices(id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS water_container (id INT AUTO_INCREMENT, startDate DATE, endDate DATE, currentValue double, totalValue double, PRIMARY KEY (id))")
        cursor.execute("INSERT INTO water_container (id, startDate, endDate, currentValue, totalValue) VALUES (1, NOW(), NOW() + INTERVAL 7 DAY, 80, 100) ON DUPLICATE KEY UPDATE currentValue = 1, totalValue = 100")
        cursor.execute("INSERT INTO water_container (id, startDate, endDate, currentValue, totalValue) VALUES (2, NOW() - INTERVAL 7 DAY, NOW(), 40, 100) ON DUPLICATE KEY UPDATE currentValue = 2, totalValue = 100")
        db.commit()

        cursor.close()
        db.close()
        return 0
    
    except mysql.Error as err:
        print(str(err), flush=True)
        exit(-1)

if __name__ == '__main__':
    instantiateDatabase()