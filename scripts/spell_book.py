import pygame

from settings import *

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
        self.speed = 2500
        self.min_speed = 150
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
        radius = 150
        explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surface, (255, 0, 0, 90), (radius, radius), radius)

        self.image = explosion_surface
        self.rect = self.image.get_rect(center=self.rect.center)
        self.hitbox = self.rect

    def collision(self):
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

class FastWindEffect(pygame.sprite.Sprite):
    def __init__(self, pos, follow_strength, player, groups):
        super().__init__(groups)
        self.follow_strength = follow_strength
        self.player = player
        self.animate()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2()
        self.image_timer_max = 0.2 + follow_strength / 100
        self.image_timer = self.image_timer_max

    def move(self, dt):
        self.vel = self.vel.lerp(self.player.rect.center - self.pos + pygame.Vector2(0, -1), 1)
        self.pos += self.vel * self.follow_strength * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox = self.rect

    def animate(self):
        image = self.player.image
        mask = pygame.mask.from_surface(image)
        outline = mask.outline()
        mask_surf = mask.to_surface()
        mask_surf.set_colorkey((0, 0, 0))
        for point in outline:
            mask_surf.set_at(point, (0, 0, 1))
        mask_surf.set_alpha(90)

        self.image = mask_surf

    def update(self, dt):
        self.move(dt)
        if self.image_timer > 0:
            self.image_timer -= dt
        else:
            self.animate()
            self.image_timer = self.image_timer_max
