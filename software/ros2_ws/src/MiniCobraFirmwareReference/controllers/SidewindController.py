import threading
from constants.motor_constants import *
import math
from utils import Conversions as cn
from controllers.SubController import SubController

class SidewindController(SubController):
    """
    Encapsulates all multithreaded behavior for sidewinding motion and pattern generation.
    """
    def __init__(self, driver, state):
        SubController.__init__(self, driver, state)

        # self.driver_lock = driver_lock
        self.driver_lock = threading.Lock()

        # default values (adjusted for mini-cobra)
        self.prof_accel = math.ceil(0.30 * MAX_PROF_ACCEL)
        self.prof_velo = math.ceil(0.30 * MAX_PROF_VELO)
        self.theta = 45  # Reduced from 75 for better sidewinding motion
        self.period = 2.5
        self.create_profile(self.theta, self.period)

        # sw state variables
        self.sidewinding = False
        self.sidewind_stop = threading.Event()
        self.sidewind_ctl_thread = None

    def config_profile(self):
        """
        Configure the profile with the stored profile acceleration and profile velocity
        to avoid errors with movement.
        """
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_ACCELERATION, [int(self.prof_accel) for i in JOINT_IDS])
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_VELOCITY, [int(self.prof_velo) for i in JOINT_IDS])

    def create_profile(self, theta, period):
        """
        adjusts prof_accel and prof_velo to produce the wave defined by theta and period

        :param theta: angle measurement of the bending of the snake motors, amplitude of wave in degrees
        :param period: the time to finish an entire sine wave cycle of movement

        """
        if theta < SIDEWIND_LOWER_BOUND or theta > SIDEWIND_UPPER_BOUND:
            raise ValueError("theta must be between %d and %d, theta is %f"
                             % (SIDEWIND_LOWER_BOUND, SIDEWIND_UPPER_BOUND, theta))
        if period < PERIOD_LOWER_BOUND or period > PERIOD_UPPER_BOUND:
            raise ValueError("period must be between %f and %f, period is %f"
                             % (PERIOD_LOWER_BOUND, PERIOD_UPPER_BOUND, period))

        # kinematic formula is 2 * Theta [degrees] / (period [seconds] / 4) = ang_accel [deg/s^2],
        # derived from delta_Theta = ang_velo_0 * time + (1/2) * ang_accel * time^2,
        # so ang_accel = 2 * delta_Theta / (time ^ 2)
        # given that ang_velo_0, or starting angular velocity is 0
        ang_accel = 2.0 * theta / ((period / 4.0)**2)
        prof_accel = int(math.ceil(cn.ang_accel_to_profile(ang_accel)))
        if prof_accel < 0 or prof_accel > MAX_PROF_ACCEL:
            raise ValueError("prof_accel value %f out of range, max: %d" % (prof_accel, MAX_PROF_ACCEL))

        # finding profile velocity
        ang_velo = ang_accel * (period / 4.0)
        prof_velo = int(math.ceil(cn.ang_velo_to_profile(ang_velo)))
        if prof_velo < 0 or prof_velo > MAX_PROF_VELO:
            raise ValueError("prof_velo value %f out of range, max: %d" % (prof_velo, MAX_PROF_VELO))

        # use driver object for updating all motors
        self.driver_lock.acquire()
        self.config_profile()
        self.driver_lock.release()
        self.theta = theta
        self.period = period
        self.prof_accel = prof_accel
        self.prof_velo = prof_velo

    def sidewind_entry(self, dir=FWD_DIRECTION):
        """
        Start sidewinding function and join existing threads and sidewind_ctl_thread
        if sidewinding was previously happening.

        sidewind_ctl_thread is the thread that holds start_sidewind in a perpetual
        while loop until receiving the halt signal.

        Returns immediately after calling.
        """
        if self.sidewinding == True:
            self.halt_sidewind()
        else:
            if self.sidewind_ctl_thread is not None:
                self.halt_sidewind()
            self.sidewinding = True
            self.sidewind_stop.clear()
            self.sidewind_ctl_thread = threading.Thread(target=self._start_sidewind, args=(dir,))
            self.config_profile()
            self.set_state("SIDEWIND")
            self.sidewind_ctl_thread.start()


    def _pattern_generator(self, id, amp, start_time):
        """
        Continuously produce pattern until done.
        :param id: motor ID that is being used
        :param amp: percentage of wave amplitude from self.theta that this pattern generator
            will produce
        :param start_time: "where" in the cycle the pattern generator is going to start at

        """
        if id == LATCH_ID:
            raise ValueError("id cannot be LATCH_ID: %d" % LATCH_ID)
        if id not in JOINT_IDS:
            raise ValueError("invalid id: %d" % id)
        if amp < 0.0 or amp > 1.0:
            raise ValueError("amp must be between 0 and 1, amp is: %f" % amp)
        local_time = start_time % self.period

        # assuming sine function, end of first quarter of period is where the peak is,
        # end of third quarter is where the trough is
        ts_write_one = self.period * 0.25
        # pos_write_one is position of peak
        pos_write_one = int(math.ceil(cn.angle_to_pos(self.theta * amp)))
        ts_write_two = self.period * 0.75
        # pos_write_two is position of trough
        pos_write_two = int(math.ceil(cn.angle_to_pos(-self.theta * amp)))
        """
        print("pos_write_one : %s" % pos_write_one)
        print("pos_write_two : %s" % pos_write_two)
        """

        approaching_cycle_one = (local_time < ts_write_one)
        self.driver_lock.acquire()
        # issue a write to just go to the closest between peak and trough
        if approaching_cycle_one:
            self.driver_obj.single_write(id, ADDR_GOAL_POSITION, pos_write_one)
        else:
            self.driver_obj.single_write(id, ADDR_GOAL_POSITION, pos_write_two)
        self.driver_lock.release()
        approaching_cycle_one = not approaching_cycle_one

        while self.sidewinding:
            # if cycling is True, then we behave normally
            if approaching_cycle_one:
                # hit the timestamp, need to go to the other one...
                if ts_write_one - 0.05 < local_time < ts_write_one + 0.05:
                    self.driver_lock.acquire()
                    self.driver_obj.single_write(id, ADDR_GOAL_POSITION, pos_write_two)
                    self.driver_lock.release()
            else:
                if ts_write_two - 0.05 < local_time < ts_write_two + 0.05:
                    self.driver_lock.acquire()
                    self.driver_obj.single_write(id, ADDR_GOAL_POSITION, pos_write_one)
                    self.driver_lock.release()
            approaching_cycle_one = not approaching_cycle_one
            if self.sidewind_stop.wait(0.05):
                # returns true if we break out of sidewinding
                break
            local_time = (local_time + 0.05) % self.period

    def _start_sidewind(self, dir=FWD_DIRECTION):
        """
            Enable sidewinding until told to stop.
            :param dir: being either FWD, LEFT, or RIGHT

            :returns pointer to main thread
        """
        if dir < 0 or dir > max(LEFT, RIGHT):
            raise ValueError("dir is out of bounds, dir is %d" % dir)
        threads = []
        curr_amp = 1.0
        curr_time = 0.0
        id_ordered = JOINT_IDS
        if dir == LEFT:
            # reverse the order of "staggering" when going different direction
            id_ordered.reverse()
        for id in id_ordered:
            if id % 2 != 0:
                # vertical joints -- damp these by default by 60%
                threads.append(threading.Thread(target=self._pattern_generator, args=(id, curr_amp * 0.4, curr_time)))
            else:
                # horizontal joints -- these are the ones that are moving "sideways
                threads.append(threading.Thread(target=self._pattern_generator, args=(id, curr_amp, curr_time)))
            # if turning, damp by 10% each time we go "down"
            if dir != FWD_DIRECTION:
                curr_amp *= 0.9
            curr_time += self.period / 3
        for thread in threads:
            thread.start()
        while self.sidewinding:
            if self.sidewind_stop.wait(0.05):
                break
        for thread in threads:
            thread.join()

    def halt_sidewind(self):
        self.sidewinding = False
        self.sidewind_stop.set()
        if self.sidewind_ctl_thread is not None and self.sidewind_ctl_thread.is_alive():
            self.sidewind_ctl_thread.join()
        if self.get_state() != "HEX":
            self.set_state("SNAKE")
