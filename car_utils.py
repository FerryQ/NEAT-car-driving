import pygame

def car_collision(win,car,TRACK_BORDER_MASK):
    collision_point = car.collide2(TRACK_BORDER_MASK)
    if collision_point:
        pygame.draw.circle(win, (255, 0, 0), collision_point, 5)
        car.bounce()


def line_collision(win,car,my_font,game_map):
    for i,sensor in enumerate(car.sensors):
        sensor.line_collide(game_map) # calculates where the line and border collides
        pygame.draw.circle(win, (255, 0, 0), sensor.collision_vec, 5) #draws a red dot as a point of collision
        text_surface = my_font.render(str(sensor.distance()), False, (0, 200, 0)) #generates 
        win.blit(text_surface, (0, 25 * i))



# Playeer movement
def move_player(player_car):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)

    
    if keys[pygame.K_w]:
        player_car.start_accel()
    elif keys[pygame.K_s]:
        player_car.start_brake()
    else:
        player_car.release_pedals()
    
    player_car.move()
    

    
