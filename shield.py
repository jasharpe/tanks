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

    self.update_graphics()

  def update_graphics(self):
    t = interpolation.quadratic_bi(self.pulse_time, constants.SHIELD_PULSE_PERIOD)
    # pulsating (breathing)
    #size = int(round(interpolation.reverse_linear(t, 1.1, 1.0) * interpolation.linear(self.growth_time, constants.SHIELD_GROWTH_TIME) * constants.TILE_SIZE * constants.SHIELD_RADIUS_RATIO * 2))
    size = int(round(interpolation.linear(self.growth_time, constants.SHIELD_GROWTH_TIME) * constants.TILE_SIZE * constants.SHIELD_RADIUS_RATIO * 2))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(pygame.Color(0, 0, 0, 0))
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)

    circle_size = int(round(self.image.get_width() / 2))
    c = interpolation.interpolate_colours(t, constants.SHIELD_COLOUR, constants.SHIELD_COLOUR_TWO)
    #c.b += int(round(100.0 * t))
    pygame.draw.circle(self.image, c, image_center, circle_size)
    
    # pulse
    #pulse_size = int(round(interpolation.quadratic(self.pulse_time, constants.SHIELD_PULSE_PERIOD) * constants.TILE_SIZE * constants.SHIELD_RADIUS_RATIO))
    #pygame.draw.circle(self.image, constants.SHIELD_PULSE_COLOUR, image_center, pulse_size, min(pulse_size, 2))
    
    self.rect = self.image.get_rect(center=self.tank.position.scale(constants.TILE_SIZE))

  def update(self, delta):
    self.pulsed = False
    self.pulse_time = self.pulse_time + delta
    if self.pulse_time > constants.SHIELD_PULSE_PERIOD:
      self.pulsed = True
      self.pulse_time %= constants.SHIELD_PULSE_PERIOD
    self.growth_time = min(self.growth_time + delta, constants.SHIELD_GROWTH_TIME)
    self.update_graphics()
