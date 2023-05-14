import hardware
import disp_utils

import app_macropad
import app_metronome
import app_tuner
import app_visualizer

import joystick

MODE_NORMAL = 0
MODE_SWITCHING = 1

class ModeSwitcher:
    curr_mode = MODE_NORMAL
    curr_app = 0

    def __init__(self):
        disp_utils.display.splash()

        self.apps = [
            app_macropad.MacroPad("MUSO PAD"),
            app_metronome.Metronome("METRONOM-NOM"),
            app_tuner.Tuner("TUNER"),
            app_visualizer.Visualizer("VISUALIZER")
            ]

        self.apps[self.curr_app].enter()

    def loop_handler(self):
        # update all buttons
        for i in hardware.keys.keys():
            hardware.keys[i].update()

        """
        for i in hardware.keys.keys():
            if hardware.keys[i].long_press:
                print(hardware.KEYS_MAP[i]["name"], " long pressed")
            if hardware.keys[i].short_count != 0:
                print(hardware.KEYS_MAP[i]["name"], " short pressed", hardware.keys[i].short_count, "times")
            if hardware.keys[i].long_press and hardware.keys[i].short_count == 1:
                print(hardware.KEYS_MAP[i]["name"], " double long pressed")
            #if hardware.keys[i].pressed:
            #    print(hardware.KEYS_MAP[i]["name"], " pressed")
        """

        # button actions
        if hardware.clicked(hardware.KEY_ENC):
            if self.curr_mode == MODE_NORMAL:
                self.curr_mode = MODE_SWITCHING
                self.apps[self.curr_app].exit()
                disp_utils.display.print("Switching", self.apps[self.curr_app].title)
            else:
                self.curr_mode = MODE_NORMAL
                self.apps[self.curr_app].enter()
            print("Button pressed. Mode is now " + str(self.curr_mode))

        # joystick
        joy_xy = joystick.read_joystick()
        self.apps[self.curr_app].handle_joystick(joy_xy)

        if self.curr_mode == MODE_NORMAL:
            self.apps[self.curr_app].loop_handler()
        else:
            pos_change = hardware.encoder_get_change()
            if pos_change != 0:
                if pos_change > 0:
                    self.next_app()
                else:
                    self.prev_app()


    def next_app(self):
        self.curr_app = (self.curr_app + 1) % len(self.apps)
        print("next app: " + self.apps[self.curr_app].title)
        disp_utils.display.print("Switching", self.apps[self.curr_app].title)

    def prev_app(self):
        self.curr_app = (self.curr_app - 1) % len(self.apps)
        print("prev app: " + self.apps[self.curr_app].title)
        disp_utils.display.print("Switching", self.apps[self.curr_app].title)


switcher = ModeSwitcher()
