from constants.transform_constants import *

class SubController:
    """
    Parent Class for subsystem controllers, such as those that
    control sidewinding, transformations, and crawling.
    """

    def __init__(self, driver, state):
        """
        Superclass constructor for driver and state object holder.

        Args:
            driver : driver object, of class MotorDriver
            state : state object, should an array of length one containing a single string

        """
        if not (len(state) == 1 and state[0] in STATES):
            raise ValueError("Invalid state: %s" % str(state))
        self.driver_obj = driver
        self.state = state

    def get_state(self):
        """
        Returns:
             State as a string
        """
        assert len(self.state) == 1 and self.state[0] in STATES
        return str(self.state[0])

    def set_state(self, new_state):
        """
        Set state to new_state

        Args:
            new_state : a new state as a string.
        """
        if new_state not in STATES:
            raise ValueError("Invalid state %s, must be a state from %s" % (new_state, str(STATES)))
        assert len(self.state) == 1 and self.state[0] in STATES
        self.state[0] = new_state
        print("SET STATE TO: \t%s" % self.state[0])
