""" Game program for a pinball machine """

__author__ = 'Ian Means'

import sys
from queue import Queue
import concurrent.futures

from pinball_game import PinballManager
from pinball_PLC import PinballPLC
from pinball_goaliemotor import MotorController


# Create the data queues for PLC and motor controls
plc_data_q = Queue()
plc_cmd_q = Queue()
motor_q = Queue()

# Set up pinball game
game = PinballManager(plc_data_q, plc_cmd_q, motor_q)

# Set up PLC comms
plc = PinballPLC(plc_data_q, plc_cmd_q, demo_mode=True) #demo_mode=True

# Set up goalie motor controls
motor = MotorController(motor_q)

def thread_manager():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        ex.submit(game.run_game)
        ex.submit(plc.read_loop)
        ex.submit(motor.run_motor)
    sys.exit()

if __name__ == '__main__':
    thread_manager()