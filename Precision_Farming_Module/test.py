from test_post import get_polygons_id, remove_polygons
import threading
import requests
import json
from pprint import pprint

NUM_THREADS = 1

ITERATIONS = 10

def test_plan():

    global ITERATIONS

    for i in range( ITERATIONS ):

        res = requests.get("http://0.0.0.0:5001/getplan")
        
        


if __name__ == '__main__' :
    
    for i in range( NUM_THREADS ):

        x = threading.Thread(target=test_plan)

        x.start()

    