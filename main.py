import pygame, sys, spritesheet, time, random, font_loader, noise, math # import pygame and sys

clock = pygame.time.Clock() # set up the clock

from pygame.locals import * # import pygame modules
pygame.init() # initiate pygame

pygame.display.set_caption('Ninja Legends') # set the window name

WINDOW_SIZE = (900,600) # set up window size

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate screen

display = pygame.Surface((300, 200))

BG_COLOR = (39, 39, 68)

FPS = 60

pygame.mouse.set_visible(False)

global animation_frames
animation_frames = {}

def load_animations(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey(BG_COLOR)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

animation_database = {}

animation_database['run'] = load_animations('Data/Images/PlayerAnimations/Run', [10, 10])
animation_database['idle'] = load_animations('Data/Images/PlayerAnimations/Idle', [28, 7, 28, 7])

player_action = 'idle'
player_frame = 0
player_flip = True

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

jump_sound = pygame.mixer.Sound('Data/Music/jump.wav')
jump_sound.set_volume(.075)

grass_0 = pygame.mixer.Sound('Data/Music/grass_0.wav')
grass_1 = pygame.mixer.Sound('Data/Music/grass_1.wav')
grass_0.set_volume(.15)
grass_1.set_volume(.15)
grass_sounds = [grass_0, grass_1]
grass_sound_timer = 0

pygame.mixer.music.load('Data/Music/music.wav')
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

TILE_SIZE = grass_image.get_width()
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

def show_fps():
	# shows the frame rate on the screen
	fr = str(int(clock.get_fps())) + ' FPS'
	frt = pixel_font.render(display, fr, (10, 10))
	return frt

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

def blitRotate(surf, cleanimage, pos, originPos, angle):
    image_rect = cleanimage.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    outlineSurf = pygame.transform.rotate(cleanimage, angle)
    rotated_image_rect = cleanimage.get_rect(center = rotated_image_center)
    surf.blit(cleanimage, rotated_image_rect)
    return outlineSurf, rotated_image_rect
    
def perfect_outline(img, loc, display):
    final_surf = pygame.Surface((img.get_size()))
    mask = pygame.mask.from_surface(img)
    mask_surf = mask.to_surface()
    mask_surf.set_colorkey((0,0,0))
    final_surf.blit(mask_surf,(loc[0]-1,loc[1]))
    final_surf.blit(mask_surf,(loc[0]+1,loc[1]))
    final_surf.blit(mask_surf,(loc[0],loc[1]-1))
    final_surf.blit(mask_surf,(loc[0],loc[1]+1))
    
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
  
pixel_font = font_loader.Font('Data/Images/Fonts/pixelfont.png')

bullet_velocity = 2
bullets = []

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
        self.speed = 2
        bullet_image = pygame.transform.rotate(self.bullet, angle)
        self.pos = (x + self.offset_x, y + self.offset_y)
    
    def update(self):
        self.pos = (self.pos[0] + self.dir[0]*self.speed,
                    self.pos[1] + self.dir[1]*self.speed)
        
    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center = self.pos)
        surf.blit(self.bullet, bullet_rect)

mobs = []
class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self, mobs)
        self.image = pygame.image.load()

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

spawn_x = 3000

scroll = [0, 0]
true_scroll = [spawn_x, 0]

measuring_img = pygame.image.load('Data/Images/PlayerAnimations/Idle/idle_0.png')
player_rect = pygame.Rect(spawn_x, 0, measuring_img.get_width(), measuring_img.get_height())

level = 1

outlineSurf = pygame.Surface((13, 13))
perfect_outline_2(shuriken_image, (1,1), outlineSurf)
outlineSurf.blit(shuriken_image, (1, 1))
clean_outline = outlineSurf.copy()

while True: # game loop
    if grass_sound_timer > 0:
        grass_sound_timer -= 1
    
    display.fill(BG_COLOR)

    true_scroll[0] += (player_rect.x-scroll[0]-142)/20
    true_scroll[1] += (player_rect.y-scroll[1]-92)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

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
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '2':
                display.blit(tile_index[2], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '1':
                display.blit(tile_index[1], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '3':
                display.blit(tile_index[3], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '4':
                display.blit(tile_index[4], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if tile == '5':
                display.blit(tile_index[5], (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
            if not tile == '0' and tile == '4':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        if player_rect.x > spawn_x - 100:
            player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2 
    if player_y_momentum > 3:
        player_y_momentum = 3
    if player_rect.x <= spawn_x - 100:
        pixel_font.render(display, 'You have reached the boundary', (50, 150))
    
    if player_movement[0] > 0:
        if player_movement[1] == 0: 
            player_action,player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True
    if player_movement[0] == 0:
        if player_movement[1] == 0: 
            player_action,player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] < 0:
        if player_movement[1] == 0: 
            player_action,player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    else:
        pass # will be changed when jump animation is created
        

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        player_y_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    
    player_center = [player_rect.centerx - scroll[0], player_rect.centery - scroll[1]]
    crosshair_center = [crosshair_rect.x, crosshair_rect.y]
    
    rel_x, rel_y = crosshair_center[0] - player_center[0], crosshair_center[1] - player_center[1]
    angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
    
    outlineSurf, bullet_rect = blitRotate(display, clean_outline, (player_center[0], player_center[1]), (0, 0), angle)
    
    display.blit(pygame.transform.flip(player_img, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))
    
    mouse_pos = pygame.mouse.get_pos()
    crosshair_rect.x = mouse_pos[0]/3-crosshair.get_width()/2
    crosshair_rect.y = mouse_pos[1]/3-crosshair.get_width()/2
    display.blit(crosshair, (crosshair_rect.x, crosshair_rect.y))

    for event in pygame.event.get():
        if event.type == QUIT: # check for window quit
            pygame.quit() # stop pygame
            sys.exit() # stop script
        if event.type == MOUSEBUTTONDOWN:
            bullets.append(Bullet(player_center[0], player_center[1], rel_x, rel_y, angle, clean_outline, (bullet_rect.centerx, bullet_rect.centery)))
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
        
    for bullet in bullets[:]:
        bullet.update()
        if not display.get_rect().collidepoint(bullet.pos):
            bullets.remove(bullet)
            
    for bullet in bullets:
        bullet.draw(display)

    frt = show_fps()

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update() # update display
    clock.tick(FPS)