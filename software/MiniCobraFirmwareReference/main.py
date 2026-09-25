#!/usr/bin/env python3
"""
Main control script for Mini-Cobra (8 motors, IDs 2-9)
Provides keyboard interface for all locomotion modes
"""
from MotorDriver import MotorInterface
from controllers.CoreController import Controller
from KeypressInterface import KeypressInterface
from constants.motor_constants import *

def main():
    print("=" * 60)
    print("Mini-Cobra Control System")
    print("=" * 60)
    print(f"Motor IDs: {JOINT_IDS}")
    print(f"Device: {DEVICE_NAME}")
    print("=" * 60)

    # Create motor interface (cobra_mini=True for no latch motor)
    motor_interface = MotorInterface(JOINT_IDS, DEVICE_NAME, cobra_mini=True)

    # Create controller (starts motor interface internally)
    controller = Controller(motor_interface)

    print("\n✓ Controller initialized")
    print("  Ready for keyboard control\n")

    # Create and run keyboard interface
    interface = KeypressInterface(controller)

    try:
        interface.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            controller.halt()
            controller.driver_stop()
        except:
            pass
        print("\n✓ Shutdown complete")

if __name__ == '__main__':
    main()
