import time
from constants import *
from utils import Conversions as cn, MotorCalculations as mc
from constants.transform_constants import *
from controllers.SubController import SubController

class TransformController(SubController):
    def __init__(self, driver, state):
        """
        Create a TransformController instance to handle state transitions like transforming to and from
        hex, spiral, and tilt configurations.

        Args:
            driver: A driver object that should be from whatever MotorController instance
            created the current instance of TransformController
        """
        SubController.__init__(self, driver, state)
        # transform variables
        self.transformed_hex = False
        self.transformed_spiral = False
        self.is_tilted = False
        self.transform_prof_velo = TRANSFORM_PROF_VELO
        self.transform_prof_accel = TRANSFORM_PROF_ACCEL
        self.spiral_theta = TRANSFORM_SPIRAL_THETA

    def config_profile(self):
        """
        Set the profile velocity and acceleration for during transformation. Should
        always be followed by a restoration of cached profile velocity/acceleration.
        """
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_VELOCITY,
                                    [int(self.transform_prof_velo) for i in JOINT_IDS])
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_ACCELERATION,
                                    [int(self.transform_prof_accel) for i in JOINT_IDS])

    def _time_for_move(self, ids, angles, tilt=False):
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
        if tilt:
            return mc.delta_time(max_delta, TILT_PROF_ACCEL, TILT_PROF_VELO)
        else:
            return mc.delta_time(max_delta, self.transform_prof_accel, self.transform_prof_velo)

    def config_spiral(self, new_theta):
        """
        Sets the spiral theta to be the new angle, provided it is in bounds. This
        does not make the snake move into the spiral configuration but just
        allows the class fields to be the right values.

        Units are degrees.
        """
        if new_theta > SPIRAL_UPPER_BOUND or new_theta < SPIRAL_LOWER_BOUND:
            raise ValueError("new_theta must be between %d and %d, new_theta is %f"
                             % (SPIRAL_LOWER_BOUND, SPIRAL_UPPER_BOUND, new_theta))
        self.spiral_theta = new_theta

    def hex(self):
        """
        Transform into hexagon if already hexagon, if not, back into zero position.

        Returns:
            None, but only returns when hexagonal transformation is finished.
        """
        if not self.driver_obj.is_cobra_mini() and self.transformed_hex:
            try:
                self.driver_obj.single_write(LATCH_ID, ADDR_GOAL_POSITION, LATCH_UNLOCK)
            except Exception:
                self.driver_obj.reboot_motor(LATCH_ID)
                print("Latch Motor Rebooted, try to do hex transform again....")
                return

        if not self.transformed_hex:
            # Hex angles for 8 motors (adapted from 11-motor config)
            hex_angles = [
                [60, 0, 50, 0, 60, 0, 50, 0],
                [55, 0, 60, 0, 65, 0, 60, 0]
            ]
            self.transformed_hex = not self.transformed_hex
            self.set_state("HEX")
        else:
            # Return to zero from hex (8 motors)
            hex_angles = [
                [60, 0, 45, 0, 60, 0, 45, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
            self.transformed_hex = not self.transformed_hex
            self.set_state("SNAKE")
        # Main hex transform loop
        for angles in hex_angles:
            positions = [int(cn.angle_to_pos(angle)) for angle in angles]
            self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION, positions)
            time.sleep(2)
            time.sleep(self._time_for_move(JOINT_IDS, angles))
        if not self.driver_obj.is_cobra_mini() and self.transformed_hex:
            # set latch motor -- we just transformed into hex
            self.driver_obj.single_write(LATCH_ID, ADDR_GOAL_POSITION, LATCH_LOCK)

    def tilt(self, back=False):
        """
        Tilt the snake in the hexagonal form only.

        @params back: direction of tilt, with back=False (default), tilting
            the snake towards direction of head if head is on top side of hexagon,
            and back=True tilting in the opposite direction.
        """

        if not (self.transformed_hex and (self.get_state() == "HEX" or
                                          self.get_state() == "TILT")):
            print("Cannot Tilt without state == HEX or TILT")
            return
        input_angles = []

        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_VELOCITY,
            [TILT_PROF_VELO for i in JOINT_IDS])
        self.driver_obj.sync_write(JOINT_IDS, ADDR_PROFILE_ACCELERATION,
            [TILT_PROF_ACCEL for i in JOINT_IDS])
        if self.is_tilted:
            # Return from tilt (8 motors)
            input_angles = [60, 0, 60, 0, 60, 0, 60, 0]
            self.set_state("HEX")
            self.is_tilted = False
        else:
            # TODO: Add library to poll information from, so that retrieved_phase has
            # a different value than 0....
            # retrieved_phase = imu_driver.get_phase()
            retrieved_phase = 0
            if retrieved_phase not in HEX_PHASES:
                raise Exception("Invalid phase from imu_driver")

            movement_one = ((not back and (retrieved_phase == 0 or retrieved_phase == 3)) or
                (back and (retrieved_phase == 2 or retrieved_phase == 5)))
            movement_two = ((not back and (retrieved_phase == 1 or retrieved_phase == 4)) or
                (back and (retrieved_phase == 0 or retrieved_phase == 3)))
            movement_three = ((not back and (retrieved_phase == 2 or retrieved_phase == 5)) or
                (back and (retrieved_phase == 1 or retrieved_phase == 4)))

            if movement_one:
                # Tilt angles for 8 motors
                input_angles = [47.5, 0, 47.5, 0, 70, 0, 47.5, 0]
            elif movement_two:
                input_angles = [70, 0, 47.5, 0, 47.5, 0, 70, 0]
            elif movement_three:
                input_angles = [47.5, 0, 70, 0, 47.5, 0, 70, 0]
            assert len(input_angles) == 8
            self.is_tilted = True
            self.set_state("TILT")
        self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION,
                                   [cn.angle_to_pos(a) for a in input_angles])
        time.sleep(self._time_for_move(JOINT_IDS, input_angles, tilt=True))

    def spiral(self):
        """
        Writes a spiral configuration into the motors. Only works if we have all 11 motors.

        If already in spiral, then go to zero.

        """

        if self.transformed_spiral:
            self.zero()
            self.transformed_spiral = False
        else:
            # Spiral configuration for 8 motors
            spiral_config = [self.spiral_theta, self.spiral_theta, -self.spiral_theta, self.spiral_theta,
                             -self.spiral_theta, -self.spiral_theta, self.spiral_theta, -self.spiral_theta]
            positions = [int(cn.angle_to_pos(theta)) for theta in spiral_config]
            self.driver_obj.sync_write(JOINT_IDS, ADDR_GOAL_POSITION, positions)
            self.transformed_spiral = True
            time.sleep(self._time_for_move(JOINT_IDS, spiral_config))
            self.set_state("SPIRAL")

    def zero(self):
        """
        Writes a zero configuration into the motors (all straight)
        """
        if self.transformed_hex:
            # transform out of hexagon before attempting spiral
            self.hex()

        if self.transformed_spiral:
            self.transformed_spiral = False

        self.driver_obj.sync_write(JOINT_IDS,
                                   ADDR_GOAL_POSITION,
                                   [ZERO_POSITION for i in JOINT_IDS])
        time.sleep(self._time_for_move(JOINT_IDS, [0 for i in JOINT_IDS]))
        self.set_state("SNAKE")
