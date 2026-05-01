''' The set of functions for communicating with the PLC'''
from queue import Queue
import time

from pylogix import PLC

# IP address of the PLC, hardcoded for now
IP = '192.168.99.6'

# Put all tag addresses here as constants
BUMPERS = "Program:MainProgram.BC.ACC"
STANDING_TARGETS = "Program:MainProgram.STC.ACC"
RAMP_SPINNER = "Program:MainProgram.RampC.ACC"
DROP_TARGET_1 = "Program:MainProgram.DT1C.ACC"
DROP_TARGET_2 = "Program:MainProgram.DT2C.ACC"
DROP_TARGET_3 = "Program:MainProgram.DT3C.ACC"
GOAL = "Program:MainProgram.GC.ACC"
FREE_KICK = "Program:MainProgram.FKC.ACC" #Bool
START_BUTTON = "Program:MainProgram.SB_PRESSED" # Bool
KICKBACK = "Program:MainProgram.KBC.ACC" #Bool. Latches when activated. Only reset to reactivate
IN_PLAY = "Program:MainProgram.BOL" # Bool, don't reset
GAME_LOCK = "Program:MainProgram.GL" # Output, disable when true

# Create list of tags
resettable_tags = [
    BUMPERS,
    STANDING_TARGETS,
    RAMP_SPINNER,
    DROP_TARGET_1,
    DROP_TARGET_2,
    DROP_TARGET_3,
    GOAL,
    FREE_KICK,
    START_BUTTON
]
input_tags = [
    BUMPERS,
    STANDING_TARGETS,
    RAMP_SPINNER,
    DROP_TARGET_1,
    DROP_TARGET_2,
    DROP_TARGET_3,
    GOAL,
    FREE_KICK,
    START_BUTTON,
    KICKBACK,
    IN_PLAY
]
# Associate tags with IDs (used in main game loop)
tag_names = {
    BUMPERS: 'bumpers',
    STANDING_TARGETS: 'standing_targets',
    RAMP_SPINNER: 'ramp_spinner',
    DROP_TARGET_1: 'drop_target_1',
    DROP_TARGET_2: 'drop_target_2',
    DROP_TARGET_3: 'drop_target_3',
    GOAL: 'goal',
    FREE_KICK: 'free_kick',
    START_BUTTON: 'start_button',
    KICKBACK: 'kickback',
    IN_PLAY: 'in_play',
    GAME_LOCK: 'game_lock'
}

class PinballPLC():

    QUIT = 0
    LOCK = 1
    UNLOCK = 2

    def __init__(self, data_q: Queue, cmd_q: Queue):
        self.data_q = data_q
        self.cmd_q = cmd_q
        self.plc = PLC(IP)
        self.tag_values = {
            'bumpers': 0,
            'standing_targets': 0,
            'ramp_spinner': 0,
            'drop_target_1': 0,
            'drop_target_2': 0,
            'drop_target_3': 0,
            'goal': 0,
            'free_kick': 0,
            'start_button': 0,
            'kickback': 0,
            'in_play': 0
        }
        request = [(tag, 0) for tag in resettable_tags]
        response = self.plc.Write(request)
    
    def read_loop(self):
        while True:
            request = [(tag, 0) for tag in resettable_tags]
            # Check the command queue
            if not self.cmd_q.empty():
                cmd = self.cmd_q.get() # Maybe set a timeout with exception handling?
                if cmd == self.QUIT:
                    # End the connection and return so the thread manager can 
                    # properly close out the thread
                    self.plc.Close()
                    return
                if cmd == self.LOCK:
                    request.append((GAME_LOCK, True))
                if cmd == self.UNLOCK:
                    request.append((GAME_LOCK, False))
            for tag in self.plc.Read(input_tags):
                self.tag_values[tag_names[tag.TagName]] = tag.Value
            self.data_q.put(self.tag_values)
            response = self.plc.Write(request)


if __name__ == "__main__":
    with PLC(IP) as thing:
        tags = thing.Read(input_tags)
        for tag in tags:
            print(tag)
        print(thing.Read(GAME_LOCK))
