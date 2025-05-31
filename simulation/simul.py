import neat
import neat.checkpoint
import pygame
from neural_network.NN import NN
import time
import sys
import numpy as np
from utils import button

from car_components.car import NormalCar, DriftCar

colours = [
    (255, 0, 0),  # red
    (0, 255, 0),  # green
    (0, 0, 255),  # blue
    (255, 255, 0),  # yellow
    (255, 0, 255),  # magenta
    (0, 255, 255),  # cyan
    (255, 165, 0),  # orange
    (128, 0, 128),  # purple
    (0, 128, 128),  # teal
    (128, 128, 0),  # olive
]


class Simulation:
    def __init__(
        self,
        win,
        max_generations,
        track,
        car_speed,
        start,
        car_img,
        best_car_img,
        drift_car=False,
        checkpoint=False,
    ):
        self.max_generations = max_generations
        self.win = win
        self.CURRENT_GENERATION = 0
        self.track = track
        self.car_speed = car_speed
        self.start = start
        self.stats = None
        self.car_img = car_img
        self.best_car_img = best_car_img
        self.drift_car = drift_car
        self.clock = pygame.time.Clock()
        self.best_nn = None
        self.best_fitness = -1000000
        self.best_index = 0
        self.my_font = pygame.font.SysFont("Comic Sans MS", 25)
        self.nns = [None] * 70
        self.exited = False
        self.checkpoint = checkpoint

        exit_img = pygame.image.load("images/EXIT.png").convert_alpha()

        self.exit_button = button.Button(1280, 0, exit_img, 1)

        # Nodes and connections

        num_points = 70

        # Random (x, y) coordinates uniformly distributed
        x_coords = np.random.randint(1450, 1850, size=num_points)
        y_coords = np.random.randint(650, 1000, size=num_points)

        self.pixel_coords = np.column_stack((x_coords, y_coords))

    def make_gate(self, positions):
        for position in positions:
            pygame.draw.line(self.win, (0, 255, 255), (position[0]), (position[1]), 2)

    def apply_output_to_car(self, car, output):

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

    def get_inputs_for_network(self, car):
        distances = car.get_distance()
        if self.drift_car:
            return distances + [car.velocity.length(), car.angle]

        return distances + [car.vel, car.angle]

    def run_simulation(self):
        config_path = "./config.txt"
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )

        if self.checkpoint:
            print("LOADED")
            population = neat.Checkpointer.restore_checkpoint("neat-checkpoint-10")
        else:
            print("NOT LOADED")
            population = neat.Population(config)

        # Create Population And Add Reporters
        population.add_reporter(neat.StdOutReporter(True))
        # population.add_reporter(neat.Checkpointer(generation_interval=5, filename_prefix='neat-checkpoint-'))

        self.stats = neat.StatisticsReporter()
        population.add_reporter(self.stats)

        # population.run(self.eval_genomes, 1000)
        try:
            population.run(self.eval_genomes, 1000)
        except neat.CompleteExtinctionException:
            neat.Checkpointer().save_checkpoint(
                config, population.population, population.species, 10
            )
            print("Stopped training early.")

    def draw(self, cars, timer):
        self.win.fill((0, 0, 0))
        self.win.blit(self.track, (0, 0))
        cars[self.best_index].best_car = True

        for car in cars:
            if car.is_alive() and not car.best_car:
                car.draw(self.win)

        if self.best_nn:
            self.best_nn.draw(self.win)

        cars[self.best_index].draw(self.win)
        pygame.draw.circle(self.win, (255, 0, 0), cars[self.best_index].position, 15)

        # Display Info
        text = self.my_font.render(
            "Generation: " + str(self.CURRENT_GENERATION), True, (255, 255, 255)
        )
        text_rect = text.get_rect()
        text_rect.topleft = (1400, 540)
        self.win.blit(text, text_rect)

        if self.stats.generation_statistics:
            species_list = self.stats.get_species_sizes()
            num_species = 0
            for species in species_list[-1]:
                if species != 0:
                    num_species += 1

            index = 0
            for i in range(num_species):
                for _ in range(species_list[-1][i]):
                    pygame.draw.circle(
                        self.win, colours[i], self.pixel_coords[index], 10
                    )
                    index += 1

            text_surface = self.my_font.render(
                "Number of species:" + str(num_species), True, (255, 255, 255)
            )
            self.win.blit(text_surface, (1400, 540 + text_rect.height))

        text_surface = self.my_font.render(str(timer), False, (255, 0, 0))
        self.win.blit(text_surface, (1200, 850))

        pygame.display.update()

    def eval_genomes(self, genomes, config):

        nets = []
        cars = []
        self.best_fitness = float("-inf")

        i = 0
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            if self.drift_car:
                car = DriftCar(
                    self.car_speed,
                    6,
                    self.start,
                    self.car_img,
                    self.track,
                    self.best_car_img,
                )
            else:
                car = NormalCar(
                    self.car_speed,
                    6,
                    self.start,
                    self.car_img,
                    self.track,
                    self.best_car_img,
                )

            cars.append(car)
            self.nns[i] = NN(config, genome, (1500, 130))
            genome.fitness = 0
            i += 1

        self.CURRENT_GENERATION += 1

        run = True
        timer = 0

        while run:
            self.clock.tick(60)
            no_speed = 0
            alive_counter = 0  # how many cars are alive
            # apply intputs for car and feed that into NN
            for i, car in enumerate(cars):
                inputs = self.get_inputs_for_network(car)
                outputs = nets[i].activate(inputs)
                output = outputs.index(max(outputs))

                self.apply_output_to_car(car, output)

                for node in self.nns[i].nodes:
                    node.inputs = inputs
                    node.output = output

                if car.is_alive():
                    if car.vel == 0 and not self.drift_car:
                        no_speed += 1
                    alive_counter += 1
                    car.update()
                    genomes[i][1].fitness += car.get_reward()
                    if genomes[i][1].fitness > self.best_fitness:
                        self.best_fitness = genomes[i][1].fitness
                        self.best_nn = self.nns[i]
                        self.best_index = i

            timer += 1

            if timer > 1 and alive_counter == no_speed:
                run = False

            if alive_counter == 0:
                run = False

            if timer > 1000:
                run = False

            self.draw(cars, timer)

            if self.exit_button.draw(self.win):
                run = False
                self.exited = True
                raise neat.CompleteExtinctionException("User terminated training")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        run = False

            pygame.display.update()
