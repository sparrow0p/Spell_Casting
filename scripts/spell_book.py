import pygame

from settings import *

class ShootingStar(pygame.sprite.Sprite):
    def __init__(self, pos, dir, groups, player):
        super().__init__(groups)
        self.player = player
        self.dir = dir.normalize()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.pos = self.rect.center
        self.speed = 2000
        self.min_speed = 200
        self.decel = 35
        self.fly_timer = 0.5
        self.explosion_timer = 0.1

    def move(self, dt):
        if self.fly_timer > 0:
            self.pos += self.dir * self.speed * dt

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center

        if self.speed > self.min_speed:
            self.speed -= self.decel
            if self.speed < self.min_speed:
                self.speed = self.min_speed

    def update_timer(self, dt):
        if self.fly_timer > 0:
            self.fly_timer -= dt
        elif self.explosion_timer > 0:
            self.explosion_timer -= dt
        else:
            self.kill()

    def animate(self):
        if self.fly_timer > 0:
            pygame.Surface.fill(self.image, (0, 0, 255))

    def update(self, dt):
        self.move(dt)
        self.animate()
        self.update_timer(dt)
