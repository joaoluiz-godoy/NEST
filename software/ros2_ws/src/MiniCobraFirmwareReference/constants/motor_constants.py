"""Raw Values"""
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
BAUDRATE = 57600
PROTOCOL_VERSION = 2.0
# min and max might be subject to change based on range of motion
# hard limits -- TODO: change to angle measurements as constants are user facing
MIN_POSITION = 1000
MAX_POSITION = 3000
# TODO: controller constants for soft position limits, 1 or 2 degrees in from the min
# and max
ZERO_POSITION = 2048
# previously was 20, changed to 30 to reduce issues with hanging
DXL_MOVING_STATUS_THRESHOLD = 30
SIDEWIND_LOWER_BOUND = 30
SIDEWIND_UPPER_BOUND = 75
PERIOD_LOWER_BOUND = 2.0
PERIOD_UPPER_BOUND = 8.0
# Mini-cobra: 8 motors with IDs 2-9
JOINT_IDS = [i for i in range(2, 10)]
# whatever is unused in JOINT_IDS
LATCH_ID = 11  # Not used in mini-cobra
LATCH_UNLOCK = 1784
LATCH_LOCK = 1440

# unit for profile acceleration, in rev/min^2
PROF_ACCEL_UNITS = 214.577
# unit for profile velocity in rev/min
PROF_VELO_UNITS = 0.229

# Change device name if we get an error,
# make it whatever shows up when you type "ls /dev/tty.usb*" in terminal.
# adjust for microusb on the Raspi Zero
DEVICE_NAME = '/dev/ttyUSB0'

# directional constants for sidewinding control
FWD_DIRECTION = 0
LEFT = 1
RIGHT = 2

# crawling control
CRAWL_FWD = 0
CRAWL_CW = 1
CRAWL_CCW = 2
CRAWL_BACK = 3

"""
Arbitrary limits for prof accel and velocity, currently set
way above the theoretical sidewinding acceleration and velocity
values
"""
MAX_PROF_ACCEL = 20
MAX_PROF_VELO = 500


"""Writable Data Addresses"""
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_CURRENT = 102
ADDR_GOAL_VELOCITY = 104
ADDR_PROFILE_ACCELERATION = 108
ADDR_PROFILE_VELOCITY = 112
ADDR_GOAL_POSITION = 116

"""
Dictionaries to verify maximum/minimum write values to the addresses

those for goal current, goal_velocity, and torque_enable are from the control table,
and prof_accel, goal_position, prof_velocity are determined by us
"""

WRITABLE_ADDR_MAX_VALS = {}

WRITABLE_ADDR_MIN_VALS = {}

"""Read-only Data Addresses"""
ADDR_PRESENT_CURRENT = 126
ADDR_PRESENT_VELOCITY = 128
ADDR_PRESENT_POSITION = 132
ADDR_PRESENT_INPUT_VOLTAGE = 144
ADDR_PRESENT_TEMPERATURE = 146

"""
Dictionaries to verify if any given address belongs to either class
and provide a lookup for byte length for each address, all in O(1) time.
"""

WRITABLE_ADDR_LENS = {ADDR_TORQUE_ENABLE : 1, ADDR_GOAL_CURRENT : 2,
                      ADDR_GOAL_VELOCITY : 4, ADDR_PROFILE_ACCELERATION : 4,
                      ADDR_PROFILE_VELOCITY : 4, ADDR_GOAL_POSITION : 4}

RODATA_ADDR_LENS = {ADDR_PRESENT_CURRENT : 2, ADDR_PRESENT_VELOCITY : 4,
                    ADDR_PRESENT_POSITION : 4, ADDR_PRESENT_INPUT_VOLTAGE : 2,
                    ADDR_PRESENT_TEMPERATURE : 1}
