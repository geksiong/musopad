import board
import digitalio
import time

import app_switcher

# Onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

counter1 = 0

while True:
    app_switcher.switcher.loop_handler()

    # flash LED every 0.5 seconds, just to show it's alive
    if (counter1 > 50):
        led.value = not led.value
        counter1 = 0
        # do the bongo
        #oled_display.display.bongo()

    counter1 += 1
    time.sleep(0.01)

