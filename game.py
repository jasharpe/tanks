import pygame, constants, math, sys
import menu
from victory import VictoryScreen
from sound import SoundManager
import level_loader
import getopt
from font import FontManager
from settings import Settings

STAGE_LEVEL = 1
STAGE_MENU = 2
STAGE_VICTORY = 3

class Game:
  def __init__(self, starting_level=None):
    self.settings = Settings(constants.DEFAULT_SETTINGS, "game")
    self.font_manager = FontManager()
    self.sound_manager = SoundManager(self.settings)
    self.sound_manager.trigger_music("movemovemove.ogg", 0.7)
    self.levels = []
    # this is dumb :P
    for i in range(1, 10000):
      try:
        level = level_loader.load_level(i, self)
        self.levels.append(level.name)
      except:
        break
    if starting_level is not None:
      self.current_level = starting_level
      self.max_level = self.current_level
      self.stage = STAGE_LEVEL
      self.restart_level()
      self.menu = None
    else:
      self.current_level = 1
      self.max_level = self.current_level
      self.stage = STAGE_MENU
      self.level = None
      self.menu = menu.MainMenu(self, None)
    self.menu_stack = []
    self.events = []
    self.should_quit = False
    self.victory = None

  # register an action to be executed before the next
  # update cycle. Do this in order to prevent changing
  # things in the middle of an update cycle which is Bad.
  def register_event(self, event):
    event.set_game(self)
    self.events.append(event)

  def resume(self):
    self.stage = STAGE_LEVEL

  def start_new_game(self):
    self.current_level = 1
    self.restart_level()
    self.stage = STAGE_LEVEL

  def quit(self):
    self.should_quit = True

  def advance_level(self):
    self.current_level += 1
    try:
      self.restart_level()
      self.max_level = max(self.max_level, self.current_level)
    except:
      self.level = None
      self.victory = VictoryScreen(self)
      self.stage = STAGE_VICTORY

  def hot_swap(self, module):
    if self.settings['hot_swap']:
      pass
      #import reloader.reloader as reloader
      #reloader.reload(module)

  def restart_level(self):
    self.hot_swap(level_loader)
    self.level = level_loader.load_level(self.current_level, self)

  def go_to_level(self, level):
    self.current_level = level
    self.restart_level()
    self.stage = STAGE_LEVEL

  def enter_menu(self, sub_menu=None):
    if sub_menu is None:
      self.hot_swap(menu)
      self.menu = menu.MainMenu(self, self.level)
      self.menu_stack = []
      self.stage = STAGE_MENU
    else:
      self.menu_stack.append(self.menu)
      self.menu = sub_menu

  def back_menu(self):
    self.menu = self.menu_stack.pop()

  def update(self, delta, pygame_events, pressed, mouse):
    old_stage = self.stage

    for event in self.events:
      event.do()
    self.events = []

    if self.should_quit:
      return True

    for event in pygame_events:
      if self.stage is STAGE_LEVEL:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and not self.level.is_finished():
          self.restart_level()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.enter_menu()
      elif self.stage is STAGE_VICTORY:
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
          if self.victory.cooldown == 0:
            self.enter_menu()

    # do this check so we don't accidentally update with
    # unintentional input.
    # this kind of sucks, maybe there's a purpose to
    # update_controls() methods after all?
    if old_stage is self.stage:
      if self.stage is STAGE_LEVEL:
        self.level.update(delta, pygame_events, pressed, mouse)
      elif self.stage is STAGE_MENU:
        self.menu.update(delta, pygame_events, pressed, mouse)
      elif self.stage is STAGE_VICTORY:
        self.victory.update(delta, pygame_events, pressed, mouse)

    return False

  def draw(self, screen):
    if self.stage is STAGE_LEVEL:
      self.level.draw(screen)
    elif self.stage is STAGE_MENU:
      self.menu.draw(screen)
    elif self.stage is STAGE_VICTORY:
      self.victory.draw(screen)
