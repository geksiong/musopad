import keypad
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import usb_hid
from adafruit_hid.mouse import Mouse

import bongo

import hardware
import joystick

class MacroPad:
    def __init__(self, title):
        self.title = title

        self.fs1_state = None

        self.keyboard = Keyboard(usb_hid.devices)
        self.keyboard_layout = KeyboardLayoutUS(self.keyboard)

        self.mouse = Mouse(usb_hid.devices)

        # Bongo cat!
        self.bongo_cat = bongo.Bongo()
        self.bongo_cat.x = 39
        self.bongo_cat.y = 25

    def enter(self):
        hardware.display.show(self.bongo_cat.group)

    def exit(self):
        pass  # nothing to do

    def handle_joystick(self, joy_xy):
        (x, y) = joystick.get_mouse_move(joy_xy)
        if x != 0 or y != 0:
            self.mouse.move(x, y)

    def loop_handler(self):

        if hardware.clicked(hardware.KEY_FS1):
            self.keyboard.press(Keycode.PAGE_UP)
            self.keyboard.release_all()
        elif hardware.clicked(hardware.KEY_FS2):
            self.keyboard.press(Keycode.PAGE_DOWN)
            self.keyboard.release_all()
        elif hardware.long_clicked(hardware.KEY_FS1):
            self.keyboard.press(Keycode.HOME)
            self.keyboard.release_all()
        elif hardware.long_clicked(hardware.KEY_FS2):
            self.keyboard.press(Keycode.END)
            self.keyboard.release_all()
        elif hardware.clicked(hardware.KEY_BTN):
            print("red button pressed")
            self.bongo_cat.update(keypad.Event(1, True))
        elif hardware.clicked(hardware.KEY_JOY):
            print("joy button pressed")
            self.mouse.click(Mouse.LEFT_BUTTON)
        elif hardware.long_clicked(hardware.KEY_JOY):
            print("joy button long pressed")
            self.mouse.click(Mouse.RIGHT_BUTTON)

        #time.sleep(0.1)
