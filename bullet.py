import pygame, math
import constants
from geometry import Vector, Point, Line

class Bullet(pygame.sprite.Sprite):
  # position holds xy coordinates of the bullet as a Point
  # direction contains an angle in radians from the positive
  # x axis.
  def __init__(self, x, y, direction):
    super(Bullet, self).__init__()
    
    self.original = pygame.Surface([constants.TILE_SIZE * constants.BULLET_WIDTH_RATIO, constants.TILE_SIZE * constants.BULLET_HEIGHT_RATIO], flags=pygame.SRCALPHA)
    self.original.fill(constants.BULLET_COLOR)
    self.image = self.original
    self.rect = self.image.get_rect()

    self.position = Point(x, y)
    self.old_position = self.position
    self.direction = direction
    self.reset_vec()
    self.bounces = 0

    self.travelled = Line(self.position, self.position)
    self.update_graphics()

  def has_bounces(self):
    return self.bounces < 1

  def reset_vec(self):
    self.vec = Vector(math.cos(self.direction), math.sin(self.direction)).normalize()

  # bounce off wall (which is a line segment).
  # traces movement of bullet backwards 
  def bounce(self, wall):
    line = Line(self.position, self.position.translate(self.vec))
    self.position = wall.reflect(self.position)
    self.old_position = wall.reflect(self.old_position)
    p = line.intersect(wall)
    self.direction = (self.position - p).angle()
    self.travelled = Line(self.old_position, self.position)
    self.reset_vec()
    self.bounces += 1

    self.update_graphics()

  def update(self, delta):
    self.old_position = self.position
    self.position = self.position.translate(
        (constants.BULLET_SPEED * delta / 1000.0) * self.vec)
    self.travelled = Line(self.old_position, self.position)
    self.update_graphics()

  def update_graphics(self):
    self.image = pygame.transform.rotate(self.original, -self.direction * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))
