"""
Limits for spiral theta (how much each joint is actuated)

(in degrees)
"""
SPIRAL_UPPER_BOUND = 75
SPIRAL_LOWER_BOUND = 30

TILT_PROF_VELO = 300
TILT_PROF_ACCEL = 0 # make this infinite, so we have faster tilt

TRANSFORM_PROF_VELO = 350
TRANSFORM_PROF_ACCEL = 6
TRANSFORM_SPIRAL_THETA = 60

# Constants for Hexagonal Control
HEX_PHASES = list(range(6))


# States:
STATES = ["SNAKE", "SPIRAL", "HEX", "TILT", "CRAWL", "SIDEWIND", "SURVEY"]
