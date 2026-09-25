from motors import MotorDriver
from MotorDriver import *
from driver import driver
from dynamixel_sdk import *


def motor_timing():
    ids = [0]
    d0 = MotorDriver.MotorDriver(ids, 'COM3')
    c0 = controller(d0)
    c0.driver_start()
    d0.sync_write(ids, ADDR_PROFILE_ACCELERATION, [5 for i in ids])
    velocities = [50, 90.5, 200, 2500]

    experiment_num = 0
    try:
        # main control loop
        while True:
            print("Press any key to continue! (or press ESC to quit!)")
            if getch() == chr(0x1b):
                c0.driver_stop()
                break
            else:
                print("Experiment #%d" % experiment_num)
                for velo in velocities:
                    d0.sync_write(ids, ADDR_PROFILE_VELOCITY, [velo for i in ids])
                    if getch() == chr(0x1b):
                        break
                    traj_apply = c0.sync_movement_no_ts(ids, [0], [[-75]])
                    if not traj_apply:
                        # error occurred in driver
                        quit()

                    angle_target = [[75]]
                    # time in milliseconds
                    time_start = time.time() * 1000
                    traj_apply = c0.sync_movement_no_ts(ids, [0], angle_target)
                    print("Profile Velocity: %d, Time: %dms" %
                          (velo, int((time.time() * 1000) - time_start)))
                    if not traj_apply:
                        # error occurred in driver
                        quit()
                experiment_num += 1
    except KeyboardInterrupt:
        print "Interrupted by keyboard interrupt, closing driver"
        c0.driver_stop()


if __name__ == "__main__":
    motor_timing()







