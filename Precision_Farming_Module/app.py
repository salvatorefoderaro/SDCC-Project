from datetime import datetime, date, time, timezone, timedelta
from WeatherForecast import WeatherForecast
from satellite_image import Satellite_Image
from flask import Flask, request
from polygon import Polygon, Sensor
from threading import Thread
from pprint import pprint
import threading
import requests
import os
import re
import sys
import json
import logging




# Global variables

WATER_CONTAINER = 0.0                   # Water residual volume within the container (m^3)
REMAINING_DAYS = 0                      # Remaining days before water refill
TODAY_WATER = 0.0                       # Total water volume reserved for today's computation
WATER_PRICE = 1.40                      # Water price : euro/(m^3)
SAVED_WATER = 0.0                       # Saved water volume for this day, after analysis and planning phases.
TOTAL_AREA = 0.0                        # Total fields' coverage (m^2)

CREATE_POLY_URL = ""                    # URL to POST the desired polygon's geographic coordinates
GET_SATELLITE_IMG_URL = ""              # URL to GET satellite data about the polygon associated to the ID
APPID = ""                              # User credential to access OpenWeatherAPI Server
POLYGONS_INFOS = []                     # List of Polygon objects
SATELLITE_IMAGES = []                   # List of Satellite_Image objects
SEVEN_DAYS_WEATHER_FORCASTS = []        # List of WeatherForecast objects



app = Flask(__name__)                   # Create the Flask app


# REST API to compute Daily Water Plan and get results back to the user cluster.
@app.route('/planning', methods = ['POST', 'GET'])
def planning():
    if request.method == 'POST':

        global  WATER_CONTAINER, REMAINING_DAYS, TODAY_WATER, SAVED_WATER, TOTAL_AREA, POLYGONS_INFOS, SEVEN_DAYS_WEATHER_FORCASTS

        args = request.get_json()

        # Check if the expire date is correctly formulated.
        expire = datetime.fromtimestamp(args.get("expire")).date()
        if expire < date.today():
            return "Something went wrong..."

        # Set the current value for water container's volume and update the remaining time before water refill.
        WATER_CONTAINER = args.get("water_container_volume")
        print(WATER_CONTAINER)
        # Evaluate the remaining days until the day of water refill, to compute the current day water plan.
        REMAINING_DAYS = evaluate_remaining_days( expire )
        print(REMAINING_DAYS)

        # Calculate the value of today's total water amount
        TODAY_WATER = WATER_CONTAINER/REMAINING_DAYS
        print(TODAY_WATER)
        # Append sensors' informations on each reference-polygon's list.
        group_list = args.get("groups_list")
        for elem in group_list:
            for polygon in POLYGONS_INFOS:
                if elem["center"] == polygon.center:
                    new_sensor = Sensor( polygon, elem["avgTemperatura"], elem["avgUmidita"])
                    polygon.add_sensor(new_sensor)

        # Compute data analysis and planning to retrieve the daily water-unit, for each of the 3 irrigations, for each polygon.
        for polygon in POLYGONS_INFOS:
            water_unit = ( TODAY_WATER * ( polygon.proportion ) ) / 3 
            polygon.calculate_avg_soil_moisture()
            polygon.calculate_avg_soil_temperature()
            wuc = float( polygon.evaluate_water_unit_coefficient() )
            polygon.set_water_unit_coefficient( float(wuc) )
            polygon.set_water_unit( water_unit * float(wuc) )
            SAVED_WATER += ( ( water_unit - polygon.water_unit ) * 3 )

        # Write the json response of the planning phase and send it back to the user.
        with open('planning_infos.json') as plan:
            data = json.load(plan)
            plan.close()
        counter = 0
        data["saved_water"] = SAVED_WATER
        for p in POLYGONS_INFOS:
            data["groups_list"][counter]["center"] = p.center
            data["groups_list"][counter]["groupName"] = p.name
            data["groups_list"][counter]["daily_water_unit"] = p.water_unit
            counter += 1

        return data
    
    return "You should use a POST method"
    

# REST API to get 7 days Weather Forecasting
@app.route('/weather_forecasts')
def weather_forecasts():
    with open('dashboard_infos.json') as dash_infos:
        data = json.load(dash_infos)
        dash_infos.close()
    counter = 0
    print(len(SEVEN_DAYS_WEATHER_FORCASTS))
    for day in SEVEN_DAYS_WEATHER_FORCASTS:
        data["weather_forecasts"][counter]["day"] = day.day.strftime("%d/%m/%Y")
        data["weather_forecasts"][counter]["description"] = day.description
        data["weather_forecasts"][counter]["temperatures"]["morning"] = day.temperatures["morn"]
        data["weather_forecasts"][counter]["temperatures"]["daylight"] = day.temperatures["day"]
        data["weather_forecasts"][counter]["temperatures"]["evening"] = day.temperatures["eve"]
        data["weather_forecasts"][counter]["temperatures"]["night"] = day.temperatures["night"]
        data["weather_forecasts"][counter]["prob_of_precipitations"] = day.pop
        data["weather_forecasts"][counter]["air_humidity"] = day.humidity
        data["weather_forecasts"][counter]["clouds_percentage"] = day.clouds
        data["weather_forecasts"][counter]["wind_speed"] = day.wind_speed
        counter += 1

    return data


'''
----------------------------------------------------------------------------------------------------------------------------------
'''


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
        p.set_proportion((p.area)/TOTAL_AREA)


# This function contains API call to the Agro API Server, to get all satellite's collected data about tracked polygon.
def get_satellite_img( polygon ):

    # get the timestamps of the 'start' and the 'end' parameters of image research
    end_dt = datetime.now()
    end_dt = end_dt - timedelta(hours=5)
    end_timestamp = end_dt.timestamp()
    days_gap = timedelta(days=20)    
    start_dt = end_dt - days_gap 
    start_timestamp = start_dt.timestamp()

    # prepearing parameters for http  API request
    parameters = { 'polygon_id': polygon.id, 'start': int(start_timestamp), 'end': int(end_timestamp) }
    url = ( 'http://api.agromonitoring.com/agro/1.0/image/search?start=' + 
            str(parameters['start']) + '&end=' + str(parameters['end']) + 
            '&clouds_max=20&polyid=' + parameters['polygon_id'] + '&appid=' + APPID )

    try:
        print('Retrieving Satellite data at : ', url )
        res = requests.get(url)
        data = res.json()

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Error retrieving polygons from OpenWeatherMap Server.')
    
    satellite_img = Satellite_Image(polygon,    data[0]['type'],   data[0]['dt'],     data[0]['dc'],             data[0]['cl'], 
                                    data[0]['image']['truecolor'], data[0]['image']['ndvi'],  data[0]['image']['evi'],
                                    data[0]['stats']['ndvi'],      data[0]['stats']['evi'] )
    
    try:
        # request API to the NDVI stats link, to get all informations to be used
        res = requests.get( satellite_img.ndvi_stats_link )
        ndvi_stats = res.json()
        satellite_img.set_ndvi_stats(ndvi_stats)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Error retrieving polygons from OpenWeatherMap Server.')


    try:
        # request API to the EVI stats link, to get all informations to be used
        res = requests.get( satellite_img.evi_stats_link )
        evi_stats = res.json()
        satellite_img.set_evi_stats(evi_stats)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Error retrieving polygons from OpenWeatherMap Server.')


    SATELLITE_IMAGES.append(satellite_img)


# This function contains API call to the OpenWeatherAPI Server, to retrieve 7 days weather forecasts.
def weather_by_geocoordinates():

    # Keep the reference zone-geo-coordinates as the center of one of the tracked polygons.
    ref_geo_coordinates = POLYGONS_INFOS[0].center
    longitude = ref_geo_coordinates[0]
    latitude = ref_geo_coordinates[1]

    try:
        res = requests.get( 'https://api.openweathermap.org/data/2.5/onecall?lat=' + str(latitude) + '&lon=' + 
                            str(longitude) + '&units=metric&exclude=hourly,minutely&appid=' + APPID )
        data = res.json()

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logging.warning('Error retrieving weather infos about these coordinates from OpenWeatherMap Server.')

    forecasts = data['daily']

    for this_day in forecasts:

        weather_forecast = WeatherForecast( this_day['dt'], this_day['weather'][0]['description'],    this_day['temp'],   this_day['pop'],   
                                            this_day['clouds'], this_day['humidity'],    this_day['wind_speed'] )
        
        SEVEN_DAYS_WEATHER_FORCASTS.append(weather_forecast)


def evaluate_remaining_days( expire ):

    today = date.today()
    
    if expire > today :
        return  (expire-today).days
    else:
        return  0


# This function contains all retrieval calls to setup the server infos at the launch.
def setup():

    global POLYGONS_INFOS, SATELLITE_IMAGES, SEVEN_DAYS_WEATHER_FORCASTS

    read_configurations()
    keep_infos()
    retrieve_polygons()
    for p in POLYGONS_INFOS:
        get_satellite_img(p) 
    weather_by_geocoordinates()

if __name__ == '__main__':

    setup()
    app.run(host='0.0.0.0', debug=False, port = 5000)