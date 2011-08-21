import pygame
import constants

class VictoryScreen:
  def __init__(self, game):
    self.game = game
    self.cooldown = constants.SCREEN_CHANGE_COOLDOWN

  def update(self, delta, events, pressed, mouse):
    self.cooldown = max(0, self.cooldown - delta)

  def write_line(self, line, screen):
    text = self.game.font_manager.render(line, 36, constants.DEFAULT_TEXT_COLOR)
    text_pos = text.get_rect(centerx = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    self.top += text.get_height() + 10
    screen.blit(text, text_pos)

  def draw(self, screen):
    self.top = 300
    self.write_line("You beat everything!", screen)
    if self.cooldown == 0:
      self.write_line("(Press any key to return to the menu)", screen)
