import displayio
import terminalio
from adafruit_display_text import label

import hardware

class OLEDDisplay:

    def __init__(self):
        self.splash_screen = displayio.Group()
        self.text1 = label.Label(terminalio.FONT, scale=2, text="Hello Muso", color=0xFFFFFF, x=10, y=26)
        self.splash_screen.append(self.text1)

        self.simple_labels = [
            label.Label(terminalio.FONT, text="", color=0xFFFFFF, anchor_point=(0.5,0), anchored_position=(hardware.DISP_WIDTH/2, 0)),
            label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=8, y=16+1*10),
            label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=8, y=16+2*10),
            label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=8, y=16+3*10)
        ]

        self.simple_screen = displayio.Group()
        for l in self.simple_labels:
            self.simple_screen.append(l)


    def splash(self):
        hardware.display.show(self.splash_screen)

    def print(self, title, *argv):
        self.simple_labels[0].text = title
        i = 0
        for arg in argv:
            i += 1
            if i < len(self.simple_labels): self.simple_labels[i].text = arg

        hardware.display.show(self.simple_screen)

display = OLEDDisplay()
