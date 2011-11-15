import constants
from screen import Screen

class LoadScreen(Screen):
  def __init__(self, level):
    Screen.__init__(self, level)

  def draw(self, screen):
    self.top = 300
    self.write_line("%d. %s" % (self.level.game.current_level, self.level.name), screen)

class StatsScreen(Screen):
  def __init__(self, level):
    Screen.__init__(self, level)
    self.computed_stats = {}

  def write_stat_line(self, part1, part2, screen):
    text = self.level.game.font_manager.render(part1, 40, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(right = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    screen.blit(text, text_pos)
    
    text = self.level.game.font_manager.render(part2, 40, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(left = 3 * constants.RESOLUTION_X / 4)
    text_pos.top = self.top
    screen.blit(text, text_pos)

    self.top += text.get_height() + 10

  def get_or_compute(self, stat, getter):
    if stat in self.computed_stats:
      value = self.computed_stats[stat]
    else:
      value = getter()
      self.computed_stats[stat] = value
    return value

  def draw(self, screen):
    stats = self.level.stats
    self.top = 150
    self.write_line("Victory!", screen)
    self.top += 50
    fired_shots = self.get_or_compute("fired_shots", lambda: stats.fired_shots(self.level.player))
    self.write_stat_line("Fired Shots:", "%d" % fired_shots, screen)
    hit_shots = self.get_or_compute("hit_shots", lambda: stats.hit_shots(self.level.player))
    self.write_stat_line("Hits:", "%d" % hit_shots, screen)
    blocked_shots = self.get_or_compute("blocked_shots", lambda: stats.blocked_shots(self.level.player))
    self.write_stat_line("Blocked Shots:", "%d" % blocked_shots, screen)
    accuracy = self.get_or_compute("accuracy", lambda: stats.accuracy(self.level.player))
    accuracy_percentage = int(round(accuracy * 100))
    self.write_stat_line("Accuracy:", "%d%%" % accuracy_percentage, screen)
    kill_total = self.get_or_compute("kill_total", lambda: stats.kill_total(self.level.player))
    self.write_stat_line("Kills:", "%d" % kill_total, screen)
    friendly_fire_kills = self.get_or_compute("friendly_fire_kills", lambda: stats.friendly_fire_kills(self.level.player))
    self.write_stat_line("FF Kills:", "%d" % friendly_fire_kills, screen)
    if self.level.cooldown == 0:
      self.top += 50
      self.write_line("(Press any key to continue)", screen)
