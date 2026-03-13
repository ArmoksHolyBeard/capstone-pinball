'''
Using the Allegro A4988 stepper motor driver.
This only uses two data pins, one for direction and one for step.
A rising edge on the step input moves the motor one step.
There are microstepping options but this iis probably not worth it for this project

TODO: Some sort of step tracking and integration with the two switches to determine goalie position
TODO: Will probably have to make this a coroutine
'''
import time
import board
import digitalio

# Time delay between steps in ms
STEP_DELAY = 0.1
TRIGGER_PULSE_TIME = 0.1

# Pin setup
dir_pin = digitalio.DigitalInOut(board.D5)
dir_pin.switch_to_output()
# dir_pin.direction = digitalio.Direction.OUTPUT

step_pin = digitalio.DigitalInOut(board.D6)
step_pin.switch_to_output()
# step_pin.direction = digitalio.Direction.OUTPUT

enable  = digitalio.DigitalInOut(board.D16)
enable.switch_to_output()
# enable.direction = digitalio.Direction.OUTPUT

right_sensor = digitalio.DigitalInOut(board.D13)
right_sensor.switch_to_input()
# right_sensor = digitalio.Direction.INPUT

left_sensor = digitalio.DigitalInOut(board.D12)
left_sensor.switch_to_input()
# left_sensor = digitalio.Direction.INPUT

# Count tracking
count = 0
right_step_limit = 0
left_step_left = 0

def step_once():
    step_pin.value = True
    # The A4988 has a minimum pulse width of 1 microsecond for the high-low
    time.sleep(0.2)
    step_pin.value = False
    time.sleep(0.8)

def setDirection(d):
    if d == 'R':
        dir_pin.value = True
    if d == 'L':
        dir_pin.value = False

def index_motor():
    enable.value = True

    # Get the right side limit
    setDirection('R')
    while running := (not right_sensor.value):
        step_once()
        count += 1
        time.sleep(STEP_DELAY)
    right_step_limit = count
    
    # Get the left limit
    setDirection('L')
    while running := (not left_sensor.value):
        step_once()
        count -= 1
        time.sleep(STEP_DELAY)
    left_step_left = count

    enable.value = False

if __name__ == "__main__":
    # Test stuff
    enable.value = False
    for d in (directions := ['R', 'L']):
        setDirection(d)
        for i in range(10):
            step_once()
            #time.sleep(STEP_DELAY)
    enable.value = True