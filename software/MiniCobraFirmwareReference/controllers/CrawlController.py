import threading
from utils import Conversions as cn
from constants.motor_constants import *
from controllers.SubController import SubController


class CrawlController(SubController):
    def __init__(self, driver, state):
        SubController.__init__(self, driver, state)
        self._last_idx = 0
        self._crawlin = False
        self._crawlin_stop = threading.Event()
        self._crawlin_ctl_thread = None
        self._prof_velo = 88
        self._prof_accel = 0

    def crawl_entry(self, dir=CRAWL_FWD):
        """
        External function call for Controller class to interact with.
        """

        if dir < 0 or dir > CRAWL_BACK:
            raise ValueError("dir is out of range, dir is %d" % dir)

        if self._crawlin:
            self.halt_crawl()
        else:
            if self._crawlin_ctl_thread is not None:
                self.halt_crawl()
            self._crawlin = True
            self._crawlin_stop.clear()
            self._crawlin_ctl_thread = threading.Thread(target=self._start_crawl, args=(dir,))
            self.config_profile()
            self.set_state("CRAWL")
            self._crawlin_ctl_thread.start()

    def config_profile(self):
        """
        Configure the profile with the stored profile acceleration and profile velocity
        to avoid errors with movement.
        """
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_ACCELERATION, [int(self._prof_accel) for i in JOINT_IDS])
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_VELOCITY, [int(self._prof_velo) for i in JOINT_IDS])

    def _phase_swap(self, angles):
        # Crawl phase angles for 8 motors
        angles = [
            [30, 45, 0, 0, -30, -45, 0, 0],
            [0, 0, 30, 45, 0, 0, -30, -45],
            [-30, -45, 0, 0, 30, 45, 0, 0],
            [0, 0, -30, -45, 0, 0, 30, 45]
        ]
        return angles

    def _start_crawl(self, dir):
        """
        Crawling, state, restores the cached

        """
        if dir < CRAWL_FWD or dir > CRAWL_BACK:
            raise ValueError("dir is out of range, dir is %d" % dir)

        # Crawl angles for 8 motors
        angles = [
            [0, 0, 30, 45, 0, 0, -30, -45],
            [30, 45, 0, 0, -30, -45, 0, 0],
            [0, 0, -30, -45, 0, 0, 30, 45],
            [-30, -45, 0, 0, 30, 45, 0, 0]
        ]

        if dir == CRAWL_BACK:
            angles = self._phase_swap(angles)
        if dir == CRAWL_CW or dir == CRAWL_CCW:
            angles.reverse()

        while self._crawlin:
            index = self._last_idx % len(angles)
            positions = [cn.angle_to_pos(angle) for angle in angles[index]]
            self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION, positions)
            if self._crawlin_stop.wait(0.50):
                # returns true if we break out of crawling
                index += 1
                self._last_idx = index
                break
            index += 1
            self._last_idx = index

    def halt_crawl(self):
        """
        Halt crawling motion and join control thread.
        """

        self._crawlin = False
        self._crawlin_stop.set()
        if self._crawlin_ctl_thread is not None and self._crawlin_ctl_thread.isAlive():
            self._crawlin_ctl_thread.join()
        if self.get_state() != "HEX":
            self.set_state("SNAKE")

