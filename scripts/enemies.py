import pygame.transform

from settings import *
from random import random
from components import *
from spell_book import RockWall

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
        mask = pygame.mask.from_surface(self.image)
        self.mask_surf = mask.to_surface()
        self.mask_surf.set_colorkey((0, 0, 0))
        surf_w, surf_h = self.mask_surf.get_size()
        for x in range(surf_w):
            for y in range(surf_h):
                if self.mask_surf.get_at((x, y))[0] == 255:
                    self.mask_surf.set_at((x, y), (230, 30, 30))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.sounds = {}
        self.max_volume = 0.15
        self.volume = self.max_volume
        load_audio(self, "enemies/bat", self.max_volume)
        self.hitbox = self.rect.inflate(-0.5 * BAT_SIZE, -0.5 * BAT_SIZE)
        self.hitbox.bottom = self.rect.bottom
        self.collision_sprites = collision_sprites
        self.angle = 0
        self.direction = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.move_speed = 2.5 * BAT_SIZE * 0
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
        self.health = HealthComponent(self, 2)
        self.height = 0.0
        self.max_height = 0.0
        self.thrown_speed = 7 * BAT_SIZE
        self.thrown_dir = pygame.Vector2()
        self.thrown_timer_start = 0.0
        self.thrown_timer = 0.0
        self.flap_sfx_timer = 0.1
        self.flap_sfx_timer_max = 0.9
        self.flap_sfx_frequency = 0.0

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

    def kill(self):
        play(self, "death", volume=self.volume * 2)
        super().kill()

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
            case 'thrown':
                self.vel = self.thrown_dir.normalize() * self.thrown_speed
                self.height = (2 * (self.thrown_timer / self.thrown_timer_start) - 1) ** 2 * self.max_height - self.max_height

        self.pos.x += self.vel.x * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = round(self.pos.x)
        if self.state != 'thrown':
            self.collision('horizontal')
        self.pos.y += self.vel.y * dt
        if self.state == 'thrown':
            self.rect.bottom = round(self.pos.y) + 0.125 * BAT_SIZE + self.height
        else:
            self.rect.bottom = round(self.pos.y) + 0.125 * BAT_SIZE
        self.hitbox.centery = round(self.pos.y)
        if self.state != 'thrown':
            self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if hasattr(sprite, 'hit_timer') and sprite.hit_timer > 0:
                    continue
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
                    play(self, "attack", play_all=True, volume=self.volume)
            case 'lunge':
                if not self.lunge_timer > 0:
                    self.state = 'move'
                    self.attack_cooldown = self.attack_cooldown_max
            case 'thrown':
                if self.thrown_timer <= 0:
                    if self.health.health <= 0:
                        self.kill()
                    else:
                        self.state = 'move'

    def update_timer(self, dt):
        if self.charge_timer > 0:
            self.charge_timer -= dt * (random() + 1)
        if self.lunge_timer > 0:
            self.lunge_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.health.i_frame_timer > 0:
            self.health.i_frame_timer -= dt
        if self.thrown_timer > 0:
            self.thrown_timer -= dt
        if self.rng_num_timer > 0:
            self.rng_num_timer -= dt
        else:
            self.rng_num_timer = self.rng_num_timer_max
            self.rng_num = random()
            ang = self.rng_num * 2 * math.pi
            self.rng_vec = pygame.Vector2(math.cos(ang), math.sin(ang))
            self.rng_vec.scale_to_length(150)

        match self.state:
            case 'move':
                self.flap_sfx_frequency = 1.0
            case 'charge':
                self.flap_sfx_frequency = 4.0
            case _:
                self.flap_sfx_frequency = 0.0

        self.flap_sfx_timer -= dt * self.flap_sfx_frequency
        if self.flap_sfx_timer <= 0:
            play(self, "flap", volume=self.volume)
            self.flap_sfx_timer = self.flap_sfx_timer_max

    def animate(self, dt):
        match self.state:
            case 'move':
                self.frame_index += 5 * dt
            case 'charge' | 'lunge':
                self.frame_index += 20 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

        if self.health.i_frame_timer > 0:
            self.image = self.mask_surf

    def update(self, dt):
        self.change_state()
        self.locate_player()
        
        self.move(dt)
        self.volume = max(self.max_volume * (800.0 - self.pos.distance_to(self.player.pos)) / 800.0, 0)
        if self.old_state == 'move' and self.state == 'charge':
            attack = BatAttack(self.groups[0], self.collision_sprites, self.pos + self.direction * 150, self.direction, -self.angle, self.player, self, self.charge_timer_max + 0.05)
            attack._layer = 11
        self.update_timer(dt)
        self.animate(dt)

class BatAttack(pygame.sprite.Sprite):
    def __init__(self, groups, collision_sprites, pos, dir, angle, player, bat, charge_timer_max):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
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
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.Vector2(self.rect.center)
        self.dir = dir
        self.angle = angle

    def animate(self):
        delta = (self.charge_timer_max - self.charge_timer) / self.charge_timer_max
        if self.charge_timer > 0.25:
            self.image.set_alpha(255 * (0.25 + 0.75 * delta) ** 4)
        else:
            self.image = self.frames[1]

            if self.player.hitbox.colliderect(self.hitbox):
                offset = (self.player.hitbox.left - self.rect.left, self.player.hitbox.top - self.rect.top)
                if self.mask.overlap(pygame.mask.Mask(self.player.hitbox.size, True), offset):
                    self.player.damage(2, 300, self.dir, 50)

            for sprite in self.collision_sprites:
                if isinstance(sprite, RockWall) and sprite.hitbox.colliderect(self.hitbox):
                    offset = (sprite.hitbox.left - self.rect.left, sprite.hitbox.top - self.rect.top)
                    if self.mask.overlap(pygame.mask.Mask(sprite.hitbox.size, True), offset):
                        sprite.damage(1)

    def update(self, dt):
        if not self.charge_timer > 0.15 or not self.bat.alive() or self.bat.state == 'thrown':
            self.kill()

        self.animate()
        self.charge_timer -= dt

class Skeleton(pygame.sprite.Sprite):
    def __init__(self, groups, collision_sprites, player, pos):
        super().__init__(groups)
        self.groups = groups
        self.collision_sprites = collision_sprites
        self.player = player
        self.frames = {}
        self.load_images()
        self.state = 'walk'
        self.old_state = 'walk'
        self.frame_index = 0
        self.image = pygame.image.load(join('images', 'enemies', 'skeleton', 'idle', 'idle0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (1.5 * SKELETON_SIZE, SKELETON_SIZE))
        mask = pygame.mask.from_surface(self.image)
        self.mask_surf = mask.to_surface()
        self.mask_surf.set_colorkey((0, 0, 0))
        surf_w, surf_h = self.mask_surf.get_size()
        for x in range(surf_w):
            for y in range(surf_h):
                if self.mask_surf.get_at((x, y))[0] == 255:
                    self.mask_surf.set_at((x, y), (230, 30, 30))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.sounds = {}
        self.max_volume = 0.15
        self.volume = self.max_volume
        load_audio(self, "enemies/skeleton", self.max_volume)
        self.hitbox = self.rect.inflate(-0.875 * SKELETON_SIZE, -0.875 * SKELETON_SIZE)
        self.hitbox.bottom = self.rect.bottom
        self.direction = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.walk_speed = 0.8 * SKELETON_SIZE
        self.walk_accel = 0.15 * SKELETON_SIZE
        self.friction = 0.15 * SKELETON_SIZE
        self.charge_timer = 0
        self.charge_timer_max = 2
        self.fire_timer = 0
        self.fire_timer_max = 0.2
        self.attack_cooldown_max = 3
        self.attack_cooldown = self.attack_cooldown_max
        self.attack_range = 400.0
        self.health = HealthComponent(self, 2)
        self.height = 0.0
        self.max_height = 0.0
        self.thrown_speed = 7 * SKELETON_SIZE
        self.thrown_dir = pygame.Vector2()
        self.thrown_timer_start = 0.0
        self.thrown_timer = 0.0
        self.walk_sfx_timer = 0.1
        self.walk_sfx_timer_max = 0.9
        self.flip = False
        self.rng_num = 0
        self.rng_num_timer = 0
        self.rng_num_timer_max = 5
        self.rng_vec = pygame.Vector2()

    def load_images(self):
        folders = list(walk(join('images', 'enemies', 'skeleton')))[0][1]
        self.frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', 'skeleton', folder)):
                self.frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(sub(f'[^0-9]', '', name))):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    surf = pygame.transform.scale(surf, (1.5 * SKELETON_SIZE, SKELETON_SIZE))
                    self.frames[folder].append(surf)

    def kill(self):
        play(self, "death", volume=self.volume * 2)
        super().kill()

    def locate_player(self):
        match self.state:
            case 'walk' | 'idle':
                self.direction = (self.player.pos + self.rng_vec + (self.pos - self.player.pos).normalize() * self.attack_range - self.pos)
            case 'charge':
                if self.old_state in ['walk', 'idle']:
                    self.direction = (self.player.pos + 0.5 * self.player.vel - self.pos)
            case 'fire':
                return

    def move(self, dt):
        match self.state:
            case 'walk':
                self.vel = self.vel.lerp(self.direction.normalize() * self.walk_speed, min(self.walk_accel * dt, 1))
            case 'charge' | 'fire' | 'idle':
                self.vel = self.vel.lerp(pygame.Vector2(), min(self.friction * dt, 1))
            case 'thrown':
                self.vel = self.thrown_dir.normalize() * self.thrown_speed
                self.height = (2 * (self.thrown_timer / self.thrown_timer_start) - 1) ** 2 * self.max_height - self.max_height

        self.pos.x += self.vel.x * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = round(self.pos.x)
        if self.state != 'thrown':
            self.collision('horizontal')
        self.pos.y += self.vel.y * dt
        if self.state == 'thrown':
            self.rect.bottom = round(self.pos.y) + 0.125 * BAT_SIZE + self.height
        else:
            self.rect.bottom = round(self.pos.y) + 0.125 * BAT_SIZE
        self.hitbox.bottom = self.rect.bottom
        if self.state != 'thrown':
            self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if hasattr(sprite, 'hit_timer') and sprite.hit_timer > 0:
                    continue
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
            case 'walk' | 'idle':
                if self.state == 'walk' and self.direction.length() < 30:
                    self.state = 'idle'
                elif self.state == 'idle' and self.direction.length() > 30:
                    self.state = 'walk'

                if (self.player.pos - self.pos).length() < 1.4 * self.attack_range and not self.attack_cooldown > 0:
                    self.state = 'charge'
                    self.charge_timer = self.charge_timer_max
                    self.frame_index = 0
                    play(self, "charge", volume=self.volume)
            case 'charge':
                if not self.charge_timer > 0:
                    self.state = 'fire'
                    self.fire_timer = self.fire_timer_max
                    self.frame_index = 0
                    play(self, "fire", play_all=True, volume=self.volume)
            case 'fire':
                if not self.fire_timer > 0:
                    self.state = 'walk'
                    self.attack_cooldown = self.attack_cooldown_max + random() - 0.5
            case 'thrown':
                if self.thrown_timer <= 0:
                    if self.health.health <= 0:
                        self.kill()
                    else:
                        self.state = 'walk'

    def update_timer(self, dt):
        if self.charge_timer > 0:
            self.charge_timer -= dt * (random() + 1)
        if self.fire_timer > 0:
            self.fire_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.health.i_frame_timer > 0:
            self.health.i_frame_timer -= dt
        if self.thrown_timer > 0:
            self.thrown_timer -= dt
        if self.rng_num_timer > 0:
            self.rng_num_timer -= dt
        else:
            self.rng_num_timer = self.rng_num_timer_max
            self.rng_num = random()
            ang = self.rng_num * 2 * math.pi
            self.rng_vec = pygame.Vector2(math.cos(ang), math.sin(ang))
            self.rng_vec.scale_to_length(150)

        match self.state:
            case 'walk':
                self.walk_sfx_frequency = 1.0
            case _:
                self.walk_sfx_frequency = 0.0

        self.walk_sfx_timer -= dt * self.walk_sfx_frequency
        if self.walk_sfx_timer <= 0:
            play(self, "walk", volume=self.volume)
            self.walk_sfx_timer = self.walk_sfx_timer_max

    def animate(self, dt):
        match self.state:
            case 'walk':
                if (self.player.pos - self.pos).length() >= self.attack_range:
                    self.frame_index += 8 * dt
                else:
                    self.frame_index -= 8 * dt
            case 'idle':
                self.frame_index += 8 * dt
            case 'charge' | 'fire':
                if self.frame_index < len(self.frames[self.state]) - 1:
                    self.frame_index += 10 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

        if self.state in ['walk', 'idle']:
            self.flip = self.player.pos.x - self.pos.x < 0

        if self.flip:
            self.image = pygame.transform.flip(self.image, 1, 0)

        if self.health.i_frame_timer > 0:
            self.image = self.mask_surf

    def update(self, dt):
        self.change_state()
        self.locate_player()

        self.move(dt)
        self.volume = max(self.max_volume * (800.0 - self.pos.distance_to(self.player.pos)) / 800.0, 0)
        if self.old_state in ['walk', 'idle'] and self.state == 'charge':
            attack = SkeletonAttack(self.groups[0], self.collision_sprites, self.pos + self.direction.normalize() * 150, self.direction.normalize(),
                               self.direction.angle_to((1, 0)) / 180 * math.pi, self.player, self, self.charge_timer_max * 0.8, 20)
            attack._layer = 11
        self.update_timer(dt)
        self.animate(dt)

class SkeletonAttack(pygame.sprite.Sprite):
    def __init__(self, groups, collision_sprites, pos, dir, angle, player, skeleton, charge_timer_max, range_count):
        super().__init__(groups)
        self.groups = groups
        self.collision_sprites = collision_sprites
        self.player = player
        self.skeleton = skeleton
        self.charge_timer = charge_timer_max
        self.charge_timer_max = charge_timer_max
        self.has_just_spawned = 2
        self.range_count = range_count - 1
        self.frames = []
        for i in range(2):
            self.frames.append(pygame.image.load(join('images', 'enemies', 'attacks', 'bat_hit_effect', f'{i}.png')).convert_alpha())
            self.frames[i] = pygame.transform.scale(self.frames[i], (3 * SKELETON_ATTACK_SIZE, SKELETON_ATTACK_SIZE))
            self.frames[i] = pygame.transform.rotate(self.frames[i], angle / math.pi * 180)
        self.image = self.frames[0]
        self.image.set_alpha(int(255 * 0.25 ** 4))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = pygame.Vector2(self.rect.center)
        self.dir = dir
        self.angle = angle

    def animate(self):
        delta = (self.charge_timer_max - self.charge_timer) / self.charge_timer_max
        if self.charge_timer > 0.25:
            self.image.set_alpha(255 * (0.25 + 0.75 * delta) ** 4)
        else:
            self.image = self.frames[1]

            if self.player.hitbox.colliderect(self.hitbox):
                offset = (self.player.hitbox.left - self.rect.left, self.player.hitbox.top - self.rect.top)
                if self.mask.overlap(pygame.mask.Mask(self.player.hitbox.size, True), offset):
                    self.player.damage(2, 300, self.dir, 50)

            for sprite in self.collision_sprites:
                if isinstance(sprite, RockWall) and sprite.hitbox.colliderect(self.hitbox):
                    offset = (sprite.hitbox.left - self.rect.left, sprite.hitbox.top - self.rect.top)
                    if self.mask.overlap(pygame.mask.Mask(sprite.hitbox.size, True), offset):
                        sprite.damage(1)

    def spawn_next_attack(self):
        for sprite in self.collision_sprites:
            if isinstance(sprite, RockWall) and sprite.hitbox.colliderect(self.hitbox):
                offset = (sprite.hitbox.left - self.rect.left, sprite.hitbox.top - self.rect.top)
                if self.mask.overlap(pygame.mask.Mask(sprite.hitbox.size, True), offset):
                    return

        if self.range_count > 0:
            attack = SkeletonAttack(self.groups, self.collision_sprites, self.pos + pygame.Vector2(WORLD_SCALE * 48, 0).rotate(-self.angle / math.pi * 180),
                                    self.dir, self.angle, self.player, self.skeleton, self.charge_timer_max + 0.05, self.range_count)
            attack._layer = 11

    def update(self, dt):
        if not self.charge_timer > 0.15 or not self.skeleton.alive() or self.skeleton.state == 'thrown':
            self.kill()

        self.animate()
        self.charge_timer -= dt
        if self.has_just_spawned > 0:
            self.has_just_spawned -= 1
            if self.has_just_spawned <= 0:
                self.spawn_next_attack()

