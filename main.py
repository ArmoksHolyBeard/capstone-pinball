""" Game program for a pinball machine """

__author__ = 'Ian Means'

import sys
from enum import Enum
from queue import Queue
import concurrent.futures

import pygame
from pygame.locals import *
import pygvideo

from pinball_PLC import PinballPLC
from pinball_LED import LightController, LightSegment
from pinball_goaliemotor import MotorController


class GameState(Enum):
    QUIT = 0
    ATTRACT = 1
    IN_PLAY = 2
    END_OF_BALL = 3
    GAME_OVER = 4


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


# Create the data queues for PLC and motor controls
plc_q = Queue()
motor_q = Queue()

# Initialize pygame and pygame sound mixer
pygame.init()
pygame.mixer.init()

# Initialize the game timer and specify the frame rate
gameTime = pygame.time.Clock()
FPS = 30

# Initialize the window to fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pinball Test")

# Set up background
background = pygame.image.load("media\munich_stadium.jpg")
background.convert()

# Initialize display objects
score = Score(screen)
lives = Lives(screen)

# Initialize audio and video clips
cheer = pygame.mixer.Sound("media\cheer.wav")
ding = pygame.mixer.Sound("media\ding.wav")

video1 = pygvideo.Video("media\messi_score.mp4")
video1.set_size(screen.get_size())

video2 = pygvideo.Video("media\weissbach_ref.mp4")
video2.set_size([608, screen.get_size()[1]])

# Set up custom events
PLC_GET = pygame.USEREVENT + 1

# Set up PLC comms
plc = PinballPLC(plc_q, demo_mode=True) #demo_mode=True
plc_data = {}

# Set up goalie motor controls
motor = MotorController(motor_q)

# Set up LED segments
goalLights = LightSegment(20, 29)
slingshotLight_left = LightSegment(2)
slingshotLight_right = LightSegment(3)
ledController = LightController(
    goalLights,
    slingshotLight_left,
    slingshotLight_right
)

def thread_manager():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        ex.submit(game_manager)
        ex.submit(plc.read_loop)
        ex.submit(motor.run_motor)


def game_manager():
    # Game Loop
    game_state = GameState.ATTRACT
    while True:
        if game_state == GameState.QUIT:
            quit_game()
        if game_state == GameState.ATTRACT:
            game_state = attract_screen()   
        if game_state == GameState.IN_PLAY:
            game_state = in_play()
        if game_state == GameState.END_OF_BALL:
            game_state = end_of_ball()  
        if game_state == GameState.GAME_OVER:
            game_state = attract_screen()
        
def quit_game():
    # plc.end()
    pygame.quit()
    sys.exit()

def attract_screen():
    # Initialize screen elements, zero PLC counters
    while True:
        # Play sounds, animations, display high scores
        return # QUIT if esc, IN_PLAY if start button pressed

def in_play():
    # Initialize screen elements, zero PLC counters
    while True:
        # Check all pygame events
        for event in pygame.event.get():

            # Quit the game
            if event.type == QUIT:  
                return GameState.GAME_OVER
            
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
                    video1.play()
                if plc_data['kickback']:
                    score.addPoints(1)
                if plc_data['lives'] < lives.balls:
                    lives.subtract_balls()
                if plc_data['rampSpinner']:
                    score.addPoints(100)
                if plc_data['standingTargets']:
                    score.addPoints(1000)
                    cheer.play()
                plc_data = {}

            # video.handle_event(event)

        # Post event when PLC comms returns with a value
        if not plc_q.empty():
            plc_data = plc_q.get()
            pygame.event.post(pygame.event.Event(PLC_GET))

        # screen.fill((10, 10, 10))
        screen.blit(background)
        score.update()
        lives.update()

        if video1.is_play:
            video1.draw_and_update(screen, (0, 0))
        elif video2.is_play:
            video2.draw_and_update(screen, (500, 0))
        
        pygame.display.flip()
        gameTime.tick(FPS)

def end_of_ball():
    # Initialize screen elements
    while True:
        # Display end of ball bonus and total
        return # IN_PLAY when sequence ends, GAME_OVER if out of balls

def game_over():
    # Initialize screen elements, zero PLC counters
    while True:
        # Display game over, high scores
        return # ATTRACT after a period of time, IN_PLAY if start button pressed, QUIT if esc

if __name__ == '__main__':
    thread_manager()