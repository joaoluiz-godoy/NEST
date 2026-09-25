import sys

import argparse

from MotorDriver import MotorDriver
from controllers.CoreController import Controller
from constants.motor_constants import*
import os
from KeypressInterface import KeypressInterface
from logger import DriverLogger
from tests.MockDriver import MockDriver
import threading


dev_name = DEVICE_NAME
if os.name == "nt":
    dev_name = "COM3"

LOGGER_ADDRESSES = {"current": ADDR_PRESENT_CURRENT, "position": ADDR_PRESENT_POSITION,
                    "velocity": ADDR_PRESENT_VELOCITY, "voltage": ADDR_PRESENT_INPUT_VOLTAGE,
                    "temperature": ADDR_PRESENT_TEMPERATURE}

                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test with logger")


    targets = list(LOGGER_ADDRESSES.keys())
    targets.append("all")
    parser.add_argument('log_target', choices = targets)
    parser.add_argument('filename', type=str)
    parser.add_argument("--mock", action='store_true')

    args = parser.parse_args()

    driver = None
    if args.mock:
        driver = MockDriver([i for i in range(12)])
    else:
        driver = MotorDriver([i for i in range(12)], dev_name, cobra_mini=False)
        
    controller = Controller(driver)

    interface = KeypressInterface(controller)
    motor_control_thread = threading.Thread(target=interface.run)
    motor_control_thread.start()
    if args.log_target == "all":

        loggers = []
        for target in LOGGER_ADDRESSES:
            logger = DriverLogger(driver, controller)
            loggers.append(logger)
            filename = "dumps/%s_%s.csv" % (args.filename, target)
            print(filename)
            logger.start_threadrunner(LOGGER_ADDRESSES[target], filename)
        for logger in loggers:
            logger.join_thread()
    else:
        filename = "dumps/" + args.filename + ".csv"
        logger = DriverLogger(driver, controller)
        logger.start_threadrunner(LOGGER_ADDRESSES[args.log_target], filename)
        logger.join_thread()
    motor_control_thread.join()