import pygame, math
import constants
from geometry import Vector, Point

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
    self.vec = Vector(math.cos(direction), math.sin(direction)).normalize()
    self.direction = direction

  def update(self, delta):
    self.position = self.position.translate(
        (constants.BULLET_SPEED * delta / 1000.0) * self.vec)
    self.image = pygame.transform.rotate(self.original, -self.direction * 180.0 / math.pi)
    self.rect = self.image.get_rect(center=(constants.TILE_SIZE * self.position.x, constants.TILE_SIZE * self.position.y))
