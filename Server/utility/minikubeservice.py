import os
import subprocess

def getServiceExternalIP(serviceName):
    global SERVICE_EXTERNAL_IP
    a = subprocess.Popen(['kubectl','get','services'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, universal_newlines=True).communicate()

    list = str(a[0])
    for i in range(0, len(list.split("\\n"))):
        list = str(a[0]).split("\\n")[i].split("  ")
        for k in list:
            if '' in list:
                list.remove('')
        if list[0] == serviceName:
            SERVICE_EXTERNAL_IP = list[3].replace(" ", "")
            SERVICE_EXTERNAL_PORT = list[4].split(":")[0].replace(" ", "")
            return "http://" + SERVICE_EXTERNAL_IP + ":" + SERVICE_EXTERNAL_PORT
    return 'None'

if __name__ == "__main__":
    print(getServiceExternalIP("collectdataservice"))