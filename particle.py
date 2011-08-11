import pygame, constants, math, random
from geometry import *
from interpolation import *
import utils

class TrailParticle(pygame.sprite.Sprite):
  def __init__(self, position, colour):
    pygame.sprite.Sprite.__init__(self)

    self.position = position
    self.colour = colour
    self.age = 0
    self.max_age = constants.TRAIL_PARTICLE_AGE

    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.Surface([3, 3], flags=pygame.SRCALPHA)
    colour = self.colour
    colour.a = int(round(255 * (1 - linear(self.age, constants.TRAIL_PARTICLE_AGE))))
    self.image.fill(colour)
    self.rect = self.image.get_rect(center=self.position.scale(constants.TILE_SIZE))

  def update(self, delta):
    self.age = min(self.age + delta, constants.TRAIL_PARTICLE_AGE)
    self.update_graphics()

# these are shot off when a powerup is taken and disappears
class PowerupParticle(pygame.sprite.Sprite):
  def __init__(self, position, direction, colour_time):
    pygame.sprite.Sprite.__init__(self)

    self.position = position
    self.actual_position = position
    self.direction = direction
    self.trail_counter = 0
    self.colour_time = colour_time
    self.age = 0
    self.max_age = constants.POWERUP_PARTICLE_AGE
    self.distance_travelled = 0
    self.speed = constants.POWERUP_PARTICLE_INIT_SPEED
    self.period = utils.random_between(
        constants.POWERUP_PARTICLE_PERIOD_RATIO - 0.3,
        constants.POWERUP_PARTICLE_PERIOD_RATIO + 0.3
    )
    self.sign = 1 if random.random() > 0.5 else -1

    self.update_graphics()

  def get_colour(self):
    r = quadratic_bi(self.colour_time, constants.POWERUP_COLOUR_MODULATION_TIME)
    c = interpolate_colours(r, constants.POWERUP_COLOR_ONE, constants.POWERUP_COLOR_TWO)
    c.a = int(round(255 * (1 - linear(self.age, constants.POWERUP_PARTICLE_AGE))))
    return c

  def update_graphics(self):
    self.image = pygame.Surface([3, 3], flags=pygame.SRCALPHA)
    self.image.fill(self.get_colour())
    self.rect = self.image.get_rect(center=self.actual_position.scale(constants.TILE_SIZE))

  def update(self, delta):
    self.trail_counter += delta

    self.colour_time += delta
    while self.colour_time > constants.POWERUP_COLOUR_MODULATION_TIME:
      self.colour_time -= constants.POWERUP_COLOUR_MODULATION_TIME
    self.age = min(self.age + delta, constants.POWERUP_PARTICLE_AGE)

    self.speed = max(0, self.speed - constants.POWERUP_PARTICLE_DECEL * (delta / 1000.0))
    displacement = self.speed * self.direction * (delta / 1000.0)
    self.position = self.position.translate(displacement)
    self.distance_travelled += displacement.length()

    normal = Line(self.position, self.position.translate(self.direction)).normal()
    amp = self.sign * constants.POWERUP_PARTICLE_AMPLITUDE_RATIO * math.sin(2 * math.pi / self.period * self.distance_travelled)
    self.actual_position = self.position.translate(normal * amp)

    self.update_graphics()
