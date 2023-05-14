import time
import simpleio
import neopixel
import displayio
import terminalio
from adafruit_display_text import label

import hardware

class Metronome:
    def __init__(self, title):
        self.title = title

        # Patterns
        self.patterns = [
            { "name": "4/4", "beats": 4, "pattern": "x000", "note": 4 },
            { "name": "3/4", "beats": 3, "pattern": "x00", "note": 4 },
            { "name": "2/4", "beats": 2, "pattern": "x0", "note": 4},
            { "name": "6/8 (3+3+3)", "beats": 6, "pattern": "x00100100100", "note": 8 },
            { "name": "Solea", "beats": 12, "pattern": "x00100101010", "note": 4 },
        ]
        self.curr_pattern = 0

        self.tempo = 60
        self.delay = 60 / self.tempo
        self.time_signature = self.patterns[self.curr_pattern]["beats"]
        self.BEEP_DURATION = 0.05
        self.t0 = time.monotonic()
        self.beat = 1

        # LEDs
        self.leds = neopixel.NeoPixel(hardware.LED_RING, 12, brightness=0.1, auto_write=False)
        self.color_accent1 = (255, 0, 0)
        self.color_accent2 = (255, 165, 0)
        self.color_beat = (0, 255, 0)

        # Display
        self.beat_text = "-"

        self.label_pattern = label.Label(terminalio.FONT, scale=1, text=self.patterns[self.curr_pattern]["name"], color=0xFFFFFF, anchor_point=(0.5,0), x=8, y=16+10)
        self.label_bpm = label.Label(terminalio.FONT, scale=2, text=str(self.tempo) + " BPM", color=0xFFFFFF, anchor_point=(0.5,0), x=42, y=16+24)
        self.label_beats = label.Label(terminalio.FONT, scale=1, text=self.beat_text, color=0xFFFFFF, anchor_point=(0.5,0), x=8, y=16+42)

        self.screen = displayio.Group()
        self.screen.append(label.Label(terminalio.FONT, text=self.title, color=0xFFFFFF, anchor_point=(0.5,0), anchored_position=(128/2, 0)))
        self.screen.append(self.label_pattern)
        self.screen.append(self.label_bpm)
        self.screen.append(self.label_beats)


    def play(self, beat):  # Play metronome sound and flash display
        self.update_display()
        self.update_leds(beat)
        accent = self.patterns[self.curr_pattern]["pattern"][beat-1]
        if accent == "1" or accent == "x":  # Put emphasis on downbeat
            simpleio.tone(hardware.PWM, 1800, self.BEEP_DURATION)
        else:
            simpleio.tone(hardware.PWM, 1200, self.BEEP_DURATION)

    def enter(self):
        hardware.display.show(self.screen)

    def exit(self):
        # clear all LEDs
        for i in range(len(self.leds)):
            self.leds[i] = (0,0,0)
        self.leds.show()

    def update_leds(self, beat):
        for i in range(len(self.leds)):
            self.leds[i] = (0,0,0)
        offset = 3
        pos = (offset + self.beat - 1) % 12
        accent = self.patterns[self.curr_pattern]["pattern"][beat-1]
        if (accent == "x"):
            #self.leds[pos] = self.color_accent1
            for i in range(len(self.leds)):
                self.leds[i] = self.color_accent1
        elif (accent == "1"):
            self.leds[pos] = self.color_accent2
        else:
            self.leds[pos] = self.color_beat
        self.leds.show()

    def handle_joystick(self, joy_xy):
        pass # nothing to do

    def loop_handler(self):
        # check time
        if time.monotonic() - self.t0 >= self.delay / (self.patterns[self.curr_pattern]["note"] / 4):
            self.t0 = time.monotonic()  # reset time before click to maintain accuracy
            self.play(self.beat)
            self.beat = self.beat + 1
            if self.beat > self.time_signature:  # if the downbeat was just played, start at top of measure
                self.beat = 1

        if hardware.clicked(hardware.KEY_BTN):
            print("Metronome button pressed")
            self.curr_pattern = (self.curr_pattern + 1) % len(self.patterns)
            self.time_signature = self.patterns[self.curr_pattern]["beats"]
            self.beat = 1

        pos_change = hardware.encoder_get_change()
        if pos_change != 0:
            if pos_change > 0:
                self.tempo = min(self.tempo + 10, 400)
            else:
                self.tempo = max(self.tempo - 10, 20)
            print("Tempo is now: " + str(self.tempo))

            self.delay = 60 / self.tempo
            self.update_display()

    def update_display(self):
        self.beat_text = ""
        for i in range(self.patterns[self.curr_pattern]["beats"]):
            if (i == self.beat - 1):
                self.beat_text += "*"
            else:
                self.beat_text += "-"

        self.label_pattern.text = self.patterns[self.curr_pattern]["name"]
        self.label_bpm.text = str(self.tempo) + " BPM"
        self.label_beats.text = self.beat_text
        hardware.display.show(self.screen)

