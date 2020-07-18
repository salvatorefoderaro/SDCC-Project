from flask import Flask
import requests
import mysql.connector as mysql

def hello_world():
    db = mysql.connect(
        host = "mysql",
        user = "root",
        passwd = "password"
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
        host = "mysql",
        user = "root",
        passwd = "password",
        database = "datacamp"
    )

    cursor = db.cursor()
 
    cursor.execute("CREATE TABLE IF NOT EXISTS devices (id INT PRIMARY KEY, ipAddress VARCHAR(30), status INT)")

    cursor.close()

    db.close()

    return 0


if __name__ == '__main__':
    hello_world()