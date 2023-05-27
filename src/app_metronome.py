from adafruit_ticks import ticks_ms, ticks_diff
import neopixel
import displayio
import terminalio
from adafruit_display_text import label
import audiocore
import audiobusio
import audiomixer

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
                "sounds": "-00-x--00-x-0-x-00x-0-x-",
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
                ],
            },
            {
                "name": "Alegria",
                "beats": 12,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "-00-x--00-x--0x--0x--0x-",
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
            },
            {
                "name": "Buleria",
                "beats": 12,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "000-x-000-x-00x-00x-0-x-",
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
            },
            {
                "name": "Siguiriyas",
                "beats": 12,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "x--0x--0x--00-x-0-0-x-0-",
                "leds": [
                    "000000002000",
                    "000000000100",
                    "000000000020",
                    "000000000001",
                    "200000000000",
                    "010000000000",
                    "001000000000",
                    "000200000000",
                    "000010000000",
                    "000001000000",
                    "000000200000",
                    "000000010000"
                ]
            },
            {
                "name": "Tangos",
                "beats": 4,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "--00x-0-",
                "leds": [
                    "222000000000",
                    "000111000000",
                    "000000222000",
                    "000000000111"
                ]
            },
            {
                "name": "Rhumba",
                "beats": 4,
                "tempo_x": 1,
                "subbeats": 2,
                "sounds": "0-x-0-x-",
                "leds": [
                    "111000000000",
                    "000222000000",
                    "000000111000",
                    "000000000222"
                ]
            }


        ]

        self.curr_pattern = 0
        self._set_tempo(60)
        self.time_signature = self.beat_patterns[self.curr_pattern]["beats"]
        self.BEEP_DURATION = 0.05
        self.t0 = ticks_ms()
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

        # Speaker
        self.speaker = audiobusio.I2SOut(hardware.SND_BCLK, hardware.SND_LRC, hardware.SND_DIN)
        self.num_voices = 2
        self.curr_voice = 0
        # sufficient buffer_size needed to prevent glitches. too high and timing will be off.
        self.mixer = audiomixer.Mixer(voice_count=self.num_voices, buffer_size=4096, sample_rate=22050,
                        channel_count=1, bits_per_sample=16, samples_signed=True)
        self.speaker.play(self.mixer)
        self.mixer.voice[0].level = 1.0
        self.mixer.voice[1].level = 1.0
        self.sample_x = audiocore.WaveFile(open("files/Ping Hi.wav","rb"))
        self.sample_0 = audiocore.WaveFile(open("files/Ping Low.wav","rb"))


    def play(self):  # Play metronome sound and flash display
        # only the first sound array for now
        rhythm = self.beat_patterns[self.curr_pattern]["sounds"]
        sound = rhythm[self.step]
        if sound == "x":  # Put emphasis on downbeat
            self.curr_voice = (self.curr_voice + 1) % self.num_voices
            self.mixer.voice[self.curr_voice].play(self.sample_x, loop=False)
        elif sound == "0":
            self.curr_voice = (self.curr_voice + 1) % self.num_voices
            self.mixer.voice[self.curr_voice].play(self.sample_0, loop=False)

                # update display and leds if on beat
        if self._is_on_beat():
            self.update_display()
            self.update_leds()

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
        if ticks_diff(ticks_ms(), self.t0) >= 1000 * self.delay / self.beat_patterns[self.curr_pattern]["subbeats"]:
            self.t0 = ticks_ms()  # reset time before click to maintain accuracy
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

