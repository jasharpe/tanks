import constants
import pygame
from geometry import Point

DEFAULT_SETTINGS = {
    'debug': False
}

RIGHT_BAR_RATIO = 1.0
BOTTOM_BAR_RATIO = 0.5

RESOLUTION_X = int(round(constants.RESOLUTION_X + RIGHT_BAR_RATIO * constants.TILE_SIZE))
RESOLUTION_Y = int(round(constants.RESOLUTION_Y + BOTTOM_BAR_RATIO * constants.TILE_SIZE))

EDITOR_AREA_BOUNDS = {
    'left' : 0,
    'top' : 0,
    'right' : constants.HORIZONTAL_TILES,
    'bottom' : constants.VERTICAL_TILES
}

class EntityData(object):
  def __init__(self, ratio, label, color):
    self.ratio = ratio
    self.label = label
    self.color = color

ENTITY_SELECTED_COLOR = pygame.Color(255, 255, 0)

ENTITY_DATA = {
    'ENEMY' : EntityData(constants.TANK_SIZE_RATIO, 'E', pygame.Color(255, 0, 0)),
    'POWERUP' : EntityData(constants.POWERUP_SIZE_RATIO, 'P', pygame.Color(0, 0, 255))
}
