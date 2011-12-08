import constants, editor_constants
import pygame
import level_loader
from font import FontManager
from geometry import Point
from pygame.sprite import Group
import collision_detection as cd

# TODO:
# * Only one player entity
# * tank entities should be square, and should have rotational information
# * powerups need type
# * enemies need waypoints
# * need to place tiles (walls and floor)
# * saving and loading

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

  def select(self, selected):
    self.selected = selected
    self.update_graphics()

  def update(self, delta):
    pass

  def update_graphics(self):
    size = int(round(constants.TILE_SIZE * self.data.ratio))
    self.image = pygame.Surface([size, size], flags=pygame.SRCALPHA)
    self.image.fill(constants.COLOR_TRANSPARENT)
    center = self.position.scale(constants.TILE_SIZE)
    image_center = (self.image.get_width() / 2, self.image.get_height() / 2)
    color = editor_constants.ENTITY_SELECTED_COLOR if self.selected else self.data.color
    pygame.draw.circle(self.image, color, image_center, int(round(self.image.get_width() / 2)))
    text = self.font_manager.render(self.data.label, 20, pygame.color.Color(0, 0, 0))
    dest = Point(self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2)
    self.image.blit(text, dest)
    self.rect = self.image.get_rect(center=center)

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
    if self.entity in self.level.selected_entities:
      self.entity.select(False)
      self.level.selected_entities.remove(self.entity)

class DeleteSelectionAction(EditorAction):
  def __init__(self, level, entities, undo=False):
    EditorAction.__init__(self, level, undo)

    self.entities = entities

  def forward(self):
    self.level.clear_selection()
    for entity in self.entities:
      self.level.entities.remove(entity)

  def backward(self):
    for entity in self.entities:
      self.level.entities.add(entity)
    self.level.set_selection(self.entities)

class ToolbarOption(pygame.sprite.Sprite):
  def __init__(self, top, name, data, font_manager):
    pygame.sprite.Sprite.__init__(self)

    self.selected = False

    self.name = name
    self.data = data

    self.position = Point(constants.HORIZONTAL_TILES + editor_constants.RIGHT_BAR_ITEM_SPACING, top)
    self.size = editor_constants.RIGHT_BAR_ITEM_RATIO

    self.font_manager = font_manager

    self.update_graphics()

  def toggle_select(self):
    self.selected = not self.selected
    self.update_graphics()

  def update_graphics(self):
    size = int(round(self.size * constants.TILE_SIZE))
    self.image = pygame.Surface([size, size])
    self.image.fill(self.data.color)
    if self.selected:
      rect = pygame.Rect(self.image.get_rect())
      pygame.draw.rect(self.image, pygame.Color(0, 0, 0), rect, 1)
    text = self.font_manager.render(self.data.label, 20, pygame.color.Color(0, 0, 0))
    dest = Point(self.image.get_width() / 2 - text.get_width() / 2, self.image.get_height() / 2 - text.get_height() / 2)
    self.image.blit(text, dest) 
    self.rect = self.image.get_rect(topleft=self.position.scale(constants.TILE_SIZE))

class VerticalToolbar(pygame.sprite.Sprite):
  def __init__(self, editor_level, font_manager):
    pygame.sprite.Sprite.__init__(self)

    self.editor_level = editor_level

    self.selected = None
    self.position = Point(constants.HORIZONTAL_TILES, 0)
    self.width = editor_constants.RIGHT_BAR_RATIO
    self.height = constants.VERTICAL_TILES

    self.options = Group()
    self.hotkeys = {}
    top = editor_constants.RIGHT_BAR_ITEM_SPACING
    for (name, data) in editor_constants.ENTITY_DATA.items():
      option = ToolbarOption(top, name, data, font_manager)
      self.options.add(option)
      top += editor_constants.RIGHT_BAR_ITEM_RATIO + editor_constants.RIGHT_BAR_ITEM_SPACING
      self.hotkeys[data.hotkey] = option
    self.select(self.options.sprites()[0])

    self.update_graphics()

  def hotkey(self, hotkey):
    if hotkey in self.hotkeys:
      self.select(self.hotkeys[hotkey])

  def select(self, option):
    if self.selected is not None:
      self.selected.toggle_select()
    self.selected = option
    self.selected.toggle_select()

    self.editor_level.entity_to_create = option.name

  def left_click(self, position, pressed):
    for option in self.options:
      rect = pygame.Rect(option.position.scale(constants.TILE_SIZE), (constants.TILE_SIZE * option.size, constants.TILE_SIZE * option.size))
      if rect.collidepoint(position.scale(constants.TILE_SIZE)):
        self.select(option)

  def update_graphics(self):
    width = int(round(self.width * constants.TILE_SIZE))
    height = int(round(self.height * constants.TILE_SIZE))
    self.image = pygame.Surface([width, height])
    self.image.fill(editor_constants.TOOLBAR_COLOR)
    self.rect = self.image.get_rect(topleft=self.position.scale(constants.TILE_SIZE))

  def draw(self, screen):
    self.options.draw(screen)

MODE_ADD = 1
MODE_SELECT = 2

#ENTITIES

# bounds is 
def sphere_in_bounds(center, radius, bounds):
  return \
      center.x - radius > bounds['left'] and \
      center.x + radius < bounds['right'] and \
      center.y - radius > bounds['top'] and \
      center.y + radius < bounds['bottom']

class EditorLevel(object):
  def __init__(self, editor):
    self.editor = editor

    self.font_manager = FontManager()

    self.entities = Group()

    self.toolbars = Group()
    self.toolbars.add(VerticalToolbar(self, self.font_manager))

    self.entity_to_create = 'ENEMY'
    self.mode = MODE_ADD

    self.pending_actions = []
    self.action_stack = []
    self.undone_action_stack = []

    self.selected_entities = []
    #(name, player_start, player_direction, board, enemies, powerups) = level_loader.load(1)
    #self.player_start = PlayerStart(player_start)
  
  def add_action(self, action_type, *args):
    self.undone_action_stack = []
    self.pending_actions.append(action_type(self, *args))

  def get_entity(self, position):
    data = editor_constants.ENTITY_DATA[self.entity_to_create]
    return Entity(data, position, self.font_manager)

  def delete_selection(self):
    self.add_action(DeleteSelectionAction, list(self.selected_entities))

  def set_selection(self, entities):
    self.clear_selection()
    for entity in entities:
      if not entity in self.entities:
        raise Exception("Tried to select non-existent entity.")
      entity.select(True)
      self.selected_entities.append(entity)

  def clear_selection(self):
    for entity in self.selected_entities:
      entity.select(False)
    self.selected_entities = []

  def selection_click(self, entity, shift):
    if shift:
      if entity in self.selected_entities:
        entity.select(False)
        self.selected_entities.remove(entity)
      else:
        entity.select(True)
        self.selected_entities.append(entity)
    else:
      if entity in self.selected_entities:
        for entity in self.selected_entities:
          entity.select(False)
        self.selected_entities = []
      else:
        for other_entity in self.selected_entities:
          other_entity.select(False)
        entity.select(True)
        self.selected_entities = [entity]

  def left_click(self, position, pressed):
    for toolbar in self.toolbars:
      rect = pygame.Rect(toolbar.position, (toolbar.width, toolbar.height))
      if rect.collidepoint(position):
        toolbar.left_click(position, pressed)

    if self.mode == MODE_ADD:
      entity = self.get_entity(position)
      # make sure the entity doesn't intersect any others
      for other_entity in self.entities:
        if cd.sprite_collide(entity, other_entity):
          return
      # make sure the entity creation is in bounds
      if not sphere_in_bounds(position, entity.data.ratio / 2, editor_constants.EDITOR_AREA_BOUNDS):
        return
      self.add_action(AddEntityAction, entity)
    elif self.mode == MODE_SELECT:
      for entity in self.entities:
        if (position - entity.position).length() < entity.data.ratio / 2:
          shift = (pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL])
          self.selection_click(entity, shift)
          break

  def switch_mode(self):
    if self.mode == MODE_ADD:
      self.mode = MODE_SELECT
    elif self.mode == MODE_SELECT:
      self.clear_selection()
      self.mode = MODE_ADD
    print self.mode

  def update(self, delta, events, pressed, mouse):
    for event in events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
        self.switch_mode()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE and self.mode == MODE_SELECT:
        self.delete_selection()
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
        self.left_click(Point(event.pos[0], event.pos[1]).scale(1.0 / constants.TILE_SIZE), pressed)
      elif event.type == pygame.KEYDOWN:
        for toolbar in self.toolbars:
          toolbar.hotkey(event.key)

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
    self.toolbars.draw(screen)
    for toolbar in self.toolbars:
      toolbar.draw(screen)
