import threading
import requests
import json
from pprint import pprint

def test_plan():
    print("i'm in")
    for i in range(20):
        res = requests.get("http://0.0.0.0:5001/weather")
        


if __name__ == '__main__' :
    
    for i in range(10):

        x = threading.Thread(target=test_plan)

        x.start()

    