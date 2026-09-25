#!/usr/bin/env python3
"""
Scan for connected Dynamixel motors
"""
from dynamixel_sdk import *
from constants.motor_constants import BAUDRATE, PROTOCOL_VERSION

def scan_motors(port_name="/dev/ttyUSB0", max_id=20):
    """Scan for motors with IDs from 0 to max_id"""
    print(f"Scanning for motors on {port_name}...")
    print(f"Baudrate: {BAUDRATE}, Protocol: {PROTOCOL_VERSION}")

    port_handler = PortHandler(port_name)
    packet_handler = PacketHandler(PROTOCOL_VERSION)

    if not port_handler.openPort():
        print(f"Failed to open port {port_name}")
        return []

    if not port_handler.setBaudRate(BAUDRATE):
        print(f"Failed to set baudrate {BAUDRATE}")
        port_handler.closePort()
        return []

    found_motors = []

    for motor_id in range(max_id + 1):
        # Try to ping the motor
        dxl_model_number, dxl_comm_result, dxl_error = packet_handler.ping(port_handler, motor_id)

        if dxl_comm_result == COMM_SUCCESS:
            print(f"  ✓ Found motor ID {motor_id} (Model: {dxl_model_number})")
            found_motors.append(motor_id)

    port_handler.closePort()

    print(f"\nTotal motors found: {len(found_motors)}")
    print(f"Motor IDs: {found_motors}")

    return found_motors

if __name__ == '__main__':
    scan_motors()
