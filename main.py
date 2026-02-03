import pygame
from pygame.locals import *
import sys
import random
from pycomm3 import LogixDriver
from pinball_PLC import PinballPLC
import pygvideo

RED = (210, 50, 50)
ORANGE = (230, 110, 50)
YELLOW = (225, 225, 10)
GREEN = (0, 225, 50)
BLUE = (70, 130, 240)
PURPLE = (200, 0, 210)

class Score:
    # Maybe move these game objects to their own file
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=64)
        self.location = [surface.get_size()[0] // 2, surface.get_size()[1] - 100]
        self.color = BLUE
        self.points = 0
    
    def update(self):
        displayText = self.font.render(str(self.points), True, self.color)
        self.surface.blit(displayText, self.location)
    
    def addPoints(self, points: int):
        self.points += points

# Initialize pygame and pygame sound mixer
pygame.init()
pygame.mixer.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 30

# Initialize the window to fullscreen
displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pinball Test")

# Set up custom events
PLC_GET = pygame.USEREVENT + 1

# Initialize display objects
score = Score(displaysurface)

# Initialize audio and video clips
cheer = pygame.mixer.Sound("Test Functions\cheer.wav")

video = pygvideo.Video("Test Functions\messi_score.mp4")
video.set_size(displaysurface.get_size())
video.prepare()

# # Set up PLC comms
# plc = PinballPLC()
# plc.start()

# Game Loop
running = True
while running:

    # Check all pygame events
    for event in pygame.event.get():

        # Quit the game
        if event.type == QUIT:  
            running = False
        
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[K_j]:
                score.addPoints(2500)
                cheer.play()
            if keys[K_f]:
                score.addPoints(20000)
                video.play()
            if keys[K_ESCAPE]:
                pygame.event.post(pygame.event.Event(QUIT))

        # if event.type == PLC_GET:
        #     plc.read()
        #     if plc.getTags() != 0:
        #         score.addPoints(750)

        # video.handle_event(event)

    # # Post event when PLC comms returns with a value
    # if plc.isReady():
    #     pygame.event.post(pygame.event.Event(PLC_GET))

    displaysurface.fill((255, 255, 255))
    score.update()

    if video.is_play:
        video.draw_and_update(displaysurface, (0, 0))
    
    pygame.display.flip()
    gameTime.tick(FPS)

# Maybe move these cleanup tasks to a function
# plc.end()
pygame.quit()
sys.exit()