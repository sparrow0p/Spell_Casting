import pygame

from settings import *

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
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
                # if sprite.__class__.__name__ == "FireParticle":
                #     self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset, special_flags=pygame.BLEND_ADD)
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
