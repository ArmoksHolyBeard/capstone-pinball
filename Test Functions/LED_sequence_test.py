import time

class Lights:
    def __init__(self):
        self.sequence = self.__bullet()
        self.colors = [128, 0, 32, 0, 0, 16, 32, 32, 16]
    
    def __shiftRight(self, places: int = 1, rotate: bool = True):
        newColors = self.colors.copy()
        length = len(self.colors)
        end = length - 1
        places = places % length
        if places > 0:
            if rotate:
                newColors[:places] = self.colors[end-places+1:end+1]
                newColors[places:] = self.colors[:end-rotate+1]
            else:
                newColors[:places] = [0 for i in range(places)]
                newColors[places:] = self.colors[:end-rotate+1]
            self.colors = newColors
     
    def startSequence(self, newSequence: str):
        self.sequence.close()
        match newSequence:
            case 'bullet':
                self.sequence = self.__bullet()
            case 'blink':
                self.sequence = self.__blink()
    
    def update(self):
        return next(self.sequence)

    def __bullet(self):
        self.colors = [0 for c in self.colors]
        self.colors[0] = 255
        while True:
            yield self.colors
            self.__shiftRight()
    
    def __blink(self):
        self.colors = [0 for c in self.colors]
        while True:
            yield self.colors
            self.colors = [255-c for c in self.colors]

if __name__ == '__main__':
    light = Lights()
    light.startSequence('bullet')
    for i in range(20):
        print(light.update())
        time.sleep(0.2)
    light.startSequence('blink')
    for i in range(20):
        print(light.update())
        time.sleep(0.2)