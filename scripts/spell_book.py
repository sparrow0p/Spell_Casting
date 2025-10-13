import pygame_particles

from settings import *
from pygame_particles import examples

class ShootingStar(pygame.sprite.Sprite):
    def __init__(self, pos, dir, groups, enemy_sprites, player, collision_sprites):
        super().__init__(groups)
        self.enemy_sprites = enemy_sprites
        self.player = player
        self.dir = dir.normalize()
        self.state, self.frame_index = 'fly', 0
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.collision_sprites = collision_sprites
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

    def explosion(self):
        sprite = self.collision()
        if isinstance(sprite, pygame.sprite.Sprite):
            sprite.kill()

    def animate(self):
        if self.fly_timer > 0:
            pygame.Surface.fill(self.image, (0, 0, 255))

    def update_timer(self, dt):
        if self.fly_timer > 0:
            self.fly_timer -= dt
        elif self.explosion_timer > 0:
            self.explosion_timer -= dt
        else:
            self.kill()

    def change_state(self):
        match self.state:
            case 'fly':
                if self.fly_timer < 0 or self.collision():
                    self.fly_timer = 0
                    self.state = 'explode'
                    self.set_explosion_image()
            case 'explode':
                pass

    def set_explosion_image(self):
        radius = 200
        explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surface, (255, 0, 0, 90), (radius, radius), radius)

        self.image = explosion_surface
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox = self.rect

    def collision(self):
        # collided_sprites = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        for sprite in self.enemy_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                return sprite

        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                return True

    def update(self, dt):
        self.move(dt)
        if self.state == 'explode':
            self.explosion()
        self.animate()
        self.update_timer(dt)
        self.change_state()
