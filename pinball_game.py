from enum import Enum
from queue import Queue
import random

import pygame
from pygame.locals import *
from pyvidplayer2 import Video

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
    
    def reset(self):
        self.points = 0


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

    """ Primary methods """
    def __init__(self, data_q: Queue, cmd_q: Queue, motor_q: Queue):
        self.data_q = data_q
        self.cmd_q = cmd_q
        self.motor_q = motor_q
        self.plc_data = {}
        self.drop_target_count = 0
        self.standing_target_count = 0
        
        # Set up LED segments
        self.left_side_lights = LightSegment(0, 50)
        self.left_deadlane_lights = LightSegment(51, 57)
        self.left_slingshot_lights = LightSegment(58, 59)
        self.ramp_lights = LightSegment(60, 67)
        self.goal_lights = LightSegment(68, 75)
        self.rear_lights = LightSegment(76, 95)
        self.right_side_lights = LightSegment(96, 145)
        self.right_deadlane_lights = LightSegment(146, 152)
        self.right_slingshot_lights = LightSegment(153, 154)
        self.freekick_lights = LightSegment(155, 166)

        self.ledController = LightController(
            self.left_side_lights,
            self.left_deadlane_lights,
            self.left_slingshot_lights,
            self.ramp_lights,
            self.goal_lights,
            self.rear_lights,
            self.right_side_lights,
            self.right_deadlane_lights,
            self.right_slingshot_lights,
            self.freekick_lights
        )

    def run_game(self):
        # Initialize pygame and pygame sound mixer
        pygame.init()
        pygame.mixer.init()

        # Initialize the game timer and specify the frame rate
        self.game_time = pygame.time.Clock()

        # Initialize the window to fullscreen
        self.screen = pygame.display.set_mode((1600, 900))#, pygame.FULLSCREEN)
        pygame.display.set_caption("Pinball Test")

        # Set up background
        self.background = pygame.image.load("C:/dev/pinball/capstone-pinball/media\munich_stadium.jpg")
        self.background.convert()

        # Initialize display objects
        self.score = Score(self.screen)
        self.lives = Lives(self.screen)

        # Initialize audio clips
        self.cheers = [
            pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/cheer1.wav"),
            pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/cheer2.ogg"),
            pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/cheer3.ogg"),
            pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/cheer4.ogg"),
            pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/cheer5.ogg")
        ]
        for clip in self.cheers:
            clip.set_volume(0.2)
        self.ding = pygame.mixer.Sound("C:/dev/pinball/capstone-pinball/media/ding.wav")

        # Initialize videos clips
        self.videos = [
            Video("C:/dev/pinball/capstone-pinball/media/messi_score.mp4"),
            Video("C:/dev/pinball/capstone-pinball/media/weissbach_ref.mp4")
        ]
        for video in self.videos:
            video.set_volume(0.1)
            video.stop()

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
    
    """ Game state methods """
    def _quit_game(self):
        self.cmd_q.put(PinballPLC.QUIT)
        self.motor_q.put(MotorController.EXIT)
        for video in self.videos:
            video.close()
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

        pygame.mixer.music.load("C:/dev/pinball/capstone-pinball/media/bertsz_drum_and_bass.ogg")
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
        plc_data = {}

        # Set a 10 sec grace period
        pygame.time.set_timer(self.TIMER_EVENT, 0)
        grace = True

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
                    grace = False
                    pygame.time.set_timer(self.TIMER_EVENT, 0)

                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))
                    if keys[K_f]:
                        self._play_video(0)
                    if keys[K_g]:
                        self._play_video(1)
                    if keys[K_r]:
                        self.score.addPoints(20000)
                        self.drop_target_count += 1
                    if keys[K_t]:
                        self.score.addPoints(1000)
                        self.standing_target_count += 1
                    if keys[K_p]:
                        self.lives.subtract_balls()
                        return GameState.END_OF_BALL
                
                # Handles the PLC based events
                if event.type == self.PLC_GET:
                    if plc_data['launch']:
                        pygame.time.set_timer(self.TIMER_EVENT, 10000)
                    if plc_data['bumper_1']:
                        self.score.addPoints(500)
                    if plc_data['bumper_2']:
                        self.score.addPoints(500)
                    if plc_data['bumper_3']:
                        self.score.addPoints(500)
                    if plc_data['dropTargets']:
                        self.score.addPoints(20000)
                        self.drop_target_count += 1
                    if plc_data['goal']:
                        self.score.addPoints(1000000)
                        self._play_video(1)
                    if plc_data['kickback']:
                        self.score.addPoints(1)
                    if (plc_data['lives'] < self.lives.balls) and not grace:
                        self.lives.subtract_balls()
                        return GameState.END_OF_BALL
                        # self.cmd_q.put(PinballPLC.LOCK)
                    if plc_data['rampSpinner']:
                        self.score.addPoints(100)
                    if plc_data['standingTargets']:
                        self.score.addPoints(1000)
                        self.standing_target_count += 1
                    plc_data = {}

            # Render the background and screen elements
            self.screen.blit(self.background)
            self.score.update()
            self.lives.update()

            for video in self.videos:
                if video.active:
                    video.draw(self.screen, (0, 0))
            
            # print(self.game_time.get_fps()) # FPS Counter
            
            pygame.display.flip()
            self.game_time.tick(self.FPS)

    def _end_of_ball(self):
        # return IN_PLAY when sequence ends, GAME_OVER if out of balls
        # Initialize screen elements
        bonus_font = pygame.font.Font(size=128)
        bonus_points = (self.standing_target_count+1) * 500
        bonus_mult = self.drop_target_count + 1
        bonus_text = bonus_font.render(f"{bonus_points} x {bonus_mult} = {bonus_points*bonus_mult}", True, (40, 40, 40))

        # Display for 5 seconds
        pygame.time.set_timer(self.TIMER_EVENT, 3000)

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
                    return GameState.GAME_OVER
                
                if event.type == self.TIMER_EVENT:
                    self.score.addPoints(bonus_points*bonus_mult)
                    self.standing_target_count = 0
                    self.drop_target_count = 0
                    if self.lives.balls <= 0:
                        return GameState.GAME_OVER
                    else:
                        return GameState.IN_PLAY
                
                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))

                # Handles the PLC based events
                if event.type == self.PLC_GET:
                    if plc_data['start_button']:
                        return GameState.IN_PLAY
                    plc_data = {}
            
            # Play sounds, animations, display high scores
            self.screen.blits([
                (self.background, (0, 0)),
                (bonus_text, (500, 230))
            ])

            pygame.display.flip()
            self.game_time.tick(self.FPS)

    def _game_over(self):
        # return ATTRACT after a period of time, IN_PLAY if start button pressed, QUIT if esc

        # Initialize screen elements
        gameover_font = pygame.font.Font(size=128)
        gameover_text = gameover_font.render("Game Over", True, (40, 40, 40))

        self.score.reset()

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
    
    """ Helper methods """
    def _play_video(self, index: int):
        for video in self.videos:
            if video.active:
                video.stop()
        self.videos[index].play()
        

if __name__ == "__main__":
    queues = []
    for i in range(3):
        queues.append(Queue())
    game = PinballManager(*queues)
    game.run_game()