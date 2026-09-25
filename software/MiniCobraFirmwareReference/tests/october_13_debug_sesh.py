from motors.MotorDriver import MotorDriver
from motors.constants.motor_constants import *
import os

dev_name = DEVICE_NAME
if os.name == "nt":
    dev_name = "COM3"

def sample_0():
    driver = MotorDriver([i for i in range(12)], dev_name, cobra_mini=False)
    driver.start()

    print("output: %s" % driver.sync_read(JOINT_IDS, ADDR_PRESENT_POSITION))
    driver.stop()

sample_0()
