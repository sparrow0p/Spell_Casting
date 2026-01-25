import pygame

from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.surface.Surface((0, 0))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = pygame.Rect(pos, size)
