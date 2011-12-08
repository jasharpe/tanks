import constants
import pygame
from geometry import Point

DEFAULT_SETTINGS = {
    'debug': False
}

TOOLBAR_COLOR = pygame.Color(100, 100, 100)
TOOLBAR_ITEM_COLOR = pygame.Color(50, 50, 50)

RIGHT_BAR_RATIO = 1.0
RIGHT_BAR_ITEM_RATIO = 0.8
RIGHT_BAR_ITEM_SPACING = 0.1
BOTTOM_BAR_RATIO = 1.0

RESOLUTION_X = int(round(constants.RESOLUTION_X + RIGHT_BAR_RATIO * constants.TILE_SIZE))
RESOLUTION_Y = int(round(constants.RESOLUTION_Y + BOTTOM_BAR_RATIO * constants.TILE_SIZE))

EDITOR_AREA_BOUNDS = {
    'left' : 0,
    'top' : 0,
    'right' : constants.HORIZONTAL_TILES,
    'bottom' : constants.VERTICAL_TILES
}

class EntityData(object):
  def __init__(self, ratio, label, hotkey, color):
    self.ratio = ratio
    self.label = label
    self.hotkey = hotkey
    self.color = color

ENTITY_SELECTED_COLOR = pygame.Color(255, 255, 0)

ENTITY_DATA = {
    'PLAYER' : EntityData(constants.TANK_SIZE_RATIO, 'S', pygame.K_s, pygame.Color(0, 255, 0)),
    'ENEMY' : EntityData(constants.TANK_SIZE_RATIO, 'E', pygame.K_e, pygame.Color(255, 0, 0)),
    'POWERUP' : EntityData(constants.POWERUP_SIZE_RATIO, 'P', pygame.K_p, pygame.Color(0, 0, 255))
}
