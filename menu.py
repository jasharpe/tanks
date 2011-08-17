import pygame
import constants
from game_event import *

class MenuItem:
  def __init__(self, text, on_activate):
    self.raw_text = text
    self.activate = on_activate
    self.selected = False

  def toggle_selected(self):
    self.selected = not self.selected
    self.generate_image()

class BasicItem(MenuItem):
  def __init__(self, text, on_activate):
    MenuItem.__init__(self, text, on_activate)
    self.generate_image()

  def generate_image(self):
    color = (200, 200, 200)
    if self.selected:
      color = (255, 200, 200)
    self.image = pygame.font.Font(None, 36).render(self.raw_text, 1, color)

class CheckItem(MenuItem):
  def __init__(self, game, text, value_function, on_activate):
    MenuItem.__init__(self, text, on_activate)
    self.game = game
    self.value_function = value_function
    self.generate_image()

  def generate_image(self):
    color = (200, 200, 200)
    if self.selected:
      color = (255, 200, 200)
    text = pygame.font.Font(None, 36).render(self.raw_text, 1, color)
    self.image = pygame.Surface((text.get_width() + text.get_height() + 5, text.get_height()), flags=pygame.SRCALPHA)
    rect = pygame.Rect(1, 1, text.get_height() - 1, text.get_height() - 1)
    pygame.draw.rect(self.image, color, rect, 1)
    if self.value_function(self.game):
      pygame.draw.line(self.image, color, rect.topleft, rect.bottomright, 1)
      topright = (rect.topright[0] - 1, rect.topright[1])
      pygame.draw.line(self.image, color, rect.bottomleft, topright, 1)
    self.image.blit(text, (text.get_height() + 5, 0))

def resume_menu_action(game):
  game.register_event(ResumeEvent())

def new_game_menu_action(game):
  game.register_event(NewGameEvent())

def settings_menu_action(game):
  game.register_event(EnterMenuEvent(SettingsMenu(game)))

def quit_menu_action(game):
  game.register_event(QuitEvent())

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

def settings_back_menu_action(game):
  game.register_event(MenuBackEvent())

def music_menu_value(game):
  return game.settings['music']

def toggle_music_menu_action(game):
  game.register_event(ToggleMusicEvent())

def sound_menu_value(game):
  return game.settings['sound']

def toggle_sound_menu_action(game):
  game.register_event(ToggleSoundEvent())

class SettingsMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = []
    self.menu_items.append(BasicItem("Back", settings_back_menu_action))
    self.menu_items.append(CheckItem(self.game, "Music", music_menu_value, toggle_music_menu_action))
    self.menu_items.append(CheckItem(self.game, "Sound", sound_menu_value, toggle_sound_menu_action))
    self.menu_items[0].toggle_selected()
    self.selected = 0

class MainMenu(Menu):
  def __init__(self, game, level):
    Menu.__init__(self, game)
    self.menu_items = []
    if level is not None:
      self.menu_items.append(BasicItem("Resume", resume_menu_action))
    self.menu_items.append(BasicItem("New Game", new_game_menu_action))
    self.menu_items.append(BasicItem("Settings", settings_menu_action))
    self.menu_items.append(BasicItem("Quit", quit_menu_action))
    self.menu_items[0].toggle_selected()
    self.selected = 0
