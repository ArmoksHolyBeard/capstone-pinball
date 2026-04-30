import board
import neopixel
from time import sleep

NUM_LEDS = 200

class LightSegment():
    ''' Object for storing the led state and modulating it for various light shows '''
    def __init__(self, start_index: int, end_index: int|None = None):
        self.start_index = start_index
        self.end_index = end_index if end_index is not None else start_index
        self.segment_length = self.end_index - self.start_index + 1
        self.leds = [0x000000 for i in range(self.start_index, self.end_index+1)]
        self.sequence = self._off(0)
        self.prev_sequence = ("", 0, 0x111111, 0)
    
    def __repr__(self):
        return f'LightSegment from {self.start_index} to {self.end_index}' \
               f' containing {self._parse_hex_sequence(self.leds)}'
    
    def get_state(self):
        ''' Return the RGB values of the segment '''
        try:
            return self._parse_hex_sequence(next(self.sequence))
        except StopIteration:
            self.begin_sequence(*self.prev_sequence)
            return self._parse_hex_sequence(next(self.sequence))
    
    def begin_sequence(self,
                       new_sequence: str,
                       ttl: int = 0,
                       color: int = 0x111111,
                       delay: int = 0):
        """ Set the sequence to be run on the light segment. Optionally
            pass an RGB color in hex format and a delay as a number of 
            frames to be skipped before updating. Sequence options: 
            "off" "solid" "bullet" "blink" "alternate" "meteor" "random"
        """
        if ttl <= 0:
            ttl = 0
            self.prev_sequence = (new_sequence, ttl, color, delay)
        self.sequence.close()
        match new_sequence:
            case 'off':
                self.sequence = self._off(ttl)
            case 'solid':
                self.sequence = self._solid(ttl, color)
            case 'bullet':
                self.sequence = self._bullet(ttl, color, delay)
            case 'blink':
                self.sequence = self._blink(ttl, color, delay)
            case 'alternate':
                self.sequence = self._alternate(ttl, color, delay)
            case 'flood':
                self.sequence = self._flood_fill(ttl, color, delay)
            case _:
                self.sequence = self._off(ttl)

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
    
    def _shift(self, backwards: bool = False, rotate: bool = True, shift_in: int = 0x000000):
        new_leds = self.leds.copy()
        if backwards: # Shift left
            new_leds[-1] = self.leds[0] if rotate else shift_in
            new_leds[:-1] = self.leds[1:]
        else: # Shift right
            new_leds[0] = self.leds[-1] if rotate else shift_in
            new_leds[1:] = self.leds[:-1]
        self.leds = new_leds
    
    def _delay(self, frames: int):
        if frames > 0:
            for i in range(frames):
                yield self.leds
    
    """ Sequence methods """
    def _off(self, ttl: int):
        self._fill(0x000000)
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds
            

    def _bullet(self, ttl: int, color: int, delay: int):
        self._fill(0x000000)
        self.leds[0] = color
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds
            for buffer in self._delay(delay):
                elapsed += 1
                yield buffer
            self._shift()
    
    def _blink(self, ttl: int, color: int, delay: int):
        self._fill(0x000000)
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds
            for buffer in self._delay(delay):
                elapsed += 1
                yield buffer
            self.leds = [color-current_color for current_color in self.leds]
    
    def _solid(self, ttl: int, color: int):
        self._fill(color)
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds

    def _alternate(self, ttl: int, color: int, delay: int):
        toggle_on = True
        for i in range(self.segment_length):
            self.leds[i] = color if toggle_on else 0x000000
            toggle_on = not toggle_on
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds
            for buffer in self._delay(delay):
                elapsed += 1
                yield buffer
            self.leds = [color-current_color for current_color in self.leds]

    def _meteor(self, ttl: int, color: int, delay: int):
        pass

    def _rand_noise(self, ttl: int, color: int, delay: int):
        pass

    def _flood_fill(self, ttl: int, color: int, delay: int):
        self._fill(0x000000)
        self.leds[0] = color
        elapsed = 0
        while True:
            if ttl != 0:
                if elapsed < ttl:
                    elapsed += 1
                else:
                    break
            yield self.leds
            for buffer in self._delay(delay):
                elapsed += 1
                yield buffer
            self._shift(rotate=False, shift_in=color)


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