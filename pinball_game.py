from enum import Enum
from queue import Queue
import random

import pygame
from pygame.locals import *
import pygvideo

from pinball_LED import LightController, LightSegment
from pinball_PLC import PinballPLC
from pinball_goaliemotor import MotorController


class GameState(Enum):
    QUIT = 0
    INIT = 1
    ATTRACT = 2
    IN_PLAY = 3
    END_OF_BALL = 4
    GAME_OVER = 5


class Score:
    # Maybe move these game objects to their own file
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=128)
        self.location = (surface.get_size()[0] // 2 - 100, surface.get_size()[1] - 100)
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
        self.location = (surface.get_size()[0] - 100, 50)
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
        self.game_time = pygame.time.Clock()

        # Initialize the window to fullscreen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Pinball Test")

        # Set up background
        self.background = pygame.image.load("media\munich_stadium.jpg")
        self.background.convert()

        # Initialize display objects
        self.score = Score(self.screen)
        self.lives = Lives(self.screen)

        # Initialize audio clips
        self.cheers = [
            pygame.mixer.Sound("media/cheer1.wav"),
            pygame.mixer.Sound("media/cheer2.ogg"),
            pygame.mixer.Sound("media/cheer3.ogg"),
            pygame.mixer.Sound("media/cheer4.ogg"),
            pygame.mixer.Sound("media/cheer5.ogg")
        ]
        for clip in self.cheers:
            clip.set_volume(0.2)
        self.ding = pygame.mixer.Sound("media/ding.wav")

        # Initialize videos clips
        self.videos = [
            pygvideo.Video("media/messi_score.mp4"),
            pygvideo.Video("media/weissbach_ref.mp4")
        ]
        for video in self.videos:
            video.set_size(self.screen.get_size())
        # self.video2.set_size([608, self.screen.get_size()[1]])

        # Set up custom events
        self.TIMER_EVENT = pygame.USEREVENT + 0
        self.PLC_GET = pygame.USEREVENT + 1

        # Loop through possible gamestates
        game_state = GameState.INIT
        while True:
            if game_state == GameState.QUIT:
                game_state = self._quit_game()
                return
            if game_state == GameState.INIT:
                game_state = self._system_init()
            if game_state == GameState.ATTRACT:
                game_state = self._attract_screen()
            if game_state == GameState.IN_PLAY:
                game_state = self._in_play()
            if game_state == GameState.END_OF_BALL:
                game_state = self._end_of_ball()
            if game_state == GameState.GAME_OVER:
                game_state = self._game_over()
    
    def _quit_game(self):
        self.cmd_q.put("quit")
        # self.motor_q.put(MotorController.EXIT)
        pygvideo.quit_all()
        pygame.mixer.quit()
        pygame.quit()
        return

    def _system_init(self):
        return GameState.ATTRACT

    def _attract_screen(self):
        # Initialize screen elements
        title_font = pygame.font.Font(size=128)
        pressme_font = pygame.font.Font(size=72)

        title_text = title_font.render("World Cup Pinball", True, (40, 40, 40))
        pressme_text = pressme_font.render("Press Start", True, (60, 30, 60))

        pygame.mixer.music.load("media/bertsz_drum_and_bass.ogg")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        pygame.time.set_timer(self.TIMER_EVENT, 1000)

        plc_data = {}

        while True:

            # Post event when PLC comms returns with a value
            if not self.data_q.empty():
                plc_data = self.data_q.get()
                pygame.event.post(pygame.event.Event(self.PLC_GET))
            
            # Check all pygame events
            for event in pygame.event.get():
                # Quit the game
                if event.type == QUIT:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    return GameState.GAME_OVER # Change to GAME_OVER later
                
                if event.type == self.TIMER_EVENT:
                    sound = random.choice(self.cheers)
                    sound.play()
                    pygame.time.set_timer(self.TIMER_EVENT, int((sound.get_length()+2)*1000))
                
                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))
                    if keys[K_SPACE]:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        return GameState.IN_PLAY

                # Handles the PLC based events
                if event.type == self.PLC_GET:
                    if plc_data['start_button']:
                        return GameState.IN_PLAY
                    plc_data = {}

            # Play sounds, animations, display high scores
            self.screen.blits([
                (self.background, (0, 0)),
                (title_text, (500, 230)),
                (pressme_text, (600, 330))
            ])

            pygame.display.flip()
            self.game_time.tick(self.FPS)
    
    def _in_play(self):
        # Return END_OF_BALL if drain, GAME_OVER if esc

        # Initialize screen elements
        pygame.time.set_timer(self.TIMER_EVENT, 0)
        plc_data = {}
        while True:

            # Post event when PLC comms returns with a value
            if not self.data_q.empty():
                plc_data = self.data_q.get()
                pygame.event.post(pygame.event.Event(self.PLC_GET))

            # Check all pygame events
            for event in pygame.event.get():

                # Quit the game
                if event.type == QUIT:  
                    return GameState.GAME_OVER # Change to GAME_OVER later
                
                if event.type == self.TIMER_EVENT:
                    # self.cmd_q.put(PinballPLC.UNLOCK)
                    self.score.addPoints(1000)
                    pygame.time.set_timer(self.TIMER_EVENT, 0)

                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))
                    if keys[K_f]:
                        self._play_video(0)
                        pygame.time.set_timer(self.TIMER_EVENT, int(self.videos[0].get_duration()+500))
                
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
                        # self.videos[2].play()
                        # self.cmd_q.put(PinballPLC.LOCK)
                        # pygame.time.set_timer(self.TIMER_EVENT, int(self.videos[2].get_duration()))
                    if plc_data['rampSpinner']:
                        self.score.addPoints(100)
                    if plc_data['standingTargets']:
                        self.score.addPoints(1000)
                    plc_data = {}

            # Render the background and screen elements
            self.screen.blit(self.background)
            self.score.update()
            self.lives.update()

            for video in self.videos:
                if video.is_play:
                    video.draw_and_update(self.screen, (0, 0))
            
            # print(self.game_time.get_fps()) # FPS Counter
            
            pygame.display.flip()
            self.game_time.tick(self.FPS)

    def _end_of_ball(self):
        # return IN_PLAY when sequence ends, GAME_OVER if out of balls
        # Initialize screen elements
        # while True:
            # Display end of ball bonus and total
        pass

    def _game_over(self):
        # return ATTRACT after a period of time, IN_PLAY if start button pressed, QUIT if esc

        # Initialize screen elements
        gameover_font = pygame.font.Font(size=128)
        gameover_text = gameover_font.render("Game Over", True, (40, 40, 40))

        plc_data = {}

        while True:

            # Post event when PLC comms returns with a value
            if not self.data_q.empty():
                plc_data = self.data_q.get()
                pygame.event.post(pygame.event.Event(self.PLC_GET))
            
            # Check all pygame events
            for event in pygame.event.get():
                # Quit the game
                if event.type == QUIT:  
                    return GameState.QUIT
                
                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))
                    if keys[K_SPACE]:
                        return GameState.IN_PLAY

                # Handles the PLC based events
                if event.type == self.PLC_GET:
                    if plc_data['start_button']:
                        return GameState.IN_PLAY
                    plc_data = {}

            # Display game over, high scores
            self.screen.blits([
                (self.background, (0, 0)),
                (gameover_text, (500, 230))
            ])

            pygame.display.flip()
            self.game_time.tick(self.FPS)
    
    def _play_video(self, index: int):
        for video in self.videos:
            if video.is_ready:
                video.restop()
        self.videos[index].preplay()
        

if __name__ == "__main__":
    queues = []
    for i in range(3):
        queues.append(Queue())
    game = PinballManager(*queues)
    game.run_game()