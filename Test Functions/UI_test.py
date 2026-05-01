from enum import Enum
from queue import Queue
from datetime import datetime
import random

import pygame
from pygame.locals import *
from pyvidplayer2 import Video

YELLOW = (255, 255, 0)
GREEN = (0, 102, 51)

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
        self.font = pygame.font.Font(size=200)
        self.font.align = FONT_CENTER
        self.location = (960, 820)
        self.color = YELLOW
        self.points = 0
    
    def update(self):
        displayText = self.font.render(f"{self.points:,}", True, self.color)
        new_x = 960 - (displayText.size[0] // 2)
        self.location = (new_x, 820)
        self.surface.blit(displayText, self.location)
    
    def addPoints(self, points: int):
        self.points += points
    
    def reset(self):
        self.points = 0


class Lives:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(size=160)
        self.location = (1760, 60)
        self.color = YELLOW
        self.balls = 3
    
    def update(self):
        displayText = self.font.render(str(self.balls), True, self.color)
        self.surface.blit(displayText, self.location)
    
    def subtract_balls(self):
        self.balls -= 1


class PinballManager:
    FPS = 30

    """ Primary methods """
    def __init__(self):
        self.plc_data = {}
        self.drop_target_count = 0
        self.standing_target_count = 0
        self.directory = "C:/dev/pinball/capstone-pinball/"
        # self.directory = "/home/ian/capstone-pinball/"

    def run_game(self):
        # Initialize pygame and pygame sound mixer
        pygame.init()
        pygame.mixer.init()

        # Initialize the game timer and specify the frame rate
        self.game_time = pygame.time.Clock()

        # Initialize the window to fullscreen
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("World Cup Pinball")

        # Set up background
        self.background = pygame.image.load(self.directory + "media/background.png")
        self.background.convert()

        # Initialize display objects
        self.score = Score(self.screen)
        self.lives = Lives(self.screen)

        # Initialize audio clips
        self.cheers = [
            pygame.mixer.Sound(self.directory + "media/cheer1.wav"),
            pygame.mixer.Sound(self.directory + "media/cheer2.ogg"),
            pygame.mixer.Sound(self.directory + "media/cheer3.ogg"),
            pygame.mixer.Sound(self.directory + "media/cheer4.ogg"),
            pygame.mixer.Sound(self.directory + "media/cheer5.ogg")
        ]
        for clip in self.cheers:
            clip.set_volume(0.2)
        self.kicks = [
            pygame.mixer.Sound(self.directory + "media/kick_1.ogg"),
            pygame.mixer.Sound(self.directory + "media/kick_2.ogg"),
        ]
        for clip in self.kicks:
            clip.set_volume(0.2)
        self.whistle = pygame.mixer.Sound(self.directory + "media/whistle.ogg")
        self.whistle.set_volume(0.2)
        self.goooooaaal = pygame.mixer.Sound(self.directory + "media/cantor-goal.ogg")
        self.whistle.set_volume(0.2)

        # Initialize videos clips
        self.videos = [
            Video(self.directory + "media/weissbach-celebrate.mp4"),
            Video(self.directory + "media/weissbach-redcard.mp4")
        ]
        for video in self.videos:
            video.set_volume(0)
            video.change_resolution(760)
            video.stop()

        # Set up custom events
        self.TIMER_EVENT = pygame.USEREVENT + 0
        self.PLC_GET = pygame.USEREVENT + 1
        self.MOTOR_GET = pygame.USEREVENT + 2

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
        for video in self.videos:
            video.close()
        pygame.mixer.quit()
        pygame.quit()
        return

    def _system_init(self):
        return GameState.ATTRACT

    def _attract_screen(self):
        # Initialize screen elements
        title_font = pygame.font.Font(size=200)
        pressme_font = pygame.font.Font(size=200)

        title_text = title_font.render("World Cup Pinball", True, GREEN)
        pressme_text = pressme_font.render("Press Start", True, YELLOW)

        pygame.mixer.music.load(self.directory + "media/bertsz_drum_and_bass.ogg")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        pygame.time.set_timer(self.TIMER_EVENT, 1000)

        while True:
            # Check all pygame events
            for event in pygame.event.get():
                # Quit the game
                if event.type == QUIT:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    return GameState.GAME_OVER
                
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
                        return GameState.IN_PLAY

            # Play sounds, animations, display high scores
            self.screen.blits([
                (self.background, (0, 0)),
                (title_text, (300, 150)),
                (pressme_text, (960 - (pressme_text.size[0] // 2), 820))
            ])

            pygame.display.flip()
            self.game_time.tick(self.FPS)
    
    def _in_play(self):

        pygame.time.set_timer(self.TIMER_EVENT, 0)

        pygame.mixer.music.stop()

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
                    if keys[K_1]:
                        self.lives.subtract_balls()
                        return GameState.END_OF_BALL
                    if keys[K_2]:
                        self.score.addPoints(1000)
                        random.choice(self.kicks).play()
                        self.standing_target_count += 1
                    if keys[K_3]:
                        self.goooooaaal.play()
                        self._play_video(0)
                    if keys[K_4]:
                        self._play_video(1)
                        self.whistle.play()
                    if keys[K_5]:
                        self.score.addPoints(9999)
                        random.choice(self.kicks).play()
                        self.drop_target_count += 1

            self.screen.blit(self.background)
            self.score.update()
            self.lives.update()

            for video in self.videos:
                if video.active:
                    vid_width, vid_height = video.current_size
                    video.draw(self.screen, (960 - (vid_width // 2), 20))
            pygame.display.flip()
            self.game_time.tick(self.FPS)

    def _end_of_ball(self):
        # return IN_PLAY when sequence ends, GAME_OVER if out of balls
        # Initialize screen elements
        factor_font = pygame.font.Font(size=128)
        bonus_font = pygame.font.Font(size=200)
        bonus_base = 1
        bonus_mult = 1
        bonus = 0
        total_bonus = bonus_font.render(f"+{bonus}", True, YELLOW)
        label = factor_font.render("Bonus", True, GREEN)
        bonus_targets = factor_font.render("", True, GREEN)
        bonus_flags = factor_font.render("", True, GREEN)

        # Display for 5 seconds
        pygame.time.set_timer(self.TIMER_EVENT, 500)

        end_of_ball_index = 0

        # Play failure video
        # self._play_video(1)

        while True:
            # Check all pygame events
            for event in pygame.event.get():
                # Quit the game
                if event.type == QUIT:
                    return GameState.GAME_OVER
                
                if event.type == self.TIMER_EVENT:
                    total_bonus = bonus_font.render(f"+{bonus}", True, YELLOW)
                    if end_of_ball_index == 0:
                        random.choice(self.kicks).play()
                        bonus_targets = factor_font.render(f"Targets hit: {bonus_base}", True, (40, 40, 40))
                        bonus += 500
                        if bonus_base <= self.standing_target_count:
                            bonus_base += 1
                        else:
                            end_of_ball_index += 1
                    elif end_of_ball_index == 1:
                        random.choice(self.kicks).play()
                        bonus_flags = factor_font.render(f"Flags on Field: x{bonus_mult}", True, (40, 40, 40))
                        bonus += bonus
                        if bonus_mult <= self.drop_target_count:
                            bonus_mult += 1
                        else:
                            end_of_ball_index += 1
                            pygame.time.set_timer(self.TIMER_EVENT, 3000)
                    elif end_of_ball_index == 2:
                        self.score.addPoints(bonus)
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

            self.screen.blits([
                (self.background, (0, 0)),
                (total_bonus, (960 - (total_bonus.size[0] // 2), 820)),
                (label, (600, 80)),
                (bonus_targets, (600, 180)),
                (bonus_flags, (600, 260))
            ])
                             
            pygame.display.flip()
            self.game_time.tick(self.FPS)

    def _game_over(self):
        # return ATTRACT after a period of time, IN_PLAY if start button pressed, QUIT if esc

        # Initialize screen elements
        gameover_font = pygame.font.Font(size=200)
        gameover_text = gameover_font.render("Game Over", True, YELLOW)

        # Save score to high score log
        highscores = []
        with open("high_scores.txt", "a") as file:
            file.write(f"{self.score.points}, Date: {datetime.now()}\n")
        with open("high_scores.txt") as file:
            for line in file:
                highscores.append(int(line.split(',')[0]))
        highscore = max(highscores)

        pygame.time.set_timer(self.TIMER_EVENT, 4000)
        game_over_index = 0

        while True:
            # Check all pygame events
            for event in pygame.event.get():
                # Quit the game
                if event.type == QUIT:  
                    return GameState.QUIT
                
                if event.type == self.TIMER_EVENT:
                    if game_over_index == 0:
                        gameover_text = gameover_font.render("Final Score", True, YELLOW)
                        pygame.time.set_timer(self.TIMER_EVENT, 2000)
                    elif game_over_index == 1:
                        gameover_text = gameover_font.render(f"{self.score.points:,}", True, YELLOW)
                        pygame.time.set_timer(self.TIMER_EVENT, 5000)
                    elif game_over_index == 2:
                        gameover_text = gameover_font.render("Highscore", True, YELLOW)
                        pygame.time.set_timer(self.TIMER_EVENT, 2000)
                    elif game_over_index == 3:
                        gameover_text = gameover_font.render(f"{highscore:,}", True, YELLOW)
                        pygame.time.set_timer(self.TIMER_EVENT, 5000)
                    elif game_over_index == 4:
                        self.score.reset()
                        self.lives.balls = 3
                        return GameState.ATTRACT
                    game_over_index += 1
                
                # Handles any key presses
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[K_ESCAPE]:
                        pygame.event.post(pygame.event.Event(QUIT))
                    if keys[K_SPACE]:
                        return GameState.IN_PLAY

            self.screen.blits([
                (self.background, (0, 0)),
                (gameover_text, (960 - (gameover_text.size[0] // 2), 820))
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
    game = PinballManager()
    game.run_game()
