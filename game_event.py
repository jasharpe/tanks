class ResumeEvent:
  def __init__(self):
    pass

  def set_game(self, game):
    self.game = game

  def do(self):
    self.game.resume()

class NewGameEvent:
  def __init__(self):
    pass

  def set_game(self, game):
    self.game = game

  def do(self):
    self.game.start_new_game()

class QuitEvent:
  def __init__(self):
    pass

  def set_game(self, game):
    self.game = game

  def do(self):
    self.game.quit()

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
