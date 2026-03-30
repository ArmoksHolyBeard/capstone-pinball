from enum import Enum
from queue import Queue

import pygame
from pygame.locals import *
import pygvideo

from pinball_LED import LightController, LightSegment


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


class PinballManager:
    FPS = 30

    def __init__(self, data_q: Queue, cmd_q: Queue, motor_q: Queue):
        self.data_q = data_q
        self.cmd_q = cmd_q
        self.motor_q = motor_q
        self.plc_data = {}
        
        # Set up LED segments
        self.goalLights = LightSegment(20, 29)
        self.slingshotLight_left = LightSegment(2)
        self.slingshotLight_right = LightSegment(3)
        self.ledController = LightController(
            self.goalLights,
            self.slingshotLight_left,
            self.slingshotLight_right
        )

    def run_game(self):
        # Initialize pygame and pygame sound mixer
        pygame.init()
        pygame.mixer.init()

        # Initialize the game timer and specify the frame rate
        self.gameTime = pygame.time.Clock()

        # Initialize the window to fullscreen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Pinball Test")

        # Set up background
        self.background = pygame.image.load("media\munich_stadium.jpg")
        self.background.convert()

        # Initialize display objects
        self.score = Score(self.screen)
        self.lives = Lives(self.screen)

        # Initialize audio and video clips
        self.cheer = pygame.mixer.Sound("media/cheer.wav")
        self.ding = pygame.mixer.Sound("media/ding.wav")

        self.video1 = pygvideo.Video("media/messi_score.mp4")
        self.video1.set_size(self.screen.get_size())

        self.video2 = pygvideo.Video("media/weissbach_ref.mp4")
        self.video2.set_size([608, self.screen.get_size()[1]])

        # Set up custom events
        self.PLC_GET = pygame.USEREVENT + 1

        # Game Loop
        game_state = GameState.IN_PLAY
        while True:
            if game_state == GameState.QUIT:
                game_state = self._quit_game()
                return
            if game_state == GameState.ATTRACT:
                game_state = self._attract_screen()
            if game_state == GameState.IN_PLAY:
                game_state = self._in_play()
            if game_state == GameState.END_OF_BALL:
                game_state = self._end_of_ball()
            if game_state == GameState.GAME_OVER:
                game_state = self._attract_screen()
    
    def _quit_game(self):
        self.cmd_q.put("quit")
        pygvideo.quit_all()
        pygame.quit()
        return
    
    def _attract_screen(self):
        # Initialize screen elements, zero PLC counters
        while True:
            # Play sounds, animations, display high scores
            return # QUIT if esc, IN_PLAY if start button pressed
    
    def _in_play(self):
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
                
                # Handles the PLC based events
                if event.type == self.PLC_GET:
                    if plc_data['bumper_1']:
                        self.score.addPoints(500)
                    if plc_data['bumper_2']:
                        self.score.addPoints(500)
                    if plc_data['bumper_3']:
                        self.score.addPoints(500)
                    if plc_data['dropTargets']:
                        self.score.addPoints(20000)
                    if plc_data['goal']:
                        self.score.addPoints(1000000)
                        self.video1.play()
                    if plc_data['kickback']:
                        self.score.addPoints(1)
                    if plc_data['lives'] < self.lives.balls:
                        self.lives.subtract_balls()
                    if plc_data['rampSpinner']:
                        self.score.addPoints(100)
                    if plc_data['standingTargets']:
                        self.score.addPoints(1000)
                        self.cheer.play()
                    plc_data = {}

            # Post event when PLC comms returns with a value
            if not self.data_q.empty():
                plc_data = self.data_q.get()
                pygame.event.post(pygame.event.Event(self.PLC_GET))

            # screen.fill((10, 10, 10))
            self.screen.blit(self.background)
            self.score.update()
            self.lives.update()

            if self.video1.is_play:
                self.video1.draw_and_update(self.screen, (0, 0))
            elif self.video2.is_play:
                self.video2.draw_and_update(self.screen, (500, 0))
            
            pygame.display.flip()
            self.gameTime.tick(self.FPS)

    def _end_of_ball(self):
        # Initialize screen elements
        while True:
            # Display end of ball bonus and total
            return # IN_PLAY when sequence ends, GAME_OVER if out of balls

    def _game_over(self):
        # Initialize screen elements, zero PLC counters
        while True:
            # Display game over, high scores
            return # ATTRACT after a period of time, IN_PLAY if start button pressed, QUIT if esc


if __name__ == "__main__":
    queues = []
    for i in range(3):
        queues.append(Queue())
    game = PinballManager(*queues)
    game.run_game()