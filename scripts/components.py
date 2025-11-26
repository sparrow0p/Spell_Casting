from settings import *

class HealthComponent:
    def __init__(self, parent, max_health, i_frame_timer=0.3):
        self.parent = parent
        self.max_health = max_health
        self.health = max_health
        self.i_frame_timer_max = i_frame_timer
        self.i_frame_timer = 0

    def damage(self, damage_val, kb_strength, kb_dir, max_height):
        if self.i_frame_timer <= 0 and self.parent.state != 'dead' and self.parent.state != 'thrown':
            self.i_frame_timer = self.i_frame_timer_max
            self.health -= damage_val

            if kb_strength and kb_dir:
                self.parent.state = 'thrown'
                self.parent.thrown_dir = kb_dir
                self.parent.max_height = max_height
                self.parent.thrown_timer = kb_strength / self.parent.thrown_speed
                self.parent.thrown_timer_start = self.parent.thrown_timer
                self.parent.frame_index = 0
            elif self.health <= 0:
                self.parent.die()

    def hit_effect(self):
        if self.i_frame_timer > self.i_frame_timer_max * 0.8:
            mask = pygame.mask.from_surface(self.parent.image)
            mask_surf = mask.to_surface()
            mask_surf.set_colorkey((0, 0, 0))
            surf_w, surf_h = mask_surf.get_size()
            for x in range(surf_h):
                for y in range(surf_w):
                    if mask_surf.get_at((x, y))[0] == 255:
                        mask_surf.set_at((x, y), (230, 30, 30))
            self.parent.image = mask_surf

def apply_damage(sprite, damage_val, kb_strength=None, kb_dir=None, max_height=100):
    if hasattr(sprite, "health"):
        sprite.health.damage(damage_val, kb_strength, kb_dir, max_height)
