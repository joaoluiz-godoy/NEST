from motors.utils import Conversions as cn
import math

theta, period = 60, 3.0
ang_accel = 2.0 * theta / ((period / 4.0)**2)
ang_velo = ang_accel * (period / 4.0)
print("ang_accel: %f deg/s^2, ang_velo : %f deg/s" % (ang_accel, ang_velo))
print("max_prof_accel : %d, max_prof_velo : %d"
      % (math.ceil(cn.ang_accel_to_profile(ang_accel)), math.ceil(cn.ang_velo_to_profile(ang_velo))))


theta, period = 30, 8.0
ang_accel = 2.0 * theta / ((period / 4.0)**2)
ang_velo = ang_accel * (period / 4.0)
print("ang_accel: %f deg/s^2, ang_velo : %f deg/s" % (ang_accel, ang_velo))
print("min_prof_accel : %d, min_prof_velo : %d"
      % (math.ceil(cn.ang_accel_to_profile(ang_accel)), math.ceil(cn.ang_velo_to_profile(ang_velo))))