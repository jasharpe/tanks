import constants
import explosion
import pygame
from interpolation import quadratic_bi, interpolate_colors, quadratic, reverse_linear
from collision_circle import CollisionCircle

class Mine(pygame.sprite.Sprite):
  def __init__(self, p, owner):
    pygame.sprite.Sprite.__init__(self)
    
    self.position = p
    self.owner = owner
    self.age = 0
    self.dead = False
    self.exploding = False
    self.doots = 0

    self.collision_circle = CollisionCircle(self, constants.MINE_DETECTION_RATIO)
    self.update_graphics()

  def swell_and_explode(self):
    self.exploding = True
    self.explosion_countdown = constants.MINE_EXPLOSION_DURATION

  def get_explosion(self):
    return explosion.BigExplosion(self.position, True)

  def die(self):
    self.owner.mines -= 1
    self.dead = True

  def sound(self):
    for i in xrange(self.doots, constants.MINE_DOOTS):
      if self.age > i * constants.MINE_NON_ACTIVE_PULSE_PERIOD:
        self.doots += 1
        if i == constants.MINE_DOOTS - 1:
          return ("long_doot", 0.4)
        else:
          return ("short_doot", 0.4)
    return (None, None)

  def expire(self, level):
    if self.exploding and self.explosion_countdown == 0:
      level.explosions.add(self.get_explosion())

  def expired(self):
    return self.dead

  def update(self, delta):
    if self.exploding:
      self.explosion_countdown = max(self.explosion_countdown - delta, 0)
      if self.explosion_countdown == 0:
        self.die()
    self.age += delta
    if self.age > constants.MINE_MAX_AGE and not self.exploding:
      self.swell_and_explode()
    self.update_graphics()
    self.collision_circle.update()

  def active(self):
    return self.age > constants.MINE_ACTIVE_AGE

  def update_graphics(self):
    if self.exploding:
      t = quadratic(self.explosion_countdown, constants.MINE_EXPLOSION_DURATION)
      ratio = reverse_linear(t, constants.MINE_SIZE_RATIO, constants.MINE_MAX_SIZE_RATIO)
      size = int(round(constants.TILE_SIZE * ratio))
    else:
      size = int(round(constants.TILE_SIZE * constants.MINE_SIZE_RATIO))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    center = self.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    r = quadratic_bi(self.age % constants.MINE_COLOR_MODULATION_TIME, constants.MINE_COLOR_MODULATION_TIME)
    c = interpolate_colors(r, constants.MINE_COLOR_ONE, constants.MINE_COLOR_TWO)
    if self.exploding:
      val = min(constants.MINE_EXPLOSION_DURATION / 2, constants.MINE_EXPLOSION_DURATION - self.explosion_countdown)
      t = quadratic(val, constants.MINE_EXPLOSION_DURATION / 2)
      c = interpolate_colors(t, constants.MINE_EXPLODING_COLOR, c)
    if not self.active():
      mod_age = self.age % constants.MINE_NON_ACTIVE_PULSE_PERIOD
      if mod_age < constants.MINE_NON_ACTIVE_PULSE_LENGTH:
        c = constants.MINE_PULSE_COLOR_ONE
      else:
        c = constants.MINE_PULSE_COLOR_TWO
    pygame.draw.circle(self.image, c, image_center, int(round(self.image.get_width() / 2)))
    self.rect = self.image.get_rect(center=center)
