# -*- coding: utf-8 -*- 

from flask import Flask
import requests
from flask import request
import json
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Added
from email.mime.image import MIMEImage
import smtplib
import imghdr
import base64
from email.message import EmailMessage
from pprint import pprint

app = Flask(__name__)

'''
The module is needed to send e-mail. The configuration of smtplib is made for GMail.
'''

GMAIL_USER = ""
GMAIL_PASSWORD = ""
EMAIL_TO = ""

def readJson():
    global GMAIL_USER, GMAIL_PASSWORD, EMAIL_TO
    with open('/config/config.json') as config_file:
        data = json.load(config_file)
        GMAIL_USER = data['gmail_user']
        GMAIL_PASSWORD = data['gmail_password']
        EMAIL_TO = data['to']
        config_file.close()

@app.route('/sendEmail', methods=['GET'])
def sendEmail():

    if request.json['type'] == "error":
        gmail_user = GMAIL_USER
        gmail_password = GMAIL_PASSWORD
        device_id = str(request.json["deviceId"])
        device_ip = str(request.json["deviceIp"])
        device_port = str(request.json["devicePort"])
        device_group = str(request.json["deviceGroup"])
        FROM = gmail_user
        TO = [EMAIL_TO]
        SUBJECT = 'Dispositivo non funzionante - Cluster SSDC'

        TEXT = 'Il sensore\n\nId: ' + device_id + '\n\nIndirizzo IP: ' + device_ip + '\n\nNumero di porta: ' + device_port + '\n\nNome gruppo: ' + device_group + '\n\nrisulta non raggiungibile.'

        # Prepare the message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        # Send the message.
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(FROM, TO, message)
            logging.info("Email sent")     
            server.close()
            return "Ok"
        except smtplib.SMTPException as e:
            logging.info(str(e))
            return str(e)

    elif request.json['type'] == "alert":

        Sender_Email = GMAIL_USER
        Reciever_Email = EMAIL_TO
        Password = GMAIL_PASSWORD
        newMessage = EmailMessage()        
        device_id = str(request.json["deviceId"])
        device_ip = str(request.json["deviceIp"])
        device_port = str(request.json["devicePort"])
        device_group = str(request.json["deviceGroup"])                 
        newMessage['Subject'] = "Avviso qualità vegetazione" 
        newMessage['From'] = Sender_Email                   
        newMessage['To'] = Reciever_Email  
  
        newMessage.set_content('Il sensore\n\nId: ' + device_id + '\n\nIndirizzo IP: ' + device_ip + '\n\nNumero di porta: ' + device_port + '\n\nNome gruppo: ' + device_group + '\n\nha segnalato un avviso per la qualità della vegetazione')
        image_data = base64.b64decode(request.json['keypoints_image'])
        image_type = "jpeg"
        image_name = "Field photo"
        newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            
            smtp.login(Sender_Email, Password)              
            smtp.send_message(newMessage)

            return "Ok"

if __name__ == '__main__':
    readJson()
    app.run(debug=True, host='0.0.0.0', port=8081, threaded=True)
