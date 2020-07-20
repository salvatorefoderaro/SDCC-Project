import os
import socket
import re
import sys
import time
import threading

BCAST_IP = '239.255.255.250'
UPNP_PORT = 10000
IP = '0.0.0.0'
M_SEARCH_REQ_MATCH = "M-SEARCH"

port = 9001
protocol = "blockchain"
networkid = "main1111"
interrupted = False

def listen():
        '''
        Listen on broadcast addr with standard 1900 port
        It will reponse a standard ssdp message with blockchain ip and port info if receive a M_SEARCH message
        '''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(BCAST_IP) + socket.inet_aton(IP))
            sock.bind((IP, UPNP_PORT))
            sock.settimeout(1)
            #logger.info("upnp server is listening...")
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    #logger.info("IP Addres of the node is: %s", addr)
                    print("ricevuto")
                    respond(addr)
                except socket.error:
                    if interrupted:
                        sock.close()
                        return
                    
        except Exception as e:
            #logger.info('Error in npnp server listening: %s', e)
            return

def respond(addr):
        try:
            local_ip = get_local_IP()
            UPNP_RESPOND = """HTTP/1.1 200 OK
            CACHE-CONTROL: max-age=1800
            ST: private blockchain upnp 1.0
            EXT:
            LOCATION: {}_{}://{}:{}
            """.format(protocol, networkid, local_ip, port).replace("\n", "\r\n")
            outSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            outSock.sendto(UPNP_RESPOND.encode('ASCII'), addr)
            print("Risposta!")
            outSock.close()
        except Exception as e:
            # logger.error('Error in upnp response message to client %s', e)
            return
if __name__ == "__main__":
    listen()