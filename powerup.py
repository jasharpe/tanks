import pygame
import constants, math
from geometry import *
from interpolation import *
from shield import Shield
from particle import PowerupParticle

class Powerup(pygame.sprite.Sprite):
  def __init__(self, p):
    pygame.sprite.Sprite.__init__(self)

    self.position = p
    self.picked_up = False

    self.color_time = 0

    self.done = False
    self.taken = False
    self.target = None
    self.speed = 0.0
    self.explode_time = constants.POWERUP_EXPLODE_TIME

    self.update_graphics()
 
  def expired(self):
    return self.done

  def expire(self, level):
    level.play_sound("powerup", 0.2)
    level.powerups.remove(self)

    self.do(level, self.target)
    self.target.taking.remove(self)
    for i in xrange(0, constants.POWERUP_PARTICLES):
      angle = i * 2 * math.pi / constants.POWERUP_PARTICLES
      d = Vector(angle)
      p = self.position
      c = self.color_time
      particle = PowerupParticle(p, d, c)
      level.powerup_particles.add(particle)

  def take(self, tank):
    self.taken = True
    self.target = tank

  def update_graphics(self):
    t = linear(self.explode_time, constants.POWERUP_EXPLODE_TIME)
    size = int(round(constants.TILE_SIZE * constants.POWERUP_SIZE_RATIO * t))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    center = self.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    r = quadratic_bi(self.color_time, constants.POWERUP_COLOR_MODULATION_TIME)
    c = interpolate_colors(r, constants.POWERUP_COLOR_ONE, constants.POWERUP_COLOR_TWO)
    pygame.draw.circle(self.image, c, image_center, int(round(self.image.get_width() / 2)))
    self.rect = self.image.get_rect(center=center)

  def update(self, delta):
    self.color_time += delta
    while self.color_time > constants.POWERUP_COLOR_MODULATION_TIME:
      self.color_time -= constants.POWERUP_COLOR_MODULATION_TIME
    if self.taken:
      if self.explode_time == 0:
        self.done = True
      self.explode_time = max(0, self.explode_time - delta)
    if self.target is not None:
      d = (self.target.position - self.position).normalize()
      self.speed = self.speed + constants.POWERUP_ACCEL * (delta / 1000.0)
      self.position = self.position.translate(self.speed * d * (delta / 1000.0))
    self.update_graphics()

class ShieldPowerup(Powerup):
  def do(self, level, tank):
    shield = Shield(tank)
    level.shields.add(shield)
    tank.shields.append(shield)

  def can_take(self, tank):
    if tank.shields:
      return False
    for powerup in tank.taking:
      if type(powerup) is type(self):
        return False
    return True

class RepairPowerup(Powerup):
  def do(self, level, tank):
    tank.heal()

  def can_take(self, tank):
    if tank.health == constants.TANK_HEALTH:
      return False
    for powerup in tank.taking:
      if type(powerup) is type(self):
        return False
    return True

class SplashPowerup(Powerup):
  def do(self, level, tank):
    tank.activate_splash()

  def can_take(self, tank):
    if tank.has_splash():
      return False
    for powerup in tank.taking:
      if type(powerup) is type(self):
        return False
    return True
