import pygame, math, random, os
import constants
from geometry import Vector, Point, Line, ORIGIN
from bullet import Bullet
import interpolation

TANK_EXPLODED = 1

class SplashTimer:
  def __init__(self, time, tank):
    self.tank = tank
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.tank.splash = False
      self.splash_color_time = 0
      self.tank.update_image()
    return self.time_left == 0

class Tank(pygame.sprite.Sprite):
  def __init__(self, position, direction, color=constants.TANK_COLOR):
    pygame.sprite.Sprite.__init__(self)

    self.color = color

    # current coordinates of the centre of the tank
    self.position = position
    self.old_position = self.position
    # current direction of the tank, in radians
    self.direction = direction
    self.old_direction = self.direction
    # speed of the tank
    self.speed = 0.0
    self.cooldown = 0

    self.bullets = 0
    self.turret = None

    self.health = constants.TANK_HEALTH
    self.dead = False

    self.taking = set()
    self.splash = False
    self.splash_color_time = 0

    self.shields = []

    self.timers = []

    self.update_image()
    self.update_graphics()

  def update_image(self):
    size = constants.TILE_SIZE * constants.TANK_SIZE_RATIO
    self.original = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    diff = 20 * (constants.TANK_HEALTH - self.health)
    new_color = pygame.Color(max(0, self.color.r - diff), max(0, self.color.g - diff), max(0, self.color.b - diff))
    if self.splash:
      splash_color = pygame.Color(max(0, constants.SPLASH_TANK_COLOR.r - diff), max(0,constants.SPLASH_TANK_COLOR.g - diff), max(0, constants.SPLASH_TANK_COLOR.b - diff))
      t = interpolation.quadratic_bi(self.splash_color_time % constants.SPLASH_TANK_COLOR_PERIOD, constants.SPLASH_TANK_COLOR_PERIOD)
      final_color = interpolation.interpolate_colors(t, splash_color, new_color)
    else:
      final_color = new_color
    self.original.fill(final_color)

  def expired(self):
    return self.dead

  def hurt(self):
    if constants.INFINITE_HEALTH:
      return

    self.health -= 1
    if self.health == 0:
      self.dead = True
      for shield in self.shields:
        shield.die()
      return TANK_EXPLODED
    else:
      self.update_image()

  def heal(self):
    self.health = min(self.health + 1, constants.TANK_HEALTH)
    self.update_image()

  def has_splash(self):
    return self.splash

  def activate_splash(self):
    self.splash = True
    self.splash_color_time = 0
    self.timers.append(SplashTimer(constants.SPLASH_TANK_DURATION, self))

  # this returns the tank to its position before the last update()
  # call. It is important that this be idempotent.
  def revert(self):
    self.position = self.old_position
    self.direction = self.old_direction
    self.speed = 0.0
    self.update_graphics()
    self.turret.revert()

  def update(self, delta):
    self.cooldown -= delta
    self.cooldown = max(self.cooldown, 0)
    self.old_position = self.position
    self.position = self.position.translate(
        ((delta / 1000.0) * self.speed) *
        Vector(math.cos(self.direction), math.sin(self.direction)).normalize())
    if self.splash:
      self.splash_color_time += delta
      self.update_image()
    for timer in self.timers:
      if timer.update(delta):
        self.timers.remove(timer)
    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.transform.rotate(self.original, -self.direction * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=(self.position.scale(constants.TILE_SIZE)))
  
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

class Turret(pygame.sprite.Sprite):
  def __init__(self, tank):
    pygame.sprite.Sprite.__init__(self)

    self.original = pygame.transform.smoothscale(pygame.image.load(os.path.join(constants.DATA_DIR, "turret.png")).convert_alpha(), (int(round(constants.TURRET_LENGTH_RATIO * constants.TILE_SIZE)), int(round(constants.TURRET_WIDTH_RATIO * constants.TILE_SIZE))))
    self.image = self.original
    self.rect = self.image.get_rect()
    self.direction = 0.0

    self.tank = tank
    tank.turret = self

  def expired(self):
    return self.tank.dead

  def revert(self):
    self.update_graphics()

  # creates and returns a Bullet starting at the end of the Turret's
  # barrel and going in the direction of the barrel.
  def fire(self):
    if self.tank.cooldown == 0 and self.tank.bullets < constants.TANK_MAX_BULLETS:
      origin = self.tank.position.translate(Vector(constants.TURRET_LENGTH_RATIO / 2, 0)).rotate_about(self.direction + self.tank.direction, self.tank.position)
      self.tank.bullets += 1
      self.tank.cooldown = constants.TANK_COOLDOWN
      return Bullet(origin, self.direction + self.tank.direction, self.tank, self.tank.splash)

  # turn towards target point
  def turn(self, delta, target):
    # target direction
    d = target - self.tank.position
    # target angle
    t_a = d.angle()
    return self.turn_direction(delta, t_a)
    
  def turn_direction(self, delta, target_direction):
    t_a = target_direction
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
    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.transform.rotate(self.original, -(self.direction + self.tank.direction) * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=self.tank.rect.center)
