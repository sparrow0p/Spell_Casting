import pygame.sprite

from settings import *
from random import random, uniform

class ParticleEmitter(pygame.sprite.Sprite):
    def __init__(self, groups, pos, dir, particle, cooldown_timer_max=0.1, amount=1, one_shot=False):
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

    def update(self, dt):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
        else:
            for i in range(self.amount):
                particle = self.particle(self.groups, self.pos, self.dir)
                particle._layer = 13
            self.cooldown_timer = self.cooldown_timer_max

class BaseParticle(pygame.sprite.Sprite):
    def __init__(self, groups, pos: pygame.Vector2, life_timer=2.0, fade_timer=1.0, image=pygame.Surface((0, 0)),
                 size=(10.0, 10.0), dir=pygame.Vector2(), dir_angle_range=0.0, start_speed_range=(0.0, 0.0),
                 end_speed_range=(0.0, 0.0), accel_range=(0.0, 0.0), start_rot_range=(0.0, 0.0),
                 start_rot_speed_range=(0.0, 0.0), end_rot_speed_range=(0.0, 0.0), rot_accel_range=(0.0, 0.0)):
        super().__init__(groups)
        self.pos = pos
        self.life_timer = life_timer
        self.fade_timer = fade_timer
        self.image = image
        self.image = pygame.transform.scale(self.image, size)
        self.dir = dir.rotate((2 * random() - 1) * dir_angle_range)
        self.speed = uniform(start_speed_range[0], start_speed_range[1])
        self.end_speed = uniform(end_speed_range[0], end_speed_range[1])
        self.accel = uniform(accel_range[0], accel_range[1])
        self.image = pygame.transform.rotate(self.image, uniform(start_rot_range[0], start_rot_range[1]))
        self.rot_speed = uniform(start_rot_speed_range[0], start_rot_speed_range[1])
        self.end_rot_speed = uniform(end_rot_speed_range[0], end_rot_speed_range[1])
        self.rot_accel = uniform(rot_accel_range[0], rot_accel_range[1])
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect
        self.vel = self.dir * self.speed

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

        self.move(dt)

        if self.fade_timer > self.life_timer:
            self.image.set_alpha(int(100 * self.life_timer / self.fade_timer))

class DashParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        size = 15
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        super().__init__(
            groups,
            pos,
            life_timer=0.5,
            fade_timer=0.1,
            image=self.make_regular_polygon(5, uniform(0, math.pi * 2), size / 2, surf, (96, 0, 96)),
            size=(size, size),
            dir=dir,
            dir_angle_range=30,
            start_speed_range=(500, 600),
            end_speed_range=(100, 120),
            accel_range=(10, 15),
            start_rot_range=(0, 360),
            start_rot_speed_range=(0, 0),
            end_rot_speed_range=(0, 0),
            rot_accel_range=(0, 0)
        )

    def make_regular_polygon(self, side_num, angle, radius, surf, color):
        points = []
        for i in range(side_num):
            x = radius + radius * math.cos(math.pi * 2 * i / side_num + angle)
            y = radius + radius * math.sin(math.pi * 2 * i / side_num + angle)
            points.append([int(x), int(y)])
        pygame.draw.polygon(surf, color, points)
        return surf
