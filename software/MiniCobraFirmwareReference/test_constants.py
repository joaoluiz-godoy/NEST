#!/usr/bin/env python3
"""
Test updated constants with MotorDriver
"""
from MotorDriver import MotorInterface
from constants.motor_constants import *
import time

print("Testing updated motor constants...")
print(f"Motor IDs: {JOINT_IDS}")
print(f"Position limits: {MIN_POSITION} - {MAX_POSITION}")

# Create motor interface with cobra_mini=True
motor_interface = MotorInterface(JOINT_IDS, DEVICE_NAME, cobra_mini=True)
motor_interface.start()

print("\n✓ Motor interface started")

# Read positions
print("\nCurrent positions:")
positions = motor_interface.sync_read(JOINT_IDS, ADDR_PRESENT_POSITION)
for i, motor_id in enumerate(JOINT_IDS):
    print(f"  Motor {motor_id}: {positions[i]}")

# Move to zero position
print(f"\nMoving to zero position ({ZERO_POSITION})...")
zero_positions = [ZERO_POSITION] * len(JOINT_IDS)
motor_interface.sync_write(JOINT_IDS, ADDR_GOAL_POSITION, zero_positions)
time.sleep(2)

print("\n✓ Test successful!")
motor_interface.stop()
