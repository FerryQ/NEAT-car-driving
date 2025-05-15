import pygame
import math
from pygame.math import Vector2 as vec2


BORDER_COLOUR = (255, 255, 255)


class Sensor:
    def __init__(self,img,start=(0,0),end=(0,0)):
        self.start = start
        self.end = end
        self.img_width = img.get_width()
        self.img_height = img.get_height()
        self.length = 2000
        self.collision_vec = (0,0)

    def set_start(self, start):
        self.start = start
    
    def set_end(self, end):
        self.end = end
    
    def calculate_line(self, img,x,y,angle):
        offset_from_center = img.get_width() // 2  # Distance from center to front

        # Get the center of the car (rotation point)
        center_x = x + img.get_width() // 2
        center_y = y + img.get_height() // 2

        # Compute the front (headlight) position based on the angle
        start_x = center_x
        start_y = center_y

        # Compute the end of the line further in the same direction
        end_x = start_x + self.length * math.cos(math.radians(angle))
        end_y = start_y - self.length * math.sin(math.radians(angle))

        self.start = (start_x,start_y)
        self.end = (end_x,end_y)
    
    def calculate_line_left_side(self, img,x,y,angle):

        center = vec2(x + self.img_width/2, y + self.img_height/2)

        offset = vec2(0,- self.img_height/2)

        rotated_offset = offset.rotate(-angle)

        start = center + rotated_offset

        
        direction = vec2(1,0).rotate(-angle-90)

        end = start + direction* self.length

        self.start = (start.x,start.y)
        self.end = (end.x,end.y)

    def calculate_line_right_side(self, img,x,y,angle):

        center = vec2(x + self.img_width/2, y + self.img_height/2)

        offset = vec2(0, self.img_height/2)

        rotated_offset = offset.rotate(-angle)

        start = center + rotated_offset

        
        direction = vec2(1,0).rotate(-angle+90)

        end = start + direction* self.length

        self.start = (start.x,start.y)
        self.end = (end.x,end.y)


    
    def calculate_line_left_top(self,x,y,angle):
        
        center = vec2(x + self.img_width/2, y + self.img_height/2)

        offset = vec2(self.img_width / 2, -self.img_height/2)

        rotated_offset = offset.rotate(-angle)

        start = center + rotated_offset

        
        direction = vec2(1,0).rotate(-angle-30)

        end = start + direction* self.length

        self.start = (start.x,start.y)
        self.end = (end.x,end.y)
    
    def calculate_line_right_top(self,x,y,angle):
        
        
        center = vec2(x + self.img_width/2, y + self.img_height/2)

        offset = vec2(self.img_width / 2, self.img_height/2)

        rotated_offset = offset.rotate(-angle)

        start = center + rotated_offset

        direction = vec2(1,0).rotate(-angle+30)

        end = start + direction* self.length

        self.start = (start.x,start.y)
        self.end = (end.x,end.y)

    
    def distance(self):
        start_x, start_y = self.start
        end_x, end_y = self.collision_vec

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
                self.collision_vec = (x,y)
                return (x,y)  # Collision detected

        return None  # No collision
    def draw_line(self,win):

        pygame.draw.line(win, (0, 255, 255), (self.start), (self.collision_vec), 2)
