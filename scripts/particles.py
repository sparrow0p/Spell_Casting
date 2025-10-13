from settings import *
from pygame_particles import Particle
from pygame_particles.shape import Circle

class ShootingStarParticle(pygame.sprite.Sprite):
    def __init__(self, pos, groups, dir):
        super().__init__(groups)
        self.pos = pos
        self.dir = dir
        self.particle = Particle(
            center_x=pos[0],
            center_y=pos[1],
            objects_count=10,
            life_seconds=5,
            fade_seconds=1,
            life_iterations=5,
            fade_iterations=1,
            size=100,
            speed=5,
            rotate_angle=5,
            width=100,
            shape_cls=Circle,
        )
