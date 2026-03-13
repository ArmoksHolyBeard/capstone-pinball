''' The set of functions for communicating with the PLC'''

from pylogix import PLC

# IP address of the PLC, hardcoded for now
IP = '10.230.55.126'

# Put all tag addresses here as constants
BUMPER_01 = "Program:MainProgram.B1C.ACC"
BUMPER_02 = "Program:MainProgram.B2C.ACC"
BUMPER_03 = "Program:MainProgram.B3C.ACC"
DROP_TARGETS = "Program:MainProgram.DTS.ACC"
GOAL = "Program:MainProgram.GC.ACC"
KICKBACK = "Program:MainProgram.KBC.ACC"
LIVES = "Program:MainProgram.Life_Counter.ACC"
RAMP_SPINNER = "Program:MainProgram.RampC.ACC"
STANDING_TARGETS = "Program:MainProgram.STC.ACC"

# Create list of tags
allTags = [
    BUMPER_01,
    BUMPER_02,
    BUMPER_03,
    DROP_TARGETS,
    GOAL,
    KICKBACK,
    LIVES,
    RAMP_SPINNER,
    STANDING_TARGETS
]
# Associate tags with IDs (used in main game loop)
tagNames = {
    BUMPER_01: 'bumper1',
    BUMPER_02: 'bumper2',
    BUMPER_03: 'bumper3',
    DROP_TARGETS: 'dropTargets',
    GOAL: 'goal',
    KICKBACK: 'kickback',
    LIVES: 'lives',
    RAMP_SPINNER: 'rampSpinner',
    STANDING_TARGETS: 'standingTargets'
}

class PinballPLC():

    def __init__(self):
        self.plc = PLC(IP)
        self.tagValues = {
            'bumper_1': 0,
            'bumper_2': 0,
            'bumper_3': 0,
            'dropTargets': 0,
            'goal': 0,
            'kickback': 0,
            'lives': 0,
            'rampSpinner': 0,
            'standingTargets': 0
        }
    
    def end(self):
        self.plc.Close()
    
    # Plan is to make this asynchronous using asyncio, if I can get that working
    def read(self):
        current_tags = self.plc.Read(allTags)
        for tag in current_tags:
            self.tagValues[tagNames[tag.TagName]] = tag.Value
        return self.tagValues
    
    def resetTags(self):
        request = [(tag, 0) for tag in allTags]
        response = self.plc.Write(request)
        # TODO: Error checking on response

if __name__ == "__main__":
    testPLC = PinballPLC()
    print(testPLC.read())
    testPLC.resetTags()
    testPLC.end()