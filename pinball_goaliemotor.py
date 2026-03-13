'''
Using the Allegro A4988 stepper motor driver.
This only uses two data pins, one for direction and one for step.
A rising edge on the step input moves the motor one step.
There are microstepping options but this iis probably not worth it for this project

TODO: Some sort of step tracking and integration with the two switches to determine goalie position
'''
import time
import board
import digitalio

# Pin definitions
DIR_PIN = board.D5
STEP_PIN = board.D6
EN_PIN = board.D16
RIGHT_SENSOR = 13
LEFT_SENSOR = 15

# # Motor directions
# RIGHT = 1
# LEFT = 0

# Time delay between steps in ms
STEP_DELAY = 0.1
TRIGGER_PULSE_TIME = 0.1

# Pin setup
rightPin = digitalio.DigitalInOut(DIR_PIN)
rightPin.direction = digitalio.Direction.OUTPUT
stepPin = digitalio.DigitalInOut(STEP_PIN)
stepPin.direction = digitalio.Direction.OUTPUT
enable  = digitalio.DigitalInOut(EN_PIN)
enable.direction = digitalio.Direction.OUTPUT

# Count tracking
count = 0
right_limit = 0
left_left = 0

def step_once():
    stepPin.value = True
    # The A4988 has a minimum pulse width of 1 microsecond for the high-low, we'll use 10
    time.sleep(0.2)
    stepPin.value = False
    time.sleep(0.8)

def setDirection(d):
    if d == 'CW':
        rightPin.value = True
    if d == 'CCW':
        rightPin.value = False

def index_motor():
    # Set the motor direction
    # pi.write(DIR_PIN, RIGHT)
    running = True
    while running:
        step_once()
        count += 1
        time.sleep(STEP_DELAY)
        # running = not pi.read(RIGHT_SENSOR)
    right_limit = count
    
    # Get the left limit
    # pi.write(DIR_PIN, LEFT)
    running = True
    while running:
        step_once()
        count -= 1
        time.sleep(STEP_DELAY)
        # running = not pi.read(LEFT_SENSOR)
    left_left = count

if __name__ == "__main__":
    # Test stuff
    enable.value = False
    directions = ['CW', 'CCW']
    for d in directions:
        setDirection(d)
        for i in range(10):
            step_once()
            #time.sleep(STEP_DELAY)
    enable.value = True
    
