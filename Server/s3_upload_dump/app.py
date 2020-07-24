import boto3
from botocore.client import Config
import glob
import os
import logging

##Il session token risulta essere necessario quando si utilizza un account AWSEducate. In particolare deve essere aggiunto a boto3. Se non 
##Dovesse essere presente allora la funzione restituirebbe un errore.
##Le informazioni come KEY_ID, Secret_key e session_token sono disponibili nella workbench, cliccando sul pulsante account details.

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

    list_of_files = glob.glob('dump/*') # * means all if need specific format then *.csv
    print(list_of_files)
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        data = open(latest_file, 'rb')
    except IOError as e:
        logging.warning("Errore nell'apertura del file.")
        exit(-1)
    
    try:
        s3.Bucket(BUCKET_NAME).put_object(Key=latest_file, Body=data)
    except Exception as e:
        print(e)
        exit(-1)

    logging.info('Upload eseguito correttamente.')

if __name__ == '__main__':
    addToBucket()