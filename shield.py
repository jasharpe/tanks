import pygame, constants, utils
import interpolation

class Pulse:
  def __init__(self):
    self.age = 0

  def update(self, delta):
    self.age += delta

class Shield(pygame.sprite.Sprite):
  def __init__(self, tank):
    pygame.sprite.Sprite.__init__(self)

    self.tank = tank

    self.pulsed = False
    self.pulse_time = 0
    self.growth_time = 0

    self.pulses = set()
    self.pulses.add(Pulse())

    self.active = False
    self.dead = False
    self.dead_time = 0
    self.to_remove = False

    self.update_graphics()

  def expired(self):
    return self.to_remove

  def expire(self, level):
    self.tank.shields.remove(self)

  def die(self):
    self.active = False
    self.dead = True

  def update_graphics(self):
    t = interpolation.quadratic_bi(self.pulse_time, constants.SHIELD_PULSE_PERIOD)
    size = int(round((1 - interpolation.linear(self.dead_time, constants.SHIELD_DEATH_TIME)) * interpolation.linear(self.growth_time, constants.SHIELD_GROWTH_TIME) * constants.TILE_SIZE * constants.SHIELD_RADIUS_RATIO * 2))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)

    circle_size = int(round(self.image.get_width() / 2))
    c = interpolation.interpolate_colors(t, constants.SHIELD_COLOR, constants.SHIELD_COLOR_TWO)
    pygame.draw.circle(self.image, c, image_center, circle_size)
    
    self.rect = self.image.get_rect(center=self.tank.position.scale(constants.TILE_SIZE))

  def update(self, delta):
    self.pulsed = False
    self.pulse_time = self.pulse_time + delta
    if self.pulse_time > constants.SHIELD_PULSE_PERIOD:
      self.pulsed = True
      self.pulse_time %= constants.SHIELD_PULSE_PERIOD
    self.growth_time = min(self.growth_time + delta, constants.SHIELD_GROWTH_TIME)
    if self.growth_time is constants.SHIELD_GROWTH_TIME:
      self.active = True
    if self.dead:
      self.dead_time = min(self.dead_time + delta, constants.SHIELD_DEATH_TIME)
      if self.dead_time is constants.SHIELD_DEATH_TIME:
        self.to_remove = True
    self.update_graphics()
