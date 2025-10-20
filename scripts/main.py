import pygame

from settings import *
from player import Player
from enemies import Bat
from sprites import *
from random import choice
from groups import AllSprites
from pytmx.util_pygame import load_pygame

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Spell_Casting')
        self.clock = pygame.time.Clock()
        self.running = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 3000)
        self.spawn_positions = []

        self.setup()

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for obj in map.get_layer_by_name('Collisions'):
            sprite = Sprite((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y), pygame.Surface((WORLD_SCALE * obj.width, WORLD_SCALE * obj.height)),
                            (self.all_sprites, self.collision_sprites))
            sprite._layer = 0

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            sprite = Sprite((TILE_SIZE * x, TILE_SIZE * y), image, self.all_sprites)
            sprite._layer = 1

        for x, y, image in map.get_layer_by_name('Shadows').tiles():
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            sprite = Sprite((TILE_SIZE * x, TILE_SIZE * y), image, self.all_sprites)
            sprite._layer = 2

        for obj in map.get_layer_by_name('Objects'):
            resized_image = pygame.transform.scale(obj.image, (WORLD_SCALE * obj.width, WORLD_SCALE * obj.height))
            sprite = Sprite((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y), resized_image, self.all_sprites)
            sprite._layer = 13

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y), self.all_sprites, self.enemy_sprites, self.collision_sprites)
                self.player._layer = 13
            elif obj.name == 'Enemy':
                self.spawn_positions.append((WORLD_SCALE * obj.x, WORLD_SCALE * obj.y))

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

                if event.type == self.enemy_event:
                    bat = Bat(choice(self.spawn_positions), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                    bat._layer = 13

                if event.type == pygame.QUIT:
                    self.running = False

            # update 
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(pygame.Vector2(round(self.player.pos.x), round(self.player.pos.y)))
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
