from random import choice, randrange

import pygame

from settings import *
from plants import Plant
from player import Player
from sprites import *
from groups import *
from user_interface import *
from pytmx.util_pygame import load_pygame
from progress_logic import WaveLogic, WaveAreaTrigger

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Spell_Casting')
        self.clock = pygame.time.Clock()
        self.running = True
        self.update_game = False
        self.player = None
        pygame.mixer_music.load('audio/music/mus_lvl2_awake_loop.mp3')
        pygame.mixer_music.set_volume(music_v)
        pygame.mixer_music.play(loops=-1)

        # groups
        self.start_menu_sprites = pygame.sprite.Group()
        self.pause_menu_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.short_collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.hud_sprites = pygame.sprite.Group()
        self.all_sprites = AllSprites(self.hud_sprites, self.start_menu_sprites, self.pause_menu_sprites)

        StartButton(self.start_menu_sprites, self, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        ResumeButton(self.pause_menu_sprites, self, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        MusicSlider((self.start_menu_sprites, self.pause_menu_sprites), self, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 30))
        self.sfx_slider = SFXSlider((self.start_menu_sprites, self.pause_menu_sprites), self, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 30))
        ExitButton((self.start_menu_sprites, self.pause_menu_sprites), self, (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100))
        self.wave_logic = WaveLogic(self.all_sprites, self.collision_sprites, self.short_collision_sprites, self.enemy_sprites, self.sfx_slider)

    def load_game(self):
        map = load_pygame(join('map_data', 'maps', 'world.tmx'))

        for obj in map.get_layer_by_name('Collisions'):
            sprite = CollisionSprite((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y), (WORLD_SCALE * obj.width, WORLD_SCALE * obj.height), (self.all_sprites, self.short_collision_sprites))
            sprite._layer = 0

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            sprite = Sprite((TILE_SIZE * x, TILE_SIZE * y), image, self.all_sprites)
            sprite._layer = 1

        for x, y, image in map.get_layer_by_name('Tutorial').tiles():
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            sprite = Sprite((TILE_SIZE * x, TILE_SIZE * y), image, self.all_sprites)
            sprite._layer = 2

        for obj in map.get_layer_by_name('Barriers'):
            self.wave_logic.barriers_tiled[obj.index - 1].append(obj)
        self.wave_logic.raise_barriers(2)
        self.wave_logic.raise_barriers(3)

        for obj in map.get_layer_by_name('Plants'):
            plant = Plant((self.all_sprites, self.collision_sprites), obj)
            plant._layer = 13

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(self.all_sprites, self.collision_sprites, self.short_collision_sprites, self.hud_sprites, self.enemy_sprites, self.sfx_slider, (WORLD_SCALE * obj.x, WORLD_SCALE * obj.y))
                self.player._layer = 13
                self.wave_logic.player = self.player
            elif obj.name == 'Enemy':
                self.wave_logic.spawn_positions[obj.index - 1].append((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y))

        for obj in map.get_layer_by_name('Area Triggers'):
            WaveAreaTrigger(self.all_sprites, obj, self.player, self.wave_logic)

    def run(self):
        while self.running:
            # delta time
            dt = self.clock.tick() / 1000

            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.player.set_coyote_time_dash()
                    if event.key == pygame.K_z:
                        self.player.set_coyote_time_cast()

                    if (event.key == pygame.K_p or event.key == pygame.K_ESCAPE) and not self.all_sprites.draw_start_menu:
                        self.all_sprites.draw_pause_menu = not self.all_sprites.draw_pause_menu
                        self.update_game = not self.update_game

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.all_sprites.draw_start_menu:
                        for sprite in self.start_menu_sprites:
                            if hasattr(sprite, 'on_click') and sprite.hitbox.collidepoint(pygame.mouse.get_pos()):
                                sprite.on_click()

                    if self.all_sprites.draw_pause_menu:
                        for sprite in self.pause_menu_sprites:
                            if hasattr(sprite, 'on_click') and sprite.hitbox.collidepoint(pygame.mouse.get_pos()):
                                sprite.on_click()

                if event.type == pygame.MOUSEMOTION:
                    if self.all_sprites.draw_start_menu or self.all_sprites.draw_pause_menu:
                        for sprite in self.start_menu_sprites:
                            if hasattr(sprite, 'on_move'):
                                sprite.on_move()

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.all_sprites.draw_start_menu or self.all_sprites.draw_pause_menu:
                        for sprite in self.start_menu_sprites:
                            if hasattr(sprite, 'on_release'):
                                sprite.on_release()

                if event.type == pygame.QUIT:
                    self.running = False

            # update
            if self.all_sprites.draw_start_menu:
                self.start_menu_sprites.update(dt)
            if self.all_sprites.draw_pause_menu:
                self.pause_menu_sprites.update(dt)
            if self.update_game:
                self.all_sprites.update(dt)
                self.wave_logic.update(dt)

            # draw
            self.display_surface.fill('#457a7d')
            if self.player:
                self.all_sprites.draw(pygame.Vector2(round(self.player.pos.x), round(self.player.pos.y)))
            else:
                self.all_sprites.draw(pygame.Vector2(0, 0))
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
