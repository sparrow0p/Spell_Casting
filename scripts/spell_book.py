import pygame

from settings import *
from particles import *
from components import *

class ShootingStar(pygame.sprite.Sprite):
    def __init__(self, pos, dir, groups, enemy_sprites, player, collision_sprites):
        super().__init__(groups)
        self.groups = groups
        self.enemy_sprites = enemy_sprites
        self.player = player
        self.dir = dir.normalize()
        self.state, self.frame_index = 'fly', 0
        self.image = pygame.Surface((20, 20))
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.sounds = {}
        load_audio(self, 'spells/shooting_star', 0.2)
        play(self, "fly")
        self.collision_sprites = collision_sprites
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 2500
        self.min_speed = 150
        self.decel = 8000
        self.fly_timer = 0.5
        self.explosion_timer = 0.1
        self.particle_emitter = ParticleEmitter(self.groups, self.pos.copy(), ShootingStarFlyParticle, -self.dir, 0.005)
        self.particle_emitter._layer = 13
        self.radius = 120
        self.explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.explosion_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.explosion_surface, (255, 0, 0), (self.radius, self.radius), self.radius)
        self.mask = pygame.mask.from_surface(self.explosion_surface)

    def move(self, dt):
        if self.fly_timer > 0:
            self.pos += self.dir * self.speed * dt

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        self.hitbox.center = self.rect.center
        self.particle_emitter.pos = self.pos.copy()

        if self.speed > self.min_speed:
            self.speed -= self.decel * dt
            if self.speed < self.min_speed:
                self.speed = self.min_speed

    def explosion(self):
        for sprite in self.enemy_sprites:
            if self.pos.distance_to(sprite.pos) < 120 + sprite.hitbox.width / 2:
                apply_damage(sprite, 1, 200, sprite.pos - self.pos, 20)

        for sprite in self.collision_sprites:
            if isinstance(sprite, RockWall) and self.pos.distance_to(sprite.pos) < 120 + sprite.hitbox.width / 2:
                sprite.destroy('star', (sprite.pos - self.pos + pygame.Vector2(0, 40)).normalize())

        if self.pos.distance_to(self.player.pos) < 120 + self.player.hitbox.width / 2:
            self.player.damage(0, 200, self.player.pos - self.pos, 30, True)

    def update_timers(self, dt):
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
                    self.rect = self.explosion_surface.get_rect(center=self.rect.center)
                    self.hitbox = self.rect
                    self.particle_emitter.kill()
                    self.particle_emitter = ParticleEmitter(self.groups, self.pos.copy(), ShootingStarExplodeParticle, amount=100, one_shot=True)
                    self.particle_emitter._layer = 13
                    play(self, "explode", play_all=True)
                    pause(self, "fly")
            case 'explode':
                pass

    def collision(self):
        for sprite in self.enemy_sprites:
            if sprite.rect.colliderect(self.hitbox):
                return True

        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                return True

        return False

    def update(self, dt):
        self.move(dt)
        if self.state == 'explode':
            self.explosion()
        self.update_timers(dt)
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

class RockWall(pygame.sprite.Sprite):
    def __init__(self, groups, enemy_sprites, player, pos, dir):
        super().__init__(groups)
        self.groups = groups
        self.enemy_sprites = enemy_sprites
        self.player = player
        self.frames = []
        self.load_images()
        self.image = pygame.image.load(join('images', 'spells', 'rock_pillar', 'rock_pillar0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (3 * TILE_SIZE, 3.5 * TILE_SIZE))
        self.frame_index = 0
        self.sounds = {}
        load_audio(self, 'spells/rock_wall', 0.3)
        play(self, "create")
        self.dir = dir
        self.pos = pos + pygame.Vector2(2.5 * dir.x * TILE_SIZE, 2.25 * dir.y * TILE_SIZE - 0.5 * TILE_SIZE)
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = pygame.Rect(0, 0, 3 * TILE_SIZE, 2.5 * TILE_SIZE)
        self.hitbox.midbottom = self.rect.midbottom
        self.hitbox = self.hitbox.inflate((-0.3 * TILE_SIZE, -0.5 * TILE_SIZE))
        self.rect.center = self.pos
        self.hit_timer = 0.1
        self.health = 3
        self.i_frame_timer = 0
        self.i_frame_timer_max = 0.3
        self.shake_timer = 0
        self.shake_timer_max = 0.05

    def load_images(self):
        for folder_path, _, file_names in walk(join('images', 'spells', 'rock_pillar')):
            for file_name in sorted(file_names, key=lambda name: int(sub(f'[^0-9]', '', name))):
                full_path = join(folder_path, file_name)
                surf = pygame.image.load(full_path).convert_alpha()
                surf = pygame.transform.scale(surf, (3 * TILE_SIZE, 3.5 * TILE_SIZE))
                self.frames.append(surf)

    def attack(self):
        for sprite in self.enemy_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                apply_damage(sprite, 1, 300, sprite.pos - self.pos, 40)

        for sprite in self.groups[1]:
            if isinstance(sprite, RockWall) and sprite != self:
                if sprite.hitbox.colliderect(self.hitbox):
                    sprite.destroy('rock', (sprite.pos - self.player.pos + pygame.Vector2(0, 40)).normalize())

    def damage(self, damage, type=None, dir=None):
        if self.i_frame_timer <= 0:
            self.health -= damage
            self.i_frame_timer = self.i_frame_timer_max
            play(self, "damage", play_all=True)
            if self.health <= 0:
                if type and dir:
                    self.destroy(type, dir)
                self.kill()

    def shake(self):
        shake_offset = pygame.Vector2(randint(-2, 2), randint(-2, 2))
        self.rect.center = self.pos + shake_offset

    def destroy(self, type, dir):
        match type:
            case 'star':
                for i in range(-1, 2):
                    rwr = RockWallRocks(self.groups[0], self.groups[1], self.enemy_sprites, self.pos.copy(), dir.rotate(i * 15), 700, 1, type)
                    rwr._layer = 13
            case 'fire':
                for i in range(-3, 4):
                    rwr = RockWallRocks(self.groups[0], self.groups[1], self.enemy_sprites, self.pos.copy(), dir.rotate(i * 30), 700, 1, type)
                    rwr._layer = 13
            case 'rock':
                for i in range(-5, 6):
                    rwr = RockWallRocks(self.groups[0], self.groups[1], self.enemy_sprites, self.pos.copy(), dir.rotate(i * 30), 700, 1, type)
                    rwr._layer = 13

        self.kill()

    def kill(self):
        pe = ParticleEmitter(self.groups, self.pos, RockWallExplosion, one_shot=True, amount=8)
        pe._layer = 13
        play(self, "destroy", play_all=True)
        super().kill()

    def animate(self, dt):
        if self.frame_index < len(self.frames) - 1:
            self.frame_index += 36 * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = len(self.frames) - 1

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        if self.hit_timer > 0:
            self.attack()
            self.hit_timer -= dt

        if self.i_frame_timer > 0:
            self.i_frame_timer -= dt
            if self.i_frame_timer <= 0:
                self.rect.center = self.pos

        if self.i_frame_timer > 0:
            if self.shake_timer > 0:
                self.shake_timer -= dt
            else:
                self.shake_timer = self.shake_timer_max
                self.shake()

        self.animate(dt)

class RockWallRocks(pygame.sprite.Sprite):
    def __init__(self, groups, collision_sprites, enemy_sprites, pos, dir, speed, life_timer, type):
        super().__init__(groups)
        self.groups = groups
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.life_timer = life_timer
        self.type = type
        self.image = pygame.image.load(join('images', 'spells', 'rock_pillar_rocks', f'rock_pillar_rocks{randint(0, 5)}.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * WORLD_SCALE, self.image.get_height() * WORLD_SCALE))
        self.rect = self.image.get_rect(center=self.pos)
        self.hitbox = self.rect
        self.rot_dir = -1 if dir.x > 0 else 1
        self.max_height = 32 * WORLD_SCALE
        self.height_timer = 0
        self.fade_time = 0.1
        self.decel = 0.4 * speed * self.life_timer
        self.particle_emitter: ParticleEmitter
        self.pierce = 0

        match self.type:
            case 'star':
                self.particle_emitter = ParticleEmitter(self.groups, self.pos, RockWallRocksStar, -self.dir, 0.05)
            case 'fire':
                self.particle_emitter = ParticleEmitter(self.groups, self.pos, RockWallRocksFire, -self.dir, 0.05)
            case 'rock':
                self.particle_emitter = ParticleEmitter(self.groups, self.pos, RockWallRocksRock, -self.dir, 0.2)

        self.particle_emitter._layer = 13

    def move(self, dt):
        self.pos += self.speed * self.dir * dt
        height = self.max_height * self.life_timer * (-math.fabs(math.cos(6 * self.height_timer)))
        self.height_timer += dt
        self.rect.center = self.pos + pygame.Vector2(0, height)
        self.hitbox = self.rect
        self.particle_emitter.pos = self.pos.copy() + pygame.Vector2(0, height)

    def collision(self):
        for sprite in self.enemy_sprites:
            if sprite.rect.colliderect(self.hitbox) and sprite.health.i_frame_timer <= 0:
                self.pierce += 1
                match self.type:
                    case 'star':
                        apply_damage(sprite, 1, 50, sprite.pos - self.pos, 10)
                        if self.pierce == 4:
                            self.kill()
                    case 'fire':
                        apply_damage(sprite, 1, 50, sprite.pos - self.pos, 10)
                        if self.pierce == 3:
                            self.kill()
                    case 'rock':
                        apply_damage(sprite, 1, 50, sprite.pos - self.pos, 10)
                        if self.pierce == 2:
                            self.kill()

    def update(self, dt):
        self.move(dt)
        self.collision()

        self.image = pygame.transform.rotate(self.image, self.rot_dir)
        self.speed -= self.decel * dt

        if self.life_timer < self.fade_time:
            self.image.set_alpha(max(self.life_timer / self.fade_time, 0) * 255)

        if self.life_timer > 0:
            self.life_timer -= dt
        else:
            self.kill()

    def kill(self):
        self.particle_emitter.kill()
        super().kill()


class HealthDrain(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)
        self.groups = groups
        self.player = player
        self.offset = pygame.Vector2(0, 0)
        self.height = 0.8 * TILE_SIZE
        self.amplitude = 0.2 * TILE_SIZE
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=self.player.pos)
        self.hitbox = self.rect
        self.sounds = {}
        load_audio(self, "spells/health_drain", 0.1)
        play(self, "create", play_all=True)
        self.particle_emitter1 = ParticleEmitter(self.groups, self.player.pos - (self.amplitude, 0), HealingParticle, dir=pygame.Vector2(0, 1), cooldown_timer_max=0.008)
        self.particle_emitter2 = ParticleEmitter(self.groups, self.player.pos + (self.amplitude, 0), HealingParticle, dir=pygame.Vector2(0, 1), cooldown_timer_max=0.008)
        self.particle_emitter1._layer = 14
        self.particle_emitter2._layer = 13
        self.offset_timer = -0.05
        self.offset_timer_max = 0.4
        self.player.health_bar.heal(2.0)

    def update(self, dt):
        self.offset = pygame.Vector2(2 * self.amplitude * math.cos(self.offset_timer / self.offset_timer_max * 2 * math.pi), (-self.height) * self.offset_timer / self.offset_timer_max)
        self.particle_emitter1.pos = self.player.pos + self.offset
        self.particle_emitter2.pos = self.player.pos + (-self.offset.x, self.offset.y)

        if self.offset_timer > self.offset_timer_max / 2:
            self.particle_emitter1._layer = 13
            self.particle_emitter2._layer = 14

        if self.offset_timer < self.offset_timer_max:
            self.offset_timer += dt
        else:
            self.particle_emitter1.kill()
            self.particle_emitter2.kill()
            self.kill()


class DragonsBreath(pygame.sprite.Sprite):
    def __init__(self, groups, enemy_sprites, collision_sprites, player, dir):
        super().__init__(groups)
        self.groups = groups
        self.enemy_sprites = enemy_sprites
        self.collision_sprites = collision_sprites
        self.player = player
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=self.player.pos)
        self.hitbox = self.rect
        self.sounds = {}
        load_audio(self, "spells/dragons_breath", 0.6)
        play(self, "start")
        self.sounds["loop"][0].set_volume(0.25)
        play(self, "loop", repeat=-1)
        self.fire_timer = 0
        self.fire_timer_max = 0.1
        self.last_dir = dir
        self.distance = 50
        self.angle = 45

    def update(self, dt):
        if self.player.direction.length() != 0:
            self.last_dir = self.player.direction.normalize()

        if self.fire_timer > 0:
            self.fire_timer -= dt
        else:
            self.fire_timer = self.fire_timer_max
            dbf = DragonsBreathFire(self.groups, self.enemy_sprites, self.collision_sprites, self.player, self.player.pos.copy() + self.last_dir * self.distance + pygame.Vector2(0, -30), self.last_dir.rotate(math.sin(self.player.fire_timer / self.player.fire_timer_max * 6 * math.pi) * self.angle))
            dbf._layer = 13

    def kill(self):
        play(self, "end")
        pause(self, "loop")
        super().kill()

class DragonsBreathFire(pygame.sprite.Sprite):
    def __init__(self, groups, enemy_sprites, collision_sprites, player, pos, dir):
        super().__init__(groups)
        self.enemy_sprites = enemy_sprites
        self.collision_sprites = collision_sprites
        self.player = player
        self.pos = pos
        self.dir = dir
        self.frames = []
        self.load_images()
        self.image = pygame.image.load(join('images', 'spells', 'dragons_breath', 'dragons_breath0.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (2 * TILE_SIZE, 2 * TILE_SIZE))
        self.image = pygame.transform.rotate(self.image, self.dir.angle_to(pygame.Vector2(0, -1)))
        self.image.set_alpha(196)
        self.frame_index = 0
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.life_timer_max = 0.3
        self.life_timer = self.life_timer_max
        self.fade_timer_max = 0.2
        self.fade_timer = self.fade_timer_max
        self.base_speed = randrange(600, 700)
        self.speed_min = randrange(150, 200)
        self.fade = False

    def load_images(self):
        for folder_path, _, file_names in walk(join('images', 'spells', 'dragons_breath')):
            for file_name in sorted(file_names, key=lambda name: int(sub(f'[^0-9]', '', name))):
                full_path = join(folder_path, file_name)
                surf = pygame.image.load(full_path).convert_alpha()
                surf = pygame.transform.scale(surf, (2 * TILE_SIZE, 2 * TILE_SIZE))
                surf = pygame.transform.rotate(surf, self.dir.angle_to(pygame.Vector2(0, -1)))
                surf.set_alpha(160)
                self.frames.append(surf)

    def collision(self):
        for sprite in self.enemy_sprites:
            if sprite.rect.colliderect(self.hitbox):
                apply_damage(sprite, 1, 50, sprite.pos - self.pos, 10)
                return True

        for sprite in self.collision_sprites:
            if isinstance(sprite, RockWall) and sprite.hitbox.colliderect(self.hitbox):
                sprite.damage(1, 'fire', (sprite.pos - self.player.pos + pygame.Vector2(0, 40)).normalize())

        return False

    def move(self, dt):
        self.pos += (self.base_speed - ((self.base_speed - self.speed_min) * (1 - self.life_timer / self.life_timer_max))) * self.dir * dt
        self.rect.center = self.pos
        self.hitbox = self.rect
        if not self.fade and self.collision():
            self.fade = True

    def update(self, dt):
        self.move(dt)

        if self.life_timer > 0:
            self.image = self.frames[math.floor(4 * (1 - self.life_timer / self.life_timer_max))]
            self.life_timer -= dt
            if self.life_timer <= 0:
                self.fade = True

        if self.fade:
            if self.fade_timer > 0:
                self.fade_timer -= dt
                self.image = self.frames[min(math.floor(3 * (1 - self.fade_timer / self.fade_timer_max) + 3), 6)]
                self.image.set_alpha(127 + int(self.fade_timer / self.fade_timer_max * 128))
            else:
                self.kill()
