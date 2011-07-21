import pygame, math
import constants
from geometry import Vector, Point
from bullet import Bullet

class Tank(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)

    self.original = pygame.Surface([constants.TILE_SIZE * constants.TANK_SIZE_RATIO, constants.TILE_SIZE * constants.TANK_SIZE_RATIO], flags=pygame.SRCALPHA)
    self.original.fill(constants.TANK_COLOR)
    self.image = self.original
    self.rect = self.image.get_rect()
    
    # current coordinates of the centre of the tank
    # starts at + 0.5 so that it is in the middle of its start tile
    self.position = Point(x + 0.5, y + 0.5)
    self.old_position = self.position
    # current direction of the tank, in radians
    self.direction = 0.0
    self.old_direction = self.direction
    # speed of the tank
    self.speed = 0.0

  def revert(self):
    self.position = self.old_position
    self.direction = self.old_direction
    self.speed = 0.0
    self.update_graphics()
    
  def update(self, delta):
    self.old_position = self.position
    self.position = self.position.translate(((delta / 1000.0) * self.speed) * Vector(math.cos(self.direction), math.sin(self.direction)).normalize())
    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.transform.rotate(self.original, -self.direction * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))
    #self.rect.center = (self.position.x, self.position.y)
  
  def accelerate(self, delta):
    self.speed += constants.ACCEL_SPEED * (delta / 1000.0)
    if self.speed < 0:
      self.neutral(delta)
    self.speed = min(constants.MAX_SPEED, self.speed)

  def decelerate(self, delta):
    self.speed -= constants.DECEL_SPEED * (delta / 1000.0)
    if self.speed > 0:
      self.neutral(delta)
    self.speed = max(-constants.MAX_SPEED, self.speed)

  def neutral(self, delta):
    if self.speed > 0:
      self.speed -= constants.NEUTRAL_SPEED * (delta / 1000.0)
      if self.speed < 0.01:
        self.speed = 0
    elif self.speed < 0:
      self.speed += constants.NEUTRAL_SPEED * (delta / 1000.0)
      if self.speed > -0.01:
        self.speed = 0

  def turn_left(self, delta):
    self.old_direction = self.direction
    self.direction -= 2 * math.pi * delta / (constants.TANK_TURNING_SPEED * 1000.0)
    if self.direction < -math.pi:
      self.direction += 2 * math.pi

  def turn_right(self, delta):
    self.old_direction = self.direction
    self.direction += 2 * math.pi * delta / (constants.TANK_TURNING_SPEED * 1000.0)
    if self.direction > math.pi:
      self.direction -= 2 * math.pi

class Turret(pygame.sprite.Sprite):
  def __init__(self, tank):
    pygame.sprite.Sprite.__init__(self)

    self.original = pygame.transform.smoothscale(pygame.image.load("turret.png").convert_alpha(), (int(round(constants.TURRET_LENGTH_RATIO * constants.TILE_SIZE)), int(round(constants.TURRET_WIDTH_RATIO * constants.TILE_SIZE))))
    self.image = self.original
    self.rect = self.image.get_rect()
    self.direction = 0.0

    self.tank = tank

  # creates and returns a Bullet starting at the end of the Turret's
  # barrel and going in the direction of the barrel.
  def fire(self):
    origin = self.tank.position.translate(Vector(constants.TURRET_LENGTH_RATIO / 2, 0)).rotate_about(self.direction + self.tank.direction, self.tank.position)
    return Bullet(origin.x, origin.y, self.direction + self.tank.direction)

  # turn towards target point
  def turn(self, delta, target):
    # target direction
    d = target - self.tank.position
    # target angle
    t_a = math.atan2(d.y, d.x)
    # current angle
    c_a = self.direction + self.tank.direction
    difference = t_a - c_a
    while difference < -math.pi:
      difference += 2 * math.pi
    while difference > math.pi:
      difference -= 2 * math.pi

    if difference > 0:
      # turn right
      self.direction += min(2 * math.pi * delta / (constants.TURRET_TURNING_SPEED * 1000.0), difference)
    elif difference < 0:
      # turn left
      self.direction -= min(2 * math.pi * delta / (constants.TURRET_TURNING_SPEED * 1000.0), -difference)

  def update(self, delta):
    self.image = pygame.transform.rotate(self.original, -(self.direction + self.tank.direction) * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=self.tank.rect.center)
