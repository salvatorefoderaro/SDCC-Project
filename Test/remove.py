import requests
import os
import re
import sys
import json



POLYGONS_ID = []



def get_polygons_id():

    global POLYGONS_ID

    res = requests.get("http://api.agromonitoring.com/agro/1.0/polygons?appid=1709a3a96099a66ed619f1f6ec016586")
    
    response = res.json()

    for elem in response:
        POLYGONS_ID.append(elem["id"])
    
    print(POLYGONS_ID)

    return 0


def remove_polygons():

    for identifier in POLYGONS_ID:

        url = ("http://api.agromonitoring.com/agro/1.0/polygons/" + identifier + "?appid=1709a3a96099a66ed619f1f6ec016586")
        print(url)

        res = requests.delete(url)

        print("response: " + str(res.status_code) )



if __name__ == "__main__":

    check = get_polygons_id()

    if check == 0:
        remove_polygons()
    
    print("procedure has been completed!")

