import math
from constants.motor_constants import *
import os
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class Conversions:
    """
    Static utility class for unit conversions.
    """

    @staticmethod
    def angle_to_pos(angle, use_radians=False):
        """
        Converts angle (degrees or radians) into position (deg/pulse), with rounding via
        flooring and returns an int.
        """
        if use_radians:
            return int(math.floor((angle * 4096 / float((2 * math.pi))) + ZERO_POSITION))
        else:
            return int(math.floor((angle * 4096 / float(360)) + ZERO_POSITION))

    @staticmethod
    def ang_accel_to_profile(ang_accel):
        """
        Conversion method for angular acceleration
        :param ang_accel: angular acceleration in deg/s^2
        :return : profile acceleration in dynamixel units, aka (1 du = 214.577 rev/min^2) unrounded
        """
        return ((ang_accel / 360.0) * (3600)) / PROF_ACCEL_UNITS

    @staticmethod
    def prof_accel_to_ang(prof_accel):
        """
        Conversion method for angular acceleration
        :param prof_accel: profile acceleration in dynamixel units
        :return : profile acceleration in angles, aka (1 du = 214.577 rev/min^2) unrounded
        """
        return ((prof_accel * 360.0) / 3600) * PROF_ACCEL_UNITS

    @staticmethod
    def ang_velo_to_profile(ang_velo):
        """
        Convert angular velocity to profile velocity
        :param ang_velo: angular velocity in deg/s
        :return : profile velocity in dynamixel units (1 du = 0.229 rev/min) unrounded
        """
        return ((ang_velo / 360.0) * 60) / PROF_VELO_UNITS

    @staticmethod
    def prof_velo_to_ang(prof_velo):
        """
        Convert profile velocity to angular velocity
        :param prof_velo: profile velocity in dynamixel units (1 du = 0.229 rev/min) unrounded
        :return : angular velocity in deg/s
        """
        return ((prof_velo * 360.0) / 60) * PROF_VELO_UNITS

    @staticmethod
    def pos_to_angle(pos, delta=False):
        """
        Converts position (deg/pulse) into angle (degrees), without rounding and returns float.

        Args:
            delta : True if pos is a delta position rather than fixed position
        """
        if delta:
            return pos * (float(360) / 4096)
        else:
            return (pos - ZERO_POSITION) * (float(360) / 4096)

    @staticmethod
    def produce_velocity(delta_angle, delta_time):
        """
        delta_angle -- degrees, delta_time -- seconds
        returns velocity value with units of (rev/min)
        """
        return int(math.floor((delta_angle / delta_time) / float(6)))


class MotorCalculations:
    @staticmethod
    def wave_function(t, theta, period):
        """
        Takes in a time and returns the wave position, in degrees (not Dynamixel Units)
        :param t: timestamp, in range from 0 to period.
        :return: wave position as a float, in degrees
        """
        if t < 0 or t > theta:
            raise ValueError("t must be between 0 and %f, t is %f" % (period, t))
        return theta * math.sin((math.pi / theta) * t)


    @staticmethod
    def delta_time(delta, prof_accel, prof_velo):
        """
        Helper function for determining position change time requirement. Imperfect, but quick.

        Args:
            delta : rotational movement in angles
            prof_accel : profile acceleration in dynamixel units. If 0, assume infinite accel. 
            prof_velo : profile velocity in dynamixel units
        Returns:
            a float for the time to perform the delta in angles given
            profile acceleration and velocity
        """
        # assume initial angular velocity is 0
        ang_velo = Conversions.prof_velo_to_ang(prof_velo)
        # print("Angular Velocity: %f degrees/s" % ang_velo)
        if prof_accel != 0:
            ang_accel = Conversions.prof_accel_to_ang(prof_accel)
            return min(math.sqrt(delta / ang_accel) * 2, ang_velo/ang_accel * 2)
        else:
            return delta / ang_velo
