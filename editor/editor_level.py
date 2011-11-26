import constants, editor_constants
import pygame
import level_loader
from font import FontManager
from geometry import Point
from pygame.sprite import OrderedUpdates

class Entity(pygame.sprite.Sprite):
  def __init__(self, data, position, font_manager):
    pygame.sprite.Sprite.__init__(self)
    
    self.data = data
    self.position = position
    self.font_manager = font_manager

    self.selected = False

    self.update_graphics()
  
  def set_position(self, position):
    self.position = position

  def update(self, delta):
    pass

  def update_graphics(self):
    size = int(round(constants.TILE_SIZE * self.data.ratio))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    center = self.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    pygame.draw.circle(self.image, self.data.color, image_center, int(round(self.image.get_width() / 2)))
    text = self.font_manager.render(self.data.label, 20, pygame.color.Color(0, 0, 0))
    dest = Point(self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2)
    self.image.blit(text, dest)
    self.rect = self.image.get_rect(center=center)

MODE_ADD = 1
MODE_DELETE = 2

class EditorAction(object):
  def __init__(self, level, undo):
    self.level = level
    self.undo = undo

  def do(self):
    if not self.undo:
      return self.forward()
    else:
      return self.backward()

class AddEntityAction(EditorAction):
  def __init__(self, level, entity, undo=False):
    EditorAction.__init__(self, level, undo)

    self.entity = entity

  def forward(self):
    self.level.entities.add(self.entity)

  def backward(self):
    self.level.entities.remove(self.entity)

class EditorLevel(object):
  def __init__(self, editor):
    self.editor = editor

    self.font_manager = FontManager()

    self.entities = OrderedUpdates()
    self.entity_to_create = 'ENEMY'
    self.mode = MODE_ADD

    self.pending_actions = []
    self.action_stack = []
    self.undone_action_stack = []
    #(name, player_start, player_direction, board, enemies, powerups) = level_loader.load(1)
    #self.player_start = PlayerStart(player_start)
  
  def add_action(self, action_type, *args):
    self.undone_action_stack = []
    self.pending_actions.append(action_type(self, *args))
    print self.undone_action_stack

  def get_entity(self, position):
    data = editor_constants.ENTITY_DATA[self.entity_to_create]
    return Entity(data, position, self.font_manager)

  def left_click(self, position):
    self.add_action(AddEntityAction, self.get_entity(position))

  def switch_mode(self):
    if self.mode == MODE_ADD:
      self.mode = MODE_DELETE
    elif self.mode == MODE_DELETE:
      self.mode = MODE_ADD
    print self.mode

  def update(self, delta, events, pressed, mouse):
    for event in events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
        self.switch_mode()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_y and event.mod & pygame.KMOD_CTRL:
        if self.undone_action_stack:
          action = self.undone_action_stack.pop()
          action.undo = False
          self.pending_actions.append(action)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL:
        if self.action_stack:
          action = self.action_stack.pop()
          action.undo = True
          self.pending_actions.append(action)
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.left_click(Point(event.pos[0], event.pos[1]).scale(1.0 / constants.TILE_SIZE))

    for action in self.pending_actions:
      action.do()
      if action.undo:
        self.undone_action_stack.append(action)
      else:
        self.action_stack.append(action)
    self.pending_actions = []

    self.entities.update(delta)

  def draw(self, screen):
    self.entities.draw(screen)
