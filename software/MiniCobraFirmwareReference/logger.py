# thread that runs underneath the program, and reports whatever is desired at a rate of once every 0.25 seconds
import csv
from constants import *
import time
import threading


COLUMN_MAPPING = {ADDR_PRESENT_CURRENT : "crrt", ADDR_PRESENT_VELOCITY : "velo",
                    ADDR_PRESENT_POSITION : "posn", ADDR_PRESENT_INPUT_VOLTAGE : "volt",
                    ADDR_PRESENT_TEMPERATURE : "temp"}

class DriverLogger:
    """
    Class to represent logging of driver data while the main driver program
    is running.
    """


    def __init__(self, driver, controller):
        self.driver = driver
        self.controller = controller
        self.thread = None

    def start_threadrunner(self, addr, filename, tick_time=0.10):
        """
        Initialize and start the thread, immediately returning after.

        Args:
            addr (int) : integer representing address, should be within
                RODATA_ADDR_LENS keys
            filename (str) : filename, should denote date and experiment number
            tick_time (float) : time in between samples, default 100ms
        """

        self.thread = threading.Thread(target=self.log_threadrunner,
                                  args=(addr, filename),
                                  kwargs={"tick_time": tick_time})
        self.thread.start()

    def join_thread(self):
        self.thread.join()


    def start_logging(self, motor_ids, addresses, base_filename, tick_time=0.10):
        """
        Start logging for whatever addresses are within addresses.

        Args:
            motor_ids (list[int]) : list of motor IDs to log data for
            addresses (list[int]) : list of integers for addresses to measure
            base_filename (str) : base filename without csv prefix
        """

        # initialize column names for each address to log,
        # open files to write into
        col_names = {}
        file_objects = {}
        for addr in addresses:
            if addr not in RODATA_ADDR_LENS:
                raise ValueError("Invalid address: %d, need to be in RODATA_ADDR_LENS" % addr)
            suffix = COLUMN_MAPPING[addr]

            col_names[addr] = ["%d_%s" % (id, suffix) for id in motor_ids]
            col_names[addr].insert(0, "timestamp")

            file_objects[addr] = open("%s_%s.csv" % (base_filename, suffix), "wb")

        current_time = 0.0

        while self.driver.started:
            try:
                
                # rotate through the different addresses to manage, and then 
                # write a row to each file
                for addr in addresses:
                    pass


                time.sleep(tick_time)

            except Exception as e:
                print("LOGGER -- encountered exception: %s" % (str(e)))
                break

        for key in file_objects:
            file_objects[key].close()
        

        

    def log_threadrunner(self, addr, filename, tick_time=0.10):
        print("starting logger thread with filename: %s and address %d" % (filename, addr))
        """
        splits = filename.split(".", 1)
        if len(splits) != 2 or splits[1] != "csv":
            raise ValueError("Invalid input: %s, need to have .csv file extension" % filename)
        """
        if addr not in RODATA_ADDR_LENS:
            raise ValueError("Invalid address: %d, need to be in RODATA_ADDR_LENS" % addr)
        rodata_mapping = {ADDR_PRESENT_CURRENT : "crrt", ADDR_PRESENT_VELOCITY : "velo",
                    ADDR_PRESENT_POSITION : "posn", ADDR_PRESENT_INPUT_VOLTAGE : "volt",
                    ADDR_PRESENT_TEMPERATURE : "temp"}
        suffix = rodata_mapping[addr]
        col_names = ["%d_%s" % (id, suffix) for id in JOINT_IDS]
        col_names.insert(0, "timestamp")
        curr_time = 0.0

        with open(filename, 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=col_names)
            writer.writeheader()
            while self.driver.started:
                try:
                    data = self.driver.sync_read(JOINT_IDS, addr)
                    tuple_input_list = [(col_names[i + 1], data[i]) for i in range(len(data))]
                    tuple_input_list.insert(0, ("timestamp", curr_time))
                    writer.writerow(dict(tuple_input_list))
                    curr_time += tick_time
                    time.sleep(tick_time)
                    # print("LOGGER -- current time: %f" % curr_time)
                except Exception:
                    print("LOGGER -- encountered exception")
                    break
        print("LOGGER -- logger threadrunner closed")
