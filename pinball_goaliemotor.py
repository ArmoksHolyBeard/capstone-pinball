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

# Time delay between steps in s
TRIGGER_PULSE_TIME = 0.000005
FAST_STEP = 0.000010
SLOW_STEP = 0.000020

# Linear direction of the goalie
RIGHT = False
LEFT = True

# 3200 counts is one full rotation

class MotorController:

    INDEX = 0
    PAUSE = 1
    DEFEND = 2
    
    direction_pin = digitalio.DigitalInOut(board.D5)
    direction_pin.switch_to_output()

    step_pin = digitalio.DigitalInOut(board.D6)
    step_pin.switch_to_output()

    disable  = digitalio.DigitalInOut(board.D16)
    disable.switch_to_output()

    right_sensor = digitalio.DigitalInOut(board.D13)
    right_sensor.switch_to_input()

    left_sensor = digitalio.DigitalInOut(board.D12)
    left_sensor.switch_to_input()
    
    def __init__(self, cmd_q: Queue):
        self.cmd_q = cmd_q
        self.count = 0
        self.right_step_limit = 0
        self.left_step_left = 0
        self.direction = LEFT
        self.state = self._disable_motor()
        self.endpoints_set = False

    def _step_once(self):
        if self.direction == RIGHT:
            self.count += 1
        elif self.direction == LEFT:
            self.count -= 1
        
        if not (
            self.endpoints_set
            and (
                self.count >= self.right_step_limit
                or self.count <= self.right_step_limit
            )
        ):
            self.step_pin.value = True
            time.sleep(TRIGGER_PULSE_TIME)
            self.step_pin.value = False
            time.sleep(TRIGGER_PULSE_TIME)

    def _set_direction(self, new_direction: int):
        self.direction = new_direction
        self.direction_pin.value = self.direction

    def _index_motor(self):
        self.disable.value = True

        # Get the right side limit
        self._set_direction(RIGHT)
        while not self.right_sensor.value:
            self._step_once()
            time.sleep(FAST_STEP)
            yield
        self.right_step_limit = self.count
        
        # Get the left limit
        self._set_direction(LEFT)
        while not self.left_sensor.value:
            self._step_once()
            time.sleep(FAST_STEP)
            yield
        self.left_step_left = self.count
        self.endpoints_set = True

    def _disable_motor(self):
        self.disable.value = True
        while True:
            yield
    
    def _defend(self):
        self.disable.value = False
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
                        self.state = self._index_motor()
                    case self.PAUSE:
                        self.state = self._disable_motor()
                    case self.DEFEND if self.endpoints_set:
                        self.state = self._defend()
                    case _:
                        self.state = self._disable_motor()
            else:
                next(self.state)


if __name__ == "__main__":
    q = Queue()
    motor = MotorController(q)
    motor.disable.value = False
    for i in range(4):
        motor._set_direction(RIGHT)
        for j in range(800):
            motor._step_once()
            time.sleep(SLOW_STEP)
        motor._set_direction(LEFT)
        for k in range(400):
            motor._step_once()
            time.sleep(FAST_STEP)
    motor.disable.value = True

