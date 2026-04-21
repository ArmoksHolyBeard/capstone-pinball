import board
import neopixel
from time import sleep

NUM_LEDS = 200

class LightSegment():
    ''' Object for storing the led state and modulating it for various light shows '''
    def __init__(self, start_index: int, end_index: int=None):
        self.start_index = start_index
        self.end_index = end_index if end_index else start_index
        self.segment_length = end_index - start_index + 1
        self.leds = [0x000000 for i in range(self.start_index, self.end_index+1)]
        self.sequence = self._off()
    
    def __repr__(self):
        return f'LightSegment from {self.start_index} to {self.end_index}' \
               f' containing {self._parse_hex_sequence(self.leds)}'
    
    def get_state(self):
        ''' Return the RGB values of the segment '''
        return self._parse_hex_sequence(next(self.sequence))
    
    def begin_sequence(self,
                       new_sequence: str,
                       color: int = 0x111111,
                       delay=0):
        """ Set the sequence to be run on the light segment. Optionally
            pass an RGB color in hex format and a delay as a number of 
            frames to be skipped before updating. Sequence options: 
            "off" "solid" "bullet" "blink" "alternate" "meteor" "random"
        """
        self.sequence.close()
        match new_sequence:
            case 'off':
                self.sequence = self._off()
            case 'solid':
                self.sequence = self._solid(color)
            case 'bullet':
                self.sequence = self._bullet(color, delay)
            case 'blink':
                self.sequence = self._blink(color, delay)
            case 'alternate':
                self.sequence = self._alternate(color, delay)
            case _:
                self.sequence = self._off()

    def _parse_hex(self, hexValue: int):
        ''' Turn a hex value into a tuple of ints '''
        r = int(hexValue >> 16 & 0xFF)
        g = int(hexValue >> 8 & 0xFF)
        b = int(hexValue & 0xFF)
        return r, g, b
    
    def _parse_hex_sequence(self, hexes: list):
        return [self._parse_hex(h) for h in hexes]
    
    def _fill(self, color: int):
        self.leds = [color for led in self.leds]
    
    def _shift(self, backwards: bool = False, rotate: bool = True):
        new_leds = self.leds.copy()
        if backwards: # Shift left
            new_leds[-1] = self.leds[0] if rotate else 0x000000
            new_leds[:-1] = self.leds[1:]
        else: # Shift right
            new_leds[0] = self.leds[-1] if rotate else 0x000000
            new_leds[1:] = self.leds[:-1]
        self.leds = new_leds
    
    def _delay(self, frames: int):
        if frames > 0:
            for i in range(frames):
                yield self.leds
    
    """ Sequence methods """
    def _off(self):
        self._fill(0x000000)
        while True:
            yield self.leds

    def _bullet(self, color: int, delay: int):
        self._fill(0x000000)
        self.leds[0] = color
        while True:
            yield self.leds
            for buffer in self._delay(delay):
                yield buffer
            self._shift()
    
    def _blink(self, color: int, delay: int):
        self._fill(0x000000)
        while True:
            yield self.leds
            for buffer in self._delay(delay):
                yield buffer
            self.leds = [color-current_color for current_color in self.leds]
    
    def _solid(self, color: int):
        self._fill(color)
        while True:
            yield self.leds

    def _alternate(self, color: int, delay: int):
        toggle_on = True
        for led in self.leds:
            led = color if toggle_on else 0x000000
            toggle_on = not toggle_on
        while True:
            yield self.leds
            for buffer in self._delay(delay):
                yield buffer
            self.leds = [color-current_color for current_color in self.leds]

    def _meteor(self, color: int, delay: int):
        pass

    def _rand_noise(self, color: int, delay: int):
        pass

    def _flood_fill(self, color: int, delay: int):
        pass


class LightController():
    ''' Object for holding and displaying the various sequences during the game. '''
    def __init__(self, *segments: LightSegment):
        self.segments = segments
        self.colors = [0 for i in range(NUM_LEDS)]
        self.pixels = neopixel.NeoPixel(board.D10,
                                        NUM_LEDS,
                                        auto_write=False)
    
    def write(self):
        ''' Write all segments to the LED strip '''
        for segment in self.segments:
            self.colors[segment.start_index:segment.end_index+1] = segment.get_state()
        self.pixels[:] = self.colors
        self.pixels.show()

    def stop(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()


if __name__ == "__main__":
    seg1 = LightSegment(0, 9)
    seg2 = LightSegment(10, 19)
    seg3 = LightSegment(30, 42)
    allLights = LightController(seg1, seg2, seg3)

    for i in range(80):
        allLights.write()
        sleep(0.025)
    
    seg1.begin_sequence('bullet')
    seg2.begin_sequence('blink')
    seg3.begin_sequence('bullet')

    for i in range(160):
        allLights.write()
        sleep(0.025)
    
    seg1.begin_sequence('blink')

    for i in range(80):
        allLights.write()
        sleep(0.025)
    
    seg1.begin_sequence('off')
    seg2.begin_sequence('off')
    seg3.begin_sequence('off')