import pygame, sys, spritesheet, time, random, font_loader, noise, math # import pygame and sys

import Data.engine as e

clock = pygame.time.Clock() # set up the clock

from pygame.locals import * # import pygame modules
pygame.init() # initiate pygame

pygame.display.set_caption('Ninja Legends') # set the window name

WINDOW_SIZE = (900,600) # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate screen

display = pygame.Surface((300, 200))

BG_COLOR = (39, 39, 68)
e.set_global_colorkey(BG_COLOR)

FPS = 60

pygame.mouse.set_visible(False)

e.load_animations('Data/Images/Animations/')

tileset = spritesheet.Spritesheet('data/images/Tiles/tileset.png')
grass_image = pygame.transform.scale(tileset.get_sprite(0, 0, 16, 16), (16,16))
dirt_image = pygame.transform.scale(tileset.get_sprite(16, 0, 16, 16), (16,16))
bg_image = tileset.get_sprite(32, 0, 16, 16)
left_grass_image = tileset.get_sprite(48, 0, 16, 16).convert()
left_grass_image.set_colorkey((255, 255, 255))
right_grass_image = pygame.transform.flip(left_grass_image, True, False)
plant = spritesheet.Spritesheet('data/images/Tiles/plant.png')
plant_image = plant.get_sprite(0,0,16,16).convert()
plant_image.set_colorkey((BG_COLOR))
crosshair = pygame.image.load('Data/Images/Graphics/crosshair.png').convert()
crosshair_rect = pygame.Rect(0, 0, crosshair.get_width(), crosshair.get_height())
crosshair.set_colorkey((0, 0, 0))
shuriken_image = pygame.image.load('Data/Images/Weapons/shuriken.png').convert_alpha()

pygame.mixer.pre_init(44100, -16, 2, 5)

jump_sound = pygame.mixer.Sound('Data/Audio/jump.wav')
jump_sound.set_volume(.075)

grass_0 = pygame.mixer.Sound('Data/Audio/grass_0.wav')
grass_1 = pygame.mixer.Sound('Data/Audio/grass_1.wav')
grass_0.set_volume(.15)
grass_1.set_volume(.15)
grass_sounds = [grass_0, grass_1]
grass_sound_timer = 0

pygame.mixer.music.load('Data/Audio/music.wav')
pygame.mixer.music.play(-1)
muted = False

tile_index = {1:grass_image,
              2:dirt_image,
              0:bg_image,
              3:left_grass_image,
              4:right_grass_image,
              5:plant_image
              }

game_map = {}

TILE_SIZE = tile_index[1].get_width()
CHUNK_SIZE = 8

def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            height = int(noise.pnoise1(target_x * 0.1, repeat=9999999) * 4)
            if target_y >= 9 - height:
                tile_type = 2 # dirt
            elif target_y == 8 - height:
                tile_type = 1 # grass
            elif target_y == 8 - height - 1:
                if random.randint(1,3) == 1:
                    tile_type = 5 # plant
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data                   

def blitRotate(surf, cleanimage, pos, originPos, angle):
    image_rect = cleanimage.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    outlineSurf = pygame.transform.rotate(cleanimage, angle)
    rotated_image_rect = cleanimage.get_rect(center = rotated_image_center)
    surf.blit(cleanimage, rotated_image_rect)
    return outlineSurf, rotated_image_rect
    
def perfect_outline_2(img, loc, display):
    mask = pygame.mask.from_surface(img)
    mask_outline = mask.outline()
    mask_surf = pygame.Surface(img.get_size())
    for pixel in mask_outline:
        mask_surf.set_at(pixel,(255,255,255))
    mask_surf.set_colorkey((0,0,0))
    display.blit(mask_surf,(loc[0]-1,loc[1]))
    display.blit(mask_surf,(loc[0]+1,loc[1]))
    display.blit(mask_surf,(loc[0],loc[1]-1))
    display.blit(mask_surf,(loc[0],loc[1]+1))
    display.set_colorkey((0,0,0))
    
def show_fps():
	# shows the frame rate on the screen
	fr = str(int(clock.get_fps())) + ' FPS'
	frt = pixel_font.render(display, fr, (10, 10))
	return frt
  
pixel_font = font_loader.Font('Data/Images/Fonts/pixelfont.png')

bullets = []
shooting = False

class Bullet:
    def __init__(self, x, y, rel_x, rel_y, angle, bullet_image, shuriken_center):
        self.dir = (rel_x, rel_y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0]/length, self.dir[1]/length)
        
        self.bullet = bullet_image.copy()
        self.offset_x, self.offset_y = shuriken_center[0] - x, shuriken_center[1] - y
        self.offset_angle = (180 / math.pi) * -math.atan2(self.offset_y, self.offset_x)
        self.offset_length = math.hypot(*(self.offset_x, self.offset_y))
        self.offset = [self.offset_angle,
                       self.offset_length]
        self.speed = 3
        bullet_image = pygame.transform.rotate(self.bullet, angle)
        self.pos = (x + self.offset_x, y + self.offset_y)
        self.bullet_rect = self.bullet.get_rect(center = self.pos)
    
    def update(self):
        self.pos = (self.pos[0] + self.dir[0]*self.speed,
                    self.pos[1] + self.dir[1]*self.speed)
        self.bullet_rect = self.bullet.get_rect(center = self.pos)
        
    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center = self.pos)
        surf.blit(self.bullet, bullet_rect)
    def collision_test(self, rect):
        return self.bullet_rect.colliderect(rect)

def dtf(dt):
    return dt / 1000 * 60

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

spawn_x = 3000

scroll = [0, 0]
true_scroll = [spawn_x, 0]

dt = 0 # delta time
last_frame = pygame.time.get_ticks()

player = e.entity(3000, 0, 11, 15, 'player', True)
enemies = {}
for i in range(10):
    enemy_x = random.randint(3100, 4000)
    enemy = e.entity(enemy_x, 0, 11, 15, 'enemy', True)
    collisions = None
    movement = [0, 0]
    momentum = 0
    enemies['enemy' + str(i)] = [enemy, collisions, movement, momentum]
    
directions = ['left', 'right']

outlineSurf = pygame.Surface((13, 13))
perfect_outline_2(shuriken_image, (1,1), outlineSurf)
outlineSurf.blit(shuriken_image, (1, 1))
clean_outline = outlineSurf.copy()

while True: # game loop
    dt = pygame.time.get_ticks() - last_frame
    last_frame = pygame.time.get_ticks()
    if grass_sound_timer > 0:
        grass_sound_timer -= 1 + dtf(dt)
    
    display.fill(BG_COLOR)

    true_scroll[0] += (player.x-scroll[0]-142)/20
    true_scroll[1] += (player.y-scroll[1]-92)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0] + dtf(dt))
    scroll[1] = int(scroll[1] + dtf(dt))

    tile_rects = []
    for y in range(4):
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
    
    for enemy in enemies:
        enemies[enemy][2] = [0, 0]
        enemy_y_momentum = enemies[enemy][3]
        direction = random.choice(directions)
        if direction == 'right':
            enemies[enemy][2][0] += 1 * dtf(dt)
        if direction == 'left':
            enemies[enemy][2][0] -= 1 * dtf(dt)
        movement = enemies[enemy][2]
        if movement[0] > 0:
            enemies[enemy][0].set_flip(True)
        if movement[0] < 0:
            enemies[enemy][0].set_flip(False)
        enemies[enemy][2][1] += enemy_y_momentum * dtf(dt)
        enemy_y_momentum += 0.2 * dtf(dt)
        if enemy_y_momentum > 3:
            enemy_y_momentum = 3
        enemies[enemy][3] = enemy_y_momentum
    
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2 * dtf(dt)
    if moving_left:
        if player.x > 2900:
            player_movement[0] -= 2 * dtf(dt)
    player_movement[1] += player_y_momentum * dtf(dt)
    player_y_momentum += 0.2 * dtf(dt)
    if player_y_momentum > 3:
        player_y_momentum = 3
    if player.x <= 2900:
        pixel_font.render(display, 'You have reached the boundary', (50, 150))
    
    if player_movement[0] > 0:
        if player_movement[1] == 0: 
            player.set_action('run')
        player.set_flip(True)
    if player_movement[0] == 0:
        if player_movement[1] == 0: 
            player.set_action('idle')
    if player_movement[0] < 0:
        if player_movement[1] == 0: 
            player.set_action('run')
        player.set_flip(False)
    else:
        pass # will be changed when jump animation is created

    collision_types = player.move(player_movement, tile_rects, display)
    for enemy in enemies:
        enemy_collision_types = enemies[enemy][0].move(enemies[enemy][2], tile_rects, display)
        enemies[enemy][1] = enemy_collision_types

    if collision_types['bottom']:
        player_y_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1 + dtf(dt)
        
    player.change_frame(1)
    for enemy in enemies:
        enemies[enemy][0].change_frame(1)
    player_center = (player.get_center()[0] - scroll[0], player.get_center()[1] - scroll[1])
    crosshair_center = [crosshair_rect.centerx, crosshair_rect.centery]
    
    rel_x, rel_y = crosshair_center[0] - player_center[0], crosshair_center[1] - player_center[1]
    angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
    
    if shooting == False:
        outlineSurf, bullet_rect = blitRotate(display, clean_outline, (player_center[0], player_center[1]), (0, 0), angle)
    
    mouse_pos = pygame.mouse.get_pos()
    crosshair_rect.x = mouse_pos[0]/3-crosshair.get_width()/2
    crosshair_rect.y = mouse_pos[1]/3-crosshair.get_width()/2
    display.blit(crosshair, (crosshair_rect.x, crosshair_rect.y))

    player.display(display, scroll)
    for enemy in enemies:
        enemies[enemy][0].display(display, scroll)

    for event in pygame.event.get():
        if event.type == QUIT: # check for window quit
            pygame.quit() # stop pygame
            sys.exit() # stop script
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if shooting == False:
                    bullets.append(Bullet(player_center[0], player_center[1], rel_x, rel_y, angle, clean_outline, (bullet_rect.centerx, bullet_rect.centery)))
                    shooting = True
        if event.type == KEYDOWN:
            if event.key == K_RIGHT or event.key == K_d:
                moving_right = True
            if event.key == K_LEFT or event.key == K_a:
                moving_left = True
            if event.key == K_UP or event.key == K_w or event.key == K_SPACE:
                if air_timer < 6:
                    jump_sound.play()
                    player_y_momentum = -4
            if event.key == K_m:
                if muted == False:
                    pygame.mixer.music.fadeout(1000)
                    muted = True
                else:
                    pygame.mixer.music.play(-1)
        if event.type == KEYUP:
            if event.key == K_RIGHT or event.key == K_d:
                moving_right = False
            if event.key == K_LEFT or event.key == K_a:
                moving_left = False
        
    for bullet in bullets:
        bullet.update()
        if not display.get_rect().collidepoint(bullet.pos):
            try:
                bullets.remove(bullet)
            except:
                pass
            shooting = False
            
    for bullet in bullets:
        bullet.draw(display)

    frt = show_fps()

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update() # update display
    clock.tick(FPS)