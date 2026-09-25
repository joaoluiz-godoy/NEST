from motors.controllers.CoreController import *
from motors.utils import getch
from motors.MotorDriver import MotorDriver
from motors.dynamixel_sdk import *
from motors.constants.motor_constants import *
import os
from motors.utils import Conversions as cn
"""
Run this test to transform into hex shape
"""

dev_name = DEVICE_NAME
if os.name == "nt":
    dev_name = "COM3"
    
def hex_test():
    ids = range(0, 11)
    d0 = MotorDriver(ids, dev_name, cobra_mini=True)
    c0 = Controller(d0)

    # c0.driver_start()
    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [1000 for i in ids])
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [4 for i in ids])

    """
    CHANGE angles IF YOU WANT TO EXPLORE OTHER FORMATIONS OF HEXAGON
    """
    angles = [
        [0, 0, 60, 0, 60, 0, 60, 0, 60, 0, 60],
        #[47.5, 0, 47.5, 0, 85, 0, 47.5, 0, 47.5, 0, 85],
        #[0, 0, 60, 0, 60, 0, 60, 0, 60, 0, 60],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    num_steps = len(angles)

    try:
        i = 0
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            #present_current = d0.sync_read(ids, ADDR_PRESENT_CURRENT)
            #print("Current: " + str(present_current))
            positions = [cn.angle_to_pos(angle) for angle in angles[i]]
            d0.sync_write(ids, ADDR_GOAL_POSITION, positions)
            i = (i + 1) % num_steps
            time.sleep(0.5)
        d0.sync_write(ids, ADDR_GOAL_POSITION, [2048 for i in ids])
        c0.driver_stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()
        
def spiral_test():
    ids = range(0, 11)
    d0 = MotorDriver(ids, 'COM3', cobra_mini=True)
    c0 = Controller(d0)

    # c0.driver_start()
    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [1000 for i in ids])
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [10 for i in ids])

    """
    CHANGE angles IF YOU WANT TO EXPLORE OTHER FORMATIONS OF HEXAGON
    """
    """
    angle_max = 83
    for i in range(6):
    """    
    angles = [
        [83, 83, -83, 83, -83, -83, -83, -83, 83, -83, 83],
        [50, 50, -50, 50, -50, -50, -50, -50, 50, -50, 50],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    num_steps = len(angles)

    try:
        i = 0
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            #present_current = d0.sync_read(ids, ADDR_PRESENT_CURRENT)
            #print("Current: " + str(present_current))
            positions = [cn.angle_to_pos(angle) for angle in angles[i]]
            d0.sync_write(ids, ADDR_GOAL_POSITION, positions)
            i = (i + 1) % num_steps
            time.sleep(0.5)
        d0.sync_write(ids, ADDR_GOAL_POSITION, [2048 for i in ids])
        c0.driver_stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()

def trajectory_tests_no_timing():
    ids = range(0, 11)
    d0 = MotorDriver(ids, 'COM3')
    c0 = Controller(d0)

    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [1000 for i in ids])
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [10 for i in ids])

    angles = [
        [0, 0, 30, 60, 0, 0, -30, -60, 0, 0, 30],
        [30, 60, 0, 0, -30, -60, 0, 0, 30, 60, 0],
        [0, 0, -30, -60, 0, 0, 30, 60, 0, 0, -30],
        [-30, -60, 0, 0, 30, 60, 0, 0, -30, -60, 0]
    ]


    try:
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            # time in milliseconds
            time_start = time.time() * 1000

            traj_apply = c0.sync_movement_no_ts(ids, [0, 0.5, 1, 1.5], angles)
            print("Time taken: %dms" % int((time.time() * 1000) - time_start))
            if not traj_apply:
                # error occured in driver
                quit()
        c0.driver_stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()


def traj_timing_tests():
    # use this one for all 11 motors
    ids = range(0, 11)
    # use this one for subset of motors
    ids = range(0, 11)
    d0 = MotorDriver(ids, 'COM3')
    c0 = Controller(d0)

    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [1000 for i in ids])
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [10 for i in ids])

    time_series = [0.5, 1, 1.5, 3]
    angles = [
        [0, 0, 30, 60, 0, 0, -30, -60, 0, 0, 30],
        [30, 60, 0, 0, -30, -60, 0, 0, 30, 60, 0],
        [0, 0, -30, -60, 0, 0, 30, 60, 0, 0, -30],
        [-30, -60, 0, 0, 30, 60, 0, 0, -30, -60, 0]
    ]
    """
    angles = [
        [0, 0, 30, 60, 0, 0],
        [30, 60, 0, 0, -30, -60],
        [0, 0, -30, -60, 0, 0],
        [-30, -60, 0, 0, 30, 60]
    ]
    """
    try:
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            # time in milliseconds
            time_start = time.time() * 1000

            traj_apply = c0.sync_movement(ids, time_series, angles)
            print("Total Time: %dms" % int((time.time() * 1000) - time_start))
            if not traj_apply:
                # error occurred in driver
                quit()
        c0.driver_stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()

def hex_timing_tests():
    # use this one for all 11 motors
    ids = range(0, 11)
    # use this one for subset of motors
    ids = range(0, 11)
    d0 = MotorDriver(ids, 'COM3')
    c0 = Controller(d0)

    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [1000 for i in ids])
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [10 for i in ids])

    time_series = [0.3, 0.6]
    angles = [
        [60, 0, 60, 0, 60, 0, 60, 0, 60, 0, 60],
        [47.5, 0, 47.5, 0, 85, 0, 47.5, 0, 47.5, 0, 85],
    ]
    """
    angles = [
        [0, 0, 30, 60, 0, 0],
        [30, 60, 0, 0, -30, -60],
        [0, 0, -30, -60, 0, 0],
        [-30, -60, 0, 0, 30, 60]
    ]
    """
    try:
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            # time in milliseconds
            time_start = time.time() * 1000

            traj_apply = c0.sync_movement(ids, time_series, angles)
            print("Total Time: %dms" % int((time.time() * 1000) - time_start))
            if not traj_apply:
                # error occurred in driver
                quit()
        c0.driver_stop()

    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()


def assertion_tests():

    assert cn.angle_to_pos(0) == ZERO_POSITION
    assert cn.angle_to_pos(90) == 3072
    assert cn.angle_to_pos(-90) == 1024
    print("Assertion tests passed!")

    assert cn.pos_to_angle(3072) == 90.0
    print(str(cn.pos_to_angle(3072)) + str(cn.pos_to_angle(1024)))
    print("ZERO: " + str(cn.pos_to_angle(ZERO_POSITION)))
    print("MIN: " + str(cn.pos_to_angle(MIN_POSITION)))
    print("MAX: " + str(cn.pos_to_angle(MAX_POSITION)))

"""
def sidewind_interpolate_test():
    ids = range(0, 11)

    # if using Mac, change COM3 to whatever shows up when you type "ls /dev/tty.usb*" in terminal.
    d0 = MotorDriver(ids, '/dev/tty.usbserial-FT6RW5MF')
    c0 = Controller(d0)

    c0.driver_start()
    try:
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                break
            # time in milliseconds
            time_start = time.time() * 1000
            c0.interpolate_sidewind(ids, 4)
            c0.zero()
            print("Total Time: %dms" % int((time.time() * 1000) - time_start))
        c0.driver_stop()
    except KeyboardInterrupt:
        print("Interrupted by keyboard interrupt, closing driver")
        c0.driver_stop()
"""

if __name__ == "__main__":
    # spiral_test()
    hex_test()






