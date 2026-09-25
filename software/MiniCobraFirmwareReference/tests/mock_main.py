import sys
sys.path.append("..")

from motors.tests.MockDriver import MockDriver
from motors.controllers import Controller
from motors.KeypressInterface import KeypressInterface

if __name__ == "__main__":

    mock_driver = MockDriver(list(range(12)))

    controller = Controller(mock_driver)

    interface = KeypressInterface(controller)
    interface.run()