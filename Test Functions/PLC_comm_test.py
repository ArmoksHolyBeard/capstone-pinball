from pycomm3 import LogixDriver
import datetime as dt
import time

PLC_IP = '10.230.49.142'

# CIPDriver.discover()

with open("PLC-Log.txt", "a") as log:
    log.write("****************\n")
    log.write(str(dt.datetime.now()) + "\n")
    
    startTime = time.perf_counter()
    plc = LogixDriver(PLC_IP)
    plc.open()
    endTime = time.perf_counter()
    log.write(f"Time to open comms {endTime - startTime:.3f}s\n")
    
    # with LogixDriver(PLC_IP) as plc:
        # log.write(str(plc) + "\n")
        # log.write(str(plc.tags) + "\n")
        # writeZero = {'data': 0}
        # plc.write("Local:1:I", writeZero)

    tag_list = plc.get_tag_list()
    for tag in tag_list:
        startTime = time.perf_counter()
        plc_data = plc.read(tag["tag_name"])
        endTime = time.perf_counter()
        log.write(f"\t Read {str(plc_data)} in {endTime - startTime:.3f}s\n")
    # print(plc.read("Local:1:I").value['Data'])

    # writeZero = {'Data': 4098, 'Fault': 0}
    # output = plc.write("Local:1:I", writeZero)
    
    plc.close()
    log.write("****************\n\n")
