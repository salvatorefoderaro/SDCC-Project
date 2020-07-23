import sys
from ssdp import Server, Client
from ssdp import gen_logger
from queue import Queue

logger = gen_logger('sample')

if __name__ == '__main__':
    try:
        upnpServer  = Server(9001, 'blockchain', 'main1111')
        upnpServer.run()
    except Exception as e:
        logger.error(e)