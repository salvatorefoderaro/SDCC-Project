import os
import socket
import re
import sys
import time
import threading
import socket
import time
import requests

MINE_IP_ADDRESS = ""
CLUSTER_IP_ADDRESS = ""

def getMineIPAddress():
    global MINE_IP_ADDRESS
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    MINE_IP_ADDRESS = IP

SEARCH_INTERVAL = 5
BCAST_IP = '239.255.255.250'
BCAST_PORT = 10000
port = 9001
protocol = "blockchain"
networkid = "main1111"

def getClusterIPAddress():
        global CLUSTER_IP_ADDRESS
        '''
        broadcast SSDP DISCOVER message to LAN network
        filter our protocal and add to network
        '''
        SSDP_DISCOVER = ('M-SEARCH * HTTP/1.1\r\n' +
                        'HOST: 239.255.255.250:1900\r\n' +
                        'MAN: "ssdp:discover"\r\n' +
                        'MX: 1\r\n' +
                        'ST: ssdp:all\r\n' +
                        '\r\n')
        LOCATION_REGEX = re.compile("LOCATION: {}_{}://[ ]*(.+)\r\n".format(protocol, networkid), re.IGNORECASE)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(SSDP_DISCOVER.encode('ASCII'), (BCAST_IP, BCAST_PORT))
        sock.settimeout(3)
        data, addr = sock.recvfrom(1024)
        CLUSTER_IP_ADDRESS = addr[0].split('\'')[0]
                
if __name__ == '__main__':
    getClusterIPAddress()
    getMineIPAddress()
    
    while (True):
        dictToSend = {'id':'100', 'ip':MINE_IP_ADDRESS, 'status':'3'}
        try:
            res = requests.post('http://'+CLUSTER_IP_ADDRESS+':5000/sendDataToCluster', json=dictToSend)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            getClusterIPAddress()
        time.sleep(60)
