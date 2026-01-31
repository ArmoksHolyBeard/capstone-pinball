from pycomm3 import LogixDriver
import datetime as dt
import time

PLC_IP = '10.230.49.142'



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

        # *** Cody's test code ***
        # tag_bits = plc_data.value
        # if type(tag_bits) is dict:
        #     try: 
        #         print(tag_bits['Data'])
        #     except KeyError:
        #         print("No Data")


        # # List version
        # inputs = []

        # for bit in range(16):
        #     inputs.append(bool((io_word >> bit) & 1))
        
        if tag["tag_name"] == "Local:1:I":
            tag_bits = int(plc_data.value['Data'])
            # Dictionary version
            plc_inputs = {
                "left_button":  bool((tag_bits >> 0) & 1), # parsing by name
                "right_button": bool((tag_bits >> 2) & 1), 
            }

            if plc_inputs["left_button"]:
                print("Left Button")
            
            if plc_inputs["right_button"]:
                print("Right Button")



        endTime = time.perf_counter()
        log.write(f"\t Read {str(plc_data)} in {endTime - startTime:.3f}s\n")
    
    
    # print(plc.read("Local:1:I").value['Data'])

    # # Write testing
    # writeZero = {'Data': 4098, 'Fault': 0}
    # output = plc.write("Local:1:I", writeZero)
    
    plc.close()
    log.write("****************\n")