import pygame
import os
from utils import button
import neat
import sys
import numpy as np
from car_components import car_utils as cu
from scipy.spatial import ConvexHull
from simulation.simul import Simulation
from car_components.utils import scale_image, draw_rotate_car, rotate_car
from pygame.math import Vector2 as vec2
from car_components.car import NormalCar, DriftCar

# window settings and initialization
pygame.init()
WIDTH, HEIGHT = (1920, 1080)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # display proportions
pygame.display.set_caption("CAR GAME!")

# ------------------------------------CAR SETTINGS------------------------------------#
CAR = scale_image(
    pygame.image.load("images/car2.png").convert_alpha(), 0.4
)  # car image
CAR_SIZE_X, CAR_SIZE_Y = CAR.get_size()  # car size
CAR_SPEED = 6  # car speed
BEST_CAR = scale_image(
    pygame.image.load("images/best_car.png").convert_alpha(), 0.4
)  # car image

# TEXT
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
my_font = pygame.font.SysFont("Comic Sans MS", 30)
guide_font = pygame.font.SysFont("purisa", 50)


# ------------------------------------BUTTONS------------------------------------#
# images
levels_img = pygame.image.load("images/levels.png").convert_alpha()
level1_img = pygame.image.load("images/lvl1.png").convert_alpha()
level2_img = pygame.image.load("images/lvl2.png").convert_alpha()
level3_img = pygame.image.load("images/lvl3.png").convert_alpha()
myo_img = pygame.image.load("images/myo.png").convert_alpha()
procedural_img = pygame.image.load("images/track_generator.png").convert_alpha()

drift_car_img = scale_image(pygame.image.load("images/drift.png").convert_alpha(), 2)
normal_car_img = scale_image(pygame.image.load("images/normal.png").convert_alpha(), 2)
level1_track_img = scale_image(
    pygame.image.load("images/track1.png").convert_alpha(), 0.1125
)
level2_track_img = scale_image(
    pygame.image.load("images/track2.png").convert_alpha(), 0.1125
)
new_generation_img = pygame.image.load("images/NEW_GENERATION.png").convert_alpha()
load_generation_img = pygame.image.load("images/LOAD_GENERATION.png").convert_alpha()


# init buttons
levels_button = button.Button(WIDTH/2 - levels_img.get_width()/2, 700, levels_img, 1)
level1_button = button.Button(WIDTH/2 - 2*level1_img.get_width() - 40, HEIGHT/2, level1_img, 1)
level2_button = button.Button(WIDTH/2 - level2_img.get_width() + 20, HEIGHT/2, level2_img, 1)
level3_button = button.Button(750, 302, level3_img, 1)
myo_button = button.Button(WIDTH/2 + 80, HEIGHT/2, myo_img, 1)
test_button = button.Button(WIDTH/2 + procedural_img.get_width() + 140, HEIGHT/2, procedural_img, 1)
drift_car_button = button.Button(
    760 - drift_car_img.get_width() / 2, 500, drift_car_img, 1
)
normal_car_button = button.Button(
    1160 - normal_car_img.get_width() / 2, 500, normal_car_img, 1
)
new_generation_button = button.Button(
    760 - drift_car_img.get_width() / 2, 500, new_generation_img, 1
)
load_generation_button = button.Button(
    1160 - normal_car_img.get_width() / 2, 500, load_generation_img, 1
)


# ------------------------------------TRACK SETTINGS------------------------------------#
TRACK1 = pygame.image.load("images/track1.png").convert()  # Track image
TRACK2 = pygame.image.load("images/track2.png").convert()  # Track image

BORDER_COLOUR = (255, 255, 255)  # Border colour for collision

START = (WIDTH // 2, 500)  # starting position
FPS = 60


class Game_info:

    def __init__(self, started=False, levels_menu=False):
        self.started = started
        self.exited = False
        self.levels_menu = levels_menu

        self.drift_car = False
        self.normal_car = False

        self.level_one = False

        self.level_two = False

        self.level_three = False

        self.myo_level = False

        self.test_level = False

        if os.path.exists("neat-checkpoint-10"):
            print("File exists")
            self.new_generation = False  # in the beggining i want only new_generatio we don't have a loaded one
        else:
            print("File does not exist")
            self.new_generation = True  # in the beggining i want only new_generatio we don't have a loaded one

    def reset(self):
        self.started = False
        self.exited = False
        self.levels_menu = False

        self.drift_car = False
        self.normal_car = False

        self.level_one = False

        self.level_two = False

        self.level_three = False

        self.myo_level = False

        self.test_level = False

        self.new_generation = False


# Pick betweeen two modes and start simulation
def drift_normal(win, track, start_pos, new_generation,game_info):
    while not game_info.drift_car and not game_info.normal_car:
        win.fill((190, 190, 210))

        text1 = guide_font.render("PICK DRIVING MODE", True, (0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        win.blit(text1, ((WIDTH / 2) - (text1.get_width() // 2), 50))

        if drift_car_button.draw(win):
            game_info.drift_car = True
        if normal_car_button.draw(win):
            game_info.normal_car = True
        pygame.display.update()

    if game_info.drift_car:
        simulation = Simulation(
            win, 1000, track, CAR_SPEED, start_pos, CAR, BEST_CAR, True, new_generation
        )

        simulation.run_simulation()
    else:
        simulation = Simulation(
            win, 1000, track, 8, start_pos, CAR, BEST_CAR, checkpoint=new_generation
        )

        simulation.run_simulation()

    return simulation.exited

# Screen mode - pick between new generation or load existing one
def load_or_new(win,game_info):
    while not game_info.drift_car and not game_info.normal_car:
        win.fill((190, 190, 210))

        text1 = guide_font.render(
            "Start new generation or Load your previous", True, (0, 0, 0)
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        win.blit(text1, ((WIDTH / 2) - (text1.get_width() // 2), 50))

        if new_generation_button.draw(win):
            return False
        if load_generation_button.draw(win):
            return True
        pygame.display.update()

    return


# initializing car
def place_car(pos, track):
    return DriftCar(CAR_SPEED, 4, pos, CAR, track)


# car update (moving, car collision, line collision)
def update(car):
    car.update()
    cu.move_player(car)
    # cu.car_collision(WIN,car,TRACK)
    # cu.line_collision(WIN,car,my_font,TRACK)

# make gates
def make_gate(positions):
    for position in positions:
        pygame.draw.line(WIN, (0, 255, 255), (position[0]), (position[1]), 2)






def bezier(p0, p1, p2, screen):
    for t in np.arange(0, 1, 0.01):
        point = (1 - t) * ((1 - t) * p0 + t * p1) + t * ((1 - t) * p1 + t * p2)
        # point = p0 + t*(p1-p0)
        pygame.draw.circle(screen, (0, 0, 0), point.astype(int), 50)


def generate_hull():
    num_points = 20

    x_coords = np.random.randint(150, 1150, size=num_points)
    y_coords = np.random.randint(150, 920, size=num_points)

    pixel_coords = np.column_stack((x_coords, y_coords))

    conv_points = ConvexHull(pixel_coords).vertices
    num_conv_points = len(conv_points)

    return pixel_coords, conv_points, num_conv_points

def game_loop():
    run = True
    clock = pygame.time.Clock()
    # player_car = NormalCar(CAR_SPEED,4)

    cars = []

    # initializing game_info
    game_info = Game_info()

    # initializing points for procedura generation
    num_points = 56
    x_coords = np.random.randint(250, 1150, size=num_points)
    y_coords = np.random.randint(250, 920, size=num_points)

    pixel_coords = np.column_stack((x_coords, y_coords))

    conv_points = ConvexHull(pixel_coords).vertices
    num_conv_points = len(conv_points)
    while run:
        clock.tick(FPS)  # speed of rendering

        # ------------------------------------START MENU------------------------------------#
        while not game_info.started:
            WIN.fill((255, 255, 255))

            if levels_button.draw(WIN):
                game_info.levels_menu = True

            if game_info.levels_menu:
                WIN.fill((190, 190, 210))
                # action level 1 button
                WIN.blit(level1_track_img, (WIDTH/2 - 2*level1_img.get_width() - 40 , HEIGHT/2 - 1.6*level1_img.get_height()))
                if level1_button.draw(WIN):
                    game_info.started = True
                    game_info.level_one = True
                # action level 2 button
                WIN.blit(level2_track_img, (WIDTH/2 - level2_img.get_width() + 20, HEIGHT/2 - 1.6*level2_img.get_height()))
                if level2_button.draw(WIN):
                    game_info.started = True
                    game_info.level_two = True

                # action level 3 button
                if myo_button.draw(WIN):
                    game_info.started = True
                    game_info.myo_level = True
                    WIN.fill((255, 255, 255))

                if test_button.draw(WIN):
                    game_info.started = True
                    game_info.test_level = True

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

        # ------------------------------------Procedural generator LEVEL------------------------------------#
        drawing = False
        placed_car = False
        track_done = False
        start_pos = None
        PROCEDURAL_TRACK = pygame.Surface((1400, 1080))
        PROCEDURAL_TRACK.fill((255, 255, 255))
        while game_info.test_level:
            WIN.fill((255, 255, 255))
            WIN.blit(PROCEDURAL_TRACK, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:  # generates new tracks
                        PROCEDURAL_TRACK.fill((255, 255, 255))
                        pixel_coords, conv_points, num_conv_points = generate_hull()
                        while (num_conv_points % 2) != 0:
                            PROCEDURAL_TRACK.fill((255, 255, 255))
                            pixel_coords, conv_points, num_conv_points = generate_hull()

                # Place car
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    start_pos = (x, y)

            # Draw car at mouse position
            if not start_pos:
                x, y = pygame.mouse.get_pos()
                WIN.blit(CAR, (x, y))
                text1 = guide_font.render(
                    "Now pick a starting position with left click", True, (0, 0, 0)
                )
                text2 = guide_font.render(
                    "Press N to generate new track", True, (0, 0, 0)
                )

                WIN.blit(text1, ((WIDTH / 2) - (text1.get_width() // 2), 50))
                WIN.blit(text2, ((WIDTH / 2) - (text2.get_width() // 2), 60 + text1.get_height()))

            if start_pos:
                load_or_new_switch = False
                if not game_info.new_generation:
                    load_or_new_switch = load_or_new(WIN,game_info)

                game_info.exited = drift_normal(
                    WIN, PROCEDURAL_TRACK, start_pos, load_or_new_switch, game_info
                )
                if game_info.exited:
                    game_info.reset()
                else:
                    run = False

            # draws the track
            for index in range(0, num_conv_points, 2):
                bezier(
                    pixel_coords[conv_points[index % num_conv_points]],
                    pixel_coords[conv_points[(index + 1) % num_conv_points]],
                    pixel_coords[conv_points[(index + 2) % num_conv_points]],
                    PROCEDURAL_TRACK,
                )

            pygame.display.update()

        # ------------------------------------LEVEL ONE------------------------------------#
        while game_info.level_one:
            load_or_new_switch = False
            if not game_info.new_generation:
                load_or_new_switch = load_or_new(WIN,game_info)
            game_info.exited = drift_normal(
                WIN, TRACK1, (660, 895), load_or_new_switch, game_info
            )  # choose between drift or normal car
            if game_info.exited:
                game_info.reset()
            else:
                run = False

        # ------------------------------------LEVEL TWO------------------------------------#
        while game_info.level_two:
            load_or_new_switch = False
            if not game_info.new_generation:
                load_or_new_switch = load_or_new(WIN,game_info)  # new == True, load == False
            game_info.exited = drift_normal(
                WIN, TRACK2, (700, 987), load_or_new_switch, game_info
            )  # choose between drift or normal car
            if game_info.exited:
                game_info.reset()
            else:
                run = False

        # ------------------------------------LEVEL THREE------------------------------------#
        drawing = False
        placed_car = False
        track_done = False
        start_pos = None
        TRACK_DRAWN = pygame.Surface((1400, 1080))
        TRACK_DRAWN.fill((255, 255, 255))
        # level three
        while game_info.myo_level:
            clock.tick(FPS)  # speed of rendering

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

                # Place car
                if event.type == pygame.MOUSEBUTTONDOWN and track_done:
                    x, y = pygame.mouse.get_pos()
                    start_pos = (x, y)

                # Track done
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        track_done = True

            WIN.fill((255, 255, 255))
            WIN.blit(TRACK_DRAWN, (0, 0))
            # Guide Text
            if not track_done:
                text1 = guide_font.render("Draw with your mouse", True, (0, 0, 0))
                text2 = guide_font.render("if you are done press SPACEBAR", True, (0, 0, 0))

                WIN.blit(text1, ((WIDTH / 2) - (text1.get_width() // 2), 50))
                WIN.blit(
                    text2, ((WIDTH / 2) - (text2.get_width() // 2), 50 + text1.get_height())
                )

            if track_done and not start_pos:
                x, y = pygame.mouse.get_pos()
                WIN.blit(CAR, (x, y))
                text1 = guide_font.render(
                    "Now pick a starting position with left click", True, (0, 0, 0)
                )

                WIN.blit(text1, ((WIDTH / 2) - (text1.get_width() // 2), 50))

            # Draw while holding mouse
            for car in cars:
                if placed_car:
                    car.draw(WIN)
                    update(car)
            if drawing:
                x, y = pygame.mouse.get_pos()
                pygame.draw.circle(TRACK_DRAWN, (0, 0, 0), (x, y), 50)

            if start_pos:
                load_or_new_switch = False
                if not game_info.new_generation:
                    load_or_new_switch = load_or_new(WIN,game_info)
                game_info.exited = drift_normal(
                    WIN, TRACK_DRAWN, start_pos, load_or_new_switch, game_info
                )
                if game_info.exited:
                    game_info.reset()
                else:
                    run = False

            pygame.display.update()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    game_loop()  
