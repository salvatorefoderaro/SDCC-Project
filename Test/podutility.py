# -*- coding: utf-8 -*- 

import os
import subprocess
import time

def killPod(podName, podSubname):
    string ="name=k8s_" + podName + "_" + podName + podSubname + "*"
    a = subprocess.Popen(['sh', 'getContainerID.sh', string], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True).communicate()

    list = str(a[0]).split("\\n")
    list = list[0].split("\n")
    a = subprocess.Popen(['sh', 'killContainerID.sh', list[0]], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True).communicate()
    return 'None'

def checkPodStatus(appName):
    name = "app="+appName
    a = subprocess.Popen(['kubectl', 'get', '--no-headers=true','pods','-l', name], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True).communicate()

    list = str(a[0]).split("\\n")
    list = list[0].split("\n")
    list.pop()
    for i in list:
        if i.split()[2] != 'Running':
            print("\nTest not passed!")
        else:
            print("\nTest passed!")

if __name__ == "__main__":
    killPod("dbconnector", "deployment")
    time.sleep(40)
    checkPodStatus("dashboard")