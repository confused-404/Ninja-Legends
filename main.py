import pygame, sys, Data.Scripts.spritesheet as spritesheet, time, random, Data.Scripts.font_loader as font_loader, noise, math, csv # import pygame and sys

import Data.engine as e

clock = pygame.time.Clock() # set up the clock

from pygame.locals import * # import pygame modules
pygame.init() # initiate pygame

pygame.display.set_caption('Ninja Legends') # set the window name

WINDOW_SIZE = (900,600) # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate screen

display = pygame.Surface((300, 200))

BG_COLOR = (39, 39, 68)
BLACK = (0, 0, 0)
e.set_global_colorkey(BG_COLOR)

FPS = 60

pygame.mouse.set_visible(False)

### IMAGE LOADING

e.load_animations('Data/Images/Animations/')

TILE_SIZE = 16

tileset = spritesheet.Spritesheet('data/images/Tiles/tileset.png')
 
top_grass = tileset.get_sprite(TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
top_grass.set_colorkey(BLACK)
left_top_grass = tileset.get_sprite(0, 0, TILE_SIZE, TILE_SIZE)
left_top_grass.set_colorkey(BLACK)
right_top_grass = tileset.get_sprite(2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
right_top_grass.set_colorkey(BLACK)
left_middle_dirt = tileset.get_sprite(0, TILE_SIZE, TILE_SIZE, TILE_SIZE)
left_middle_dirt.set_colorkey(BLACK)
center_middle_dirt = tileset.get_sprite(TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)
center_middle_dirt.set_colorkey(BLACK)
right_middle_dirt = tileset.get_sprite(2*TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)
right_middle_dirt.set_colorkey(BLACK)
left_bottom_dirt = tileset.get_sprite(0, 2*TILE_SIZE, TILE_SIZE, TILE_SIZE)
left_bottom_dirt.set_colorkey(BLACK)
center_bottom_dirt = tileset.get_sprite(TILE_SIZE, 2*TILE_SIZE, TILE_SIZE, TILE_SIZE)
center_bottom_dirt.set_colorkey(BLACK)
right_bottom_dirt = tileset.get_sprite(2*TILE_SIZE, 2*TILE_SIZE, TILE_SIZE, TILE_SIZE)
right_bottom_dirt.set_colorkey(BLACK)

left_horizontal_grass = tileset.get_sprite(0, 3*TILE_SIZE, TILE_SIZE, TILE_SIZE)
left_horizontal_grass.set_colorkey(BLACK)
center_horizontal_grass = tileset.get_sprite(TILE_SIZE, 3*TILE_SIZE, TILE_SIZE, TILE_SIZE)
center_horizontal_grass.set_colorkey(BLACK)
right_horizontal_grass = tileset.get_sprite(2*TILE_SIZE, 3*TILE_SIZE, TILE_SIZE, TILE_SIZE)
right_horizontal_grass.set_colorkey(BLACK)

top_vertical_grass = tileset.get_sprite(3*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
top_vertical_grass.set_colorkey(BLACK)
middle_vertical_grass = tileset.get_sprite(3*TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)
middle_vertical_grass.set_colorkey(BLACK)
bottom_vertical_grass = tileset.get_sprite(3*TILE_SIZE, 2*TILE_SIZE, TILE_SIZE, TILE_SIZE)
bottom_vertical_grass.set_colorkey(BLACK)

independent_grass = tileset.get_sprite(3*TILE_SIZE,3*TILE_SIZE, TILE_SIZE, TILE_SIZE)
independent_grass.set_colorkey(BLACK)

plant = tileset.get_sprite(4*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)
plant.set_colorkey(BLACK)

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

tile_index = {1:top_grass,
              0:left_top_grass,
              2:right_top_grass,
              5:left_middle_dirt,
              6:center_middle_dirt,
              7:right_middle_dirt,
              10:left_bottom_dirt,
              11:center_bottom_dirt,
              12:right_bottom_dirt,
              
              15:left_horizontal_grass,
              16:center_horizontal_grass,
              17:right_horizontal_grass,
              
              3:top_vertical_grass,
              8:middle_vertical_grass,
              13:bottom_vertical_grass,
              
              18:independent_grass,
              
              4:plant,
              
              -1:None
              }

game_maps = [[], [], []]
level = 0
with open('Data/Maps/level0_csv.csv', 'r') as f:
    csv_reader = csv.reader(f)
    for x in csv_reader:
        x = [int(n) for n in x]
        game_maps[0].append(x)

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

class Background():
      def __init__(self, image, speed):
            self.bgimage = image
            self.rectBGimg = [296, 200]
 
            self.bgX1 = 0
 
            self.bgX2 = 296
            
            self.oldscroll = [0, 0]
 
            self.moving_speed = speed
         
      def update(self, scroll, player_x, player_died):
        if player_died:
            scroll = [0, 0]
        if self.bgX1 < -self.rectBGimg[0]:
            self.bgX1 = self.rectBGimg[0]
        if self.bgX2 < -self.rectBGimg[0]:
            self.bgX2 = self.rectBGimg[0]
           
        elif self.bgX2 > self.rectBGimg[0]:
            self.bgX2 = -self.rectBGimg[0] 
        elif self.bgX1 > self.rectBGimg[0]:
            self.bgX1 = -self.rectBGimg[0] 
        
        self.bgX1 -= (scroll[0] - self.oldscroll[0]) * self.moving_speed
        self.bgX2 -= (scroll[0] - self.oldscroll[0]) * self.moving_speed
        self.oldscroll = scroll
            
             
      def render(self):
         display.blit(self.bgimage, (self.bgX1, 0))
         display.blit(self.bgimage, (self.bgX2, 0))
         
      def re_init(self):
 
            self.bgX1 = 0
 
            self.bgX2 = 296
            
            self.oldscroll = [0, 0]
 

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

spawn_x = 170

scroll = [0, 0]
true_scroll = [0, 0]

dt = 0 # delta time
last_frame = pygame.time.get_ticks()

player = e.entity(spawn_x, 0, 11, 15, 'player', True)
player_died = False
player_jump = False
player_jump2 = False
enemies = {}
for i in range(0):
    enemy_x = random.randint(3400, 6000)
    enemy = e.entity(enemy_x, 0, 11, 15, 'enemy', True)
    collisions = None
    movement = [0, 0]
    momentum = 0
    enemies['enemy' + str(i)] = [enemy, collisions, movement, momentum, 0]

outlineSurf = pygame.Surface((13, 13))
perfect_outline_2(shuriken_image, (1,1), outlineSurf)
outlineSurf.blit(shuriken_image, (1, 1))
clean_outline = outlineSurf.copy()
first_collision = False

foreground = pygame.image.load("Data/Images/Tiles/foreground.png")
middleground = pygame.image.load("Data/Images/Tiles/middleground.png")
background = pygame.image.load("Data/Images/Tiles/background.png")
background_layers = [Background(background, .5), Background(middleground, 1), Background(foreground, 2)]

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

    level_map = game_maps[level]
    
    for bg in background_layers:
        if player_died:
            bg.re_init()
            true_scroll = [0, 0]
        bg.update(scroll, player.x, player_died)
        bg.render()
        
    
    tile_rects = []
    y = 0
    for layer in level_map:
        x = 0
        for tile in layer:
            if tile != -1:
                display.blit(tile_index[tile],(x*TILE_SIZE-scroll[0],y*TILE_SIZE-scroll[1]))
            if tile != -1 and tile != 4:
                tile_rects.append(pygame.Rect(x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE))
            x += 1
        y += 1

    display_r = pygame.Rect(scroll[0], scroll[1], 300, 200)
    
    for enemy in enemies:
        if display_r.colliderect(enemies[enemy][0].obj.rect):
            if enemies[enemy][3] > 3:
                enemies[enemy][3] = 3
            enemies[enemy][2] = [0, enemies[enemy][3]]
            if player.x > enemies[enemy][0].x + 10:
                enemies[enemy][2][0] = 1
            if player.x < enemies[enemy][0].x - 10:
                enemies[enemy][2][0] = -1
            if enemies[enemy][2][0] > 0:
                enemies[enemy][0].set_action('run')
                enemies[enemy][0].set_flip(True)
            if enemies[enemy][2][0] < 0:
                enemies[enemy][0].set_action('run')
                enemies[enemy][0].set_flip(False)
            if enemies[enemy][2][0] == 0:
                enemies[enemy][0].set_action('idle')
            enemies[enemy][2][1] += enemies[enemy][3] * dtf(dt)
            enemies[enemy][3] += 0.2 * dtf(dt)
                
            enemy_collision_types = enemies[enemy][0].move(enemies[enemy][2], tile_rects, display)
            enemies[enemy][1] = enemy_collision_types
            if enemies[enemy][1]['bottom']:
                enemies[enemy][3] = 0
                enemies[enemy][4] = 0
            else:
                enemies[enemy][4] += 1 * dtf(dt)
            if enemies[enemy][1]['right'] or enemies[enemy][1]['left']:
                if enemies[enemy][4] < 6:
                    enemies[enemy][3] = -1.5
        
            enemies[enemy][0].change_frame(1)
        
    player_movement = [0, 0]
    if first_collision:
        if moving_right:
            player_movement[0] += 2 * dtf(dt)
        if moving_left:
            if player.x > spawn_x:
                player_movement[0] -= 2 * dtf(dt)
    player_movement[1] += player_y_momentum * dtf(dt)
    player_y_momentum += 0.2 * dtf(dt)
    if player_y_momentum > 3:
        player_y_momentum = 3
        if player.x <= -100:
            boundary_text = pixel_font.render(display, 'You have reached the boundary', (50, 150))
        if player.y >= 500:
            player.set_pos(spawn_x, 0)
            first_collision = False
            player_died = True
        else:
            player_died = False
        
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

    if collision_types['bottom']:
        first_collision = True
        player_y_momentum = 0
        player_jump, player_jump2 = True, True
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
        
    player.change_frame(1)
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
                
                if player_jump:
                    player_jump = False
                    jump_sound.play()
                    player_y_momentum = -4
                elif player_jump2:
                    player_jump2 = False
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
        
        for enemy in enemies:
            pygame.draw.rect(display, (0, 0, 255), enemies[enemy][0].obj.rect)
            pygame.draw.rect(display, (255, 0, 0), bullet.bullet_rect)
            if enemies[enemy][0].obj.rect.colliderect(bullet.bullet_rect):
                try:
                    bullets.remove(bullet)
                    enemies.pop(enemy)
                except:
                    pass
                shooting = False
        
        if not display.get_rect().collidepoint(bullet.pos):
            try:
                bullets.remove(bullet)
            except:
                pass
            shooting = False
            
    for bullet in bullets:
        if bullet:
            bullet.draw(display)

    frt = show_fps()

    ### Fade In/ Fade OUt:
    
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update() # update display
    clock.tick(FPS)