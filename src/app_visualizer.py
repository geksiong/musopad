# Adapted from https://steam-tokyo.com/making-circuitpython-music-visualizer/

# CircuitPython Music Visualizer
# Aoyama_PROD, STEAM Tokyo
import array
import displayio
import adafruit_imageload
import ulab.numpy as np
import ulab.utils
import simpleio

import hardware

class Visualizer:
    def __init__(self, title):
        self.title = title

        self.sr = 22000  # Sampling rate
        self.sample_ct = 1024  # Sample count
        self.peak = [31] * 32  # Array to hold the maximum value of the variable pxy
        self.gain_f = 1000000  # You can adjust the gain by changing this value
        self.nyquist = self.sample_ct // 2 + 1  # Nyquist value

        self.samples = array.array('H', [0] * (self.sample_ct+3))

        self.sprite_sheet, palette = adafruit_imageload.load("/files/HeatMap_sprites_4x4.bmp",
                                                        bitmap=displayio.Bitmap,
                                                        palette=displayio.Palette)

        self.sprite_hd = displayio.TileGrid(
            self.sprite_sheet,
            pixel_shader=palette,
            width=16,
            height=16,
            tile_width=4,
            tile_height=4)

        self.screen = displayio.Group(scale=1)
        self.screen.append(self.sprite_hd)

    def enter(self):
        hardware.display.show(self.screen)

    def exit(self):
        pass  # nothing to do

    def handle_joystick(self, joy_xy):
        pass # nothing to do

    def handle_key_event(self, event):
        print("App currently doesn't handle any keys")

    def loop_handler(self):
        hardware.mic_readinto(self.samples, self.sr)

        samparray = np.array(self.samples[3:])

        f = ulab.utils.spectrogram(samparray)  # FFT(absolute)

        step = self.sample_ct // 32
        for i in range(step, self.nyquist, step):  # Discard first 3 values
            pxx = int((i - step + 1) / step)  # x of sprite

            fmax4 = max(f[i:i + step - 1]) - 15000 # Get max value of every four of f
            # map fmax4 value
            pxy = int(simpleio.map_range(fmax4, 0, self.gain_f, 15, 0))

            #print(pxx, pxy)
            print(i, fmax4, pxx, pxy)

            if self.peak[pxx] > pxy:
                self.peak[pxx] = pxy  # update the peak array
            elif self.peak[pxx] < 14:
                self.peak[pxx] = self.peak[pxx] + 2  # move pixels down by 2

            # Clear existing sprites
            if self.peak[pxx] > 0:
                self.sprite_hd[pxx, self.peak[pxx] - 1] = 0
            if self.peak[pxx] > 1:
                self.sprite_hd[pxx, self.peak[pxx] - 2] = 0
                # Place sprites
                self.sprite_hd[pxx, self.peak[pxx]] = 15 - int(self.peak[pxx]/2)

        hardware.display.show(self.screen)
