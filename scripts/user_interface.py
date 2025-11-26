import pygame.sprite

from settings import *
from math import floor

class ManaBar(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.size = 1.08
        self.empty_bar = pygame.image.load(join('images', 'ui', 'mana_bar', 'empty_bar.png')).convert_alpha()
        self.bar = pygame.image.load(join('images', 'ui', 'mana_bar', 'bar.png')).convert_alpha()
        self.overlay = pygame.image.load(join('images', 'ui', 'mana_bar', 'overlay.png')).convert_alpha()
        self.empty_bar = pygame.transform.scale(self.empty_bar, (320 * WORLD_SCALE * self.size, 32 * WORLD_SCALE * self.size))
        self.bar = pygame.transform.scale(self.bar, (320 * WORLD_SCALE * self.size, 32 * WORLD_SCALE * self.size))
        self.overlay = pygame.transform.scale(self.overlay, (320 * WORLD_SCALE * self.size, 32 * WORLD_SCALE * self.size))
        self.image = pygame.Surface((320 * WORLD_SCALE * self.size, 32 * WORLD_SCALE * self.size), pygame.SRCALPHA)
        self.bar.set_alpha(224)
        self.overlay.set_alpha(224)
        self.image.set_alpha(224)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect
        self.charge = 6.0
        self.image.blits(((self.empty_bar, self.rect.topleft), (self.bar, self.rect.topleft), (self.overlay, self.rect.topleft)))

    def update(self, dt):
        bar_pos = pygame.Vector2(48 * WORLD_SCALE * self.size * (self.charge - 6.0), 0)
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.empty_bar, (0, 0))
        self.image.blit(self.bar, bar_pos)
        self.image.fill((0, 0, 0, 0), ((0, 0), (20 * WORLD_SCALE * self.size, 32 * WORLD_SCALE * self.size)))
        self.image.blit(self.overlay, (0, 0))

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.size = 1.08
        self.empty_bar = pygame.image.load(join('images', 'ui', 'health_bar', 'empty_bar.png')).convert_alpha()
        self.bar = pygame.image.load(join('images', 'ui', 'health_bar', 'bar.png')).convert_alpha()
        self.overlay = pygame.image.load(join('images', 'ui', 'health_bar', 'overlay.png')).convert_alpha()
        self.empty_bar = pygame.transform.scale(self.empty_bar, (32 * WORLD_SCALE * self.size, 192 * WORLD_SCALE * self.size))
        self.bar = pygame.transform.scale(self.bar, (32 * WORLD_SCALE * self.size, 192 * WORLD_SCALE * self.size))
        self.overlay = pygame.transform.scale(self.overlay, (32 * WORLD_SCALE * self.size, 192 * WORLD_SCALE * self.size))
        self.image = pygame.Surface((32 * WORLD_SCALE * self.size, 192 * WORLD_SCALE * self.size), pygame.SRCALPHA)
        self.bar.set_alpha(224)
        self.overlay.set_alpha(224)
        self.image.set_alpha(224)
        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.hitbox = self.rect
        self.charge = 6.0
        self.image.blits(((self.empty_bar, (0, 0)), (self.bar, (0, 0)), (self.overlay, (0, 0))))

    def heal(self, hp):
        self.charge = min(self.charge + hp, 6.0)

    def update(self, dt):
        bar_pos = pygame.Vector2(0, 26 * WORLD_SCALE * self.size * (6.0 - self.charge))
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.empty_bar, (0, 0))
        if self.charge > 0:
            self.image.blit(self.bar, bar_pos)
        self.image.fill((0, 0, 0, 0), ((0, 173 * WORLD_SCALE * self.size), (32 * WORLD_SCALE * self.size, 20 * WORLD_SCALE * self.size)))
        self.image.blit(self.overlay, (0, 0))
        if self.charge <= 0:
            self.image.blit(self.empty_bar, (0, 0))
