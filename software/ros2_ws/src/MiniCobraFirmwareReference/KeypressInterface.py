from utils import getch
from constants.motor_constants import *

class KeypressInterface:
    def __init__(self, controller):
        self.controller = controller

    def run(self):
        try:
            # main control loop
            while True:
                print("Commands:\n\tw / a / d : sidewind fwd / left / right\n\th : halt\n\tz : zero"
                      "\n\te : spiral toggle\n\tx : hexagon toggle\n\tt : tilt forward toggle"
                      "\n\ty : tilt backwards toggle\n\tc / v / b / n : crawling fwd / back / ccw / cw "
                      "\n\tk : reboot\n\tj : force reboot"
                      "\n\ts : survey major panning\n\tf : survey minor panning"
                      "\n(or press ESC to quit!)\n")
                char = getch()
                print("INPUT: %s\n" % char)
                if char == "w":
                    self.controller.start_sidewind_wrapper()
                elif char == "a":
                    self.controller.start_sidewind_wrapper(dir=LEFT)
                elif char == "d":
                    self.controller.start_sidewind_wrapper(dir=RIGHT)
                elif char == "h":
                    self.controller.halt()
                elif char == "z":
                    self.controller.zero_wrapper()
                elif char == "e":
                    self.controller.spiral_wrapper()
                elif char == "x":
                    self.controller.hex_wrapper()
                elif char == "t":
                    self.controller.tilt_fwd_wrapper()
                elif char == "y":
                    self.controller.tilt_back_wrapper()
                elif char == "c":
                    self.controller.crawl_wrapper()
                elif char == "s":
                    self.controller.survey_wrapper(True)
                elif char == "f":
                    self.controller.survey_wrapper(False)
                elif char == "v":
                    self.controller.crawl_wrapper(dir=CRAWL_BACK)
                elif char == "b":
                    self.controller.crawl_wrapper(dir=CRAWL_CCW)
                elif char == "n":
                    self.controller.crawl_wrapper(dir=CRAWL_CW)
                elif char == "k":
                    self.controller.reboot_all()
                elif char == "j":
                    self.controller.reboot_all(force_reboot=True)
                elif char == chr(0x1b):
                    self.controller.driver_stop()
                    break


        except KeyboardInterrupt:
            print("Interrupted by keyboard interrupt, closing driver")
            self.controller.halt()
            self.controller.driver_stop()
