from test_post import get_polygons_id, remove_polygons
import threading
import requests
import json
from pprint import pprint

def test_plan():

    for i in range(100):

        res = requests.get("http://0.0.0.0:5001/getplan")
        
        


if __name__ == '__main__' :
    
    for i in range(1):

        x = threading.Thread(target=test_plan)

        x.start()

    