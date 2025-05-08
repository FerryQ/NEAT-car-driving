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

REWARD_GATES = [((1315, 1287),(1394, 1462)),((1616, 1181), (1825, 1333)), ((1935, 748), (2184, 670)),((1606, 373), (1684, 163)), ((1027, 383), (879, 189)), ((477, 566), (263, 463)), ((72, 742),(312, 685)),((186, 1167),(437, 1009)),((219, 1247),(437, 1159)),((201, 1027),(425, 915))]



#TEXT
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)


# Track settings
TRACK = pygame.image.load("images/track4.png").convert() # Track image
BORDER_COLOUR = (255, 255, 255) # Border colour for collision


START = (1138, 1388)# starting position
FPS = 60

CURRENT_GENERATION = 0


def make_gate(positions):
    for position in positions:
        pygame.draw.line(WIN, (0, 255, 255), (position[0]), (position[1]), 2)

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
    distances = car.get_distance()
    return distances + [car.velocity.length(), car.angle]

def eval_genomes(genomes, config):
    nets = []
    cars = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        car = PlayerCar(CAR_SPEED, 4, START, CAR, TRACK, REWARD_GATES)
        cars.append(car)
        genome.fitness = 0

    global CURRENT_GENERATION
    CURRENT_GENERATION += 1

    run = True
    timer = 0
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        alive_counter = 0 # how many cars are alive

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i,car in enumerate(cars):
            inputs = get_inputs_for_network(car)
            output = nets[i].activate(inputs)

            apply_output_to_car(car, output)

            if car.is_alive():
                alive_counter += 1
                genomes[i][1].fitness += car.get_reward()
                car.update()


        


        timer += 1

        if alive_counter == 0:
            run = False
        if timer > 1000:
            run =  False
        
        


        WIN.fill((0,0,0));
        WIN.blit(TRACK,(0,0))
        for car in cars:
            if car.is_alive():
                car.draw(WIN)

        make_gate(REWARD_GATES)
        
        # Display Info
        text = my_font.render("Generation: " + str(CURRENT_GENERATION), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        WIN.blit(text, text_rect)

        text_surface = my_font.render(str(timer),False,(255,0,0))
        WIN.blit(text_surface,(1200,850))

        pygame.display.flip()









if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(eval_genomes, 1000)