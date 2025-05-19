import pygame
from sensors import Sensor
import math
from pygame.math import Vector2 as vec2
from utils import scale_image
from utils import draw_rotate_car


BORDER_COLOUR = (255, 255, 255) # border colour for collision
GATE_REWARD = 1000000



class AbstractCar:
    def __init__(self, max_vel, rotation_vel, start_pos, car_image,game_map,best_car,reward_gates=None,drift_mode=False):
        self.img = car_image
        self.best_car_img = best_car
        self.game_map = game_map
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
        self.max_speed = 6
        self.forward = (0,0)
        self.direction = vec2(1, 0)  # Forward facing direction
        self.acceleration = 0.2
        self.friction = 0.97
        self.drift_factor = 0.99# Lower = less drift, 1 = more drift


        #Car flags
        self.accelerate = False # car is accelerating
        self.brake = False # car is braking
        self.drift_mode = False#drift_mode

        # Genome
        self.distance = 0
        self.time = 0
        self.alive = True
        self.reward_gates = reward_gates
        self.gates_passed = 0
        self.best_car = False

    def is_alive(self):
        return self.alive


    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel

        elif right:
            self.angle -= self.rotation_vel
    
    def update(self):
        self.collide2(self.game_map) #car and map collision
        for sensor in self.sensors:
            sensor.line_collide(self.game_map) # calculates where the line and border collides

        self.move()

    def get_reward(self):
        reward = 0
        """
        if self.reward_gates_collision():
            reward += GATE_REWARD
        
        
        """
        if self.vel < 0:
            reward -= 1000000
        reward -= self.time / 10
        reward += self.distance
       

        return reward
    
    def reward_gates_collision(self):
        car_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        

        if car_rect.clipline(self.reward_gates[self.gates_passed % 12]):
                self.gates_passed += 1

                return True
        
        
        return False

        
    #returns distances of sensors between car and collision points
    def get_distance(self):
        distances = [0,0,0,0,0]
        for i,sensor in enumerate(self.sensors):
            distances[i] = sensor.distance()
        
        return distances 

    #implemented in DriftCar and NormalCar
    def move(self):
        pass
    
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
        if self.best_car:

            draw_rotate_car(win,self.best_car_img,(self.x,self.y),self.angle) # drawing rotated car
        else:    
            draw_rotate_car(win,self.img,(self.x,self.y),self.angle) # drawing rotated car

        self.sensors[0].calculate_line(self.img,self.x,self.y,self.angle)               # 0°
        self.sensors[1].calculate_line_left_side(self.img,self.x,self.y,self.angle)     # 90°
        self.sensors[2].calculate_line_right_side(self.img,self.x,self.y,self.angle)    # -90°
        self.sensors[3].calculate_line_left_top(self.x,self.y,self.angle)               # 30°
        self.sensors[4].calculate_line_right_top(self.x,self.y,self.angle)              # -30°
        
        for sensor in self.sensors:
            sensor.draw_line(win)
        

        
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






class NormalCar(AbstractCar):

    def move(self):
        
        if self.accelerate:
            self.vel = min(self.vel + self.acceleration, self.max_vel)
        elif self.brake:
            self.vel = max(self.vel - self.acceleration, -self.max_vel)
        else:
            self.vel *= 0.98


        #self.vel *= self.friction
        self.distance += self.vel
        self.time += 1
        
        forward = vec2(1, 0).rotate(-self.angle)
        
        self.position += self.vel * forward
        self.x, self.y = self.position.x, self.position.y


class DriftCar(AbstractCar):

    def get_reward(self):
        reward = 0
        """
        if self.reward_gates_collision():
            reward += GATE_REWARD
        
        
        """
        if self.velocity.dot(self.forward) < 0:
            speed = -300000
        else:
            speed = self.velocity.dot(self.forward) * 5
        time = -self.time / 10
        distance = self.distance

        reward = speed + time + distance

        #print(f"Speed,time,distance {speed, time, distance}")
       

        return reward
    
    def move(self):
        # computing where the car is facing (-angle because pygame and me are treating angles differently)
        forward = vec2(1, 0).rotate(-self.angle)
        self.forward = forward

        # apply accelerate/brake, depending on the input from user
        if self.accelerate:
            self.velocity += forward * self.acceleration #
        if self.brake:
            self.velocity -= forward * self.acceleration/2
        if self.velocity.length() > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

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
        self.distance += self.velocity.length()
        self.time += 1
        
