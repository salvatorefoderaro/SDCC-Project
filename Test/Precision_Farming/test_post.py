from datetime import datetime, date, time, timezone, timedelta
from matplotlib import pyplot as plt
from flask import Flask, request 
from polygon import Polygon, Sensor
from threading import Thread
from pprint import pprint
import threading
import requests
import os
import re
import sys
import socket
import logging
import json


MINE_IP_ADDRESS = ""
POLYGONS_INFOS = [] 
CREATE_POLY_URL = "" 
APPID = ""     
TOTAL_AREA = 0.0  
PLANNING_TIMES = []
POLYGONS_ID = []



app = Flask(__name__)                   # Create the Flask app




# TEST CASE: SAMPLE REST API TO POST SENSORS' DATA AND GET THE WATER DAILY PLAN
@app.route("/getplan")
def getplan():

    global PLANNING_TIMES

    with open('sensor_data.json') as j:
        data = json.load(j)
        j.close()

    data["water_container_volume"] = 6000
    data["expire"] = datetime(2020, 9, 28, 0, 0, 0, 0 ).timestamp()

    #pprint(data)

    try:

        BEFORE = datetime.now()
        res = requests.post("http://testsdcc1-env.eba-egewcv65.eu-central-1.elasticbeanstalk.com/planning", json = data )
        data = res.json()
        pprint(data)
        AFTER = datetime.now()

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Errore!')
    

    interval_sample = ( AFTER - BEFORE ).total_seconds()
    
    PLANNING_TIMES.append(interval_sample)

    return "Ok"

@app.route("/weather")
def weather():

    data = { "center" : str(POLYGONS_INFOS[0].center) }

    try:
        res = requests.get("http://testsdcc1-env.eba-egewcv65.eu-central-1.elasticbeanstalk.com:80/weather_forecasts", json = data)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Errore!')
    
    return res.json()

@app.route("/times")
def times():

    global PLANNING_TIMES
    
    plt.scatter(range(len(PLANNING_TIMES)), PLANNING_TIMES, c='r', label='planning time (local host) - #threads = 1')
    plt.xlabel('measurements')
    plt.ylabel('y')
    plt.show()

    meanvalue = 0.0

    for num in PLANNING_TIMES:
        meanvalue = meanvalue + num
    
    meanvalue = ( meanvalue/(len(PLANNING_TIMES)) )

    return str(meanvalue)





def get_polygons_id():

    global POLYGONS_INFOS, POLYGONS_ID

    for elem in POLYGONS_INFOS:
        POLYGONS_ID.append(elem.id)

    return 0


def remove_polygons():

    for identifier in POLYGONS_ID:

        url = ("http://api.agromonitoring.com/agro/1.0/polygons/" + identifier + "?appid=1709a3a96099a66ed619f1f6ec016586")
        print(url)

        res = requests.delete(url)

        print("response: " + str(res.status_code) )


def test_plan():

        res = requests.get("http://testsdcc1-env.eba-egewcv65.eu-central-1.elasticbeanstalk.com:80/weather_forecasts").json
        pprint(res)






# This function gets configuration infos from 'config.json' file, in order to access OpenWeatherAPI Server.
def read_configurations():

    global  CREATE_POLY_URL, APPID
    with open('config.json') as configurations:
        data = json.load(configurations)
        CREATE_POLY_URL = data['create_poly_url']
        GET_SATELLITE_IMG_URL = data['get_satellite_image_url']
        APPID = data['appid']
        configurations.close()


# This function keeps information from the polygons' json files, to be used as parameters for polygons' ID retrieval.
def keep_infos():

    with open('polygon_A.json') as poly_A_infos:
        data = json.load(poly_A_infos)
        #instantiate a Polygon object and populate its attributes
        poly_A = Polygon()
        poly_A.set_json_infos(data)
        poly_A.set_name(data['name']) 
        POLYGONS_INFOS.append(poly_A)        #append the Polygon object to the list
        poly_A_infos.close()

    with open('polygon_B.json') as poly_B_infos:
        data = json.load(poly_B_infos)
        #instantiate a Polygon object and populate its attributes
        poly_B = Polygon()
        poly_B.set_json_infos(data) 
        poly_B.set_name(data['name']) 
        POLYGONS_INFOS.append(poly_B)        #append the Polygon object to the list
        poly_B_infos.close()

    with open('polygon_C.json') as poly_C_infos:
        data = json.load(poly_C_infos)
        #instantiate a Polygon object and populate its attributes
        poly_C = Polygon()
        poly_C.set_json_infos(data)
        poly_C.set_name(data['name'])
        POLYGONS_INFOS.append(poly_C)        #append the Polygon object to the list
        poly_C_infos.close()
    
    with open('polygon_D.json') as poly_D_infos:
        data = json.load(poly_D_infos)
        #instantiate a Polygon object and populate its attributes
        poly_D = Polygon()
        poly_D.set_json_infos(data)
        poly_D.set_name(data['name'])
        POLYGONS_INFOS.append(poly_D)        #append the Polygon object to the list
        poly_D_infos.close()
    

# This function contains API call to the OpenWeatherAPI Server, to retrieve all polygons identifiers and main geometric features.
def retrieve_polygons():

    global TOTAL_AREA, POLYGONS_INFOS

    for p in POLYGONS_INFOS:

        try:
            res = requests.post( CREATE_POLY_URL + APPID,json = p.json_infos )
            data = res.json()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            logging.warning('Error retrieving polygons from OpenWeatherMap Server.')

        p.set_id( data['id'] )
        p.set_center(data['center'])
        p.set_area(data['area'])
        TOTAL_AREA += p.area
    
    for p in POLYGONS_INFOS:
        p.set_proportion = (p.area)/TOTAL_AREA


# Funzione per l'ottenimento del proprio indirizzo IP all'interno della rete
def getMineIpAddress():
    global MINE_IP_ADDRESS
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    MINE_IP_ADDRESS = IP


def setup():
    getMineIpAddress()
    read_configurations()




if __name__ == '__main__' :

    setup()
    app.run(host='0.0.0.0', debug=False, port = 5001)