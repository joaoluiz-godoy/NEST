import threading
from utils import Conversions as cn, MotorCalculations as mc
from constants.motor_constants import *
from constants.transform_constants import *
from controllers.SubController import SubController
import time

class SurveyController(SubController):
    def __init__(self, driver, state):
        SubController.__init__(self, driver, state)
        self._last_idx = 0
        self.surveypose = False
        self.surveying = False
        self.surveying_stop = threading.Event()
        self.surveying_ctl_thread = None
        self.survey_prof_velo = 250
        self.survey_prof_accel = 0
        self.majorpan = True
        self.minorpan = False

    def survey_entry(self):
        """
        External function call for Controller class to interact with.
        """

        if self.surveying:
            self.halt_survey()
        else:
            if self.surveying_ctl_thread is not None:
                self.halt_survey()
            self.surveying = True
            self.surveying_stop.clear()
            self.surveying_ctl_thread = threading.Thread(target=self._start_survey)
            self.config_profile()
            self.set_state("SURVEY")
            self.enterpose()
            self.surveying_ctl_thread.start()

    def config_profile(self):
        """
        Configure the profile with the stored profile acceleration and profile velocity
        to avoid errors with movement.
        """
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_ACCELERATION, [int(self.survey_prof_accel) for i in JOINT_IDS])
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_VELOCITY, [int(self.survey_prof_velo) for i in JOINT_IDS])

    def major_pan(self):
        # configures the variables the variables so that _start_survey() writes a major pan
        self.majorpan = True
        self.minorpan = False

    def minor_pan(self):
        # configures the variables the variables so that _start_survey() writes a minor pan
        self.majorpan = False
        self.minorpan = True

    def _time_for_move(self, ids, angles):
        """
        Helper function to take in an array of ids and an array of angles, and determine how
        long it will take for the longest difference to be executed, compared to the present positions.

        Args:
            ids: array of ids
            angles: array of angles in degrees, not positions
        Returns:
            time, as a float, for the longest joint angle transition
        """
        if len(ids) != len(angles):
            raise ValueError("Invalid, length of ids %d must match length of angles %d" % (len(ids), len(angles)))
        start_positions = self.driver_obj.sync_read(ids, ADDR_PRESENT_POSITION)
        end_positions = [cn.angle_to_pos(angle) for angle in angles]
        max_delta = abs(start_positions[0] - end_positions[0])

        for i in range(1, len(start_positions)):
            delta = abs(start_positions[i] - end_positions[i])
            if delta > max_delta:
                max_delta = delta
        # now calculate the time it will take to move max_delta in positions
        max_delta = cn.pos_to_angle(max_delta, delta=True)
        # print(max_delta)
        
        return mc.delta_time(max_delta, self.survey_prof_accel, self.survey_prof_velo)
    
    def enterpose(self):
        if self.surveypose:
            self.halt_survey()

        else:
            # Survey pose angles for 8 motors
            poseangles = [-40, 0, -30, 0, 40, 0, 25, 0]
            self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION,
                                        [cn.angle_to_pos(angle) for angle in poseangles])
            self.surveypose = True
            time.sleep(self._time_for_move(JOINT_IDS, poseangles))


    def _start_survey(self):
        """
        Surveying, state, restores the cached

        """
        wagangles = [30, 0, -30, 0]


        while self.surveying:
            index = self._last_idx % len(wagangles)
            position = int(cn.angle_to_pos(wagangles[index]))
            
            if self.majorpan:
                # writes angle to joint 5 for major panning (motor ID 5 exists in our setup)
                self.driver_obj.single_write(5, ADDR_GOAL_POSITION, position)
            elif self.minorpan:
                # writes angle to joint 2 for minor panning (changed from 1 for 8-motor setup)
                self.driver_obj.single_write(2, ADDR_GOAL_POSITION, position)
            else:
                self.halt_survey()

            if self.surveying_stop.wait(0.50):
                # returns true if we break out of surveying
                index += 1
                self._last_idx = index
                break
            index += 1
            self._last_idx = index

    def halt_survey(self):
        """
        Halts survey motion, returns to a zero position in all motors, and joins control thread.
        """
        
        self.surveying = False
        self.surveypose = False
        self.surveying_stop.set()
        if self.surveying_ctl_thread is not None and self.surveying_ctl_thread.is_alive():
            self.surveying_ctl_thread.join()

        self.driver_obj.sync_write(JOINT_IDS,
                                   ADDR_GOAL_POSITION,
                                   [ZERO_POSITION for i in JOINT_IDS])
        time.sleep(self._time_for_move(JOINT_IDS, [0 for i in JOINT_IDS]))

        self.set_state("SNAKE")

