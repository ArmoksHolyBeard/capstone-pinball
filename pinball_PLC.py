''' The set of functions for communicating with the PLC'''
from queue import Queue
from time import sleep

from pylogix import PLC

# IP address of the PLC, hardcoded for now
IP = '10.230.55.126'

# Put all tag addresses here as constants
IN_PLAY = "Program:MainProgram.Life_Counter.ACC"
BUMPER_01 = "Program:MainProgram.B1C.ACC"
BUMPER_02 = "Program:MainProgram.B2C.ACC"
BUMPER_03 = "Program:MainProgram.B3C.ACC"
STANDING_TARGETS = "Program:MainProgram.STC.ACC"
RAMP_SPINNER = "Program:MainProgram.RampC.ACC"
DROP_TARGETS = "Program:MainProgram.DTS.ACC"
KICKBACK = "Program:MainProgram.KBC.ACC"
GOAL = "Program:MainProgram.GC.ACC"

# TODO: Tags for system enable, start button, maybe flippers
SYSTEM_ENABLE = "foo"
FREE_KICK = "bar"
START_BUTTON = "quux"

# Create list of tags
score_tags = [
    BUMPER_01,
    BUMPER_02,
    BUMPER_03,
    STANDING_TARGETS,
    RAMP_SPINNER,
    DROP_TARGETS,
    KICKBACK,
    GOAL
]
all_tags = [
    IN_PLAY,
    BUMPER_01,
    BUMPER_02,
    BUMPER_03,
    STANDING_TARGETS,
    RAMP_SPINNER,
    DROP_TARGETS,
    KICKBACK,
    GOAL
]
# Associate tags with IDs (used in main game loop)
tag_names = {
    SYSTEM_ENABLE: "system_enable",
    START_BUTTON: "start_button",
    IN_PLAY: 'in_play',
    BUMPER_01: 'bumper1',
    BUMPER_02: 'bumper2',
    BUMPER_03: 'bumper3',
    STANDING_TARGETS: 'standing_targets',
    RAMP_SPINNER: 'ramp_spinner',
    DROP_TARGETS: 'drop_targets',
    KICKBACK: 'kickback',
    FREE_KICK: "free_kick",
    GOAL: 'goal'
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
            'system_enable': 0,
            'start_button': 0,
            'in_play': 0,
            'bumper_1': 0,
            'bumper_2': 0,
            'bumper_3': 0,
            'standing_targets': 0,
            'ramp_spinner': 0,
            'drop_targets': 0,
            'kickback': 0,
            'free_kick': 0,
            'goal': 0
        }
    
    def _read(self):
        current_tags = self.plc.Read(all_tags)
        for tag in current_tags:
            self.tag_values[tag_names[tag.TagName]] = tag.Value
        return self.tag_values
    
    def _toggle_lock(self, enabled: bool):
        response = self.plc.Write(SYSTEM_ENABLE, enabled)
    
    def _reset_tags(self):
        request = [(tag, 0) for tag in score_tags]
        request.append(())
        response = self.plc.Write(request)
        # TODO: Error checking on response
    
    def read_loop(self):
        while True:
            # Check the command queue
            if not self.cmd_q.empty():
                cmd = self.cmd_q.get() # Maybe set a timeout with exception handling?
                if cmd == self.QUIT:
                    # End the connection and return so the thread manager can 
                    # properly close out the thread
                    self.plc.Close()
                    return
                if cmd == self.LOCK:
                    self._toggle_lock(True)
                if cmd == self.UNLOCK:
                    self._toggle_lock(False)
            for tag in self.plc.Read(all_tags):
                self.tag_values[tag_names[tag.TagName]] = tag.Value
            self.data_q.put(self.tag_values)
            request = [(tag, 0) for tag in score_tags]
            reset_in_play = 1 if self.tag_values['in_play'] > 0 else 0
            request.append((IN_PLAY, reset_in_play))
            response = self.plc.Write(request)

if __name__ == "__main__":
    with PLC() as thing:
        devices = thing.Discover()
        for device in devices.Value:
            print(device)
    if input("Continue? (y/n)").lower() == "y":
        test_Q1 = Queue()
        test_Q2 = Queue()
        test_PLC = PinballPLC(test_Q1, test_Q2)
        print(test_PLC._read())
        print(test_PLC._reset_tags())
        print()
        if input("Continue? (y/n)").lower() == "y":
            for i in range(20):
                for tag, value in test_PLC._read().items():
                    print(f"{tag}: {value}")
                print()
                sleep(0.5)
        test_PLC._end()