from font import FontManager
from level_editor import LevelEditor
import pygame
import constants, editor_constants
from settings import Settings
from editor_menu import EditorMainMenu

STAGE_EDITOR = 1
STAGE_MENU   = 2

class EditorGame(object):
  def __init__(self):
    self.settings = Settings(editor_constants.DEFAULT_SETTINGS, "editor")
    self.font_manager = FontManager()
    self.editor = LevelEditor(self)
    self.menu_stack = []
    self.events = []
    self.should_quit = False
    self.stage = STAGE_EDITOR
  
  def register_event(self, event):
    event.set_game(self)
    self.events.append(event)

  def quit(self):
    self.should_quit = True

  def resume(self):
    self.stage = STAGE_EDITOR

  def new_level(self):
    pass

  def save_level(self):
    pass

  def enter_menu(self, sub_menu=None):
    if sub_menu is None:
      self.menu = EditorMainMenu(self)
      self.menu_stack = []
      self.stage = STAGE_MENU
    else:
      self.menu_stack.append(self.menu)
      self.menu = sub_menu

  def back_menu(self):
    self.menu = self.menu_stack.pop()

  def update(self, delta, events, pressed, mouse):
    for event in self.events:
      event.do()
    self.events = []

    if self.should_quit:
      return True

    for event in events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        self.enter_menu()

    if self.stage is STAGE_EDITOR:
      self.editor.update(delta, events, pressed, mouse)
    elif self.stage is STAGE_MENU:
      self.menu.update(delta, events, pressed, mouse)

    return False

  def draw(self, screen):
    if self.stage is STAGE_EDITOR:
      self.editor.draw(screen)
    elif self.stage is STAGE_MENU:
      self.menu.draw(screen)
