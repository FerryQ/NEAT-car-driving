import pygame
import time
import math
import random
import pygame.math
import car_utils as cu
from utils import scale_image, draw_rotate_car,rotate_car
from pygame.math import Vector2 as vec2

pygame.init()
WIDTH, HEIGHT = (1200,800)
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")


#TEXT
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)



CAR = scale_image(pygame.image.load("images/car2.png").convert_alpha(), 0.3)
CAR_SIZE_X, CAR_SIZE_Y = CAR.get_size()

TRACK = pygame.image.load("images/track1_notalpha.png").convert()
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK,threshold=240)
BORDER_COLOUR = (255, 255, 255)
#TRACK_INNER = pygame.image.load("images/track3_inner.png").convert_alpha()



START = (WIDTH//2, 500)
FPS = 60

class Particle:
    def __init__(self, pos, velocity, lifetime, size):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)
        self.lifetime = lifetime
        self.age = 0
        self.size = size

    def update(self):
        self.pos += self.velocity
        self.age += 1
        return self.age < self.lifetime

    def draw(self, win):
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        color = (128, 128, 128, alpha)  # semi-transparent gray
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.size // 2, self.size // 2), self.size // 2)
        win.blit(surface, (self.pos.x, self.pos.y))

class Sensor:
    def __init__(self,start=(0,0),end=(0,0)):
        self.start = start
        self.end = end

    def set_start(self, start):
        self.start = start
    
    def set_end(self, end):
        self.end = end
    
    def calculate_line(self, img,x,y,angle):
        length = 300
        offset_from_center = img.get_width() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = x + img.get_width() // 2
        center_y = y + img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x + offset_from_center * math.cos(math.radians(angle))
        start_y = center_y - offset_from_center * math.sin(math.radians(angle))

        # Compute the end of the line further in the same direction
        end_x = start_x + length * math.cos(math.radians(angle))
        end_y = start_y - length * math.sin(math.radians(angle))

        self.start = (start_x,start_y)
        self.end = (end_x,end_y)
    
    def calculate_line_left_side(self, img,x,y,angle):
        length = 300
        offset_from_center = img.get_height() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = x + img.get_width() // 2
        center_y = y + img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x - offset_from_center * math.sin(math.radians(angle))
        start_y = center_y - offset_from_center * math.cos(math.radians(angle))

        # Compute the end of the line further in the same direction
        end_x = start_x - length * math.sin(math.radians(angle))
        end_y = start_y - length * math.cos(math.radians(angle))

        self.start = (start_x,start_y)
        self.end = (end_x,end_y)

    def calculate_line_right_side(self, img,x,y,angle):
        length = 300
        offset_from_center = img.get_height() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = x + img.get_width() // 2
        center_y = y + img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x + offset_from_center * math.sin(math.radians(angle))
        start_y = center_y + offset_from_center * math.cos(math.radians(angle))

        # Compute the end of the line further in the same direction
        end_x = start_x + length * math.sin(math.radians(angle))
        end_y = start_y + length * math.cos(math.radians(angle))

        self.start = (start_x,start_y)
        self.end = (end_x,end_y)
    
    def calculate_line_left_top(self, img,x,y,angle):
        length = 300
        offset_from_center = img.get_height() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = x + img.get_width() // 2
        center_y = y + img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x + math.sin(math.radians(angle))
        start_y = center_y - offset_from_center * math.cos(math.radians(angle))

        # Compute the end of the line further in the same direction
        end_x = start_x + length * math.sin(math.radians(angle))
        end_y = start_y + length * math.cos(math.radians(angle))

        self.start = (start_x,start_y)
        self.end = (end_x,end_y)
    
    def distance(self, col_point):
        start_x, start_y = self.start
        end_x, end_y = col_point

        dx = end_x - start_x 
        dy = end_y - start_y 

        return (math.hypot(dx,dy))
    
    def line_collide(self,game_map,x_mask=0,y_mask=0):
        start_x, start_y = self.start

        end_x, end_y = self.end

        dx = end_x - start_x 
        dy = end_y - start_y 

        distance = int(math.hypot(dx,dy))

        for i in range(distance):

            t = i / distance
            x = int(start_x + t * dx)
            y = int(start_y + t * dy)

            # Offset relative to mask

            # Make sure we're not out of bounds
            
            if game_map.get_at((x, y)) == BORDER_COLOUR:
                return (x,y)  # Collision detected

        return None  # No collision
    def draw_line(self,win):
        pygame.draw.line(win, (0, 255, 255), (self.start), (self.end), 2)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel, start_pos, drift_mode=False):
        self.img = self.IMG
        self.width = self.IMG.get_size()[0]
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = start_pos
        self.start_pos = start_pos
        self.sensors = [Sensor(),Sensor(),Sensor(),Sensor()]
        self.particles = []

        #drifting
        self.position = vec2(self.x, self.y)
        self.velocity = vec2(0, 0)
        self.direction = vec2(1, 0)  # Forward facing direction
        self.acceleration = 0.2
        self.friction = 0.98
        self.drift_factor = 1# Lower = less drift, 1 = more drift

        self.accelerate = False
        self.brake = False

        self.drift_mode = True#drift_mode


    def emit_particles(self):
        offset_from_center = self.img.get_width() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = self.x + self.img.get_width() // 2
        center_y = self.y + self.img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x - offset_from_center * math.cos(math.radians(self.angle))
        start_y = center_y - offset_from_center * math.sin(math.radians(-self.angle))

        rear_pos = pygame.math.Vector2(start_x, start_y)

        # randomize particle drift
        drift = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        velocity = drift - self.velocity * 0.1  # slow backward drift

        particle = Particle(pos=rear_pos, velocity=velocity, lifetime=30, size=5)
        self.particles.append(particle)

        # update and clean old particles
        self.particles = [p for p in self.particles if p.update()]
    
    def draw_particles(self, win):
        for p in self.particles:
            p.draw(win)

    
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel

        elif right:
            self.angle -= self.rotation_vel

        
    
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration,self.max_vel)
        self.vel *= self.friction

        self.move()

    def move_backwards(self):
        self.vel = max(self.vel - self.acceleration,-self.max_vel/2)
        self.vel *= self.friction
        self.move()

    
    def move(self):
        # 1) Recompute “nose” direction from your angle
        forward = vec2(1, 0).rotate(-self.angle)

        # 2) Apply throttle/brake flags
        if self.accelerate:
            self.velocity += forward * self.acceleration
        if self.brake:
            self.velocity -= forward * self.acceleration/2

        # 3) Apply general friction (slows both forward & sideways)
        self.velocity *= self.friction

        # 4) Split into forward & sideways parts for drift
        forward_vel = forward * self.velocity.dot(forward)
        side_vel = self.velocity - forward_vel
        self.velocity = forward_vel + side_vel * self.drift_factor

        # 5) Update position
        self.position += self.velocity
        self.x, self.y = self.position.x, self.position.y
    
    def move2(self):
        
        if self.accelerate:
            self.vel = min(self.vel + self.acceleration, self.max_vel)
        if self.brake:
            self.vel = max(self.vel - self.acceleration, -self.max_vel)

        self.vel *= self.friction
        
        forward = vec2(1, 0).rotate(-self.angle)
        
        self.position += self.vel * forward
        self.x, self.y = self.position.x, self.position.y

    
    def start_accel(self):
        self.accelerate = True
        self.brake      = False

    def start_brake(self):
        self.brake      = True
        self.accelerate = False

    def release_pedals(self):
        self.accelerate = False
        self.brake      = False
    
    def draw(self, win):
        self.sensors[0].calculate_line(self.img,self.x,self.y,self.angle)
        self.sensors[1].calculate_line_left_side(self.img,self.x,self.y,self.angle)
        self.sensors[2].calculate_line_right_side(self.img,self.x,self.y,self.angle)
        #self.sensors[3].calculate_line_left_top(self.img,self.x,self.y,self.angle)



        draw_rotate_car(win,self.img,(self.x,self.y),self.angle)
        for sensor in self.sensors:
            sensor.draw_line(win)

        

    def collide2(self,game_map):
        for point in self.get_rotated_corners():
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOUR:
                    return (point[0], point[1])

        return None
    
    def get_rotated_corners(self):
        w, h = CAR_SIZE_X, CAR_SIZE_Y
        cx = self.x + w / 2
        cy = self.y + h / 2
        angle_rad = math.radians(-self.angle)

        # Local corner offsets from center
        dx = w / 2
        dy = h / 2
        corners = [
            (-dx, -dy), (dx, -dy), (dx, dy), (-dx, dy)
        ]

        rotated = []
        for ox, oy in corners:
            rx = ox * math.cos(angle_rad) - oy * math.sin(angle_rad)
            ry = ox * math.sin(angle_rad) + oy * math.cos(angle_rad)
            rotated.append((cx + rx, cy + ry))
        return rotated
    
    def draw_car_border(self):
        rect = self.img.get_rect(topleft=(self.x, self.y))
        pygame.draw.rect(WIN, (255, 0, 0), rect, 2)
    

    def reset(self):
        self.vel = 0
        self.angle = 0
        self.x, self.y = self.start_pos
        self.velocity = vec2(0, 0)
        self.direction = vec2(1, 0)  # Forward facing direction
        self.position = vec2(self.x, self.y)


        self.brake = False
        self.accelerate = False






class PlayerCar(AbstractCar):
    IMG = CAR

    def bounce(self):
        if self.drift_mode:
            self.velocity = -self.velocity
        
        else:
            self.vel = -self.vel

        self.move()



def place_car(pos):
    return PlayerCar(CAR_SPEED,4,pos)

def draw(win, player_car):
    player_car.draw(win)
    player_car.emit_particles()
    player_car.draw_particles(win)

    

def update(car):
    cu.move_player(car)
    cu.car_collision(WIN,car,TRACK)
    cu.line_collision(WIN,car,my_font,TRACK)

def reset_cars(car):
    for car in cars:
        car.reset()

run =  True
clock = pygame.time.Clock()
CAR_SPEED = 8
#player_car = PlayerCar(CAR_SPEED,4)

WIN.fill((200, 200, 200))
cars = []

while run:
    clock.tick(FPS) #speed of rendering

    #WIN.fill(BORDER_COLOUR)
    WIN.blit(TRACK,(0,0))


    for car in cars:
        draw(WIN, car)
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
                print("KOKOTKO")
                reset_cars(cars)

    
    pygame.display.update()

    



pygame.quit()
