#!/usr/bin/env python3
"""
Simple direct test without MotorDriver wrapper
"""
from dynamixel_sdk import *

# Constants
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
PROTOCOL_VERSION = 2.0
BAUDRATE = 57600
DEVICE_NAME = "/dev/ttyUSB0"

# Motor IDs 2-9
motor_ids = list(range(2, 10))

print("Initializing Dynamixel...")

# Initialize port and packet handlers
port_handler = PortHandler(DEVICE_NAME)
packet_handler = PacketHandler(PROTOCOL_VERSION)

# Open port
if not port_handler.openPort():
    print("Failed to open port")
    exit()

print("✓ Port opened")

# Set baudrate
if not port_handler.setBaudRate(BAUDRATE):
    print("Failed to set baudrate")
    exit()

print("✓ Baudrate set")

# Enable torque
print("\nEnabling torque...")
for motor_id in motor_ids:
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(
        port_handler, motor_id, ADDR_TORQUE_ENABLE, 1
    )
    if dxl_comm_result == COMM_SUCCESS:
        print(f"  ✓ Motor {motor_id} torque enabled")
    else:
        print(f"  ✗ Motor {motor_id} failed: {packet_handler.getTxRxResult(dxl_comm_result)}")

# Read positions
print("\nReading positions...")
for motor_id in motor_ids:
    position, dxl_comm_result, dxl_error = packet_handler.read4ByteTxRx(
        port_handler, motor_id, ADDR_PRESENT_POSITION
    )
    if dxl_comm_result == COMM_SUCCESS:
        print(f"  Motor {motor_id}: {position}")

# Move to center (2000)
print("\nMoving to center position (2000)...")
for motor_id in motor_ids:
    dxl_comm_result, dxl_error = packet_handler.write4ByteTxRx(
        port_handler, motor_id, ADDR_GOAL_POSITION, 2000
    )
    if dxl_comm_result == COMM_SUCCESS:
        print(f"  ✓ Motor {motor_id} goal set")

print("\n✓ Test complete!")

# Cleanup
port_handler.closePort()
