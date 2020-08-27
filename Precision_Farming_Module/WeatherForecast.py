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