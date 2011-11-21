import pygame, constants, os

class FontManager:
  def __init__(self):
    self.cache = {}

  def render(self, text, size, color):
    k = (text, size, color[:4])
    # rendering text is reeeeally slow in pygame, so cache it
    if not k in self.cache:
      font = pygame.font.Font(os.path.join(constants.DATA_DIR, "army.ttf"), size)
      self.cache[k] = font.render(text, 1, color)
    return self.cache[k]
