import pygame
import constants
from geometry import *
from interpolation import *

class Powerup(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)

    self.position = Point(x + 0.5, y + 0.5)
    self.picked_up = False

    self.colour_time = 0

    self.done = False
    self.taken = False
    self.target = None
    self.speed = 0.0
    self.explode_time = constants.POWERUP_EXPLODE_TIME

    self.update_graphics()
  
  def take(self, tank):
    self.taken = True
    self.target = tank

  def update_graphics(self):
    t = linear(self.explode_time, constants.POWERUP_EXPLODE_TIME)
    size = int(round(constants.TILE_SIZE * constants.POWERUP_SIZE_RATIO * t))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(pygame.Color(0, 0, 0, 0))
    center = self.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    r = quadratic_bi(self.colour_time, constants.POWERUP_COLOUR_MODULATION_TIME)
    c = interpolate_colours(r, constants.POWERUP_COLOR_ONE, constants.POWERUP_COLOR_TWO)
    pygame.draw.circle(self.image, c, image_center, int(round(self.image.get_width() / 2)))
    self.rect = self.image.get_rect(center=center)

  def update(self, delta):
    self.colour_time += delta
    while self.colour_time > constants.POWERUP_COLOUR_MODULATION_TIME:
      self.colour_time -= constants.POWERUP_COLOUR_MODULATION_TIME
    if self.taken:
      if self.explode_time == 0:
        self.done = True
      self.explode_time = max(0, self.explode_time - delta)
    if self.target is not None:
      d = (self.target.position - self.position).normalize()
      self.speed = self.speed + constants.POWERUP_ACCEL * (delta / 1000.0)
      self.position = self.position.translate(self.speed * d * (delta / 1000.0))
    self.update_graphics()
