import pygame
from pygame.locals import *
import sys
import random

# Initialize pygame
pygame.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 2

# Initialize the window
displaysurface = pygame.display.set_mode((1024, 512))
pygame.display.set_caption("Pinball Test")


font = pygame.font.Font(size=64)
counter = 0

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    displaysurface.fill((255, 255, 255))

    counterText = font.render(str(counter), True, (0, 0, 0))
    displaysurface.blit(counterText, (random.randint(64, 960), random.randint(64, 512-64)))
    counter += 1

    pygame.display.update()
    gameTime.tick(FPS)

'''For the main GUI, look into PyGame. TKinter may work but might be tedious and not very flashy.
    Likely could stick to terminal during early development and polish it later.'''

'''For video, look into OpenCV or MoviePy. Might be able to play video directly. If using PyGame pygvideo might work'''

'''If using PyGame, it can handle game sounds'''

'''Lights will be APA102 addressable LEDs using SPI. Check ECET 434 textbook ch.8 for example using Luma'''

'''For communication with the PLC, look into pycomm3 or pylogix'''

'''Scoring will be coded from scratch'''