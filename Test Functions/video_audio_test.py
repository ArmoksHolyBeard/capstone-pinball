import pygame
from pygame.locals import *
import pygvideo
import sys

pygame.init()
pygame.mixer.init()

gameTime = pygame.time.Clock()
FPS = 30

displaysurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pinball Test")

cheer = pygame.mixer.Sound("Test Functions\cheer.wav")

video = pygvideo.Video("Test Functions\messi_score.mp4")
video.set_size(displaysurface.get_size())
video.prepare()

while True:

    # Check all pygame events
    for event in pygame.event.get():

        # Quit the game
        if event.type == QUIT:  
            pygame.quit()
        
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[K_g]:
                video.play()
            if keys[K_d]:
                cheer.play()
            if keys[K_ESCAPE]:
                pygame.quit()
        
        video.handle_event(event)
    
    displaysurface.fill((255, 255, 255))

    if video.is_play:
        video.draw_and_update(displaysurface, (0, 0))

    pygame.display.flip()

    gameTime.tick(FPS)

sys.exit()