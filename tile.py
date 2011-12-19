import pygame, random
import constants
from geometry import Vector, Point, Line

TILE_RIGHT = 1
TILE_LEFT = 2
TILE_BOTTOM = 3
TILE_TOP = 4

class Tile(pygame.sprite.Sprite):
  def __init__(self, tile_type, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface([constants.TILE_SIZE, constants.TILE_SIZE], flags=pygame.SRCALPHA)
    if tile_type == 'W':
      self.image.fill(constants.TILE_WALL_COLOR)
      self.solid = True
    elif tile_type == 'G':
      self.image.fill(constants.TILE_GROUND_COLOR)
      self.solid = False
    self.type = tile_type
    self.rect = self.image.get_rect()
    self.rect.x = constants.TILE_SIZE * x
    self.rect.y = constants.TILE_SIZE * y
    self.position = Point(x + 0.5, y + 0.5)
    self.exposed_sides = {
        TILE_RIGHT : True,
        TILE_LEFT : True,
        TILE_TOP : True,
        TILE_BOTTOM : True
    }
    self.sides = None

  def set_accessible(self, direction, value):
    self.exposed_sides[direction] = value

  def get_sides(self):
    if self.sides is None:
      tile_top_left = self.position.translate(Vector(-0.5, -0.5))
      tile_top_right = self.position.translate(Vector(0.5, -0.5))
      tile_bottom_right = self.position.translate(Vector(0.5, 0.5))
      tile_bottom_left = self.position.translate(Vector(-0.5, 0.5))
      
      self.sides = []
      tile_left = Line(tile_bottom_left, tile_top_left)
      if self.exposed_sides[TILE_LEFT]:
        self.sides.append(tile_left)
      tile_right = Line(tile_top_right, tile_bottom_right)
      if self.exposed_sides[TILE_RIGHT]:
        self.sides.append(tile_right)
      tile_top = Line(tile_top_left, tile_top_right)
      if self.exposed_sides[TILE_TOP]:
        self.sides.append(tile_top)
      tile_bottom = Line(tile_bottom_right, tile_bottom_left)
      if self.exposed_sides[TILE_BOTTOM]:
        self.sides.append(tile_bottom)

    return self.sides
