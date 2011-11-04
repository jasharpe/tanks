import pygame, os
import constants
from geometry import Vector, Point, Line

class Shockwave(pygame.sprite.Sprite):
  def __init__(self, position):
    super(Shockwave, self).__init__()
    
    self.original = pygame.image.load(os.path.join(constants.DATA_DIR, "shock.png")).convert_alpha()
    self.image = self.original
    self.age = 0

    self.position = position
    self.update_graphics()

  def update(self, delta):
    self.age += delta
    if self.age < constants.SHOCKWAVE_DURATION:
      self.update_graphics()

  def expired(self):
    return self.age > constants.SHOCKWAVE_DURATION

  def update_graphics(self):
    # interpolate from 0 to 1
    t = float(self.age) / constants.SHOCKWAVE_DURATION
    # interpolate from 0 to 1 to 0 so the shockwave explodes then shrinks
    a = 1 - 2 * abs(t - 0.5)
    multiplier = a * constants.SHOCKWAVE_MAX_RATIO + (1 - a) * constants.SHOCKWAVE_MIN_RATIO
    radius = int(round(multiplier * constants.TILE_SIZE))
    self.image = pygame.transform.smoothscale(self.original, (radius, radius))
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))

class Explosion(pygame.sprite.Sprite):
  def __init__(self, position, explosion_max_ratio=constants.EXPLOSION_MAX_RATIO, explosion_min_ratio=constants.EXPLOSION_MIN_RATIO, damages=False):
    pygame.sprite.Sprite.__init__(self)

    self.original = pygame.image.load(os.path.join(constants.DATA_DIR, "explosion.png")).convert_alpha()
    self.image = self.original
    self.age = 0

    self.explosion_max_ratio = explosion_max_ratio
    self.explosion_min_ratio = explosion_min_ratio

    self.damages = damages
    # ensure that each tank can only be damaged once by this explosion
    self.damaged = set()

    self.position = position
    self.update_graphics()

  def expired(self):
    return self.age > constants.EXPLOSION_DURATION

  def update(self, delta):
    self.age += delta
    if self.age < constants.EXPLOSION_DURATION:
      self.update_graphics()

  def update_graphics(self):
    # interpolate from 0 to 1
    t = float(self.age) / constants.EXPLOSION_DURATION
    # interpolate from 0 to 1 to 0 so the shockwave explodes then shrinks
    a = 1 - 2 * abs(t - 0.5)
    #a = t
    multiplier = a * self.explosion_max_ratio + (1 - a) * self.explosion_min_ratio
    radius = int(round(multiplier * constants.TILE_SIZE))
    self.image = pygame.transform.smoothscale(self.original, (radius, radius))
    self.image.set_alpha(255 * a)
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))

class BigExplosion(Explosion):
  def __init__(self, position, damages=False):
    Explosion.__init__(self, position, constants.BIG_EXPLOSION_MAX_RATIO, constants.BIG_EXPLOSION_MIN_RATIO, damages)
