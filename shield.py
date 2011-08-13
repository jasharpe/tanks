import pygame, constants

class Shield(pygame.sprite.Sprite):
  def __init__(self, tank):
    pygame.sprite.Sprite.__init__(self)

    self.tank = tank

    self.pulsed = False
    self.pulse_time = 0

    self.update_graphics()

  def update_graphics(self):
    size = int(round(constants.TILE_SIZE * constants.SHIELD_RADIUS_RATIO * 2))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(pygame.Color(0, 0, 0, 0))
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    pygame.draw.circle(self.image, constants.SHIELD_COLOUR, image_center, int(round(self.image.get_width() / 2)))
    self.rect = self.image.get_rect(center=self.tank.position.scale(constants.TILE_SIZE))

  def update(self, delta):
    self.pulsed = False
    self.pulse_time = self.pulse_time + delta
    if self.pulse_time > constants.SHIELD_PULSE_PERIOD:
      self.pulsed = True
      self.pulse_time %= constants.SHIELD_PULSE_PERIOD
    self.update_graphics()
