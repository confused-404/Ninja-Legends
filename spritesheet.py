import pygame
import json

class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()



    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0,0,0))
        sprite.set_colorkey((255,255,255))
        sprite.blit(self.sprite_sheet,(0, 0),(x, y, w, h))
        return sprite