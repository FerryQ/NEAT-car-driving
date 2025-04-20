import pygame
import time
import math
from utils import scale_image, draw_rotate_car,rotate_car

pygame.init()
WIDTH, HEIGHT = (900,800)
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #display proportions
pygame.display.set_caption("CAR GAME!")

#TEXT
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)



CAR = scale_image(pygame.image.load("images/car2.png").convert_alpha(), 0.3)
TRACK = pygame.image.load("images/track2.png").convert_alpha()
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK,threshold=240)
#TRACK_INNER = pygame.image.load("images/track3_inner.png").convert_alpha()



START = (WIDTH//2, 500)
FPS = 60

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
    
    def distance(self, col_point):
        start_x, start_y = self.start
        end_x, end_y = col_point

        dx = end_x - start_x 
        dy = end_y - start_y 

        return (math.hypot(dx,dy))
    
    def line_collide(self,mask,x_mask=0,y_mask=0):
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
            offset_x = x - x_mask
            offset_y = y - y_mask

            # Make sure we're not out of bounds
            if 0 <= offset_x < mask.get_size()[0] and 0 <= offset_y < mask.get_size()[1]:
                if mask.get_at((offset_x, offset_y)):
                    return (x,y)  # Collision detected

        return None  # No collision
    def draw_line(self,win):
        pygame.draw.line(win, (0, 255, 255), (self.start), (self.end), 2)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.sensor1 = Sensor() 
    
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        
        elif right:
            self.angle -= self.rotation_vel
    
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration,self.max_vel)
        self.move()

    def move_backwards(self):
        self.vel = max(self.vel - self.acceleration,-self.max_vel/2)
        self.move()

    def move(self):
        if self.vel >= 0:
            radians = math.radians(self.angle)
            self.x += self.vel * math.cos(radians)
            self.y -= self.vel * math.sin(radians)
        else:
            radians = math.radians(self.angle-180)
            self.x += -self.vel * math.cos(radians)
            self.y -= -self.vel * math.sin(radians)

    def draw(self, win):
        self.sensor1.calculate_line(self.img,self.x,self.y,self.angle)
        draw_rotate_car(win,self.img,(self.x,self.y),self.angle)
        self.sensor1.draw_line(win)
        

    
    
    
    

    def collide(self,mask,x=0,y=0):
        #rotating the image
        rotated_image = rotate_car(self.img,(self.x,self.y),self.angle)
        #mask from rotated image
        car_mask = pygame.mask.from_surface(rotated_image)

        orig_rect   = self.img.get_rect(topleft=(self.x, self.y))
        rotated_rect = rotated_image.get_rect(center=orig_rect.center)
        # 4) Compute offset relative to the track mask’s origin
        offset_x = int(rotated_rect.left - x)
        offset_y = int(rotated_rect.top  - y)

        # 5) Finally, test for overlap
        poi = mask.overlap(car_mask, (offset_x, offset_y))
        return poi
    
    def draw_car_border(self):
        rect = self.img.get_rect(topleft=(self.x, self.y))
        pygame.draw.rect(WIN, (255, 0, 0), rect, 2)
    
    

    def reduce_speed(self):
        if self.vel >= 0:
            self.vel = max(0, self.vel - self.acceleration/2)
        else:
            self.vel = min(0, self.vel + self.acceleration/2)
        self.move()



class PlayerCar(AbstractCar):
    IMG = CAR
    START_POS = START

    def bounce(self):
        self.vel = -self.vel
        self.move()



def draw(win, player_car):
    player_car.draw(win)
    
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        player_car.move_forward()
        moved = True
    if keys[pygame.K_s]:
        player_car.move_backwards()
        moved = True

    
    if not moved:
        player_car.reduce_speed()



run =  True
clock = pygame.time.Clock()
CAR_SPEED = 7
player_car = PlayerCar(CAR_SPEED,4)

WIN.fill((200, 200, 200))

while run:
    clock.tick(FPS) #speed of rendering

    WIN.fill((120, 120, 120))
    WIN.blit(TRACK,(0,0))



    draw(WIN, player_car)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    

    move_player(player_car)
    collision_point = player_car.collide(TRACK_BORDER_MASK)
    if collision_point:
        pygame.draw.circle(WIN, (255, 0, 0), collision_point, 5)
        player_car.bounce()
        pygame.display.update()


    collision_point_line = player_car.sensor1.line_collide(TRACK_BORDER_MASK)

    if collision_point_line:
        pygame.draw.circle(WIN, (255, 0, 0), collision_point_line, 5)
        text_surface = my_font.render(str(player_car.sensor1.distance(collision_point_line)), False, (0, 200, 0))
        WIN.blit(text_surface,(0,0))
        pygame.display.update()




pygame.quit()
