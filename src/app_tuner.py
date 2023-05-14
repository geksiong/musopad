import array
import time
import math
import ulab.numpy as np
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.sparkline import Sparkline

import hardware

import yin

# I could also just generate this list programmatically
NOTE_PITCHES = (
    ("C2", 65.47), ("C#2/Cb2", 69.30), ("D2", 73.42), ("D#2/Eb2", 77.78), ("E2", 82.41), ("F2", 87.31),
    ("F#2/Gb2", 92.50), ("G2", 98.00), ("G#2/Ab2", 103.83), ("A2", 110.00), ("A#2/Bb2", 116.54), ("B2", 123.47),

    ("C3", 130.81), ("C#3/Cb3", 138.59), ("D3", 146.83), ("D#3/Eb3", 155.56), ("E3", 164.81), ("F3", 174.61),
    ("F#3/Gb3", 185.00), ("G3", 196.00), ("G#3/Ab3", 207.65), ("A3", 220.00), ("A#3/Bb3", 233.08), ("B3", 246.94),

    ("C4", 261.63), ("C#4/Cb", 277.18), ("D4", 293.66), ("D#4/Eb4", 311.13), ("E4", 329.63), ("F4", 349.23),
    ("F#4/Gb4", 369.99), ("G4", 392.00), ("G#4/Ab4", 415.30), ("A4", 440.00), ("A#4/Bb4", 466.16), ("B4", 493.88),

    ("C5", 523.25), ("C#5/Cb5", 554.37), ("D5", 587.33), ("D#5/Eb5", 622.25), ("E5", 659.25), ("F5", 698.46),
    ("F#5/Gb5", 739.99), ("G5", 783.99), ("G#5/Ab5", 830.61), ("A5", 880.00), ("A#5/Bb5", 932.33), ("B5", 987.77),
)

class Tuner:
    def __init__(self, title):
        self.title = title

        self.length = 1024
        self.samples = array.array("H", [0x0000] * self.length)
        self.rate = 22000

        # Display
        self.rms = 0.00
        self.detected_note = "??"
        self.pitch_diff = 0.00

        self.label_note = label.Label(terminalio.FONT, scale=2, text=self.detected_note, color=0xFFFFFF, anchor_point=(0.5,0), x=8, y=16+10)
        self.label_pitch_diff = label.Label(terminalio.FONT, scale=1, text=str(self.pitch_diff), color=0xFFFFFF, anchor_point=(0.5,0), x=96, y=16+10)
        self.spark = Sparkline(width=128, height=16, max_items=128, y_min=0, y_max=33, x=0, y=48)


        self.screen = displayio.Group()
        self.screen.append(label.Label(terminalio.FONT, text=self.title, color=0xFFFFFF, anchor_point=(0.5,0), anchored_position=(128/2, 0)))
        #self.screen.append(label.Label(terminalio.FONT, text=f'{self.rms:>10}', color=0xFFFFFF, x=8, y=16+1*10))
        self.screen.append(self.label_note)
        self.screen.append(self.label_pitch_diff)
        self.screen.append(self.spark)

    def enter(self):
        hardware.display.show(self.screen)

    def exit(self):
        pass  # nothing to do

    def handle_joystick(self, joy_xy):
        pass # nothing to do

    def handle_key_event(self, event):
        print("App currently doesn't handle any keys")

    def loop_handler(self):
        hardware.mic_readinto(self.samples, self.rate)

        x = np.array([(x - 32767)/65536 for x in self.samples])
        pitches, harmonic_rates, argmins, times = yin.compute_yin(sig=x, sr=self.rate, w_len=512, w_step=256, f0_min=50, f0_max=500, harmo_thresh=0.1)
        print(pitches, harmonic_rates)

        if pitches[0] != 0.0:
            matches = [abs(pitches[0] - x[1]) for x in NOTE_PITCHES]
            idx = matches.index(min(matches))
            self.pitch_diff = pitches[0] - NOTE_PITCHES[idx][1]
            self.detected_note = NOTE_PITCHES[idx][0]
            print(self.detected_note, ":", NOTE_PITCHES[idx][1], pitches[0], self.pitch_diff)
        else:
            self.detected_note = "??"
            self.pitch_diff = 0.00

        self.update_display()
        time.sleep(0.1)

    def update_display(self):
        values = np.array(self.samples)
        minbuf = np.mean(values)
        values = values - minbuf
        samples_sum = np.sum(values * values)
        self.rms = math.sqrt(samples_sum / len(values))

        step = self.length // 128
        for i in range(0, self.length, step):
            self.spark.add_value(self.samples[i]//2000, False)

        self.spark.update()
        self.label_note.text = self.detected_note
        self.label_pitch_diff.text = f'{self.pitch_diff:.3f}'
        hardware.display.show(self.screen)

