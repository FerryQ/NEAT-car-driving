import pygame
from sensors import Sensor
import math
from pygame.math import Vector2 as vec2
from utils import scale_image
from utils import draw_rotate_car


BORDER_COLOUR = (255, 255, 255) # border colour for collision



class AbstractCar:
    def __init__(self, max_vel, rotation_vel, start_pos, car_image,drift_mode=False):
        self.img = car_image
        self.width = car_image.get_size()[0]
        self.height = car_image.get_size()[1]

        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = start_pos
        self.start_pos = start_pos
        self.sensors = [Sensor(self.img),Sensor(self.img),Sensor(self.img),Sensor(self.img),Sensor(self.img)] # 

        #drifting
        self.position = vec2(self.x, self.y)
        self.velocity = vec2(0, 0)
        self.direction = vec2(1, 0)  # Forward facing direction
        self.acceleration = 0.2
        self.friction = 0.98
        self.drift_factor = 0.98# Lower = less drift, 1 = more drift


        #Car flags
        self.accelerate = False # car is accelerating
        self.brake = False # car is braking
        self.drift_mode = False#drift_mode

        # Genome
        self.distance = 0
        self.time = 0
        self.alive = True

    def is_alive(self):
        return self.alive


    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel

        elif right:
            self.angle -= self.rotation_vel
    
    def update(self):
        self.collide2()
        self.move()


            
    def move2(self):
        # computing where the car is facing (-angle because pygame and me are treating angles differently)
        forward = vec2(1, 0).rotate(-self.angle)

        # apply accelerate/brake, depending on the input from user
        if self.accelerate:
            self.velocity += forward * self.acceleration #
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

        # update distance and time
        self.distance += self.vel
        self.time += 1
    
    #returns distances of sensors between car and collision points
    def get_distance(self):
        distances = [0,0,0,0,0]
        for i,sensor in enumerate(self.sensors):
            distances[i] = sensor.distance
        
        return distances 

    
    def move(self):
        
        if self.accelerate:
            self.vel = min(self.vel + self.acceleration, self.max_vel)
        elif self.brake:
            self.vel = max(self.vel - self.acceleration, -self.max_vel)
        else:
            self.vel = 0


        #self.vel *= self.friction
        self.distance += self.vel
        self.time += 1
        
        forward = vec2(1, 0).rotate(-self.angle)
        
        self.position += self.vel * forward
        self.x, self.y = self.position.x, self.position.y



    
    # setting mode when pressing forward (w)
    def start_accel(self):
        self.accelerate = True
        self.brake      = False

    # setting mode when pressing backwards (s)
    def start_brake(self):
        self.brake      = True
        self.accelerate = False

    # no keyboard input
    def release_pedals(self):
        self.accelerate = False
        self.brake      = False
    
    # draws sensors and rotated car
    def draw(self, win):
        self.sensors[0].calculate_line(self.img,self.x,self.y,self.angle)
        self.sensors[1].calculate_line_left_side(self.img,self.x,self.y,self.angle)
        self.sensors[2].calculate_line_right_side(self.img,self.x,self.y,self.angle)
        self.sensors[3].calculate_line_left_top(self.x,self.y,self.angle)
        self.sensors[4].calculate_line_right_top(self.x,self.y,self.angle)
        for sensor in self.sensors:
            sensor.draw_line(win)

        draw_rotate_car(win,self.img,(self.x,self.y),self.angle) # drawing rotated car

        
    # collision of car and border
    def collide2(self,game_map):
        # simple collision system checking if corner of the car overlaps the colour of the border (white) - this is faster than pixel perfect collision system with mask and etc.
        for point in self.get_rotated_corners():
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOUR:
                    self.alive = False
                    return (point[0], point[1])

        return None
    
    def get_rotated_corners(self):
        w, h = self.width, self.height
        cx = self.x + w / 2
        cy = self.y + h / 2
        center = vec2(cx,cy)

        angle_rad = math.radians(-self.angle)

        # local corner offsets from center
        dx = w / 2
        dy = h / 2
        corners = [
            vec2(-dx, -dy), vec2(dx, -dy), vec2(dx, dy), vec2(-dx, dy)
        ]
        rotated = []
        for corner in corners:
            rotated_corner = corner.rotate(-self.angle)
            rotated.append(center + rotated_corner)

        return rotated    

    def reset(self):
        self.vel = 0
        self.angle = 0
        self.x, self.y = self.start_pos
        self.velocity = vec2(0, 0)
        self.direction = vec2(1, 0)  # Forward facing direction
        self.position = vec2(self.x, self.y)


        self.brake = False
        self.accelerate = False

        self.distance = 0
        self.time = 0






class PlayerCar(AbstractCar):

    def bounce(self):
        if self.drift_mode:
            self.velocity = -self.velocity
        
        else:
            self.vel = -self.vel

        self.move()