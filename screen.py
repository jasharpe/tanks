import constants

class Screen(object):
  def __init__(self, level):
    self.level = level

  def write_line(self, line, screen):
    text = self.level.game.font_manager.render(line, 50, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(centerx = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    self.top += text.get_height() + 10
    screen.blit(text, text_pos)
