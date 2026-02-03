from pylogix import PLC
import datetime as dt
import time

PLC_IP = '10.230.49.142'



with open("PLC-Log.txt", "a") as log:
    log.write("****************\n")
    log.write(str(dt.datetime.now()) + "\n")
    
    startTime = time.perf_counter()
    plc = PLC(PLC_IP)
    endTime = time.perf_counter()
    log.write(f"Time to open comms {endTime - startTime:.3f}s\n")

    tag_list = plc.GetTagList()
    for tag in tag_list.Value:
        
        # Basic data read
        log.write(f"Tag: {tag.TagName}, type: {tag.DataType}\n")

        startTime = time.perf_counter()
        tag_data = plc.Read(tag.TagName)
        endTime = time.perf_counter()
        
        log.write(f"\t{tag_data.Status}, returned {tag_data.Value} after {endTime - startTime:.3f}s\n")

        # *** Cody's test code ***
        # tag_bits = plc_data.value
        # if type(tag_bits) is dict:
        #     try: 
        #         print(tag_bits['Data'])
        #     except KeyError:
        #         print("No Data")
        
        # if tag["tag_name"] == "Local:1:I":
        #     tag_bits = int(plc_data.value['Data'])
        #     # Dictionary version
        #     plc_inputs = {
        #         "left_button":  bool((tag_bits >> 0) & 1), # parsing by name
        #         "right_button": bool((tag_bits >> 2) & 1), 
        #     }

        #     if plc_inputs["left_button"]:
        #         print("Left Button")
            
        #     if plc_inputs["right_button"]:
        #         print("Right Button")
    

    # # Write testing
    # writeZero = {'Data': 4098, 'Fault': 0}
    # output = plc.write("Local:1:I", writeZero)
    
    plc.close()
    log.write("****************\n")