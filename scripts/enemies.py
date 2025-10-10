from random import random
from settings import *

class Bat(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, collision_sprites):
        super().__init__(groups)
        self.frames = {}
        self.load_images()
        self.player = player
        self.state = 'move'
        self.frame_index = 0
        self.image = pygame.image.load(join('images', 'enemies', 'bat', 'move', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        self.pos += pygame.Vector2(0, 0.125 * BAT_SIZE)
        self.hitbox = self.rect.inflate(-0.5 * BAT_SIZE, -0.75 * BAT_SIZE)
        self.hitbox.bottom = self.rect.bottom
        self.collision_sprites = collision_sprites

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
        if not self.lunge_timer > 0:
            angle = math.atan2(self.player.pos.y - self.pos.y, self.player.pos.x - self.pos.x)
            self.direction = pygame.Vector2(math.cos(angle), math.sin(angle))
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

    def animate(self, dt):
        match self.state:
            case 'move':
                self.frame_index += 5 * dt
            case 'charge' | 'lunge':
                self.frame_index += 20 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        self.locate_player()
        self.move(dt)
        self.change_state()
        self.update_timer(dt)
        self.animate(dt)
