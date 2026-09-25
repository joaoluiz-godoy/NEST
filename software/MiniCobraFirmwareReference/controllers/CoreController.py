import sys
sys.path.append("..")

from constants import *
from controllers.TransformController import TransformController
from controllers.SidewindController import SidewindController
from controllers.CrawlController import CrawlController
from controllers.SubController import SubController
from controllers.SurveyController import SurveyController

class Controller(SubController):
    """
    Top level wrappers for sophisticated coordination of joints.
    """
    def __init__(self, driver):
        """
        Create this with a driver object initialized with the right IDs
        """
        SubController.__init__(self, driver, ["SNAKE"])

        self.driver_obj.start()

        # sidewind object:
        self.sidewind_ctl = SidewindController(self.driver_obj, self.state)

        # crawl object
        self.crawl_ctl = CrawlController(self.driver_obj, self.state)

        # survey object
        self.survey_ctl = SurveyController(self.driver_obj, self.state)

        # transform object:
        # Holds Functions for Hexagonal, Spiral, Zero, and Tilt transformations
        self.transform_ctl = TransformController(self.driver_obj, self.state)

    def driver_stop(self):
        """
        Stop the driver, which means that the torque becomes disabled, so motors
        do not attempt to move or maintain position (going limp), and the port is closed.
        """
        self.halt()
        self.driver_obj.stop()

    def reboot_all(self, force_reboot=False):
        """
        Attempt to reboot all motors.

        Args:
            force_reboot : True if we want to reboot motors without sending a halt signal
        """
        if not force_reboot:
            self.halt()
        for id in JOINT_IDS:
            self.driver_obj.reboot_motor(id)
        if not self.driver_obj.is_cobra_mini():
            self.driver_obj.reboot_motor(LATCH_ID)


    """
    Exposing transformation methods and wrapping them in the right procedures.
    """
    def zero_wrapper(self):
        """
        Wrapping TransformController.zero()
        """
        self._transform_handler(self.transform_ctl.zero, "SNAKE")

    def hex_wrapper(self):
        """
        Wrapping TransformController.hex()
        """
        self._transform_handler(self.transform_ctl.hex, "HEX")

    def spiral_wrapper(self):
        """
        Wrapping TransformController.spiral()
        """
        self._transform_handler(self.transform_ctl.spiral, "SPIRAL")

    def tilt_fwd_wrapper(self):
        """
            Wrapping TransformController.tilt(back=False)
        """
        self._transform_handler(self.transform_ctl.tilt, "TILT")

    def tilt_back_wrapper(self):
        """
            Wrapping TransformController.tilt(back=True)
        """
        self._transform_handler(self.transform_ctl.tilt, "TILT", args=(True,))

    def _transform_handler(self, transform_callable, next_state, args=None):
        """
        Prepare everything for a transform -- when we hand off
        control to the Transform Controller function. Ensuring snake
        is not in motion and mutexes are released.

        Args:
            transform_callable : must be a function belonging to TransformController class.
            next_state : state to transform to
            args : arguments for transform_callable
        Returns:
            None, when the transformation finishes
        """
        if next_state not in STATES:
            raise ValueError("Invalid state %s" % next_state)

        if self.get_state() == "SIDEWIND":
            self.sidewind_ctl.halt_sidewind()
        elif self.get_state() == "CRAWL":
            self.crawl_ctl.halt_crawl()
        elif self.get_state() == "HEX" and not (next_state == "TILT" or next_state == "HEX"):
            self.transform_ctl.hex()

        # handle toggles -- reverting them back into SNAKE state
        if next_state == "HEX" and self.get_state() == "HEX":
            next_state = "SNAKE"
        if next_state == "SPIRAL" and self.get_state() == "SPIRAL":
            next_state = "SNAKE"
        # any tilt while already tilted will return to hex
        if next_state == "TILT" and self.get_state() == "TILT":
            next_state = "HEX"

        self.transform_ctl.config_profile()
        if args is not None:
            transform_callable(args)
        else:
            transform_callable()
        """
        # NOTE: transform_callable doesn't return until transformation is finished...
        if next_state != self.get_state():
            raise Exception("ERROR -- intended state: %s, actual state: %s" % (next_state, self.get_state()))
        """
        print("Intended State: %s, Post-Transform State: %s" % (next_state , self.get_state()))

    def crawl_wrapper(self, dir=CRAWL_FWD):
        """
        Exposes crawl start/stop for keyboard/ps4 input.

        """
        if self.get_state() == "HEX" or self.get_state() == "TILT":
            print("Do not start crawling without transforming out of hex")
            return
        if self.get_state() == "SIDEWIND":
            self.sidewind_ctl.halt_sidewind()

        elif self.get_state() == "SURVEY":
            self.survey_ctl.halt_survey()
        self.crawl_ctl.crawl_entry(dir=dir)
    
    def survey_wrapper(self, majorpanning):
        """
        Exposes survey start/stop for keyboard/ps4 input.

        """
        if self.get_state() == "HEX" or self.get_state() == "TILT":
            print("Do not start crawling without transforming out of hex")
            return
        if self.get_state() == "SIDEWIND":
            self.sidewind_ctl.halt_sidewind()
        elif self.get_state() == "CRAWL":
            self.crawl_ctl.halt_crawl()
        
        if majorpanning:
            self.survey_ctl.major_pan()
        else:
            self.survey_ctl.minor_pan()
        self.survey_ctl.survey_entry()

    def start_sidewind_wrapper(self, dir=FWD_DIRECTION):
        """
            Start sidewinding function, with thread functionality delegated to
            the sidewind_ctl object.

            Args:
                dir : direction of sidewinding
            Returns:
                None, immediately after calling.
        """
        if self.get_state() == "HEX" or self.get_state() == "TILT":
            print("Do not start sidewinding without transforming out of hex")
            return
        if self.get_state() == "CRAWL":
            self.crawl_ctl.halt_crawl()
        elif self.get_state() == "SURVEY":
            self.survey_ctl.halt_survey()
        
        self.sidewind_ctl.sidewind_entry(dir)
        

    def halt(self):
        """
        Stop the movement from any sidewinding/crawling/survey states, and break out of
        those states by modifying relevant flags/events (sidewinding, sidewind_stop).

        Freezes movement by reading all positions and then writing those positions back
        into the motors.
        """
        self.sidewind_ctl.halt_sidewind()
        self.crawl_ctl.halt_crawl()
        self.survey_ctl.halt_survey()
        positions = self.driver_obj.sync_read(JOINT_IDS, ADDR_PRESENT_POSITION)
        positions = [int(i) for i in positions]
        self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION, positions)
