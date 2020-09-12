import boto3
import botocore
from botocore.client import Config
import glob
import os
import logging
import json
import logging

'''
The module is needed to upload the DB dump to S3.
'''

AWS_KEY_ID = ""
AWS_SECRET_KEY = ""
BUCKET_NAME = ""
s3 = ""

# Read the .json file to get the config.
def readJson():
    global AWS_KEY_ID, AWS_SECRET_KEY, BUCKET_NAME
    with open('/config/s3_key.json') as config_file:
        data = json.load(config_file)
        AWS_KEY_ID = data['aws_key_id']
        AWS_SECRET_KEY = data['aws_secret_key']
        BUCKET_NAME = data['bucket_name']

###################################

def addToBucket():

    s3 = boto3.resource(
        's3',
        aws_access_key_id=AWS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_KEY,
        config=Config(signature_version='s3v4')
        )

    with open('/config/cluster_config.json') as config_file:
        data = json.load(config_file)
        FOLDER_NAME = data['folder_name']
        config_file.close()

    # List all the file in the folder
    list_of_files = glob.glob('dump/*')

    # Get the most recent file (using timestamp) 
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        data = open(latest_file, 'rb')
    except IOError as e:
        logging.warning("Errore nell'apertura del file.")
        exit(-1)
    
    # Put the file to S3
    s3.Bucket(BUCKET_NAME).put_object(Key=FOLDER_NAME+'/'+latest_file, Body=data)

    # Dopo l'upload elimino il file per non occupare inutilmente spazio
    os.remove(latest_file)

if __name__ == '__main__':
    readJson()
    addToBucket()