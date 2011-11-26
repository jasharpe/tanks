import constants
import pygame

DEFAULT_SETTINGS = {
    'debug': False
}

class EntityData(object):
  def __init__(self, ratio, label, color):
    self.ratio = ratio
    self.label = label
    self.color = color

ENTITY_DATA = {
    'ENEMY' : EntityData(constants.TANK_SIZE_RATIO, 'E', pygame.Color(255, 0, 0)),
}
