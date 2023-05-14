import analogio
import simpleio

import hardware

x_axis = analogio.AnalogIn(hardware.JOY_X)
y_axis = analogio.AnalogIn(hardware.JOY_Y)

DEADZONE = 10

directions = ["E","SE","S","SW","W","NW","N","NE","0"]

def read_joystick():
    """
    Read joystick pins and scale to range(-100, 100)

    Based on HW-S04 board oriented with pins on the left.
    """
    x = int(simpleio.map_range(x_axis.value, 0, 65535, -100, 100))
    y = int(simpleio.map_range(y_axis.value, 0, 65535, -100, 100))

    # eliminate dead_zone
    filter_x = x if abs(x) > DEADZONE else 0
    filter_y = y if abs(y) > DEADZONE else 0
    return (filter_x, filter_y)

def direction(joy_xy):
    """
    Return direction of movement. Center is 'C'
    """
    (x, y) = joy_xy
    if x == 0 and y == 0: return "C"
    if x > 0 and y == 0: return "R"
    if x < 0 and y == 0: return "L"

    if x == 0 and y < 0: return "D"
    if x > 0 and y < 0: return "DR"
    if x < 0 and y < 0: return "DL"

    if x == 0 and y > 0: return "U"
    if x > 0 and y > 0: return "UR"
    if x < 0 and y > 0: return "UL"

def accelerate(n, deadzone=DEADZONE):
    if (abs(n) < deadzone):
        return 0

    if n < -80:
        return -8
    if n < -60:
        return -6
    if n < -40:
        return -4
    if n < -20:
        return -2

    if n > 80:
        return 8
    if n > 60:
        return 6
    if n > 40:
        return 4
    if n > 20:
        return 2


    return 1

def get_mouse_move(joy_xy):
    (x, y) = joy_xy
    return (accelerate(x), accelerate(y))
