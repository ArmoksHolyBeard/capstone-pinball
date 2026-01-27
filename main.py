import pygame
from pygame.locals import *
import sys
import random
from pycomm3 import LogixDriver
from pinball_PLC import PinballPLC

RED = (210, 50, 50)
ORANGE = (230, 110, 50)
YELLOW = (225, 225, 10)
GREEN = (0, 225, 50)
BLUE = (70, 130, 240)
PURPLE = (200, 0, 210)

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 512

class Score:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=64)
        self.location = [random.randint(0, 500), random.randint(0, 500)]
        self.color = BLUE
        self.points = 0
    
    def update(self):
        displayText = self.font.render(str(self.points), True, self.color)
        self.surface.blit(displayText, self.location)
    
    def addPoints(self, points: int):
        self.points += points

# Initialize pygame
pygame.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 4

# Initialize the window
displaysurface = pygame.display.set_mode((1024, 512))
pygame.display.set_caption("Pinball Test")

# Set up custom events
PLC_GET = pygame.USEREVENT + 1

# Initialize display objects
score = Score(displaysurface)

# Set up PLC comms
plc = PinballPLC()
plc.start()

# Game Loop
while True:

    # Check all pygame events
    for event in pygame.event.get():

        # Quit the game
        if event.type == QUIT:  
            plc.end()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[K_g]:
                score.addPoints(500)
        
        # 
        if event.type == PLC_GET:
            plc.read()
            if plc.getTags() != 0:
                score.addPoints(750)

    
    if plc.isReady():
        pygame.event.post(pygame.event.Event(PLC_GET))

    displaysurface.fill((255, 255, 255))
    score.update()

    pygame.display.update()
    gameTime.tick(FPS)

'''For the main GUI, look into PyGame. TKinter may work but might be tedious and not very flashy.
    Likely could stick to terminal during early development and polish it later.'''

'''For video, look into OpenCV or MoviePy. Might be able to play video directly. If using PyGame pygvideo might work'''

'''If using PyGame, it can handle game sounds'''

'''For communication with the PLC, look into pycomm3 or pylogix'''

'''Scoring will be coded from scratch'''