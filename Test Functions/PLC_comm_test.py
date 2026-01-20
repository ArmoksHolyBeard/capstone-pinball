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
