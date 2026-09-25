#!/usr/bin/env python3
"""
Sidewinding test for 8-motor mini-cobra (IDs 2-9)
Based on working slither.py from SnakeTest1
"""
import time
import math
from dynamixel_sdk import *

# Control table addresses
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_PROFILE_VELOCITY = 112
ADDR_PROFILE_ACCELERATION = 108

# Protocol and communication settings
PROTOCOL_VERSION = 2.0
BAUDRATE = 57600
DEVICE_NAME = "/dev/ttyUSB0"

# Motor IDs (2-9)
MOTOR_IDS = list(range(2, 10))

# Position limits
MIN_POSITION = 1000
MAX_POSITION = 3000
CENTER_POSITION = 2000

def initialize_motors(port_handler, packet_handler):
    """Initialize and enable torque for all motors"""
    print("Initializing motors...")

    # Open port
    if not port_handler.openPort():
        raise RuntimeError("Failed to open port")
    print("✓ Port opened")

    # Set baudrate
    if not port_handler.setBaudRate(BAUDRATE):
        raise RuntimeError("Failed to set baudrate")
    print("✓ Baudrate set")

    # Enable torque for all motors
    for motor_id in MOTOR_IDS:
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(
            port_handler, motor_id, ADDR_TORQUE_ENABLE, 1
        )
        if dxl_comm_result != COMM_SUCCESS:
            raise RuntimeError(f"Failed to enable torque for motor {motor_id}")

    print(f"✓ Torque enabled for motors: {MOTOR_IDS}")

    # Set profile velocity and acceleration for smooth movement
    for motor_id in MOTOR_IDS:
        # Set profile velocity (higher = faster)
        packet_handler.write4ByteTxRx(port_handler, motor_id, ADDR_PROFILE_VELOCITY, 200)
        # Set profile acceleration (0 = infinite acceleration)
        packet_handler.write4ByteTxRx(port_handler, motor_id, ADDR_PROFILE_ACCELERATION, 0)

    print("✓ Profile settings configured")

def move_to_center(port_handler, packet_handler):
    """Move all motors to center position"""
    print("\nMoving to center position...")
    for motor_id in MOTOR_IDS:
        packet_handler.write4ByteTxRx(
            port_handler, motor_id, ADDR_GOAL_POSITION, CENTER_POSITION
        )
    time.sleep(2)
    print("✓ Centered")

def sidewind(port_handler, packet_handler,
             duration=20.0,
             freq=0.2,                # Hz: wave oscillation frequency
             amplitude=500,           # pulse amplitude around center (reduced from 700)
             center=CENTER_POSITION,  # center position
             phase_step=math.pi / 4,  # phase offset between joints
             update_dt=0.03):         # seconds between updates
    """
    Execute sidewinding motion with traveling sine wave pattern
    """
    print(f"\nStarting sidewinding for {duration} seconds...")
    print(f"  Frequency: {freq} Hz")
    print(f"  Amplitude: {amplitude} pulses")
    print(f"  Phase step: {phase_step:.2f} rad ({math.degrees(phase_step):.1f}°)")
    print(f"  Update rate: {1/update_dt:.1f} Hz")
    print("\nPress Ctrl+C to stop early\n")

    start_time = time.time()

    try:
        while True:
            t = time.time() - start_time
            if t > duration:
                break

            # Calculate and set position for each motor
            for i, motor_id in enumerate(MOTOR_IDS):
                # Phase shift along the body creates traveling wave
                phase = i * phase_step
                raw_pos = center + amplitude * math.sin(2 * math.pi * freq * t + phase)

                # Clamp to safe range
                goal = max(MIN_POSITION, min(MAX_POSITION, int(raw_pos)))

                # Write goal position (streaming, no waiting)
                dxl_comm_result, dxl_error = packet_handler.write4ByteTxRx(
                    port_handler, motor_id, ADDR_GOAL_POSITION, goal
                )

                if dxl_comm_result != COMM_SUCCESS or dxl_error != 0:
                    print(f"Warning: Comm issue on motor {motor_id}")

            # Status update every 2 seconds
            if int(t) != int(t - update_dt) and int(t) % 2 == 0:
                print(f"  Time: {t:.1f}s / {duration}s")

            time.sleep(update_dt)

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    print(f"\n✓ Sidewinding complete ({time.time() - start_time:.1f}s)")

def main():
    """Main function"""
    # Initialize port and packet handlers
    port_handler = PortHandler(DEVICE_NAME)
    packet_handler = PacketHandler(PROTOCOL_VERSION)

    try:
        # Initialize motors
        initialize_motors(port_handler, packet_handler)

        # Move to center position first
        move_to_center(port_handler, packet_handler)

        # Execute sidewinding
        sidewind(port_handler, packet_handler, duration=20.0)

        # Return to center
        move_to_center(port_handler, packet_handler)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

    finally:
        # Disable torque and close port
        print("\nCleaning up...")
        for motor_id in MOTOR_IDS:
            packet_handler.write1ByteTxRx(
                port_handler, motor_id, ADDR_TORQUE_ENABLE, 0
            )
        port_handler.closePort()
        print("✓ Done")

if __name__ == "__main__":
    main()
