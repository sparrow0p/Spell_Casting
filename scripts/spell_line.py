import pygame

from settings import *

class SpellLine(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, dir):
        super().__init__(groups)
        self.dir = dir
        self.player = player
        self.length = self.player.dash_speed * self.player.dash_timer_max
        self.frames = {}
        self.load_images()
        self.frame_index = 0
        self.image = pygame.image.load(join('images', 'effects', 'draw_effect', '0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.length, self.length))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.pos = self.rect.center
        self.pos = self.set_pos()
        self.rect.center = self.pos

    def load_images(self):
        for folder_path, _, file_names in walk(join('images', 'effects', 'draw_effect')):
            self.frames = []
            for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                full_path = join(folder_path, file_name)
                surf = pygame.image.load(full_path).convert_alpha()
                if self.dir % 2 == 0:
                    surf = pygame.transform.scale(surf, (self.length, self.length))
                else:
                    surf = pygame.transform.scale(surf, (self.length * math.sqrt(2), self.length))
                surf = pygame.transform.rotate(surf, -self.dir * 45)
                # surf.fill((0, 0, 255))
                self.frames.append(surf)

    def set_pos(self):
        match self.dir:
            case 0:
                return self.pos + pygame.Vector2(self.length / 2, 0)
            case 1:
                return self.pos + pygame.Vector2(self.length / 8, self.length / 8)
            case 2:
                return self.pos + pygame.Vector2(0, self.length / 2)
            case 3:
                return self.pos + pygame.Vector2(-self.length * 7/8, self.length / 8)
            case 4:
                return self.pos + pygame.Vector2(-self.length / 2, 0)
            case 5:
                return self.pos + pygame.Vector2(-self.length * 7/8, -self.length * 7/8)
            case 6:
                return self.pos + pygame.Vector2(0, -self.length / 2)
            case 7:
                return self.pos + pygame.Vector2(self.length / 8, -self.length * 7/8)

    def animate(self, dt):
        self.frame_index += 12 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        self.animate(dt)
