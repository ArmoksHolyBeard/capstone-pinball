''' The set of functions for communicating with the PLC'''

from pycomm3 import LogixDriver
import asyncio

# IP address of the PLC, hardcoded for now
IP = '10.230.49.142'

class PinballPLC():

    def __init__(self):
        self.plc = LogixDriver(IP)
        self.current_tags = {}
        self.ready = False
    
    def start(self):
        self.plc.open()
    
    def end(self):
        self.plc.close()
    
    # Plan is to make this asynchronous using asyncio, if I can get that working
    def read(self):
        self.current_tags = self.plc.read("Local:1:I").value['Data']
        self.ready = True
    
    def getTags(self):
        self.ready = False
        return self.current_tags
    
    def isReady(self):
        return self.ready