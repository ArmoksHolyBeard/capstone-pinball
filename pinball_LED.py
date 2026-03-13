import board
import neopixel
from time import sleep

# Set the total number of LEDs in the chain
NUM_LEDS = 50

class LightSegment():
    ''' Object for storing the led state and modulating it for various light shows '''
    def __init__(self, startIndex: int, endIndex: int=None):
        self.startIndex = startIndex
        self.endIndex = endIndex if endIndex else startIndex
        self.leds = [0 for i in range(self.startIndex, self.endIndex+1)]
        self.sequence = self.__off()
    
    def __repr__(self):
        return f'LightSegment from {self.startIndex} to {self.endIndex} containing {self.__parse_hex_sequence(self.leds)}'
    
    def get_state(self):
        return self.__parse_hex_sequence(next(self.sequence))
    
    def begin_sequence(self, newSequence: str):
        self.sequence.close()
        match newSequence:
            case 'off':
                self.sequence = self.__off()
            case 'bullet':
                self.sequence = self.__bullet()
            case 'blink':
                self.sequence = self.__blink()
            case 'alternate':
                self.sequence = self.__alternate()

    def __parse_hex(self, hexValue: int):
        ''' Turn a hex value into a tuple of ints '''
        r = int(hexValue >> 16 & 0xFF)
        g = int(hexValue >> 8 & 0xFF)
        b = int(hexValue & 0xFF)
        return r, g, b
    
    def __parse_hex_sequence(self, hexes: list):
        return [self.__parse_hex(h) for h in hexes]
    
    def __clear(self):
        self.leds = [0 for led in self.leds]
    
    def __shiftRight(self, places: int = 1, rotate: bool = True):
        new_leds = self.leds.copy()
        length = len(self.leds)
        end = length - 1
        places = places % length
        if places > 0:
            if rotate:
                new_leds[:places] = self.leds[end-places+1:end+1]
                new_leds[places:] = self.leds[:end-rotate+1]
            else:
                new_leds[:places] = [0 for i in range(places)]
                new_leds[places:] = self.leds[:end-rotate+1]
            self.leds = new_leds
    
    def __off(self):
        while True:
            self.__clear()
            yield self.leds

    def __bullet(self):
        self.__clear()
        self.leds[0] = 0xCC4400
        while True:
            yield self.leds
            self.__shiftRight()
    
    def __blink(self):
        self.__clear()
        while True:
            yield self.leds
            self.leds = [0x00AA77-led for led in self.leds]

    def __alternate(self):
        pass

    def __rand_noise(self):
        pass

class LightController():
    ''' Object for holding and displaying the various sequences during the game. '''
    def __init__(self, *segments: LightSegment):
        self.segments = segments
        self.colors = [0 for i in range(NUM_LEDS)]
        self.pixels = neopixel.NeoPixel(board.D10, NUM_LEDS, auto_write=False)
    
    def write(self):
        ''' Write all segments to the LED strip '''
        for segment in self.segments:
            self.colors[segment.startIndex:segment.endIndex+1] = segment.getState()
        self.pixels[:] = self.colors
        self.pixels.show()

if __name__ == "__main__":
    seg1 = LightSegment(0, 9)
    seg2 = LightSegment(10, 19)
    seg3 = LightSegment(30, 42)
    allLights = LightController(seg1, seg2, seg3)

    for i in range(80):
        allLights.write()
    
    seg1.begin_sequence('bullet')
    seg2.begin_sequence('blink')
    seg3.begin_sequence('bullet')

    for i in range(160):
        allLights.write()
    
    seg1.begin_sequence('blink')

    for i in range(80):
        allLights.write()
    
    seg1.begin_sequence('off')
    seg2.begin_sequence('off')
    seg3.begin_sequence('off')