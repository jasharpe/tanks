import pygame
import constants

class VictoryScreen:
  def __init__(self):
    self.cooldown = constants.SCREEN_CHANGE_COOLDOWN

  def update(self, delta, events, pressed, mouse):
    self.cooldown = max(0, self.cooldown - delta)

  def write_line(self, line, screen):
    text = pygame.font.Font(None, 36).render(line, 1, (200, 200, 200))
    text_pos = text.get_rect(centerx = constants.RESOLUTION_X / 2)
    text_pos.top = self.top
    self.top += text.get_height()
    screen.blit(text, text_pos)

  def draw(self, screen):
    self.top = 300
    self.write_line("You beat everything!", screen)
    if self.cooldown == 0:
      self.write_line("(Press any key to return to the menu)", screen)
