import pygame

def car_collision(win,car,TRACK_BORDER_MASK):
    collision_point = car.collide2(TRACK_BORDER_MASK)
    if collision_point:
        pygame.draw.circle(win, (255, 0, 0), collision_point, 5)
        car.bounce()

def sensors_collide(car,game_map):
    collision_points_line = []
    for i,sensor in enumerate(car.sensors):
        point = sensor.line_collide(game_map) 
        if point:
            collision_points_line.append((i,point))
    
    return collision_points_line

def line_collision(win,car,my_font,game_map):
    collision_point_lines = sensors_collide(car,game_map)

    for point in collision_point_lines:
        pygame.draw.circle(win, (255, 0, 0), point[1], 5)
        text_surface = my_font.render(str(car.sensors[point[0]].distance(point[1])), False, (0, 200, 0))
        win.blit(text_surface, (0, 25 * point[0]))


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
    

    
    
