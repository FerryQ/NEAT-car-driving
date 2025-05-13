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
from car import PlayerCar

# window settings and initialization
pygame.init()
WIDTH, HEIGHT = (1920,1080)
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")

# Car settings
CAR = scale_image(pygame.image.load("images/car2.png").convert_alpha(), 0.4) # car image
CAR_SIZE_X, CAR_SIZE_Y = CAR.get_size() # car size
CAR_SPEED = 6 # car speed



#TEXT
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)

# Start menu
levels_img = pygame.image.load("images/levels.png").convert_alpha()
level1_img = pygame.image.load("images/level1.png").convert_alpha()
level2_img = pygame.image.load("images/level2.png").convert_alpha()

level1_track_img = scale_image(pygame.image.load("images/track1.png").convert_alpha(),0.1125)





levels_button = button.Button(810,526,levels_img,1) 
level1_button = button.Button(358,302,level1_img,1)

level2_button = button.Button(535,302,level2_img,1)
level3_button = button.Button(735,302,level2_img,1)




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
        self.level_one = False

        self.level_two = False
        self.level_two_ran = False

        self.level_three = False
        self.level_three_ran = False




# initializing car
def place_car(pos,track):
    return PlayerCar(CAR_SPEED,6,pos,CAR, track, positions)

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

cars = []

#initializing game_info
game_info = Game_info()

# NEAT

CURRENT_GENERATION = 0


def make_gate(positions):
    for position in positions:
        pygame.draw.line(WIN, (0, 255, 255), (position[0]), (position[1]), 2)

def apply_output_to_car(car,output):
    

    if output == 0:
        car.rotate(left=True)
    elif output == 1:
        car.rotate(right=True)
    elif output == 2:
        car.start_accel() 
    elif output == 3:
        car.start_brake()
    elif output == 4:
        car.release_pedals()

    
def get_inputs_for_network(car):
    distances = car.get_distance()
    return distances + [car.vel, car.angle]

def eval_genomes(genomes, config, track,win,start):

    nets = []
    cars = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        car = PlayerCar(CAR_SPEED, 6, start, CAR, track)
        cars.append(car)
        genome.fitness = 0

    global CURRENT_GENERATION
    CURRENT_GENERATION += 1

    run = True
    timer = 0
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        no_speed = 0
        alive_counter = 0 # how many cars are alive

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i,car in enumerate(cars):
            inputs = get_inputs_for_network(car)
            outputs = nets[i].activate(inputs)
            output = outputs.index(max(outputs))

            apply_output_to_car(car, output)

            if car.is_alive():
                if car.vel == 0:
                    no_speed += 1
                alive_counter += 1
                genomes[i][1].fitness += car.get_reward()
                car.update()


        timer += 1

        if timer > 1 and alive_counter == no_speed:
            run = False

        if alive_counter == 0:
            run = False
        if timer > 1000:
            run =  False
        
        win.fill((0,0,0));
        win.blit(track,(0,0))
        for car in cars:
            if car.is_alive():
                car.draw(win)

        #make_gate(REWARD_GATES)
        
        # Display Info
        text = my_font.render("Generation: " + str(CURRENT_GENERATION), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        win.blit(text, text_rect)

        text_surface = my_font.render(str(timer),False,(255,0,0))
        win.blit(text_surface,(1200,850))

        pygame.display.flip()






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
            WIN.blit(level1_track_img,(300,160))
            if level1_button.draw(WIN):
                game_info.started = True
                game_info.level_one = True
            #action level 2 button
            if level2_button.draw(WIN):
                game_info.started = True
                game_info.level_two = True
            
            #action level 3 button
            if level3_button.draw(WIN):
                game_info.started = True
                game_info.level_three = True

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_info.started = True
    
    while game_info.level_one:
        clock.tick(FPS) #speed of rendering

        WIN.fill((0,0,255))
        WIN.blit(TRACK1,(0,0))
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                game_info.level_one = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                print((x,y))
                cars.append(place_car((x,y),TRACK1))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_cars(cars)

        pygame.display.update()

    #level two
    while game_info.level_two:
        simulation = Simulation(WIN,1000,TRACK1,CAR_SPEED,(660,895),CAR)

        simulation.run_simulation()
    
    #level three
    while game_info.level_three:
        simulation = Simulation(WIN,1000,TRACK2,CAR_SPEED,(690,975),CAR)

        simulation.run_simulation()

        


    
    pygame.display.update()

pygame.quit()
