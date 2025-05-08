import pygame
import neat
import sys
from car import PlayerCar
import car_utils as cu
from utils import scale_image

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


START = (1138, 1388)# starting position
FPS = 60

def update(car):
    # Move the car
    car.update()

    # Collision with border/track
    cu.car_collision(WIN, car, TRACK)


    # update distance traveled or checkpoints
    cu.line_collision(WIN, car, my_font, TRACK)

def apply_output_to_car(car,output):
    steer_left, steer_right, accelerate = output

    if steer_left > 0.5:
        car.rotate(left=True)
    if steer_right > 0.5:
        car.rotate(right=True)
    if accelerate > 0.5:
        car.start_accel()
    else:
        car.release_pedals()

def get_inputs_for_network(car):
    distances = car.get_distances()
    return distances + [car.velocity, car.angle]

def eval_genomes(genomes, config):
    nets = []
    cars = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        car = PlayerCar(CAR_SPEED, 4, START, CAR)
        cars.append(car)
        genome.fitness = 0

    run = True
    while run:
        for car in cars:
            inputs = car.get_distances()
            output = net.activate(inputs)

            apply_output_to_car(car, output)
            update(car)

        if car.is_alive():
            run = False
            break

        # Check for collision
        if car.crashed:
            run = False

        # Reward progress (distance or time survived)
        genome.fitness += 1

