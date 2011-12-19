from game_event import Event

class NewLevelEvent(Event):
  def do(self):
    self.game.new_level()

class SaveLevelEvent(Event):
  def do(self):
    self.game.save_level()

class LoadLevelEvent(Event):
  def __init__(self, level):
    self.level = level

  def do(self):
    self.game.load_level(self.level)
