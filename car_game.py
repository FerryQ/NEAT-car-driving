import pygame
import time
import math

WIDTH, HEIGHT = (900,800)

WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")


run =  True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()