#!/usr/bin/env python3
"""
Test all transformation modes for 8-motor mini-cobra
"""
from MotorDriver import MotorInterface
from controllers.CoreController import Controller
from constants.motor_constants import *
import time

def test_mode(controller, mode_name, mode_func):
    """Test a single mode"""
    print(f"\n{'='*60}")
    print(f"Testing: {mode_name}")
    print(f"{'='*60}")
    try:
        mode_func()
        print(f"✓ {mode_name} completed successfully")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"✗ {mode_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Mini-Cobra Mode Test Suite")
    print("=" * 60)
    print(f"Motor IDs: {JOINT_IDS}")
    print("=" * 60)

    # Create motor interface and controller
    motor_interface = MotorInterface(JOINT_IDS, DEVICE_NAME, cobra_mini=True)
    controller = Controller(motor_interface)

    results = {}

    try:
        # Test 1: Zero position
        results['Zero'] = test_mode(controller, "Zero Position", controller.zero_wrapper)

        # Test 2: Hex transformation
        results['Hex'] = test_mode(controller, "Hexagon Transformation", controller.hex_wrapper)

        # Test 3: Return from hex
        if results['Hex']:
            results['Hex Return'] = test_mode(controller, "Hexagon Return to Zero", controller.hex_wrapper)

        # Test 4: Spiral transformation
        controller.zero_wrapper()
        time.sleep(2)
        results['Spiral'] = test_mode(controller, "Spiral Transformation", controller.spiral_wrapper)

        # Test 5: Return from spiral
        if results['Spiral']:
            results['Spiral Return'] = test_mode(controller, "Spiral Return to Zero", controller.spiral_wrapper)

        # Test 6: Tilt (requires hex first)
        controller.zero_wrapper()
        time.sleep(1)
        controller.hex_wrapper()
        time.sleep(2)
        results['Tilt Forward'] = test_mode(controller, "Tilt Forward", controller.tilt_fwd_wrapper)

        # Test 7: Return from tilt
        if results['Tilt Forward']:
            results['Tilt Return'] = test_mode(controller, "Tilt Return", controller.tilt_fwd_wrapper)

        # Return to zero
        print("\n" + "=" * 60)
        print("Returning to zero position...")
        print("=" * 60)
        controller.zero_wrapper()
        time.sleep(2)

        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for mode, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{mode:20s} {status}")

        passed = sum(1 for r in results.values() if r)
        total = len(results)
        print(f"\nTotal: {passed}/{total} tests passed")

    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nCleaning up...")
        controller.halt()
        controller.driver_stop()
        print("✓ Done")

if __name__ == '__main__':
    main()
