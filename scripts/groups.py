import pygame

from settings import *

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self, hud_sprites, start_menu_sprites, pause_menu_sprites):
        super().__init__()
        self.hud_sprites = hud_sprites
        self.start_menu_sprites = start_menu_sprites
        self.pause_menu_sprites = pause_menu_sprites
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.draw_start_menu = True
        self.draw_game = False
        self.draw_pause_menu = False
        self.bg1 = pygame.image.load('images/ui/backgrounds/bg1.png')
        self.bg1 = pygame.transform.scale(self.bg1, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bg2 = pygame.surface.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.bg2.fill((0, 0, 0, 96))

    def draw(self, target_pos):
        self.offset = -target_pos + pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        if self.draw_game:
            # Group sprites by layer
            layers = {}
            for sprite in self.sprites():
                layers.setdefault(sprite._layer, []).append(sprite)

            for layer in sorted(layers.keys()):
                for sprite in sorted(layers[layer], key=lambda s: s.hitbox.bottom):
                    if sprite in self.hud_sprites:
                        self.display_surface.blit(sprite.image, sprite.rect.topleft)
                    else:
                        self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        if self.draw_start_menu:
            self.display_surface.blit(self.bg1, (0, 0))
            for sprite in self.start_menu_sprites:
                self.display_surface.blit(sprite.image, sprite.rect.topleft)

        if self.draw_pause_menu:
            self.display_surface.blit(self.bg2, (0, 0))
            for sprite in self.pause_menu_sprites:
                self.display_surface.blit(sprite.image, sprite.rect.topleft)
