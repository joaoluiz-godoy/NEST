#!/usr/bin/env python3
"""
Simple test to verify 8 motors are connected and responsive
Based on working SnakeTest1 code
"""
from MotorDriver import MotorInterface
from constants.motor_constants import *
import time

def test_motors():
    print("Testing 8-motor mini-cobra connection...")

    # Initialize with 8 motors (IDs 2-9) on /dev/ttyUSB0
    motor_ids = list(range(2, 10))  # [2, 3, 4, 5, 6, 7, 8, 9]

    try:
        # Create motor interface with cobra_mini=True
        motor_interface = MotorInterface(motor_ids, "/dev/ttyUSB0", cobra_mini=True)
        motor_interface.start()

        print(f"✓ Successfully connected to motors: {motor_ids}")

        # Read current positions
        print("\nReading current positions...")
        positions = motor_interface.sync_read(motor_ids, ADDR_PRESENT_POSITION)
        for i, motor_id in enumerate(motor_ids):
            print(f"  Motor {motor_id}: {positions[i]}")

        # Move all motors to center position (2000)
        print("\nMoving all motors to center position (2000)...")
        center_positions = [2000] * len(motor_ids)
        motor_interface.sync_write(motor_ids, ADDR_GOAL_POSITION, center_positions)
        time.sleep(2)

        # Read final positions
        print("\nFinal positions:")
        final_positions = motor_interface.sync_read(motor_ids, ADDR_PRESENT_POSITION)
        for i, motor_id in enumerate(motor_ids):
            print(f"  Motor {motor_id}: {final_positions[i]}")

        print("\n✓ Motor test successful!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    finally:
        motor_interface.stop()
        print("Motor interface stopped.")

if __name__ == '__main__':
    test_motors()
