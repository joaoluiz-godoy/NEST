import sys
sys.path.append("..")

from MotorDriver import MotorDriver
from controllers.CoreController import Controller
from constants.motor_constants import*
import os
from KeypressInterface import KeypressInterface
#from motors.PS4Interface import PS4Interface
#from motors.PS4Interface import PS4Interface


dev_name = DEVICE_NAME
if os.name == "nt":
    dev_name = "COM3"

if __name__ == "__main__":
    driver = MotorDriver([i for i in range(12)], dev_name, cobra_mini=False)

    controller = Controller(driver)

    interface = KeypressInterface(controller)
    interface.run()


    """
    Uncomment to run ps4 controller interface

    ps4controller = PS4Interface(controller, interface="/dev/input/js0", connecting_using_ds4drv=False)
    ps4controller.listen(timeout=60)
    
    """


