import pygame

from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'idle_r', 0
        self.image = pygame.image.load(join('images', 'player', 'idle_r', '0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        self.pos += pygame.Vector2(0, 0.125 * PLAYER_SIZE)
        self.hitbox = self.rect.inflate(-0.5 * PLAYER_SIZE, -0.75 * PLAYER_SIZE)
        self.hitbox.bottom = self.rect.bottom

        # movement
        self.direction = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.run_speed = 3.125 * PLAYER_SIZE
        self.dash_speed = 7.5 * PLAYER_SIZE
        self.run_accel = 0.15 * PLAYER_SIZE
        self.dash_accel = 1 * PLAYER_SIZE
        self.friction = 0.15 * PLAYER_SIZE
        self.collision_sprites = collision_sprites
        self.last_run_dir = 'right'
        self.dash_dir = pygame.Vector2()
        self.dash_dir_int = 0
        self.dash_timer = 0
        self.dash_timer_max = 0.18
        self.is_dashing = False
        self.is_dashing_old = False
        self.coyote_time_dash = 0
        self.coyote_time_dash_max = 0.1

    def load_images(self):
        self.frames = {'idle_r': [], 'idle_l': [], 'run_r': [], 'run_l': [], 'dash_r': [], 'dash_l': []}

        for state in self.frames.keys():
            for folder_path, sub_folder, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        surf = pygame.transform.scale(surf, (PLAYER_SIZE, PLAYER_SIZE))
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        if self.direction:
            self.direction = self.direction.normalize()

    def move(self, dt):
        if self.direction == (0, 0) and not self.is_dashing:
            self.vel = self.vel.lerp(pygame.Vector2(), min(self.friction * dt, 1))

        if self.is_dashing_old and not self.is_dashing:
            self.vel = self.vel.normalize() * self.run_speed

        if not self.is_dashing:
            self.vel = self.vel.lerp(self.direction * self.run_speed, min(self.run_accel * dt, 1))
        else:
            self.vel = self.vel.lerp(self.dash_dir * self.dash_speed, min(self.dash_accel * dt, 1))

        self.pos.x += self.vel.x * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.pos.y += self.vel.y * dt
        self.rect.bottom = round(self.pos.y) + 0.125 * PLAYER_SIZE
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

    def dash(self):
        self.coyote_time_dash = self.coyote_time_dash_max

    def dash_update(self, dt):
        self.is_dashing_old = self.is_dashing

        if self.direction and not self.is_dashing and self.coyote_time_dash > 0:
            self.dash_timer = self.dash_timer_max
            self.dash_dir = self.direction
            self.dash_dir_int = math.atan2(self.direction.y, self.direction.x) % (2 * math.pi) * 4 / math.pi
            self.is_dashing = True

        if self.dash_timer > 0:
            self.dash_timer -= dt
        else:
            self.is_dashing = False

        if self.coyote_time_dash > 0:
            self.coyote_time_dash -= dt

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
        if not self.is_dashing:
            if self.vel.length() > 10:
                if self.vel.x >= 0:
                    self.state = 'run_r'
                    self.last_run_dir = 'right'
                else:
                    self.state = 'run_l'
                    self.last_run_dir = 'left'
            else:
                self.state = 'idle_r' if self.last_run_dir == 'right' else 'idle_l'
        else:
            if self.dash_dir.x >= 0:
                self.state = 'dash_r'
                self.last_run_dir = 'right'
            else:
                self.state = 'dash_l'
                self.last_run_dir = 'left'

    def animate(self, dt):
        match self.state:
            case 'run_r' | 'run_l' | 'dash_r' | 'dash_l':
                self.frame_index += 12 * dt
            case 'idle_r' | 'idle_l':
                self.frame_index += 5 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.dash_update(dt)
        self.change_state()
        self.animate(dt)
