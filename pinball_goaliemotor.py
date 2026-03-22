'''
Using the Allegro A4988 stepper motor driver.
This only uses two data pins, one for direction and one for step.
A rising edge on the step input moves the motor one step.
There are microstepping options but this iis probably not worth it for this project
'''
import time
from queue import Queue

import board
import digitalio

# Time delay between steps in ms
STEP_DELAY = 0.1
TRIGGER_PULSE_TIME = 0.1


class MotorController:

    INDEX = 0
    PAUSE = 1
    DEFEND = 2
    
    dir_pin = digitalio.DigitalInOut(board.D5)
    dir_pin.switch_to_output()

    step_pin = digitalio.DigitalInOut(board.D6)
    step_pin.switch_to_output()

    enable  = digitalio.DigitalInOut(board.D16)
    enable.switch_to_output()

    right_sensor = digitalio.DigitalInOut(board.D13)
    right_sensor.switch_to_input()

    left_sensor = digitalio.DigitalInOut(board.D12)
    left_sensor.switch_to_input()
    
    def __init__(self, data_q: Queue):
        self.data_q = data_q
        self.count = 0
        self.right_step_limit = 0
        self.left_step_left = 0
        self.state = self.disable()
        self.endpoints_set = False

    def step_once(self):
        self.step_pin.value = True
        time.sleep(0.2)
        self.step_pin.value = False
        time.sleep(0.8)

    def setDirection(self, d):
        if d == 'R':
            self.dir_pin.value = True
        if d == 'L':
            self.dir_pin.value = False

    def index_motor(self):
        self.enable.value = True

        # Get the right side limit
        self.setDirection('R')
        while not self.right_sensor.value:
            self.step_once()
            self.count += 1
            time.sleep(STEP_DELAY)
            yield
        self.right_step_limit = self.count
        
        # Get the left limit
        self.setDirection('L')
        while not self.left_sensor.value:
            self.step_once()
            self.count -= 1
            time.sleep(STEP_DELAY)
            yield
        self.left_step_left = self.count
        self.endpoints_set = True

    def disable(self):
        self.enable.value = False
        while True:
            yield
    
    def defend(self):
        while True:
            yield
    
    def run_motor(self):
        # TODO: Error handling and exit condition
        while True:
            if not self.data_q.empty():
                next_state = self.data_q.get()
                self.state.close()
                match next_state:
                    case self.INDEX:
                        self.state = self.index_motor()
                    case self.PAUSE:
                        self.state = self.disable()
                    case self.DEFEND if self.endpoints_set:
                        self.state = self.defend()
                    case _:
                        self.state = self.disable()
            else:
                next(self.state)


if __name__ == "__main__":
    pass