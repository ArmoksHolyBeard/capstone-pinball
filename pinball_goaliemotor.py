'''
Using the Allegro A4988 stepper motor driver.
This only uses two data pins, one for direction and one for step.
A rising edge on the step input moves the motor one step.
There are microstepping options but this iis probably not worth it for this project
'''
import time
import math
from random import randint
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

    EXIT = 0
    INDEX = 1
    PAUSE = 2
    DEFEND = 3
    
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
        self.left_step_limit = 0
        self.direction = LEFT
        self.state = self._pause_motor()
        self.endpoints_set = False

        # Default motor to off
        self.disable.value = True

    def _step_once(self):
        if self.direction == RIGHT:
            self.count += 1
        elif self.direction == LEFT:
            self.count -= 1
        
        if (self.endpoints_set
            and (self.count >= self.right_step_limit 
                 or self.count <= self.right_step_limit)
        ):
                self.step_pin.value = True
                time.sleep(TRIGGER_PULSE_TIME)
                self.step_pin.value = False
                time.sleep(TRIGGER_PULSE_TIME)
    
    def _safe_step_once(self):
        if not (self.right_sensor.value or self.left_sensor.value):
            if self.direction == RIGHT:
                self.count += 1
            elif self.direction == LEFT:
                self.count -= 1

            self.step_pin.value = True
            time.sleep(TRIGGER_PULSE_TIME)
            self.step_pin.value = False
            time.sleep(TRIGGER_PULSE_TIME)
            return True
        else:
            return False

    def _set_direction(self, new_direction: int):
        self.direction = new_direction
        self.direction_pin.value = self.direction

    def _index_motor(self):
        self.disable.value = False

        # Get the right side limit
        self._set_direction(RIGHT)
        while not self._safe_step_once():
            time.sleep(SLOW_STEP)
            yield
        self.right_step_limit = self.count
        
        # Get the left limit
        self._set_direction(LEFT)
        while not self._safe_step_once():
            time.sleep(SLOW_STEP)
            yield
        self.left_step_limit = self.count

        # Make the center zero
        count_total = self.right_step_limit - self.left_step_limit
        self.right_step_limit = count_total // 2
        self.left_step_limit = -self.right_step_limit

        self.endpoints_set = True

    def _pause_motor(self):
        self.disable.value = True
        while True:
            yield
    
    def _defend(self):
        self.disable.value = False
        while True:
            target = randint(0, self.right_step_limit)
            if self.count > 0:
                self._set_direction(LEFT)
                target = -target
            else:
                self._set_direction(RIGHT)
            while self.count != target:
                self._safe_step_once()
                time.sleep(FAST_STEP)
                yield
    
    def run_motor(self):
        # TODO: Error handling
        while True:
            if not self.cmd_q.empty():
                next_state = self.cmd_q.get() # Maybe set a timeout with exception handling?
                self.state.close()
                match next_state:
                    case self.EXIT:
                        # Turn off the motor driver and return so the
                        # thread manager can properly close out the thread
                        self.disable.value = True
                        return
                    case self.INDEX:
                        self.state = self._index_motor()
                    case self.PAUSE:
                        self.state = self._pause_motor()
                    case self.DEFEND if self.endpoints_set:
                        self.state = self._defend()
                    case _:
                        self.state = self._pause_motor()
            else:
                try:
                    next(self.state)
                except StopIteration:
                    self.state.close()
                    self.state = self._pause_motor()


if __name__ == "__main__":
    q = Queue()
    motor = MotorController(q)
    motor.disable.value = False
    directions = [RIGHT, LEFT]
    for direction in directions:
        print(f"Moving {direction=}...")
        motor._set_direction(direction)
        decision = input("Move half turn?\n")
        if decision == "q":
            continue
        for i in range(1600):
            if not motor._safe_step_once():
                print("Limit reached")
                break
            time.sleep(SLOW_STEP)
        print(f"Count: {motor.count}")


