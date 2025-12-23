import pygame.sprite

from settings import *
from random import random, randint, uniform

class ParticleEmitter(pygame.sprite.Sprite):
    def __init__(self, groups, pos, particle, dir=pygame.Vector2(1, 0), cooldown_timer_max=0.1, amount=1, one_shot=False):
        super().__init__(groups)
        self.groups = groups
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.pos = self.rect.center
        self.dir = dir
        self.particle = particle
        self.cooldown_timer = 0
        self.cooldown_timer_max = cooldown_timer_max
        self.amount = amount
        self.one_shot = one_shot
        self.particles = []

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        else:
            for i in range(self.amount):
                particle = self.particle(self.groups, self.pos, self.dir)
                particle._layer = self.layer
                self.particles.append(particle)
            self.cooldown_timer = self.cooldown_timer_max

        if self.one_shot:
            self.kill()

class BaseParticle(pygame.sprite.Sprite):
    def __init__(self, groups, pos: pygame.Vector2, life_timer=2.0, fade_timer=-1.0, image=pygame.Surface((0, 0), pygame.SRCALPHA),
                 size=(10.0, 10.0), start_colour_range=((0, 0, 0, 0), (0, 0, 0, 0)), end_colour_range=((0, 0, 0, 0), (0, 0, 0, 0)),
                 dir=pygame.Vector2(), dir_angle_range=0.0, start_speed_range=(0.0, 0.0), end_speed_range=(0.0, 0.0),
                 accel_range=(0.0, 0.0), start_rot_range=(0.0, 0.0), start_rot_speed_range=(0.0, 0.0),
                 end_rot_speed_range=(0.0, 0.0), rot_accel_range=(0.0, 0.0)):
        super().__init__(groups)
        self.pos = pos
        self.life_timer_max = life_timer
        self.life_timer = self.life_timer_max
        self.fade_timer = fade_timer
        self.org_image = image
        self.org_image = pygame.transform.scale(self.org_image, size)
        self.start_color = pygame.Color((0, 0, 0))
        self.start_color.hsla = self.randcolor(start_colour_range)
        self.color = self.start_color
        self.end_color = pygame.Color((0, 0, 0))
        self.end_color.hsla = self.randcolor(end_colour_range)
        self.dir = dir.rotate((2 * random() - 1) * dir_angle_range)
        self.speed = uniform(start_speed_range[0], start_speed_range[1])
        self.end_speed = uniform(end_speed_range[0], end_speed_range[1])
        self.accel = uniform(accel_range[0], accel_range[1])
        self.org_image = pygame.transform.rotate(self.org_image, uniform(start_rot_range[0], start_rot_range[1]))
        self.rot_speed = uniform(start_rot_speed_range[0], start_rot_speed_range[1])
        self.end_rot_speed = uniform(end_rot_speed_range[0], end_rot_speed_range[1])
        self.rot_accel = uniform(rot_accel_range[0], rot_accel_range[1])
        self.image = self.org_image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect
        self.vel = self.dir * self.speed

        if self.color[3] != 0:
            self.set_color(self.color)

    def randcolor(self, color_range):
        color = []
        for i in range(4):
            color.append(randint(color_range[0][i], color_range[1][i]))
        return color

    def set_color(self, color):
        self.rect = self.image.get_rect()
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(color)
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def update_color(self):
        color_rgb = []
        for i in range(4):
            color_rgb.append(sorted((self.start_color[i] + int((1 - self.life_timer / self.life_timer_max) * (self.end_color[i] - self.start_color[i])), 0, 255))[1])
        color = pygame.Color(color_rgb)
        self.rect = self.image.get_rect()
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(color)
        self.image = self.org_image.copy()
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def move(self, dt):
        self.vel = self.vel.lerp(self.dir * self.end_speed, min(self.accel * dt, 1))
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox = self.rect

    def update(self, dt):
        if self.life_timer > 0:
            self.life_timer -= dt
        else:
            self.kill()

        if self.end_color != self.color:
            self.update_color()

        self.move(dt)

        if self.fade_timer > self.life_timer:
            self.image.set_alpha(int(100 * self.life_timer / self.fade_timer))

class DashParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.size = 16
        self.image = pygame.image.load(join('images', 'effects', 'dash_particles', f'{randint(1, 15)}.png')).convert_alpha()
        self.image.set_alpha(200)
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.2,
            fade_timer=0.02,
            image=self.image,
            size=(self.size, self.size),
            start_colour_range=((0, 0, 100, 100), (0, 10, 100, 100)),
            end_colour_range=((0, 10, 100, 100), (0, 10, 100, 100)),
            dir=pygame.Vector2(0, -1),
            dir_angle_range=45,
            start_speed_range=(120, 400),
            end_speed_range=(100, 120),
            accel_range=(10, 15),
            start_rot_range=(0, 360)
        )

class ShootingStarFlyParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'effects', 'shooting_star', 'fly', '0.png')).convert_alpha()
        start_rot_range = 90 - math.atan2(dir[1], dir[0]) % (2 * math.pi) * 180 / math.pi
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.3,
            fade_timer=0.1,
            image=self.image,
            size=(16, 32),
            start_colour_range=((270, 100, 80, 100), (280, 100, 90, 100)),
            end_colour_range=((250, 100, 50, 100), (260, 100, 60, 100)),
            dir=dir,
            dir_angle_range=90,
            start_speed_range=(50, 60),
            end_speed_range=(50, 60),
            accel_range=(10, 15),
            start_rot_range=(start_rot_range, start_rot_range)
        )

class ShootingStarExplodeParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'effects', 'shooting_star', 'explode', '0.png')).convert_alpha()
        self.dir = pygame.math.Vector2(uniform(-1, 1), uniform(-1, 1)).normalize()
        randpos = random() * 128
        super().__init__(
            groups=groups,
            pos=pos + self.dir * randpos,
            life_timer=0.5 + random() * 0.3,
            fade_timer=0.3,
            image=self.image,
            size=(32 + 48 - randpos / 3, 32 + 48 - randpos / 3),
            start_colour_range=((10, 100, 50, 100), (20, 100, 60, 100)),
            end_colour_range=((20, 100, 5, 100), (20, 100, 10, 100)),
            dir=self.dir,
            start_speed_range=(40, 50),
            end_speed_range=(0, 10),
            accel_range=(3, 5),
        )

class RockWallExplosion(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'spells', 'rock_pillar_rocks', f'rock_pillar_rocks{randint(0, 5)}.png')).convert_alpha()
        self.dir = pygame.math.Vector2(uniform(-1/2, 1/2), 1).normalize()
        super().__init__(
            groups=groups,
            pos=pos + pygame.math.Vector2(uniform(-100, 100), uniform(-100, 100)),
            life_timer=0.5 + random() * 0.3,
            fade_timer=0.3,
            image=self.image,
            size=(64, 64),
            dir=self.dir,
            start_speed_range=(200, 220),
            end_speed_range=(0, 10),
            accel_range=(2, 3),
        )

class RockWallRocksStar(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'effects', 'shooting_star', 'fly', '0.png')).convert_alpha()
        start_rot_range = 90 - math.atan2(dir[1], dir[0]) % (2 * math.pi) * 180 / math.pi
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.3,
            fade_timer=0.1,
            image=self.image,
            size=(24, 48),
            start_colour_range=((270, 100, 80, 100), (280, 100, 90, 100)),
            end_colour_range=((250, 100, 50, 100), (260, 100, 60, 100)),
            dir=dir,
            dir_angle_range=90,
            start_speed_range=(50, 60),
            end_speed_range=(50, 60),
            accel_range=(10, 15),
            start_rot_range=(start_rot_range, start_rot_range)
        )

class RockWallRocksFire(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'spells', 'dragons_breath', 'dragons_breath3.png')).convert_alpha()
        start_rot_range = 90 - math.atan2(dir[1], dir[0]) % (2 * math.pi) * 180 / math.pi
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.3,
            fade_timer=0.1,
            image=self.image,
            size=(64, 64),
            start_colour_range=((270, 100, 80, 100), (280, 100, 90, 100)),
            end_colour_range=((250, 100, 50, 100), (260, 100, 60, 100)),
            dir=dir,
            dir_angle_range=90,
            start_speed_range=(50, 60),
            end_speed_range=(50, 60),
            accel_range=(10, 15),
            start_rot_range=(start_rot_range, start_rot_range)
        )

class RockWallRocksRock(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'spells', 'rock_pillar_rocks', 'rock_pillar_rocks0.png')).convert_alpha()
        start_rot_range = 90 - math.atan2(dir[1], dir[0]) % (2 * math.pi) * 180 / math.pi
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.3,
            fade_timer=0.1,
            image=self.image,
            size=(32, 32),
            dir=dir,
            dir_angle_range=90,
            start_speed_range=(50, 60),
            end_speed_range=(50, 60),
            accel_range=(10, 15),
            start_rot_range=(start_rot_range, start_rot_range)
        )

class HealingParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        self.image = pygame.image.load(join('images', 'effects', 'shooting_star', 'fly', '0.png')).convert_alpha()
        super().__init__(
            groups=groups,
            pos=pos,
            life_timer=0.5 + random() * 0.3,
            fade_timer=0.3,
            image=self.image,
            size=(16, 16),
            start_colour_range=((60, 100, 50, 100), (70, 100, 60, 100)),
            end_colour_range=((70, 100, 5, 100), (70, 100, 10, 100)),
            dir=dir,
            start_speed_range=(0, 10),
            end_speed_range=(0, 0),
            accel_range=(1, 2),
        )
