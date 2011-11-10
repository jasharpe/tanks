from game_event import RestartLevelEvent, AdvanceLevelEvent, PlaySoundEvent
import constants

class TimedLevelAdvance:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(AdvanceLevelEvent(self.level))
    return self.time_left == 0

class TimedLevelVictory:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.victory = True
      self.level.cooldown = constants.SCREEN_CHANGE_COOLDOWN
    return self.time_left == 0

class TimedLevelRestart:
  def __init__(self, time, level):
    self.level = level
    self.time_left = time

  def update(self, delta):
    self.time_left -= delta
    self.time_left = max(0, self.time_left)
    if self.time_left == 0:
      self.level.game.register_event(RestartLevelEvent(self.level))
    return self.time_left == 0
