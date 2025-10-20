import pygame.sprite

from settings import *

class ParticleEmitter(pygame.sprite.Sprite):
    def __init__(self, groups, particle, pos, dir):
        self.particle = particle
        self.pos = pos
        self.particle.dir = dir

class BaseParticle(pygame.sprite.Sprite):
    def __init__(self, groups, pos: pygame.Vector2, object_count=1, life_seconds=2.0, fade_seconds=1.0, shape=3,
                 size=10.0, dir=0.0, max_dir_angle=0.0, start_speed_range=(0.0, 0.0), max_speed_range=(0.0, 0.0),
                 acc_range=(0.0, 0.0), start_rot_range=(0.0, 0.0), start_rot_speed_range=(0.0, 0.0), min_rot_speed_range=(0.0, 0.0),
                 max_rot_speed_range=(0.0, 0.0), rot_acc_range=(0.0, 0.0)):
        super().__init__(groups)
        self.pos = pos
        self.object_count = object_count
        self.life_seconds = life_seconds
        self.fade_seconds = fade_seconds
        self.shape = shape
        self.size = size
        self.dir = dir
        self.max_dir_angle = max_dir_angle
        self.start_speed_range = start_speed_range
        self.max_speed_range = max_speed_range
        self.acc_range = acc_range
        self.start_rot_range = start_rot_range
        self.start_rot_speed_range = start_rot_speed_range
        self.min_rot_speed_range = min_rot_speed_range
        self.max_rot_speed_range = max_rot_speed_range
        self.rot_acc_range = rot_acc_range

        def make_regular_polygon(numSides, tiltAngle, x, y, radius):
            pts = []
            for i in range(numSides):
                x = x + radius * math.cos(tiltAngle + math.pi * 2 * i / numSides)
                y = y + radius * math.sin(tiltAngle + math.pi * 2 * i / numSides)
                pts.append([int(x), int(y)])
        # pygame.draw.polygon(surf, color, pts)

class DashParticle(BaseParticle):
    def __init__(self, groups, pos, dir):
        super().__init__(groups, pos, 1, 1, 0.5, 3, 10, dir, 15, (100, 200), (100, 200), 0, (0, 120))
