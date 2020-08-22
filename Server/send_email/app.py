# -*- coding: utf-8 -*- 

from flask import Flask
import requests
import mysql.connector as mysql
from flask import request
import json
import smtplib

app = Flask(__name__)

'''
Modulo che si occupa di regisrare i nuovi dispositivi e le registrazioni prodotte nel sengolo dai singoli dispositivi.
'''

@app.route('/sendEmail', methods=['GET'])
def collectData():
    gmail_user = 'gnammeorg@gmail.com'
    gmail_password = '***'
    device_id = str(request.args.get("deviceId"))
    device_ip = str(request.args.get("deviceIp"))
    device_port = str(request.args.get("devicePort"))
    FROM = gmail_user
    TO = ['salvatore.foderaro@gmail.com']
    SUBJECT = 'Dispositivo non funzionante - Cluster SSDC'
    TEXT = 'Il sensore\n\nId: ' + device_id + '\n\nIndirizzo IP: ' + device_ip + '\n\nNumero di porta: ' + device_port + '\n\nrisulta non raggiungibile.'

# Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(FROM, TO, message)       
        server.close()

        print ('Email sent!')
    except:
        print ('Something went wrong...')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081, threaded=True)
