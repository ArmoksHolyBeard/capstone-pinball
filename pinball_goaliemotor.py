'''
Using the Allegro A4988 stepper motor driver.
This only uses two data pins, one for direction and one for step.
A rising edge on the step input moves the motor one step.
There are microstepping options but this iis probably not worth it for this project

TODO: Some sort of step tracking and integration with the two switches to determine goalie position
'''
import time
# import pigpio

# Pin definitions
DIR_PIN = 12
STEP_PIN = 16
RIGHT_SENSOR = 13
LEFT_SENSOR = 15

# Motor directions
RIGHT = 1
LEFT = 0

# Time delay between steps in ms
STEP_DELAY = 0.010
TRIGGER_PULSE_TIME = 0.00001

# Pin setup
# pi.set_mode(DER_PIN, pigpio.OUTPUT)
# pi.set_mode(STEP_PIN, pigpio.OUTPUT)
# pi.set_mode(RIGHT_SENSOR, pigpio.INPUT)
# pi.set_mode(LEFT_SENSOR, pigpio.INPUT)

# Count tracking
count = 0
right_limit = 0
left_left = 0

def step_once():
    # pi.write(STEP_PIN, 1)
    # The A4988 has a minimum pulse width of 1 microsecond for the high-low, we'll use 10
    time.sleep(TRIGGER_PULSE_TIME)
    # pi.write(STEP_PIN, 0)

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
    pass