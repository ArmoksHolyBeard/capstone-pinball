import board
import neopixel
from time import sleep

NUM_LEDS = 240
pixels = neopixel.NeoPixel(board.D21, NUM_LEDS)

red = 0
green = 255
for i in range(NUM_LEDS):
    if i > 0:
        pixels[i-1] = (0, 0, 0)
    pixels[i] = (red, green, 127)
    red += 1
    green -= 1
    sleep(0.001)

pixels.fill((0, 0, 0))