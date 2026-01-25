import pygame.sprite

from settings import *
from components import load_audio, play
from particles import RockWallExplosion, ParticleEmitter
from enemies import Bat, Skeleton

class WaveLogic:
    def __init__(self, all_sprites, collision_sprites, short_collision_sprites, enemy_sprites, sfx_slider):
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.short_collision_sprites = short_collision_sprites
        self.enemy_sprites = enemy_sprites
        self.sfx_slider = sfx_slider
        self.player = None
        self.wave_index = 0
        self.enemy_spawn_amount = {1: [5, 0], 2: [4, 4], 3: [8, 6]}
        self.enemies_to_spawn = [0, 0]
        self.enemy_spawn_timer_max = 0.5
        self.enemy_spawn_timer = self.enemy_spawn_timer_max
        self.enemies = []
        self.enemies_old = False
        self.barriers_tiled = [[], [], []]
        self.barriers = [[], [], []]
        self.spawn_positions = [[], [], []]

    def trigger_next_wave(self, index):
        self.wave_index = index
        self.raise_barriers(index)
        self.enemies_to_spawn = self.enemy_spawn_amount[index]

    def raise_barriers(self, index):
        for obj in self.barriers_tiled[index - 1]:
            barrier = Barrier((self.all_sprites, self.collision_sprites), (WORLD_SCALE * obj.x, WORLD_SCALE * obj.y), self.sfx_slider)
            barrier._layer = 13
            self.barriers[index - 1].append(barrier)

    def break_barriers(self, index):
        for obj in self.barriers[index - 1]:
            obj.kill()

    def update(self, dt):
        if self.enemy_spawn_timer > 0:
            self.enemy_spawn_timer -= dt
            if self.enemy_spawn_timer <= 0:
                self.enemy_spawn_timer = self.enemy_spawn_timer_max

                if self.enemies_to_spawn != [0, 0]:
                    if self.enemies_to_spawn[0] > 0:
                        bat = Bat(choice(self.spawn_positions[self.wave_index - 1]), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, self.sfx_slider)
                        bat._layer = 13
                        self.enemies.append(bat)
                        self.enemies_to_spawn[0] -= 1
                    else:
                        skeleton = Skeleton((self.all_sprites, self.enemy_sprites), self.collision_sprites, self.short_collision_sprites, self.player, self.sfx_slider, choice(self.spawn_positions[self.wave_index - 1]))
                        skeleton._layer = 13
                        self.enemies.append(skeleton)
                        self.enemies_to_spawn[1] -= 1

        for enemy in self.enemies:
            if enemy not in self.enemy_sprites:
                self.enemies.remove(enemy)

        if self.enemies_old and not self.enemies:
            if self.wave_index != 3:
                self.break_barriers(self.wave_index + 1)
            else:
                self.break_barriers(1)
                self.break_barriers(2)
                self.break_barriers(3)

        self.enemies_old = self.enemies != []

class Barrier(pygame.sprite.Sprite):
    def __init__(self, groups, pos, sfx_slider):
        super().__init__(groups)
        self.groups = groups
        self.pos = pos
        self.sfx_slider = sfx_slider
        self.frames = []
        self.load_images()
        self.image = pygame.image.load(join('images', 'spells', 'rock_pillar', 'rock_pillar0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (3 * TILE_SIZE, 3.5 * TILE_SIZE))
        self.frame_index = 0
        self.sounds = {}
        load_audio(self, 'spells/rock_wall')
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hitbox = pygame.Rect(0, 0, 3 * TILE_SIZE, 2.5 * TILE_SIZE)
        self.hitbox.midbottom = self.rect.midbottom
        self.hitbox = self.hitbox.inflate((-0.3 * TILE_SIZE, -0.5 * TILE_SIZE))
        self.rect.topleft = self.pos

    def load_images(self):
        for folder_path, _, file_names in walk(join('images', 'spells', 'rock_pillar')):
            for file_name in sorted(file_names, key=lambda name: int(sub(f'[^0-9]', '', name))):
                full_path = join(folder_path, file_name)
                surf = pygame.image.load(full_path).convert_alpha()
                surf = pygame.transform.scale(surf, (3 * TILE_SIZE, 3.5 * TILE_SIZE))
                self.frames.append(surf)

    def kill(self):
        pe = ParticleEmitter(self.groups[0], self.pos, RockWallExplosion, one_shot=True, amount=8)
        pe._layer = 13
        play(self, "destroy", self.sfx_slider, volume=0.2, play_all=True)
        super().kill()

    def animate(self, dt):
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 36 * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)

class WaveAreaTrigger(pygame.sprite.Sprite):
    def __init__(self, groups, obj, player, wave_logic):
        super().__init__(groups)
        self.obj = obj
        self.player = player
        self.wave_logic = wave_logic
        self.pos = pygame.Vector2(WORLD_SCALE * obj.x, WORLD_SCALE * obj.y)
        self.image = pygame.surface.Surface((WORLD_SCALE * obj.width, WORLD_SCALE * obj.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hitbox = self.rect

    def update(self, dt):
        if self.player.hitbox.colliderect(self.hitbox):
            self.wave_logic.trigger_next_wave(self.obj.index)
            self.kill()
