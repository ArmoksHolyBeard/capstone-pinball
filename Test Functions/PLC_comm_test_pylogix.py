from pylogix import PLC
import datetime as dt
import time

PLC_IP = '10.230.55.126'

# with open("PLC-Log.txt", "a") as log:
#     log.write("****************\n")
#     log.write(str(dt.datetime.now()) + "\n")
    
#     startTime = time.perf_counter()
plc = PLC(PLC_IP)
#     endTime = time.perf_counter()
#     log.write(f"Time to open comms {endTime - startTime:.3f}s\n")

    # tag_list = plc.GetTagList()
    # for tag in tag_list.Value:
    #     # Basic data read
    #     log.write(f"Tag: {tag.TagName}, type: {tag.DataType}\n")
    #     startTime = time.perf_counter()
    #     tag_data = plc.Read(tag.TagName)
    #     endTime = time.perf_counter()
    #     log.write(f"\t{tag_data.Status}, returned {tag_data.Value} after {endTime - startTime:.3f}s\n")

startTime = time.perf_counter()
target_1_count = plc.Read("Program:MainProgram.BUTTON_CNT.ACC")
if target_1_count.Status == "Success":
    print(f"Counter Value: {target_1_count.Value}")
    ack = plc.Write("Program:MainProgram.BUTTON_CNT.ACC", 0)
    print(f"Writing {ack.Value}, {ack.Status}")
endTime = time.perf_counter()
print(f"Time elapsed: {endTime - startTime:.3f}s")

plc.Close()
# log.write("****************\n")