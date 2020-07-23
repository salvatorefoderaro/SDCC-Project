import boto3
from botocore.client import Config

##Il session token risulta essere necessario quando si utilizza un account AWSEducate. In particolare deve essere aggiunto a boto3. Se non 
##Dovesse essere presente allora la funzione restituirebbe un errore.
##Le informazioni come KEY_ID, Secret_key e session_token sono disponibili nella workbench, cliccando sul pulsante account details.

from flask import Flask, render_template
from flask import request

app = Flask(__name__)

##S3 config############################

### information from configS3
BUCKET_NAME = "sdcc-test-bucket"

s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
###################################

def addToBucket():
    #La funzione aggiunge l'immagine all'interno del bucket desiderato.
    #imgPath: str --> path locale del file
    #imgName: str --> nome del file una volta inserito all'interno del bucket.
    try:
        data = open("dump/dump20200723.sql", 'rb')
    except IOError as e:
        print(e)
        print("Errore nel caricamento dell'immagine.")
        exit(1)
    
    s3.Bucket(BUCKET_NAME).put_object(Key="dump20200723.sql", Body=data)
    print('Upload eseguito correttamente.')

    '''my_bucket = s3.Bucket(BUCKET_NAME)

    for file in my_bucket.objects.all():
        s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)
        print(file.key)'''

if __name__ == '__main__':
    addToBucket()