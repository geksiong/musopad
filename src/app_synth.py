import hardware
import audiobusio
import synthio

class Synthesizer:
    def __init__(self, title):
        self.title = title

        self.melody = synthio.MidiTrack(b"\0\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0*\x80L\0\6\x90J\0" +
                        b"*\x80J\0\6\x90H\0*\x80H\0\6\x90J\0*\x80J\0\6\x90L\0T\x80L\0" +
                        b"\x0c\x90H\0T\x80H\0\x0c\x90H\0T\x80H\0", tempo=640)


    def enter(self):
        self.speaker = audiobusio.I2SOut(hardware.SND_BCLK, hardware.SND_LRC, hardware.SND_DIN)

    def exit(self):
        self.speaker.deinit()

    def handle_joystick(self, joy_xy):
        pass

    def loop_handler(self):

        if hardware.clicked(hardware.KEY_BTN):
            print("red button pressed")
            self.speaker.play(self.melody)
