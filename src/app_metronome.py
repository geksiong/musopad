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
        # sounds: x = strong, 0 = weak, . = silence
        self.beat_patterns = [
            {
                "name": "4/4",
                "beats": 4,
                "tempo_x": 1,
                "subbeats": 1,
                "sounds": "x000",
                "leds": [
                    "222000000000",
                    "000111000000",
                    "000000111000",
                    "000000000111"
                ]
            },
            {
                "name": "3/4",
                "beats": 3,
                "tempo_x": 1,
                "subbeats": 1,
                "sounds": "x00",
                "leds": [
                    "222200000000",
                    "000011110000",
                    "000000001111"
                ]
            },
            {
                "name": "2/4",
                "beats": 2,
                "tempo_x": 1,
                "subbeats": 1,
                "sounds": "x0",
                "leds": [
                    "222222000000",
                    "000000111111",
                ]
            },
            {
                "name": "6/8 (3+3)",
                "beats": 6,
                "tempo_x": 3,
                "subbeats": 1,
                "sounds": "x00x00",
                "leds": [
                    "220000000000",
                    "001100000000",
                    "000011000000",
                    "000000220000",
                    "000000001100",
                    "000000000011",
                ]
            },
            {
                "name": "Solea",
                "beats": 12,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "011.x.011.x.1.x.11x.1.x.",
                "leds": [
                    "010000000000",
                    "001000000000",
                    "000200000000",
                    "000010000000",
                    "000001000000",
                    "000000200000",
                    "000000010000",
                    "000000002000",
                    "000000000100",
                    "000000000020",
                    "000000000001",
                    "200000000000"
                ]
            }
        ]

        self.curr_pattern = 0
        self._set_tempo(60)
        self.time_signature = self.beat_patterns[self.curr_pattern]["beats"]
        self.BEEP_DURATION = 0.05
        self.t0 = time.monotonic()
        self.step = 0
        self.beat = 0

        # LEDs
        self.leds = neopixel.NeoPixel(hardware.LED_RING, 12, brightness=0.1, auto_write=False)
        self.led_colors = [
            (0, 0, 0),      # no color
            (0, 255, 0),    # beat
            (255, 0, 0),    # accent1
            (255, 165, 0)   # accent2
        ]

        # Display
        self.beat_text = "-"

        self.label_pattern = label.Label(terminalio.FONT, scale=1, text=self.beat_patterns[self.curr_pattern]["name"], color=0xFFFFFF, anchor_point=(0.5,0), x=8, y=16+10)
        self.label_bpm = label.Label(terminalio.FONT, scale=2, text=str(self.tempo) + " BPM", color=0xFFFFFF, anchor_point=(0.5,0), x=42, y=16+24)
        self.label_beats = label.Label(terminalio.FONT, scale=1, text=self.beat_text, color=0xFFFFFF, anchor_point=(0.5,0), x=8, y=16+42)

        self.screen = displayio.Group()
        self.screen.append(label.Label(terminalio.FONT, text=self.title, color=0xFFFFFF, anchor_point=(0.5,0), anchored_position=(128/2, 0)))
        self.screen.append(self.label_pattern)
        self.screen.append(self.label_bpm)
        self.screen.append(self.label_beats)


    def play(self):  # Play metronome sound and flash display
        # update display and leds if on beat
        if self._is_on_beat():
            self.update_display()
            self.update_leds()

        # only the first sound array for now
        rhythm = self.beat_patterns[self.curr_pattern]["sounds"]
        sound = rhythm[self.step]
        if sound == "x":  # Put emphasis on downbeat
            simpleio.tone(hardware.PWM, 1800, self.BEEP_DURATION)
        elif sound == "0":
            simpleio.tone(hardware.PWM, 1200, self.BEEP_DURATION)
        elif sound == "1":
            simpleio.tone(hardware.PWM, 400, self.BEEP_DURATION)

    def enter(self):
        hardware.display.show(self.screen)

    def exit(self):
        # clear all LEDs
        for i in range(len(self.leds)):
            self.leds[i] = (0,0,0)
        self.leds.show()

    def update_leds(self):
        offset = 3
        led_pattern = self.beat_patterns[self.curr_pattern]["leds"]
        for i in range(len(self.leds)):
            pos = (offset + i) % len(self.leds)
            self.leds[pos] = self.led_colors[int(led_pattern[self.beat][i])]

        self.leds.show()

    def handle_joystick(self, joy_xy):
        pass # nothing to do

    def _set_tempo(self, tempo):
        self.tempo = tempo
        self.delay = 60 / (self.tempo * self.beat_patterns[self.curr_pattern]["tempo_x"])

    def _is_on_beat(self):
        return self.step % self.beat_patterns[self.curr_pattern]["subbeats"] == 0

    def loop_handler(self):
        # check time
        if time.monotonic() - self.t0 >= self.delay / self.beat_patterns[self.curr_pattern]["subbeats"]:
            self.t0 = time.monotonic()  # reset time before click to maintain accuracy
            #print(self.step, self.beat, self._is_on_beat())
            self.play()

            # increment
            self.step = (self.step + 1) % (self.beat_patterns[self.curr_pattern]["beats"] * self.beat_patterns[self.curr_pattern]["subbeats"])
            if self._is_on_beat():
                self.beat = (self.beat + 1) % self.time_signature

        if hardware.clicked(hardware.KEY_BTN):
            print("Metronome button pressed")
            self.curr_pattern = (self.curr_pattern + 1) % len(self.beat_patterns)
            self.time_signature = self.beat_patterns[self.curr_pattern]["beats"]
            self._set_tempo(self.tempo)
            self.step = 0
            self.beat = 0

        pos_change = hardware.encoder_get_change()
        if pos_change != 0:
            if pos_change > 0:
                self._set_tempo(min(self.tempo + 10, 400))
            else:
                self._set_tempo(max(self.tempo - 10, 20))

            self.update_display()

    def update_display(self):
        self.beat_text = ""
        for i in range(self.beat_patterns[self.curr_pattern]["beats"]):
            if (i == self.beat):
                self.beat_text += "*"
            else:
                self.beat_text += "-"

        self.label_pattern.text = self.beat_patterns[self.curr_pattern]["name"]
        self.label_bpm.text = str(self.tempo) + " BPM"
        self.label_beats.text = self.beat_text
        hardware.display.show(self.screen)

