''' The set of functions for communicating with the PLC'''
from queue import Queue
from time import sleep

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
# TODO: Tags for system enable, start button, maybe flippers
SYSTEM_ENABLE = "foo"

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

    QUIT = 0
    LOCK = 1
    UNLOCK = 2

    def __init__(self, data_q: Queue, cmd_q: Queue, /, *, demo_mode=False):
        self.data_q = data_q
        self.cmd_q = cmd_q
        self.plc = PLC(IP) if not demo_mode else None
        self.tag_values = {
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
        self.demo_mode = demo_mode
    
    def _end(self):
        if not self.demo_mode:
            self.plc.Close()
    
    def _read(self):
        current_tags = self.plc.Read(allTags)
        for tag in current_tags:
            self.tag_values[tagNames[tag.TagName]] = tag.Value
        return self.tag_values
    
    def _toggle_lock(self, enabled: bool):
        response = self.plc.Write(SYSTEM_ENABLE, enabled)
    
    def _resetTags(self):
        request = [(tag, 0) for tag in allTags]
        response = self.plc.Write(request)
        # TODO: Error checking on response
    
    def read_loop(self):
        # TODO: Error handling and exit condition
        while True:
            # Check the command queue
            if not self.cmd_q.empty():
                cmd = self.cmd_q.get()
                if cmd == self.QUIT: # Maybe set a timeout with exception handling?
                    # Turn off the motor driver and return so the
                    # thread manager can properly close out the thread
                    self._end()
                    return
                if cmd == self.LOCK:
                    self._toggle_enable(True)
                if cmd == self.UNLOCK:
                    self._toggle_enable(False)
            if not self.demo_mode:
                self.data_q.put(self._read()) # Maybe set a timeout with exception handling?
                self._resetTags()

if __name__ == "__main__":
    test_Q1 = Queue()
    test_Q2 = Queue()
    test_PLC = PinballPLC(test_Q1, test_Q2)
    print(test_PLC._read())
    print(test_PLC._resetTags())
    print()
    if (input("Continue? y/n ")).upper() == "Y":
        for i in range(20):
            for tag, value in test_PLC._read().items():
                print(f"{tag}: {value}")
            print()
            sleep(0.5)
    test_PLC._end()