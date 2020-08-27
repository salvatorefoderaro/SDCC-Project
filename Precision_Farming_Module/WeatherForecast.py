import json
from datetime import datetime

class WeatherForecast():

    def __init__(    self,   day,    description,    temperatures,   pop,   clouds,     humidity,       wind_speed   ):
        
        self.day = datetime.fromtimestamp(day)
        self.description = description
        self.temperatures = temperatures
        self.pop = 100*pop
        self.clouds = clouds
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.mean_temperature = ( temperatures["day"] + temperatures["eve"] ) / 2
    

    def print_all( self):

        print( " \n--------------------------------------------------------------------------------------------------------------------\n ")
        print( " --------------------| WEATHER FORECASTS :: " + str(self.day) + " |-----------------------------------------\n ")
        print( " --------------------------------------------------------------------------------------------------------------------\n ")
        print( "    Weather    Description                    :   " + self.description + "   \n ")
        print( "    Cloud percentage                          :   " + str(self.clouds) + "%   \n ")
        print( "    Probability of precipitations             :   " + str(self.pop) + "%   \n ")
        print( "    Humidity                                  :   " + str(self.humidity) + "%   \n ")
        print( "    Wind Speed                                :   " + str(self.wind_speed) + " m/s   \n ")
        print( " --------------------------------------------------------------------------------------------------------------------\n ")
        print( " ------------------------------------           TEMPERATURES            ---------------------------------------------\n ")
        print( "    Morning temperature                       :   " + str(self.temperatures['morn']) + "°C   \n ")
        print( "    Daylight temperature                      :   " + str(self.temperatures['day']) + "°C   \n ")
        print( "    Evening temperature                       :   " + str(self.temperatures['eve']) + "°C   \n ")
        print( "    Night temperature                         :   " + str(self.temperatures['night']) + "°C   \n ")
        print( " ---------------------------------------------------------------------------------------------------------------------\n\n ")




class Forecasts_Analyzer():

    def __init__( self ):
        self.forecasts = []
        self.state = "DEFAULT"
        self.coefficient = 1.0
    

    def add_forecast( self, forecast ):
        self.forecasts.append( forecast )
    

    def evaluate_state( self ):

        POP = 0.0
        HUMIDITY = 0.0
        CLOUDS = 0.0
        TEMP = 0.0
        counter = 0

        for f in self.forecasts:
            POP += f.pop
            HUMIDITY += f.humidity
            CLOUDS += f.clouds
            TEMP += f.mean_temperature
            counter += 1

        POP = POP/counter
        HUMIDITY = HUMIDITY/counter
        CLOUDS = CLOUDS/counter
        TEMP = TEMP/counter

        if  TEMP > 35.0 and HUMIDITY < 15.0  and POP < 15.0 :
            self.state = "DROUGHT"

        if  HUMIDITY > 35.0 and CLOUDS > 25.0 and POP > 60.0 :
            self.state = "FLOOD"
        
        if  HUMIDITY > 15.0 and CLOUDS > 10.0 and POP > 15.0 :
            self.state = "RAIN"

        
    def evaluate_coefficient( self ):

        if self.state == "DROUGHT":
            self.coefficient = 0.90

        elif self.state == "FLOOD":
            self.coefficient = 0.80

        elif self.state == "RAIN":
            self.coefficient = 0.90

        else:
            self.coefficient = 1.0
