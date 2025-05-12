import pygame
import time
import math
import random
import button
import car_utils as cu
from utils import scale_image, draw_rotate_car,rotate_car
from pygame.math import Vector2 as vec2
from car import PlayerCar

# window settings and initialization
pygame.init()
WIDTH, HEIGHT = (1920,1080)
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

# Start menu
levels_img = pygame.image.load("images/levels.png").convert_alpha()
levels_button = button.Button(WIDTH/2,HEIGHT/2,levels_img,1)


# Track settings
TRACK = pygame.image.load("images/track4.png").convert() # Track image
BORDER_COLOUR = (255, 255, 255) # Border colour for collision


START = (WIDTH//2, 500) # starting position
FPS = 60
positions = [((1616, 1181), (1825, 1333)), ((1935, 748), (2184, 670)),((1606, 373), (1684, 163)), ((1027, 383), (879, 189)), ((477, 566), (263, 463)), ((347, 724), (196, 920)), ((396, 1490), (567, 1275))]


class Game_info:
    
    def __init__(self,started = False):
        self.started = started



# initializing car
def place_car(pos):
    return PlayerCar(CAR_SPEED,4,pos,CAR, TRACK, positions)

# car update (moving, car collision, line collision)
def update(car):
    car.update()
    cu.move_player(car)
    #cu.car_collision(WIN,car,TRACK)
    #cu.line_collision(WIN,car,my_font,TRACK)

def reset_cars(car):
    for car in cars:
        car.reset()

def make_gate(positions):
    for position in positions:
        pygame.draw.line(WIN, (0, 255, 255), (position[0]), (position[1]), 2)


run =  True
clock = pygame.time.Clock()
#player_car = PlayerCar(CAR_SPEED,4)



#list of cars
cars = []

#initializing game_info
game_info = Game_info()

while run:
    clock.tick(FPS) #speed of rendering
    
    while not game_info.started:
        WIN.fill((255,255,255));
        if levels_button.draw(WIN):
            game_info.started = True


        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_info.started = True


        

    #WIN.fill(BORDER_COLOUR)
    WIN.fill((0,0,0));
    WIN.blit(TRACK,(0,0))


    for car in cars:
        car.draw(WIN)
        if car.is_alive():
            text = my_font.render("ALIVE",False,(0, 255, 0))
            WIN.blit(text, (0, 25 * 10))
        else:
            text = my_font.render("DEAD",False,(255, 0, 0))
            WIN.blit(text, (0, 25 * 10))

        if car.reward_gates_collision():
            text = my_font.render("TOUCHING",False,(240, 0, 0))
            WIN.blit(text, (0, 25 * 15))
        else:
            text = my_font.render("NOT TOUCHING",False,(240, 70, 0))
            WIN.blit(text, (0, 25 * 15))




        update(car)
    make_gate(positions)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            print((x,y))
            cars.append(place_car((x,y)))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_cars(cars)

    
    pygame.display.update()

print(positions)
pygame.quit()
