import pygame
import constants
from geometry import Vector, Point, Line

class Shockwave(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super(Shockwave, self).__init__()
    
    self.original = pygame.image.load("shock.png").convert_alpha()
    self.image = self.original
    self.age = 0

    self.position = Point(x, y)
    self.update_graphics()

  def update(self, delta):
    self.age += delta
    if self.age < constants.SHOCKWAVE_DURATION:
      self.update_graphics()

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
  def __init__(self, x, y):
    super(Explosion, self).__init__()

  
