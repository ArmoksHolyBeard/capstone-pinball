import pygame
from pygame.locals import *
import sys
import random
from pinball_PLC import PinballPLC
from pinball_LED import LightController, LightSegment
import pygvideo

class Score:
    # Maybe move these game objects to their own file
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=64)
        self.location = [surface.get_size()[0] // 2, surface.get_size()[1] - 100]
        self.color = (128, 128, 128)
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
FPS = 15

# Initialize the window to fullscreen
# displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
displaysurface = pygame.display.set_mode((600, 400))
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

# Set up PLC comms
plc = PinballPLC()
plc_data = {}

# Set up LED segments
goalLights = LightSegment(20, 29)
slingshotLight_left = LightSegment(2)
slingshotLight_right = LightSegment(3)
ledController = LightController(
    goalLights,
    slingshotLight_left,
    slingshotLight_right
)

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
        
        # Handles the PLC based events
        if event.type == PLC_GET:
            if plc_data['bumper_1']:
                score.addPoints(500)
            if plc_data['bumper_2']:
                score.addPoints(500)
            if plc_data['bumper_3']:
                score.addPoints(500)
            if plc_data['dropTargets']:
                score.addPoints(20000)
            if plc_data['goal']:
                score.addPoints(1000000)
                video.play()
            if plc_data['kickback']:
                score.addPoints(1)
            if plc_data['lives']:
                # Check difference
                pass
            if plc_data['rampSpinner']:
                score.addPoints(100)
            if plc_data['standingTargets']:
                score.addPoints(1000)
                cheer.play()
            plc.resetTags()

        # video.handle_event(event)

    # Post event when PLC comms returns with a value
    plc_data = plc.read()
    pygame.event.post(pygame.event.Event(PLC_GET))

    displaysurface.fill((255, 255, 255))
    score.update()

    if video.is_play:
        video.draw_and_update(displaysurface, (0, 0))
    
    pygame.display.flip()
    gameTime.tick(FPS)

# Maybe move these cleanup tasks to a function
plc.end()
pygame.quit()
sys.exit()