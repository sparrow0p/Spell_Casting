from settings import *

class Plant(pygame.sprite.Sprite):
    def __init__(self, groups, t_obj):
        super().__init__(groups)
        self.groups = groups
        self.t_obj = t_obj
        self.image = pygame.image.load(join('images', 'decals', 'plants', f'{self.t_obj.name}.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (WORLD_SCALE * self.image.get_width(), WORLD_SCALE * self.image.get_height()))
        self.rect = self.image.get_rect(topleft=(WORLD_SCALE * self.t_obj.x, WORLD_SCALE * self.t_obj.y))
        self.hitbox = pygame.rect.Rect(0, 0, WORLD_SCALE * self.t_obj.h_width, WORLD_SCALE * self.t_obj.h_height)
        self.hitbox.bottom = self.rect.bottom - WORLD_SCALE * self.t_obj.h_offset
        self.hitbox.centerx = self.rect.centerx
        shadow = Shadow(self.groups[0], self.t_obj)
        shadow._layer = 3

class Shadow(pygame.sprite.Sprite):
    def __init__(self, groups, t_obj):
        super().__init__(groups)
        self.t_obj = t_obj
        self.image = pygame.image.load(join('images', 'decals', 'shadows', f'{self.t_obj.name}.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (WORLD_SCALE * self.image.get_width(), WORLD_SCALE * self.image.get_height()))
        self.rect = self.image.get_rect(topleft=(WORLD_SCALE * self.t_obj.x, WORLD_SCALE * self.t_obj.y))
        self.hitbox = self.rect
