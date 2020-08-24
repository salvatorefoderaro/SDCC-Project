import boto3
from botocore.client import Config
import glob
import os
import logging
import json

##Il session token risulta essere necessario quando si utilizza un account AWSEducate. In particolare deve essere aggiunto a boto3. Se non 
##Dovesse essere presente allora la funzione restituirebbe un errore.
##Le informazioni come KEY_ID, Secret_key e session_token sono disponibili nella workbench, cliccando sul pulsante account details.

##S3 config############################

### information from configS3

'''
Modulo per il caricamento del dump del database nel bucket S3.
'''


BUCKET_NAME = "sdcc-test-bucket"
ACCESS_KEY_ID = "AKIA57G4V3XAZXYSWEYA"
ACCESS_SECRET_KEY = "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"

s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
###################################

def addToBucket():

    with open('/config/cluster_config.json') as config_file:
        data = json.load(config_file)
        FOLDER_NAME = data['folder_name']
        config_file.close()

    # Ottengo la lista dei file presenti nella cartella 'dump'
    list_of_files = glob.glob('dump/*') 

    # Considero il file più recente
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        data = open(latest_file, 'rb')
    except IOError as e:
        logging.warning("Errore nell'apertura del file.")
        exit(-1)
    
    try:
        s3.Bucket(BUCKET_NAME).put_object(Key=FOLDER_NAME+'/'+latest_file, Body=data)
    except Exception as e:
        print(e)
        exit(-1)

    logging.info('Upload eseguito correttamente.')

    # Dopo l'upload elimino il file per non occupare inutilmente spazio
    os.remove(latest_file)

if __name__ == '__main__':
    addToBucket()