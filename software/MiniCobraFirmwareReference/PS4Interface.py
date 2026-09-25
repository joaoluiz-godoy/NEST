
from pyPS4Controller.controller import Controller 
    
class PS4Interface(Controller):

    def __init__(self, controller, **kwargs):
        Controller.__init__(self, **kwargs)
        self.controller = controller

    def on_L3_up(self):
       self.controller.start_sidewind_wrapper()

    def on_L3_down(self):
       self.controller.halt()

    def on_x_press(self):
       self.controller.spiral_wrapper()
    
    def on_triangle_press(self):
       self.controller.hex_wrapper()

    def on_circle_press(self):
       self.controller.zero_wrapper()
    
    def on_up_arrow_press(self):
       self.controller.tilt_fwd_wrapper()

    def on_down_arrow_press(self):
       self.controller.tilt_back_wrapper()

    def on_options_press(self):
       self.controller.driver_stop()






"""
Event actions for pyPS4Controller


on_x_press
on_x_release
on_triangle_press
on_triangle_release
on_circle_press
on_circle_release
on_square_press
on_square_release
on_L1_press
on_L1_release
on_L2_press
on_L2_release
on_R1_press
on_R1_release
on_R2_press
on_R2_release
on_up_arrow_press
on_up_down_arrow_release
on_down_arrow_press
on_left_arrow_press
on_left_right_arrow_release
on_right_arrow_press
on_L3_up
on_L3_down
on_L3_left
on_L3_right
on_L3_x_at_rest  # L3 joystick is at rest after the joystick was moved and let go off on x axis
on_L3_y_at_rest  # L3 joystick is at rest after the joystick was moved and let go off on y axis
on_L3_press  # L3 joystick is clicked. This event is only detected when connecting without ds4drv
on_L3_release  # L3 joystick is released after the click. This event is only detected when connecting without ds4drv
on_R3_up
on_R3_down
on_R3_left
on_R3_right
on_R3_x_at_rest  # R3 joystick is at rest after the joystick was moved and let go off on x axis
on_R3_y_at_rest  # R3 joystick is at rest after the joystick was moved and let go off on y axis
on_R3_press  # R3 joystick is clicked. This event is only detected when connecting without ds4drv
on_R3_release  # R3 joystick is released after the click. This event is only detected when connecting without ds4drv
on_options_press
on_options_release
on_share_press  # this event is only detected when connecting without ds4drv
on_share_release  # this event is only detected when connecting without ds4drv
on_playstation_button_press  # this event is only detected when connecting without ds4drv
on_playstation_button_release  # this event is only detected when connecting without ds4drv

"""
