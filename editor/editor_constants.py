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
  def __init__(self, ratio, label, hotkey, color, shape):
    self.ratio = ratio
    self.label = label
    self.hotkey = hotkey
    self.color = color
    self.shape = shape

ENTITY_SELECTED_COLOR = pygame.Color(255, 255, 0)

ENTITY_DATA = [
    ('PLAYER', EntityData(constants.TANK_SIZE_RATIO, 'S', pygame.K_s, pygame.Color(0, 255, 0), "SQUARE")),
    ('ENEMY', EntityData(constants.TANK_SIZE_RATIO, 'E', pygame.K_e, pygame.Color(255, 0, 0), "SQUARE")),
    ('SHIELD', EntityData(constants.POWERUP_SIZE_RATIO, 'SH', pygame.K_h, pygame.Color(0, 0, 255), "ROUND")),
    ('REPAIR', EntityData(constants.POWERUP_SIZE_RATIO, 'R', pygame.K_r, pygame.Color(0, 0, 255), "ROUND")),
    ('SPLASH', EntityData(constants.POWERUP_SIZE_RATIO, 'SP', pygame.K_p, pygame.Color(0, 0, 255), "ROUND"))
]

ENTITY_DATA_MAP = {}
for (name, data) in ENTITY_DATA:
  ENTITY_DATA_MAP[name] = data

WAYPOINT_DATA = EntityData(constants.POWERUP_SIZE_RATIO, 'W', None, pygame.Color(200, 200, 200), "ROUND")
