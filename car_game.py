import pygame
import time
import math
import random
import car_utils as cu
from utils import scale_image, draw_rotate_car,rotate_car
from pygame.math import Vector2 as vec2
from car import PlayerCar

# window settings and initialization
pygame.init()
WIDTH, HEIGHT = (2400,1700)
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")

# Car settings
CAR = scale_image(pygame.image.load("images/car2.png").convert_alpha(), 0.4) # car image
CAR_SIZE_X, CAR_SIZE_Y = CAR.get_size() # car size
CAR_SPEED = 8 # car speed



#TEXT
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)


# Track settings
TRACK = pygame.image.load("images/track4.png").convert() # Track image
BORDER_COLOUR = (255, 255, 255) # Border colour for collision


START = (WIDTH//2, 500) # starting position
FPS = 60


# initializing car
def place_car(pos):
    print(pos)
    return PlayerCar(CAR_SPEED,4,pos,CAR)

# car update (moving, car collision, line collision)
def update(car):
    cu.move_player(car)
    cu.car_collision(WIN,car,TRACK)
    cu.line_collision(WIN,car,my_font,TRACK)

def reset_cars(car):
    for car in cars:
        car.reset()

run =  True
clock = pygame.time.Clock()
#player_car = PlayerCar(CAR_SPEED,4)

cars = []

while run:
    clock.tick(FPS) #speed of rendering

    #WIN.fill(BORDER_COLOUR)
    WIN.fill((0,0,0));
    WIN.blit(TRACK,(0,0))


    for car in cars:
        car.draw(WIN)
        update(car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            cars.append(place_car((x,y)))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_cars(cars)

    
    pygame.display.update()


pygame.quit()
