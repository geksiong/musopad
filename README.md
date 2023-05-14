# MusoPad - Musician's Macro Pad

**Status**: Prototype

## Concept

This was initially to be just a simple macropad with some keyboard switches and a couple of footswitches, to help me navigate music scores on the screen as I'm playing my instruments. The device is to be based off a Raspberry Pi Pico which has USB HID capabilities. Then I thought why get make more utility out of this board? This "simple" idea has quickly evolved into a multi-functional device with a display, microphone and speaker.

Since this is to be a device for musicians, I've named it "MusoPad".

The current prototype demonstrates some basic functionality.

## Parts

- Raspberry Pi Pico
- Display: 0.96-inch SPI SSD13306 OLED display
- Microphone: MAX4466
- Audio: PWM audio
- NeoPixel ring with 12-LEDs
- Inputs:
  - Analog joystick with button
  - Rotary encoder with button
  - Push button *(current prototype has one pushbutton)*
  - Keys and footswitches via a PCF8575 16-channel IO Expander *(current prototype has 2 footswitches)*

## Circuit Diagram

*Coming soon*

## Dependencies

*Coming soon*

## Applications

### App Switcher

This is the core framework for enabling multiple apps to be hosted on the same device.

Enter the "App Switcher" by pressing the rotary encoder's button. Rotate left and right to select the app to switch to. Press the button again to exit.

### MacroPad

The MacroPad sends keys and mouse events via USB HID:

- the joystick controls the mouse pointer, with some acceleration (more movement the farther out you go)
- pushing on the joystick button sends a left mouse click. Long press to send a right mouse click.
- the push button currently controls a Bongo Cat on the display.
- 2 footswitches are configured: short presses send Page Up/Down, long presses send Home/End

### Metronome

A metronome with ability to select different rhythms.

- Rotary knob controls the BPM.
- The push button toggles between various beat patterns.
- The beats are played back on the speaker via PWM audio, and are also displayed on the NeoPixel ring.
- I chose the 12-LED NeoPixel so I can use it for subdivisions of 2, 3, 4, 6 and 12 (for flamenco beats)
- Timing is a little off sometimes.

### Tuner

- This is an experiment to see if I can implement a pitch detection function. I adapted a Python implementation that I've found of the YIN algorithm to CircuitPython.
- The app displays the audio waveform, detected pitch and difference from the desired pitch.
- The algorithm works. However, speed is still too slow to be practical. The tuner on my Android phone works much better for this.
- It is tricky to adjust the mic sensitivity to reduce random pitches being detected due to picked up noise.
- Higher pitches need to be fairly loud to get picked up.

### Visualizer

- Spectrum visualizer from mic input. Currently it displays the FFT bins as-is. To display this more correctly I still need to accumulate the bins by log intervals.


## Roadmap

- [ ] Expand number of keys and their actions
- [ ] Amplifier for louder audio
- [ ] More usable tuner
- [ ] More patterns for metronome
- [ ] Nicer metronome sounds (wav file playback)
- [ ] microSD card for storage of assets
- [ ] App idea: Chording keyboard (looking at artsey.io)
- [ ] App idea: Step sequencer
- [ ] App idea: Midi player
