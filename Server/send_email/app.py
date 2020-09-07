# -*- coding: utf-8 -*- 

from flask import Flask
import requests
from flask import request
import json
import smtplib
import logging

app = Flask(__name__)

'''
The module is needed to send e-mail. The configuration of smtplib is made for GMail.
'''

@app.route('/sendEmail', methods=['GET'])
def sendEmail():
    gmail_user = 'gnammeorg@gmail.com'
    gmail_password = '***'
    device_id = str(request.args.get("deviceId"))
    device_ip = str(request.args.get("deviceIp"))
    device_port = str(request.args.get("devicePort"))
    type = str(request.args.get("type"))
    FROM = gmail_user
    TO = ['salvatore.foderaro@gmail.com']
    SUBJECT = 'Dispositivo non funzionante - Cluster SSDC'

    # Create the body of the message
    if type == "error":
        TEXT = 'Il sensore\n\nId: ' + device_id + '\n\nIndirizzo IP: ' + device_ip + '\n\nNumero di porta: ' + device_port + '\n\nrisulta non raggiungibile.'

    # Prepare the message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the message.
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(FROM, TO, message)       
        server.close()
        return 0
    except smtplib.SMTPException as e:
        logging.info(str(e), flush=True)
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081, threaded=True)
