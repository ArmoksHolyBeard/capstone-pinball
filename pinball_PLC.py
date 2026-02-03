''' The set of functions for communicating with the PLC'''

from pylogix import PLC

# IP address of the PLC, hardcoded for now
IP = '10.230.55.126'

# Put all tag addresses here as constants
COUNTER_01 = "Program:MainProgram.BUTTON_CNT.ACC"

# Create list of tags
allTags = [COUNTER_01]

class PinballPLC():

    def __init__(self):
        self.plc = PLC(IP)
    
    def end(self):
        self.plc.Close()
    
    # Plan is to make this asynchronous using asyncio, if I can get that working
    def read(self):
        current_tags = self.plc.Read(allTags)
        return [(tag.TagName, tag.Value) for tag in current_tags]
        # for tag in current_tags:
        #     print(f"{tag.TagName} has value {tag.Value}")
    
    def resetTags(self):
        request = [(tag, 0) for tag in allTags]
        response = self.plc.Write(request)
        # print(response)

if __name__ == "__main__":
    testPLC = PinballPLC()
    testPLC.read()
    testPLC.resetTags()