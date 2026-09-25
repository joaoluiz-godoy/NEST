import sys
sys.path.append("..")
from MotorDriver import MotorDriver
from constants import *

class MockDriver(MotorDriver):
    """
    Mock class for driver. Initialize motor controller with instance of this class
    whenever one needs to test the controller layer behavior.
    """

    def __init__(self, ids, cobra_mini=False):
        MotorDriver.__init__(self, ids, "MOCK_DRIVER", cobra_mini=cobra_mini)
        self.joint_posns = [2048 for i in self.ids]
        self.started = False

    def single_read(self, id, addr):
        if addr == ADDR_PRESENT_POSITION:
            return self.joint_posns[id]
        else:
            return 777

    def sync_read(self, ids, addr):
        if addr != ADDR_PRESENT_POSITION:
            return [777 for id in ids]
        to_return = []
        for id in ids:
            to_return.append(self.joint_posns[id])
        return to_return

    """
    Start driver, connect controller and motors.
    """

    def start(self):
        self.started = True
        print("Driver started.")

    """
    Stop driver and free resources when finished running.
    """

    def stop(self):
        self.started = False
        print("Driver stopped.")

    """
    Writes a single value of data to the given address for a single motor
    specified with id. 
    """
    def single_write(self, id, addr, data):
        if addr == ADDR_GOAL_POSITION and (id != LATCH_ID) and ((data < MIN_POSITION) or (data > MAX_POSITION)):
            raise Exception("Invalid goal position %d, min: %d, max: %d" % (data, MIN_POSITION, MAX_POSITION))
        if not isinstance(data, int):
            raise Exception("data is not an int")

        if addr == ADDR_GOAL_POSITION:
            self.joint_posns[id] = data
        print("WRITE -- motor ID: %d, addr: %d, data: %d" % (id, addr, data))

    def sync_write(self, ids, addr, data):
        for item in data:
            if not isinstance(item, int):
                raise Exception("item of data is not an int")
            if addr == ADDR_GOAL_POSITION and ((item < MIN_POSITION) or (item > MAX_POSITION)):
                raise Exception("Invalid goal position %d, min: %d, max: %d" % (data, MIN_POSITION, MAX_POSITION))
        for i in range(len(ids)):
            if addr == ADDR_GOAL_POSITION:
                self.joint_posns[i] = data[i]
        print("SYNC_WRITE -- ids: %s, addr: %d, data: %s" % (str(ids), addr, str(data)))

    def reboot_motor(self, id):
        print("REBOOT -- id: %d" % id)