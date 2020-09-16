from ssdp import Server
from ssdp import gen_logger
import logging  

if __name__ == '__main__':   
    # Start SSDP server
    ssdpServer = Server(30006, 'ssdp', 'cluster')
    ssdpServer.start()
