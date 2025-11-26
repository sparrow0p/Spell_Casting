import pygame

from settings import *

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self, ui_sprites):
        super().__init__()
        self.ui_sprites = ui_sprites
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset = -target_pos + pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        # Group sprites by layer
        layers = {}
        for sprite in self.sprites():
            layers.setdefault(sprite._layer, []).append(sprite)

        for layer in sorted(layers.keys()):
            for sprite in sorted(layers[layer], key=lambda s: s.hitbox.bottom):
                if sprite in self.ui_sprites:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft)
                else:
                    self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
