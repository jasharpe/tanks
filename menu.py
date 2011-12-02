import pygame
import constants
from game_event import *
import re

class MenuItem:
  def __init__(self, menu, text, on_activate):
    self.menu = menu
    self.raw_text = text
    self.activate = on_activate
    self.selected = False

  def get_color(self):
    return constants.SELECTED_TEXT_COLOR if self.selected else constants.DEFAULT_TEXT_COLOR

  def toggle_selected(self):
    self.selected = not self.selected

class BasicItem(MenuItem):
  def __init__(self, menu, text, on_activate):
    MenuItem.__init__(self, menu, text, on_activate)
    self.last_selected = None

  def generate_image(self):
    if self.last_selected is None or not self.last_selected is self.selected:
      self.image = self.menu.game.font_manager.render(self.raw_text.upper(), 50, self.get_color())
    self.last_selected = self.selected

class CheckItem(MenuItem):
  def __init__(self, menu, text, value_function, on_activate):
    MenuItem.__init__(self, menu, text, on_activate)
    self.value_function = value_function
    self.last_value = None #value_function(menu.game)
    self.last_selected = None

  def generate_image(self):
    if (self.last_selected is None or not self.last_selected is self.selected) or \
       (self.last_value is None or not self.last_value is self.value_function(self.menu.game)):
      color = self.get_color()
      text = self.menu.game.font_manager.render(self.raw_text, 50, color)
      self.image = pygame.Surface((text.get_width() + text.get_height() + 5, text.get_height()), flags=pygame.SRCALPHA)
      rect = pygame.Rect(1, 1, text.get_height() - 1, text.get_height() - 1)
      pygame.draw.rect(self.image, color, rect, 1)
      if self.value_function(self.menu.game):
        pygame.draw.line(self.image, color, rect.topleft, rect.bottomright, 1)
        topright = (rect.topright[0] - 1, rect.topright[1])
        pygame.draw.line(self.image, color, rect.bottomleft, topright, 1)
      self.image.blit(text, (text.get_height() + 5, 0))
    self.last_selected = self.selected
    self.last_value = self.value_function(self.menu.game)

class Menu:
  def __init__(self, game):
    self.game = game

  def update(self, delta, events, pressed, mouse):
    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN:
          self.menu_items[self.selected].toggle_selected()
          self.selected = (self.selected + 1) % len(self.menu_items)
          self.menu_items[self.selected].toggle_selected()
        elif event.key == pygame.K_UP:
          self.menu_items[self.selected].toggle_selected()
          self.selected = (self.selected - 1) % len(self.menu_items)
          self.menu_items[self.selected].toggle_selected()
        elif event.key == pygame.K_RETURN:
          self.menu_items[self.selected].activate(self.game)

  def draw(self, screen):
    image_top = 300
    for menu_item in self.menu_items:
      menu_item.generate_image()
      image_pos = menu_item.image.get_rect(centerx = constants.RESOLUTION_X / 2)
      image_pos.top = image_top
      image_top += menu_item.image.get_height() + 5
      screen.blit(menu_item.image, image_pos)

def register_event(event, *args):
  return lambda game: game.register_event(event(*args))

def get_setting(val):
  return lambda game: game.settings[val]

class SettingsMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = [
        BasicItem(self, "Back", register_event(MenuBackEvent)),
        CheckItem(self, "Music", get_setting('music'), register_event(ToggleMusicEvent)),
        CheckItem(self, "Sound", get_setting('sound'), register_event(ToggleSoundEvent)),
        CheckItem(self, "Debug", get_setting('debug'), register_event(ToggleDebugEvent)),
        #CheckItem(self, "Hot Swap", get_setting('hot_swap'), register_event(ToggleHotSwapEvent))
    ]
    self.menu_items[0].toggle_selected()
    self.selected = 0

class LevelMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = [
        BasicItem(self, "Back", register_event(MenuBackEvent))
    ]
    for i in xrange(0, game.max_level):
      self.menu_items.append(
          BasicItem(self, "%d. %s" % (i + 1, game.levels[i]), register_event(GoToLevelEvent, i + 1))
      )
    self.menu_items[0].toggle_selected()
    self.selected = 0

def enter_menu_action(menu_type):
  return lambda game: game.register_event(EnterMenuEvent(menu_type(game)))

class MainMenu(Menu):
  def __init__(self, game, level):
    Menu.__init__(self, game)
    self.menu_items = []
    if level is not None:
      self.menu_items.append(BasicItem(self, "Resume", register_event(ResumeEvent)))
    self.menu_items.append(BasicItem(self, "New Game", register_event(NewGameEvent)))
    if self.game.max_level > 1:
      self.menu_items.append(BasicItem(self, "Level Select", enter_menu_action(LevelMenu)))
    self.menu_items.append(BasicItem(self, "Settings", enter_menu_action(SettingsMenu)))
    self.menu_items.append(BasicItem(self, "Quit", register_event(QuitEvent)))
    self.menu_items[0].toggle_selected()
    self.selected = 0

  def draw(self, screen):
    if not self.game.level is None:
      level_text = '%d. %s' % (self.game.current_level, self.game.level.name)
      level_image = self.game.font_manager.render(level_text, 50, constants.DEFAULT_TEXT_COLOR)
      image_pos = level_image.get_rect(centerx = constants.RESOLUTION_X / 2)
      image_pos.top = 200
      screen.blit(level_image, image_pos)
    Menu.draw(self, screen)
