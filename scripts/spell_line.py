import pygame

from settings import *

S_GIRTH = 3
E_GIRTH = 10

class SpellLine(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.groups = groups
        self.player = player
        self.spell_line_shapes = []
        self.current_line_polygon = None
        self.current_line_circle = None
        self.previous_line_polygon = None
        self.is_first_line = True

    def start_drawing(self):
        if self.is_first_line:
            circle = SpellLineCircle(self.player, self.groups)
            circle._layer = 10
            self.spell_line_shapes.append(circle)

        if self.current_line_circle:
            self.current_line_circle.is_growing = True
        if self.current_line_polygon:
            self.current_line_polygon.end_pos = self.player.pos.copy()
            self.current_line_polygon.is_growing = True

        polygon = SpellLinePolygon(self.player, self.is_first_line, self.groups)
        polygon._layer = 10
        if self.current_line_polygon:
            self.previous_line_polygon = self.current_line_polygon
        self.current_line_polygon = polygon
        self.spell_line_shapes.append(polygon)

        self.is_first_line = False

    def stop_drawing(self):
        if self.current_line_circle:
            self.current_line_circle.is_growing = False
        if self.previous_line_polygon:
            self.previous_line_polygon.is_growing = False
        self.current_line_polygon.is_drawing = False

        circle = SpellLineCircle(self.player, self.groups)
        circle._layer = 10
        self.current_line_circle = circle
        self.spell_line_shapes.append(circle)

    def clear_all(self):
        for shape in self.spell_line_shapes:
            shape.kill()
        self.spell_line_shapes.clear()
        self.is_first_line = True

class SpellLinePolygon(pygame.sprite.Sprite):
    def __init__(self, player, is_first_line, groups):
        super().__init__(groups)
        self.player = player
        self.is_first_line = is_first_line
        self.max_size = self.player.dash_speed * self.player.dash_timer_max
        self.image = pygame.Surface((4 * self.max_size, 4 * self.max_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.player.pos.copy())
        self.hitbox = self.rect
        self.start_pos = self.rect.center
        self.end_pos = self.rect.center
        self.dir = self.player.dash_dir
        self.start_girth = S_GIRTH
        self.end_girth = S_GIRTH
        self.offset = (2 * self.max_size, 2 * self.max_size)
        self.is_drawing = True
        self.is_growing = False

    def update(self, dt):
        if self.is_drawing:
            if not self.is_first_line:
                self.start_girth = S_GIRTH + (E_GIRTH - S_GIRTH) * min(((self.player.dash_timer_max - self.player.dash_timer) / self.player.dash_timer_max), 1)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, (255, 255, 255),
                                (self.offset + self.dir.rotate(-90).normalize() * self.start_girth,
                                 self.offset + self.dir.rotate(90).normalize() * self.start_girth,
                                 self.offset + self.player.pos - self.start_pos + self.dir.rotate(90).normalize() * self.end_girth,
                                 self.offset + self.player.pos - self.start_pos + self.dir.rotate(-90).normalize() * self.end_girth))

        if self.is_growing:
            self.end_girth = S_GIRTH + (E_GIRTH - S_GIRTH) * min(((self.player.dash_timer_max - self.player.dash_timer) / self.player.dash_timer_max), 1)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, (255, 255, 255),
                                (self.offset + self.dir.rotate(-90).normalize() * self.start_girth,
                                 self.offset + self.dir.rotate(90).normalize() * self.start_girth,
                                 self.offset + self.end_pos - self.start_pos + self.dir.rotate(
                                     90).normalize() * self.end_girth,
                                 self.offset + self.end_pos - self.start_pos + self.dir.rotate(
                                     -90).normalize() * self.end_girth))

class SpellLineCircle(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.player = player
        self.radius = S_GIRTH
        self.image = pygame.Surface((2 * E_GIRTH, 2 * E_GIRTH), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (E_GIRTH, E_GIRTH), self.radius)
        self.rect = self.image.get_rect(center=self.player.pos)
        self.hitbox = self.rect
        self.is_growing = False

    def update(self, dt):
        if self.is_growing:
            self.radius = S_GIRTH + (E_GIRTH - S_GIRTH) * min(((self.player.dash_timer_max - self.player.dash_timer) / self.player.dash_timer_max), 1)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, (255, 255, 255), (self.radius, self.radius), self.radius)
