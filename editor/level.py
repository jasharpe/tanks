import pygame
import level_loader

class EditorEntity(pygame.sprite.Sprite):
  def __init__(self, position, name):
    self.name = name
  
  def set_position(self, position):
    self.position = position

  def update(self, delta):
    pass
  
  def draw(self, screen):
    pass


class LevelEditor(object):
  def __init__(self, editor):
    self.editor = editor
    (name, player_start, player_direction, board, enemies, powerups) = level_loader.load(1)
    self.player_start = PlayerStart(player_start)
  
  def update(self, delta, events, pressed, mouse):
    pass

  def draw(self, screen):
    pass
