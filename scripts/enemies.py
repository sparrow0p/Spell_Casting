from random import random

import pygame

from settings import *

class Bat(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, collision_sprites):
        super().__init__(groups)
        self.groups = groups
        self.frames = {}
        self.load_images()
        self.player = player
        self.state = 'move'
        self.old_state = 'move'
        self.frame_index = 0
        self.image = pygame.image.load(join('images', 'enemies', 'bat', 'move', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.hitbox = self.rect.inflate(-0.5 * BAT_SIZE, BAT_SIZE)
        self.hitbox.bottom = self.rect.bottom
        self.collision_sprites = collision_sprites
        self.angle = 0

        # movement
        self.direction = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.move_speed = 3.125 * BAT_SIZE
        self.move_accel = 0.15 * BAT_SIZE
        self.charge_speed = 0.125 * BAT_SIZE
        self.lunge_speed = 15 * BAT_SIZE
        self.friction = 0.15 * BAT_SIZE
        self.charge_timer = 0
        self.charge_timer_max = 1
        self.lunge_timer = 0
        self.lunge_timer_max = 0.2
        self.attack_cooldown = 0
        self.attack_cooldown_max = 1
        self.rng_num = 0
        self.rng_num_timer = 0
        self.rng_num_timer_max = 1
        self.rng_vec = pygame.Vector2()

    def load_images(self):
        folders = list(walk(join('images', 'enemies', 'bat')))[0][1]
        self.frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', 'bat', folder)):
                self.frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.frames[folder].append(surf)

    def locate_player(self):
        match self.state:
            case 'move':
                target_pos = self.player.pos + self.rng_vec
                self.angle = math.atan2(target_pos.y - self.pos.y, target_pos.x - self.pos.x)
            case 'charge':
                if self.old_state == 'move':
                    self.angle = math.atan2(self.player.pos.y + self.player.vel.y * 0.5 - self.pos.y,
                                            self.player.pos.x + self.player.vel.x * 0.5 - self.pos.x)
            case 'lunge':
                return

        self.direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        if self.direction:
            self.direction = self.direction.normalize()

    def move(self, dt):
        match self.state:
            case 'move':
                self.direction = self.direction.rotate(-30 + self.rng_num * 60)
                self.vel = self.vel.lerp(self.direction * self.move_speed, min(self.move_accel * dt, 1))
            case 'charge':
                self.vel = self.vel.lerp(self.direction * self.charge_speed, min(self.move_accel * dt, 1))
            case 'lunge':
                self.vel = self.vel.lerp(self.direction * self.lunge_speed, min(self.move_accel * dt, 1))

        self.pos.x += self.vel.x * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.pos.y += self.vel.y * dt
        self.rect.bottom = round(self.pos.y) + 0.125 * BAT_SIZE
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.vel.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                        self.pos.x = self.hitbox.centerx
                    else:
                        self.hitbox.left = sprite.hitbox.right
                        self.pos.x = self.hitbox.centerx
                elif direction == 'vertical':
                    if self.vel.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                        self.pos.y = self.hitbox.centery
                    else:
                        self.hitbox.top = sprite.hitbox.bottom
                        self.pos.y = self.hitbox.centery

    def change_state(self):
        self.old_state = self.state

        match self.state:
            case 'move':
                if math.hypot(self.pos.x - self.player.pos.x, self.pos.y - self.player.pos.y) < 200 and not self.attack_cooldown > 0:
                    self.state = 'charge'
                    self.charge_timer = self.charge_timer_max
            case 'charge':
                if not self.charge_timer > 0:
                    self.state = 'lunge'
                    self.lunge_timer = self.lunge_timer_max
            case 'lunge':
                if not self.lunge_timer > 0:
                    self.state = 'move'
                    self.attack_cooldown = self.attack_cooldown_max

    def update_timer(self, dt):
        if self.charge_timer > 0:
            self.charge_timer -= dt * (random() + 1)
        if self.lunge_timer > 0:
            self.lunge_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.rng_num_timer > 0:
            self.rng_num_timer -= dt
        else:
            self.rng_num_timer = self.rng_num_timer_max
            self.rng_num = random()
            ang = self.rng_num * 2 * math.pi
            self.rng_vec = pygame.Vector2(math.cos(ang), math.sin(ang))
            self.rng_vec.scale_to_length(150)

    def animate(self, dt):
        match self.state:
            case 'move':
                self.frame_index += 5 * dt
            case 'charge' | 'lunge':
                self.frame_index += 20 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        self.change_state()
        self.locate_player()
        self.move(dt)
        if self.old_state == 'move' and self.state == 'charge':
            Attack(self.pos + self.direction * 150, - self.angle, self.groups[0], self.player, self, self.charge_timer_max)
        self.update_timer(dt)
        self.animate(dt)

class Attack(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, player, bat, charge_timer_max):
        super().__init__(groups)
        self.player = player
        self.bat = bat
        self.charge_timer = charge_timer_max
        self.charge_timer_max = charge_timer_max
        self.frames = []
        for i in range(2):
            self.frames.append(pygame.image.load(join('images', 'enemies', 'attacks', 'bat_hit_effect', f'{i}.png')).convert_alpha())
            self.frames[i] = pygame.transform.scale(self.frames[i], (1.5 * BAT_ATTACK_SIZE, BAT_ATTACK_SIZE))
            self.frames[i] = pygame.transform.rotate(self.frames[i], angle / math.pi * 180)
        self.image = self.frames[0]
        self.image.set_alpha(int(255 * 0.25 ** 4))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.angle = angle

    def animate(self, dt):
        delta = (self.charge_timer_max - self.charge_timer) / self.charge_timer_max
        if self.charge_timer > 0.25:
            self.image.set_alpha(255 * (0.25 + 0.75 * delta) ** 4)
        else:
            self.image = self.frames[1]

    def update(self, dt):
        print(self.bat)
        if not self.charge_timer > 0.15 or not self.bat.alive():
            self.kill()

        self.animate(dt)
        self.charge_timer -= dt
