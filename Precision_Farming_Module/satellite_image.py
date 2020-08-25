from datetime import datetime

class Satellite_Image():

    # This class collects satellite's data about a specificied associated polygon.
    # Data are caught by Satellite's images on ESA Copernicus Sentinel 2 / Landsat 8 missions.

    def __init__(   self,           polygon,            satellite,             acquisition_date, 
                    data_coverage,  cloud_coverage,     img_link,       
                    ndvi_img_link,  evi_img_link,       ndvi_stats_link,       evi_stats_link  ):

        self.polygon = polygon
        self.satellite = satellite
        self.acquisition_date = datetime.fromtimestamp(acquisition_date)
        self.data_coverage = data_coverage
        self.cloud_coverage = cloud_coverage
        self.img_link = img_link
        self.ndvi_img_link = ndvi_img_link
        self.evi_img_link = evi_img_link
        self.ndvi_stats_link = ndvi_stats_link
        self.evi_stats_link = evi_stats_link
    


    def set_ndvi_stats( self, ndvi_stats ):
        self.ndvi_mean = ndvi_stats['mean']
        self.ndvi_min = ndvi_stats['min']
        self.ndvi_max = ndvi_stats['max']
        self.ndvi_std = ndvi_stats['std']



    def set_evi_stats( self, evi_stats ):
        self.evi_mean = evi_stats['mean']
        self.evi_min = evi_stats['min']
        self.evi_max = evi_stats['max']
        self.evi_std = evi_stats['std']

    

    
    def print_all(self):
        print( " \n--------------------------------------------------------------------------------------------------------------------\n ")
        print( " --------------------| POLYGON FEATURES TABLE :: " + self.polygon.name + " |-----------------------------------------\n ")
        print( " --------------------------------------------------------------------------------------------------------------------\n ")
        print( "    True colors image link                    :   " + self.img_link + "   \n ")
        print( "    Center Coordinates [longitude - latitude] :   " + str(self.polygon.center) + "   \n ")
        print( "    Polygon Area                              :   " + str(self.polygon.area) + " m^2   \n ")
        print( "    Acquisition date                          :   " + str(self.acquisition_date) + "   \n ")
        print( "    Data coverage                             :   " + str(self.data_coverage) + "%   \n ")
        print( "    Cloud coverage                            :   " + str(self.cloud_coverage) + "%   \n ")
        print( "    Satellite                                 :   " + str(self.satellite) + "    \n ")
        print( " --------------------------------------------------------------------------------------------------------------------\n ")
        print( "    NDVI image link                           :   " + self.ndvi_img_link + "   \n ")
        print( "    ndvi mean value                           :   " + str(self.ndvi_mean) + "   \n ")
        print( "    ndvi min value                            :   " + str(self.ndvi_min) + "   \n ")
        print( "    ndvi max value                            :   " + str(self.ndvi_max) + "   \n ")
        print( "    ndvi std deviation                        :   " + str(self.ndvi_std) + "   \n ")
        print( " --------------------------------------------------------------------------------------------------------------------\n ")
        print( "    EVI image link                            :   " + self.evi_img_link + "   \n ")
        print( "    evi mean value                            :   " + str(self.evi_mean) + "   \n ")
        print( "    evi min value                             :   " + str(self.evi_min) + "   \n ")
        print( "    evi max value                             :   " + str(self.evi_max) + "   \n ")
        print( "    evi std deviation                         :   " + str(self.evi_std) + "   \n ")
        print( " ---------------------------------------------------------------------------------------------------------------\n\n ")