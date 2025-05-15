import pygame
import time
import math
import random
import button
import neat
import sys
import car_utils as cu
from simul import Simulation
from utils import scale_image, draw_rotate_car,rotate_car
from pygame.math import Vector2 as vec2
from car import NormalCar, DriftCar

# window settings and initialization
pygame.init()
WIDTH, HEIGHT = (1920,1080)
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")

# Car settings
CAR = scale_image(pygame.image.load("images/car2.png").convert_alpha(), 0.4) # car image
CAR_SIZE_X, CAR_SIZE_Y = CAR.get_size() # car size
CAR_SPEED = 6 # car speed
BEST_CAR = scale_image(pygame.image.load("images/best_car.png").convert_alpha(), 0.4) # car image



        



#TEXT
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)
guide_font = pygame.font.SysFont('purisa', 50)


# Start menu
levels_img = pygame.image.load("images/levels.png").convert_alpha()
level1_img = pygame.image.load("images/lvl1.png").convert_alpha()
level2_img = pygame.image.load("images/lvl2.png").convert_alpha()
level3_img = pygame.image.load("images/lvl3.png").convert_alpha()
myo_img = pygame.image.load("images/myo.png").convert_alpha()
drift_car_img = scale_image(pygame.image.load("images/drift.png").convert_alpha(),2)
normal_car_img = scale_image(pygame.image.load("images/normal.png").convert_alpha(),2)

level1_track_img = scale_image(pygame.image.load("images/track1.png").convert_alpha(),0.1125)
level2_track_img = scale_image(pygame.image.load("images/track2.png").convert_alpha(),0.1125)





levels_button = button.Button(810,526,levels_img,1) 
level1_button = button.Button(350,302,level1_img,1)
level2_button = button.Button(550,302,level2_img,1)
level3_button = button.Button(750,302,level3_img,1)
myo_button = button.Button(950,302,myo_img,1)

drift_car_button = button.Button(760-drift_car_img.get_width()/2,500,drift_car_img,1)
normal_car_button = button.Button(1160 - normal_car_img.get_width()/2 ,500,normal_car_img,1)





# Track settings
TRACK1 = pygame.image.load("images/track1.png").convert() # Track image
TRACK2 = pygame.image.load("images/track2.png").convert() # Track image



BORDER_COLOUR = (255, 255, 255) # Border colour for collision


START = (WIDTH//2, 500) # starting position
FPS = 60
positions = [((1616, 1181), (1825, 1333)), ((1935, 748), (2184, 670)),((1606, 373), (1684, 163)), ((1027, 383), (879, 189)), ((477, 566), (263, 463)), ((347, 724), (196, 920)), ((396, 1490), (567, 1275))]


class Game_info:
    
    def __init__(self,started = False,levels_menu=False):
        self.started = started
        self.levels_menu = levels_menu

        self.drift_car = False
        self.normal_car = False

        self.level_one = False

        self.level_two = False

        self.level_three = False

        self.myo_level = False


def drift_normal(win,track,start_pos):
    while not game_info.drift_car and not game_info.normal_car:
        win.fill((190,190,210))

        text1 = guide_font.render("PICK DRIVING MODE",True,(0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        win.blit(text1,((WIDTH/2) - (text1.get_width()//2),50))
        pygame.draw.line(win,(255,0,0),(960,0),(960,1080),3)

        if drift_car_button.draw(win):
            game_info.drift_car = True
        if normal_car_button.draw(win):
            game_info.normal_car = True
        pygame.display.update()

    if game_info.drift_car:
        simulation = Simulation(win,1000,track,CAR_SPEED,start_pos,CAR,BEST_CAR,True)

        simulation.run_simulation()
    else:
        simulation = Simulation(win,1000,track,CAR_SPEED,start_pos,CAR,BEST_CAR)

        simulation.run_simulation()




# initializing car
def place_car(pos,track):
    return DriftCar(CAR_SPEED,4,pos,CAR, track, positions)

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
#player_car = NormalCar(CAR_SPEED,4)

cars = []

#initializing game_info
game_info = Game_info()


while run:
    clock.tick(FPS) #speed of rendering
    
    #game menu
    while not game_info.started:
        WIN.fill((255,255,255))
            
        if levels_button.draw(WIN):
            game_info.levels_menu = True
        
        if game_info.levels_menu:
            WIN.fill((190,190,210))
            #action level 1 button
            WIN.blit(level1_track_img,(330,160))
            if level1_button.draw(WIN):
                game_info.started = True
                game_info.level_one = True
            #action level 2 button
            WIN.blit(level2_track_img,(530,160))
            if level2_button.draw(WIN):
                game_info.started = True
                game_info.level_two = True
            
            #action level 3 button
            if myo_button.draw(WIN):
                game_info.started = True
                game_info.myo_level = True
                WIN.fill((255,255,255))


        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sys.exit()
    
    while game_info.level_one:
        drift_normal(WIN,TRACK1,(660,895))

    #level two
    while game_info.level_two:
        drift_normal(WIN,TRACK2,(700,987))

    drawing = False
    placed_car = False
    track_done = False
    start_pos = None
    TRACK_DRAWN = pygame.Surface((1400,1080))
    TRACK_DRAWN.fill((255, 255, 255))
    #level three
    while game_info.myo_level:
        clock.tick(FPS) #speed of rendering

      # white background
        



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Start drawing
            if event.type == pygame.MOUSEBUTTONDOWN and not track_done:
                if event.button == 1:  # Left mouse button
                    drawing = True

            # Stop drawing
            if event.type == pygame.MOUSEBUTTONUP and not track_done:
                if event.button == 1:
                    drawing = False

            if event.type == pygame.MOUSEBUTTONDOWN and track_done:
                x, y = pygame.mouse.get_pos()
                start_pos = (x,y)

                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    x, y = pygame.mouse.get_pos()
                    cars.append(place_car((x,y),TRACK_DRAWN))
                    placed_car = True
                if event.key == pygame.K_SPACE:
                    track_done = True

        WIN.fill((255, 255, 255))
        WIN.blit(TRACK_DRAWN, (0, 0))
        if not track_done:
            text1 = guide_font.render("Draw with your mouse",True,(0,0,0))
            text2 = guide_font.render("if you are done press SPACEBAR",True,(0,0,0))

            WIN.blit(text1,((WIDTH/2) - (text1.get_width()//2),50))
            WIN.blit(text2,((WIDTH/2) - (text2.get_width()//2),50+text1.get_height()))

        if track_done and not start_pos:
            x, y = pygame.mouse.get_pos()
            WIN.blit(CAR,(x,y))
            text1 = guide_font.render("Now pick a starting position with left click",True,(0,0,0))

            WIN.blit(text1,((WIDTH/2) - (text1.get_width()//2),50))



            
    # Draw while holding mouse
        for car in cars:
            if placed_car:
                car.draw(WIN)
                update(car)
        if drawing:
            x, y = pygame.mouse.get_pos()
            pygame.draw.circle(TRACK_DRAWN, (0, 0, 0), (x, y), 50)

        if start_pos:
            drift_normal(WIN,TRACK_DRAWN,start_pos)
            



        pygame.display.update()

        """

        simulation = Simulation(WIN,1000,TRACK2,CAR_SPEED,(690,975),CAR)

        simulation.run_simulation()
        """

        


    
    pygame.display.update()

pygame.quit()
