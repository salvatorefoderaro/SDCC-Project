class Polygon():

    def __init__(self):
        self.my_sensors = []
        self.water_unit_coefficient = 1.0
        self.avg_soil_moisture = 0.0
        self.avg_soil_temperature = 0.0
        self.to_plan = False
    
    def set_satellite_image( self, satellite_image ):
        self.satellite_image = satellite_image

    def set_name(self, name):
        self.name = name
    
    def set_groupName(self,groupName):
        self.groupName = groupName

    def set_to_plan( self ):
        self.to_plan = True
    
    def set_id(self, id):
        self.id = id
    
    def set_center(self, coordinates):
        self.center = coordinates
    
    def set_area(self, area):
        self.area = (10000)*area

    def set_json_infos(self, json_infos):
        self.json_infos = json_infos

    def set_water_unit(self, water_unit):
        self.water_unit = water_unit
    
    def set_water_unit_coefficient(self, water_unit_coefficient):
        self.water_unit_coefficient = water_unit_coefficient

    def set_proportion(self, proportion):
        self.proportion = proportion
    
    def add_sensor(self, sensor):
        self.my_sensors.append(sensor)

    def calculate_avg_soil_temperature( self ):
        T = 0.0
        counter = 0
        for sensor in self.my_sensors:
            T = T + sensor.avg_soil_temperature
            counter += 1

        self.avg_soil_temperature = T/counter
    
    def calculate_avg_soil_moisture( self ):
        M = 0.0
        counter = 0
        for sensor in self.my_sensors:
            M = M + sensor.avg_soil_moisture
            counter += 1
        self.avg_soil_moisture = M/counter

    def evaluate_water_unit_coefficient( self ):

        if self.avg_soil_temperature >= 30.0 and self.avg_soil_moisture >= 35.0:
            return  0.25

        elif self.avg_soil_temperature >= 30.0 and self.avg_soil_moisture <= 25.0:
            return  1.0

        elif self.avg_soil_temperature >= 30.0 and ( self.avg_soil_moisture >= 25.0 and self.avg_soil_moisture <= 35.0 ) :
            return  0.75

        elif self.avg_soil_temperature <= 15.0 and self.avg_soil_moisture >= 35.0:
            return  0.0

        elif self.avg_soil_temperature <= 15.0 and self.avg_soil_moisture <= 25.0:
            return  0.5
        
        elif self.avg_soil_temperature <= 15.0 and ( self.avg_soil_moisture >= 25.0 and self.avg_soil_moisture <= 35.0 ):
            return  0.2

        elif ( self.avg_soil_temperature >= 15.0 and self.avg_soil_temperature <= 30.0 )  and self.avg_soil_moisture >= 35.0:
            return  0.2
        
        elif ( self.avg_soil_temperature >= 15.0 and self.avg_soil_temperature <= 30.0 )  and self.avg_soil_moisture <= 25.0:
            return  0.8
        
        elif ( self.avg_soil_temperature >= 15.0 and self.avg_soil_temperature <= 30.0 ) and ( self.avg_soil_moisture >= 25.0 and self.avg_soil_moisture <= 35.0 ):
            return  0.5




class Sensor():

    def __init__(   self,  reference_polygon,    avg_soil_temperature,     avg_soil_moisture    ):
        self.reference_polygon = reference_polygon
        self.avg_soil_moisture = avg_soil_moisture
        self.avg_soil_temperature = avg_soil_temperature