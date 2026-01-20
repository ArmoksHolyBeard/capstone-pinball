import pygame
from pygame.locals import *
import sys
import random

RED = (210, 50, 50)
ORANGE = (230, 110, 50)
YELLOW = (225, 225, 10)
GREEN = (0, 225, 50)
BLUE = (70, 130, 240)
PURPLE = (200, 0, 210)

colorList = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 512

class TestObject:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=64)
        self.location = [random.randint(0, 500), random.randint(0, 500)]
        self.velocity = [10, 5]
        self.color = RED
        self.text = "HELLO, WORLD!"
    
    def update(self):
        self.location[0] += self.velocity[0]
        self.location[1] += self.velocity[1]

        if ((self.location[0] >= SCREEN_WIDTH-350) and (self.velocity[0] > 0)) or ((self.location[0] <= 0) and (self.velocity[0] < 0)):
            self.velocity[0] = -self.velocity[0]
            self.color = random.choice(colorList)

        if (self.location[1] >= SCREEN_HEIGHT-32) and (self.velocity[1] > 0) or ((self.location[1] <= 0) and (self.velocity[1] < 0)):
            self.velocity[1] = -self.velocity[1]
            self.color = random.choice(colorList)

        displayText = self.font.render(self.text, True, self.color)
        self.surface.blit(displayText, self.location)

# Initialize pygame
pygame.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 24

# Initialize the window
displaysurface = pygame.display.set_mode((1024, 512))
pygame.display.set_caption("Pinball Test")

testText = TestObject(displaysurface)

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    displaysurface.fill((255, 255, 255))

    testText.update()

    pygame.display.update()
    gameTime.tick(FPS)

'''For the main GUI, look into PyGame. TKinter may work but might be tedious and not very flashy.
    Likely could stick to terminal during early development and polish it later.'''

'''For video, look into OpenCV or MoviePy. Might be able to play video directly. If using PyGame pygvideo might work'''

'''If using PyGame, it can handle game sounds'''

'''For communication with the PLC, look into pycomm3 or pylogix'''

'''Scoring will be coded from scratch'''