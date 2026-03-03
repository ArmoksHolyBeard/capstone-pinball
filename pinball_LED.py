# import board
# import neopixel

# Set the total number of LEDs in the chain
NUM_LEDS = 240

# Initialize the LEDs
# pixels = neopixel.NeoPixel(board.D21, NUM_LEDS, auto_write=False)

class LightSegment():
    ''' Object for storing the led state and modulating it for various light shows '''
    def __init__(self, startIndex: int, endIndex: int=None):
        self.startIndex = startIndex
        self.endIndex = endIndex if endIndex else startIndex
        self.leds = [0xF for i in range(self.startIndex, self.endIndex+1)]
    
    def getState(self) -> list:
        ''' Return the tuple color values of the LEDs in the segment '''
        return [self._parseHex(h) for h in self.leds]
    
    def _parseHex(self, hexValue):
        ''' Turn a hex value into a tuple of ints '''
        r = int(hexValue >> 16 & 0xFF)
        g = int(hexValue >> 8 & 0xFF)
        b = int(hexValue & 0xFF)
        return (r, g, b)
    
    def blink(self):
        pass

class LightController():
    ''' Object for holding and displaying the various sequences during the game. '''
    def __init__(self, *segments: LightSegment):
        self.segments = segments
        self.colors = [0 for i in range(NUM_LEDS)]
    
    def write(self):
        ''' Write all segments to the LED strip '''
        for segment in self.segments:
            self.colors[segment.startIndex:segment.endIndex] = segment.getState()
        print(self.colors)
        # pixels[:] = self.colors
        # pixels.show()

if __name__ == "__main__":
    seg1 = LightSegment(11, 25)
    seg2 = LightSegment(2)
    allLights = LightController(seg1, seg2)
    allLights.write()