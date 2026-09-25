# thread that runs underneath the program, and reports whatever is desired at a rate of once every 0.25 seconds
import csv
from motors.constants import *
import time
import threading

class DriverLogger:
    def __init__(self, driver):
        self.driver = driver

    def start_threadrunner(self, addr, filename, time_limit, tick_time=0.25):
        thread = threading.Thread(target=self.log_threadrunner,
                                  args=(addr, filename, time_limit),
                                  kwargs={"tick_time" : tick_time})
        thread.start()

    def log_threadrunner(self, addr, filename, time_limit, tick_time=0.25):
        splits = filename.split(".", 1)
        if len(splits) != 2 or splits[1] != "csv":
            raise ValueError("Invalid input: %s, need to have .csv file extension" % filename)
        if addr not in RODATA_ADDR_LENS:
            raise ValueError("Invalid address: %d, need to be in RODATA_ADDR_LENS" % addr)
        rodata_mapping = {ADDR_PRESENT_CURRENT : "crrt", ADDR_PRESENT_VELOCITY : "velo",
                    ADDR_PRESENT_POSITION : "posn", ADDR_PRESENT_INPUT_VOLTAGE : "volt",
                    ADDR_PRESENT_TEMPERATURE : "temp"}
        suffix = rodata_mapping[addr]
        col_names = ["%d_suffix" % id for id in JOINT_IDS]
        col_names.insert(0, "timestamp")
        curr_time = 0.0
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=col_names)
            writer.writeheader()
            while curr_time < time_limit:
                data = self.driver.sync_read(JOINT_IDS, addr)
                tuple_input_list = [(col_names[i + 1], data[i]) for i in range(len(data))]
                tuple_input_list.insert(0, ("timestamp", curr_time))
                writer.writerow(dict(tuple_input_list))
                curr_time += tick_time
                time.sleep(tick_time)
                print("LOGGER -- current time: %f" % curr_time)

        print("LOGGER -- logger threadrunner closed")



