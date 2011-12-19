from menu import Menu, BasicItem, register_event, enter_menu_action, get_setting, CheckItem
from game_event import ResumeEvent, QuitEvent, MenuBackEvent, ToggleDebugEvent
from editor_event import NewLevelEvent, SaveLevelEvent, LoadLevelEvent
import constants
import os

class SettingsMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = [
        BasicItem(self, "Back", register_event(MenuBackEvent)),
        CheckItem(self, "Debug", get_setting('debug'), register_event(ToggleDebugEvent))
    ]
    self.menu_items[0].toggle_selected()
    self.selected = 0

class LoadLevelMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = [
        BasicItem(self, "Back", register_event(MenuBackEvent)),
    ]
    for level in filter(lambda x: x.endswith(".dat"), os.listdir(constants.DATA_DIR)):
      self.menu_items.append(BasicItem(self, level, register_event(LoadLevelEvent, level)))
    self.menu_items[0].toggle_selected()
    self.selected = 0

class EditorMainMenu(Menu):
  def __init__(self, game):
    Menu.__init__(self, game)
    self.menu_items = []
    # TODO: fix up the logic for these so they only show when relevant
    self.menu_items.append(BasicItem(self, "Resume", register_event(ResumeEvent)))
    self.menu_items.append(BasicItem(self, "New Level", register_event(NewLevelEvent)))
    self.menu_items.append(BasicItem(self, "Save", register_event(SaveLevelEvent)))
    self.menu_items.append(BasicItem(self, "Load", enter_menu_action(LoadLevelMenu)))
    self.menu_items.append(BasicItem(self, "Settings", enter_menu_action(SettingsMenu)))
    self.menu_items.append(BasicItem(self, "Quit", register_event(QuitEvent)))
    self.menu_items[0].toggle_selected()
    self.selected = 0
