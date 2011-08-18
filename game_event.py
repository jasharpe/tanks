class Event(object):
  def set_game(self, game):
    self.game = game

  def do(self):
    raise Exception("Implement 'do' method.")

class ResumeEvent(Event):
  def do(self):
    self.game.resume()

class NewGameEvent(Event):
  def do(self):
    self.game.start_new_game()

class QuitEvent(Event):
  def do(self):
    self.game.quit()

class EnterMenuEvent(Event):
  def __init__(self, menu):
    Event.__init__(self)
    self.menu = menu

  def do(self):
    self.game.enter_menu(self.menu)

class MenuBackEvent(Event):
  def do(self):
    self.game.back_menu()

class ToggleMusicEvent(Event):
  def do(self):
    self.game.settings['music'] = not self.game.settings['music']
    if self.game.settings['music']:
      self.game.sound_manager.trigger_music("movemovemove.ogg")
    else:
      self.game.sound_manager.end_music()

class ToggleSoundEvent(Event):
  def do(self):
    self.game.settings['sound'] = not self.game.settings['sound']

class ToggleDebugEvent(Event):
  def do(self):
    self.game.settings['debug'] = not self.game.settings['debug']

class AdvanceLevelEvent:
  def __init__(self, level):
    self.level = level

  def set_game(self, game):
    self.game = game

  def do(self):
    if self.game.level is self.level:
      self.game.advance_level()

class RestartLevelEvent:
  def __init__(self, level):
    self.level = level

  def set_game(self, game):
    self.game = game

  def do(self):
    if self.game.level is self.level:
      self.game.restart_level()

class GoToLevelEvent(Event):
  def __init__(self, level):
    self.level = level

  def do(self):
    self.game.go_to_level(self.level)

class PlayMusicEvent:
  def __init__(self, level, name, volume=1.0):
    self.level = level
    self.name = name
    self.volume = volume

  def set_game(self, game):
    self.game = game

  def do(self):
    if self.game.level is self.level:
      self.game.sound_manager.trigger_music(self.name, self.volume)

class PlaySoundEvent:
  def __init__(self, level, name, volume=1.0):
    self.level = level
    self.name = name
    self.volume = volume

  def set_game(self, game):
    self.game = game

  def do(self):
    if self.game.level is self.level:
      self.game.sound_manager.trigger_sound(self.name, self.volume)
