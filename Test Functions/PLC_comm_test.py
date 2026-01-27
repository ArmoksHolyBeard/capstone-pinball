from pycomm3 import LogixDriver
from pycomm3 import CIPDriver
import datetime as dt
import time

PLC_IP = '10.10.10.10'

CIPDriver.discover()

with open("PLC-Log.txt", "a") as log:
    log.write("****************\n")
    log.write(str(dt.datetime.now()) + "\n")
    startTime = time.perf_counter()
    try:
        with LogixDriver(PLC_IP) as plc:
            log.write(str(plc))
            for i in range(5):
                plc.get_module_info(i)
            log.write(str(plc.tags))
    except:
        log.write("Error\n")
    finally:
        endTime = time.perf_counter()
        log.write(f"Test took {endTime - startTime:.3f}s\n")
        log.write("****************\n\n")


# Note from Cody: I believe I found a way to parse the bits of the I/O cards. Posting below. Please note I have not tested this yet 1/27/25.
io_word = 4098  # value read from PLC

inputs = []

for bit in range(16):
    inputs.append(bool((io_word >> bit) & 1))

# Now you have:
# inputs[0] -> Input 0
# inputs[1] -> Input 1
# ...
# inputs[15] -> Input 15

# Another way to do it with Dictionary:
io_word = 4098 # value read from PLC

plc_inputs = { # dictionary for Input card
    "flipper_left":  bool((io_word >> 1) & 1), # parsing by name
    "flipper_right": bool((io_word >> 2) & 1), 
    "bumper_1":      bool((io_word >> 12) & 1),
}
if plc_inputs["bumper_1"]:   # if bumper_1 is activated
    score += 100             # arbitrary score number
    play_sound("bumper.wav") 
# This does not consider debouncing though, not sure how to use Diff_up command in python or if we want to do it on the PLC side.
