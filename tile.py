import pygame
import constants
from geometry import Vector, Point

WALL_COLOR = pygame.Color(150, 0, 0, 255)
GROUND_COLOR = pygame.Color(100, 100, 100, 255)

class Tile(pygame.sprite.Sprite):
  def __init__(self, tile_type, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface([constants.TILE_SIZE, constants.TILE_SIZE], flags=pygame.SRCALPHA)
    if tile_type == 'W':
      self.image.fill(WALL_COLOR)
      self.solid = True
    elif tile_type == 'G':
      self.image.fill(GROUND_COLOR)
      self.solid = False
    self.rect = self.image.get_rect()
    self.rect.x = constants.TILE_SIZE * x
    self.rect.y = constants.TILE_SIZE * y
    self.position = Point(x + 0.5, y + 0.5)
