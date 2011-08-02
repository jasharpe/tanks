import pygame, math, random
import constants
from geometry import Vector, Point, Line, ORIGIN
from bullet import Bullet

class Tank(pygame.sprite.Sprite):
  def __init__(self, x, y, color=constants.TANK_COLOR):
    pygame.sprite.Sprite.__init__(self)

    self.original = pygame.Surface([constants.TILE_SIZE * constants.TANK_SIZE_RATIO, constants.TILE_SIZE * constants.TANK_SIZE_RATIO], flags=pygame.SRCALPHA)
    self.original.fill(color)
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

    self.cooldown = 0

    self.bullets = 0

  # this returns the tank to its position before the last update()
  # call. It is important that this be idempotent.
  def revert(self):
    self.position = self.old_position
    self.direction = self.old_direction
    self.speed = 0.0
    self.update_graphics()
    
  def update(self, delta):
    self.cooldown -= delta
    self.cooldown = max(self.cooldown, 0)
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

  def get_sides(self):
    half_width = constants.TANK_SIZE_RATIO / 2
    half_height = constants.TANK_SIZE_RATIO / 2
    minus_center = ORIGIN - self.position
    plus_center = self.position - ORIGIN
    back_left = self.position.translate(Vector(-half_width, -half_height)).translate(minus_center).rotate(self.direction).translate(plus_center)
    front_left = self.position.translate(Vector(half_width, -half_height)).translate(minus_center).rotate(self.direction).translate(plus_center)
    back_right = self.position.translate(Vector(-half_width, half_height)).translate(minus_center).rotate(self.direction).translate(plus_center)
    front_right = self.position.translate(Vector(half_width, half_height)).translate(minus_center).rotate(self.direction).translate(plus_center)
    front = Line(front_left, front_right)
    back = Line(back_left, back_right)
    left = Line(back_left, front_left)
    right = Line(back_right, front_right)
    return [front, back, left, right]
    
  def collides_with_tank(self, tank):
    if not pygame.sprite.collide_rect(self, tank):
      return False

    this_sides = self.get_sides()
    other_sides = tank.get_sides()
    for side in this_sides:
      for other_side in other_sides:
        p = side.intersect_segments(other_side)
        print p
        if p is not None:
          return True
    
    return False

  def collides_with_tile(self, tiles):
    for tile in tiles:
      # if the rects don't even collide, then they don't collide
      if not pygame.sprite.collide_rect(self, tile):
        continue
      
      # otherwise, have to verify collision in case of turned tank
      intersects = []
      for side in self.get_sides():
        for tile_side in tile.get_sides():
          p = side.intersect_segments(tile_side)
          if not p is None:
            intersects.append((side, tile_side, p))

      if intersects:
        return True

    return False

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
    if self.tank.cooldown == 0 and self.tank.bullets < constants.TANK_MAX_BULLETS:
      origin = self.tank.position.translate(Vector(constants.TURRET_LENGTH_RATIO / 2, 0)).rotate_about(self.direction + self.tank.direction, self.tank.position)
      self.tank.bullets += 1
      self.tank.cooldown = constants.TANK_COOLDOWN
      return Bullet(origin.x, origin.y, self.direction + self.tank.direction, self.tank)

  # turn towards target point
  def turn(self, delta, target):
    # target direction
    d = target - self.tank.position
    # target angle
    t_a = d.angle()
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
