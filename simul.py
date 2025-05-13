import neat
import pygame
import time
import sys
import numpy as np

from car import NormalCar, DriftCar

class Simulation:
    def __init__(self,win,max_generations, track, car_speed, start,car_img,drift_car=False):
        self.max_generations = max_generations
        self.win = win
        self.CURRENT_GENERATION = 0
        self.track = track
        self.car_speed = car_speed
        self.start = start
        self.stats = None
        self.car_img = car_img 
        self.drift_car = drift_car
        self.clock = pygame.time.Clock()
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)

        num_points = 65

        # Random (x, y) coordinates uniformly distributed
        x_coords = np.random.randint(1450, 1850, size=num_points)
        y_coords = np.random.randint(650, 1000, size=num_points)

        self.pixel_coords = np.column_stack((x_coords, y_coords))


    
    def make_gate(self,positions):
        for position in positions:
            pygame.draw.line(self.win, (0, 255, 255), (position[0]), (position[1]), 2)

    def apply_output_to_car(self,car,output):
        

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

        
    def get_inputs_for_network(self,car):
        distances = car.get_distance()
        if self.drift_car:
            return distances + [car.velocity.length(), car.angle]
        
        return distances + [car.vel, car.angle]

        

    def run_simulation(self):
        config_path = "./config.txt"
        config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    config_path)

        # Create Population And Add Reporters
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        population.add_reporter(self.stats)

        population.run(self.eval_genomes, 1000)

    def draw(self,cars,timer):
        self.win.fill((0,0,0));
        self.win.blit(self.track,(0,0))
        for car in cars:
            if car.is_alive():
                car.draw(self.win)

        for pixel in self.pixel_coords:
            pygame.draw.circle(self.win,(255,0,0),pixel,10)

        #make_gate(REWARD_GATES)
        
        # Display Info
        text = self.my_font.render("Generation: " + str(self.CURRENT_GENERATION), True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.topleft = (1400, 540)
        self.win.blit(text, text_rect)


        if self.stats.generation_statistics:
            species_list = self.stats.get_species_sizes()

            num_species = len(species_list[-1])

            text_surface = self.my_font.render(str(num_species),False,(255,0,0))
            self.win.blit(text_surface,(1400,850))

        text_surface = self.my_font.render(str(timer),False,(255,0,0))
        self.win.blit(text_surface,(1200,850))

        pygame.display.update()


    def eval_genomes(self,genomes, config):

        nets = []
        cars = []
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            if self.drift_car:
                car = DriftCar(self.car_speed, 6, self.start, self.car_img, self.track)
            else:
                car = NormalCar(self.car_speed, 6, self.start, self.car_img, self.track)

            cars.append(car)
            genome.fitness = 0

        self.CURRENT_GENERATION += 1

        run = True
        timer = 0

        while run:
            self.clock.tick(60)
            no_speed = 0
            alive_counter = 0 # how many cars are alive

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        run = False

            for i,car in enumerate(cars):
                inputs = self.get_inputs_for_network(car)
                outputs = nets[i].activate(inputs)
                output = outputs.index(max(outputs))

                self.apply_output_to_car(car, output)

                if car.is_alive():
                    if car.vel == 0 and not self.drift_car:
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

            self.draw(cars,timer)
            
            
