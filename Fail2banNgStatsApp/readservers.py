import sys
from numpy import genfromtxt


class ServerListReader(object):
    numberList = []
    addressList = []
    portList = []

    @classmethod
    def readServerList(cls):
        ServerList = genfromtxt('ServerList.csv', delimiter='/')
        numberList = ServerList[:,1]
        addressList = ServerList[:, 2]
        portList = ServerList[:,3]
        sys.stdout.write(numberList)
        sys.stdout.flush()
