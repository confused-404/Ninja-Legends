import pygame, sys, spritesheet, time, random, font_loader # import pygame and sys

clock = pygame.time.Clock() # set up the clock

from pygame.locals import * # import pygame modules
pygame.init() # initiate pygame

pygame.display.set_caption('Ninja Legends') # set the window name

WINDOW_SIZE = (600,400) # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate screen

display = pygame.Surface((300, 200))

BG_COLOR = (39, 39, 68)

FPS = 60

player_image = pygame.transform.scale(pygame.image.load('Data/Images/thumbnail_player_image.png').convert(), (18,18))
player_image.set_colorkey(BG_COLOR)

flipped_player_image = pygame.transform.flip(player_image, True, False)
flipped_player_image.set_colorkey(BG_COLOR)

current_image = player_image

spritesheet = spritesheet.Spritesheet('data/images/tileset.png')
grass_image = pygame.transform.scale(spritesheet.get_sprite(0, 0, 16, 16), (16,16))
dirt_image = pygame.transform.scale(spritesheet.get_sprite(16, 0, 16, 16), (16,16))
bg_image = spritesheet.get_sprite(32, 0, 16, 16)
left_grass_image = spritesheet.get_sprite(48, 0, 16, 16).convert()
left_grass_image.set_colorkey((255, 255, 255))
right_grass_image = pygame.transform.flip(left_grass_image, True, False)

tile_index = {1:grass_image,
              2:dirt_image,
              0:bg_image,
              3:left_grass_image,
              4:right_grass_image
              }

game_map = {}

TILE_SIZE = grass_image.get_width()
CHUNK_SIZE = 8

def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            if target_y > 10:
                tile_type = 2 # dirt
            elif target_y == 10:
                tile_type = 1 # grass
            elif target_y < 10:
                tile_type = 0
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data
                    

def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split("\n")
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types
  
pixel_font = font_loader.Font('Data/Images/pixelfont.png')

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

spawn_x = 3000

scroll = [0, 0]
true_scroll = [spawn_x, 0]

player_rect = pygame.Rect(spawn_x, 0, player_image.get_width(), player_image.get_height())

level = 1

while True: # game loop
    display.fill(BG_COLOR)

    true_scroll[0] += (player_rect.x-scroll[0]-142)/20
    true_scroll[1] += (player_rect.y-scroll[1]-92)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    tile_rects = []
    for y in range(3):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x,target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]],(tile[0][0]*16-scroll[0],tile[0][1]*16-scroll[1]))
                if tile[1] in [1,2, 3, 4] and not pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16) in tile_rects:
                    tile_rects.append(pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16))    
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '2':
                display.blit(tile_index[2], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '1':
                display.blit(tile_index[1], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '0':
                display.blit(tile_index[0], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '3':
                display.blit(tile_index[3], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '4':
                display.blit(tile_index[4], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if not tile == '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right:
        current_image = flipped_player_image
        player_movement[0] += 2
    if moving_left:
        current_image = player_image
        if player_rect.x > spawn_x - 100:
            player_movement[0] -= 2
        else:
            pass
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2 
    if player_y_momentum > 3:
        player_y_momentum = 3
    if player_rect.x <= spawn_x - 100:
        pixel_font.render(display, 'You have reached the boundary', (50, 150))

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    display.blit(current_image, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get(): # event loop
        if event.type == QUIT: # check for window quit
            pygame.quit() # stop pygame
            sys.exit() # stop script
        if event.type == KEYDOWN:
            if event.key == K_RIGHT or event.key == K_d:
                moving_right = True
            if event.key == K_LEFT or event.key == K_a:
                moving_left = True
            if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                if air_timer < 6:
                    player_y_momentum = -4
        if event.type == KEYUP:
            if event.key == K_RIGHT or event.key == K_d:
                moving_right = False
            if event.key == K_LEFT or event.key == K_a:
                moving_left = False
            

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update() # update display
    clock.tick(FPS)
