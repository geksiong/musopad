import board
import digitalio
import rotaryio
import analogbufio
import busio
import adafruit_pcf8575
from adafruit_debouncer import Button
import displayio
import adafruit_displayio_ssd1306

# Controls
ROT_LEFT = board.GP19
ROT_RIGHT = board.GP20
ROT_BTN = board.GP21

JOY_X = board.A1
JOY_Y = board.A0
JOY_BTN = board.GP22

BUTTON1 = board.GP14

# I2C IO Expander
IO_ADDR = 0x20
IO_SCL = board.GP7
IO_SDA = board.GP6

IO_FS1 = 8
IO_FS2 = 9

# Enumerate keys, CircuitPython does not have Enum
KEY_ENC = 0
KEY_BTN = 1
KEY_JOY = 2
KEY_FS1 = 11
KEY_FS2 = 12

SRC_PIN = 0
SRC_IO  = 1

KEYS_MAP = {
    KEY_ENC: { "name": "rot_btn", "source": SRC_PIN, "value": ROT_BTN},
    KEY_JOY: { "name": "joy_btn", "source": SRC_PIN, "value": JOY_BTN},
    KEY_FS1: { "name": "io_fs1", "source": SRC_IO, "value": IO_FS1},
    KEY_FS2: { "name": "io_fs2", "source": SRC_IO, "value": IO_FS2},
    KEY_BTN: { "name": "red_btn", "source": SRC_PIN, "value": BUTTON1},
}

# Audio
MIC_IN = board.A2
PWM = board.GP15

# LED
LED_RING = board.GP16

# Display
DISP_SCK = board.GP2
DISP_SDA = board.GP3
DISP_RST = board.GP4
DISP_DC = board.GP0
DISP_CS = board.GP1

DISP_WIDTH = 128
DISP_HEIGHT = 64

enc = rotaryio.IncrementalEncoder(ROT_LEFT, ROT_RIGHT)
enc_last_pos = enc.position


def mic_readinto(buffer, sample_rate):
    mic = analogbufio.BufferedIn(MIC_IN, sample_rate=sample_rate)
    mic.readinto(buffer)
    mic.deinit()


def encoder_get_change():
    global enc_last_pos
    change = enc.position - enc_last_pos
    enc_last_pos = enc.position
    return change

def clicked(keynum):
    return True if keys[keynum].short_count == 1 else False

def double_clicked(keynum):
    return True if keys[keynum].short_count == 2 else False

def long_clicked(keynum):
    return True if keys[keynum].long_press else False

def long_double_clicked(keynum):
    return True if keys[keynum].long_press and keys[keynum].short_count == 1 else False




#### INITIALISE
displayio.release_displays()
spi = busio.SPI(clock=DISP_SCK, MOSI=DISP_SDA)
display_bus = displayio.FourWire(spi, command=DISP_DC, chip_select=DISP_CS, reset=DISP_RST, baudrate=1000000)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=DISP_WIDTH, height=DISP_HEIGHT)

io_bus = busio.I2C(scl=IO_SCL, sda=IO_SDA)
io = adafruit_pcf8575.PCF8575(io_bus, address=IO_ADDR)
io_fs1 = io.get_pin(IO_FS1)  # tests if board is working
#print(io_fs1.value)

# Init button pins

keys = {}

for i in KEYS_MAP.keys():
    if KEYS_MAP[i]["source"] == SRC_PIN:
        pin = digitalio.DigitalInOut(KEYS_MAP[i]["value"])
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        keys[i] = Button(pin)
    elif KEYS_MAP[i]["source"] == SRC_IO:
        predicate = lambda x: io.get_pin(x)
        io_pin = KEYS_MAP[i]["value"]
        keys[i] = Button(predicate(io_pin))
    else:
        print("Unknown key: ", KEYS_MAP[i]["source"])

print(keys)
