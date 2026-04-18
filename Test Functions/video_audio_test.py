import pygame
from pygame.locals import *
from pyvidplayer2 import Video
import sys
import concurrent.futures

def run_pygame():
    pygame.init()
    pygame.mixer.init()

    gameTime = pygame.time.Clock()
    FPS = 30

    displaysurface = pygame.display.set_mode((600, 400))#, pygame.FULLSCREEN)
    pygame.display.set_caption("Pinball Test")

    cheer = pygame.mixer.Sound("C:\dev\pinball\capstone-pinball\media\cheer2.ogg")

    video = Video("C:\dev\pinball\capstone-pinball\media\messi_score.mp4")
    video.stop()

    while True:

        # Check all pygame events
        for event in pygame.event.get():

            # Quit the game
            if event.type == QUIT:
                video.close() 
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[K_g]:
                    video.play()
                if keys[K_d]:
                    cheer.play()
                if keys[K_ESCAPE]:
                    pygame.event.post(pygame.event.Event(QUIT))
            
        
        displaysurface.fill((255, 255, 255))

        if video.active:
            video.draw(displaysurface, (0, 0))

        pygame.display.flip()

        gameTime.tick(FPS)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        ex.submit(run_pygame)