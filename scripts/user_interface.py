import pygame.sprite

from settings import *
from components import load_audio
from math import floor

class Button(pygame.sprite.Sprite):
    def __init__(self, groups, pos, width, height, text, font='Corbel', text_size=35, text_color=pygame.color.Color(255, 255, 255), color1=pygame.color.Color(128, 128, 128), color2=pygame.color.Color(96, 96, 96)):
        super().__init__(groups)
        self.pos = pos
        self.width = width
        self.height = height
        self.text = pygame.font.SysFont(font, text_size).render(text, True, text_color)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.color1 = color1
        self.color2 = color2
        self.image = pygame.surface.Surface((self.width, self.height))
        self.image.fill(self.color1)
        self.image.blit(self.text, self.text_rect)
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect
        self.hover = False

    def on_click(self):
        pass

    def update(self, dt):
        if not self.hover and self.hitbox.collidepoint(pygame.mouse.get_pos()):
            self.hover = True
            self.image.fill(self.color2)
            self.image.blit(self.text, self.text_rect)
        elif self.hover and not self.hitbox.collidepoint(pygame.mouse.get_pos()):
            self.hover = False
            self.image.fill(self.color1)
            self.image.blit(self.text, self.text_rect)

class Slider(pygame.sprite.Sprite):
    def __init__(self, groups, pos, width, height, text, font='Corbel', text_size=35, start_value=1.0, text_color=pygame.color.Color(255, 255, 255), color1=pygame.color.Color(128, 128, 128), color2=pygame.color.Color(96, 96, 96), knob_color=pygame.color.Color(112, 80, 128)):
        super().__init__(groups)
        self.pos = pos
        self.height = height
        self.radius = height / 2
        self.width = width - self.radius * 2
        self.text = pygame.font.SysFont(font, text_size).render(text, True, text_color)
        self.text_rect = self.text.get_rect(center=(self.width/2 + self.radius, self.height/2))
        self.color1 = color1
        self.color2 = color2
        self.knob_color = knob_color
        self.image = pygame.surface.Surface((self.width + self.radius * 2, self.height))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect
        self.value = start_value
        self.dragging = False

        self.animate()

    def animate(self):
        self.image.fill((0, 0, 0))
        knob_pos = self.value * self.width + self.radius
        pygame.draw.circle(self.image, self.color1, (self.radius, self.radius), self.radius)
        pygame.draw.rect(self.image, self.color1, (self.radius, 0, knob_pos - self.radius, self.height))
        pygame.draw.rect(self.image, self.color2, (knob_pos, 0, self.width - knob_pos + self.radius, self.height))
        pygame.draw.circle(self.image, self.color2, (self.width + self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, self.knob_color, (knob_pos, self.radius), self.radius)
        self.image.blit(self.text, self.text_rect)

    def on_click(self):
        self.dragging = True

    def on_move(self):
        if self.dragging:
            new_x = max(self.radius, min(pygame.mouse.get_pos()[0] - self.rect.x, self.width + self.radius))
            self.value = (new_x - self.radius) / self.width
            self.animate()

    def on_release(self):
        self.dragging = False

    def update(self, dt):
        pass

class StartButton(Button):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=60,
            text="Start"
        )
        self.game = game

    def on_click(self):
        self.game.load_game()
        self.game.all_sprites.draw_start_menu = False
        self.game.all_sprites.draw_game = True
        self.game.update_game = True
        pygame.mixer_music.fadeout(1000)
        pygame.mixer_music.load('audio/music/mus_lvl2_intro_loop.ogg')
        pygame.mixer_music.play(loops=-1)

class ResumeButton(Button):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=60,
            text="Resume"
        )
        self.game = game

    def on_click(self):
        self.game.all_sprites.draw_pause_menu = False
        self.game.update_game = True

class MainMenuButton(Button):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=60,
            text="Settings"
        )
        self.game = game

class ExitButton(Button):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=60,
            text="Exit"
        )
        self.game = game

    def on_click(self):
        self.game.running = False

class MusicSlider(Slider):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=40,
            text="Music",
            start_value=music_v
        )
        self.game = game

    def on_move(self):
        super().on_move()
        pygame.mixer.music.set_volume(self.value)

class SFXSlider(Slider):
    def __init__(self, groups, game, pos):
        super().__init__(
            groups=groups,
            pos=pos,
            width=200,
            height=40,
            text="SFX",
            start_value=sfx_v
        )
        self.game = game

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
