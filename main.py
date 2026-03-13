import pygame
from pygame.locals import *
import sys
# import random
# from pinball_PLC import PinballPLC
# from pinball_LED import LightController, LightSegment
import pygvideo

class Score:
    # Maybe move these game objects to their own file
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=128)
        self.location = [surface.get_size()[0] // 2 - 100, surface.get_size()[1] - 100]
        self.color = (63, 63, 63)
        self.points = 0
    
    def update(self):
        displayText = self.font.render(str(self.points), True, self.color)
        self.surface.blit(displayText, self.location)
    
    def addPoints(self, points: int):
        self.points += points

class Lives:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=128)
        self.location = [surface.get_size()[0] - 100, 50]
        self.color = (63, 63, 63)
        self.balls = 3
    
    def update(self):
        displayText = self.font.render(str(self.balls), True, self.color)
        self.surface.blit(displayText, self.location)
    
    def subtract_balls(self):
        self.balls -= 1

# Initialize pygame and pygame sound mixer
pygame.init()
pygame.mixer.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 30

# Initialize the window to fullscreen
displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# displaysurface = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Pinball Test")

background = pygame.image.load("media\munich_stadium.jpg")
background.convert()

# Set up custom events
# PLC_GET = pygame.USEREVENT + 1

# Initialize display objects
score = Score(displaysurface)
lives = Lives(displaysurface)

# Initialize audio and video clips
cheer = pygame.mixer.Sound("media\cheer.wav")
ding = pygame.mixer.Sound("media\ding.wav")

video1 = pygvideo.Video("media\messi_score.mp4")
video1.set_size(displaysurface.get_size())

video2 = pygvideo.Video("media\weissbach_ref.mp4")
video2.set_size([608, displaysurface.get_size()[1]])

# Set up PLC comms
# plc = PinballPLC()
# plc_data = {}

# Set up LED segments
# goalLights = LightSegment(20, 29)
# slingshotLight_left = LightSegment(2)
# slingshotLight_right = LightSegment(3)
# ledController = LightController(
#     goalLights,
#     slingshotLight_left,
#     slingshotLight_right
# )

# Game Loop
running = True
while running:

    # Check all pygame events
    for event in pygame.event.get():

        # Quit the game
        if event.type == QUIT:  
            running = False
        
        # Handles any key presses
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                pygame.event.post(pygame.event.Event(QUIT))
            if keys[K_d]:
                lives.subtract_balls()
                video1.release()
                video2.prepare()
                video2.play()
                cheer.play()
            if keys[K_k]:
                score.addPoints(7500)
                video2.release()
                video1.prepare()
                video1.play()
            if keys[K_t]:
                score.addPoints(1000)
                ding.play()
        
        # Handles the PLC based events
        # if event.type == PLC_GET:
        #     if plc_data['bumper_1']:
        #         score.addPoints(500)
        #     if plc_data['bumper_2']:
        #         score.addPoints(500)
        #     if plc_data['bumper_3']:
        #         score.addPoints(500)
        #     if plc_data['dropTargets']:
        #         score.addPoints(20000)
        #     if plc_data['goal']:
        #         score.addPoints(1000000)
        #         video1.play()
        #     if plc_data['kickback']:
        #         score.addPoints(1)
        #     if plc_data['lives']:
        #         # Check difference
        #         pass
        #     if plc_data['rampSpinner']:
        #         score.addPoints(100)
        #     if plc_data['standingTargets']:
        #         score.addPoints(1000)
        #         cheer.play()
        #     plc.resetTags()

        # video.handle_event(event)

    # Post event when PLC comms returns with a value
    # plc_data = plc.read()
    # pygame.event.post(pygame.event.Event(PLC_GET))

    # displaysurface.fill((10, 10, 10))
    displaysurface.blit(background)
    score.update()
    lives.update()

    if video1.is_play:
        video1.draw_and_update(displaysurface, (0, 0))
    elif video2.is_play:
        video2.draw_and_update(displaysurface, (500, 0))
    
    pygame.display.flip()
    gameTime.tick(FPS)

# Maybe move these cleanup tasks to a function
# plc.end()
pygame.quit()
sys.exit()