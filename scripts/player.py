import pygame
from random import choice

from settings import *
from user_interface import *
from spell_line import SpellLine
from spell_book import *
from particles import ParticleEmitter, DashParticle
from components import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, collision_sprites, ui_sprites, enemy_sprites, pos):
        super().__init__(groups)
        self.groups = groups
        self.collision_sprites = collision_sprites
        self.ui_sprites = ui_sprites
        self.enemy_sprites = enemy_sprites
        self.frames = {}
        self.load_images()
        self.sounds = {}
        load_audio(self, "player", 0.3)
        self.set_volume()
        self.state, self.frame_index = 'idle', 0
        self.image = pygame.image.load(join('images', 'player', 'idle', 'idle0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.bottom)
        self.pos += pygame.Vector2(0, 0.125 * PLAYER_SIZE)
        self.hitbox = self.rect.inflate(-0.5 * PLAYER_SIZE, -0.75 * PLAYER_SIZE)
        self.hitbox.bottom = self.rect.bottom
        self.mana_bar = ManaBar((self.groups, self.ui_sprites))
        self.mana_bar._layer = 30
        self.health_bar = HealthBar((self.groups, self.ui_sprites))
        self.health_bar._layer = 30
        self.direction = pygame.Vector2()
        self.vel = pygame.Vector2()
        self.run_speed = 3.25 * PLAYER_SIZE
        self.dash_speed = 7.5 * PLAYER_SIZE
        self.run_accel = 0.15 * PLAYER_SIZE
        self.dash_accel = 1 * PLAYER_SIZE
        self.friction = 0.15 * PLAYER_SIZE
        self.is_moving_right = True
        self.dash_dir = pygame.Vector2()
        self.dash_dir_int = 0
        self.dash_timer = 0
        self.dash_timer_max = 0.18
        self.is_dashing = False
        self.is_dashing_old = False
        self.coyote_time_dash = 0
        self.coyote_time_dash_max = 0.1
        self.coyote_time_cast = 0
        self.coyote_time_cast_max = 0.18
        self.spell_list = []
        self.is_drawing = False
        self.spell_line = SpellLine(self, self.groups)
        self.fast_wind_speed_mult = 1.8
        self.is_fast_wind = False
        self.fast_wind_effects = []
        self.i_frame_timer = 0
        self.i_frame_timer_max = 0.5
        self.dash_particle_emitter = pygame.sprite.Sprite()
        self.height = 0.0
        self.max_height = 0.0
        self.thrown_speed = 7 * PLAYER_SIZE
        self.thrown_dir = pygame.Vector2()
        self.thrown_timer_start = 0.0
        self.thrown_timer = 0.0
        self.dash_start_pos = pygame.Vector2()
        self.recharge_timer_max = 0.4
        self.recharge_timer = 0
        self.recharge_rate = 0.7
        self.dragons_breath = None
        self.fire_timer = 0
        self.fire_timer_max = 2
        self.walk_speed = 1.25 * PLAYER_SIZE
        self.walk_accel = 0.25 * PLAYER_SIZE
        self.run_sfx_timer = 0.1
        self.run_sfx_timer_max = 0.3
        self.run_sfx_frequency = 0.0
        self.has_cat_ears = False

    def load_images(self):
        folders = list(walk(join('images', 'player')))[0][1]
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'player', folder)):
                self.frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(sub(f'[^0-9]', '', name))):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    surf = pygame.transform.scale(surf, (PLAYER_SIZE, PLAYER_SIZE))
                    self.frames[folder].append(surf)

    def set_volume(self):
        self.sounds["damage"][0].set_volume(0.6)
        self.sounds["damage"][1].set_volume(0.6)
        self.sounds["damage"][2].set_volume(1.5)
        self.sounds["fw_start"][0].set_volume(0.2)
        self.sounds["fw_loop"][0].set_volume(0.1)
        self.sounds["fw_end"][0].set_volume(0.2)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        if self.direction:
            self.direction = self.direction.normalize()

    def change_state(self):
        match self.state:
            case 'idle':
                if self.is_dashing:
                    self.state = 'dash'
                elif self.vel.length() > 10:
                    self.is_moving_right = True if self.vel.x >= 0 else False
                    self.state = 'walk' if self.fire_timer > 0 else 'run'

            case 'run':
                self.is_moving_right = True if self.vel.x >= 0 else False
                if self.is_dashing:
                    self.state = 'dash'
                elif self.vel.length() < 10:
                    self.state = 'idle'

            case 'dash':
                if self.dash_dir.x != 0:
                    self.is_moving_right = True if self.dash_dir.x >= 0 else False
                if not self.is_dashing:
                    if len(self.spell_list) > 6:
                        self.cast_fail()
                        if self.vel.length() > 10:
                            self.state = 'run'
                        else:
                            self.state = 'idle'
                    else:
                        self.state = 'dash_idle'

            case 'dash_idle':
                if self.is_dashing:
                    self.state = 'dash'
                elif not self.is_drawing:
                    if self.vel.length() > 10:
                        self.state = 'run'
                    else:
                        self.state = 'idle'

            case 'walk':
                self.is_moving_right = True if self.vel.x >= 0 else False
                if self.vel.length() < 10:
                    self.state = 'idle'
                if self.fire_timer <= 0:
                    self.dragons_breath.kill()
                    self.state = 'idle' if self.vel.length() < 10 else 'run'

            case 'thrown':
                if self.thrown_timer <= 0:
                    if self.health_bar.charge <= 0:
                        self.die()
                    else:
                        self.frame_index = 0
                        self.state = 'get_up'
                        play(self, "knockback_land")

            case 'get_up':
                pass

            case 'dead':
                pass

    def damage(self, damage_val, kb_strength=None, kb_dir=None, max_height=100, roll=False):
        if self.i_frame_timer <= 0 and self.state != 'dead' and self.state != 'thrown':
            self.i_frame_timer = self.i_frame_timer_max
            self.health_bar.charge -= damage_val
            play(self, "damage", play_all=True)

            if kb_strength and kb_dir:
                self.state = 'thrown'
                self.thrown_dir = kb_dir
                self.max_height = max_height
                self.is_moving_right = True if self.thrown_dir.x >= 0 else False
                self.thrown_timer = kb_strength / self.thrown_speed
                self.thrown_timer_start = self.thrown_timer
                self.frame_index = 0
                self.fire_timer = 0
                if self.dragons_breath:
                    self.dragons_breath.kill()
                self.cast_fail()
            elif self.health_bar.charge <= 0:
                self.die()

    def die(self):
        self.state = 'dead'
        self.cast_fail()
        self.frame_index = 0
        self.vel = pygame.Vector2()
        play(self, "death")

    def move(self, dt):
        match self.state:
            case 'dead':
                return
            case 'get_up':
                self.vel = self.vel.lerp(pygame.Vector2(), min(self.friction * dt, 1))
            case 'thrown':
                self.vel = self.thrown_dir.normalize() * self.thrown_speed
                self.height = (2 * (self.thrown_timer / self.thrown_timer_start) - 1) ** 2 * self.max_height - self.max_height
            case 'dash':
                self.vel = self.vel.lerp(self.dash_dir * self.dash_speed, min(self.dash_accel * dt, 1))
            case _:
                if self.is_drawing:
                    self.vel = pygame.Vector2()
                    if self.is_dashing_old:
                        self.spell_line.stop_drawing()
                elif self.is_dashing_old:
                    self.vel = self.vel.normalize() * self.run_speed
                elif self.direction == (0, 0):
                    self.vel = self.vel.lerp(pygame.Vector2(), min(self.friction * dt, 1))
                elif self.fire_timer > 0:
                    self.vel = self.vel.lerp(self.direction * self.walk_speed, min(self.walk_accel * dt, 1))
                else:
                    self.vel = self.vel.lerp(self.direction * self.run_speed, min(self.run_accel * dt, 1))

        self.pos.x += self.vel.x * dt if not self.is_fast_wind else self.fast_wind_speed_mult * self.vel.x * dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        self.pos.y += self.vel.y * dt if not self.is_fast_wind else self.fast_wind_speed_mult * self.vel.y * dt
        if self.state == 'thrown':
            self.rect.bottom = round(self.pos.y) + 0.125 * PLAYER_SIZE + self.height
        else:
            self.rect.bottom = round(self.pos.y) + 0.125 * PLAYER_SIZE
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

    def set_coyote_time_dash(self):
        if self.state in ('idle', 'run', 'dash', 'dash_idle'):
            self.coyote_time_dash = self.coyote_time_dash_max

    def dash(self, dt):
        self.is_dashing_old = self.is_dashing

        if self.direction and not self.is_dashing and self.coyote_time_dash > 0 and self.mana_bar.charge >= 1:
            self.coyote_time_dash = 0
            self.dash_timer = self.dash_timer_max if not self.is_fast_wind else self.dash_timer_max / self.fast_wind_speed_mult
            self.dash_dir = self.direction
            self.dash_dir_int = math.atan2(self.direction.y, self.direction.x) % (2 * math.pi) * 4 / math.pi
            if not self.spell_list:
                self.spell_list.append(self.dash_dir_int)
            else:
                self.spell_list.append((self.dash_dir_int - self.spell_list[0]) % 8)
            self.is_dashing = True
            self.is_drawing = True
            play(self, "dash")
            self.spell_line.start_drawing()
            self.dash_particle_emitter = ParticleEmitter(self.groups, self.pos, DashParticle, cooldown_timer_max=0.005)
            self.dash_particle_emitter._layer = 13
            self.mana_bar.charge -= 1
            self.recharge_timer = self.recharge_timer_max

        if self.dash_timer > 0:
            self.dash_timer -= dt
            self.dash_particle_emitter.pos = self.hitbox.center
        else:
            self.is_dashing = False
            self.dash_particle_emitter.kill()

        if self.coyote_time_dash > 0:
            self.coyote_time_dash -= dt

    def set_coyote_time_cast(self):
        self.coyote_time_cast = self.coyote_time_cast_max

    def try_casting(self, dt):
        if self.spell_list and self.coyote_time_cast > 0 and not self.is_dashing:
            self.coyote_time_cast = 0
            if self.is_fast_wind:
                play(self, "fw_end")
                pause(self, "fw_loop")
                self.is_fast_wind = False
                for fwe in self.fast_wind_effects:
                    fwe.kill()
            self.cast()
            self.spell_list = []
            self.is_drawing = False
            self.spell_line.clear_all()

        if self.coyote_time_cast > 0:
            self.coyote_time_cast -= dt

    def cast(self):
        spell_dir = self.spell_list.pop(0)
        match self.spell_list:
            case []:
                shooting_star = ShootingStar(self.pos, self.dash_dir, self.groups, self.enemy_sprites, self, self.collision_sprites)
                shooting_star._layer = 0
                return 'falling_star'
            case [0]:
                self.is_fast_wind = True
                play(self, "fw_start")
                play(self, "fw_loop", repeat=-1)
                for i in (24, 12, 9):
                    fwe = FastWindEffect(self.rect.center + pygame.Vector2(0, -1), i, self, self.groups)
                    fwe._layer = 13
                    self.fast_wind_effects.append(fwe)
                return 'fast_wind'
            case [1] | [7]:
                hd = HealthDrain(self.groups, self)
                hd._layer = 13
                return 'health_drain'
            case [3] | [5]:
                self.fire_timer = self.fire_timer_max
                self.dragons_breath = DragonsBreath(self.groups, self.enemy_sprites, self.collision_sprites, self, self.dash_dir)
                self.state = 'walk'
                return 'dragons_breath'
            case [4]:
                rock_wall = RockWall((self.groups, self.collision_sprites), self.enemy_sprites, self, self.pos.copy(), self.dash_dir)
                rock_wall._layer = 13
                return 'stone_wall'
            case [3, 1, 4] | [5, 7, 4]:
                self.has_cat_ears = not self.has_cat_ears
                return 'car_ears'

    def cast_fail(self):
        self.coyote_time_dash = 0
        self.spell_list = []
        self.is_drawing = False
        self.spell_line.clear_all()
        if self.is_fast_wind:
            play(self, "fw_end")
            pause(self, "fw_loop")
            self.is_fast_wind = False
            for fwe in self.fast_wind_effects:
                fwe.kill()

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

    def animate(self, dt):
        match self.state:
            case 'run' | 'dash':
                self.frame_index += 13 * dt
            case 'idle' | 'walk':
                self.frame_index += 5 * dt
            case 'dash_idle':
                self.frame_index += 2 * dt
            case 'thrown':
                if self.frame_index < len(self.frames[self.state]) - 1:
                    self.frame_index += 20 * dt
            case 'get_up':
                self.frame_index += 12 * dt
                if self.frame_index >= len(self.frames[self.state]):
                    self.state = 'idle'
            case 'dead':
                if self.frame_index < len(self.frames[self.state]) - 1:
                    self.frame_index += 12 * dt

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])] if not self.has_cat_ears else self.frames[self.state + "_cat_ears"][int(self.frame_index) % len(self.frames[self.state])]

        if not self.is_moving_right:
            self.image = pygame.transform.flip(self.image, 1, 0)

        if self.i_frame_timer > self.i_frame_timer_max * 0.8:
            mask = pygame.mask.from_surface(self.image)
            mask_surf = mask.to_surface()
            mask_surf.set_colorkey((0, 0, 0))
            surf_w, surf_h = mask_surf.get_size()
            for x in range(surf_w):
                for y in range(surf_h):
                    if mask_surf.get_at((x, y))[0] == 255:
                        mask_surf.set_at((x, y), (230, 30, 30))
            self.image = mask_surf

    def update_timers(self, dt):
        if self.i_frame_timer > 0:
            self.i_frame_timer -= dt

        if self.thrown_timer > 0:
            self.thrown_timer -= dt

        if self.recharge_timer > 0:
            self.recharge_timer -= dt

        if self.fire_timer > 0:
            self.fire_timer -= dt
            if self.fire_timer <= 0:
                self.dragons_breath.kill()

        match self.state:
            case 'run':
                self.run_sfx_frequency = 1.0
            case 'walk':
                self.run_sfx_frequency = 0.5
            case _:
                self.run_sfx_frequency = 0.0

        self.run_sfx_timer -= dt * self.run_sfx_frequency
        if self.run_sfx_timer <= 0:
            play(self, "footsteps")
            self.run_sfx_timer = self.run_sfx_timer_max

    def update(self, dt):
        self.input()
        self.move(dt)
        self.dash(dt)
        self.try_casting(dt)
        self.change_state()
        self.animate(dt)
        self.update_timers(dt)

        if self.mana_bar.charge < 6 and self.recharge_timer <= 0:
            self.mana_bar.charge = min(self.mana_bar.charge + self.recharge_rate * self.fast_wind_speed_mult * dt, 6) if self.is_fast_wind else min(self.mana_bar.charge + self.recharge_rate * dt, 6)
